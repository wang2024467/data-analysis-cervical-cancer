import pandas as pd

from src.modeling.train_compare import add_inconsistent_flag, prepare_xy


def test_add_inconsistent_flag_marks_expected_rows() -> None:
    df = pd.DataFrame(
        {
            "stds": [0, 1],
            "stds_number": [2, 0],
            "biopsy": [0, 1],
            "hinselmann": [0, 0],
            "schiller": [0, 0],
            "cytology": [0, 0],
            "age": [22, 31],
        }
    )
    out = add_inconsistent_flag(df)
    assert out["inconsistent_flag"].tolist() == [1, 1]


def test_prepare_xy_drop_inconsistent() -> None:
    df = pd.DataFrame(
        {
            "stds": [0, 1],
            "stds_number": [2, 0],
            "biopsy": [0, 1],
            "hinselmann": [0, 1],
            "schiller": [0, 1],
            "cytology": [0, 1],
            "age": [22, 31],
            "inconsistent_flag": [1, 0],
        }
    )
    X, y = prepare_xy(df, drop_inconsistent=True)
    assert len(X) == 1
    assert len(y) == 1
