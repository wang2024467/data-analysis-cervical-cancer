# Metric Definitions (Template)

## Core Metrics

### 1) biopsy_rate
- Definition: mean of `biopsy` (0/1) in the selected population.
- SQL source: `mart_target_prevalence`.
- Use: baseline prevalence for target planning and class imbalance awareness.

### 2) hinselmann_rate / schiller_rate / cytology_rate
- Definition: mean of each target indicator (0/1).
- SQL source: `mart_target_prevalence`.
- Use: screening-test positivity comparison.

### 3) std_history_rate
- Definition: mean of `has_std_history` by age segment.
- SQL source: `mart_risk_by_age`.
- Use: contextual risk interpretation.

### 4) smoker_rate
- Definition: mean of `is_smoker` by age segment.
- SQL source: `mart_risk_by_age`.
- Use: behavioral risk context.

## Sample Run Snapshot (30-row synthetic sample)
- total_rows: 30
- hinselmann_rate: 0.1667
- schiller_rate: 0.2333
- cytology_rate: 0.1333
- biopsy_rate: 0.3333
- consistency conflicts: 4 (2 std-flag conflicts + 2 biopsy-label mismatches)

## Modeling Note
In this execution environment, `scikit-learn` was unavailable, so model training was skipped with trace notes emitted to `outputs/model_cards/experiment_note_*.md`.
On local VS Code after `pip install -r requirements.txt`, baseline and advanced models should run as configured.
