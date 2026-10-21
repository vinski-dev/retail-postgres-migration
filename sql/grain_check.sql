--orders grain check
select
    order_id,
    count(*) as row_count
from analytics.stg_olist_orders -- Replace 'analytics' with your target schema if different
group by order_id
having count(*) > 1;

--order items grain check
select
    order_id,
    order_item_id,
    count(*) as row_count
from analytics.stg_olist_order_items
group by order_id, order_item_id
having count(*) > 1;

--product grain check
select
    product_id,
    count(*) as row_count
from analytics.stg_olist_products
group by product_id
having count(*) > 1;

--review grain check
select
    order_id,
    count(*) as row_count
from analytics.stg_olist_reviews
group by order_id
having count(*) > 1;

