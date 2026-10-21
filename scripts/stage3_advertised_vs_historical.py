import pandas as pd

SALE_START = pd.Timestamp("2026-10-04")   # change if your sale window differs
ADV_THRESHOLD = 30                         # advertised discount (%) treated as "big claim"
LOOKBACK, MIN_OBS = 28, 21

obs = pd.read_csv("data/price_observations.csv", parse_dates=["observed_at"])
price = obs.pivot(index="observed_at", columns="product_id", values="selling_price")
adv = obs.pivot(index="observed_at", columns="product_id", values="advertised_discount_pct")

rows = []
for t in price.index[LOOKBACK:]:
    hist = price.loc[t - pd.Timedelta(days=LOOKBACK): t - pd.Timedelta(days=1)]
    df = pd.DataFrame({
        "observed_at": t,
        "current_price": price.loc[t],
        "hist_avg_28d": hist.mean(),
        "hist_obs": hist.notna().sum(),
        "advertised_discount_pct": adv.loc[t],
    })
    rows.append(df.rename_axis("product_id").reset_index())

ev = pd.concat(rows, ignore_index=True)
ev = ev[(ev.hist_obs >= MIN_OBS) & ev.current_price.notna()].copy()

ev["price_diff"] = ev.current_price - ev.hist_avg_28d
ev["hist_change_pct"] = ev.price_diff / ev.hist_avg_28d * 100
ev["hist_reduction_pct"] = -ev.hist_change_pct
ev["gap_pp"] = ev.advertised_discount_pct - ev.hist_reduction_pct
ev["below_avg"] = ev.current_price < ev.hist_avg_28d
ev["sale_period"] = ev.observed_at >= SALE_START
ev["needs_review"] = (ev.advertised_discount_pct >= ADV_THRESHOLD) & (ev.hist_reduction_pct < 5)

print("=== STAGE 2 CHECK (should match your numbers) ===")
print("evaluations:", len(ev), "| products:", ev.product_id.nunique(), "| dates:", ev.observed_at.nunique())
print("below average:", int(ev.below_avg.sum()), f"({ev.below_avg.mean()*100:.2f}%)")
print("avg reduction when below:", round(ev.loc[ev.below_avg, "hist_reduction_pct"].mean(), 2), "%")

print("\n=== ADVERTISED DISCOUNT DISTRIBUTION ===")
print(ev.advertised_discount_pct.describe().round(1))

print("\n=== ADVERTISED vs HISTORICAL, BY PERIOD ===")
g = ev.groupby("sale_period").agg(
    evaluations=("product_id", "size"),
    avg_advertised_pct=("advertised_discount_pct", "mean"),
    avg_hist_reduction_pct=("hist_reduction_pct", "mean"),
    avg_gap_pp=("gap_pp", "mean"),
    pct_below_avg=("below_avg", "mean"),
    needs_review=("needs_review", "sum"),
).round(2)
g["pct_below_avg"] = (g.pct_below_avg * 100).round(1)
g.index = g.index.map({False: "before sale", True: "sale period"})
print(g)

print("\n=== TOP 10 LARGEST GAPS DURING SALE ===")
cols = ["product_id", "observed_at", "current_price", "hist_avg_28d", "advertised_discount_pct", "hist_reduction_pct", "gap_pp"]
print(ev[ev.sale_period].sort_values("gap_pp", ascending=False)[cols].head(10).round(1).to_string(index=False))

ev.round(2).to_csv("data/real_discount_radar_stage3_comparison.csv", index=False)
g.to_csv("data/real_discount_radar_stage3_summary.csv")
print("\nSaved: data/real_discount_radar_stage3_comparison.csv and ..._summary.csv")
