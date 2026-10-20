{{ config(materialized='table') }}

with days as (
    select
        cast(generate_series(
            '2010-01-01'::timestamp,
            '2030-12-31'::timestamp,
            '1 day'::interval
        ) as date) as date_day
)

select date_day
from days