# Benchmark Results - Retail Streaming Platform

## Current Baseline Metrics

**Test Date:** July 2, 2026

### Pipeline Architecture
```
Kafka (6 topics) -> Spark Structured Streaming -> Iceberg REST Catalog -> MinIO S3 -> Trino
```

### Current State

| Metric | Value |
|--------|-------|
| **Kafka Consumer Lag** | 0 (all caught up) |
| **Producer Rate** | ~10 events/sec (~600 events/min) |
| **Data Generator** | Running at 1.0x time multiplier |
| **Spark Processing** | Real-time, micro-batch |
| **Trino Query Latency** | 2-5 seconds (full table scan) |

### Topic Offsets (Kafka)

| Topic | Current Offset | Consumer Lag |
|-------|--------------|--------------|
| retail.orders | 116,114 | 0 |
| retail.payments | 116,114 | 0 |
| retail.delivery | 116,114 | 0 |
| retail.fraud_signals | 48,037 | 0 |
| retail.inventory | 87,229 | 0 |
| retail.customer_profile | 11,492 | 0 |

### Iceberg Table Row Counts

| Table | Row Count |
|-------|-----------|
| orders | 116,316 |
| payments | 116,316 |
| delivery | 116,316 |
| fraud_signals | 48,037 |
| inventory | 87,229 |
| customer_profile | 11,492 |
| **TOTAL** | **~500,000** |

## Performance Characteristics

### Throughput
- **Current Load:** ~600 events/minute (10 events/sec)
- **Processing:** Real-time (lag = 0)
- **End-to-End Latency:** ~30-60 seconds (Kafka -> Spark -> Iceberg -> Queryable)

### Bottlenecks Identified
1. **Single Partition** - Kafka topics have only 1 partition, limiting parallelism
2. **Single Spark Executor** - Limited micro-batch parallelism
3. **Iceberg REST Catalog** - Adds ~1-2s latency per commit
4. **Trino Full Table Scan** - COUNT(*) requires scanning all data files

## Scaling Recommendations

### To Increase Throughput:
1. **Increase Kafka Partitions** - Add 6-12 partitions per topic
2. **Scale Spark** - Add more executors or increase parallelism
3. **Batch Iceberg Writes** - Increase micro-batch interval to 5-10 seconds
4. **Use Iceberg FileIO** - Direct S3 writes instead of REST catalog for commits

### Target Throughputs
| Configuration | Expected Throughput |
|--------------|-------------------|
| Current | ~600 events/min |
| 6 partitions, 3 spark executors | ~3,000 events/min |
| 12 partitions, 6 spark executors | ~10,000 events/min |
| Optimized batch commits | ~20,000+ events/min |

## Benchmark Scripts

### Run Quick Monitor
```bash
./scripts/kafka_monitor.sh 5 10  # 5 sec interval, 10 samples
```

### Run Full Benchmark
```bash
docker compose run --rm benchmark
```

### Manual Throughput Test
```bash
# Check consumer lag
docker exec kafka kafka-consumer-groups --bootstrap-server kafka:29092 \
  --group retail-stream-consumer --describe

# Count Iceberg rows via Trino
docker exec trino trino --server http://trino:8080 \
  --catalog iceberg --schema retail \
  --execute "SELECT count(*) FROM orders"
```
