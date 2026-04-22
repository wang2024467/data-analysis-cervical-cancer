import pandas as pd

from src.pipeline.run_sql import align_to_expected_columns, normalize_columns


def test_alignment_supports_aliases_and_missing_columns() -> None:
    df = pd.DataFrame(
        {
            "First sexual intercourse (age)": [15, 16],
            "Citology": [0, 1],
            "Biopsy": [0, 1],
        }
    )
    normalized = normalize_columns(df)
    aligned = align_to_expected_columns(normalized)

    assert "first_sexual_intercourse" in aligned.columns
    assert "cytology" in aligned.columns
    assert aligned["first_sexual_intercourse"].tolist() == [15, 16]
    assert aligned["cytology"].tolist() == [0, 1]
    assert aligned["age"].isna().all()
