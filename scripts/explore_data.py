import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

products = pd.read_csv("data/products.csv")
obs = pd.read_csv("data/price_observations.csv", parse_dates=["observed_at"])

print("=== SHAPE ===")
print("products:", products.shape, "| observations:", obs.shape)

print("\n=== NULL COUNTS ===")
print(products.isnull().sum())
print(obs.isnull().sum())

print("\n=== DUPLICATES (same product, same day) ===")
print(obs.duplicated(subset=["product_id", "observed_at"]).sum())

print("\n=== DATE RANGE ===")
print(obs["observed_at"].min().date(), "to", obs["observed_at"].max().date())
print("days per product:", obs.groupby("product_id").size().unique())

print("\n=== PRICE CHECKS ===")
merged = obs.merge(products, on="product_id")
print("prices above MRP:", (merged["selling_price"] > merged["mrp"]).sum())
print("prices <= 0:", (merged["selling_price"] <= 0).sum())
print(obs["selling_price"].describe())

print("\n=== PRODUCTS PER CATEGORY ===")
print(products["category"].value_counts())

sale_start = pd.Timestamp("2026-10-04")
fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharex=True)
for ax, behaviour in zip(axes, ["genuine", "inflated", "flat"]):
    pid = obs.loc[obs["true_behaviour"] == behaviour, "product_id"].iloc[0]
    d = obs[obs["product_id"] == pid]
    ax.plot(d["observed_at"], d["selling_price"])
    ax.axvline(sale_start, color="red", linestyle="--", label="sale starts")
    ax.set_title(f"{behaviour} (product {pid})")
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylabel("price (INR)")
axes[0].legend()
plt.tight_layout()
plt.savefig("docs/price_patterns.png", dpi=120)
print("\nChart saved: docs/price_patterns.png")
