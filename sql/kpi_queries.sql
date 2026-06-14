-- ============================================================
-- Business Reporting Automation - KPI SQL Views
-- Compatible with PostgreSQL
-- ============================================================

-- 1. Revenue Trend View (Monthly)
CREATE OR REPLACE VIEW vw_revenue_trend AS
SELECT
    DATE_TRUNC('month', order_date) AS month,
    SUM(revenue)                    AS total_revenue,
    COUNT(order_id)                 AS total_orders,
    AVG(revenue)                    AS avg_order_value
FROM orders
WHERE status = 'Completed'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- 2. Category Performance View
CREATE OR REPLACE VIEW vw_category_performance AS
SELECT
    category,
    COUNT(order_id)   AS total_orders,
    SUM(revenue)      AS total_revenue,
    AVG(revenue)      AS avg_order_value,
    SUM(quantity)     AS total_units_sold
FROM orders
WHERE status = 'Completed'
GROUP BY category
ORDER BY total_revenue DESC;

-- 3. Regional Sales View
CREATE OR REPLACE VIEW vw_regional_sales AS
SELECT
    region,
    COUNT(order_id)                         AS total_orders,
    SUM(revenue)                            AS total_revenue,
    ROUND(AVG(revenue)::numeric, 2)        AS avg_order_value,
    COUNT(DISTINCT customer_id)            AS unique_customers
FROM orders
GROUP BY region
ORDER BY total_revenue DESC;

-- 4. Order Status Distribution View
CREATE OR REPLACE VIEW vw_order_status AS
SELECT
    status,
    COUNT(order_id)                                AS order_count,
    ROUND(100.0 * COUNT(order_id) / SUM(COUNT(order_id)) OVER (), 2) AS pct_share
FROM orders
GROUP BY status;

-- 5. Payment Method Breakdown View
CREATE OR REPLACE VIEW vw_payment_methods AS
SELECT
    payment_method,
    COUNT(order_id)   AS total_orders,
    SUM(revenue)      AS total_revenue
FROM orders
WHERE status = 'Completed'
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- 6. Data Quality Monitoring View
CREATE OR REPLACE VIEW vw_data_quality AS
SELECT
    'Missing Revenue'       AS issue_type,
    COUNT(*)                AS issue_count,
    NOW()                   AS checked_at
FROM orders WHERE revenue IS NULL
UNION ALL
SELECT
    'Duplicate Order IDs',
    COUNT(*) - COUNT(DISTINCT order_id),
    NOW()
FROM orders
UNION ALL
SELECT
    'Future Dates',
    COUNT(*),
    NOW()
FROM orders WHERE order_date > CURRENT_DATE
UNION ALL
SELECT
    'Negative Revenue',
    COUNT(*),
    NOW()
FROM orders WHERE revenue < 0;

-- 7. Top 10 Orders by Revenue
CREATE OR REPLACE VIEW vw_top_orders AS
SELECT
    order_id,
    order_date,
    category,
    region,
    revenue,
    quantity,
    status
FROM orders
WHERE status = 'Completed'
ORDER BY revenue DESC
LIMIT 10;

-- 8. Daily Sales for Last 30 Days
CREATE OR REPLACE VIEW vw_daily_sales_30d AS
SELECT
    order_date::date            AS sale_date,
    COUNT(order_id)             AS orders,
    SUM(revenue)                AS daily_revenue
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
  AND status = 'Completed'
GROUP BY order_date::date
ORDER BY sale_date;
