# Pipeline Design (Template)

## Runtime Flow
1. Resolve input source:
   - use newest `data/raw/*.csv` if exists
   - otherwise fall back to `data/samples/cervical_cancer_sample.csv`
2. Read CSV and normalize column names.
3. Align to canonical schema (missing columns become NULL).
4. Persist `raw_cervical_cancer` to DuckDB.
5. Execute SQL in order:
   - `sql/staging`
   - `sql/marts`
   - `sql/checks`
6. Apply quality gate thresholds.

## Outputs
- `stg_patients`
- `mart_target_prevalence`
- `mart_risk_by_age`
- `check_null_rates`
- `check_range_violations`
- `check_consistency_violations`

## Operational Notes
- Every run has a run_id in logs.
- Pipeline fails fast if quality gate is violated.
