import sqlite3
import pandas as pd

products = pd.read_csv("data/products.csv")
obs = pd.read_csv("data/price_observations.csv")

conn = sqlite3.connect("data/discount_radar.db")
cur = conn.cursor()
cur.executescript("""
DROP TABLE IF EXISTS price_observations;
DROP TABLE IF EXISTS products;
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    mrp INTEGER NOT NULL,
    url TEXT
);
CREATE TABLE price_observations (
    product_id INTEGER NOT NULL,
    observed_at TEXT NOT NULL,
    selling_price INTEGER NOT NULL,
    advertised_discount_pct REAL,
    data_quality TEXT,
    true_behaviour TEXT,
    PRIMARY KEY (product_id, observed_at),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
""")
products.to_sql("products", conn, if_exists="append", index=False)
obs.to_sql("price_observations", conn, if_exists="append", index=False)
conn.commit()
print("products:", cur.execute("SELECT COUNT(*) FROM products").fetchone()[0])
print("observations:", cur.execute("SELECT COUNT(*) FROM price_observations").fetchone()[0])
conn.close()
