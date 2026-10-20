{{ config(materialized='table') }}

with staging as (
    select * from {{ ref('stg_superstore_orders') }}
)

select
    -- Identifiers (Foreign Keys)
    order_id,
    customer_id,
    product_id,
    postal_code,

    -- Dates & Attributes
    order_date,
    ship_date,
    ship_mode,

    -- Metrics
    sales,
    quantity,
    discount,
    profit,

    -- Audit
    _batch_id,
    _loaded_at
from staging