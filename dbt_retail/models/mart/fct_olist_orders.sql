with orders as (
    select * from {{ ref('stg_olist_orders') }}
),

order_items_agg as (
    select * from {{ ref('int_olist_order_items_aggregated') }}
),

reviews as (
    select * from {{ ref('stg_olist_reviews') }}
)

select
    -- Identifiers
    o.order_id,
    o.customer_id,

    -- Dimensions
    o.order_status,

    -- Timestamps
    o.order_purchase_at,
    o.order_approved_at,
    o.order_delivered_carrier_at,
    o.order_delivered_customer_at,
    o.order_estimated_delivery_at,

    -- Financial Metrics (from intermediate)
    coalesce(i.total_items, 0) as total_items,
    coalesce(i.total_order_price, 0) as total_sales_amount,
    coalesce(i.total_freight_value, 0) as total_freight_amount,
    coalesce(i.total_order_value, 0) as total_gross_revenue,

    -- CX / Review Metrics
    r.review_id,
    r.csat_score,
    r.review_comment_title,

    -- Derived Enterprise Metric: Detractor Flag
    case
        when r.csat_score in (1, 2) then 1
        else 0
    end as is_detractor

from orders o
left join order_items_agg i
    on o.order_id = i.order_id
left join reviews r
    on o.order_id = r.order_id