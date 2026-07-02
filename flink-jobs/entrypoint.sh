#!/bin/bash
# Entrypoint for Flink job container
# Waits for dependencies then runs the Python Kafka->Iceberg consumer

set -e

echo "Waiting for services to be ready..."
python /opt/flink-jobs/wait_for_services.py

echo "Starting Kafka to Iceberg consumer..."
exec python3 -u /opt/flink-jobs/flink_job.py
