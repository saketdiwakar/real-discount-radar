import sqlite3
import pandas as pd

conn = sqlite3.connect("data/discount_radar.db")
conn.executescript(open("sql/01_classify.sql", encoding="utf-8").read())

for i, q in enumerate(open("sql/02_summary.sql", encoding="utf-8").read().split("-----"), 1):
    q = q.strip()
    if q:
        print(f"\n=== QUERY {i} ===")
        print(pd.read_sql(q, conn).round(2).to_string(index=False))

sql_df = pd.read_sql("SELECT product_id, label FROM product_classification", conn)
py_df = pd.read_csv("data/product_classification.csv")[["product_id", "label"]]
m = sql_df.merge(py_df, on="product_id", suffixes=("_sql", "_python"))
print("\n=== SQL vs PYTHON AGREEMENT ===")
print("products compared:", len(m), "| agree:", int((m.label_sql == m.label_python).sum()))
conn.close()
