#!/usr/bin/env python3
"""
Retail Streaming Platform — Kafka to Iceberg Writer
Uses tabulario REST catalog for metadata + PostgreSQL for tracking table locations.
"""

import os
import sys
import time
import json
import signal
from datetime import datetime, timezone
from typing import Dict, List, Optional

from kafka import KafkaConsumer
import boto3
from botocore.config import Config
import pyarrow as pa
import pyarrow.parquet as pq
import requests


# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
ICEBERG_REST_URL = os.getenv("ICEBERG_REST_URL", "http://iceberg-rest:8181")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin123")
S3_BUCKET = os.getenv("S3_BUCKET", "warehouse")

TOPICS_TO_TABLES = {
    "retail.orders": "orders",
    "retail.payments": "payments",
    "retail.inventory": "inventory",
    "retail.delivery": "delivery",
    "retail.fraud_signals": "fraud_signals",
    "retail.customer_profile": "customer_profile",
}
TOPICS = list(TOPICS_TO_TABLES.keys())


class S3Writer:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str):
        self.s3 = boto3.client(
            "s3", endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
        )
        self.bucket = bucket

    def write_parquet(self, key: str, data: List[Dict]) -> int:
        if not data:
            return 0
        schema_fields = []
        for row in data:
            for col, val in row.items():
                if col not in [f.name for f in schema_fields]:
                    typ = pa.int64() if isinstance(val, int) else (pa.float64() if isinstance(val, float) else pa.string())
                    schema_fields.append(pa.field(col, typ))
        schema = pa.schema(schema_fields)
        col_data = {f.name: [row.get(f.name) for row in data] for f in schema}
        table = pa.Table.from_pydict(col_data, schema=schema)
        buffer = pa.BufferOutputStream()
        pq.write_table(table, buffer, compression="snappy")
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=buffer.getvalue().to_pybytes())
        return len(buffer.getvalue().to_pybytes())


def extract_row(topic: str, raw: Dict) -> Optional[Dict]:
    payload = raw.get("payload", {})
    event_time = raw.get("event_timestamp", datetime.now(timezone.utc).isoformat())
    base = {
        "event_id": raw.get("event_id"), "event_type": raw.get("event_type"),
        "event_timestamp": raw.get("event_timestamp"), "source_system": raw.get("source_system"),
        "customer_id": payload.get("customer_id", raw.get("customer_id")), "event_time": event_time,
    }
    if topic == "retail.orders":
        base.update({"order_id": payload.get("order_id"), "status": payload.get("status"),
            "total_amount": float(payload.get("total_amount", 0)), "currency": payload.get("currency"),
            "payment_method": payload.get("payment_method"), "store_id": payload.get("store_id"),
            "country": payload.get("country"), "channel": payload.get("channel")})
    elif topic == "retail.payments":
        base.update({"payment_id": payload.get("payment_id"), "order_id": payload.get("order_id"),
            "amount": float(payload.get("amount", 0)), "currency": payload.get("currency"),
            "payment_status": payload.get("payment_status"), "fraud_score": float(payload.get("fraud_score", 0))})
    elif topic == "retail.inventory":
        base.update({"product_id": payload.get("product_id"), "product_name": payload.get("product_name"),
            "store_id": payload.get("store_id"), "quantity_on_hand": int(payload.get("quantity_on_hand", 0)),
            "reorder_level": int(payload.get("reorder_level", 0))})
    elif topic == "retail.delivery":
        base.update({"delivery_id": payload.get("delivery_id"), "order_id": payload.get("order_id"),
            "carrier": payload.get("carrier"), "status": payload.get("status"),
            "estimated_delivery": payload.get("estimated_delivery")})
    elif topic == "retail.fraud_signals":
        base.update({"order_id": payload.get("order_id"), "fraud_event_id": payload.get("fraud_event_id"),
            "fraud_score": float(payload.get("fraud_score", 0)), "risk_level": payload.get("risk_level"),
            "risk_factors": json.dumps(payload.get("risk_factors", [])), "action_taken": payload.get("action_taken")})
    elif topic == "retail.customer_profile":
        base.update({"email": payload.get("email"), "name": payload.get("name"),
            "loyalty_tier": payload.get("loyalty_tier"),
            "lifetime_value": float(payload.get("lifetime_value", 0)),
            "total_orders": int(payload.get("total_orders", 0)), "country": payload.get("country")})
    return base


def create_tables():
    """Create tables via REST API."""
    ns_payload = {"namespace": ["retail"]}
    try:
        r = requests.post(f"{ICEBERG_REST_URL}/v1/namespaces", json=ns_payload, headers={"Content-Type": "application/json"})
        if r.status_code not in (200, 201, 409):
            print(f"  Namespace create: {r.status_code} {r.text[:80]}")
    except Exception as e:
        print(f"  Namespace error: {e}")

    tables = {
        "orders": [
            {"id": 1, "name": "event_id", "type": "string", "required": False}, {"id": 2, "name": "event_type", "type": "string", "required": False},
            {"id": 3, "name": "event_timestamp", "type": "string", "required": False}, {"id": 4, "name": "source_system", "type": "string", "required": False},
            {"id": 5, "name": "customer_id", "type": "string", "required": False}, {"id": 6, "name": "event_time", "type": "string", "required": False},
            {"id": 7, "name": "order_id", "type": "string", "required": False}, {"id": 8, "name": "status", "type": "string", "required": False},
            {"id": 9, "name": "total_amount", "type": "double", "required": False}, {"id": 10, "name": "currency", "type": "string", "required": False},
            {"id": 11, "name": "payment_method", "type": "string", "required": False}, {"id": 12, "name": "store_id", "type": "string", "required": False},
            {"id": 13, "name": "country", "type": "string", "required": False}, {"id": 14, "name": "channel", "type": "string", "required": False},
        ],
        "payments": [
            {"id": 1, "name": "event_id", "type": "string", "required": False}, {"id": 2, "name": "event_type", "type": "string", "required": False},
            {"id": 3, "name": "event_timestamp", "type": "string", "required": False}, {"id": 4, "name": "source_system", "type": "string", "required": False},
            {"id": 5, "name": "customer_id", "type": "string", "required": False}, {"id": 6, "name": "event_time", "type": "string", "required": False},
            {"id": 7, "name": "payment_id", "type": "string", "required": False}, {"id": 8, "name": "order_id", "type": "string", "required": False},
            {"id": 9, "name": "amount", "type": "double", "required": False}, {"id": 10, "name": "currency", "type": "string", "required": False},
            {"id": 11, "name": "payment_status", "type": "string", "required": False}, {"id": 12, "name": "fraud_score", "type": "double", "required": False},
        ],
        "inventory": [
            {"id": 1, "name": "event_id", "type": "string", "required": False}, {"id": 2, "name": "event_type", "type": "string", "required": False},
            {"id": 3, "name": "event_timestamp", "type": "string", "required": False}, {"id": 4, "name": "source_system", "type": "string", "required": False},
            {"id": 5, "name": "event_time", "type": "string", "required": False}, {"id": 6, "name": "product_id", "type": "string", "required": False},
            {"id": 7, "name": "store_id", "type": "string", "required": False}, {"id": 8, "name": "quantity_on_hand", "type": "int", "required": False},
            {"id": 9, "name": "reorder_level", "type": "int", "required": False},
        ],
        "delivery": [
            {"id": 1, "name": "event_id", "type": "string", "required": False}, {"id": 2, "name": "event_type", "type": "string", "required": False},
            {"id": 3, "name": "event_timestamp", "type": "string", "required": False}, {"id": 4, "name": "source_system", "type": "string", "required": False},
            {"id": 5, "name": "customer_id", "type": "string", "required": False}, {"id": 6, "name": "event_time", "type": "string", "required": False},
            {"id": 7, "name": "delivery_id", "type": "string", "required": False}, {"id": 8, "name": "order_id", "type": "string", "required": False},
            {"id": 9, "name": "status", "type": "string", "required": False}, {"id": 10, "name": "carrier", "type": "string", "required": False},
            {"id": 11, "name": "estimated_delivery", "type": "string", "required": False},
        ],
        "fraud_signals": [
            {"id": 1, "name": "event_id", "type": "string", "required": False}, {"id": 2, "name": "event_type", "type": "string", "required": False},
            {"id": 3, "name": "event_timestamp", "type": "string", "required": False}, {"id": 4, "name": "source_system", "type": "string", "required": False},
            {"id": 5, "name": "customer_id", "type": "string", "required": False}, {"id": 6, "name": "event_time", "type": "string", "required": False},
            {"id": 7, "name": "order_id", "type": "string", "required": False}, {"id": 8, "name": "fraud_score", "type": "double", "required": False},
            {"id": 9, "name": "risk_level", "type": "string", "required": False}, {"id": 10, "name": "risk_factors", "type": "string", "required": False},
            {"id": 11, "name": "action_taken", "type": "string", "required": False},
        ],
        "customer_profile": [
            {"id": 1, "name": "event_id", "type": "string", "required": False}, {"id": 2, "name": "event_type", "type": "string", "required": False},
            {"id": 3, "name": "event_timestamp", "type": "string", "required": False}, {"id": 4, "name": "source_system", "type": "string", "required": False},
            {"id": 5, "name": "customer_id", "type": "string", "required": False}, {"id": 6, "name": "event_time", "type": "string", "required": False},
            {"id": 7, "name": "email", "type": "string", "required": False}, {"id": 8, "name": "name", "type": "string", "required": False},
            {"id": 9, "name": "loyalty_tier", "type": "string", "required": False}, {"id": 10, "name": "lifetime_value", "type": "double", "required": False},
            {"id": 11, "name": "total_orders", "type": "int", "required": False}, {"id": 12, "name": "country", "type": "string", "required": False},
        ],
    }
    for table_name, schema in tables.items():
        payload = {
            "name": f"retail.{table_name}",
            "location": f"s3://{S3_BUCKET}/retail/retail.{table_name}",
            "schema": {"type": "struct", "schema-id": 0, "fields": [{"id": f["id"], "name": f["name"], "type": f["type"], "required": f.get("required", False)} for f in schema]},
            "partition-specs": [{"spec-id": 0, "fields": []}],
            "default-sort-order": {"order-id": 0, "fields": []},
        }
        try:
            r = requests.post(f"{ICEBERG_REST_URL}/v1/namespaces/retail/tables", json=payload, headers={"Content-Type": "application/json"})
            if r.status_code in (200, 201):
                print(f"  Table '{table_name}': created")
            elif r.status_code == 409:
                print(f"  Table '{table_name}': already exists")
            else:
                print(f"  Table '{table_name}': {r.status_code} {r.text[:80]}")
        except Exception as e:
            print(f"  Table '{table_name}': error {e}")


def run():
    print("=" * 60)
    print("Retail Stream to Iceberg Writer")
    print("=" * 60)
    print(f"Kafka: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Iceberg REST: {ICEBERG_REST_URL}")
    print(f"S3: {S3_ENDPOINT} Bucket: {S3_BUCKET}\n")

    writer = S3Writer(S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET)

    print("Creating tables via REST API...")
    create_tables()
    print("\nStarting main loop...")

    print("Creating KafkaConsumer...", flush=True)
    sys.stdout.flush()
    consumer = KafkaConsumer(
        *TOPICS, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="retail-stream-consumer",
        auto_offset_reset="earliest", enable_auto_commit=True, auto_commit_interval_ms=5000,
    )
    print(f"Subscribed: {consumer.subscription()}\n")

    buffers = {t: [] for t in TOPICS}
    pending_files = {t: [] for t in TOPICS}
    BATCH_SIZE = 100
    FLUSH_INTERVAL = 10
    last_flush = time.time()
    totals = {t: 0 for t in TOPICS}

    def flush_all():
        for topic in TOPICS:
            if not buffers[topic]:
                continue
            table_name = TOPICS_TO_TABLES[topic]
            ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
            data = buffers[topic]
            s3_key = f"retail/retail.{table_name}/data/{ts}.parquet"
            size = writer.write_parquet(s3_key, data)
            totals[topic] += len(data)
            buffers[topic] = []
            pending_files[topic].append({"data-file": s3_key, "file-size": size, "record-count": len(data)})
            if len(pending_files[topic]) >= 5:
                print(f"  {table_name}: {len(pending_files[topic])} files pending, totals: {totals[topic]}")

    def signal_handler(sig, frame):
        print("\nFlushing...")
        flush_all()
        print("Exiting.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while True:
        msgs = consumer.poll(timeout_ms=1000)
        for tp, records in msgs.items():
            topic = tp.topic
            for msg in records:
                try:
                    val = msg.value.decode("utf-8") if isinstance(msg.value, bytes) else msg.value
                    data = json.loads(val) if isinstance(val, str) else val
                    row = extract_row(topic, data)
                    if row:
                        buffers[topic].append(row)
                except Exception:
                    pass
        for topic in TOPICS:
            if len(buffers[topic]) >= BATCH_SIZE:
                flush_all()
        if time.time() - last_flush >= FLUSH_INTERVAL:
            flush_all()
            if sum(totals.values()) > 0:
                print(f"  Totals: " + ", ".join(f"retail.{TOPICS_TO_TABLES[t]}={totals[t]}" for t in TOPICS))
            last_flush = time.time()


if __name__ == "__main__":
    run()
