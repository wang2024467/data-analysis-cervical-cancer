# Cervical Cancer Risk Data Project Report (SQL, Data Processing, Python Productionization, and Modeling Results)

## 1) Project Objective and Scope
This project builds an end-to-end workflow on the UCI Cervical Cancer (Risk Factors) dataset, covering ingestion, schema standardization, SQL transformations, quality gates, model training/comparison, and BI-ready exports. The practical objective is to deliver a reproducible analytics + modeling pipeline that is portfolio-ready and operationally explainable.

Core goals:
- Deliver stable, repeatable datasets and metrics through a configurable pipeline.
- Use SQL marts/checks to produce interpretable risk insights.
- Use Python engineering patterns for training, diagnostics, and export automation.
- Generate stakeholder-facing outputs (dashboard CSVs and model cards).

## 2) Dataset and Processing Methods

### 2.1 Input Resolution Strategy
The pipeline first attempts to read the latest CSV from `data/raw`; if unavailable, it falls back to `data/samples/cervical_cancer_sample.csv`. This provides a production-first behavior while preserving local reproducibility.

Each run generates a `run_id` and logs input path, row/column count, executed SQL files, and quality summary for traceability.

### 2.2 Column Normalization and Schema Alignment
Before persistence, column names are normalized (case/format harmonization and duplicate-safe renaming). Then data is aligned to a canonical schema via `EXPECTED_COLUMNS` (alias mapping + NULL fill for missing columns).

Example: `citology` is mapped as an alias of `cytology`, preventing schema drift from breaking downstream SQL/modeling steps.

### 2.3 SQL Staging Logic (`stg_patients`)
Key methods in staging:
- Type coercion with `CAST/TRY_CAST` for robust handling of dirty numeric values.
- Derived features:
  - `is_smoker`: 1 when `smokes = 1`, else 0.
  - `has_std_history`: 1 when `stds = 1` or `stds_number > 0`, else 0.

This layer creates a consistent modeling/analytics-ready patient table.

### 2.4 SQL Mart Logic
1. `mart_target_prevalence`
   - Uses `AVG(COALESCE(...,0))` to compute positivity rates for `hinselmann`, `schiller`, `cytology`, and `biopsy`.
   - Primary use: prevalence baseline and class-imbalance awareness.

2. `mart_risk_by_age`
   - Age bands: `under_25`, `25_34`, `35_44`, `45_plus`.
   - Aggregates `patient_count`, `biopsy_rate`, `std_history_rate`, `smoker_rate` by segment.
   - Primary use: segment-level risk interpretation and dashboard consumption.

### 2.5 Data Quality Checks and Gate
Three SQL check groups are implemented:
- Null-rate checks (`check_null_rates`).
- Range checks (`check_range_violations`) on age, first sexual intercourse age, and pregnancies.
- Consistency checks (`check_consistency_violations`):
  - `stds=0` while `stds_number>0`.
  - `biopsy=1` while all three screening indicators are zero.

Configured quality gate thresholds (`configs/pipeline.yml`):
- `max_null_rate <= 0.25`
- `allow_range_violations <= 0`
- `allow_consistency_violations <= 10`

## 3) SQL and Data Outcomes

### 3.1 Overall Target Prevalence (858 rows)
- `hinselmann_rate = 0.0408`
- `schiller_rate = 0.0862`
- `cytology_rate = 0.0513`
- `biopsy_rate = 0.0641`

Conclusion: `biopsy` positivity is ~6.4%, indicating meaningful class imbalance. Model selection should prioritize recall/threshold policy, not only accuracy.

### 3.2 Age-Segment Findings
- `45_plus` has the highest `biopsy_rate` (0.1739) but small sample size (n=23).
- Ages 25–44 carry larger volumes and slightly elevated behavioral/history risk indicators versus `under_25`.

Conclusion: The data suggests a high-risk small cohort (`45_plus`) and medium-risk high-volume cohorts (25–44), supporting segment-aware operational policies.

### 3.3 Quality Findings
- Highest null rate is `stds` at ~0.1224 (below 0.25 threshold).
- Range violations: 0.
- Consistency checks include `possible_label_mismatch_rows = 6`, still within configured allowance (`<=10`).

Conclusion: Data quality is sufficient for controlled modeling experiments, with residual label-consistency risk that should be monitored.

## 4) Python Productionization (Engineering)

### 4.1 Reproducibility and Configurability
- YAML-driven pipeline parameters (paths + quality thresholds).
- Stable execution order: `staging -> marts -> checks -> quality gate`.

### 4.2 Operational Design
- Structured logs including `run_id` and quality summary.
- Fail-fast behavior when quality gate fails.
- Parameterized modeling script (drop inconsistent records, output paths, figure directory, model card path).

### 4.3 Delivery Automation
- Automated export of key DuckDB tables to Power BI CSV inputs.
- Automated diagnostics output:
  - Threshold decision table (precision/recall/f1/fpr).
  - Error-slice table (age/smoking/STD-history).
  - Calibration table (with Brier score).
  - One-page dashboard KPI table.
  - Model card with decisions, limitations, and ethical scope.

### 4.4 Test Coverage
Unit tests are present for key control logic:
- Quality gate pass/fail behavior.
- Raw CSV selection behavior.
- Inconsistency flagging and `drop_inconsistent` logic.

## 5) Modeling Methods and Results

### 5.1 Modeling Setup
- Task: binary classification for `biopsy`.
- Features: all non-target columns excluding diagnostic targets.
- Preprocessing: median imputation.
- Split: `train_test_split(test_size=0.2, stratify=y, random_state=42)`.
- Candidate models: Logistic Regression, Random Forest, optional LightGBM/XGBoost.
- Metrics: accuracy, precision, recall, f1, roc_auc, confusion matrix.

### 5.2 Experiment A (Keep Inconsistent Rows, n=858)
Best by F1: `logistic_regression`
- `f1=0.2439`, `recall=0.4545`, `precision=0.1667`, `roc_auc=0.6143`
- Selected threshold: `0.20` (recall-oriented policy)

Interpretation: Better aligned with screening-first scenarios where missing positives is costly.

### 5.3 Experiment B (Drop Inconsistent Rows, n=852)
Best by F1: `random_forest`
- `f1=0.1667`, `recall=0.1000`, `precision=0.5000`, `roc_auc=0.6255`
- Selected threshold: `0.05`

Interpretation: Precision improves but recall drops materially, showing that cleaning policy directly shifts error trade-offs.

### 5.4 Practical Recommendation
- If business priority is minimizing missed high-risk patients: start with **keep inconsistent + logistic regression + lower threshold**.
- If business priority is reducing false positives: **drop inconsistent + random forest** is a candidate, with explicit acceptance of lower recall.

## 6) Limitations and Next Steps
1. Small and imbalanced dataset; add repeated CV and confidence intervals.
2. Label-noise sensitivity; review potential mismatch rows and consider robust training.
3. No external validation cohort; add temporal/out-of-site validation.
4. Production hardening: model registry, drift monitoring, scheduled retraining, audit trails.
5. Business coupling: map thresholds to follow-up cost and miss-detection risk via decision curves.

## 7) Executive Summary
The project already demonstrates a production-style foundation: schema-aligned ingestion, SQL analytics marts, explicit quality gates, configurable model training, diagnostics, and BI exports. The highest-value next iteration is improving label governance while preserving a recall-aware screening strategy.

