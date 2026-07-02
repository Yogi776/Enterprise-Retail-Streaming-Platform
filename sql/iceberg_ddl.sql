-- ============================================
-- Enterprise Retail Streaming Platform
-- Apache Iceberg Table Definitions
-- ============================================

-- Create Iceberg database
CREATE SCHEMA IF NOT EXISTS retail;

-- ============================================
-- ORDERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS retail.orders (
    order_id STRING,
    customer_id STRING,
    order_timestamp TIMESTAMP,
    status STRING,
    total_amount DECIMAL(12, 2),
    currency STRING,
    payment_method STRING,
    store_id STRING,
    store_location STRING,
    country STRING,
    order_items ARRAY<STRUCT<
        product_id: STRING,
        product_name: STRING,
        quantity: INT,
        unit_price: DECIMAL(10, 2),
        discount: DECIMAL(10, 2)
    >>,
    shipping_address STRUCT<
        street: STRING,
        city: STRING,
        state: STRING,
        zip_code: STRING,
        country: STRING
    >,
    fraud_score DECIMAL(5, 3),
    fraud_flags ARRAY<STRING>,
    created_at TIMESTAMP,
    processed_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (days(order_timestamp), country)
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd'
);

-- ============================================
-- PAYMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS retail.payments (
    payment_id STRING,
    order_id STRING,
    customer_id STRING,
    payment_timestamp TIMESTAMP,
    amount DECIMAL(12, 2),
    currency STRING,
    payment_method STRING,
    payment_status STRING,
    payment_provider STRING,
    transaction_fee DECIMAL(10, 2),
    is_refunded BOOLEAN,
    refund_amount DECIMAL(12, 2),
    failure_reason STRING,
    risk_score DECIMAL(5, 3),
    country STRING,
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (days(payment_timestamp), country)
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd'
);

-- ============================================
-- INVENTORY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS retail.inventory (
    inventory_id STRING,
    product_id STRING,
    product_name STRING,
    category STRING,
    subcategory STRING,
    store_id STRING,
    store_location STRING,
    quantity_on_hand INT,
    reorder_point INT,
    max_stock_level INT,
    last_restock_date TIMESTAMP,
    next_restock_date TIMESTAMP,
    is_low_stock BOOLEAN,
    is_out_of_stock BOOLEAN,
    warehouse_location STRING,
    unit_cost DECIMAL(10, 2),
    country STRING,
    updated_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (days(updated_at), country)
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd'
);

-- ============================================
-- CUSTOMERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS retail.customers (
    customer_id STRING,
    email STRING,
    first_name STRING,
    last_name STRING,
    phone_number STRING,
    customer_segment STRING,
    loyalty_tier STRING,
    loyalty_points INT,
    registration_date TIMESTAMP,
    country STRING,
    city STRING,
    postal_code STRING,
    total_orders INT,
    total_spent DECIMAL(14, 2),
    average_order_value DECIMAL(10, 2),
    last_order_date TIMESTAMP,
    last_activity_date TIMESTAMP,
    is_active BOOLEAN,
    churn_risk_score DECIMAL(5, 3),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (country)
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd'
);

-- ============================================
-- FRAUD EVENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS retail.fraud_events (
    fraud_event_id STRING,
    order_id STRING,
    customer_id STRING,
    payment_id STRING,
    fraud_timestamp TIMESTAMP,
    fraud_type STRING,
    fraud_score DECIMAL(5, 3),
    risk_factors ARRAY<STRING>,
    action_taken STRING,
    is_confirmed BOOLEAN,
    confirmed_at TIMESTAMP,
    country STRING,
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (days(fraud_timestamp), country)
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd'
);

-- ============================================
-- DELIVERY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS retail.delivery (
    delivery_id STRING,
    order_id STRING,
    customer_id STRING,
    shipment_id STRING,
    carrier STRING,
    tracking_number STRING,
    delivery_status STRING,
    estimated_delivery_date TIMESTAMP,
    actual_delivery_date TIMESTAMP,
    delivery_address STRUCT<
        street: STRING,
        city: STRING,
        state: STRING,
        zip_code: STRING,
        country: STRING
    >,
    shipping_method STRING,
    shipping_cost DECIMAL(10, 2),
    weight_kg DECIMAL(8, 3),
    is_delayed BOOLEAN,
    delay_reason STRING,
    country STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (days(created_at), country)
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd'
);

-- ============================================
-- PRODUCTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS retail.products (
    product_id STRING,
    product_name STRING,
    category STRING,
    subcategory STRING,
    brand STRING,
    supplier_id STRING,
    unit_cost DECIMAL(10, 2),
    unit_price DECIMAL(10, 2),
    margin_percentage DECIMAL(6, 2),
    is_active BOOLEAN,
    country STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (category, country)
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd'
);

-- ============================================
-- STORES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS retail.stores (
    store_id STRING,
    store_name STRING,
    store_type STRING,
    location STRUCT<
        street: STRING,
        city: STRING,
        state: STRING,
        zip_code: STRING,
        country: STRING,
        latitude: DECIMAL(10, 7),
        longitude: DECIMAL(10, 7)
    >,
    square_footage INT,
    opening_date DATE,
    manager_name STRING,
    is_active BOOLEAN,
    country STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (country)
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd'
);

-- ============================================
-- DAILY AGGREGATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS retail.daily_aggregations (
    aggregation_date DATE,
    country STRING,
    total_orders INT,
    total_revenue DECIMAL(14, 2),
    total_refunds DECIMAL(14, 2),
    net_revenue DECIMAL(14, 2),
    total_customers INT,
    new_customers INT,
    returning_customers INT,
    average_order_value DECIMAL(10, 2),
    fraud_attempts INT,
    low_stock_products INT,
    out_of_stock_events INT,
    total_deliveries INT,
    delayed_deliveries INT,
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (aggregation_date, country)
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd'
);

-- ============================================
-- HOURLY METRICS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS retail.hourly_metrics (
    metric_hour TIMESTAMP,
    country STRING,
    store_id STRING,
    orders_count INT,
    revenue DECIMAL(14, 2),
    payment_success_rate DECIMAL(6, 3),
    fraud_rate DECIMAL(6, 3),
    inventory_turnover DECIMAL(8, 3),
    customer_visits INT,
    conversion_rate DECIMAL(6, 3),
    average_fulfillment_time_minutes DECIMAL(8, 2),
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (hours(metric_hour), country)
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd'
);