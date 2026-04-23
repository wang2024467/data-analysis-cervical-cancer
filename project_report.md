# Cervical Cancer Risk Data Project Research Report

## Abstract
Using the UCI Cervical Cancer Risk Factors dataset, this study develops an end-to-end workflow that covers data ingestion, schema standardization, SQL layered modeling, data quality gates, machine learning model comparison, and BI delivery. The objective is not to optimize a single metric in isolation, but to establish a reproducible, auditable, and decision-oriented analytical framework. Under realistic screening constraints, the study focuses on how data quality and class imbalance influence model behavior, and systematically compares Logistic Regression, Random Forest, LightGBM, and XGBoost under two settings: retaining inconsistent records versus removing inconsistent records.

## 1. Background and Problem Definition
Cervical cancer screening tasks are typically characterized by low positive prevalence, potential label noise, and a business objective that values missed-case reduction more than raw accuracy alone. Therefore, this project defines `biopsy` as the binary target and builds a full chain from raw data to threshold recommendations. The core research question is how to combine engineering-grade data pipelines with model diagnostics to produce screening-priority recommendations that remain operationally interpretable when missingness and consistency conflicts are present.

## 2. Data and Methods
### 2.1 Data Ingestion and Schema Alignment
At runtime, the pipeline first reads the most recent CSV file from `data/raw`; when no raw file is available, it falls back to `data/samples/cervical_cancer_sample.csv`. This design supports both production freshness and local reproducibility. Before loading into DuckDB, columns are normalized and then aligned via `EXPECTED_COLUMNS`, including alias mapping and NULL backfilling for missing fields. For example, `citology` is mapped to `cytology`, preventing upstream naming variation from breaking downstream SQL and modeling stages.

### 2.2 SQL Layered Modeling
In the staging layer, `stg_patients` applies `CAST/TRY_CAST` to enforce field types and derives two risk-related features, `is_smoker` and `has_std_history`. This table acts as a standardized analytical base that isolates downstream logic from raw typing and naming noise. In the marts layer, `mart_target_prevalence` quantifies target prevalence and class imbalance, while `mart_risk_by_age` outputs age-segmented `biopsy_rate`, `std_history_rate`, and `smoker_rate` for population-level risk interpretation.

### 2.3 Data Quality Control and Gate Strategy
Quality control includes null-rate checks, range checks, and consistency checks. Null-rate checks control core field usability; range checks detect implausible values; consistency checks identify structural conflicts such as `stds=0` with `stds_number>0`, and potential label contradictions where `biopsy=1` while all three screening indicators are zero. Gate thresholds are configured as `max_null_rate<=0.25`, range violations not exceeding 0, and consistency violations not exceeding 10. A fail-fast policy is used so that any threshold breach stops the pipeline before model training.

### 2.4 Modeling and Evaluation Framework
Modeling uses `biopsy` as the target and all non-diagnostic fields as predictors. Numeric preprocessing is median imputation, and data splitting uses stratified `train_test_split(test_size=0.2, random_state=42)`. Candidate models include Logistic Regression, Random Forest, LightGBM, and XGBoost. Evaluation spans accuracy, precision, recall, f1, and roc_auc, and is complemented by threshold decision analysis, error slicing, and calibration analysis. Because consistency-conflict records may affect label trustworthiness, two controlled experiments are conducted: one retaining inconsistent records and one removing them.

## 3. Experimental Results
### 3.1 Data Statistics and Quality Outcomes
The full dataset includes 858 rows, with `biopsy_rate=0.0641`, indicating substantial class imbalance. Age-segment analysis shows the highest `biopsy_rate` in `45_plus` (0.1739), though the subgroup is small and should be interpreted cautiously. Quality checks show the highest null rate in `stds` at approximately 0.1224, still below the gate threshold; range violations are zero; and six potential label-conflict records are detected in consistency checks, within the configured allowance.

### 3.2 Four-Model Comparison in Experiment A (Retain Inconsistent Records)
Under retained inconsistent records (n=858), Logistic Regression achieves `recall=0.4545` and `f1=0.2439`, showing strong positive-case capture and making it a practical baseline for screening-priority workflows, although its `precision=0.1667` implies a heavier false-positive burden. Random Forest reaches `precision=0.5000`, substantially higher than Logistic Regression, indicating conservative positive labeling; however, its `recall=0.0909` suggests a higher miss risk, which can conflict with screening-first objectives. LightGBM records the highest `roc_auc=0.6968`, indicating better ranking capacity, but its default-point `recall=0.0909` and `f1=0.1333` remain limited, showing that strong ranking does not automatically translate to high recall at the operating threshold. XGBoost yields `precision=0`, `recall=0`, and `f1=0`, suggesting failure to form an effective positive boundary under current sample scale and imbalance, likely due to threshold mismatch and insufficient tuning under constrained data.

### 3.3 Four-Model Comparison in Experiment B (Remove Inconsistent Records)
After removing inconsistent records (n=852), Random Forest ranks first by `f1=0.1667` and keeps `precision=0.5000`, indicating better adaptation to a cleaner distribution in terms of false-positive control, though `recall=0.1000` remains low. Logistic Regression maintains higher recall than tree models (`recall=0.3000`) but drops to `precision=0.0857`, implying increased false alarms when inconsistencies are removed. LightGBM remains intermediate (`precision=0.2000`, `recall=0.1000`, `f1=0.1333`) with balanced but non-leading behavior. XGBoost again fails to identify positives, indicating inadequate stability for current project conditions unless accompanied by stronger resampling and hyperparameter optimization.

### 3.4 Cross-Experiment Interpretation
Comparing both experiments shows that data-cleaning policy materially shifts the recall-precision trade-off. Retaining conflict records favors recall-oriented behavior, especially for Logistic Regression, while removing conflicts tends to favor precision-oriented behavior, especially for Random Forest. If the business objective is to reduce missed high-risk patients, higher-recall configurations should be prioritized with threshold tuning to manage false positives. If the objective is to reduce follow-up burden, higher-precision tree-based configurations may be preferred, but with explicit acceptance of additional misses.

## 4. Engineering Implementation and Deliverability
From an engineering perspective, the project demonstrates a runnable, traceable, and deliverable system. The workflow is YAML-parameterized, run logs include `run_id` and quality summaries, SQL execution order is deterministic, and quality gates interrupt execution immediately on threshold breaches. The modeling script supports parameterized outputs and automatically generates threshold decision tables, error-slice tables, calibration tables, one-page KPI tables, and model cards. In parallel, the export module writes key DuckDB outputs to Power BI-ready CSV files, shortening the path from model experimentation to stakeholder-facing reporting.

## 5. Discussion
Results indicate that in small, imbalanced medical-screening datasets, model quality cannot be judged apart from operational goals. Logistic Regression offers stronger recall and interpretability and is suitable for front-end risk triage. Random Forest offers stronger precision and stability and is better aligned with resource-constrained conservative screening. LightGBM shows promising ranking ability but insufficient threshold-level conversion under current settings. XGBoost remains unstable in the present setup and should not be a primary candidate without deeper tuning. More importantly, the project contributes a sustainable evaluation framework that upgrades model selection from one-off score comparison to joint threshold-error-cost decision design.

## 6. Conclusion
This study establishes a practical end-to-end cervical cancer risk pipeline that integrates data processing, SQL analytics, quality governance, model comparison, and reporting delivery. Under current evidence, a recall-oriented Logistic Regression setup is more suitable when minimizing missed screenings is the priority, whereas Random Forest is more suitable when controlling false positives is primary. Future work should focus on label governance, external validation, resampling and hyperparameter optimization, and cost-aware threshold selection to further improve reliability and real-world interpretability.

3. No external validation cohort; add temporal/out-of-site validation.
4. Production hardening: model registry, drift monitoring, scheduled retraining, audit trails.
5. Business coupling: map thresholds to follow-up cost and miss-detection risk via decision curves.

## 7) Executive Summary
The project already demonstrates a production-style foundation: schema-aligned ingestion, SQL analytics marts, explicit quality gates, configurable model training, diagnostics, and BI exports. The highest-value next iteration is improving label governance while preserving a recall-aware screening strategy.

