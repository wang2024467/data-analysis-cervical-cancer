# Cervical Cancer Data Project (Job-Ready Portfolio)

## 1) Project Goal
Build a **job-ready, end-to-end data project** using the Cervical Cancer Risk Factors dataset (858 patients, with missing values), designed to demonstrate the exact skills required by modern Data/AI roles:

- Python engineering (notebook + scripts)
- SQL analytics
- Data pipeline thinking (ETL/ELT, validation, reproducibility)
- Data analytics and communication
- AI/LLM workflow integration
- Cloud-style data organization
- Documentation, testing, collaboration habits

This README provides the **project structure and execution plan only** (no coding in this step).

---

## 2) Dataset Context (Given)
- Source: Hospital Universitario de Caracas, Venezuela.
- Size: 858 patient records.
- Data types: demographics, habits, medical history, STD-related indicators, diagnosis outcomes.
- Missing values: present in multiple fields (privacy-related non-response).
- Potential target variables:
  - `Hinselmann`
  - `Schiller`
  - `Cytology`
  - `Biopsy`

---

## 2.1) API-First Mini Project Option (Recommended Add-On)
If your goal is to practice **API ingestion + JSON handling + pipeline + AI/analytics**, relying only on UCI CSV is not enough.

Recommended approach: keep the cervical-cancer dataset as core analysis data, and add one small API-driven module.

### Candidate API Sources (health/public)
1. **CDC / data.cdc.gov APIs** (Socrata endpoints)
   - Strong for public-health indicators, time series, and regional attributes.
   - Good JSON + pagination + schema drift practice.
2. **WHO/OECD/World Bank health indicators APIs**
   - Great for country-level context and feature enrichment.
3. **General public APIs (if health-specific endpoint is limited)**
   - Acceptable if you clearly frame transformation and analytics logic.

### Why API track matters for jobs
- Demonstrates real ingestion workflows (auth/rate limit/retries).
- Shows JSON normalization and schema control.
- Fits ETL + validation + analytics + model/AI integration patterns.

### OpenAI API Key — Should We Use It?
**Yes, as an optional enhancement, not as a hard dependency.**

Use OpenAI API for:
- auto-generating data quality summaries,
- translating technical metrics into business explanations,
- lightweight analyst Q&A over project docs (mini-RAG).

Keep graceful fallback:
- if no API key, pipeline still runs and outputs deterministic reports.

---

## 3) What This Project Should Prove to Hiring Managers

### A. Python
- Clean modular scripts (not only notebook cells)
- Data I/O (`csv/json/parquet`)
- Reusable functions
- Config-driven runs
- Basic logging and CLI execution

### B. SQL
- Filtering, grouping, joins
- CTEs, `CASE WHEN`, window functions
- Data quality validation queries
- Reporting-ready aggregate outputs

### C. Data Engineering Concepts
- Clear ETL/ELT pipeline stages
- Data schema + data dictionary
- Batch workflow design
- Data quality checks
- Lineage from raw → cleaned → features → outputs

### D. Analytics
- Missing value strategy
- Exploratory analysis
- Risk-factor summaries
- Business-facing metrics + visual explanation

### E. AI Engineering Fundamentals
- Prompt design for data documentation/summaries
- Lightweight RAG over project docs/data dictionary
- Tool-calling idea (LLM + SQL/helper functions)
- Explain where LLM fits in pipeline safely

### F. Cloud/Platform Awareness
- Project laid out in “cloud-like” zones:
  - raw / processed / curated / artifacts
- Storage-first thinking (object-storage style)
- Notebook + pipeline + reporting interoperability

### G. Engineering Habits
- Version control discipline
- Reproducible environment
- Tests for core transforms/validations
- Clear README and run instructions

### H. Communication
- Translate JD needs into technical deliverables
- Document assumptions, risks, and limitations
- Make outputs understandable to non-technical stakeholders

---

## 4) Recommended Repository Structure (Cloud-Like)

```text
.
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── configs/
│   ├── storage.yml         # local/S3/Fabric path mapping
│   ├── pipeline.yml        # batch run configuration
│   └── quality_rules.yml   # configurable data checks
├── data/
│   ├── raw/                # immutable landing zone (Bronze)
│   │   └── cervical_cancer/
│   │       └── ingestion_date=YYYY-MM-DD/
│   ├── processed/          # standardized/cleaned zone (Silver)
│   │   └── cervical_cancer/
│   │       └── run_id=.../
│   ├── curated/            # business/report-ready zone (Gold)
│   │   └── cervical_cancer/
│   │       └── snapshot_date=YYYY-MM-DD/
│   ├── serving/            # dashboard-consumption extracts
│   └── samples/            # optional small test samples
├── orchestration/
│   ├── job_steps.md        # pipeline step order + dependencies
│   └── runbook.md          # failure handling + rerun guidance
├── sql/
│   ├── staging/            # staging transforms
│   ├── marts/              # analytical models / reporting tables
│   └── checks/             # data validation queries
├── src/
│   ├── config/
│   ├── ingestion/
│   ├── cleaning/
│   ├── validation/
│   ├── features/
│   ├── analytics/
│   ├── reporting/
│   ├── modeling/
│   └── ai_workflow/
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_feature_review.ipynb
│   └── 03_results_story.ipynb
├── tests/
│   ├── test_cleaning.py
│   ├── test_validation.py
│   └── test_features.py
├── docs/
│   ├── data_dictionary.md
│   ├── pipeline_design.md
│   ├── storage_mapping.md  # local ↔ S3/Fabric/OneLake mapping
│   ├── metric_definitions.md
│   ├── ai_workflow_design.md
│   └── decision_log.md
├── dashboards/
│   ├── powerbi/            # pbix + exported screenshots
│   └── streamlit/          # optional dashboard app
└── outputs/
    ├── tables/
    ├── figures/
    └── model_cards/
```

### Storage Zone Semantics (Interview-Ready)
- **Raw/Bronze:** append-only, no destructive updates.
- **Processed/Silver:** cleaned + standardized + validated.
- **Curated/Gold:** KPI/reporting datasets for BI/consumers.
- **Serving:** lightweight exports optimized for dashboard refresh.

---

## 5) Execution Roadmap (Portfolio-Oriented)

### Phase 1 — Foundation (Week 1)
1. Define problem statement and success metrics.
2. Formalize dataset schema and data dictionary.
3. Build raw/processed/curated folder logic.
4. Add validation checklist for missing values and invalid ranges.

**Deliverable:** reproducible ingestion + baseline profiling report.

### Phase 2 — Cleaning + SQL Layer (Week 1–2)
1. Missing value handling strategy (documented).
2. Type correction and standardization.
3. SQL marts for key risk summaries.
4. SQL validation queries and data quality report.

**Deliverable:** cleaned dataset + SQL analytics package.

### Phase 3 — Analytics + Storytelling (Week 2)
1. EDA focused on risk factors and target distributions.
2. Segment analysis (age groups, smoking, STDs, etc.).
3. Create visual outputs and insight narrative.

**Deliverable:** stakeholder-friendly analytics report.

### Phase 4 — AI Workflow Add-on (Week 3)
1. Prompt templates for column summary and anomaly explanation.
2. Basic RAG over `docs/data_dictionary.md` and metrics docs.
3. Tool-calling proof-of-concept (LLM asks SQL helper for aggregates).
4. Safety notes: traceability + human review checkpoints.

**Deliverable:** AI-assisted analytics workflow demo.

### Phase 5 — Dashboard + Job Packaging (Week 3)
1. Build dashboard (Power BI preferred, Streamlit optional).
2. Add project walkthrough in README.
3. Add “How this maps to JD skills” table.
4. Polish GitHub presentation and results artifacts.

**Deliverable:** recruiter-ready portfolio repo.

---

## 6) Data Quality & Validation Framework (Must-Have)
Define and track checks such as:
- Null rate by column
- Allowed range checks (e.g., age, pregnancies)
- Cross-field consistency checks
- Duplicate row detection
- Drift checks between raw and processed versions

Document each check with:
- Rule name
- SQL/Python implementation reference
- Pass/fail status
- Remediation approach

---

## 7) SQL Competency Checklist (For Resume Confidence)
Include examples in project SQL files for:
- Multi-table joins
- CTE pipelines
- Window functions (`ROW_NUMBER`, `AVG OVER`, etc.)
- `CASE WHEN` derived risk flags
- Validation queries and exception tables
- Aggregation tables for dashboard consumption

---


## 7.1) SQL Implementation Plan (Step-by-Step)

Focus on **SQL as the project core**. Build SQL work in four layers so interviewers can clearly see progression from raw data to reporting:

### Layer A — Profiling & Validation (Start Here)
Goal: prove data understanding and quality control.

- `SELECT` + `WHERE` to inspect nulls, outliers, and unexpected values.
- `GROUP BY` to profile distributions (age bands, smoking, STDs prevalence).
- Validation queries:
  - null-rate by field
  - invalid range checks (e.g., age < 10 or > 100)
  - cross-field consistency (e.g., `STDs = 0` but `STDs:number > 0`)

**Deliverables**
- `sql/checks/01_null_checks.sql`
- `sql/checks/02_range_checks.sql`
- `sql/checks/03_consistency_checks.sql`
- `outputs/tables/data_quality_summary.csv`

### Layer B — Staging Transforms
Goal: create analyst-friendly base tables.

- Standardize names/types and missing-value flags in staging SQL.
- Use `CASE WHEN` to derive stable flags:
  - `is_smoker`
  - `high_std_risk`
  - `diagnosis_history_flag`
- Keep logic explicit and reviewable (avoid hidden notebook-only transforms).

**Deliverables**
- `sql/staging/stg_patients.sql`
- `sql/staging/stg_risk_flags.sql`

### Layer C — Analytical Marts
Goal: produce reusable metrics tables for dashboard/reporting.

- Use `JOIN` to combine demographic, behavior, and diagnosis signals.
- Use `CTE` chains for readable transformation flow.
- Build aggregation marts:
  - risk by age group
  - risk by smoking exposure
  - risk by STD indicators

**Deliverables**
- `sql/marts/mart_risk_by_age.sql`
- `sql/marts/mart_risk_by_behavior.sql`
- `sql/marts/mart_target_prevalence.sql`

### Layer D — Advanced Analytics SQL
Goal: show stronger SQL maturity (important for hiring).

- Apply window functions for ranking and cohort comparison:
  - `ROW_NUMBER()` for top risk cohorts
  - `AVG(...) OVER(PARTITION BY ...)` for within-group baselines
  - rolling/relative comparisons where meaningful
- Add exception tables for failed quality rules.

**Deliverables**
- `sql/marts/mart_window_cohort_analysis.sql`
- `sql/checks/99_exceptions.sql`

### Minimum SQL Skill Coverage Matrix
This project should explicitly demonstrate each required SQL skill:

- `SELECT / WHERE / GROUP BY` → profiling + quality summaries
- `JOIN` → integrated risk marts
- `CTE` → modular transformation logic
- `CASE WHEN` → derived risk flags
- `window functions` → cohort ranking/baselines
- `data validation queries` → null/range/consistency checks
- `aggregation/reporting` → dashboard-ready summary tables

### Suggested Weekly SQL Milestones
- **Week 1:** Profiling + validation queries complete.
- **Week 2:** Staging + marts complete.
- **Week 3:** Window-function analysis + final reporting tables + SQL documentation.


## 7.2) Python Engineering Implementation Plan (Concrete)

Goal: show **production-style Python habits**, not notebook-only work.

### A) Code Organization
Use modules by responsibility so each step is testable and reusable:
- `src/ingestion/` → read raw data, schema checks, source metadata capture
- `src/cleaning/` → missing handling, type normalization, rule-based cleaning
- `src/validation/` → quality checks + failure reports
- `src/features/` → reusable derived fields/risk flags
- `src/reporting/` → export tables/figures for dashboard and docs
- `src/ai_workflow/` → prompt templates, retrieval helpers, tool-call wrappers

### B) Execution Pattern (CLI + Scripts)
Each pipeline step should be runnable from command line (for reproducibility):
- `python -m src.ingestion.run --config configs/pipeline.yml`
- `python -m src.cleaning.run --config configs/pipeline.yml`
- `python -m src.validation.run --config configs/quality_rules.yml`
- `python -m src.reporting.run --config configs/pipeline.yml`

This makes batch runs and scheduler/orchestration integration straightforward.

### C) Config-Driven, Not Hard-Coded
- Keep paths, thresholds, and target choices in `configs/*.yml`.
- Avoid hard-coded file locations in notebooks/scripts.
- Use one config per environment/profile (e.g., local/dev/demo).

### D) Data I/O Standards
- Raw ingestion: keep original format + checksum metadata.
- Intermediate storage: parquet preferred for processed/curated layers.
- Final reporting: CSV extracts for BI tools + markdown summaries for docs.
- Keep naming convention consistent with storage partitions (`ingestion_date`, `run_id`, `snapshot_date`).

### E) Logging + Observability Basics
- Structured logs per stage:
  - rows in/out
  - null-rate changes
  - rule failures
  - runtime duration
- Save validation outputs as machine-readable artifacts in `outputs/tables/`.

### F) Testing Strategy (Minimum but Real)
- Unit tests for transform functions (type/missing/range behavior).
- Data quality tests for validation rules.
- Regression check on a small sample dataset in `data/samples/`.
- Add a smoke test pipeline run in CI (or local equivalent) to ensure pipeline integrity.

### G) Notebook Policy
- Notebook for EDA/communication only.
- If notebook logic becomes reusable, migrate it into `src/` module.
- Notebook should consume curated outputs, not mutate core pipeline logic.

### H) What to Demonstrate in Interviews
- “I can run the full workflow from CLI with config files.”
- “Data quality is enforced in code + SQL checks, not manual inspection only.”
- “Same project structure can map from local folders to S3/Fabric paths.”
- “Outputs are reproducible and versionable for analytics and BI delivery.”

### Python Engineering Deliverables
- `src/*` modular pipeline scripts
- `configs/*.yml` parameterized settings
- `tests/` for transforms + validation
- `docs/pipeline_design.md` with run sequence
- reproducible command list in README quickstart

---

## 7.3) Methods We Will Use (Concrete Methodology)

To avoid being too generic, this project will explicitly use the following methods.

### A) Data Cleaning Methods
- Missingness profiling by feature (null count/null rate).
- Rule-based imputation strategy by field type:
  - binary flags (`0/1`) → mode or explicit `unknown` flag strategy
  - continuous/int fields → median/IQR-aware imputation where appropriate
- Outlier handling with domain-safe constraints (winsorize or cap only when justified).
- Consistency repair rules (cross-field logic checks).

### B) Data Validation Methods
- Schema validation (required columns, type expectations).
- Range checks (e.g., plausible age and year-type fields).
- Cross-field checks (logical contradictions).
- Freshness/completeness checks by ingestion snapshot.
- Exception-table pattern: failed rows written to dedicated audit outputs.

### C) Analytical Methods
- Descriptive statistics and prevalence analysis.
- Cohort segmentation (age bands, smoking exposure, STD history).
- Risk-rate comparison across target variables (`Hinselmann`, `Schiller`, `Cytology`, `Biopsy`).
- Trend/contrast tables for stakeholder interpretation.

### D) SQL Methods
- CTE-based transformation flows.
- `CASE WHEN` risk-flag engineering.
- Window-function cohort ranking and baseline comparison.
- Aggregation marts for BI consumption.

### E) Modeling Methods (Required: Baseline + Advanced)
- **Baseline (required):** logistic regression for interpretable benchmark.
- **Advanced models (required):** tree ensembles (Random Forest / XGBoost / LightGBM depending on environment).
- Class-imbalance handling (class weights / threshold tuning / resampling where justified).
- Evaluation with precision, recall, F1, ROC-AUC, and confusion matrix.
- Feature interpretation for explainability.

### F) AI/LLM Methods
- Prompt templates for data dictionary and anomaly explanation.
- Mini-RAG over internal docs.
- Tool-calling pattern for safe aggregate retrieval + narrative generation.

---

## 7.4) Which README/Docs Files We Plan to Use
Besides the root `README.md`, we will maintain focused documentation files so each concern is easy to review.

### Core README Files
- `README.md` (project overview, quickstart, roadmap)
- `docs/pipeline_design.md` (step-by-step pipeline logic)
- `docs/data_dictionary.md` (column definitions + missingness notes)
- `docs/storage_mapping.md` (local ↔ S3/Fabric mapping)
- `docs/metric_definitions.md` (KPIs and calculation rules)
- `docs/ai_workflow_design.md` (LLM boundaries, prompts, tool flow)
- `docs/api_ingestion_design.md` (API source, JSON schema, pagination, retries)
- `docs/decision_log.md` (important design choices and trade-offs)

### Recommended Additions
- `docs/methodology.md` (cleaning/validation/analytics/modeling methods in one place)
- `docs/validation_rules.md` (rule catalog + severity + owner)
- `docs/runbook.md` (how to run, rerun, and troubleshoot pipeline)

### Why This Documentation Split Works
- Recruiter/hiring manager can scan `README.md` quickly.
- Reviewer can deep-dive by topic in `docs/`.
- Method traceability improves reproducibility and team collaboration.

---

## 7.5) Modeling Strategy (Required: 4 Models)
To match your latest requirement, this project will train and compare **all 4 models** below.

### Required Model Stack
1. **Logistic Regression** (baseline, interpretable)
2. **Random Forest** (nonlinear ensemble baseline)
3. **XGBoost** (boosted tree, strong tabular performance)
4. **LightGBM** (efficient gradient boosting)

### Unified Evaluation Protocol
- Same train/validation split or stratified CV for all models.
- Metrics: precision, recall, F1, ROC-AUC, PR-AUC, confusion matrix.
- Threshold tuning aligned with screening objective (recall-sensitive).
- Calibration check when probability outputs are consumed downstream.

### Model Selection Rule
- Select final model using:
  - performance on agreed primary metric,
  - stability across folds/splits,
  - inference efficiency,
  - explainability needs.

### Modeling Deliverables
- `notebooks/04_model_benchmark_4_models.ipynb`
- `src/modeling/train_logistic_regression.py`
- `src/modeling/train_random_forest.py`
- `src/modeling/train_xgboost.py`
- `src/modeling/train_lightgbm.py`
- `src/modeling/evaluate.py`
- `outputs/model_cards/biopsy_model_card.md`

---

## 7.6) API Ingestion + JSON Pipeline Plan (Small but Real)
Build one compact API workflow to complement the core dataset.

### Pipeline Steps
1. Pull API data (incremental where possible).
2. Persist raw JSON snapshots in `data/raw/api_source/...`.
3. Normalize JSON to tabular form in `data/processed/`.
4. Run validation checks (missing keys, schema/type drift, duplicates).
5. Publish curated table for analytics/model enrichment.

### Implementation Files
- `src/ingestion/fetch_api_data.py`
- `src/ingestion/normalize_api_json.py`
- `src/validation/validate_api_payload.py`
- `sql/staging/stg_api_context.sql`
- `sql/marts/mart_enriched_risk.sql`

### OpenAI Integration (Optional)
- `src/ai_workflow/summarize_quality_report.py`
- `src/ai_workflow/generate_insight_narrative.py`
- controlled by env var (`OPENAI_API_KEY`) with no-key fallback mode.

---

## 8) AI/LLM Add-on Scope (Right-Sized)
Keep this practical and portfolio-friendly:

1. **Prompted data dictionary summarizer**
   - Input: column metadata + null rates
   - Output: human-readable field explanations

2. **Doc Q&A (Mini-RAG)**
   - Retrieve from project docs
   - Answer questions like “How is missing smoking data handled?”

3. **Tool-assisted analytics assistant**
   - LLM generates request
   - Tool executes controlled SQL aggregate
   - LLM formats explanation for analyst

---

## 9) Cloud Exposure Without Over-Engineering
Even if local-first, mirror cloud practices:
- Treat `data/` as object-storage zones with Bronze/Silver/Gold semantics.
- Keep immutable raw layer and append-only ingestion paths.
- Use partition-friendly paths (`ingestion_date`, `run_id`, `snapshot_date`).
- Separate compute logic (`src/`/`sql/`) from storage layout (`data/`).
- Keep notebooks for analysis only; pipelines remain script/SQL-driven.
- Track artifacts and run metadata for reproducibility and lineage.

This gives interview-ready language for S3/OneLake/Fabric-style environments.

---

## 9.1) How to Show S3/Fabric-Style Workflow in This Repo
Use this simple narrative in README/docs/interviews:

1. **Storage-first ingestion**
   - Land source file in `data/raw/.../ingestion_date=.../`.
   - Never overwrite raw data.

2. **Pipeline transformation**
   - Batch pipeline reads raw → writes processed (`run_id` partition).
   - Validation checks run after each major transform.

3. **Curated publishing**
   - Publish curated tables by `snapshot_date`.
   - SQL marts and BI read curated/serving layers only.

4. **Notebook role (not production role)**
   - Notebooks are for EDA and analysis explanation.
   - Production logic remains in `src/` + `sql/` + orchestration docs.

### Platform Mapping (Local to Cloud)
- Local `data/raw` ↔ S3 bucket prefix / Fabric Lakehouse Files (Bronze)
- Local `data/processed` ↔ Silver tables/files
- Local `data/curated` ↔ Gold tables/files
- Local `outputs/` ↔ BI exports / artifacts

This directly demonstrates familiarity with object storage concepts and Fabric/S3-like workflows without requiring heavy cloud deployment.

---

## 10) Documentation Pack (Critical for Hiring)
At minimum include:
- `README.md` (project overview + quickstart)
- `docs/pipeline_design.md` (ETL flow + lineage)
- `docs/data_dictionary.md` (field definitions + missingness)
- `docs/storage_mapping.md` (local ↔ S3/Fabric/OneLake conventions)
- `docs/metric_definitions.md` (business/analytics KPIs)
- `docs/ai_workflow_design.md` (LLM role + controls)
- `docs/decision_log.md` (why choices were made)

---

## 11) Suggested Resume Bullets (After Completion)
- Designed and implemented an end-to-end healthcare data pipeline (raw → curated) with documented data quality checks.
- Built SQL analytics marts using CTEs, joins, window functions, and validation queries to support reporting.
- Developed Python-based data cleaning and feature workflows with reproducible project structure and testing.
- Delivered an AI-assisted analytics prototype (prompt + retrieval + tool-calling pattern) integrated with project documentation and query outputs.
- Produced dashboard/reporting artifacts to communicate risk-factor insights to non-technical stakeholders.

---

## 12) Immediate Next Step (Implementation In Progress)
Before implementation, align on these decisions:
1. Primary target variable for deep analysis (`Biopsy` recommended).
2. Preferred dashboard stack (Power BI vs Streamlit).
3. AI add-on depth (simple prompt workflow vs mini-RAG + tool calling).
4. Timeline (2-week fast track vs 3-week full version).

Current status: folder skeleton + SQL pipeline stubs are now included; next step is to run with the full dataset and iterate validations/models.

---

## 13) Quickstart (Now You Can Run Locally)

### 1. Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run SQL + data-structure pipeline
```bash
python -m src.pipeline.run_sql --config configs/pipeline.yml
```

This command will:
- read sample CSV (`data/samples/cervical_cancer_sample.csv`)
- normalize column names
- build `raw_cervical_cancer` and `stg_patients`
- build marts (`mart_target_prevalence`, `mart_risk_by_age`)
- build validation tables (`check_null_rates`, `check_range_violations`, `check_consistency_violations`)
- save results in DuckDB file: `data/processed/cervical_cancer.duckdb`

### 3. Optional: inspect output quickly
```bash
python - <<'PY'
import duckdb
con = duckdb.connect('data/processed/cervical_cancer.duckdb')
print(con.sql('show tables').df())
print(con.sql('select * from mart_target_prevalence').df())
PY
```
