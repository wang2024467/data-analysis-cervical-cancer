import argparse
from pathlib import Path
from typing import Dict, Tuple, Any

import duckdb
import numpy as np
import pandas as pd


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


def evaluate_model(name: str, model: Any, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
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
    }


def train_models(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
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
    for name, clf in models.items():
        pipe = Pipeline(steps=[("prep", preprocessor), ("model", clf)])
        pipe.fit(X_train, y_train)
        rows.append(evaluate_model(name, pipe, X_test, y_test))

    return pd.DataFrame(rows).sort_values(by="f1", ascending=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train baseline + advanced models on stg_patients")
    parser.add_argument("--db", default="data/processed/cervical_cancer.duckdb")
    parser.add_argument("--drop-inconsistent", action="store_true")
    parser.add_argument("--out", default="outputs/tables/model_comparison.csv")
    parser.add_argument("--notes", default="outputs/model_cards/experiment_note.md")
    args = parser.parse_args()

    df = load_training_frame(Path(args.db))
    df = add_inconsistent_flag(df)
    X, y = prepare_xy(df, drop_inconsistent=args.drop_inconsistent)

    notes = Path(args.notes)
    notes.parent.mkdir(parents=True, exist_ok=True)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = train_models(X, y)
        result.to_csv(out_path, index=False)

        notes.write_text(
            "\n".join(
                [
                    "# Experiment Note",
                    f"drop_inconsistent={args.drop_inconsistent}",
                    f"rows_used={len(X)}",
                    f"target_positive_rate={float(y.mean()):.6f}",
                    "models_trained=" + ", ".join(result["model"].tolist()),
                ]
            ),
            encoding="utf-8",
        )

        print(result)
        print(f"Saved: {out_path}")
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
