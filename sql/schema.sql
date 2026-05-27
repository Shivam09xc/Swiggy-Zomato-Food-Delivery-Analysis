-- SQL Database Schema Setup (MySQL / PostgreSQL Compatible)
-- Dual-Model Compatibility: Supports both Flat-File Analytics and Normalized Relational Designs.

-- Create Database if not exists
-- CREATE DATABASE IF NOT EXISTS food_delivery_db;
-- USE food_delivery_db;

-- Drop existing tables to clean environment (child tables dropped first)
DROP TABLE IF EXISTS orders_normalized;
DROP TABLE IF EXISTS restaurants;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS orders;

-- ========================================================
-- MODEL 1: FLAT ANALYTICAL TABLE (For STEP 4 Queries)
-- ========================================================
-- This table directly ingest the flat 'data/cleaned_data.csv' file.
-- Named exactly 'orders' to match the raw Query 1, 2, 3, 4, and 5 from Step 4.

CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    restaurant_name VARCHAR(100) NOT NULL,
    food_item VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    order_time DATETIME NOT NULL,
    delivery_time INT NULL, -- NULL for cancelled orders
    delivery_area VARCHAR(100) NOT NULL,
    order_status VARCHAR(50) NOT NULL, -- 'Delivered' or 'Cancelled'
    rating INT NULL, -- NULL for cancelled orders
    review TEXT NULL,
    order_value DECIMAL(10, 2) NOT NULL,
    delivery_partner VARCHAR(50) NOT NULL,
    
    -- Feature Engineered Temporal Columns
    order_date DATE NOT NULL,
    order_hour INT NOT NULL,
    order_day VARCHAR(20) NOT NULL,
    order_day_name VARCHAR(20) NOT NULL,
    order_day_of_week INT NOT NULL,
    is_weekend TINYINT NOT NULL,
    peak_hour_label VARCHAR(50) NOT NULL,
    delivery_delay INT NULL, -- Operational delay beyond 30 mins
    
    -- Sentiment Analysis NLP Columns
    sentiment_polarity DECIMAL(5, 4) NOT NULL,
    sentiment_subjectivity DECIMAL(5, 4) NOT NULL,
    sentiment_category VARCHAR(50) NOT NULL
);

-- Optimize Flat table performance
CREATE INDEX idx_orders_flat_area ON orders(delivery_area);
CREATE INDEX idx_orders_flat_item ON orders(food_item);
CREATE INDEX idx_orders_flat_status ON orders(order_status);


-- ========================================================
-- MODEL 2: NORMALIZED RELATIONAL LAYOUT (For STEP 3 Design)
-- ========================================================
-- Normalized tables referencing key constraints.

-- 1. Customers Table
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL
);

-- 2. Restaurants Table
CREATE TABLE restaurants (
    restaurant_id VARCHAR(50) PRIMARY KEY,
    restaurant_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    area VARCHAR(100) NOT NULL
);

-- 3. Normalized Orders Table (Child Table)
CREATE TABLE orders_normalized (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    restaurant_id VARCHAR(50) NOT NULL,
    order_time DATETIME NOT NULL,
    delivery_time INT NULL,
    status VARCHAR(50) NOT NULL, -- 'Delivered' or 'Cancelled'
    rating INT NULL,
    order_value DECIMAL(10, 2) NOT NULL,
    
    -- Optional columns for relational analytics extensions
    food_item VARCHAR(100) NULL,
    
    -- Referential Integrity Constraints
    CONSTRAINT fk_norm_customer FOREIGN KEY (customer_id) 
        REFERENCES customers(customer_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_norm_restaurant FOREIGN KEY (restaurant_id) 
        REFERENCES restaurants(restaurant_id) 
        ON DELETE CASCADE
);

-- Optimize Normalized table performance
CREATE INDEX idx_norm_cust ON orders_normalized(customer_id);
CREATE INDEX idx_norm_rest ON orders_normalized(restaurant_id);
CREATE INDEX idx_norm_status ON orders_normalized(status);
