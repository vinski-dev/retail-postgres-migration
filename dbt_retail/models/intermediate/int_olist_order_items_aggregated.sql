with order_items as (
    select * from {{ ref('stg_olist_order_items') }}
)

select
    order_id,
    count(order_item_id) as total_items,
    sum(item_price) as total_order_price,
    sum(freight_value) as total_freight_value,
    sum(total_item_value) as total_order_value
from order_items
group by 1