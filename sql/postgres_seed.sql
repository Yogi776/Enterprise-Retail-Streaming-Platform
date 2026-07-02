-- ============================================================
-- PostgreSQL Seed Data for Retail Streaming Platform
-- Reference data loaded on first startup
-- ============================================================

-- Stores reference table
CREATE TABLE IF NOT EXISTS stores (
    store_id VARCHAR(50) PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    store_type VARCHAR(50),  -- flagship, regular, warehouse
    street VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(3) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    square_footage INTEGER,
    opening_date DATE,
    manager_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO stores (store_id, store_name, store_type, city, state, zip_code, country, latitude, longitude, square_footage, opening_date, manager_name) VALUES
('STORE-US-001', 'Manhattan Flagship', 'flagship', 'New York', 'NY', '10001', 'US', 40.7484, -73.9967, 45000, '2018-03-15', 'Sarah Johnson'),
('STORE-US-002', 'LA Downtown', 'regular', 'Los Angeles', 'CA', '90001', 'US', 34.0522, -118.2437, 25000, '2019-07-20', 'Michael Chen'),
('STORE-US-003', 'Chicago Magnificent', 'regular', 'Chicago', 'IL', '60601', 'US', 41.8781, -87.6298, 30000, '2020-01-10', 'Emily Rodriguez'),
('STORE-US-004', 'Houston Galleria', 'flagship', 'Houston', 'TX', '77001', 'US', 29.7604, -95.3698, 38000, '2019-11-05', 'David Kim'),
('STORE-US-005', 'Miami Beach', 'regular', 'Miami', 'FL', '33101', 'US', 25.7617, -80.1918, 22000, '2021-05-01', 'Jessica Williams'),
('STORE-UK-001', 'London Oxford St', 'flagship', 'London', 'England', 'W1D 1NS', 'UK', 51.5154, -0.1410, 35000, '2018-09-01', 'James Thompson'),
('STORE-UK-002', 'Manchester Arndale', 'regular', 'Manchester', 'England', 'M4 3AQ', 'UK', 53.4808, -2.2426, 20000, '2019-04-15', 'Sophie Anderson'),
('STORE-DE-001', 'Berlin Mitte', 'flagship', 'Berlin', 'Berlin', '10115', 'DE', 52.5200, 13.4050, 28000, '2020-02-20', 'Hans Mueller'),
('STORE-FR-001', 'Paris Champs-Élysées', 'flagship', 'Paris', 'Île-de-France', '75008', 'FR', 48.8698, 2.3078, 32000, '2018-06-01', 'Marie Dupont'),
('STORE-JP-001', 'Tokyo Shibuya', 'flagship', 'Tokyo', 'Tokyo', '150-0001', 'JP', 35.6595, 139.7004, 40000, '2017-11-15', 'Yuki Tanaka');

-- Products reference table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    brand VARCHAR(100),
    supplier_id VARCHAR(50),
    unit_cost DECIMAL(10, 2) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    margin_percentage DECIMAL(6, 2) GENERATED ALWAYS AS (
        CASE WHEN unit_price > 0
             THEN ((unit_price - unit_cost) / unit_price * 100)
             ELSE 0 END
    ) STORED,
    weight_kg DECIMAL(8, 3),
    is_active BOOLEAN DEFAULT true,
    country VARCHAR(3) DEFAULT 'US',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products (product_id, product_name, category, subcategory, brand, unit_cost, unit_price, weight_kg) VALUES
-- Electronics
('SKU-ELEC-001', 'Wireless Bluetooth Headphones', 'electronics', 'audio', 'SoundMax', 45.00, 79.99, 0.25),
('SKU-ELEC-002', 'Smart Watch Series 5', 'electronics', 'wearables', 'TechTime', 150.00, 249.99, 0.05),
('SKU-ELEC-003', 'USB-C Charging Cable 3-Pack', 'electronics', 'accessories', 'ChargePro', 8.00, 19.99, 0.10),
('SKU-ELEC-004', 'Portable Power Bank 20000mAh', 'electronics', 'accessories', 'PowerGo', 25.00, 49.99, 0.35),
('SKU-ELEC-005', 'Bluetooth Speaker', 'electronics', 'audio', 'SoundMax', 30.00, 59.99, 0.60),
('SKU-ELEC-006', 'Wireless Mouse', 'electronics', 'accessories', 'ClickPro', 15.00, 29.99, 0.12),
('SKU-ELEC-007', 'Mechanical Keyboard', 'electronics', 'accessories', 'TypeMaster', 50.00, 89.99, 0.85),
('SKU-ELEC-008', '4K Webcam', 'electronics', 'accessories', 'VisionCam', 70.00, 119.99, 0.18),
-- Grocery
('SKU-GROC-001', 'Organic Oat Milk 1L', 'grocery', 'dairy', 'GreenFarm', 2.50, 4.99, 1.05),
('SKU-GROC-002', 'Free-Range Eggs 12pk', 'grocery', 'dairy', 'FarmFresh', 3.50, 6.99, 0.72),
('SKU-GROC-003', 'Artisan Sourdough Bread', 'grocery', 'bakery', 'BakerBox', 2.20, 5.49, 0.60),
('SKU-GROC-004', 'Cold Press Coffee 750ml', 'grocery', 'beverages', 'BrewCo', 4.00, 8.99, 0.80),
('SKU-GROC-005', 'Greek Yogurt 500g', 'grocery', 'dairy', 'GreenFarm', 1.80, 3.99, 0.52),
('SKU-GROC-006', 'Avocado 4-Pack', 'grocery', 'produce', 'FreshHarvest', 3.00, 5.99, 0.45),
('SKU-GROC-007', 'Organic Spinach 200g', 'grocery', 'produce', 'GreenFarm', 1.50, 3.49, 0.21),
('SKU-GROC-008', 'Grass-Fed Butter 250g', 'grocery', 'dairy', 'FarmFresh', 4.00, 7.49, 0.26),
-- Fashion
('SKU-FASH-001', 'Cotton T-Shirt White M', 'fashion', 'tops', 'StyleFit', 10.00, 24.99, 0.20),
('SKU-FASH-002', 'Slim Fit Jeans 32x30', 'fashion', 'bottoms', 'DenimCo', 28.00, 59.99, 0.55),
('SKU-FASH-003', 'Running Sneakers Size 10', 'fashion', 'footwear', 'SpeedRun', 45.00, 89.99, 0.75),
('SKU-FASH-004', 'Wool Blend Sweater', 'fashion', 'tops', 'WarmWool', 35.00, 74.99, 0.45),
('SKU-FASH-005', 'Leather Belt Brown', 'fashion', 'accessories', 'LeatherLux', 15.00, 34.99, 0.25),
('SKU-FASH-006', 'Canvas Backpack', 'fashion', 'bags', 'UrbanCarry', 20.00, 44.99, 0.70),
('SKU-FASH-007', 'Polarized Sunglasses', 'fashion', 'accessories', 'SunStyle', 30.00, 69.99, 0.05),
('SKU-FASH-008', 'Cotton Dress Shirt Blue L', 'fashion', 'tops', 'StyleFit', 22.00, 49.99, 0.30),
-- Home
('SKU-HOME-001', 'Stainless Steel Cookware Set', 'home', 'kitchen', 'ChefMaster', 75.00, 149.99, 8.50),
('SKU-HOME-002', 'Memory Foam Pillow 2-Pack', 'home', 'bedroom', 'SleepWell', 18.00, 39.99, 2.20),
('SKU-HOME-003', 'Scented Candle Collection', 'home', 'decor', 'AromaLux', 12.00, 29.99, 0.90),
('SKU-HOME-004', 'Bamboo Cutting Board Set', 'home', 'kitchen', 'EcoCut', 15.00, 34.99, 1.80),
('SKU-HOME-005', 'Smart LED Light Bulbs 4-Pack', 'home', 'electrical', 'LumiSmart', 22.00, 49.99, 0.20),
('SKU-HOME-006', 'Weighted Blanket 15lb', 'home', 'bedroom', 'SleepWell', 45.00, 89.99, 7.00),
('SKU-HOME-007', 'French Press Coffee Maker', 'home', 'kitchen', 'BrewMaster', 14.00, 29.99, 0.85),
('SKU-HOME-008', 'Linen Throw Blanket', 'home', 'bedroom', 'CozyNest', 28.00, 59.99, 1.20),
-- Beauty
('SKU-BEAU-001', 'Vitamin C Serum 30ml', 'beauty', 'skincare', 'GlowPure', 20.00, 45.99, 0.05),
('SKU-BEAU-002', 'Moisturizing Face Cream', 'beauty', 'skincare', 'HydraSkin', 17.00, 38.99, 0.10),
('SKU-BEAU-003', 'Makeup Brush Set 12-Piece', 'beauty', 'makeup', 'BlendPro', 14.00, 34.99, 0.30),
('SKU-BEAU-004', 'Hair Dryer 2000W', 'beauty', 'haircare', 'StyleAir', 28.00, 59.99, 0.65),
('SKU-BEAU-005', 'Organic Shampoo 500ml', 'beauty', 'haircare', 'PureHair', 6.00, 14.99, 0.55),
('SKU-BEAU-006', 'Sunscreen SPF 50 200ml', 'beauty', 'skincare', 'SunGuard', 8.00, 19.99, 0.22),
('SKU-BEAU-007', 'Perfume Gift Set', 'beauty', 'fragrance', 'EssenceLux', 35.00, 74.99, 0.35),
('SKU-BEAU-008', 'Electric Toothbrush', 'beauty', 'dental', 'DentaClean', 38.00, 79.99, 0.25),
-- Sports
('SKU-SPRT-001', 'Yoga Mat Premium 6mm', 'sports', 'fitness', 'FlexiFit', 18.00, 39.99, 1.50),
('SKU-SPRT-002', 'Resistance Bands Set', 'sports', 'fitness', 'FlexiFit', 10.00, 24.99, 0.30),
('SKU-SPRT-003', 'Running Water Bottle 750ml', 'sports', 'outdoor', 'HydroRun', 8.00, 19.99, 0.08),
('SKU-SPRT-004', 'Dumbbell Set 20kg', 'sports', 'fitness', 'IronPower', 42.00, 89.99, 21.00),
('SKU-SPRT-005', 'Tennis Racket Pro', 'sports', 'rackets', 'RallyPro', 65.00, 129.99, 0.30),
('SKU-SPRT-006', 'Cycling Gloves Padded', 'sports', 'cycling', 'RideGear', 10.00, 24.99, 0.15),
('SKU-SPRT-007', 'Foam Roller 90cm', 'sports', 'fitness', 'FlexiFit', 15.00, 34.99, 1.20),
('SKU-SPRT-008', 'Fitness Tracker Band', 'sports', 'wearables', 'ActiveTrack', 28.00, 59.99, 0.05);

-- Payment methods reference
CREATE TABLE IF NOT EXISTS payment_methods (
    method_id VARCHAR(50) PRIMARY KEY,
    method_name VARCHAR(100) NOT NULL,
    provider VARCHAR(100),
    is_enabled BOOLEAN DEFAULT true,
    fee_percentage DECIMAL(5, 3),
    fee_fixed DECIMAL(8, 2)
);

INSERT INTO payment_methods (method_id, method_name, provider, fee_percentage, fee_fixed) VALUES
('credit_card', 'Credit Card', 'Stripe', 0.029, 0.30),
('debit_card', 'Debit Card', 'Stripe', 0.019, 0.20),
('wallet', 'Digital Wallet', 'PayPal', 0.025, 0.25),
('bank_transfer', 'Bank Transfer', 'Stripe', 0.008, 0.15),
('cash', 'Cash on Delivery', NULL, 0.000, 0.00);

-- Customer segments reference
CREATE TABLE IF NOT EXISTS customer_segments (
    segment_id VARCHAR(50) PRIMARY KEY,
    segment_name VARCHAR(100) NOT NULL,
    min_orders INTEGER,
    max_orders INTEGER,
    min_ltv DECIMAL(12, 2),
    max_ltv DECIMAL(12, 2),
    churn_risk VARCHAR(20),
    description TEXT
);

INSERT INTO customer_segments (segment_id, segment_name, min_orders, max_orders, min_ltv, max_ltv, churn_risk, description) VALUES
('new', 'New Customers', 0, 1, 0, 99.99, 'low', 'Customers with 1 order in their lifetime'),
('active', 'Active Customers', 2, NULL, 100.00, NULL, 'low', 'Regular customers with 2+ orders'),
('at_risk', 'At-Risk Customers', NULL, NULL, NULL, NULL, 'high', 'Customers who have not ordered in 30-60 days'),
('churned', 'Churned Customers', NULL, NULL, NULL, NULL, 'critical', 'Customers with no orders in 90+ days'),
('vip', 'VIP Customers', 10, NULL, 10000.00, NULL, 'low', 'High-value customers with $10,000+ lifetime spend');

-- Loyalty tiers reference
CREATE TABLE IF NOT EXISTS loyalty_tiers (
    tier_id VARCHAR(50) PRIMARY KEY,
    tier_name VARCHAR(100) NOT NULL,
    min_points INTEGER DEFAULT 0,
    max_points INTEGER,
    discount_percentage DECIMAL(4, 2),
    free_shipping BOOLEAN,
    priority_support BOOLEAN,
    description TEXT
);

INSERT INTO loyalty_tiers (tier_id, tier_name, min_points, max_points, discount_percentage, free_shipping, priority_support) VALUES
('bronze', 'Bronze', 0, 999, 0.00, false, false),
('silver', 'Silver', 1000, 4999, 2.50, true, false),
('gold', 'Gold', 5000, 9999, 5.00, true, true),
('platinum', 'Platinum', 10000, NULL, 10.00, true, true);

-- Country and currency mapping
CREATE TABLE IF NOT EXISTS country_currency (
    country_code VARCHAR(3) PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    currency_code VARCHAR(3) NOT NULL,
    currency_symbol VARCHAR(5) NOT NULL,
    exchange_rate_to_usd DECIMAL(10, 4) DEFAULT 1.0000,
    region VARCHAR(50)
);

INSERT INTO country_currency (country_code, country_name, currency_code, currency_symbol, exchange_rate_to_usd, region) VALUES
('US', 'United States', 'USD', '$', 1.0000, 'North America'),
('UK', 'United Kingdom', 'GBP', '£', 0.79, 'Europe'),
('DE', 'Germany', 'EUR', '€', 0.92, 'Europe'),
('FR', 'France', 'EUR', '€', 0.92, 'Europe'),
('ES', 'Spain', 'EUR', '€', 0.92, 'Europe'),
('IT', 'Italy', 'EUR', '€', 0.92, 'Europe'),
('JP', 'Japan', 'JPY', '¥', 149.50, 'Asia Pacific'),
('AU', 'Australia', 'AUD', 'A$', 1.53, 'Asia Pacific');

-- Fraud rule thresholds reference
CREATE TABLE IF NOT EXISTS fraud_rules (
    rule_id VARCHAR(50) PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    condition_type VARCHAR(50) NOT NULL,  -- velocity, amount, geographic, pattern
    threshold_value DECIMAL(10, 2),
    score_impact DECIMAL(5, 3),
    is_active BOOLEAN DEFAULT true,
    description TEXT
);

INSERT INTO fraud_rules (rule_id, rule_name, condition_type, threshold_value, score_impact, description) VALUES
('velocity_1', '5+ orders in 1 hour', 'velocity', 5.00, 0.30, 'More than 5 orders from same customer in 1 hour'),
('velocity_2', '10+ orders in 24 hours', 'velocity', 10.00, 0.50, 'More than 10 orders from same customer in 24 hours'),
('amount_1', 'Single order > $1000', 'amount', 1000.00, 0.20, 'Order amount exceeds $1,000'),
('amount_2', 'Single order > $5000', 'amount', 5000.00, 0.60, 'Order amount exceeds $5,000'),
('geo_1', 'New country for customer', 'geographic', NULL, 0.15, 'Order from different country than previous orders'),
('pattern_1', 'Multiple failed payments', 'pattern', 3.00, 0.40, '3+ failed payment attempts'),
('device_1', 'New device first order', 'pattern', NULL, 0.10, 'First order from new device');

-- Reorder point configuration
CREATE TABLE IF NOT EXISTS reorder_config (
    config_id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    default_reorder_point INTEGER DEFAULT 20,
    default_min_order_qty INTEGER DEFAULT 50,
    default_lead_time_days INTEGER DEFAULT 7,
    is_active BOOLEAN DEFAULT true
);

INSERT INTO reorder_config (config_id, category, default_reorder_point, default_min_order_qty, default_lead_time_days) VALUES
('electronics', 'electronics', 15, 30, 14),
('grocery', 'grocery', 50, 100, 3),
('fashion', 'fashion', 25, 50, 10),
('home', 'home', 20, 40, 7),
('beauty', 'beauty', 30, 60, 5),
('sports', 'sports', 20, 40, 7);