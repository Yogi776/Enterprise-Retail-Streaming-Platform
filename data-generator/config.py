# Configuration for Data Generator
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_ORDERS = os.getenv("KAFKA_TOPIC_ORDERS", "retail.orders")
KAFKA_TOPIC_PAYMENTS = os.getenv("KAFKA_TOPIC_PAYMENTS", "retail.payments")
KAFKA_TOPIC_INVENTORY = os.getenv("KAFKA_TOPIC_INVENTORY", "retail.inventory")
KAFKA_TOPIC_CUSTOMERS = os.getenv("KAFKA_TOPIC_CUSTOMERS", "retail.customers")
KAFKA_TOPIC_FRAUD = os.getenv("KAFKA_TOPIC_FRAUD", "retail.fraud")

EVENTS_PER_SECOND = int(os.getenv("EVENTS_PER_SECOND", "100"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))

COUNTRIES = ["US", "UK", "DE", "FR", "ES", "IT", "JP", "AU"]
CURRENCIES = {"US": "USD", "UK": "GBP", "DE": "EUR", "FR": "EUR", "ES": "EUR", "IT": "EUR", "JP": "JPY", "AU": "AUD"}