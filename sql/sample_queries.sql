-- ============================================================
-- Trino / Iceberg Sample Queries
-- Enterprise Retail Streaming Platform
-- Run against: iceberg.retail schema
-- ============================================================

-- ============================================================
-- SECTION 1: Executive & Revenue Queries
-- ============================================================

-- Q1: Live order count (last hour)
SELECT
    COUNT(*) AS order_count,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS avg_order_value
FROM iceberg.retail.orders
WHERE order_timestamp >= NOW() - INTERVAL '1' HOUR;

-- Q2: Revenue by channel (today)
SELECT
    channel,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue,
    AVG(total_amount) AS avg_order_value
FROM iceberg.retail.orders
WHERE DATE(order_timestamp) = CURRENT_DATE
GROUP BY channel
ORDER BY revenue DESC;

-- Q3: Revenue by country (today)
SELECT
    country,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue,
    AVG(total_amount) AS avg_order_value
FROM iceberg.retail.orders
WHERE DATE(order_timestamp) = CURRENT_DATE
GROUP BY country
ORDER BY revenue DESC;

-- Q4: Revenue trend by hour (last 24 hours)
SELECT
    DATE_TRUNC('hour', order_timestamp) AS hour,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue
FROM iceberg.retail.orders
WHERE order_timestamp >= NOW() - INTERVAL '24' HOUR
GROUP BY DATE_TRUNC('hour', order_timestamp)
ORDER BY hour;

-- Q5: Daily revenue vs. previous day comparison
WITH today AS (
    SELECT
        DATE(order_timestamp) AS day,
        SUM(total_amount) AS revenue
    FROM iceberg.retail.orders
    WHERE DATE(order_timestamp) = CURRENT_DATE
    GROUP BY DATE(order_timestamp)
),
yesterday AS (
    SELECT
        DATE(order_timestamp) AS day,
        SUM(total_amount) AS revenue
    FROM iceberg.retail.orders
    WHERE DATE(order_timestamp) = CURRENT_DATE - INTERVAL '1' DAY
    GROUP BY DATE(order_timestamp)
)
SELECT
    t.day,
    t.revenue AS today_revenue,
    y.revenue AS yesterday_revenue,
    t.revenue - y.revenue AS revenue_diff,
    ROUND((t.revenue - y.revenue) / y.revenue * 100, 2) AS revenue_growth_pct
FROM today t
LEFT JOIN yesterday y ON t.day = y.day + INTERVAL '1' DAY;

-- Q6: Top 10 products by revenue (last 7 days)
SELECT
    oi.product_id,
    oi.product_name,
    oi.category,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.unit_price * oi.quantity - oi.discount) AS revenue
FROM iceberg.retail.orders,
    UNNEST(order_items) AS t(oi)
WHERE order_timestamp >= NOW() - INTERVAL '7' DAY
GROUP BY oi.product_id, oi.product_name, oi.category
ORDER BY revenue DESC
LIMIT 10;

-- Q7: Average order value by country (last 30 days)
SELECT
    country,
    COUNT(*) AS total_orders,
    AVG(total_amount) AS avg_order_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_amount) AS median_order_value,
    MIN(total_amount) AS min_order,
    MAX(total_amount) AS max_order
FROM iceberg.retail.orders
WHERE order_timestamp >= NOW() - INTERVAL '30' DAY
GROUP BY country
ORDER BY avg_order_value DESC;

-- ============================================================
-- SECTION 2: Payment Health Queries
-- ============================================================

-- Q8: Payment success rate by hour (last 24 hours)
SELECT
    DATE_TRUNC('hour', payment_timestamp) AS hour,
    COUNT(*) AS total_transactions,
    COUNT(*) FILTER (WHERE payment_status = 'completed') AS successful,
    COUNT(*) FILTER (WHERE payment_status = 'failed') AS failed,
    ROUND(COUNT(*) FILTER (WHERE payment_status = 'completed') * 100.0 / COUNT(*), 2) AS success_rate_pct,
    AVG(amount) FILTER (WHERE payment_status = 'completed') AS avg_transaction_value
FROM iceberg.retail.payments
WHERE payment_timestamp >= NOW() - INTERVAL '24' HOUR
GROUP BY DATE_TRUNC('hour', payment_timestamp)
ORDER BY hour;

-- Q9: Payment failure rate by method
SELECT
    payment_method,
    COUNT(*) AS total_transactions,
    COUNT(*) FILTER (WHERE payment_status = 'failed') AS failed_count,
    ROUND(COUNT(*) FILTER (WHERE payment_status = 'failed') * 100.0 / COUNT(*), 2) AS failure_rate_pct,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM iceberg.retail.payments
WHERE payment_timestamp >= NOW() - INTERVAL '7' DAY
GROUP BY payment_method
ORDER BY failure_rate_pct DESC;

-- Q10: Payment failure reasons breakdown
SELECT
    failure_reason,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage,
    SUM(amount) FILTER (WHERE payment_status = 'failed') AS total_failed_amount
FROM iceberg.retail.payments
WHERE payment_timestamp >= NOW() - INTERVAL '7' DAY
    AND payment_status = 'failed'
GROUP BY failure_reason
ORDER BY count DESC;

-- Q11: High-risk failed payments (last 24 hours)
SELECT
    payment_id,
    order_id,
    customer_id,
    amount,
    payment_method,
    failure_reason,
    risk_score,
    payment_timestamp
FROM iceberg.retail.payments
WHERE payment_timestamp >= NOW() - INTERVAL '24' HOUR
    AND payment_status = 'failed'
    AND risk_score > 0.5
ORDER BY risk_score DESC, payment_timestamp DESC;

-- Q12: Payment reconciliation (orders without payments)
SELECT
    o.order_id,
    o.customer_id,
    o.total_amount,
    o.order_timestamp,
    o.status AS order_status,
    p.payment_id IS NULL AS missing_payment
FROM iceberg.retail.orders o
LEFT JOIN iceberg.retail.payments p ON o.order_id = p.order_id
WHERE o.order_timestamp >= NOW() - INTERVAL '24' HOUR
    AND o.status = 'completed'
    AND p.payment_id IS NULL;

-- ============================================================
-- SECTION 3: Inventory Queries
-- ============================================================

-- Q13: Current inventory snapshot (low stock products)
SELECT
    product_id,
    product_name,
    category,
    quantity_on_hand,
    reorder_point,
    warehouse_location,
    CASE
        WHEN quantity_on_hand = 0 THEN 'OUT_OF_STOCK'
        WHEN quantity_on_hand < reorder_point THEN 'LOW_STOCK'
        ELSE 'IN_STOCK'
    END AS stock_status,
    ROUND((quantity_on_hand / NULLIF(reorder_point, 0)) AS coverage_ratio
FROM iceberg.retail.inventory
WHERE quantity_on_hand < reorder_point
   OR quantity_on_hand = 0
ORDER BY quantity_on_hand ASC;

-- Q14: Products at stockout risk (coverage < 7 days)
SELECT
    product_id,
    product_name,
    category,
    quantity_on_hand,
    reorder_point,
    days_of_supply,
    CASE
        WHEN days_of_supply < 3 THEN 'CRITICAL'
        WHEN days_of_supply < 7 THEN 'URGENT'
        ELSE 'WARNING'
    END AS risk_level
FROM iceberg.retail.inventory_realtime_snapshot
WHERE days_of_supply < 14
ORDER BY days_of_supply ASC;

-- Q15: Inventory stockout events (last 7 days)
SELECT
    DATE(event_timestamp) AS day,
    COUNT(*) AS stockout_count,
    COUNT(DISTINCT product_id) AS unique_products_out,
    category
FROM iceberg.retail.inventory_events
WHERE event_type = 'inventory_stockout'
    AND event_timestamp >= NOW() - INTERVAL '7' DAY
GROUP BY DATE(event_timestamp), category
ORDER BY day DESC, stockout_count DESC;

-- Q16: Inventory turnover by category (last 30 days)
SELECT
    category,
    SUM(ABS(quantity_change)) AS total_movement,
    COUNT(*) AS movement_events,
    AVG(ABS(quantity_change)) AS avg_movement_per_event
FROM iceberg.retail.inventory_movements
WHERE event_timestamp >= NOW() - INTERVAL '30' DAY
GROUP BY category
ORDER BY total_movement DESC;

-- Q17: Reorder recommendations
SELECT
    product_id,
    product_name,
    category,
    quantity_on_hand,
    reorder_point,
    max_stock_level,
    (max_stock_level - quantity_on_hand) AS suggested_order_qty,
    supplier_id,
    lead_time_days
FROM iceberg.retail.inventory_realtime_snapshot
WHERE quantity_on_hand < reorder_point
ORDER BY (reorder_point - quantity_on_hand) DESC;

-- ============================================================
-- SECTION 4: Delivery Queries
-- ============================================================

-- Q18: Delivery SLA compliance rate by carrier (last 7 days)
SELECT
    carrier,
    COUNT(*) AS total_deliveries,
    COUNT(*) FILTER (WHERE delivery_status = 'delivered'
        AND actual_delivery_date <= estimated_delivery_date) AS on_time,
    COUNT(*) FILTER (WHERE delivery_status = 'delivered'
        AND actual_delivery_date > estimated_delivery_date) AS late,
    ROUND(COUNT(*) FILTER (WHERE delivery_status = 'delivered'
        AND actual_delivery_date <= estimated_delivery_date) * 100.0 /
        NULLIF(COUNT(*) FILTER (WHERE delivery_status = 'delivered'), 0), 2) AS sla_compliance_pct,
    AVG(actual_delivery_date - order_timestamp) FILTER (WHERE delivery_status = 'delivered')
        AS avg_delivery_hours
FROM iceberg.retail.delivery
WHERE created_at >= NOW() - INTERVAL '7' DAY
GROUP BY carrier
ORDER BY sla_compliance_pct DESC;

-- Q19: Delivery delay rate by region (last 7 days)
SELECT
    country,
    COUNT(*) AS total_deliveries,
    COUNT(*) FILTER (WHERE is_delayed = true) AS delayed_count,
    ROUND(COUNT(*) FILTER (WHERE is_delayed = true) * 100.0 / COUNT(*), 2) AS delay_rate_pct,
    AVG(delivery_delay_hours) FILTER (WHERE is_delayed = true) AS avg_delay_hours
FROM iceberg.retail.delivery
WHERE created_at >= NOW() - INTERVAL '7' DAY
GROUP BY country
ORDER BY delay_rate_pct DESC;

-- Q20: Top delay reasons
SELECT
    delay_reason,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM iceberg.retail.delivery
WHERE created_at >= NOW() - INTERVAL '7' DAY
    AND is_delayed = true
GROUP BY delay_reason
ORDER BY count DESC;

-- Q21: Orders with SLA breach
SELECT
    order_id,
    customer_id,
    carrier,
    estimated_delivery_date,
    actual_delivery_date,
    (actual_delivery_date - estimated_delivery_date) AS delay_hours,
    delay_reason
FROM iceberg.retail.delivery
WHERE delivery_status = 'delivered'
    AND actual_delivery_date > estimated_delivery_date
    AND created_at >= NOW() - INTERVAL '24' HOUR
ORDER BY (actual_delivery_date - estimated_delivery_date) DESC;

-- ============================================================
-- SECTION 5: Fraud Queries
-- ============================================================

-- Q22: Fraud alert summary by severity (today)
SELECT
    CASE
        WHEN fraud_score >= 0.8 THEN 'HIGH'
        WHEN fraud_score >= 0.5 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS severity,
    COUNT(*) AS alert_count,
    SUM(amount) AS total_amount_at_risk,
    COUNT(DISTINCT customer_id) AS affected_customers
FROM iceberg.retail.fraud_signals
WHERE fraud_timestamp >= NOW() - INTERVAL '24' HOUR
GROUP BY
    CASE
        WHEN fraud_score >= 0.8 THEN 'HIGH'
        WHEN fraud_score >= 0.5 THEN 'MEDIUM'
        ELSE 'LOW'
    END
ORDER BY
    CASE severity WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END;

-- Q23: Fraud trend by hour (last 48 hours)
SELECT
    DATE_TRUNC('hour', fraud_timestamp) AS hour,
    COUNT(*) AS fraud_count,
    COUNT(*) FILTER (WHERE fraud_score >= 0.8) AS high_risk_count,
    AVG(fraud_score) AS avg_fraud_score
FROM iceberg.retail.fraud_signals
WHERE fraud_timestamp >= NOW() - INTERVAL '48' HOUR
GROUP BY DATE_TRUNC('hour', fraud_timestamp)
ORDER BY hour;

-- Q24: Fraud by type (last 7 days)
SELECT
    fraud_type,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage,
    AVG(fraud_score) AS avg_score
FROM iceberg.retail.fraud_signals
WHERE fraud_timestamp >= NOW() - INTERVAL '7' DAY
GROUP BY fraud_type
ORDER BY count DESC;

-- Q25: High-risk transactions (score > 0.7)
SELECT
    fraud_event_id,
    order_id,
    customer_id,
    fraud_type,
    fraud_score,
    amount,
    country,
    action_taken,
    fraud_timestamp
FROM iceberg.retail.fraud_signals
WHERE fraud_score >= 0.7
    AND is_confirmed = false
ORDER BY fraud_score DESC
LIMIT 50;

-- ============================================================
-- SECTION 6: Customer Queries
-- ============================================================

-- Q26: Customer lifetime value (top 20)
SELECT
    customer_id,
    COUNT(*) AS total_orders,
    SUM(total_amount) AS lifetime_value,
    AVG(total_amount) AS avg_order_value,
    MIN(order_timestamp) AS first_order,
    MAX(order_timestamp) AS last_order,
    DATEDIFF('day', MIN(order_timestamp), CURRENT_DATE) AS customer_age_days,
    CASE
        WHEN DATEDIFF('day', MAX(order_timestamp), CURRENT_DATE) > 90 THEN 'CHURNED'
        WHEN DATEDIFF('day', MAX(order_timestamp), CURRENT_DATE) > 30 THEN 'AT_RISK'
        ELSE 'ACTIVE'
    END AS customer_status
FROM iceberg.retail.orders
WHERE status = 'completed'
GROUP BY customer_id
HAVING SUM(total_amount) > 0
ORDER BY lifetime_value DESC
LIMIT 20;

-- Q27: Repeat customer rate (last 30 days)
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(*) AS order_count
    FROM iceberg.retail.orders
    WHERE order_timestamp >= NOW() - INTERVAL '30' DAY
        AND status = 'completed'
    GROUP BY customer_id
)
SELECT
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE order_count > 1) AS repeat_customers,
    ROUND(COUNT(*) FILTER (WHERE order_count > 1) * 100.0 / COUNT(*), 2) AS repeat_rate_pct,
    COUNT(*) FILTER (WHERE order_count = 1) AS one_time_customers,
    AVG(order_count) FILTER (WHERE order_count > 1) AS avg_orders_per_repeat_customer
FROM customer_orders;

-- Q28: Customer churn analysis
SELECT
    CASE
        WHEN last_order_days_ago <= 30 THEN 'ACTIVE'
        WHEN last_order_days_ago BETWEEN 31 AND 60 THEN 'AT_RISK'
        WHEN last_order_days_ago BETWEEN 61 AND 90 THEN 'AT_RISK_CRITICAL'
        ELSE 'CHURNED'
    END AS segment,
    COUNT(*) AS customer_count,
    AVG(lifetime_value) AS avg_lifetime_value
FROM (
    SELECT
        customer_id,
        MAX(order_timestamp) AS last_order_date,
        DATEDIFF('day', MAX(order_timestamp), CURRENT_DATE) AS last_order_days_ago,
        SUM(total_amount) AS lifetime_value
    FROM iceberg.retail.orders
    GROUP BY customer_id
) sub
GROUP BY
    CASE
        WHEN last_order_days_ago <= 30 THEN 'ACTIVE'
        WHEN last_order_days_ago BETWEEN 31 AND 60 THEN 'AT_RISK'
        WHEN last_order_days_ago BETWEEN 61 AND 90 THEN 'AT_RISK_CRITICAL'
        ELSE 'CHURNED'
    END
ORDER BY
    CASE
        WHEN segment = 'ACTIVE' THEN 1
        WHEN segment = 'AT_RISK' THEN 2
        WHEN segment = 'AT_RISK_CRITICAL' THEN 3
        ELSE 4
    END;

-- Q29: Customer 360 profile (specific customer)
SELECT
    c.customer_id,
    c.email,
    c.first_name,
    c.last_name,
    c.loyalty_tier,
    c.customer_segment,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COALESCE(SUM(o.total_amount), 0) AS lifetime_value,
    COUNT(DISTINCT p.payment_id) AS total_payments,
    COUNT(DISTINCT d.delivery_id) FILTER (WHERE d.status = 'delivered') AS successful_deliveries,
    AVG(o.total_amount) AS avg_order_value,
    MIN(o.order_timestamp) AS first_order_date,
    MAX(o.order_timestamp) AS last_order_date
FROM iceberg.retail.customers c
LEFT JOIN iceberg.retail.orders o ON c.customer_id = o.customer_id
LEFT JOIN iceberg.retail.payments p ON c.customer_id = p.customer_id
LEFT JOIN iceberg.retail.delivery d ON c.customer_id = d.customer_id
WHERE c.customer_id = 'CUST-EXAMPLE'
GROUP BY c.customer_id, c.email, c.first_name, c.last_name, c.loyalty_tier, c.customer_segment;

-- ============================================================
-- SECTION 7: Recommendation Analytics
-- ============================================================

-- Q30: Recommendation CTR by type (last 7 days)
SELECT
    recommendation_type,
    COUNT(*) AS impressions,
    COUNT(*) FILTER (WHERE event_type = 'recommendation_click') AS clicks,
    COUNT(*) FILTER (WHERE event_type = 'recommendation_purchase') AS purchases,
    ROUND(COUNT(*) FILTER (WHERE event_type = 'recommendation_click') * 100.0 / COUNT(*), 2) AS ctr_pct,
    ROUND(COUNT(*) FILTER (WHERE event_type = 'recommendation_purchase') * 100.0 /
        NULLIF(COUNT(*) FILTER (WHERE event_type = 'recommendation_click'), 0), 2) AS conversion_rate_pct,
    SUM(revenue_attributed) AS attributed_revenue
FROM iceberg.retail.recommendations
WHERE event_timestamp >= NOW() - INTERVAL '7' DAY
GROUP BY recommendation_type
ORDER BY ctr_pct DESC;

-- Q31: Revenue from recommendations vs. organic
SELECT
    CASE
        WHEN event_type = 'recommendation_purchase' THEN 'FROM_RECOMMENDATION'
        ELSE 'ORGANIC'
    END AS source,
    COUNT(DISTINCT customer_id) AS customers,
    SUM(revenue_attributed) AS revenue,
    ROUND(SUM(revenue_attributed) * 100.0 /
        SUM(SUM(revenue_attributed)) OVER (), 2) AS revenue_share_pct
FROM iceberg.retail.recommendations
WHERE event_timestamp >= NOW() - INTERVAL '7' DAY
    AND revenue_attributed > 0
GROUP BY
    CASE
        WHEN event_type = 'recommendation_purchase' THEN 'FROM_RECOMMENDATION'
        ELSE 'ORGANIC'
    END;

-- Q32: Top recommended products
SELECT
    product_id,
    product_name,
    COUNT(*) FILTER (WHERE event_type = 'recommendation_impression') AS impressions,
    COUNT(*) FILTER (WHERE event_type = 'recommendation_click') AS clicks,
    COUNT(*) FILTER (WHERE event_type = 'recommendation_purchase') AS purchases,
    ROUND(COUNT(*) FILTER (WHERE event_type = 'recommendation_click') * 100.0 /
        NULLIF(COUNT(*) FILTER (WHERE event_type = 'recommendation_impression'), 0), 2) AS ctr_pct,
    SUM(revenue_attributed) AS attributed_revenue
FROM iceberg.retail.recommendations
WHERE event_timestamp >= NOW() - INTERVAL '7' DAY
GROUP BY product_id, product_name
ORDER BY impressions DESC
LIMIT 20;

-- ============================================================
-- SECTION 8: Aggregations & Reporting
-- ============================================================

-- Q33: Daily aggregation metrics (last 30 days)
SELECT
    DATE(order_timestamp) AS day,
    country,
    COUNT(*) AS total_orders,
    SUM(total_amount) AS gross_revenue,
    COUNT(DISTINCT customer_id) AS unique_customers,
    AVG(total_amount) AS avg_order_value,
    COUNT(DISTINCT customer_id) FILTER (WHERE order_timestamp = (
        SELECT MIN(order_timestamp) FROM iceberg.retail.orders o2
        WHERE o2.customer_id = iceberg.retail.orders.customer_id
    )) AS new_customers
FROM iceberg.retail.orders
WHERE order_timestamp >= NOW() - INTERVAL '30' DAY
GROUP BY DATE(order_timestamp), country
ORDER BY day DESC, country;

-- Q34: Hourly metrics for real-time dashboard
SELECT
    DATE_TRUNC('hour', order_timestamp) AS hour,
    COUNT(*) AS orders,
    SUM(total_amount) AS revenue,
    COUNT(DISTINCT customer_id) AS active_customers,
    AVG(total_amount) AS avg_order_value
FROM iceberg.retail.orders
WHERE order_timestamp >= NOW() - INTERVAL '4' HOUR
GROUP BY DATE_TRUNC('hour', order_timestamp)
ORDER BY hour;

-- Q35: Cross-domain: Orders with payment + delivery + fraud joined
SELECT
    o.order_id,
    o.customer_id,
    o.total_amount AS order_amount,
    o.order_timestamp,
    p.payment_status,
    p.risk_score,
    d.delivery_status,
    CASE
        WHEN p.payment_status != 'completed' THEN 'PAYMENT_ISSUE'
        WHEN p.risk_score > 0.7 THEN 'FRAUD_RISK'
        WHEN d.delivery_status != 'delivered' THEN 'DELIVERY_ISSUE'
        ELSE 'OK'
    END AS health_status
FROM iceberg.retail.orders o
LEFT JOIN iceberg.retail.payments p ON o.order_id = p.order_id
LEFT JOIN iceberg.retail.delivery d ON o.order_id = d.order_id
WHERE o.order_timestamp >= NOW() - INTERVAL '24' HOUR
    AND (
        p.payment_status != 'completed'
        OR p.risk_score > 0.7
        OR d.delivery_status != 'delivered'
    )
ORDER BY
    CASE
        WHEN p.risk_score > 0.7 THEN 1
        WHEN p.payment_status != 'completed' THEN 2
        ELSE 3
    END;