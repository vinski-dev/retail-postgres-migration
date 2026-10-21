with source as (
    select * from {{ source('olist', 'olist_order_items') }}
)

select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    cast(shipping_limit_date as timestamp) as shipping_limit_at,
    cast(price as numeric(10,2)) as item_price,
    cast(freight_value as numeric(10,2)) as freight_value,
    cast(price + freight_value as numeric(10,2)) as total_item_value
from source