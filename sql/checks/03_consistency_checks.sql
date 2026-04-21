CREATE OR REPLACE TABLE check_consistency_violations AS
SELECT
    SUM(CASE WHEN stds = 0 AND stds_number > 0 THEN 1 ELSE 0 END) AS std_flag_conflict_rows,
    SUM(CASE WHEN biopsy = 1 AND (hinselmann = 0 AND schiller = 0 AND citology = 0) THEN 1 ELSE 0 END) AS possible_label_mismatch_rows
FROM stg_patients;
