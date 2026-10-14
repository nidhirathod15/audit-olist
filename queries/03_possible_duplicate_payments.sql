SELECT order_id, payment_type, payment_value, COUNT(*) AS times
FROM order_payments
GROUP BY order_id, payment_type, payment_value
HAVING COUNT(*) > 1
ORDER BY payment_value DESC;