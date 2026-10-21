with source as (
    select * from {{ source('olist', 'olist_customers') }}
)

select
    -- Identifiers
    customer_id,
    customer_unique_id,

    -- Demographics
    cast(customer_zip_code_prefix as text) as zip_code,
    customer_city as city,
    customer_state as state
from source