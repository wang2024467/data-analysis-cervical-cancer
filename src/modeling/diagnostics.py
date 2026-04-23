from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

import duckdb
import numpy as np
import pandas as pd


def build_threshold_decision_table(
    y_true: pd.Series,
    y_proba: np.ndarray,
    thresholds: Iterable[float] | None = None,
) -> pd.DataFrame:
    from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score

    if thresholds is None:
        thresholds = np.linspace(0.05, 0.95, 19)

    rows: List[Dict[str, float]] = []
    y_arr = y_true.astype(int).to_numpy()
    for threshold in thresholds:
        y_pred = (y_proba >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_arr, y_pred, labels=[0, 1]).ravel()
        fpr = float(fp / (fp + tn)) if (fp + tn) else 0.0
        rows.append(
            {
                "threshold": float(threshold),
                "precision": float(precision_score(y_arr, y_pred, zero_division=0)),
                "recall": float(recall_score(y_arr, y_pred, zero_division=0)),
                "f1": float(f1_score(y_arr, y_pred, zero_division=0)),
                "fpr": fpr,
                "tn": int(tn),
                "fp": int(fp),
                "fn": int(fn),
                "tp": int(tp),
            }
        )
    return pd.DataFrame(rows).sort_values("threshold").reset_index(drop=True)


def build_error_slice_table(
    X_test: pd.DataFrame,
    y_true: pd.Series,
    y_pred: np.ndarray,
) -> pd.DataFrame:
    work = X_test.copy()
    work["y_true"] = y_true.astype(int).to_numpy()
    work["y_pred"] = y_pred.astype(int)

    work["age_group"] = pd.cut(
        work.get("age", pd.Series(np.nan, index=work.index)),
        bins=[0, 24, 34, 44, 54, 120],
        labels=["<=24", "25-34", "35-44", "45-54", "55+"],
        include_lowest=True,
    ).astype(str)
    work["is_smoker"] = (work.get("smokes", 0).fillna(0) > 0).astype(int)
    work["has_std_history"] = (
        (work.get("stds", 0).fillna(0) > 0) | (work.get("stds_number", 0).fillna(0) > 0)
    ).astype(int)

    work["error_type"] = np.where(
        (work["y_true"] == 1) & (work["y_pred"] == 0),
        "FN",
        np.where((work["y_true"] == 0) & (work["y_pred"] == 1), "FP", "OK"),
    )
    err = work[work["error_type"].isin(["FN", "FP"])].copy()
    if err.empty:
        return pd.DataFrame(
            columns=[
                "slice_name",
                "slice_value",
                "error_type",
                "error_count",
                "slice_total_rows",
                "error_rate_within_slice",
            ]
        )

    def _agg(slice_name: str, col: str) -> pd.DataFrame:
        errors = (
            err.groupby([col, "error_type"], dropna=False)
            .size()
            .reset_index(name="error_count")
            .rename(columns={col: "slice_value"})
        )
        totals = work.groupby(col, dropna=False).size().reset_index(name="slice_total_rows").rename(columns={col: "slice_value"})
        out = errors.merge(totals, on="slice_value", how="left")
        out["slice_name"] = slice_name
        out["error_rate_within_slice"] = out["error_count"] / out["slice_total_rows"]
        return out[["slice_name", "slice_value", "error_type", "error_count", "slice_total_rows", "error_rate_within_slice"]]

    return pd.concat(
        [
            _agg("age_group", "age_group"),
            _agg("is_smoker", "is_smoker"),
            _agg("has_std_history", "has_std_history"),
        ],
        ignore_index=True,
    )


def build_calibration_table(y_true: pd.Series, y_proba: np.ndarray, n_bins: int = 10) -> pd.DataFrame:
    from sklearn.calibration import calibration_curve
    from sklearn.metrics import brier_score_loss

    prob_true, prob_pred = calibration_curve(y_true.astype(int), y_proba, n_bins=n_bins, strategy="quantile")
    return pd.DataFrame(
        {
            "bin_id": np.arange(1, len(prob_true) + 1),
            "mean_predicted_probability": prob_pred,
            "observed_positive_rate": prob_true,
            "brier_score": [float(brier_score_loss(y_true.astype(int), y_proba))] * len(prob_true),
        }
    )


def build_quality_summary(db_path: Path) -> pd.DataFrame:
    con = duckdb.connect(str(db_path))
    max_null_rate = con.sql("SELECT COALESCE(MAX(null_rate), 0.0) AS v FROM check_null_rates").fetchone()[0]
    range_violations = con.sql(
        "SELECT COALESCE(SUM(COALESCE(invalid_age_rows, 0)), 0) AS v FROM check_range_violations"
    ).fetchone()[0]
    consistency_violations = con.sql(
        "SELECT COALESCE(SUM(COALESCE(std_flag_conflict_rows, 0)), 0) AS v FROM check_consistency_violations"
    ).fetchone()[0]
    con.close()
    rows = [
        ("max_null_rate", float(max_null_rate), 0.25, float(max_null_rate) <= 0.25),
        ("range_violations_total", int(range_violations), 0, int(range_violations) <= 0),
        ("consistency_violations_total", int(consistency_violations), 0, int(consistency_violations) <= 0),
    ]
    return pd.DataFrame(rows, columns=["check_name", "observed_value", "threshold", "pass"])


def save_model_figures(
    artifacts: Mapping[str, Dict[str, Any]],
    best_model: str,
    threshold_table: pd.DataFrame,
    figures_dir: Path,
) -> bool:
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        return False
    from sklearn.metrics import (
        ConfusionMatrixDisplay,
        PrecisionRecallDisplay,
        RocCurveDisplay,
        confusion_matrix,
    )

    figures_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(7, 5))
    for model_name, artifact in artifacts.items():
        RocCurveDisplay.from_predictions(
            artifact["y_true"],
            artifact["y_proba"],
            name=model_name,
            plot_chance_level=False,
        )
    plt.title("ROC Curves by Model")
    plt.tight_layout()
    plt.savefig(figures_dir / "roc_curve_models.png", dpi=150)
    plt.close()

    plt.figure(figsize=(7, 5))
    for model_name, artifact in artifacts.items():
        PrecisionRecallDisplay.from_predictions(
            artifact["y_true"],
            artifact["y_proba"],
            name=model_name,
        )
    plt.title("Precision-Recall Curves by Model")
    plt.tight_layout()
    plt.savefig(figures_dir / "pr_curve_models.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(threshold_table["threshold"], threshold_table["precision"], label="precision")
    plt.plot(threshold_table["threshold"], threshold_table["recall"], label="recall")
    plt.plot(threshold_table["threshold"], threshold_table["f1"], label="f1")
    plt.plot(threshold_table["threshold"], threshold_table["fp"], label="fp")
    plt.plot(threshold_table["threshold"], threshold_table["fn"], label="fn")
    plt.title(f"Threshold Tradeoff ({best_model})")
    plt.xlabel("Threshold")
    plt.grid(alpha=0.2)
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "threshold_tradeoff_best_model.png", dpi=150)
    plt.close()

    for model_name, artifact in artifacts.items():
        cm = confusion_matrix(artifact["y_true"], artifact["y_pred"], labels=[0, 1])
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[0, 1])
        disp.plot(cmap="Blues", colorbar=False)
        plt.title(f"Confusion Matrix - {model_name}")
        plt.tight_layout()
        plt.savefig(figures_dir / f"confusion_matrix_{model_name}.png", dpi=150)
        plt.close()

    best_artifact = artifacts[best_model]
    model = best_artifact["pipeline"].named_steps["model"]
    feature_names = list(best_artifact["X_test"].columns)
    importance = None
    if hasattr(model, "feature_importances_"):
        importance = np.array(model.feature_importances_, dtype=float)
    elif hasattr(model, "coef_"):
        importance = np.abs(np.ravel(model.coef_))
    if importance is not None and len(importance) == len(feature_names):
        top = pd.DataFrame({"feature": feature_names, "importance": importance}).sort_values("importance", ascending=False).head(15)
        plt.figure(figsize=(8, 6))
        plt.barh(top["feature"][::-1], top["importance"][::-1])
        plt.title(f"Feature Importance ({best_model})")
        plt.tight_layout()
        plt.savefig(figures_dir / "feature_importance_best_model.png", dpi=150)
        plt.close()

    return True


def write_model_card(
    path: Path,
    *,
    drop_inconsistent: bool,
    rows_used: int,
    target_positive_rate: float,
    model_results: pd.DataFrame,
    best_model: str,
    best_threshold: float,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Model Card (Biopsy Risk Classifier)",
        "",
        "## Versioning",
        f"- data_source_table: `stg_patients`",
        f"- rows_used: {rows_used}",
        f"- drop_inconsistent: {drop_inconsistent}",
        f"- target_positive_rate: {target_positive_rate:.6f}",
        "",
        "## Feature Scope",
        "- all non-target columns from `stg_patients` except diagnostic targets (`hinselmann`, `schiller`, `cytology`, `biopsy`)",
        "",
        "## Candidate Models",
    ]
    for _, row in model_results.iterrows():
        lines.append(
            f"- {row['model']}: f1={row['f1']:.4f}, recall={row['recall']:.4f}, precision={row['precision']:.4f}, roc_auc={row['roc_auc']:.4f}"
        )
    lines.extend(
        [
            "",
            "## Decision Policy",
            f"- selected_model: `{best_model}`",
            f"- selected_threshold: {best_threshold:.2f}",
            "- threshold criterion: maximize recall under practical precision constraints for screening",
            "",
            "## Limitations & Risks",
            "- small tabular dataset; uncertainty can be high across splits",
            "- missingness and label noise may bias estimates",
            "- no external validation cohort included",
            "",
            "## Ethical / Safe Use Notes",
            "- not for standalone diagnosis; clinical review is mandatory",
            "- monitor subgroup error rates (age/smoking/std-history) for potential harm concentration",
            "",
            "## Intended / Out-of-Scope",
            "- intended: screening prioritization aid in analytics sandbox",
            "- not intended: production medical decision support without governance approvals",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
