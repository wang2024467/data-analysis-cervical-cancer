import argparse
from pathlib import Path

import duckdb


EXPORT_QUERIES = {
    "mart_target_prevalence.csv": "SELECT * FROM mart_target_prevalence",
    "mart_risk_by_age.csv": "SELECT * FROM mart_risk_by_age",
    "check_null_rates.csv": "SELECT * FROM check_null_rates",
    "check_range_violations.csv": "SELECT * FROM check_range_violations",
    "check_consistency_violations.csv": "SELECT * FROM check_consistency_violations",
}


def export_powerbi_inputs(db_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    try:
        for filename, query in EXPORT_QUERIES.items():
            df = con.sql(query).df()
            out = output_dir / filename
            df.to_csv(out, index=False)
            print(f"Exported: {out}")
    finally:
        con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export DuckDB tables for Power BI dashboard inputs")
    parser.add_argument("--db", default="data/processed/cervical_cancer.duckdb")
    parser.add_argument("--out", default="dashboards/powerbi/data")
    args = parser.parse_args()

    export_powerbi_inputs(Path(args.db), Path(args.out))


if __name__ == "__main__":
    main()
