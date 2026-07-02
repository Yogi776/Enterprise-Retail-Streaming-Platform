#!/bin/bash
# Kafka Topic Creation Script
# Creates all 8 retail topics with 3 partitions each
# Run after Kafka is healthy

KAFKA_HOST=${KAFKA_HOST:-localhost}
KAFKA_PORT=${KAFKA_PORT:-9092}
BOOTSTRAP_SERVER="${KAFKA_HOST}:${KAFKA_PORT}"

TOPICS=(
    "retail.orders"
    "retail.payments"
    "retail.inventory"
    "retail.delivery"
    "retail.customer_behavior"
    "retail.recommendations"
    "retail.fraud_signals"
    "retail.customer_profile"
)

echo "Waiting for Kafka to be ready at ${BOOTSTRAP_SERVER}..."
until kafka-topics --bootstrap-server "${BOOTSTRAP_SERVER}" --list > /dev/null 2>&1; do
    echo "Kafka not ready yet, waiting 5s..."
    sleep 5
done
echo "Kafka is ready!"

for topic in "${TOPICS[@]}"; do
    echo "Creating topic: ${topic}"
    kafka-topics \
        --create \
        --bootstrap-server "${BOOTSTRAP_SERVER}" \
        --topic "${topic}" \
        --partitions 3 \
        --replication-factor 1 \
        --if-not-exists \
        && echo "  -> Created ${topic}" \
        || echo "  -> Failed to create ${topic}"
done

echo ""
echo "Listing all topics:"
kafka-topics --bootstrap-server "${BOOTSTRAP_SERVER}" --list

echo ""
echo "Verifying topic details:"
for topic in "${TOPICS[@]}"; do
    kafka-topics --bootstrap-server "${BOOTSTRAP_SERVER}" --topic "${topic}" --describe
done