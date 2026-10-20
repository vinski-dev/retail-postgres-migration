with source as (
    select * from {{ source('raw_data', 'raw_superstore_orders') }}
),

deduplicated as (
    select
        *,
        -- Superstore data is line-item level. A unique record is an Order + Product.
        row_number() over (
            partition by order_id, product_id
            order by _loaded_at desc
        ) as rn
    from source
),

cleaned as (
    select
        -- Primary Keys & Identifiers
        trim(order_id) as order_id,
        trim(customer_id) as customer_id,
        trim(product_id) as product_id,

        -- Dates
        cast(order_date as date) as order_date,
        cast(ship_date as date) as ship_date,

        -- Categorical Dimensions
        trim(ship_mode) as ship_mode,
        trim(customer_name) as customer_name,
        trim(segment) as segment,
        trim(country) as country,
        trim(city) as city,
        trim(state) as state,
        trim(cast(postal_code as text)) as postal_code,
        -- trim(postal_code) as postal_code,
        trim(region) as region,
        trim(category) as category,
        trim(sub_category) as sub_category,
        trim(product_name) as product_name,

        -- Metrics (Ensure absolute numbers where appropriate)
        abs(cast(sales as numeric(10,2))) as sales,
        abs(cast(quantity as int)) as quantity,
        cast(discount as numeric(4,2)) as discount,
        cast(profit as numeric(10,2)) as profit,

        -- Audit Metadata
        _batch_id,
        _loaded_at

    from deduplicated
    where rn = 1               -- Keep only the most recent extraction per line item
      and order_id is not null -- Drop fatal errors
)

select * from cleaned