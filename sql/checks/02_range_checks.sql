CREATE OR REPLACE TABLE check_range_violations AS
SELECT
    SUM(CASE WHEN age < 10 OR age > 100 THEN 1 ELSE 0 END) AS invalid_age_rows,
    SUM(CASE WHEN first_sexual_intercourse < 8 OR first_sexual_intercourse > 40 THEN 1 ELSE 0 END) AS invalid_first_sexual_intercourse_rows,
    SUM(CASE WHEN num_of_pregnancies < 0 OR num_of_pregnancies > 20 THEN 1 ELSE 0 END) AS invalid_pregnancy_rows
FROM stg_patients;
