with source as (select * from {{ source('raw', 'payments') }})
select
    order_id,
    payment_type,
    cast(payment_installments as integer) as installments,
    cast(payment_value        as double)  as payment_value
from source
