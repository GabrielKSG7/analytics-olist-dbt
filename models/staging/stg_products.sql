with source as (select * from {{ source('raw', 'products') }})
select
    product_id,
    coalesce(product_category_name, 'desconhecida') as product_category
from source
