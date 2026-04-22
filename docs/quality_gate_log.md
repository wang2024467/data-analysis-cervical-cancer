# Quality Gate Log

Track threshold changes for traceability.

## Current (Strict)
- max_null_rate: 0.25
- allow_range_violations: 0
- allow_consistency_violations: 0
- intent: production-like strict validation

## Exploratory Profile (Suggested)
- max_null_rate: 0.25
- allow_range_violations: 0
- allow_consistency_violations: 10
- intent: allow known small inconsistencies while continuing model experimentation

## Notes
- Any threshold relaxation should be logged with date, reason, and owner.
