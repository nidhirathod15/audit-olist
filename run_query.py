import sys
import duckdb
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

con = duckdb.connect("olist.duckdb", read_only=True)
sql = open(sys.argv[1], encoding="utf-8").read()
df = con.execute(sql).df()
print(f"{len(df)} rows\n")
print(df.head(20).to_string(index=False))