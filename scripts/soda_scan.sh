#!/bin/bash
# Soda Core scan script for Retail Streaming Platform
# Scans Iceberg tables via Trino for data quality

set -e

SODA_DIR="/soda"
DS_CONFIG="${SODA_DIR}/ds_trino.yml"
CHECKS_FILE="${SODA_DIR}/retail_checks.yml"

echo "========================================"
echo "Soda Core Data Quality Scan"
echo "========================================"
echo ""

# Check if soda is available
if ! command -v soda &> /dev/null; then
    echo "Installing Soda Core..."
    pip install soda-trino -q
fi

# Run scan
echo "Running data quality checks..."
soda scan -ds "$DS_CONFIG" -c "$CHECKS_FILE" --verbose

exit $?
