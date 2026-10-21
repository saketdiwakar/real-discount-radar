import sqlite3
import pandas as pd

conn = sqlite3.connect("data/discount_radar.db")

summary = pd.read_sql("""
    SELECT p.product_id, p.name, p.category, p.mrp,
           c.baseline_median, c.baseline_mean, c.baseline_min, c.sale_price,
           c.runup_pct, c.advertised_discount_pct, c.real_reduction_median_pct,
           c.gap_pp, c.label,
           CASE WHEN c.advertised_discount_pct >= 30 AND c.real_reduction_median_pct < 5
                THEN 'Review' ELSE 'OK' END AS review_flag
    FROM product_classification c
    JOIN products p USING (product_id)
""", conn)
summary.round(2).to_csv("data/powerbi_product_summary.csv", index=False)

daily = pd.read_sql("""
    SELECT o.product_id, p.name, p.category, o.observed_at, o.selling_price,
           o.advertised_discount_pct, p.mrp, c.label,
           CASE WHEN o.observed_at >= '2026-10-04' THEN 'Sale' ELSE 'Pre-sale' END AS period
    FROM price_observations o
    JOIN products p USING (product_id)
    JOIN product_classification c USING (product_id)
""", conn)
daily.to_csv("data/powerbi_daily_prices.csv", index=False)

print("summary rows:", len(summary), "| daily rows:", len(daily))
print(summary.review_flag.value_counts())
conn.close()
