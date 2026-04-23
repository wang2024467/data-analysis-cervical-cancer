# Model Card (Biopsy Risk Classifier)

## Versioning
- data_source_table: `stg_patients`
- rows_used: 852
- drop_inconsistent: True
- target_positive_rate: 0.057512

## Feature Scope
- all non-target columns from `stg_patients` except diagnostic targets (`hinselmann`, `schiller`, `cytology`, `biopsy`)

## Candidate Models
- random_forest: f1=0.1667, recall=0.1000, precision=0.5000, roc_auc=0.6255
- logistic_regression: f1=0.1333, recall=0.3000, precision=0.0857, roc_auc=0.5466
- lightgbm: f1=0.1333, recall=0.1000, precision=0.2000, roc_auc=0.5466
- xgboost: f1=0.0000, recall=0.0000, precision=0.0000, roc_auc=0.5938

## Decision Policy
- selected_model: `random_forest`
- selected_threshold: 0.05
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