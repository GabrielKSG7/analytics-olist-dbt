with source as (select * from {{ source('raw', 'order_items') }})
select
    order_id,
    order_item_id,
    product_id,
    cast(price        as double) as price,
    cast(freight_value as double) as freight_value
from source
