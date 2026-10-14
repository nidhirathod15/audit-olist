WITH items AS (
  SELECT order_id, SUM(price + freight_value) AS items_total
  FROM order_items GROUP BY order_id),
pays AS (
  SELECT order_id, SUM(payment_value) AS paid
  FROM order_payments GROUP BY order_id),
d AS (
  SELECT o.order_id, o.order_status,
         COALESCE(p.paid,0) - COALESCE(i.items_total,0) AS diff
  FROM orders o
  LEFT JOIN items i USING (order_id)
  LEFT JOIN pays p USING (order_id))
SELECT order_status,
       COUNT(*) AS orders,
       SUM(CASE WHEN ABS(diff) > 1 THEN 1 ELSE 0 END) AS mismatched,
       ROUND(SUM(CASE WHEN ABS(diff) > 1 THEN diff ELSE 0 END), 2) AS net_difference
FROM d
GROUP BY order_status
ORDER BY mismatched DESC;