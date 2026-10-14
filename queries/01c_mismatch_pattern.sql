WITH items AS (
  SELECT order_id, SUM(price + freight_value) AS items_total
  FROM order_items GROUP BY order_id),
pays AS (
  SELECT order_id, SUM(payment_value) AS paid
  FROM order_payments GROUP BY order_id),
d AS (
  SELECT o.order_id, o.order_status, i.items_total, p.paid
  FROM orders o
  LEFT JOIN items i USING (order_id)
  LEFT JOIN pays p USING (order_id))
SELECT order_status,
       CASE WHEN items_total IS NULL AND paid IS NOT NULL THEN 'payment, no items'
            WHEN paid IS NULL AND items_total IS NOT NULL THEN 'items, no payment'
            WHEN paid > items_total THEN 'paid more than items'
            ELSE 'paid less than items' END AS pattern,
       COUNT(*) AS orders,
       ROUND(SUM(COALESCE(paid,0) - COALESCE(items_total,0)), 2) AS net_difference
FROM d
WHERE ABS(COALESCE(paid,0) - COALESCE(items_total,0)) > 1
GROUP BY order_status, pattern
ORDER BY orders DESC;