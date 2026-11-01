{{ config(
     materialized = 'table'
 ) }}

WITH src AS (
    SELECT * FROM
    {{ source(
        'crmuser',
        'branch'
    ) }}
),

FINAL AS (
    SELECT
        branch_id,
        province,
        cluster_name,
        city_name,
        branch_name,
        CURRENT_TIMESTAMP AS created_date

    FROM
        src
)

SELECT * FROM FINAL
