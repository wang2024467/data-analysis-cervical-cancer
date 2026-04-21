import argparse
import logging
from pathlib import Path
from datetime import datetime
import uuid

import duckdb
import pandas as pd
import yaml

from src.utils.column_utils import normalize_column_name


EXPECTED_COLUMNS = {
    "age": ["age"],
    "number_of_sexual_partners": ["number_of_sexual_partners"],
    "first_sexual_intercourse": ["first_sexual_intercourse", "first_sexual_intercourse_age"],
    "num_of_pregnancies": ["num_of_pregnancies"],
    "smokes": ["smokes"],
    "smokes_years": ["smokes_years"],
    "smokes_packs_year": ["smokes_packs_year"],
    "hormonal_contraceptives": ["hormonal_contraceptives"],
    "hormonal_contraceptives_years": ["hormonal_contraceptives_years"],
    "iud": ["iud"],
    "iud_years": ["iud_years"],
    "stds": ["stds"],
    "stds_number": ["stds_number"],
    "stds_condylomatosis": ["stds_condylomatosis"],
    "stds_cervical_condylomatosis": ["stds_cervical_condylomatosis"],
    "stds_vaginal_condylomatosis": ["stds_vaginal_condylomatosis"],
    "stds_vulvo_perineal_condylomatosis": ["stds_vulvo_perineal_condylomatosis"],
    "stds_syphilis": ["stds_syphilis"],
    "stds_pelvic_inflammatory_disease": ["stds_pelvic_inflammatory_disease"],
    "stds_genital_herpes": ["stds_genital_herpes"],
    "stds_molluscum_contagiosum": ["stds_molluscum_contagiosum"],
    "stds_aids": ["stds_aids"],
    "stds_hiv": ["stds_hiv"],
    "stds_hepatitis_b": ["stds_hepatitis_b"],
    "stds_hpv": ["stds_hpv"],
    "stds_number_of_diagnosis": ["stds_number_of_diagnosis"],
    "stds_time_since_first_diagnosis": ["stds_time_since_first_diagnosis"],
    "stds_time_since_last_diagnosis": ["stds_time_since_last_diagnosis"],
    "dx_cancer": ["dx_cancer"],
    "dx_cin": ["dx_cin"],
    "dx_hpv": ["dx_hpv"],
    "dx": ["dx"],
    "hinselmann": ["hinselmann"],
    "schiller": ["schiller"],
    "cytology": ["cytology", "citology"],
    "biopsy": ["biopsy"],
}


def build_logger(run_id: str) -> logging.Logger:
    logger = logging.getLogger("cervical_pipeline")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(handler)
    logger.info("pipeline_start run_id=%s", run_id)
    return logger


def load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapped = {}
    for c in df.columns:
        candidate = normalize_column_name(c)
        original_candidate = candidate
        suffix = 1
        while candidate in mapped.values():
            suffix += 1
            candidate = f"{original_candidate}_{suffix}"
        mapped[c] = candidate
    return df.rename(columns=mapped)


def align_to_expected_columns(df: pd.DataFrame) -> pd.DataFrame:
    aligned = pd.DataFrame(index=df.index)
    for canonical, aliases in EXPECTED_COLUMNS.items():
        source = next((alias for alias in aliases if alias in df.columns), None)
        if source is None:
            aligned[canonical] = pd.NA
        else:
            aligned[canonical] = df[source]
    return aligned


def execute_sql_folder(conn: duckdb.DuckDBPyConnection, folder: Path, logger: logging.Logger) -> None:
    for sql_file in sorted(folder.glob("*.sql")):
        sql = sql_file.read_text(encoding="utf-8")
        conn.execute(sql)
        logger.info("executed_sql file=%s", sql_file)


def evaluate_quality_gate(conn: duckdb.DuckDBPyConnection, config: dict, logger: logging.Logger) -> None:
    quality_cfg = config.get("quality_gate", {})
    max_null_rate = float(quality_cfg.get("max_null_rate", 1.0))
    allow_range_violations = int(quality_cfg.get("allow_range_violations", 0))
    allow_consistency_violations = int(quality_cfg.get("allow_consistency_violations", 0))

    max_observed_null_rate = conn.sql("SELECT COALESCE(MAX(null_rate), 0) AS v FROM check_null_rates").fetchone()[0]
    range_violations = conn.sql(
        """
        SELECT COALESCE(invalid_age_rows, 0)
             + COALESCE(invalid_first_sexual_intercourse_rows, 0)
             + COALESCE(invalid_pregnancy_rows, 0)
        FROM check_range_violations
        """
    ).fetchone()[0]
    consistency_violations = conn.sql(
        """
        SELECT COALESCE(std_flag_conflict_rows, 0)
             + COALESCE(possible_label_mismatch_rows, 0)
        FROM check_consistency_violations
        """
    ).fetchone()[0]

    logger.info(
        "quality_summary max_null_rate=%.4f range_violations=%s consistency_violations=%s",
        float(max_observed_null_rate),
        int(range_violations),
        int(consistency_violations),
    )

    failures = []
    if float(max_observed_null_rate) > max_null_rate:
        failures.append(f"max_null_rate_exceeded observed={max_observed_null_rate:.4f} threshold={max_null_rate:.4f}")
    if int(range_violations) > allow_range_violations:
        failures.append(f"range_violations_exceeded observed={range_violations} allowed={allow_range_violations}")
    if int(consistency_violations) > allow_consistency_violations:
        failures.append(
            f"consistency_violations_exceeded observed={consistency_violations} allowed={allow_consistency_violations}"
        )

    if failures:
        raise ValueError("quality_gate_failed: " + " | ".join(failures))


def run_pipeline(config_path: Path) -> None:
    run_id = f"{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"
    logger = build_logger(run_id)
    config = load_config(config_path)
    raw_csv = Path(config["raw_csv_path"])
    db_path = Path(config["duckdb_path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not raw_csv.exists():
        raise FileNotFoundError(f"Raw CSV not found: {raw_csv}")

    logger.info("load_input path=%s", raw_csv)
    df = pd.read_csv(raw_csv)
    input_rows = len(df)
    logger.info("input_rows=%s input_columns=%s", input_rows, len(df.columns))

    df = normalize_columns(df)
    df = align_to_expected_columns(df)

    conn = duckdb.connect(str(db_path))
    conn.execute("CREATE OR REPLACE TABLE raw_cervical_cancer AS SELECT * FROM df")

    execute_sql_folder(conn, Path("sql/staging"), logger)
    execute_sql_folder(conn, Path("sql/marts"), logger)
    execute_sql_folder(conn, Path("sql/checks"), logger)

    evaluate_quality_gate(conn, config, logger)

    conn.close()
    logger.info("pipeline_complete run_id=%s db_path=%s", run_id, db_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SQL pipeline for cervical cancer project")
    parser.add_argument("--config", default="configs/pipeline.yml", help="Path to pipeline yaml config")
    args = parser.parse_args()
    run_pipeline(Path(args.config))
