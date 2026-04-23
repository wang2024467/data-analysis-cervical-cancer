import numpy as np
import pandas as pd

from src.modeling.diagnostics import (
    build_error_slice_table,
    build_threshold_decision_table,
)


def test_build_threshold_decision_table_has_expected_columns() -> None:
    y_true = pd.Series([0, 0, 1, 1])
    y_proba = np.array([0.1, 0.2, 0.7, 0.9])
    out = build_threshold_decision_table(y_true, y_proba, thresholds=[0.5])
    assert out.loc[0, "threshold"] == 0.5
    assert set(["precision", "recall", "f1", "fpr", "fp", "fn"]).issubset(set(out.columns))


def test_build_error_slice_table_tracks_fn_fp_segments() -> None:
    X_test = pd.DataFrame(
        {
            "age": [23, 29, 47, 61],
            "smokes": [0, 1, 0, 1],
            "stds": [0, 0, 1, 0],
            "stds_number": [0, 0, 1, 0],
        }
    )
    y_true = pd.Series([0, 1, 1, 0])
    y_pred = np.array([1, 0, 1, 0])  # one FP + one FN
    out = build_error_slice_table(X_test, y_true, y_pred)
    assert not out.empty
    assert set(out["error_type"].unique()) == {"FP", "FN"}
    assert {"age_group", "is_smoker", "has_std_history"}.issubset(set(out["slice_name"].unique()))
