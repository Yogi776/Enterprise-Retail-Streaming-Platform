#!/usr/bin/env python3
"""Wait for Kafka and Iceberg REST to be ready."""
import socket
import urllib.request
import os
import sys
import time

def wait_kafka(host, port, retries=30, delay=2):
    for i in range(retries):
        try:
            s = socket.socket()
            s.settimeout(3)
            s.connect((host, int(port)))
            s.close()
            print(f"Kafka at {host}:{port} is ready!")
            return True
        except Exception as e:
            print(f"Kafka not ready, attempt {i+1}/{retries}: {e}")
            time.sleep(delay)
    return False

def wait_iceberg(url, retries=30, delay=2):
    for i in range(retries):
        try:
            r = urllib.request.urlopen(url, timeout=5)
            print(f"Iceberg REST at {url} is ready!")
            return True
        except Exception as e:
            print(f"Iceberg REST not ready, attempt {i+1}/{retries}: {e}")
            time.sleep(delay)
    return False

if __name__ == "__main__":
    kafka_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
    kafka_host, kafka_port = kafka_servers.split(":")
    iceberg_url = os.environ.get("ICEBERG_REST_URL", "http://iceberg-rest:8181") + "/v1/namespaces"

    if not wait_kafka(kafka_host, int(kafka_port)):
        print("ERROR: Kafka not available")
        sys.exit(1)

    if not wait_iceberg(iceberg_url):
        print("ERROR: Iceberg REST not available")
        sys.exit(1)

    print("All services ready. Starting main job...")
    sys.exit(0)
