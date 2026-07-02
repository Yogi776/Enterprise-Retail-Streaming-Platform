#!/usr/bin/env python3
"""
End-to-End Benchmark for Retail Streaming Platform
Measures: Kafka -> Spark -> Iceberg -> Trino throughput
"""

import subprocess
import time
import json
from datetime import datetime
from trino.dbapi import connect as trino_connect

# Configuration
KAFKA_BOOTSTRAP = "kafka:29092"
TRINO_HOST = "trino"
TRINO_PORT = 8080
CATALOG = "iceberg"
SCHEMA = "retail"
BENCHMARK_DURATION_SEC = 300  # 5 minutes per scenario
POLL_INTERVAL_SEC = 10

TABLES = ["orders", "payments", "inventory", "delivery", "fraud_signals", "customer_profile"]
TOPICS = ["retail.orders", "retail.payments", "retail.inventory", "retail.delivery", 
          "retail.fraud_signals", "retail.customer_profile"]
CONSUMER_GROUP = "retail-stream-consumer"

def run_cmd(cmd, timeout=30):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", 1

def get_kafka_consumer_lag():
    """Get consumer lag for all topics"""
    cmd = f"docker exec kafka kafka-consumer-groups --bootstrap-server {KAFKA_BOOTSTRAP} --group {CONSUMER_GROUP} --describe"
    stdout, _, _ = run_cmd(cmd)
    
    total_lag = 0
    topic_lags = {}
    for line in stdout.split("\n"):
        if "retail." in line:
            parts = line.split()
            if len(parts) >= 9:
                topic = parts[1]
                lag = int(parts[8]) if parts[8].isdigit() else 0
                total_lag += lag
                topic_lags[topic] = lag
    return total_lag, topic_lags

def get_kafka_messages_per_sec():
    """Estimate messages/sec by checking log-end-offset delta"""
    total_msgs = 0
    for topic in TOPICS:
        cmd = f"docker exec kafka kafka-run-class kafka.tools.GetOffsetShell --bootstrap-server {KAFKA_BOOTSTRAP} --topic {topic} --time -1 --offsets 1"
        stdout, _, _ = run_cmd(cmd)
        for line in stdout.split("\n"):
            if ": Partition:" in line:
                parts = line.split(":")
                if len(parts) >= 4 and parts[3].strip().isdigit():
                    total_msgs += int(parts[3].strip())
    return total_msgs

def get_trino_row_counts():
    """Get row counts for all tables via Trino"""
    conn = trino_connect(host=TRINO_HOST, port=TRINO_PORT, catalog=CATALOG, schema=SCHEMA, user="admin")
    cursor = conn.cursor()
    
    counts = {}
    for table in TABLES:
        try:
            cursor.execute(f"SELECT count(*) FROM {table}")
            result = cursor.fetchone()
            counts[table] = result[0] if result else 0
        except Exception as e:
            counts[table] = f"Error: {e}"
    
    cursor.close()
    conn.close()
    return counts

def get_trino_query_latency():
    """Measure Trino query latency for a simple count"""
    conn = trino_connect(host=TRINO_HOST, port=TRINO_PORT, catalog=CATALOG, schema=SCHEMA, user="admin")
    cursor = conn.cursor()
    
    start = time.time()
    cursor.execute("SELECT count(*) FROM orders")
    cursor.fetchone()
    latency_ms = (time.time() - start) * 1000
    
    cursor.close()
    conn.close()
    return latency_ms

def print_header():
    """Print benchmark header"""
    print("=" * 80)
    print("END-TO-END BENCHMARK - Retail Streaming Platform")
    print("=" * 80)
    print(f"Start Time: {datetime.now()}")
    print(f"Kafka: {KAFKA_BOOTSTRAP}")
    print(f"Trino: {TRINO_HOST}:{TRINO_PORT}/{CATALOG}.{SCHEMA}")
    print(f"Duration: {BENCHMARK_DURATION_SEC}s per scenario")
    print("=" * 80)

def print_metrics(timestamp, kafka_lag, row_counts, trino_latency_ms):
    """Print current metrics"""
    print(f"\n[{timestamp}] METRICS:")
    print(f"  Kafka Consumer Lag: {kafka_lag:,} events")
    print(f"  Trino Query Latency: {trino_latency_ms:.1f} ms")
    print(f"  Row Counts:")
    total_rows = 0
    for table, count in row_counts.items():
        if isinstance(count, int):
            total_rows += count
            print(f"    {table}: {count:,}")
        else:
            print(f"    {table}: {count}")
    print(f"    TOTAL: {total_rows:,}")

def run_benchmark_scenario(scenario_name, duration_sec):
    """Run a single benchmark scenario"""
    print(f"\n{'='*80}")
    print(f"SCENARIO: {scenario_name}")
    print(f"Duration: {duration_sec}s")
    print(f"{'='*80}")
    
    start_time = time.time()
    initial_counts = get_trino_row_counts()
    initial_lag, _ = get_kafka_consumer_lag()
    
    print(f"\nInitial State:")
    print(f"  Initial Lag: {initial_lag:,}")
    print(f"  Initial Rows: {sum(v for v in initial_counts.values() if isinstance(v, int)):,}")
    
    # Collect samples
    samples = []
    sample_num = 0
    
    while time.time() - start_time < duration_sec:
        sample_num += 1
        elapsed = time.time() - start_time
        
        kafka_lag, topic_lags = get_kafka_consumer_lag()
        row_counts = get_trino_row_counts()
        trino_latency = get_trino_query_latency()
        
        # Calculate throughput (rows added since start)
        total_initial = sum(v for v in initial_counts.values() if isinstance(v, int))
        total_current = sum(v for v in row_counts.values() if isinstance(v, int))
        rows_added = total_current - total_initial
        events_per_sec = rows_added / elapsed if elapsed > 0 else 0
        events_per_min = events_per_sec * 60
        
        sample = {
            "elapsed_sec": elapsed,
            "sample": sample_num,
            "kafka_lag": kafka_lag,
            "topic_lags": topic_lags,
            "row_counts": row_counts,
            "total_rows": total_current,
            "rows_added": rows_added,
            "events_per_sec": events_per_sec,
            "events_per_min": events_per_min,
            "trino_latency_ms": trino_latency
        }
        samples.append(sample)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] Sample {sample_num} ({elapsed:.0f}s elapsed):")
        print(f"  Kafka Lag: {kafka_lag:,}")
        for topic, lag in topic_lags.items():
            print(f"    {topic}: {lag:,}")
        print(f"  Throughput: {events_per_sec:.1f} events/sec ({events_per_min:.0f} events/min)")
        print(f"  Rows Added: {rows_added:,}")
        print(f"  Trino Latency: {trino_latency:.1f} ms")
        
        if elapsed < duration_sec:
            time.sleep(POLL_INTERVAL_SEC)
    
    # Calculate summary stats
    total_lag_change = kafka_lag - initial_lag
    final_rows = sum(v for v in row_counts.values() if isinstance(v, int))
    total_processed = final_rows - total_initial
    avg_events_per_sec = total_processed / duration_sec if duration_sec > 0 else 0
    avg_events_per_min = avg_events_per_sec * 60
    
    print(f"\n{'='*80}")
    print(f"SCENARIO SUMMARY: {scenario_name}")
    print(f"{'='*80}")
    print(f"  Duration: {duration_sec}s")
    print(f"  Total Events Processed: {total_processed:,}")
    print(f"  Avg Throughput: {avg_events_per_sec:.1f} events/sec ({avg_events_per_min:.0f} events/min)")
    print(f"  Initial Lag: {initial_lag:,}")
    print(f"  Final Lag: {kafka_lag:,}")
    print(f"  Lag Change: {total_lag_change:+,d}")
    print(f"  Final Trino Latency: {trino_latency:.1f} ms")
    
    return {
        "scenario": scenario_name,
        "duration_sec": duration_sec,
        "total_processed": total_processed,
        "avg_events_per_sec": avg_events_per_sec,
        "avg_events_per_min": avg_events_per_min,
        "initial_lag": initial_lag,
        "final_lag": kafka_lag,
        "lag_change": total_lag_change,
        "final_trino_latency_ms": trino_latency,
        "samples": samples
    }

def main():
    print_header()
    
    # Get baseline state
    print("\nCollecting baseline metrics...")
    baseline_lag, baseline_topic_lags = get_kafka_consumer_lag()
    baseline_counts = get_trino_row_counts()
    
    print(f"Baseline Kafka Lag: {baseline_lag:,}")
    print(f"Baseline Row Counts: {sum(v for v in baseline_counts.values() if isinstance(v, int)):,}")
    
    # Run scenarios
    scenarios = [
        ("Baseline (Current Load)", 60),  # 1 minute baseline
        ("5x Load Test", 120),           # 2 minutes at 5x
        ("10x Load Test", 120),          # 2 minutes at 10x
        ("Stress Test", 180),            # 3 minutes max load
    ]
    
    results = []
    for scenario_name, duration in scenarios:
        result = run_benchmark_scenario(scenario_name, duration)
        results.append(result)
    
    # Print final comparison
    print("\n" + "=" * 80)
    print("BENCHMARK COMPLETE - FINAL COMPARISON")
    print("=" * 80)
    print(f"{'Scenario':<25} {'Events/Min':<15} {'Kafka Lag':<15} {'Trino Latency':<15}")
    print("-" * 80)
    for r in results:
        print(f"{r['scenario']:<25} {r['avg_events_per_min']:<15.0f} {r['final_lag']:<15,} {r['final_trino_latency_ms']:<15.1f} ms")
    
    # Find max sustainable throughput
    max_throughput = max(r['avg_events_per_min'] for r in results)
    sustainable = [r for r in results if r['lag_change'] < 1000]  # Lag growing < 1000 = sustainable
    if sustainable:
        max_sustainable = max(s['avg_events_per_min'] for s in sustainable)
        print(f"\nMax Throughput: {max_throughput:.0f} events/min")
        print(f"Max Sustainable: {max_sustainable:.0f} events/min (lag growing < 1000)")
    else:
        print(f"\nMax Throughput: {max_throughput:.0f} events/min")
        print("Warning: No sustainable scenario found - lag growing unbounded")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
