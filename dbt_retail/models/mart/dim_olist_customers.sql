with customers as (
    select * from {{ ref('stg_olist_customers') }}
)

select
    customer_id,
    customer_unique_id,
    city,
    state,
    zip_code
from customers