from pathlib import Path

import duckdb

from src.reporting.export_powerbi_inputs import export_powerbi_inputs


def test_export_powerbi_inputs_creates_expected_csvs(tmp_path: Path) -> None:
    db_path = tmp_path / "test.duckdb"
    out_dir = tmp_path / "out"

    con = duckdb.connect(str(db_path))
    con.execute("CREATE TABLE mart_target_prevalence(total_rows INTEGER, biopsy_rate DOUBLE)")
    con.execute("INSERT INTO mart_target_prevalence VALUES (10, 0.2)")
    con.execute("CREATE TABLE mart_risk_by_age(age_group VARCHAR, patient_count INTEGER)")
    con.execute("INSERT INTO mart_risk_by_age VALUES ('25_34', 4)")
    con.execute("CREATE TABLE check_null_rates(column_name VARCHAR, null_rate DOUBLE)")
    con.execute("INSERT INTO check_null_rates VALUES ('age', 0.0)")
    con.execute("CREATE TABLE check_range_violations(invalid_age_rows INTEGER)")
    con.execute("INSERT INTO check_range_violations VALUES (0)")
    con.execute("CREATE TABLE check_consistency_violations(std_flag_conflict_rows INTEGER)")
    con.execute("INSERT INTO check_consistency_violations VALUES (1)")
    con.close()

    export_powerbi_inputs(db_path, out_dir)

    assert (out_dir / "mart_target_prevalence.csv").exists()
    assert (out_dir / "mart_risk_by_age.csv").exists()
    assert (out_dir / "check_null_rates.csv").exists()
    assert (out_dir / "check_range_violations.csv").exists()
    assert (out_dir / "check_consistency_violations.csv").exists()
