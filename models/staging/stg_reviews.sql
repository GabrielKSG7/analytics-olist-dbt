with source as (select * from {{ source('raw', 'reviews') }})
select
    review_id,
    order_id,
    cast(review_score as integer) as review_score
from source
