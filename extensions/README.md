# Polyglot Extensions (Optional)

This folder adds lightweight **R + C++** demos on top of the main Python/SQL pipeline.

## 1) R statistical extension

Run:

```bash
Rscript extensions/r/eda_r_report.R data/raw/risk_factors_cervical_cancer.csv outputs/figures
```

Outputs:
- `outputs/figures/r_logit_odds_ratio.csv`
- `outputs/figures/r_predicted_risk_density.png`

## 2) C++ profiling extension (invoked by Python)

Run:

```bash
python -m src.extensions.run_cpp_profile --csv data/raw/risk_factors_cervical_cancer.csv --out outputs/tables/cpp_risk_profile.json
```

Outputs:
- `outputs/tables/cpp_risk_profile.json`

Notes:
- Requires `g++` in PATH.
- These are optional portfolio add-ons; core pipeline stays Python + SQL.
