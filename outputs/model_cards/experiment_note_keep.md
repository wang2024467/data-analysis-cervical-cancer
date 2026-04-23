# Model Card (Biopsy Risk Classifier)

## Versioning
- data_source_table: `stg_patients`
- rows_used: 858
- drop_inconsistent: False
- target_positive_rate: 0.064103

## Feature Scope
- all non-target columns from `stg_patients` except diagnostic targets (`hinselmann`, `schiller`, `cytology`, `biopsy`)

## Candidate Models
- logistic_regression: f1=0.2439, recall=0.4545, precision=0.1667, roc_auc=0.6143
- random_forest: f1=0.1538, recall=0.0909, precision=0.5000, roc_auc=0.6669
- lightgbm: f1=0.1333, recall=0.0909, precision=0.2500, roc_auc=0.6968
- xgboost: f1=0.0000, recall=0.0000, precision=0.0000, roc_auc=0.6211

## Decision Policy
- selected_model: `logistic_regression`
- selected_threshold: 0.20
- threshold criterion: maximize recall under practical precision constraints for screening

## Limitations & Risks
- small tabular dataset; uncertainty can be high across splits
- missingness and label noise may bias estimates
- no external validation cohort included

## Ethical / Safe Use Notes
- not for standalone diagnosis; clinical review is mandatory
- monitor subgroup error rates (age/smoking/std-history) for potential harm concentration

## Intended / Out-of-Scope
- intended: screening prioritization aid in analytics sandbox
- not intended: production medical decision support without governance approvals