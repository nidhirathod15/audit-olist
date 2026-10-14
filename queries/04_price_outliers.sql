WITH x AS (
  SELECT oi.order_id, pr.product_category_name AS category, oi.price,
         AVG(oi.price) OVER (PARTITION BY pr.product_category_name) AS mu,
         STDDEV_SAMP(oi.price) OVER (PARTITION BY pr.product_category_name) AS sd
  FROM order_items oi JOIN products pr USING (product_id))
SELECT order_id, category, price, ROUND((price - mu) / sd, 1) AS z_score
FROM x WHERE sd > 0 AND (price - mu) / sd > 4
ORDER BY z_score DESC;