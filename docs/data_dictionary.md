# Data Dictionary (Template)

## Purpose
Define canonical field names, source names, types, and business meaning.

## Recommended Columns
| canonical_name | source_aliases | dtype | description | nullable | notes |
|---|---|---|---|---|---|
| age | Age | int | Patient age | no | |
| number_of_sexual_partners | Number of sexual partners | float | Partner count | yes | |
| first_sexual_intercourse | First sexual intercourse / First sexual intercourse (age) | float | First intercourse age | yes | |
| biopsy | Biopsy | int (0/1) | Target label | yes | Primary target |

## TODO
- Expand table to all canonical columns in `EXPECTED_COLUMNS`.
- Add accepted ranges and validation ownership.
