#!/usr/bin/env python3
"""
Retail Streaming Platform — Kafka to Iceberg via PySpark Structured Streaming
"""

import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, get_json_object
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType


spark = SparkSession.builder \
    .appName("RetailKafkaToIceberg") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.defaultCatalog", "demo") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print("SparkSession created")


def jget(path, as_type=None):
    """Extract JSON field from Kafka value column."""
    c = get_json_object(col("value").cast("string"), path)
    if as_type == "double":
        return c.cast("double")
    elif as_type == "int":
        return c.cast("int")
    return c


# ── Table creation ───────────────────────────────────────────────────────────

def create_tables():
    spark.sql("CREATE NAMESPACE IF NOT EXISTS demo.retail")

    spark.sql("""
        CREATE TABLE IF NOT EXISTS demo.retail.orders (
            event_id STRING, event_type STRING, event_timestamp STRING,
            source_system STRING, customer_id STRING, event_time STRING,
            order_id STRING, status STRING, total_amount DOUBLE,
            currency STRING, payment_method STRING, store_id STRING,
            country STRING, channel STRING
        ) USING iceberg PARTITIONED BY (country)
    """)
    spark.sql("""
        CREATE TABLE IF NOT EXISTS demo.retail.payments (
            event_id STRING, event_type STRING, event_timestamp STRING,
            source_system STRING, customer_id STRING, event_time STRING,
            payment_id STRING, order_id STRING, amount DOUBLE,
            currency STRING, payment_status STRING, fraud_score DOUBLE
        ) USING iceberg
    """)
    spark.sql("""
        CREATE TABLE IF NOT EXISTS demo.retail.inventory (
            event_id STRING, event_type STRING, event_timestamp STRING,
            source_system STRING, event_time STRING,
            product_id STRING, product_name STRING, store_id STRING,
            quantity_on_hand INT, reorder_level INT
        ) USING iceberg PARTITIONED BY (store_id)
    """)
    spark.sql("""
        CREATE TABLE IF NOT EXISTS demo.retail.delivery (
            event_id STRING, event_type STRING, event_timestamp STRING,
            source_system STRING, customer_id STRING, event_time STRING,
            delivery_id STRING, order_id STRING, status STRING,
            carrier STRING, estimated_delivery STRING
        ) USING iceberg
    """)
    spark.sql("""
        CREATE TABLE IF NOT EXISTS demo.retail.fraud_signals (
            event_id STRING, event_type STRING, event_timestamp STRING,
            source_system STRING, customer_id STRING, event_time STRING,
            order_id STRING, fraud_score DOUBLE, risk_level STRING,
            risk_factors STRING, action_taken STRING
        ) USING iceberg
    """)
    spark.sql("""
        CREATE TABLE IF NOT EXISTS demo.retail.customer_profile (
            event_id STRING, event_type STRING, event_timestamp STRING,
            source_system STRING, customer_id STRING, event_time STRING,
            email STRING, name STRING, loyalty_tier STRING,
            lifetime_value DOUBLE, total_orders INT, country STRING
        ) USING iceberg
    """)
    print("Tables created/verified.")


# ── Stream readers ─────────────────────────────────────────────────────────

def read_orders():
    return spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "retail.orders") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load() \
        .select(
            jget("$.event_id").alias("event_id"),
            jget("$.event_type").alias("event_type"),
            jget("$.event_timestamp").alias("event_timestamp"),
            jget("$.source_system").alias("source_system"),
            jget("$.customer_id").alias("customer_id"),
            jget("$.created_at").alias("event_time"),
            jget("$.payload.order_id").alias("order_id"),
            jget("$.payload.status").alias("status"),
            jget("$.payload.total_amount", "double").alias("total_amount"),
            jget("$.payload.currency").alias("currency"),
            jget("$.payload.payment_method").alias("payment_method"),
            jget("$.payload.store_id").alias("store_id"),
            jget("$.payload.country").alias("country"),
            jget("$.payload.channel").alias("channel"),
        )


def read_payments():
    return spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "retail.payments") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load() \
        .select(
            jget("$.event_id").alias("event_id"),
            jget("$.event_type").alias("event_type"),
            jget("$.event_timestamp").alias("event_timestamp"),
            jget("$.source_system").alias("source_system"),
            jget("$.customer_id").alias("customer_id"),
            jget("$.created_at").alias("event_time"),
            jget("$.payload.payment_id").alias("payment_id"),
            jget("$.payload.order_id").alias("order_id"),
            jget("$.payload.amount", "double").alias("amount"),
            jget("$.payload.currency").alias("currency"),
            jget("$.payload.payment_status").alias("payment_status"),
            jget("$.payload.fraud_score", "double").alias("fraud_score"),
        )


def read_inventory():
    return spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "retail.inventory") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load() \
        .select(
            jget("$.event_id").alias("event_id"),
            jget("$.event_type").alias("event_type"),
            jget("$.event_timestamp").alias("event_timestamp"),
            jget("$.source_system").alias("source_system"),
            jget("$.created_at").alias("event_time"),
            jget("$.payload.product_id").alias("product_id"),
            jget("$.payload.product_name").alias("product_name"),
            jget("$.payload.store_id").alias("store_id"),
            jget("$.payload.quantity_on_hand", "int").alias("quantity_on_hand"),
            jget("$.payload.reorder_level", "int").alias("reorder_level"),
        )


def read_delivery():
    return spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "retail.delivery") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load() \
        .select(
            jget("$.event_id").alias("event_id"),
            jget("$.event_type").alias("event_type"),
            jget("$.event_timestamp").alias("event_timestamp"),
            jget("$.source_system").alias("source_system"),
            jget("$.customer_id").alias("customer_id"),
            jget("$.created_at").alias("event_time"),
            jget("$.payload.delivery_id").alias("delivery_id"),
            jget("$.payload.order_id").alias("order_id"),
            jget("$.payload.status").alias("status"),
            jget("$.payload.carrier").alias("carrier"),
            jget("$.payload.estimated_delivery").alias("estimated_delivery"),
        )


def read_fraud():
    return spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "retail.fraud_signals") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load() \
        .select(
            jget("$.event_id").alias("event_id"),
            jget("$.event_type").alias("event_type"),
            jget("$.event_timestamp").alias("event_timestamp"),
            jget("$.source_system").alias("source_system"),
            jget("$.customer_id").alias("customer_id"),
            jget("$.created_at").alias("event_time"),
            jget("$.payload.order_id").alias("order_id"),
            jget("$.payload.fraud_score", "double").alias("fraud_score"),
            jget("$.payload.risk_level").alias("risk_level"),
            jget("$.payload.risk_factors").alias("risk_factors"),
            jget("$.payload.action_taken").alias("action_taken"),
        )


def read_customer():
    return spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "retail.customer_profile") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load() \
        .select(
            jget("$.event_id").alias("event_id"),
            jget("$.event_type").alias("event_type"),
            jget("$.event_timestamp").alias("event_timestamp"),
            jget("$.source_system").alias("source_system"),
            jget("$.customer_id").alias("customer_id"),
            jget("$.created_at").alias("event_time"),
            jget("$.payload.email").alias("email"),
            jget("$.payload.name").alias("name"),
            jget("$.payload.loyalty_tier").alias("loyalty_tier"),
            jget("$.payload.lifetime_value", "double").alias("lifetime_value"),
            jget("$.payload.total_orders", "int").alias("total_orders"),
            jget("$.payload.country").alias("country"),
        )


# ── Write Streams ─────────────────────────────────────────────────────────────

CHECKPOINT = "/tmp/checkpoints/"

def start_stream(read_fn, table):
    q = read_fn().writeStream \
        .format("iceberg") \
        .outputMode("append") \
        .trigger(processingTime="5 seconds") \
        .option("checkpointLocation", f"{CHECKPOINT}{table}") \
        .toTable(f"demo.retail.{table}")
    print(f"Started: demo.retail.{table}")
    return q


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Starting streaming queries...")
    create_tables()

    streams = [
        (read_orders, "orders"),
        (read_payments, "payments"),
        (read_inventory, "inventory"),
        (read_delivery, "delivery"),
        (read_fraud, "fraud_signals"),
        (read_customer, "customer_profile"),
    ]

    queries = [start_stream(fn, tbl) for fn, tbl in streams]
    print(f"All {len(queries)} streams started.")

    try:
        for q in queries:
            q.awaitTermination()
    except KeyboardInterrupt:
        print("Shutting down...")
        for q in queries:
            q.stop()
        spark.stop()
        sys.exit(0)
