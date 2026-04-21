CREATE OR REPLACE TABLE mart_target_prevalence AS
SELECT
    COUNT(*) AS total_rows,
    AVG(COALESCE(hinselmann, 0)) AS hinselmann_rate,
    AVG(COALESCE(schiller, 0)) AS schiller_rate,
    AVG(COALESCE(citology, 0)) AS citology_rate,
    AVG(COALESCE(biopsy, 0)) AS biopsy_rate
FROM stg_patients;
