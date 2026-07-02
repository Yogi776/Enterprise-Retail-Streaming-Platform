#!/usr/bin/env python3
"""
Data Quality Scanner for Retail Streaming Platform
Connects to Trino and validates Iceberg tables
"""

from trino.dbapi import connect
import sys
from datetime import datetime

# Trino connection
TRINO_HOST = "trino"
TRINO_PORT = 8080
CATALOG = "iceberg"
SCHEMA = "retail"

def get_connection():
    return connect(host=TRINO_HOST, port=TRINO_PORT, catalog=CATALOG, schema=SCHEMA, user="admin")

def run_check(cursor, name, query, expected_pass=True):
    """Run a check and return result"""
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        passed = result[0] == 1 if expected_pass else result[0] == 0
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
        return passed
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return False

def check_table(cursor, table_name, checks):
    """Check a table with given checks"""
    print(f"\n=== Checking table: {table_name} ===")
    all_passed = True
    for check in checks:
        name = check["name"]
        query = check["query"]
        passed = run_check(cursor, name, query)
        if not passed:
            all_passed = False
    return all_passed

def main():
    print("=" * 60)
    print("DATA QUALITY SCAN - Retail Streaming Platform")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    print(f"Target: Trino {TRINO_HOST}:{TRINO_PORT}/{CATALOG}.{SCHEMA}")
    print()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get table list
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Found tables: {', '.join(tables)}")

        all_tables_passed = True

        # ORDERS table checks
        if check_table(cursor, "orders", [
            {"name": "Table has data (row_count > 0)", "query": "SELECT CASE WHEN count(*) > 0 THEN 1 ELSE 0 END FROM orders"},
            {"name": "No null event_ids", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM orders WHERE event_id IS NULL"},
            {"name": "No null order_ids", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM orders WHERE order_id IS NULL"},
            {"name": "No null customer_ids", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM orders WHERE customer_id IS NULL"},
            {"name": "Total amount >= 0", "query": "SELECT CASE WHEN min(total_amount) >= 0 THEN 1 ELSE 0 END FROM orders"},
            {"name": "No null total_amounts", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM orders WHERE total_amount IS NULL"},
            {"name": "Valid status values", "query": "SELECT CASE WHEN count(DISTINCT status) >= 1 THEN 1 ELSE 0 END FROM orders"},
        ]):
            pass
        else:
            all_tables_passed = False

        # PAYMENTS table checks
        if check_table(cursor, "payments", [
            {"name": "Table has data (row_count > 0)", "query": "SELECT CASE WHEN count(*) > 0 THEN 1 ELSE 0 END FROM payments"},
            {"name": "No null event_ids", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM payments WHERE event_id IS NULL"},
            {"name": "No null payment_ids", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM payments WHERE payment_id IS NULL"},
            {"name": "No null order_ids", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM payments WHERE order_id IS NULL"},
            {"name": "Amount >= 0", "query": "SELECT CASE WHEN min(amount) >= 0 THEN 1 ELSE 0 END FROM payments"},
            {"name": "No null amounts", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM payments WHERE amount IS NULL"},
            {"name": "Valid payment_status", "query": "SELECT CASE WHEN count(DISTINCT payment_status) >= 1 THEN 1 ELSE 0 END FROM payments"},
        ]):
            pass
        else:
            all_tables_passed = False

        # CUSTOMER_PROFILE table checks
        if check_table(cursor, "customer_profile", [
            {"name": "Table has data (row_count > 0)", "query": "SELECT CASE WHEN count(*) > 0 THEN 1 ELSE 0 END FROM customer_profile"},
            {"name": "No null event_ids", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM customer_profile WHERE event_id IS NULL"},
            {"name": "No null customer_ids", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM customer_profile WHERE customer_id IS NULL"},
            {"name": "Customer_ids are unique", "query": "SELECT CASE WHEN count(DISTINCT customer_id) = count(*) THEN 1 ELSE 0 END FROM customer_profile"},
            {"name": "No null emails", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM customer_profile WHERE email IS NULL"},
            {"name": "No null loyalty_tiers", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM customer_profile WHERE loyalty_tier IS NULL"},
        ]):
            pass
        else:
            all_tables_passed = False

        # INVENTORY table checks
        if check_table(cursor, "inventory", [
            {"name": "Table has data (row_count > 0)", "query": "SELECT CASE WHEN count(*) > 0 THEN 1 ELSE 0 END FROM inventory"},
            {"name": "No null product_ids", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM inventory WHERE product_id IS NULL"},
            {"name": "Quantity on hand >= 0", "query": "SELECT CASE WHEN min(quantity_on_hand) >= 0 THEN 1 ELSE 0 END FROM inventory"},
            {"name": "Reorder level >= 0", "query": "SELECT CASE WHEN min(reorder_level) >= 0 THEN 1 ELSE 0 END FROM inventory"},
        ]):
            pass
        else:
            all_tables_passed = False

        # FRAUD_SIGNALS table checks
        if check_table(cursor, "fraud_signals", [
            {"name": "Table has data (row_count > 0)", "query": "SELECT CASE WHEN count(*) > 0 THEN 1 ELSE 0 END FROM fraud_signals"},
            {"name": "No null event_ids", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM fraud_signals WHERE event_id IS NULL"},
            {"name": "No null customer_ids", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM fraud_signals WHERE customer_id IS NULL"},
            {"name": "Fraud score 0-1 range", "query": "SELECT CASE WHEN min(fraud_score) >= 0 AND max(fraud_score) <= 1 THEN 1 ELSE 0 END FROM fraud_signals"},
        ]):
            pass
        else:
            all_tables_passed = False

        # DELIVERY table checks
        if check_table(cursor, "delivery", [
            {"name": "Table has data (row_count > 0)", "query": "SELECT CASE WHEN count(*) > 0 THEN 1 ELSE 0 END FROM delivery"},
            {"name": "No null event_ids", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM delivery WHERE event_id IS NULL"},
            {"name": "No null order_ids", "query": "SELECT CASE WHEN count(*) = 0 THEN 1 ELSE 0 END FROM delivery WHERE order_id IS NULL"},
        ]):
            pass
        else:
            all_tables_passed = False

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        if all_tables_passed:
            print("RESULT: ALL CHECKS PASSED")
            print("=" * 60)
            return 0
        else:
            print("RESULT: SOME CHECKS FAILED")
            print("=" * 60)
            return 1

    except Exception as e:
        print(f"\nERROR: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
