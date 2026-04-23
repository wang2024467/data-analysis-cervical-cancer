import argparse
from pathlib import Path
from typing import Dict, Tuple, Any

import duckdb
import numpy as np
import pandas as pd

from src.modeling.diagnostics import (
    build_calibration_table,
    build_error_slice_table,
    build_quality_summary,
    build_threshold_decision_table,
    save_model_figures,
    write_model_card,
)


def load_training_frame(db_path: Path) -> pd.DataFrame:
    con = duckdb.connect(str(db_path))
    df = con.sql("SELECT * FROM stg_patients").df()
    con.close()
    return df


def add_inconsistent_flag(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["inconsistent_flag"] = (
        ((out["stds"] == 0) & (out["stds_number"] > 0))
        | ((out["biopsy"] == 1) & (out["hinselmann"] == 0) & (out["schiller"] == 0) & (out["cytology"] == 0))
    ).astype(int)
    return out


def prepare_xy(df: pd.DataFrame, drop_inconsistent: bool) -> Tuple[pd.DataFrame, pd.Series]:
    data = df.copy()
    if drop_inconsistent:
        data = data[data["inconsistent_flag"] == 0].copy()

    y = data["biopsy"].fillna(0).astype(int)
    feature_cols = [
        c
        for c in data.columns
        if c not in {"biopsy", "hinselmann", "schiller", "cytology"}
    ]
    X = data[feature_cols]
    return X, y


def evaluate_model(name: str, model: Any, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
    from sklearn.metrics import (
        accuracy_score,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    pred = model.predict(X_test)
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_test)[:, 1]
    else:
        proba = pred

    return {
        "model": name,
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, proba)) if len(np.unique(y_test)) > 1 else np.nan,
        "tn_fp_fn_tp": str(confusion_matrix(y_test, pred).ravel().tolist()),
        "y_pred": pred,
        "y_proba": proba,
    }


def train_models(X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
    try:
        from sklearn.compose import ColumnTransformer
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import Pipeline
    except Exception as e:
        raise RuntimeError("scikit-learn is required for baseline models. Install requirements.txt first.") from e

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    num_cols = list(X.columns)
    preprocessor = ColumnTransformer(
        transformers=[("num", SimpleImputer(strategy="median"), num_cols)],
        remainder="drop",
    )

    models = {
        "logistic_regression": LogisticRegression(max_iter=500, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced"),
    }

    try:
        from xgboost import XGBClassifier

        models["xgboost"] = XGBClassifier(
            n_estimators=400,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=42,
        )
    except Exception:
        pass

    try:
        from lightgbm import LGBMClassifier

        models["lightgbm"] = LGBMClassifier(
            n_estimators=400,
            learning_rate=0.05,
            max_depth=-1,
            random_state=42,
        )
    except Exception:
        pass

    rows = []
    artifacts: Dict[str, Dict[str, Any]] = {}
    for name, clf in models.items():
        pipe = Pipeline(steps=[("prep", preprocessor), ("model", clf)])
        pipe.fit(X_train, y_train)
        evaluation = evaluate_model(name, pipe, X_test, y_test)
        rows.append(
            {
                "model": evaluation["model"],
                "accuracy": evaluation["accuracy"],
                "precision": evaluation["precision"],
                "recall": evaluation["recall"],
                "f1": evaluation["f1"],
                "roc_auc": evaluation["roc_auc"],
                "tn_fp_fn_tp": evaluation["tn_fp_fn_tp"],
            }
        )
        artifacts[name] = {
            "pipeline": pipe,
            "X_test": X_test.copy(),
            "y_true": y_test.to_numpy(copy=True),
            "y_pred": evaluation["y_pred"],
            "y_proba": evaluation["y_proba"],
        }

    return pd.DataFrame(rows).sort_values(by="f1", ascending=False), artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Train baseline + advanced models on stg_patients")
    parser.add_argument("--db", default="data/processed/cervical_cancer.duckdb")
    parser.add_argument("--drop-inconsistent", action="store_true")
    parser.add_argument("--out", default="outputs/tables/model_comparison.csv")
    parser.add_argument("--notes", default="outputs/model_cards/experiment_note.md")
    parser.add_argument("--figures-dir", default="outputs/figures")
    args = parser.parse_args()

    df = load_training_frame(Path(args.db))
    df = add_inconsistent_flag(df)
    X, y = prepare_xy(df, drop_inconsistent=args.drop_inconsistent)

    notes = Path(args.notes)
    notes.parent.mkdir(parents=True, exist_ok=True)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    figures_dir = Path(args.figures_dir)

    try:
        result, artifacts = train_models(X, y)
        result.to_csv(out_path, index=False)
        best_model = result.iloc[0]["model"]
        best_artifact = artifacts[best_model]
        threshold_table = build_threshold_decision_table(
            y_true=pd.Series(best_artifact["y_true"]),
            y_proba=np.asarray(best_artifact["y_proba"]),
        )
        threshold_path = out_path.parent / f"threshold_decision_{out_path.stem}.csv"
        threshold_table.to_csv(threshold_path, index=False)

        best_threshold_row = threshold_table.sort_values(["recall", "precision"], ascending=[False, False]).iloc[0]
        best_threshold = float(best_threshold_row["threshold"])
        tuned_pred = (np.asarray(best_artifact["y_proba"]) >= best_threshold).astype(int)

        error_slice_table = build_error_slice_table(
            X_test=best_artifact["X_test"],
            y_true=pd.Series(best_artifact["y_true"]),
            y_pred=tuned_pred,
        )
        error_slice_path = out_path.parent / f"error_slices_{out_path.stem}.csv"
        error_slice_table.to_csv(error_slice_path, index=False)

        calibration_table = build_calibration_table(
            y_true=pd.Series(best_artifact["y_true"]),
            y_proba=np.asarray(best_artifact["y_proba"]),
        )
        calibration_path = out_path.parent / f"calibration_{out_path.stem}.csv"
        calibration_table.to_csv(calibration_path, index=False)

        quality_summary = build_quality_summary(Path(args.db))
        quality_summary_path = out_path.parent / f"quality_summary_{out_path.stem}.csv"
        quality_summary.to_csv(quality_summary_path, index=False)

        dashboard_one_page = pd.DataFrame(
            [
                ("selected_model", best_model),
                ("selected_threshold", f"{best_threshold:.2f}"),
                ("selected_model_recall", f"{float(result.iloc[0]['recall']):.4f}"),
                ("selected_model_precision", f"{float(result.iloc[0]['precision']):.4f}"),
                ("selected_model_roc_auc", f"{float(result.iloc[0]['roc_auc']):.4f}"),
                ("target_positive_rate", f"{float(y.mean()):.4f}"),
                ("rows_used", str(len(X))),
                ("models_trained", ", ".join(result["model"].tolist())),
            ],
            columns=["kpi_name", "kpi_value"],
        )
        dashboard_one_page_path = out_path.parent / f"dashboard_one_page_{out_path.stem}.csv"
        dashboard_one_page.to_csv(dashboard_one_page_path, index=False)

        figures_created = save_model_figures(
            artifacts=artifacts,
            best_model=best_model,
            threshold_table=threshold_table,
            figures_dir=figures_dir,
        )

        write_model_card(
            notes,
            drop_inconsistent=args.drop_inconsistent,
            rows_used=len(X),
            target_positive_rate=float(y.mean()),
            model_results=result,
            best_model=best_model,
            best_threshold=best_threshold,
        )

        print(result)
        print(f"Saved: {out_path}")
        print(f"Saved: {threshold_path}")
        print(f"Saved: {error_slice_path}")
        print(f"Saved: {calibration_path}")
        print(f"Saved: {quality_summary_path}")
        print(f"Saved: {dashboard_one_page_path}")
        if figures_created:
            print(f"Saved figures under: {figures_dir}")
        else:
            print("Skipped figure export: matplotlib is not installed in current environment")
        print(f"Saved: {notes}")
    except RuntimeError as e:
        pd.DataFrame(
            [
                {
                    "model": "not_run",
                    "status": "skipped",
                    "reason": str(e),
                    "drop_inconsistent": args.drop_inconsistent,
                }
            ]
        ).to_csv(out_path, index=False)

        notes.write_text(
            "\n".join(
                [
                    "# Experiment Note",
                    "status=skipped",
                    f"reason={str(e)}",
                    f"drop_inconsistent={args.drop_inconsistent}",
                ]
            ),
            encoding="utf-8",
        )
        print(str(e))
        print(f"Saved: {out_path}")
        print(f"Saved skip note: {notes}")


if __name__ == "__main__":
    main()
