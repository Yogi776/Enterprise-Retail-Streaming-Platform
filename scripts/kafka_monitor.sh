#!/bin/bash
# Kafka Monitor - Quick metrics checker for Retail Streaming Platform
# Usage: ./kafka_monitor.sh [interval] [count]

KAFKA_CONTAINER="kafka"
BOOTSTRAP_SERVER="kafka:29092"
CONSUMER_GROUP="retail-stream-consumer"
INTERVAL=${1:-5}  # Default 5 seconds
COUNT=${2:-10}     # Default 10 samples

TOPICS=("retail.orders" "retail.payments" "retail.inventory" "retail.delivery" "retail.fraud_signals" "retail.customer_profile")

echo "=============================================="
echo "Kafka Monitor - Retail Streaming Platform"
echo "=============================================="
echo "Bootstrap: $BOOTSTRAP_SERVER"
echo "Consumer Group: $CONSUMER_GROUP"
echo "Interval: ${INTERVAL}s | Samples: $COUNT"
echo "Press Ctrl+C to stop"
echo "=============================================="

print_header() {
    printf "%-12s %-15s %-15s %-15s %-15s\n" "TIME" "TOTAL_LAG" "ORDERS_LAG" "PAYMENTS_LAG" "THROUGHPUT/s"
    echo "-------------------------------------------------------------------------------------"
}

get_lag() {
    local topic=$1
    docker exec $KAFKA_CONTAINER kafka-consumer-groups \
        --bootstrap-server $BOOTSTRAP_SERVER \
        --group $CONSUMER_GROUP \
        --describe \
        --topic $topic 2>/dev/null | grep -E "^\s*$topic" | awk '{sum += $9} END {print sum}'
}

get_total_lag() {
    local total=0
    for topic in "${TOPICS[@]}"; do
        lag=$(get_lag $topic)
        total=$((total + lag))
    done
    echo $total
}

get_topic_lag() {
    local topic=$1
    local lag=$(get_lag $topic)
    echo ${lag:-0}
}

get_throughput() {
    # Messages per second via consumer lag delta
    local orders_lag=$(get_topic_lag "retail.orders")
    echo $orders_lag
}

prev_total=0
prev_time=$(date +%s)

print_header

for i in $(seq 1 $COUNT); do
    current_time=$(date +"%H:%M:%S")
    total_lag=$(get_total_lag)
    orders_lag=$(get_topic_lag "retail.orders")
    payments_lag=$(get_topic_lag "retail.payments")

    # Calculate throughput (events/sec based on lag change)
    now=$(date +%s)
    time_diff=$((now - prev_time))
    if [ $time_diff -gt 0 ]; then
        lag_diff=$((total_lag - prev_total))
        throughput=$((lag_diff / time_diff))
    else
        throughput=0
    fi

    printf "%-12s %-15s %-15s %-15s %-15s\n" \
        "$current_time" \
        "$total_lag" \
        "$orders_lag" \
        "$payments_lag" \
        "$throughput"

    prev_total=$total_lag
    prev_time=$now

    if [ $i -lt $COUNT ]; then
        sleep $INTERVAL
    fi
done

echo ""
echo "=============================================="
echo "Monitor complete"
echo "=============================================="
