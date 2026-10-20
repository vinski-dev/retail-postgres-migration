{{ config(materialized='table') }}

with staging as (
    select * from {{ ref('stg_superstore_orders') }}
),

deduplicated_products as (
    select
        product_id,
        category,
        sub_category,
        product_name,
        -- Force uniqueness on product_id by keeping only the most recently ordered name variation
        row_number() over (
            partition by product_id
            order by order_date desc
        ) as rn
    from staging
    where product_id is not null
)

select
    product_id,
    category,
    sub_category,
    product_name
from deduplicated_products
where rn = 1