CREATE OR REPLACE TABLE mart_risk_by_age AS
WITH grouped AS (
    SELECT
        CASE
            WHEN age < 25 THEN 'under_25'
            WHEN age BETWEEN 25 AND 34 THEN '25_34'
            WHEN age BETWEEN 35 AND 44 THEN '35_44'
            ELSE '45_plus'
        END AS age_group,
        biopsy,
        has_std_history,
        is_smoker
    FROM stg_patients
)
SELECT
    age_group,
    COUNT(*) AS patient_count,
    AVG(COALESCE(biopsy, 0)) AS biopsy_rate,
    AVG(COALESCE(has_std_history, 0)) AS std_history_rate,
    AVG(COALESCE(is_smoker, 0)) AS smoker_rate
FROM grouped
GROUP BY age_group
ORDER BY age_group;
