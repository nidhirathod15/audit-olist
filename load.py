import duckdb
con = duckdb.connect("olist.duckdb")
tables = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "products": "olist_products_dataset.csv",
}
for name, file in tables.items():
    con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_csv_auto('data/{file}')")
    print(name, con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0])