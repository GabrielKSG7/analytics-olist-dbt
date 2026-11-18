with orders as (select * from {{ ref('stg_orders') }}),

itens as (
    select
        order_id,
        count(*)            as qtd_itens,
        sum(price)          as receita_produtos,
        sum(freight_value)  as frete
    from {{ ref('stg_order_items') }}
    group by 1
),

pagamentos as (
    select order_id, sum(payment_value) as valor_pago
    from {{ ref('stg_payments') }}
    group by 1
),

avaliacoes as (
    select order_id, avg(review_score) as nota_media
    from {{ ref('stg_reviews') }}
    group by 1
)

select
    o.order_id,
    o.customer_id,
    o.order_status,
    o.purchased_at,
    date_trunc('month', o.purchased_at)                          as mes_compra,
    coalesce(i.receita_produtos, 0) + coalesce(i.frete, 0)       as receita_total,
    coalesce(i.qtd_itens, 0)                                     as qtd_itens,
    p.valor_pago,
    a.nota_media,
    date_diff('day', o.purchased_at, o.delivered_at)             as dias_entrega,
    case when o.delivered_at <= o.estimated_delivery_at
         then 1 else 0 end                                       as entregue_no_prazo
from orders o
left join itens       i on o.order_id = i.order_id
left join pagamentos  p on o.order_id = p.order_id
left join avaliacoes  a on o.order_id = a.order_id
