with source as (
    select * from {{ source('olist', 'olist_reviews') }}
),

deduped as (
    select
        -- Identifiers
        review_id,
        order_id,

        -- Dimensions and Metrics
        cast(review_score as integer) as csat_score,
        review_comment_title,
        review_comment_message,

        -- Timestamps
        cast(review_creation_date as timestamp) as review_created_at,
        cast(review_answer_timestamp as timestamp) as review_answered_at,

        -- Deduplication logic
        row_number() over (partition by order_id order by review_creation_date desc) as rn
    from source
)

select
    review_id,
    order_id,
    csat_score,
    review_comment_title,
    review_comment_message,
    review_created_at,
    review_answered_at
from deduped
where rn = 1