CREATE OR REPLACE TABLE check_null_rates AS
SELECT 'age' AS column_name, AVG(CASE WHEN age IS NULL THEN 1 ELSE 0 END) AS null_rate FROM stg_patients
UNION ALL
SELECT 'number_of_sexual_partners', AVG(CASE WHEN number_of_sexual_partners IS NULL THEN 1 ELSE 0 END) FROM stg_patients
UNION ALL
SELECT 'first_sexual_intercourse', AVG(CASE WHEN first_sexual_intercourse IS NULL THEN 1 ELSE 0 END) FROM stg_patients
UNION ALL
SELECT 'num_of_pregnancies', AVG(CASE WHEN num_of_pregnancies IS NULL THEN 1 ELSE 0 END) FROM stg_patients
UNION ALL
SELECT 'smokes', AVG(CASE WHEN smokes IS NULL THEN 1 ELSE 0 END) FROM stg_patients
UNION ALL
SELECT 'stds', AVG(CASE WHEN stds IS NULL THEN 1 ELSE 0 END) FROM stg_patients
UNION ALL
SELECT 'biopsy', AVG(CASE WHEN biopsy IS NULL THEN 1 ELSE 0 END) FROM stg_patients;
