-- Agregado pronto para o dashboard: métricas de negócio por mês.
with f as (select * from {{ ref('fct_orders') }})
select
    mes_compra,
    count(*)                as pedidos,
    sum(receita_total)      as receita_total,
    avg(dias_entrega)       as media_dias_entrega,
    avg(entregue_no_prazo)  as taxa_entrega_no_prazo,
    avg(nota_media)         as nota_media
from f
where order_status = 'delivered'
group by 1
order by 1
