from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

categories = ["Electronics", "Fashion", "Home", "Appliances"]
n_products, n_days, sale_days = 120, 45, 5
start = pd.Timestamp("2026-08-25")

products, obs = [], []
for pid in range(1, n_products + 1):
    cat = rng.choice(categories)
    mrp = int(rng.integers(500, 50000) // 100 * 100)
    base = mrp * rng.uniform(0.55, 0.85)
    behaviour = rng.choice(["genuine", "inflated", "flat"], p=[0.25, 0.40, 0.35])
    products.append((pid, f"Product {pid}", cat, mrp, f"https://example.com/p/{pid}"))

    for d in range(n_days):
        date = start + pd.Timedelta(days=d)
        in_sale = d >= n_days - sale_days
        pre_sale = n_days - sale_days - 10 <= d < n_days - sale_days
        price = base * rng.normal(1, 0.02)
        if behaviour == "genuine" and in_sale:
            price = base * rng.uniform(0.75, 0.88)
        elif behaviour == "inflated":
            if pre_sale:
                price = base * rng.uniform(1.12, 1.25)
            if in_sale:
                price = base * rng.uniform(0.97, 1.03)
        elif behaviour == "flat" and in_sale:
            price = base * rng.uniform(0.96, 1.02)
        price = round(min(price, mrp))
        obs.append((pid, date, price, round((mrp - price) / mrp * 100, 1),
                    "simulated", behaviour))

out = Path("data")
out.mkdir(exist_ok=True)

pd.DataFrame(products, columns=["product_id", "name", "category", "mrp", "url"]).to_csv(out / "products.csv", index=False)
pd.DataFrame(obs, columns=["product_id", "observed_at", "selling_price", "advertised_discount_pct", "data_quality", "true_behaviour"]).to_csv(out / "price_observations.csv", index=False)

print("Done: data/products.csv and data/price_observations.csv created")
