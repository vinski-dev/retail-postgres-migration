{{ config(materialized='table') }}

with staging as (
    select * from {{ ref('stg_superstore_orders') }}
),

unique_customers as (
    select distinct
        customer_id,
        customer_name,
        segment
    from staging
    where customer_id is not null
)

select * from unique_customers