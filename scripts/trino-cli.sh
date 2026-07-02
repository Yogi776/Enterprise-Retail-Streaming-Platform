#!/bin/bash
# Trino CLI wrapper for querying Iceberg tables
# Usage: ./trino-cli.sh "SELECT count(*) FROM orders"

docker run --rm -i --network retail-streaming-platform_retail-network \
  trinodb/trino:448 trino \
  --server http://trino:8080 \
  --catalog iceberg \
  --schema retail \
  --user admin \
  "$@"
