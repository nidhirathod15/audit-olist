SELECT r.pattern, COUNT(*) AS orders, ROUND(SUM(r.diff), 2) AS net_difference
FROM v_reconciliation r
JOIN (SELECT DISTINCT order_id
      FROM order_payments
      GROUP BY order_id, payment_type, payment_value
      HAVING COUNT(*) > 1) d USING (order_id)
GROUP BY r.pattern
ORDER BY orders DESC;