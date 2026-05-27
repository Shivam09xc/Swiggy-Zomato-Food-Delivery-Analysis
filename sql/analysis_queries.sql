-- ========================================================
-- 📊 ZOMATO / SWIGGY FOOD DELIVERY ANALYSIS QUERIES
-- ========================================================
-- This script contains two sections:
-- Section 1: Exact flat-table queries matching STEP 4.
-- Section 2: Relational JOIN queries matching STEP 3 normalization.

-- ========================================================
-- SECTION 1: FLAT-TABLE ANALYTICAL QUERIES (AS REQUESTED)
-- ========================================================
-- Run these queries directly on the flat table 'orders' imported from 'data/cleaned_data.csv'.

-- 📌 Query 1 — Fastest Delivery Areas
-- Analyzes which geographic zones have the fastest average delivery times.
SELECT delivery_area,
AVG(delivery_time) AS avg_delivery_time
FROM orders
GROUP BY delivery_area
ORDER BY avg_delivery_time ASC;


-- 📌 Query 2 — Most Ordered Foods
-- Identifies the top-ordered food items based on overall order frequency.
SELECT food_item,
COUNT(*) AS total_orders
FROM orders
GROUP BY food_item
ORDER BY total_orders DESC;


-- 📌 Query 3 — Ratings vs Delivery Time
-- Groups completed deliveries into speeds (Fast, Medium, Slow) to evaluate speed impact on ratings.
SELECT
CASE
WHEN delivery_time < 20 THEN 'Fast'
WHEN delivery_time < 40 THEN 'Medium'
ELSE 'Slow'
END AS delivery_speed,
AVG(rating) AS avg_rating
FROM orders
GROUP BY delivery_speed;


-- 📌 Query 4 — Cancellation Analysis
-- Ranks delivery areas by the volume of cancelled orders to identify local service failures.
SELECT
delivery_area,
COUNT(*) AS cancelled_orders
FROM orders
WHERE order_status = 'Cancelled'
GROUP BY delivery_area
ORDER BY cancelled_orders DESC;


-- 📌 Query 5 — Peak Order Timings
-- Extracts the hour of the day to identify peak demand times.
SELECT
HOUR(order_time) AS peak_hour,
COUNT(*) AS total_orders
FROM orders
GROUP BY peak_hour
ORDER BY total_orders DESC;


-- ========================================================
-- SECTION 2: NORMALIZED RELATIONAL SCHEMA QUERIES (STEP 3 DDL)
-- ========================================================
-- Run these queries if you have imported the three normalized CSV tables
-- (customers_table, restaurants_table, orders_table) into the normalized database layout.

-- 📌 Relational Query 1 — Fastest Delivery Areas (JOIN Version)
-- Joins child order table with parent restaurant table to group by restaurant zone.
SELECT r.area AS delivery_area,
AVG(o.delivery_time) AS avg_delivery_time
FROM orders o
INNER JOIN restaurants r ON o.restaurant_id = r.restaurant_id
WHERE o.status = 'Delivered'
GROUP BY r.area
ORDER BY avg_delivery_time ASC;


-- 📌 Relational Query 2 — Most Ordered Foods (Normalized Schema)
-- If food items are tracked in a menu/item relationship or within order details,
-- here is how we join to retrieve popular item statistics:
SELECT o.food_item, -- (If food_item is kept inside the relational order log)
COUNT(*) AS total_orders
FROM orders o
GROUP BY o.food_item
ORDER BY total_orders DESC;


-- 📌 Relational Query 3 — Ratings vs Delivery Time (JOIN Version)
SELECT
CASE
WHEN o.delivery_time < 20 THEN 'Fast'
WHEN o.delivery_time < 40 THEN 'Medium'
ELSE 'Slow'
END AS delivery_speed,
AVG(o.rating) AS avg_rating
FROM orders o
WHERE o.status = 'Delivered'
GROUP BY delivery_speed;


-- 📌 Relational Query 4 — Cancellation Analysis (JOIN Version)
SELECT
r.area AS delivery_area,
COUNT(*) AS cancelled_orders
FROM orders o
INNER JOIN restaurants r ON o.restaurant_id = r.restaurant_id
WHERE o.status = 'Cancelled'
GROUP BY r.area
ORDER BY cancelled_orders DESC;


-- 📌 Relational Query 5 — Peak Order Timings (JOIN Version)
SELECT
HOUR(o.order_time) AS peak_hour,
COUNT(*) AS total_orders
FROM orders o
GROUP BY peak_hour
ORDER BY total_orders DESC;
