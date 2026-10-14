SELECT o.order_id, o.order_status, o.order_purchase_timestamp
FROM orders o
LEFT JOIN order_payments p USING (order_id)
WHERE o.order_status = 'delivered' AND p.order_id IS NULL;