from src.utils.column_utils import normalize_column_name


def test_normalize_column_name_basic_cases() -> None:
    assert normalize_column_name("STDs:HPV") == "stds_hpv"
    assert normalize_column_name("  Cytology  ") == "cytology"
    assert normalize_column_name("Smokes (packs/year)") == "smokes_packs_year"


def test_normalize_column_name_leading_digit() -> None:
    assert normalize_column_name("123-value") == "col_123_value"
