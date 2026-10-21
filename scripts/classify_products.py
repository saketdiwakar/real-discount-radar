import pandas as pd

obs = pd.read_csv("data/price_observations.csv", parse_dates=["observed_at"])
sale_start = pd.Timestamp("2026-10-04")

pivot = obs.pivot(index="observed_at", columns="product_id", values="selling_price")
base = pivot[(pivot.index >= sale_start - pd.Timedelta(days=28)) & (pivot.index < sale_start)]
sale = pivot[pivot.index >= sale_start]

res = pd.DataFrame({
    "baseline_mean": base.mean(),
    "baseline_median": base.median(),
    "baseline_min": base.min(),
    "sale_price": sale.mean(),
    "runup_pct": (base.tail(10).mean() / base.head(18).mean() - 1) * 100,
})
res["real_reduction_mean_pct"] = (res.baseline_mean - res.sale_price) / res.baseline_mean * 100
res["real_reduction_median_pct"] = (res.baseline_median - res.sale_price) / res.baseline_median * 100
res["advertised_discount_pct"] = obs[obs.observed_at >= sale_start].groupby("product_id")["advertised_discount_pct"].mean()
res["gap_pp"] = res.advertised_discount_pct - res.real_reduction_median_pct

def classify(r):
    if r.runup_pct >= 8 and r.real_reduction_median_pct < 5:
        return "inflated_then_discounted"
    if r.real_reduction_median_pct >= 10:
        return "genuine"
    return "marginal"

res["label"] = res.apply(classify, axis=1)
res["true_behaviour"] = obs.groupby("product_id")["true_behaviour"].first().replace({"flat": "marginal", "inflated": "inflated_then_discounted"})

print("=== LABEL COUNTS ===")
print(res["label"].value_counts())
print("\n=== AVG REAL REDUCTION: MEAN vs MEDIAN BASELINE (by true behaviour) ===")
print(res.groupby("true_behaviour")[["real_reduction_mean_pct", "real_reduction_median_pct", "advertised_discount_pct", "gap_pp"]].mean().round(2))
print("\n=== CONFUSION MATRIX (rows = true, cols = predicted) ===")
print(pd.crosstab(res["true_behaviour"], res["label"]))
print("\naccuracy:", round((res["label"] == res["true_behaviour"]).mean() * 100, 1), "%")

res.round(2).to_csv("data/product_classification.csv")
print("\nSaved: data/product_classification.csv")
