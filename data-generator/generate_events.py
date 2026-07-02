#!/usr/bin/env python3
"""
Enterprise Retail Streaming Platform — Synthetic Data Generator

Produces realistic retail events across 8 Kafka topics:
  - retail.orders
  - retail.payments
  - retail.inventory
  - retail.delivery
  - retail.customer_behavior
  - retail.recommendations
  - retail.fraud_signals
  - retail.customer_profile

Realistic distributions:
  - Evening orders spike (18-22h +40%)
  - Weekend orders boost (+25% on Sat/Sun)
  - Payment failures 3-7%
  - Fraud signals 1-3%
  - Inventory stockouts 5-10%
  - Delivery delays 8-15%
  - Repeat customers 40-60%
  - 6 product categories: electronics, grocery, fashion, home, beauty, sports

Features:
  - Intentional 1-2% duplicate event_id for deduplication testing
  - Correlation IDs linking related events (order → payment → delivery)
  - Configurable throughput via EVENTS_PER_SECOND env var
"""

import json
import os
import time
import uuid
import random
import threading
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Any

from faker import Faker
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Initialize Faker with seed for reproducible data
fake = Faker()
Faker.seed(42)
random.seed(42)

# =============================================================================
# CONFIGURATION
# =============================================================================

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
EVENTS_PER_SECOND = int(os.getenv("EVENTS_PER_SECOND", "50"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))

# Kafka topic names
TOPICS = {
    "orders": os.getenv("KAFKA_TOPIC_ORDERS", "retail.orders"),
    "payments": os.getenv("KAFKA_TOPIC_PAYMENTS", "retail.payments"),
    "inventory": os.getenv("KAFKA_TOPIC_INVENTORY", "retail.inventory"),
    "delivery": os.getenv("KAFKA_TOPIC_DELIVERY", "retail.delivery"),
    "customer_behavior": os.getenv("KAFKA_TOPIC_CUSTOMER_BEHAVIOR", "retail.customer_behavior"),
    "recommendations": os.getenv("KAFKA_TOPIC_RECOMMENDATIONS", "retail.recommendations"),
    "fraud_signals": os.getenv("KAFKA_TOPIC_FRAUD", "retail.fraud_signals"),
    "customer_profile": os.getenv("KAFKA_TOPIC_CUSTOMER_PROFILE", "retail.customer_profile"),
}

# Countries and currencies
COUNTRIES = ["US", "UK", "DE", "FR", "ES", "IT", "JP", "AU"]
CURRENCIES = {"US": "USD", "UK": "GBP", "DE": "EUR", "FR": "EUR", "ES": "EUR", "IT": "EUR", "JP": "JPY", "AU": "AUD"}

# Channels
CHANNELS = ["POS", "Web", "Mobile", "App"]

# Product categories and sample products
PRODUCTS = {
    "electronics": [
        ("SKU-ELEC-001", "Wireless Bluetooth Headphones", 79.99, 45.00),
        ("SKU-ELEC-002", "Smart Watch Series 5", 249.99, 150.00),
        ("SKU-ELEC-003", "USB-C Charging Cable 3-Pack", 19.99, 8.00),
        ("SKU-ELEC-004", "Portable Power Bank 20000mAh", 49.99, 25.00),
        ("SKU-ELEC-005", "Bluetooth Speaker", 59.99, 30.00),
        ("SKU-ELEC-006", "Wireless Mouse", 29.99, 15.00),
        ("SKU-ELEC-007", "Mechanical Keyboard", 89.99, 50.00),
        ("SKU-ELEC-008", "4K Webcam", 119.99, 70.00),
    ],
    "grocery": [
        ("SKU-GROC-001", "Organic Oat Milk 1L", 4.99, 2.50),
        ("SKU-GROC-002", "Free-Range Eggs 12pk", 6.99, 3.50),
        ("SKU-GROC-003", "Artisan Sourdough Bread", 5.49, 2.20),
        ("SKU-GROC-004", "Cold Press Coffee 750ml", 8.99, 4.00),
        ("SKU-GROC-005", "Greek Yogurt 500g", 3.99, 1.80),
        ("SKU-GROC-006", "Avocado 4-Pack", 5.99, 3.00),
        ("SKU-GROC-007", "Organic Spinach 200g", 3.49, 1.50),
        ("SKU-GROC-008", "Grass-Fed Butter 250g", 7.49, 4.00),
    ],
    "fashion": [
        ("SKU-FASH-001", "Cotton T-Shirt White M", 24.99, 10.00),
        ("SKU-FASH-002", "Slim Fit Jeans 32x30", 59.99, 28.00),
        ("SKU-FASH-003", "Running Sneakers Size 10", 89.99, 45.00),
        ("SKU-FASH-004", "Wool Blend Sweater", 74.99, 35.00),
        ("SKU-FASH-005", "Leather Belt Brown", 34.99, 15.00),
        ("SKU-FASH-006", "Canvas Backpack", 44.99, 20.00),
        ("SKU-FASH-007", "Polarized Sunglasses", 69.99, 30.00),
        ("SKU-FASH-008", "Cotton Dress Shirt Blue L", 49.99, 22.00),
    ],
    "home": [
        ("SKU-HOME-001", "Stainless Steel Cookware Set", 149.99, 75.00),
        ("SKU-HOME-002", "Memory Foam Pillow 2-Pack", 39.99, 18.00),
        ("SKU-HOME-003", "Scented Candle Collection", 29.99, 12.00),
        ("SKU-HOME-004", "Bamboo Cutting Board Set", 34.99, 15.00),
        ("SKU-HOME-005", "Smart LED Light Bulbs 4-Pack", 49.99, 22.00),
        ("SKU-HOME-006", "Weighted Blanket 15lb", 89.99, 45.00),
        ("SKU-HOME-007", "French Press Coffee Maker", 29.99, 14.00),
        ("SKU-HOME-008", "Linen Throw Blanket", 59.99, 28.00),
    ],
    "beauty": [
        ("SKU-BEAU-001", "Vitamin C Serum 30ml", 45.99, 20.00),
        ("SKU-BEAU-002", "Moisturizing Face Cream", 38.99, 17.00),
        ("SKU-BEAU-003", "Makeup Brush Set 12-Piece", 34.99, 14.00),
        ("SKU-BEAU-004", "Hair Dryer 2000W", 59.99, 28.00),
        ("SKU-BEAU-005", "Organic Shampoo 500ml", 14.99, 6.00),
        ("SKU-BEAU-006", "Sunscreen SPF 50 200ml", 19.99, 8.00),
        ("SKU-BEAU-007", "Perfume Gift Set", 74.99, 35.00),
        ("SKU-BEAU-008", "Electric Toothbrush", 79.99, 38.00),
    ],
    "sports": [
        ("SKU-SPRT-001", "Yoga Mat Premium 6mm", 39.99, 18.00),
        ("SKU-SPRT-002", "Resistance Bands Set", 24.99, 10.00),
        ("SKU-SPRT-003", "Running Water Bottle 750ml", 19.99, 8.00),
        ("SKU-SPRT-004", "Dumbbell Set 20kg", 89.99, 42.00),
        ("SKU-SPRT-005", "Tennis Racket Pro", 129.99, 65.00),
        ("SKU-SPRT-006", "Cycling Gloves Padded", 24.99, 10.00),
        ("SKU-SPRT-007", "Foam Roller 90cm", 34.99, 15.00),
        ("SKU-SPRT-008", "Fitness Tracker Band", 59.99, 28.00),
    ],
}

PAYMENT_METHODS = ["credit_card", "debit_card", "wallet", "bank_transfer"]
PAYMENT_FAILURE_REASONS = ["insufficient_funds", "card_declined", "timeout", "invalid_card", "fraud_suspected"]

CARRIERS = ["FedEx", "UPS", "USPS", "DHL"]
DELIVERY_STATUSES = ["pending", "shipped", "in_transit", "out_for_delivery", "delivered", "delayed", "failed"]
FRAUD_TYPES = ["velocity_spike", "geographic_anomaly", "new_device", "mismatched_address", "unusual_order_value", "multiple_payment_attempts"]

LOYALTY_TIERS = ["bronze", "silver", "gold", "platinum"]
CUSTOMER_SEGMENTS = ["new", "active", "at_risk", "churned", "vip"]

# State tracking
_order_counter = 0
_payment_counter = 0
_customer_ids = []
_product_skus = []
_active_customers = defaultdict(dict)  # customer_id -> {last_order, order_count, total_spent}


# =============================================================================
# HELPERS
# =============================================================================

def _get_time_multiplier() -> float:
    """Apply realistic time-based distributions to event rate."""
    now = datetime.now()
    hour = now.hour

    # Evening spike: 18-22h +40%
    if 18 <= hour <= 22:
        mult = 1.4
    # Morning spike: 9-11h +20%
    elif 9 <= hour <= 11:
        mult = 1.2
    # Night dip: 0-6h -50%
    elif 0 <= hour <= 6:
        mult = 0.5
    else:
        mult = 1.0

    # Weekend boost: Sat/Sun +25%
    if now.weekday() in (5, 6):  # Sat=5, Sun=6
        mult *= 1.25

    return mult


def _generate_event_id(duplicate_probability: float = 0.015) -> str:
    """
    Generate a unique event_id.
    With 1.5% probability, returns a duplicate (reuse last generated ID).
    This simulates real-world duplicate events for Flink deduplication testing.
    """
    global _order_counter

    if _order_counter > 10 and random.random() < duplicate_probability:
        # Return a previously generated ID (duplicate)
        if _customer_ids:
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"dup-{_order_counter - 1}"))

    return str(uuid.uuid4())


def _generate_customer_id() -> str:
    """Get or create a customer ID."""
    global _customer_ids, _active_customers

    # 70% chance of existing customer, 30% new customer
    if _customer_ids and random.random() < 0.7:
        return random.choice(_customer_ids)

    # Create new customer
    customer_id = f"CUST-{fake.uuid4()[:8].upper()}"
    _customer_ids.append(customer_id)
    _active_customers[customer_id] = {
        "join_date": datetime.now() - timedelta(days=random.randint(1, 365)),
        "order_count": 0,
        "total_spent": 0.0,
        "loyalty_tier": random.choices(LOYALTY_TIERS, weights=[30, 35, 25, 10])[0],
        "segment": random.choices(CUSTOMER_SEGMENTS, weights=[20, 40, 15, 10, 15])[0],
        "country": random.choice(COUNTRIES),
        "email": fake.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }
    return customer_id


def _generate_order_id(country: str) -> str:
    """Generate a unique order ID."""
    global _order_counter
    _order_counter += 1
    return f"ORD-{country}-{_order_counter:08d}"


def _generate_payment_id(country: str) -> str:
    """Generate a unique payment ID."""
    global _payment_counter
    _payment_counter += 1
    return f"PAY-{country}-{_payment_counter:08d}"


def _pick_product():
    """Pick a random product from any category."""
    global _product_skus
    category = random.choice(list(PRODUCTS.keys()))
    sku, name, price, cost = random.choice(PRODUCTS[category])
    _product_skus.append(sku)
    return sku, name, price, cost, category


def _generate_order_items():
    """Generate 1-5 order items."""
    item_count = random.randint(1, 5)
    items = []
    for _ in range(item_count):
        sku, name, price, cost, category = _pick_product()
        qty = random.randint(1, 3)
        discount = round(random.uniform(0, 0.2) * price, 2)
        items.append({
            "product_id": sku,
            "product_name": name,
            "category": category,
            "quantity": qty,
            "unit_price": round(price, 2),
            "discount": discount,
        })
    return items


# =============================================================================
# EVENT GENERATORS
# =============================================================================

def generate_order_event(now: datetime) -> dict[str, Any]:
    """Generate an order event."""
    customer_id = _generate_customer_id()
    country = _active_customers[customer_id]["country"]
    order_id = _generate_order_id(country)
    items = _generate_order_items()

    total_amount = sum(item["unit_price"] * item["quantity"] - item["discount"] for item in items)
    currency = CURRENCIES[country]
    channel = random.choice(CHANNELS)
    store_id = f"STORE-{country}-{random.randint(1, 20):03d}"

    event = {
        "event_id": _generate_event_id(),
        "event_type": "order_created",
        "event_timestamp": now.isoformat() + "Z",
        "source_system": channel,
        "customer_id": customer_id,
        "correlation_id": order_id,
        "payload": {
            "order_id": order_id,
            "customer_id": customer_id,
            "order_timestamp": now.isoformat() + "Z",
            "status": "pending",
            "total_amount": round(total_amount, 2),
            "currency": currency,
            "payment_method": random.choice(PAYMENT_METHODS),
            "store_id": store_id,
            "store_location": fake.city(),
            "country": country,
            "channel": channel,
            "order_items": items,
            "shipping_address": {
                "street": fake.street_address(),
                "city": fake.city(),
                "state": fake.state_abbr(),
                "zip_code": fake.postcode(),
                "country": country,
            },
        },
        "created_at": now.isoformat() + "Z",
    }

    # Update customer state
    _active_customers[customer_id]["order_count"] += 1
    _active_customers[customer_id]["total_spent"] += total_amount
    _active_customers[customer_id]["last_order"] = now

    return event


def generate_payment_event(order_event: dict, now: datetime) -> dict[str, Any]:
    """Generate a payment event linked to an order event."""
    payload = order_event["payload"]
    customer_id = payload["customer_id"]
    country = payload["country"]
    payment_id = _generate_payment_id(country)
    amount = payload["total_amount"]

    # 5% chance of payment failure
    is_failed = random.random() < 0.05
    failure_reason = random.choice(PAYMENT_FAILURE_REASONS) if is_failed else None

    # Fraud check: 2% chance of fraud
    fraud_score = round(random.uniform(0.7, 1.0), 3) if random.random() < 0.02 else round(random.uniform(0.0, 0.5), 3)

    event = {
        "event_id": _generate_event_id(),
        "event_type": "payment_processed",
        "event_timestamp": now.isoformat() + "Z",
        "source_system": order_event["source_system"],
        "customer_id": customer_id,
        "correlation_id": payment_id,
        "payload": {
            "payment_id": payment_id,
            "order_id": payload["order_id"],
            "customer_id": customer_id,
            "payment_timestamp": now.isoformat() + "Z",
            "amount": amount,
            "currency": payload["currency"],
            "payment_method": payload["payment_method"],
            "payment_status": "failed" if is_failed else "completed",
            "payment_provider": random.choice(["stripe", "paypal", "braintree", "square"]),
            "transaction_fee": round(amount * 0.029 + 0.30, 2),
            "is_refunded": False,
            "refund_amount": 0.0,
            "failure_reason": failure_reason,
            "risk_score": fraud_score,
            "country": country,
        },
        "created_at": now.isoformat() + "Z",
    }
    return event


def generate_inventory_event(now: datetime) -> dict[str, Any]:
    """Generate an inventory event (stock movement or alert)."""
    sku, name, price, cost, category = _pick_product()
    country = random.choice(COUNTRIES)

    # 8% chance of stockout, otherwise stock movement
    is_stockout = random.random() < 0.08

    if is_stockout:
        event_type = "inventory_stockout"
        quantity_change = -random.randint(5, 20)
    else:
        event_type = random.choice(["inventory_restock", "inventory_sale", "inventory_adjustment"])
        quantity_change = random.randint(-10, 50) if "sale" in event_type else random.randint(20, 100)

    event = {
        "event_id": _generate_event_id(),
        "event_type": event_type,
        "event_timestamp": now.isoformat() + "Z",
        "source_system": random.choice(CHANNELS),
        "customer_id": _generate_customer_id() if "sale" in event_type else None,
        "correlation_id": None,
        "payload": {
            "inventory_id": f"INV-{sku}-{now.strftime('%Y%m%d%H%M%S')}",
            "product_id": sku,
            "product_name": name,
            "category": category,
            "warehouse_id": f"WH-{country}-{random.randint(1, 5)}",
            "quantity_before": random.randint(50, 200),
            "quantity_change": quantity_change,
            "quantity_after": max(0, random.randint(0, 100)),
            "is_low_stock": random.random() < 0.1,
            "is_out_of_stock": is_stockout,
            "reorder_point": random.randint(10, 30),
            "country": country,
        },
        "created_at": now.isoformat() + "Z",
    }
    return event


def generate_delivery_event(order_event: dict, now: datetime) -> dict[str, Any]:
    """Generate a delivery event linked to an order."""
    payload = order_event["payload"]
    country = payload["country"]

    # 12% chance of delay
    is_delayed = random.random() < 0.12
    carrier = random.choice(CARRIERS)

    # Simulate delivery progress
    statuses = ["pending", "shipped", "in_transit", "out_for_delivery", "delivered"]
    status = random.choice(statuses[:3] if is_delayed else statuses)

    estimated_days = random.randint(1, 7)
    event = {
        "event_id": _generate_event_id(),
        "event_type": "delivery_update",
        "event_timestamp": now.isoformat() + "Z",
        "source_system": carrier,
        "customer_id": payload["customer_id"],
        "correlation_id": payload["order_id"],
        "payload": {
            "delivery_id": f"DEL-{fake.uuid4()[:8].upper()}",
            "order_id": payload["order_id"],
            "shipment_id": f"SHIP-{random.randint(100000, 999999)}",
            "carrier": carrier,
            "tracking_number": fake.bothify("??##########"),
            "status": status,
            "estimated_delivery_date": (now + timedelta(days=estimated_days)).isoformat() + "Z",
            "actual_delivery_date": (now + timedelta(days=estimated_days + random.randint(0, 2))).isoformat() + "Z" if status == "delivered" else None,
            "delivery_address": payload["shipping_address"],
            "shipping_method": random.choice(["standard", "express", "overnight"]),
            "shipping_cost": round(random.uniform(5.99, 25.99), 2),
            "weight_kg": round(random.uniform(0.5, 15.0), 2),
            "is_delayed": is_delayed,
            "delay_reason": random.choice(["weather", "carrier_delay", "customs", "address_issue"]) if is_delayed else None,
            "country": country,
        },
        "created_at": now.isoformat() + "Z",
    }
    return event


def generate_customer_behavior_event(now: datetime) -> dict[str, Any]:
    """Generate a customer behavior event."""
    customer_id = _generate_customer_id()
    country = _active_customers[customer_id]["country"]
    event_types = ["page_view", "product_view", "add_to_cart", "wishlist_add", "review_submit"]
    event_type = random.choice(event_types)

    sku, name, price, cost, category = _pick_product()

    event = {
        "event_id": _generate_event_id(),
        "event_type": f"customer_{event_type}",
        "event_timestamp": now.isoformat() + "Z",
        "source_system": random.choice(["Web", "Mobile", "App"]),
        "customer_id": customer_id,
        "correlation_id": None,
        "payload": {
            "session_id": fake.uuid4(),
            "page_url": f"/products/{sku.lower()}",
            "product_id": sku,
            "product_name": name,
            "category": category,
            "price": price,
            "duration_seconds": random.randint(10, 300) if "view" in event_type else None,
            "country": country,
        },
        "created_at": now.isoformat() + "Z",
    }
    return event


def generate_recommendation_event(now: datetime) -> dict[str, Any]:
    """Generate a recommendation impression/click event."""
    customer_id = _generate_customer_id()
    country = _active_customers[customer_id]["country"]
    sku, name, price, cost, category = _pick_product()

    event_types = ["recommendation_impression", "recommendation_click", "recommendation_purchase"]
    event_type = random.choices(event_types, weights=[70, 20, 10])[0]

    rec_types = ["also_bought", "recommended_for_you", "trending", "similar_products", "frequently_bought_together"]
    rec_type = random.choice(rec_types)

    event = {
        "event_id": _generate_event_id(),
        "event_type": event_type,
        "event_timestamp": now.isoformat() + "Z",
        "source_system": "recommendation-engine",
        "customer_id": customer_id,
        "correlation_id": None,
        "payload": {
            "recommendation_id": fake.uuid4(),
            "recommendation_type": rec_type,
            "product_id": sku,
            "product_name": name,
            "category": category,
            "position": random.randint(1, 10),
            "clicked": event_type == "recommendation_click",
            "purchased": event_type == "recommendation_purchase",
            "revenue_attributed": round(price, 2) if event_type == "recommendation_purchase" else 0.0,
            "country": country,
        },
        "created_at": now.isoformat() + "Z",
    }
    return event


def generate_fraud_signal_event(payment_event: dict, now: datetime) -> dict[str, Any]:
    """Generate a fraud signal event if payment has elevated risk."""
    risk_score = payment_event["payload"]["risk_score"]

    # Only generate fraud event if risk score > 0.3
    if risk_score < 0.3:
        return None

    payload = payment_event["payload"]
    fraud_type = random.choice(FRAUD_TYPES)

    event = {
        "event_id": _generate_event_id(),
        "event_type": "fraud_signal_detected",
        "event_timestamp": now.isoformat() + "Z",
        "source_system": "fraud-detection-engine",
        "customer_id": payload["customer_id"],
        "correlation_id": payment_event["correlation_id"],
        "payload": {
            "fraud_event_id": f"FRAUD-{fake.uuid4()[:12].upper()}",
            "order_id": payload["order_id"],
            "payment_id": payload["payment_id"],
            "customer_id": payload["customer_id"],
            "fraud_timestamp": now.isoformat() + "Z",
            "fraud_type": fraud_type,
            "fraud_score": risk_score,
            "risk_factors": [fraud_type, f"amount_{payload['amount']}", f"country_{payload['country']}"],
            "action_taken": "review" if risk_score < 0.7 else "block",
            "is_confirmed": False,
            "country": payload["country"],
        },
        "created_at": now.isoformat() + "Z",
    }
    return event


def generate_customer_profile_event(customer_id: str, now: datetime) -> dict[str, Any]:
    """Generate a customer profile update event."""
    state = _active_customers[customer_id]

    event_types = ["profile_registration", "profile_update", "loyalty_tier_change"]
    event_type = random.choices(event_types, weights=[30, 50, 20])[0]

    new_tier = state["loyalty_tier"]
    if event_type == "loyalty_tier_change":
        tiers_order = ["bronze", "silver", "gold", "platinum"]
        current_idx = tiers_order.index(new_tier)
        new_tier = random.choice(tiers_order[current_idx + 1:]) if current_idx < 3 else tiers_order[-1]

    event = {
        "event_id": _generate_event_id(),
        "event_type": f"customer_{event_type}",
        "event_timestamp": now.isoformat() + "Z",
        "source_system": random.choice(["Web", "POS", "Mobile", "App"]),
        "customer_id": customer_id,
        "correlation_id": None,
        "payload": {
            "customer_id": customer_id,
            "email": state["email"],
            "first_name": state["first_name"],
            "last_name": state["last_name"],
            "phone_number": fake.phone_number(),
            "customer_segment": state["segment"],
            "loyalty_tier": new_tier,
            "previous_loyalty_tier": state["loyalty_tier"] if event_type == "loyalty_tier_change" else None,
            "loyalty_points": random.randint(0, 10000) if new_tier != "bronze" else 0,
            "registration_date": state["join_date"].isoformat() + "Z",
            "country": state["country"],
            "city": fake.city(),
            "postal_code": fake.postcode(),
            "total_orders": state["order_count"],
            "total_spent": round(state["total_spent"], 2),
            "average_order_value": round(state["total_spent"] / state["order_count"], 2) if state["order_count"] > 0 else 0.0,
        },
        "created_at": now.isoformat() + "Z",
    }
    return event


# =============================================================================
# KAFKA PRODUCER
# =============================================================================

class RetailEventProducer:
    def __init__(self, bootstrap_servers: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            retries=3,
            retry_backoff_ms=500,
            # Batching for throughput
            batch_size=16384,
            linger_ms=10,
            compression_type="gzip",
        )
        self.topics = TOPICS
        self.running = True

    def _send(self, topic: str, key: str | None, event: dict):
        """Send an event to a Kafka topic."""
        try:
            future = self.producer.send(topic, key=key, value=event)
            future.add_callback(lambda m: None)  # fire-and-forget
            future.add_errback(lambda e: print(f"[ERROR] Failed to send to {topic}: {e}"))
        except KafkaError as e:
            print(f"[ERROR] Kafka error sending to {topic}: {e}")

    def produce_events(self, now: datetime):
        """
        Produce a batch of events for the current time window.
        Called once per batch interval.
        """
        produced_order = None

        # 1. Order event (most common — every batch has 1-3 orders)
        for _ in range(random.randint(1, 3)):
            order_event = generate_order_event(now)
            self._send(self.topics["orders"], order_event["payload"]["order_id"], order_event)
            produced_order = order_event

            # 2. Linked payment event (follows order immediately)
            payment_event = generate_payment_event(order_event, now)
            self._send(self.topics["payments"], payment_event["payload"]["payment_id"], payment_event)

            # 3. Linked delivery event (follows order)
            delivery_event = generate_delivery_event(order_event, now)
            self._send(self.topics["delivery"], delivery_event["payload"]["delivery_id"], delivery_event)

            # 4. Fraud signal (if applicable)
            fraud_event = generate_fraud_signal_event(payment_event, now)
            if fraud_event:
                self._send(self.topics["fraud_signals"], fraud_event["payload"]["fraud_event_id"], fraud_event)

            # 5. Customer profile event (occasional update for existing customers)
            if random.random() < 0.1 and _customer_ids:
                cust_id = random.choice(_customer_ids)
                profile_event = generate_customer_profile_event(cust_id, now)
                self._send(self.topics["customer_profile"], cust_id, profile_event)

        # 6. Inventory event (every batch has 1-2)
        for _ in range(random.randint(1, 2)):
            inventory_event = generate_inventory_event(now)
            self._send(self.topics["inventory"], inventory_event["payload"]["product_id"], inventory_event)

        # 7. Customer behavior events (every batch has 2-4)
        for _ in range(random.randint(2, 4)):
            behavior_event = generate_customer_behavior_event(now)
            self._send(self.topics["customer_behavior"], behavior_event["payload"].get("session_id"), behavior_event)

        # 8. Recommendation events (every batch has 1-2)
        for _ in range(random.randint(1, 2)):
            rec_event = generate_recommendation_event(now)
            self._send(self.topics["recommendations"], rec_event["payload"]["recommendation_id"], rec_event)

    def flush(self):
        """Flush all pending messages."""
        self.producer.flush()

    def close(self):
        """Close the producer."""
        self.running = False
        self.producer.flush()
        self.producer.close()


# =============================================================================
# MAIN LOOP
# =============================================================================

def main():
    print("=" * 60)
    print("Enterprise Retail Streaming Platform — Data Generator")
    print("=" * 60)
    print(f"Kafka Bootstrap Servers : {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Target Throughput       : ~{EVENTS_PER_SECOND} events/sec")
    print(f"Topics:")
    for name, topic in TOPICS.items():
        print(f"  {name:20s} -> {topic}")
    print("=" * 60)

    producer = RetailEventProducer(KAFKA_BOOTSTRAP_SERVERS)

    # Wait for Kafka to be ready
    print("\nWaiting for Kafka to be ready...")
    for attempt in range(30):
        try:
            producer.producer.bootstrap_connected()
            print("Kafka is ready!")
            break
        except Exception:
            print(f"  Attempt {attempt + 1}/30 — waiting 2s...")
            time.sleep(2)
    else:
        print("[WARN] Could not connect to Kafka — continuing anyway (will retry)")

    print("\nStarting event generation... Press Ctrl+C to stop")
    print("-" * 60)

    batch_interval = BATCH_SIZE / EVENTS_PER_SECOND  # seconds per batch

    try:
        while True:
            now = datetime.utcnow()
            time_mult = _get_time_multiplier()
            adjusted_interval = batch_interval / time_mult if time_mult > 0 else batch_interval

            producer.produce_events(now)
            producer.flush()

            print(
                f"[{now.strftime('%H:%M:%S')}] "
                f"Sent batch (~{int(BATCH_SIZE * time_mult)} events) | "
                f"Time mult: {time_mult:.2f}x | "
                f"Active customers: {len(_customer_ids)}"
            )

            time.sleep(max(0.1, adjusted_interval))

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        producer.close()
        print("Done.")


if __name__ == "__main__":
    main()