import argparse
from pathlib import Path
import duckdb
import pandas as pd
import yaml

from src.utils.column_utils import normalize_column_name


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


def execute_sql_folder(conn: duckdb.DuckDBPyConnection, folder: Path) -> None:
    for sql_file in sorted(folder.glob("*.sql")):
        sql = sql_file.read_text(encoding="utf-8")
        conn.execute(sql)
        print(f"Executed: {sql_file}")


def run_pipeline(config_path: Path) -> None:
    config = load_config(config_path)
    raw_csv = Path(config["raw_csv_path"])
    db_path = Path(config["duckdb_path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not raw_csv.exists():
        raise FileNotFoundError(f"Raw CSV not found: {raw_csv}")

    df = pd.read_csv(raw_csv)
    df = normalize_columns(df)

    conn = duckdb.connect(str(db_path))
    conn.execute("CREATE OR REPLACE TABLE raw_cervical_cancer AS SELECT * FROM df")

    execute_sql_folder(conn, Path("sql/staging"))
    execute_sql_folder(conn, Path("sql/marts"))
    execute_sql_folder(conn, Path("sql/checks"))

    conn.close()
    print(f"Pipeline complete. DuckDB file: {db_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SQL pipeline for cervical cancer project")
    parser.add_argument("--config", default="configs/pipeline.yml", help="Path to pipeline yaml config")
    args = parser.parse_args()
    run_pipeline(Path(args.config))
