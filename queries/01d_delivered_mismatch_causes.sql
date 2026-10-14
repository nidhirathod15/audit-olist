WITH items AS (
  SELECT order_id, SUM(price + freight_value) AS items_total
  FROM order_items GROUP BY order_id),
pays AS (
  SELECT order_id, SUM(payment_value) AS paid,
         MAX(payment_installments) AS max_inst,
         COUNT(DISTINCT payment_type) AS payment_types
  FROM order_payments GROUP BY order_id)
SELECT CASE WHEN p.max_inst > 1 THEN 'instalments' ELSE 'single payment' END AS grp,
       p.payment_types,
       COUNT(*) AS orders,
       ROUND(AVG(p.paid - i.items_total), 2) AS avg_difference
FROM orders o
JOIN items i USING (order_id)
JOIN pays p USING (order_id)
WHERE o.order_status = 'delivered' AND ABS(p.paid - i.items_total) > 1
GROUP BY grp, p.payment_types
ORDER BY orders DESC;