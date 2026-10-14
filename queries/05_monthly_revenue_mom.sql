WITH m AS (
  SELECT date_trunc('month', o.order_purchase_timestamp) AS month,
         SUM(oi.price + oi.freight_value) AS revenue
  FROM orders o JOIN order_items oi USING (order_id)
  WHERE o.order_status <> 'canceled'
  GROUP BY 1)
SELECT month, ROUND(revenue, 0) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / LAG(revenue) OVER (ORDER BY month), 1) AS mom_pct
FROM m ORDER BY month;