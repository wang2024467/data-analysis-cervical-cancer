# Power BI One-Page Dashboard Workflow

This workflow is designed to be reusable with **your local raw data** (not sample-only).

## Step 1 — Run pipeline on your local raw data
```bash
python -m src.pipeline.run_sql --config configs/pipeline.yml
```

## Step 2 — Export Power BI input CSVs from DuckDB
```bash
python -m src.reporting.export_powerbi_inputs --db data/processed/cervical_cancer.duckdb --out dashboards/powerbi/data
```

## Step 3 — Build one-page dashboard in Power BI
Use files from `dashboards/powerbi/data`:
- `mart_target_prevalence.csv`
- `mart_risk_by_age.csv`
- `check_null_rates.csv`
- `check_range_violations.csv`
- `check_consistency_violations.csv`

### Required visuals
1. KPI cards (4 target rates from `mart_target_prevalence`)
2. Age-group risk bar chart (`mart_risk_by_age`)
3. Data quality panel (null/range/consistency checks)

## Step 4 — Save deliverables
- Place `.pbix` file in `dashboards/powerbi/`
- Export at least 2 screenshots to `dashboards/powerbi/screenshots/`

## Notes
- Re-running Step 1 + Step 2 with updated raw CSV refreshes dashboard inputs.
- This keeps your dashboard process reproducible and local-data driven.
