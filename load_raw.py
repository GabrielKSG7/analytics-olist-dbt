"""
Carrega os dados brutos do Olist no DuckDB (schema `raw`), que e a fonte do dbt.

Dois modos:
  python load_raw.py            -> le os CSVs reais da pasta data/ (baixe do Kaggle)
  python load_raw.py --sample   -> gera um conjunto sintetico pequeno, so para
                                   testar o pipeline sem precisar baixar nada.
"""
import sys
import duckdb

DB = "olist.duckdb"

# Mapeia: tabela_raw -> nome do arquivo CSV real do Olist (Kaggle)
ARQUIVOS = {
    "orders":      "olist_orders_dataset.csv",
    "customers":   "olist_customers_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products":    "olist_products_dataset.csv",
    "payments":    "olist_order_payments_dataset.csv",
    "reviews":     "olist_order_reviews_dataset.csv",
}


def carregar_csvs():
    con = duckdb.connect(DB)
    con.execute("create schema if not exists raw")
    for tabela, arq in ARQUIVOS.items():
        caminho = f"data/{arq}"
        con.execute(
            f"create or replace table raw.{tabela} as "
            f"select * from read_csv_auto('{caminho}', header=true)"
        )
        n = con.execute(f"select count(*) from raw.{tabela}").fetchone()[0]
        print(f"raw.{tabela}: {n} linhas")
    con.close()


def gerar_amostra():
    import random
    from datetime import datetime, timedelta
    random.seed(42)
    estados = ["SP", "RJ", "MG", "RS", "PR"]
    categorias = ["cama_mesa_banho", "informatica", "moveis", "beleza", "esporte"]
    status = ["delivered", "shipped", "canceled", "invoiced", "processing"]

    customers, orders, items, products, payments, reviews = [], [], [], [], [], []
    for p in range(20):
        products.append((f"prod_{p:03d}", random.choice(categorias)))

    base = datetime(2017, 1, 1)
    for c in range(60):
        cid = f"cust_{c:04d}"
        customers.append((cid, f"uniq_{c%40:04d}", "cidade", random.choice(estados)))
        oid = f"order_{c:04d}"
        compra = base + timedelta(days=random.randint(0, 600))
        st = random.choice(status)
        entregue = compra + timedelta(days=random.randint(2, 20))
        estimada = compra + timedelta(days=random.randint(10, 25))
        orders.append((oid, cid, st,
                       compra.isoformat(),
                       entregue.isoformat() if st == "delivered" else None,
                       estimada.isoformat()))
        for it in range(random.randint(1, 3)):
            prod = random.choice(products)[0]
            preco = round(random.uniform(20, 500), 2)
            frete = round(random.uniform(5, 40), 2)
            items.append((oid, it + 1, prod, preco, frete))
            payments.append((oid, "credit_card", random.randint(1, 10), preco + frete))
        reviews.append((f"rev_{c:04d}", oid, random.randint(1, 5)))

    con = duckdb.connect(DB)
    con.execute("create schema if not exists raw")
    con.execute("create or replace table raw.customers(customer_id varchar, customer_unique_id varchar, customer_city varchar, customer_state varchar)")
    con.executemany("insert into raw.customers values (?,?,?,?)", customers)
    con.execute("create or replace table raw.orders(order_id varchar, customer_id varchar, order_status varchar, order_purchase_timestamp varchar, order_delivered_customer_date varchar, order_estimated_delivery_date varchar)")
    con.executemany("insert into raw.orders values (?,?,?,?,?,?)", orders)
    con.execute("create or replace table raw.order_items(order_id varchar, order_item_id integer, product_id varchar, price double, freight_value double)")
    con.executemany("insert into raw.order_items values (?,?,?,?,?)", items)
    con.execute("create or replace table raw.products(product_id varchar, product_category_name varchar)")
    con.executemany("insert into raw.products values (?,?)", products)
    con.execute("create or replace table raw.payments(order_id varchar, payment_type varchar, payment_installments integer, payment_value double)")
    con.executemany("insert into raw.payments values (?,?,?,?)", payments)
    con.execute("create or replace table raw.reviews(review_id varchar, order_id varchar, review_score integer)")
    con.executemany("insert into raw.reviews values (?,?,?)", reviews)
    for t in ARQUIVOS:
        n = con.execute(f"select count(*) from raw.{t}").fetchone()[0]
        print(f"raw.{t}: {n} linhas (amostra)")
    con.close()


if __name__ == "__main__":
    if "--sample" in sys.argv:
        print("Gerando dados de amostra...")
        gerar_amostra()
    else:
        print("Carregando CSVs reais de data/ ...")
        carregar_csvs()
    print("Concluido. Banco:", DB)
