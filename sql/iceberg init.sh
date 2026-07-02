#!/bin/bash
# Init script for Iceberg REST catalog - creates PostgreSQL user and database

psql -v ON_ERROR_STOP=1 "$POSTGRES_DB" <<-EOSQL
    CREATE USER iceberg WITH PASSWORD 'iceberg123';
    CREATE DATABASE iceberg OWNER iceberg;
    GRANT ALL PRIVILEGES ON DATABASE iceberg TO iceberg;
EOSQL
