with source as (select * from {{ source('raw', 'customers') }})
select
    customer_id,
    customer_unique_id,
    customer_city,
    upper(customer_state) as customer_state
from source
