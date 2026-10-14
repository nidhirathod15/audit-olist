import os
import duckdb

con = duckdb.connect("olist.duckdb")
con.execute(open("queries/00_views.sql", encoding="utf-8").read())

os.makedirs("exceptions", exist_ok=True)
con.execute("""COPY (SELECT * FROM v_exceptions ORDER BY ABS(diff) DESC)
               TO 'exceptions/reconciliation_exceptions.csv' (HEADER, DELIMITER ',')""")

print(con.execute("""SELECT suggested_action, COUNT(*) AS orders, ROUND(SUM(diff), 2) AS total_diff
                     FROM v_exceptions GROUP BY 1 ORDER BY orders DESC""").df().to_string(index=False))