-- Label summary: advertised vs real discount
SELECT label, COUNT(*) AS products,
       AVG(advertised_discount_pct) AS avg_advertised_pct,
       AVG(real_reduction_median_pct) AS avg_real_reduction_pct,
       AVG(gap_pp) AS avg_gap_pp
FROM product_classification
GROUP BY label
ORDER BY products DESC;
-----
-- Confusion matrix against the answer key
SELECT true_behaviour, label, COUNT(*) AS products
FROM product_classification
GROUP BY true_behaviour, label
ORDER BY true_behaviour, label;
-----
-- Category comparison
SELECT p.category, COUNT(*) AS products,
       SUM(CASE WHEN c.label = 'genuine' THEN 1 ELSE 0 END) AS genuine,
       SUM(CASE WHEN c.label = 'inflated_then_discounted' THEN 1 ELSE 0 END) AS inflated,
       AVG(c.advertised_discount_pct) AS avg_advertised_pct,
       AVG(c.real_reduction_median_pct) AS avg_real_reduction_pct
FROM product_classification c
JOIN products p USING (product_id)
GROUP BY p.category
ORDER BY avg_real_reduction_pct DESC;
-----
-- Top 10 offers to review: big advertised claim, little real saving
SELECT product_id, label, ROUND(sale_price) AS sale_price, ROUND(baseline_median) AS baseline_median,
       advertised_discount_pct, real_reduction_median_pct, gap_pp
FROM product_classification
WHERE advertised_discount_pct >= 30 AND real_reduction_median_pct < 5
ORDER BY gap_pp DESC
LIMIT 10;
