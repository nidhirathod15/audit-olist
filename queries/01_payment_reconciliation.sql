WITH items AS (
  SELECT order_id, SUM(price + freight_value) AS items_total
  FROM order_items GROUP BY order_id),
pays AS (
  SELECT order_id, SUM(payment_value) AS paid
  FROM order_payments GROUP BY order_id)
SELECT o.order_id, o.order_status, i.items_total, p.paid,
       ROUND(COALESCE(p.paid,0) - COALESCE(i.items_total,0), 2) AS diff
FROM orders o
LEFT JOIN items i USING (order_id)
LEFT JOIN pays p USING (order_id)
WHERE ABS(COALESCE(p.paid,0) - COALESCE(i.items_total,0)) > 1
ORDER BY ABS(diff) DESC;