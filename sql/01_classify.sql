-- Baseline = 28 days before the sale starts (2026-10-04). Median = average of the 14th and 15th ranked prices.
DROP TABLE IF EXISTS product_classification;
CREATE TABLE product_classification AS
WITH base AS (
    SELECT product_id, selling_price,
           ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY observed_at)    AS day_n,
           ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY selling_price)  AS price_rank
    FROM price_observations
    WHERE observed_at >= date('2026-10-04', '-28 days')
      AND observed_at <  '2026-10-04'
),
base_stats AS (
    SELECT product_id,
           AVG(selling_price) AS baseline_mean,
           MIN(selling_price) AS baseline_min,
           AVG(CASE WHEN price_rank IN (14, 15) THEN selling_price END) AS baseline_median,
           (AVG(CASE WHEN day_n > 18  THEN selling_price END) /
            AVG(CASE WHEN day_n <= 18 THEN selling_price END) - 1) * 100.0 AS runup_pct
    FROM base
    GROUP BY product_id
),
sale_stats AS (
    SELECT product_id,
           AVG(selling_price) AS sale_price,
           AVG(advertised_discount_pct) AS advertised_discount_pct
    FROM price_observations
    WHERE observed_at >= '2026-10-04'
    GROUP BY product_id
),
truth AS (
    SELECT product_id, MAX(true_behaviour) AS tb
    FROM price_observations
    GROUP BY product_id
),
scored AS (
    SELECT b.product_id, b.baseline_mean, b.baseline_median, b.baseline_min,
           s.sale_price, s.advertised_discount_pct, b.runup_pct,
           (b.baseline_median - s.sale_price) * 100.0 / b.baseline_median AS real_reduction_median_pct,
           t.tb
    FROM base_stats b
    JOIN sale_stats s USING (product_id)
    JOIN truth t USING (product_id)
)
SELECT product_id, baseline_mean, baseline_median, baseline_min, sale_price,
       runup_pct, real_reduction_median_pct, advertised_discount_pct,
       advertised_discount_pct - real_reduction_median_pct AS gap_pp,
       CASE WHEN runup_pct >= 8 AND real_reduction_median_pct < 5 THEN 'inflated_then_discounted'
            WHEN real_reduction_median_pct >= 10 THEN 'genuine'
            ELSE 'marginal' END AS label,
       CASE tb WHEN 'flat' THEN 'marginal'
               WHEN 'inflated' THEN 'inflated_then_discounted'
               ELSE tb END AS true_behaviour
FROM scored;
