CREATE OR REPLACE TABLE stg_patients AS
SELECT
    CAST(age AS INTEGER) AS age,
    TRY_CAST(number_of_sexual_partners AS DOUBLE) AS number_of_sexual_partners,
    TRY_CAST(first_sexual_intercourse AS DOUBLE) AS first_sexual_intercourse,
    TRY_CAST(num_of_pregnancies AS DOUBLE) AS num_of_pregnancies,
    TRY_CAST(smokes AS INTEGER) AS smokes,
    TRY_CAST(stds AS INTEGER) AS stds,
    TRY_CAST(stds_number AS DOUBLE) AS stds_number,
    TRY_CAST(dx_cancer AS INTEGER) AS dx_cancer,
    TRY_CAST(dx_hpv AS INTEGER) AS dx_hpv,
    TRY_CAST(hinselmann AS INTEGER) AS hinselmann,
    TRY_CAST(schiller AS INTEGER) AS schiller,
    TRY_CAST(citology AS INTEGER) AS citology,
    TRY_CAST(biopsy AS INTEGER) AS biopsy,
    CASE WHEN TRY_CAST(smokes AS INTEGER) = 1 THEN 1 ELSE 0 END AS is_smoker,
    CASE WHEN TRY_CAST(stds AS INTEGER) = 1 OR TRY_CAST(stds_number AS DOUBLE) > 0 THEN 1 ELSE 0 END AS has_std_history
FROM raw_cervical_cancer;
