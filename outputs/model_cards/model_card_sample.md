# Model Card (Sample Pipeline Run)

## Scope
This card documents the sample-data run and modeling workflow readiness.

## Data
- Source used: sample fallback (`data/samples/cervical_cancer_sample.csv`)
- Rows: 30
- Target analyzed: biopsy

## Data Quality Snapshot
- null gate: pass
- range gate: pass
- consistency gate: 4 issues (exploratory threshold 10 used for sample run)

## Modeling Execution Status
- keep-inconsistent experiment: skipped in this environment (missing scikit-learn)
- drop-inconsistent experiment: skipped in this environment (missing scikit-learn)
- local expected behavior: after installing `requirements.txt`, train logistic + RF + optional XGBoost/LightGBM.

## Artifacts
- outputs/model_cards/experiment_note_keep.md
- outputs/model_cards/experiment_note_drop.md
