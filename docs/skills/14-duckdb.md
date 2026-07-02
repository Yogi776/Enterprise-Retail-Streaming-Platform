# DuckDB Skill Document

## Enterprise Retail Streaming Platform - Analytics Layer

---

## Table of Contents

1. [Overview](#1-overview)
2. [Core Concepts](#2-core-concepts)
3. [Why This Project Uses It](#3-why-this-project-uses-it)
4. [Architecture Position](#4-architecture-position)
5. [Folder Structure](#5-folder-structure)
6. [Implementation Walkthrough](#6-implementation-walkthrough)
7. [Production Best Practices](#7-production-best-practices)
8. [Common Problems](#8-common-problems)
9. [Performance Optimization](#9-performance-optimization)
10. [Security](#10-security)
11. [Monitoring](#11-monitoring)
12. [Testing Strategy](#12-testing-strategy)
13. [Interview Preparation](#13-interview-preparation)
14. [Hands-on Exercises](#14-hands-on-exercises)
15. [Real Enterprise Use Cases](#15-real enterprise-use-cases)
16. [Design Decisions](#16-design-decisions)
17. [Business Value](#17-business-value)
18. [Future Improvements](#18-future-improvements)
19. [References](#19-references)
20. [Skills Demonstrated](#20-skills-demonstrated)

---

## 1. Overview

### What is DuckDB?

DuckDB is an **in-process, embeddable analytical database management system** (DBMS) designed specifically for Online Analytical Processing (OLAP). Unlike traditional databases that run as separate server processes, DuckDB runs entirely within the same process as the application, eliminating network latency and deployment complexity.

```python
import duckdb

# Simple example - no server needed
con = duckdb.connect("retail_analytics.db")
result = con.sql("""
    SELECT 
        product_category,
        SUM(revenue) as total_revenue,
        COUNT(*) as transaction_count
    FROM sales_data
    WHERE transaction_date >= '2024-01-01'
    GROUP BY product_category
    ORDER BY total_revenue DESC
""").df()
```

### Why Was DuckDB Created?

DuckDB was created by researchers at the University of California, Santa Barbara, and later developed by DuckDB Labs to address a fundamental gap in the data ecosystem:

| Problem | Traditional Solution | DuckDB Solution |
|---------|---------------------|------------------|
| Fast analytical queries on local data | Move data to data warehouse | Query data where it lives |
| Simple deployment | Complex DB cluster setup | Single library, embedded |
| Python integration | Multiple libraries (pandas + SQLAlchemy + DB) | Native pandas integration |
| Large data files | Load into database | Query directly (Parquet, CSV, JSON) |

### Business Problems DuckDB Solves

1. **Accelerating ETL Pipelines**: Pre-aggregate, filter, and join data before loading into centralized systems
2. **Embedded Analytics**: Ship analytics capabilities directly within applications
3. **Data Exploration**: Interactive analysis of large datasets without infrastructure overhead
4. **Edge Computing**: Analytics at the source of data generation (IoT, retail terminals)
5. **Reporting Acceleration**: Pre-compute expensive aggregations for dashboards

### Why Enterprises Use DuckDB

```mermaid
pie title Enterprise DuckDB Adoption Drivers
    "Zero Infrastructure Overhead" : 30
    "Native Python Integration" : 25
    "Direct File Querying" : 20
    "Columnar Vectorized Execution" : 15
    "Cost Efficiency" : 10
```

- **PostgreSQL Ecosystem Compatibility**: DuckDB's SQL dialect closely follows PostgreSQL, making it familiar to data engineers
- **Arrow Native**: Seamless integration with Apache Arrow for zero-copy data exchange
- **No Admin Overhead**: Embed in applications without requiring DBA expertise
- **ACID Transactions**: Full transaction support despite being embeddable
- **Open Source**: Apache 2.0 licensed, vibrant community

---

## 2. Core Concepts

### 2.1 OLAP (Online Analytical Processing)

OLAP is optimized for complex queries that aggregate and analyze large volumes of data. Unlike OLTP (Online Transaction Processing), which handles simple insert/update/delete operations, OLAP workloads involve:

- Multi-dimensional aggregations
- Historical trend analysis
- Complex joins across large tables
- Ad-hoc reporting queries

```sql
-- OLAP query example: Revenue analysis across multiple dimensions
SELECT 
    store_id,
    product_category,
    DATE_TRUNC('quarter', transaction_date) as quarter,
    SUM(revenue) as total_revenue,
    AVG(quantity) as avg_quantity,
    COUNT(DISTINCT customer_id) as unique_customers
FROM fact_sales
JOIN dim_products USING (product_id)
JOIN dim_stores USING (store_id)
WHERE transaction_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY store_id, product_category, DATE_TRUNC('quarter', transaction_date)
HAVING SUM(revenue) > 100000
ORDER BY quarter, total_revenue DESC;
```

### 2.2 Columnar Storage

DuckDB uses **columnar storage** internally, which stores data by column rather than by row:

```mermaid
graph LR
    subgraph "Row-Oriented Storage"
        R1["Row 1: id=1, name=Apple, revenue=100"]
        R2["Row 2: id=2, name=Banana, revenue=200"]
        R3["Row 3: id=3, name=Orange, revenue=150"]
    end
    
    subgraph "Column-Oriented Storage"
        C1["Column id: [1, 2, 3]"]
        C2["Column name: [Apple, Banana, Orange]"]
        C3["Column revenue: [100, 200, 150]"]
    end
```

**Benefits of Columnar Storage:**

| Feature | Row Store | Column Store |
|---------|-----------|--------------|
| Read for aggregation | Scans entire rows | Reads only needed columns |
| Compression | Poor (mixed types) | Excellent (similar values) |
| Vectorized ops | Row-by-row | Batch processing |
| Analytic perf | Slow | 10-100x faster |

### 2.3 Vectorized Execution

DuckDB uses **vectorized execution** (also called vectorized query processing), where queries operate on batches of rows (vectors) at a time rather than processing row-by-row:

```mermaid
flowchart TD
    subgraph "Traditional Row-by-Row"
        A1["Process Row 1"]
        A2["Process Row 2"]
        A3["Process Row 3"]
        A4["..."]
        A1 --> A2 --> A3 --> A4
    end
    
    subgraph "Vectorized Batch Processing"
        B1["Process Vector 1: 2048 rows"]
        B2["Process Vector 2: 2048 rows"]
        B3["Process Vector 3: 2048 rows"]
        B4["..."]
        B1 --> B2 --> B3 --> B4
    end
    
    style B1 fill:#90EE90
    style B2 fill:#90EE90
    style B3 fill:#90EE90
```

**Vector Size**: DuckDB uses a vector size of 2048 rows by default (configurable). This size:
- Fits in CPU L1/L2 cache for maximum efficiency
- Enables SIMD operations for parallel processing
- Reduces function call overhead dramatically

### 2.4 Transactions and ACID Compliance

DuckDB provides full ACID transaction support:

- **Atomicity**: Transactions complete entirely or not at all
- **Consistency**: Database moves from one valid state to another
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed data survives system crashes

```python
import duckdb

con = duckdb.connect("retail.db")

# Transaction example
con.begin()
try:
    con.execute("INSERT INTO inventory VALUES (1, 'SKU001', 100)")
    con.execute("INSERT INTO inventory VALUES (2, 'SKU002', 50)")
    con.commit()
except Exception as e:
    con.rollback()
    print(f"Transaction failed: {e}")
```

### 2.5 Extension System

DuckDB has a rich extension ecosystem that extends its capabilities:

```mermaid
flowchart TD
    Core["DuckDB Core"] --> Spatial["Spatial Extension"]
    Core --> Parquet["Parquet Extension"]
    Core --> Arrow["Arrow Extension"]
    Core --> Iceberg["Iceberg Extension"]
    Core --> S3["S3/HTTPFS Extension"]
    Core --> Postgres["PostgreSQL Extension"]
    Core --> Ml["ML Extension"]
    
    Spatial --> Geo["Geospatial Analytics"]
    Parquet --> FileIO["File I/O"]
    Arrow --> ZeroCopy["Zero-Copy Integration"]
    Iceberg --> TableFormat["Iceberg Tables"]
    S3 --> Cloud["Cloud Storage"]
    Postgres --> Federated["Federated Queries"]
    Ml --> MachineLearning["In-DB ML"]
```

**Key Extensions:**

```sql
-- Load extensions
INSTALL httpfs;
LOAD httpfs;

INSTALL iceberg;
LOAD iceberg;

INSTALL spatial;
LOAD spatial;

-- Use S3 directly
SELECT * FROM read_parquet('s3://bucket/data/*.parquet');

-- Use Iceberg
SELECT * FROM iceberg('s3://bucket/iceberg/table');
```

### 2.6 Memory Management

DuckDB uses **automatic memory management** with configurable limits:

```python
import duckdb

# Configure memory limit (default: 8GB)
con = duckdb.connect("retail.db", config={
    'max_memory': '4GB',
    'threads': 4
})

# Query memory usage
result = con.sql("SELECT * FROM duckdb_memory()").df()
```

### 2.7 Query Optimization

DuckDB's query optimizer includes:

- **Predicate Pushdown**: Push filters closer to data sources
- **Column Pruning**: Only read columns needed
- **Constant Folding**: Pre-compute constant expressions
- **Join Reordering**: Optimize join order based on statistics
- **Parallel Execution**: Multi-threaded query processing

```sql
-- View query plan
EXPLAIN ANALYZE
SELECT p.category, SUM(s.revenue)
FROM sales s
JOIN products p ON s.product_id = p.id
WHERE s.date >= '2024-01-01'
GROUP BY p.category;
```

---

## 3. Why This Project Uses It

### 3.1 Platform Context: Enterprise Retail Streaming

The **Enterprise Retail Streaming Platform** processes millions of retail transactions daily from multiple sources:

```mermaid
flowchart LR
    subgraph "Data Sources"
        POS["POS Terminals"]
        Online["Online Store"]
        Inv["Inventory System"]
        Cust["Customer CRM"]
    end
    
    subgraph "Streaming Layer"
        Kafka["Apache Kafka"]
    end
    
    subgraph "Processing Layer"
        Flink["Apache Flink"]
    end
    
    subgraph "Analytics Layer"
        DuckDB["DuckDB"]
    end
    
    POS --> Kafka
    Online --> Kafka
    Inv --> Kafka
    Cust --> Kafka
    
    Kafka --> Flink
    Flink --> DuckDB
```

### 3.2 Specific DuckDB Use Cases in This Platform

#### Use Case 1: Real-Time Aggregation Cache

**Problem**: Dashboards need sub-second response times for pre-computed aggregations.

**Solution**: DuckDB maintains materialized views for common queries.

```python
# analytics/aggregation_cache.py
import duckdb
import pandas as pd
from datetime import datetime, timedelta

class AggregationCache:
    def __init__(self, db_path: str = "data/aggregation_cache.db"):
        self.con = duckdb.connect(db_path)
        self._init_tables()
    
    def _init_tables(self):
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS hourly_sales (
                hour TIMESTAMP,
                store_id VARCHAR,
                category VARCHAR,
                revenue DECIMAL(10,2),
                units_sold BIGINT,
                transaction_count BIGINT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def refresh_hourly_sales(self, start_hour: datetime):
        """Refresh hourly sales for the last 24 hours."""
        self.con.execute(f"""
            INSERT INTO hourly_sales
            SELECT 
                DATE_TRUNC('hour', transaction_time) as hour,
                store_id,
                category,
                SUM(revenue) as revenue,
                SUM(quantity) as units_sold,
                COUNT(*) as transaction_count,
                CURRENT_TIMESTAMP as updated_at
            FROM live_transactions
            WHERE transaction_time >= '{start_hour}'
            GROUP BY 1, 2, 3
        """)
    
    def get_dashboard_data(self, store_id: str) -> pd.DataFrame:
        """Get pre-computed data for dashboard."""
        return self.con.sql("""
            SELECT * FROM hourly_sales 
            WHERE store_id = ?
            ORDER BY hour DESC
            LIMIT 168
        """, params=[store_id]).df()
```

#### Use Case 2: ETL Acceleration Layer

**Problem**: Loading raw Kafka data directly into the data warehouse is slow and expensive.

**Solution**: Pre-process, filter, and aggregate data in DuckDB before warehouse ingestion.

```python
# etl/duckdb_preprocessor.py
import duckdb
from pathlib import Path

class RetailDataPreprocessor:
    def __init__(self, config: dict):
        self.config = config
        self.con = duckdb.connect(config['processed_db'])
    
    def process_daily_sales(self, date: str):
        """Process and aggregate daily sales data."""
        
        # Step 1: Filter and clean raw data
        self.con.execute(f"""
            CREATE TABLE cleaned_sales_{date} AS
            SELECT 
                transaction_id,
                store_id,
                customer_id,
                product_id,
                quantity,
                unit_price,
                revenue,
                transaction_time,
                -- Data quality fixes
                COALESCE(RETURN 'store_id', 'UNKNOWN') as store_id,
                CASE 
                    WHEN quantity < 0 THEN NULL 
                    ELSE quantity 
                END as quantity
            FROM read_parquet('{self.config['raw_path']}/sales_{date}.parquet')
            WHERE revenue > 0 
              AND transaction_time IS NOT NULL
        """)
        
        # Step 2: Create aggregations
        self.con.execute(f"""
            CREATE TABLE aggregated_sales_{date} AS
            SELECT 
                store_id,
                product_id,
                DATE_TRUNC('hour', transaction_time) as hour,
                SUM(quantity) as total_quantity,
                SUM(revenue) as total_revenue,
                COUNT(*) as transaction_count,
                AVG(revenue / NULLIF(quantity, 0)) as avg_unit_price
            FROM cleaned_sales_{date}
            GROUP BY 1, 2, 3
        """)
        
        # Step 3: Export to data warehouse format
        self.con.execute(f"""
            COPY (SELECT * FROM aggregated_sales_{date}) 
            TO '{self.config['warehouse_path']}/agg_sales_{date}.parquet'
            (FORMAT PARQUET, COMPRESSION 'zstd')
        """)
        
        print(f"Processed {date}: {self.con.execute(f'SELECT COUNT(*) FROM aggregated_sales_{date}').fetchone()[0]} rows")
```

#### Use Case 3: Local Ad-Hoc Analysis

**Problem**: Data scientists need to explore data without loading it into a full database.

**Solution**: Direct query of Parquet/CSV files with DuckDB.

```python
# analytics/local_explorer.py
import duckdb
import pandas as pd

class LocalDataExplorer:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.con = duckdb.connect()
    
    def explore_directory(self) -> list[str]:
        """List all data files in the directory."""
        return self.con.execute(f"""
            SELECT * FROM glob('{self.data_path}/*.parquet')
        """).fetchall()
    
    def sample_data(self, table: str, n: int = 100) -> pd.DataFrame:
        """Get a random sample of data."""
        return self.con.sql(f"""
            SELECT * FROM '{table}'
            USING SAMPLE 100 ROWS
        """).df()
    
    def get_schema(self, table: str) -> pd.DataFrame:
        """Get schema information for a table."""
        return self.con.sql(f"""
            DESCRIBE SELECT * FROM '{table}' LIMIT 0
        """).df()
    
    def run_analysis(self, query: str) -> pd.DataFrame:
        """Execute ad-hoc analysis query."""
        return self.con.sql(query).df()
```

### 3.3 Why DuckDB Over Alternatives

| Requirement | DuckDB | SQLite | PostgreSQL | ClickHouse |
|------------|--------|--------|------------|------------|
| Embeddable | Yes | Yes | No | No |
| Analytical queries | Excellent | Poor | Good | Excellent |
| Python integration | Native | Good | Good | Good |
| Direct file query | Yes | Limited | No | No |
| Memory footprint | ~10MB | ~1MB | ~50MB+ | ~100MB+ |
| Setup complexity | None | None | High | Medium |
| OLAP optimizations | Built-in | None | Partial | Full |

---

## 4. Architecture Position

### 4.1 DuckDB in the Platform Architecture

```mermaid
flowchart TB
    subgraph "Data Ingestion Layer"
        POS["POS Terminals"]
        ECOM["E-Commerce"]
        INV["Inventory System"]
        CRM["Customer Data"]
    end
    
    subgraph "Streaming & Messaging"
        KAFKA["Apache Kafka"]
        ZK["Zookeeper"]
    end
    
    subgraph "Stream Processing"
        FLINK["Apache Flink"]
        SP["Stream Processor"]
    end
    
    subgraph "DuckDB Analytics Layer"
        subgraph "DuckDB Instances"
            ADC["Aggregation Cache\n(Read replicas for dashboards)"]
            ETL["ETL Preprocessor\n(Write path for aggregations)"]
            EXP["Data Explorer\n(Ad-hoc analysis)"]
        end
        
        subgraph "Storage"
            ADHOC["ad-hoc queries.db"]
            AGG["aggregations.db"]
            MODEL["models.db"]
        end
    end
    
    subgraph "Persistent Storage"
        DW["Data Warehouse\n(Snowflake/BigQuery)"]
        S3["S3/Cloud Storage"]
        Iceberg["Iceberg Tables"]
    end
    
    subgraph "Consumption Layer"
        DASH["Dashboards\n(Grafana/Tableau)"]
        API["Analytics API"]
        DS["Data Science"]
    end
    
    POS & ECOM & INV & CRM --> KAFKA
    KAFKA --> FLINK
    FLINK --> ADC & ETL
    ETL --> DW & S3 & Iceberg
    ADC & EXP --> DASH & API & DS
    
    style DuckDB fill:#f96,stroke:#333,stroke-width:2px
    style ADC fill:#9f9
    style ETL fill:#9f9
    style EXP fill:#9f9
```

### 4.2 Data Flow Diagram

```mermaid
sequenceDiagram
    participant POS as POS Terminal
    participant KAFKA as Kafka
    participant FLINK as Flink
    participant ETL as DuckDB ETL
    participant AGG as DuckDB Aggregations
    participant DW as Data Warehouse
    participant DASH as Dashboard
    
    POS->>KAFKA: Transaction events
    KAFKA->>FLINK: Stream of transactions
    FLINK->>ETL: Raw events (per minute batch)
    ETL->>ETL: Pre-aggregate, filter, join
    ETL->>DW: Processed parquet files
    ETL->>AGG: Update hourly/daily rollups
    AGG->>DASH: Pre-computed metrics
    DW->>AGG: Historical backfill
```

### 4.3 Component Interactions

```mermaid
flowchart LR
    subgraph "Application Layer"
        API["FastAPI Service"]
        WORKER["Background Workers"]
    end
    
    subgraph "DuckDB Layer"
        CONN["Connection Pool"]
        QUERY["Query Engine"]
        OPT["Optimizer"]
        VEC["Vectorized Exec"]
    end
    
    subgraph "Storage Layer"
        PARQUET["Parquet Files"]
        CSV["CSV Files"]
        JSON["JSON Lines"]
        S3["S3 Remote"]
    end
    
    API & WORKER --> CONN
    CONN --> QUERY
    QUERY --> OPT
    OPT --> VEC
    VEC --> PARQUET & CSV & JSON & S3
```

---

## 5. Folder Structure

### 5.1 DuckDB-Related Folders in the Platform

```
enterprise-retail-streaming-platform/
├── src/
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── aggregation_cache.py      # Pre-computed aggregations
│   │   ├── query_executor.py          # Query execution utilities
│   │   ├── schema_manager.py          # Table schema management
│   │   └── data_explorer.py           # Ad-hoc data exploration
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── duckdb_preprocessor.py    # ETL acceleration layer
│   │   ├── file_exporter.py           # Export to Parquet/CSV
│   │   └── incremental_loader.py      # Incremental data loading
│   ├── ml/
│   │   ├── __init__.py
│   │   └── feature_store.py           # ML feature engineering
│   └── config/
│       ├── __init__.py
│       └── duckdb_config.py           # DuckDB configuration
├── data/
│   ├── duckdb/
│   │   ├── retail_analytics.db        # Main analytics database
│   │   ├── aggregations.db            # Pre-computed aggregations
│   │   ├── temp/                      # Temporary DuckDB storage
│   │   │   ├── cache/                 # Query cache
│   │   │   └── spill/                 # Disk spill for large queries
│   │   └── backups/                   # Database backups
│   ├── raw/                           # Raw data files
│   │   ├── sales_2024.parquet
│   │   └── customers_2024.csv
│   └── processed/                     # Processed data
│       └── aggregations/
│           ├── hourly/
│           └── daily/
├── scripts/
│   ├── duckdb/
│   │   ├── init_schema.sql            # Initialize database schema
│   │   ├── migrations/                # Schema migrations
│   │   │   ├── 001_add_geolocation.sql
│   │   │   └── 002_add_customer_segment.sql
│   │   ├── maintenance/
│   │   │   ├── vacuum.sql             # VACUUM and ANALYZE
│   │   │   └── backup.py              # Automated backup script
│   │   └── setup_dev.sh               # Development setup
├── tests/
│   ├── unit/
│   │   ├── test_aggregation_cache.py
│   │   ├── test_query_executor.py
│   │   └── test_preprocessor.py
│   ├── integration/
│   │   ├── test_duckdb_etl.py
│   │   └── test_data_pipeline.py
│   └── fixtures/
│       ├── sample_sales.parquet
│       └── sample_customers.csv
├── docs/
│   └── skills/
│       └── 14-duckdb.md              # This document
└── config/
    ├── duckdb.yml                     # DuckDB configuration
    └── settings.yml                   # Application settings
```

### 5.2 Database Schema

```sql
-- data/duckdb/schema.sql

-- Fact table: Individual transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id VARCHAR PRIMARY KEY,
    transaction_time TIMESTAMP NOT NULL,
    store_id VARCHAR NOT NULL,
    customer_id VARCHAR,
    product_id VARCHAR NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    revenue DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0,
    payment_method VARCHAR,
    INDEX idx_transaction_time (transaction_time),
    INDEX idx_store_id (store_id),
    INDEX idx_product_id (product_id)
);

-- Dimension table: Product information
CREATE TABLE IF NOT EXISTS dim_products (
    product_id VARCHAR PRIMARY KEY,
    product_name VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    subcategory VARCHAR,
    brand VARCHAR,
    cost DECIMAL(10,2),
    INDEX idx_category (category)
);

-- Dimension table: Store information
CREATE TABLE IF NOT EXISTS dim_stores (
    store_id VARCHAR PRIMARY KEY,
    store_name VARCHAR NOT NULL,
    region VARCHAR NOT NULL,
    city VARCHAR,
    state VARCHAR,
    country VARCHAR,
    store_type VARCHAR,
    INDEX idx_region (region)
);

-- Pre-aggregated: Hourly sales summary
CREATE TABLE IF NOT EXISTS agg_hourly_sales (
    hour TIMESTAMP NOT NULL,
    store_id VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    revenue DECIMAL(12,2) NOT NULL,
    units_sold BIGINT NOT NULL,
    transaction_count BIGINT NOT NULL,
    unique_customers BIGINT,
    avg_transaction_value DECIMAL(10,2),
    PRIMARY KEY (hour, store_id, category)
);

-- Pre-aggregated: Daily sales summary
CREATE TABLE IF NOT EXISTS agg_daily_sales (
    date DATE NOT NULL,
    store_id VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    revenue DECIMAL(12,2) NOT NULL,
    units_sold BIGINT NOT NULL,
    transaction_count BIGINT NOT NULL,
    PRIMARY KEY (date, store_id, category)
);

-- Real-time view: Last 24 hours of sales
CREATE VIEW live_sales AS
SELECT * FROM fact_transactions
WHERE transaction_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours';
```

---

## 6. Implementation Walkthrough

### 6.1 Configuration

```python
# config/duckdb_config.py
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class DuckDBConfig:
    """DuckDB configuration for the retail streaming platform."""
    
    # Database paths
    database_path: str = "data/duckdb/retail_analytics.db"
    temp_directory: str = "data/duckdb/temp"
    backup_directory: str = "data/duckdb/backups"
    
    # Memory settings
    max_memory: str = "4GB"
    threads: int = 4
    
    # Optimization settings
    batch_size: int = 2048
    enable_progress_bar: bool = True
    
    # Extension settings
    load_httpfs: bool = True
    load_parquet: bool = True
    load_iceberg: bool = True
    
    # Export settings
    parquet_compression: str = "zstd"
    csv_delimiter: str = ","
    
    @classmethod
    def from_env(cls) -> "DuckDBConfig":
        """Create configuration from environment variables."""
        return cls(
            database_path=os.getenv("DUCKDB_PATH", cls.database_path),
            max_memory=os.getenv("DUCKDB_MAX_MEMORY", cls.max_memory),
            threads=int(os.getenv("DUCKDB_THREADS", cls.threads)),
        )
    
    def to_connection_params(self) -> dict:
        """Convert to DuckDB connection parameters."""
        return {
            "database": self.database_path,
            "read_only": False,
            "config": {
                "max_memory": self.max_memory,
                "threads": self.threads,
                "enable_progress_bar": self.enable_progress_bar,
            }
        }
```

### 6.2 Python Integration

```python
# src/analytics/query_executor.py
import duckdb
import pandas as pd
from pathlib import Path
from typing import Optional, Union
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class QueryExecutor:
    """Manages DuckDB connections and query execution."""
    
    def __init__(self, config: DuckDBConfig):
        self.config = config
        self._connection: Optional[duckdb.DuckDBPyConnection] = None
        self._init_directories()
    
    def _init_directories(self):
        """Initialize required directories."""
        Path(self.config.temp_directory).mkdir(parents=True, exist_ok=True)
        Path(self.config.backup_directory).mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def connect(self):
        """Context manager for database connections."""
        conn = duckdb.connect(
            self.config.database_path,
            config={
                "max_memory": self.config.max_memory,
                "threads": self.config.threads,
                "temp_directory": self.config.temp_directory,
            }
        )
        
        # Load extensions
        if self.config.load_parquet:
            conn.execute("LOAD parquet")
        if self.config.load_httpfs:
            conn.execute("LOAD httpfs")
        
        try:
            yield conn
        finally:
            conn.close()
    
    def execute(self, query: str, params: Optional[tuple] = None) -> list:
        """Execute a query and return results as list of tuples."""
        with self.connect() as conn:
            if params:
                result = conn.execute(query, params).fetchall()
            else:
                result = conn.execute(query).fetchall()
            logger.info(f"Executed query: {query[:100]}...")
            return result
    
    def execute_df(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """Execute a query and return results as DataFrame."""
        with self.connect() as conn:
            if params:
                result = conn.execute(query, params).df()
            else:
                result = conn.sql(query).df()
            logger.info(f"Query returned {len(result)} rows")
            return result
    
    def execute_arrow(self, query: str) -> "pyarrow.Table":
        """Execute a query and return results as PyArrow table."""
        with self.connect() as conn:
            return conn.execute(query).arrow()
    
    def load_parquet(self, path: str, table_name: Optional[str] = None) -> pd.DataFrame:
        """Load a Parquet file into a DataFrame."""
        with self.connect() as conn:
            if table_name:
                conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM '{path}'")
                return conn.execute(f"SELECT * FROM {table_name}").df()
            else:
                return conn.sql(f"SELECT * FROM '{path}'").df()
    
    def export_to_parquet(self, query: str, output_path: str):
        """Export query results to Parquet file."""
        with self.connect() as conn:
            conn.execute(f"""
                COPY ({query}) 
                TO '{output_path}' 
                (FORMAT PARQUET, COMPRESSION '{self.config.parquet_compression}')
            """)
            logger.info(f"Exported to {output_path}")
```

### 6.3 Example Queries

#### Query 1: Daily Sales Summary by Store

```python
# Daily sales summary query
daily_summary_query = """
WITH daily_metrics AS (
    SELECT 
        DATE_TRUNC('day', transaction_time) as date,
        store_id,
        category,
        SUM(revenue) as total_revenue,
        SUM(quantity) as total_units,
        COUNT(*) as transaction_count,
        AVG(revenue) as avg_transaction_value
    FROM fact_transactions
    WHERE transaction_time >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY 1, 2, 3
),
ranked_stores AS (
    SELECT 
        *,
        RANK() OVER (PARTITION BY date, category ORDER BY total_revenue DESC) as store_rank
    FROM daily_metrics
)
SELECT 
    date,
    store_id,
    category,
    total_revenue,
    total_units,
    transaction_count,
    avg_transaction_value,
    store_rank
FROM ranked_stores
WHERE store_rank <= 10
ORDER BY date DESC, category, store_rank;
"""

df = executor.execute_df(daily_summary_query)
print(df.head(10))
```

**Output:**
```
         date store_id    category total_revenue total_units  transaction_count  avg_transaction_value  store_rank
0 2024-01-15    ST001  Electronics    125450.00        1523           2156               58.19               1
1 2024-01-15    ST002  Electronics     98432.00        1189           1847               53.29               2
2 2024-01-15    ST003     Clothing     87532.00        2341           2890               30.29               3
```

#### Query 2: Customer Segmentation Analysis

```python
# Customer segmentation based on purchase behavior
customer_segmentation_query = """
WITH customer_stats AS (
    SELECT 
        customer_id,
        COUNT(*) as total_transactions,
        SUM(revenue) as lifetime_value,
        COUNT(DISTINCT store_id) as stores_visited,
        DATE_TRUNC('month', MAX(transaction_time)) as last_purchase_month,
        AVG(revenue) as avg_transaction_value
    FROM fact_transactions
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
segments AS (
    SELECT 
        *,
        CASE 
            WHEN lifetime_value > 10000 THEN 'Platinum'
            WHEN lifetime_value > 5000 THEN 'Gold'
            WHEN lifetime_value > 1000 THEN 'Silver'
            WHEN lifetime_value > 0 THEN 'Bronze'
            ELSE 'Inactive'
        END as segment
    FROM customer_stats
)
SELECT 
    segment,
    COUNT(*) as customer_count,
    SUM(lifetime_value) as total_value,
    AVG(avg_transaction_value) as avg_basket_size,
    AVG(stores_visited) as avg_stores
FROM segments
GROUP BY segment
ORDER BY SUM(lifetime_value) DESC;
"""

segments_df = executor.execute_df(customer_segmentation_query)
```

#### Query 3: Time-Series Forecasting Features

```python
# Generate features for ML models
ml_features_query = """
WITH daily_sales AS (
    SELECT 
        store_id,
        product_id,
        DATE_TRUNC('day', transaction_time) as date,
        SUM(revenue) as daily_revenue,
        SUM(quantity) as daily_units
    FROM fact_transactions
    GROUP BY 1, 2, 3
),
lag_features AS (
    SELECT 
        store_id,
        product_id,
        date,
        daily_revenue,
        daily_units,
        LAG(daily_revenue, 1) OVER w as revenue_lag_1,
        LAG(daily_revenue, 7) OVER w as revenue_lag_7,
        LAG(daily_units, 1) OVER w as units_lag_1,
        AVG(daily_revenue) OVER w as rolling_7d_avg,
        SUM(daily_revenue) OVER w as rolling_7d_sum
    FROM daily_sales
    WINDOW w AS (
        PARTITION BY store_id, product_id 
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    )
)
SELECT 
    *,
    revenue_lag_1 / NULLIF(rolling_7d_avg, 0) - 1 as momentum_1d,
    revenue_lag_7 / NULLIF(rolling_7d_avg, 0) - 1 as momentum_7d
FROM lag_features
WHERE date >= CURRENT_DATE - INTERVAL '7 days';
"""

features_df = executor.execute_df(ml_features_query)
```

### 6.4 Transaction Management

```python
# src/analytics/transaction_manager.py
import duckdb
from contextlib import contextmanager
from typing import Optional
import lockfile

class TransactionManager:
    """Handles transactional operations with proper locking."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._lock = lockfile.LockFile(db_path)
    
    @contextmanager
    def transaction(self, exclusive: bool = False):
        """Context manager for transactions with automatic commit/rollback."""
        conn = duckdb.connect(self.db_path)
        
        try:
            if exclusive:
                conn.execute("BEGIN EXCLUSIVE TRANSACTION")
            else:
                conn.execute("BEGIN TRANSACTION")
            
            yield conn
            
            conn.execute("COMMIT")
        except Exception as e:
            conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()
    
    def atomic_update(self, updates: list[str]):
        """Execute multiple updates atomically."""
        with self.transaction(exclusive=True) as conn:
            for update_sql in updates:
                conn.execute(update_sql)
    
    def bulk_insert(self, table: str, df, batch_size: int = 10000):
        """Insert DataFrame in batches within a transaction."""
        with self.transaction() as conn:
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i + batch_size]
                conn.execute(f"INSERT INTO {table} BY NAME SELECT * FROM batch")
```

### 6.5 Loading Data from Various Sources

```python
# src/etl/data_loader.py
import duckdb
import pandas as pd
from pathlib import Path
from typing import Union

class DataLoader:
    """Load data from various sources into DuckDB."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def load_from_parquet(self, table_name: str, file_path: str, mode: str = "append"):
        """Load data from Parquet file."""
        conn = duckdb.connect(self.db_path)
        
        if mode == "replace":
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM '{file_path}'")
        else:
            conn.execute(f"INSERT INTO {table_name} SELECT * FROM '{file_path}'")
        
        conn.close()
    
    def load_from_csv(self, table_name: str, file_path: str, 
                      delimiter: str = ",", header: bool = True):
        """Load data from CSV file with automatic type inference."""
        conn = duckdb.connect(self.db_path)
        
        options = f"(DELIMITER '{delimiter}', HEADER {header}, AUTO_DETECT TRUE)"
        
        conn.execute(f"""
            COPY {table_name} 
            FROM '{file_path}'
            {options}
        """)
        
        conn.close()
    
    def load_from_s3(self, table_name: str, s3_path: str, secret: str = None):
        """Load data directly from S3."""
        conn = duckdb.connect(self.db_path)
        
        # Set up S3 secret if provided
        if secret:
            conn.execute(f"""
                SET s3_access_key_id = '{secret.split(':')[0]}';
                SET s3_secret_access_key = '{secret.split(':')[1]}';
            """)
        
        conn.execute(f"""
            CREATE TABLE {table_name} AS 
            SELECT * FROM read_parquet('{s3_path}');
        """)
        
        conn.close()
    
    def load_from_dataframe(self, table_name: str, df: pd.DataFrame, mode: str = "append"):
        """Load data from pandas DataFrame."""
        conn = duckdb.connect(self.db_path)
        
        # Register DataFrame as a view
        conn.execute("CREATE OR REPLACE VIEW df_view AS SELECT * FROM df")
        
        if mode == "replace":
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df_view")
        else:
            conn.execute(f"INSERT INTO {table_name} SELECT * FROM df_view")
        
        conn.execute("DROP VIEW df_view")
        conn.close()
```

---

## 7. Production Best Practices

### 7.1 Scalability

```python
# Production scalability configuration
from dataclasses import dataclass

@dataclass
class ScalableConfig:
    """Configuration optimized for production scale."""
    
    # Memory: Allocate based on available RAM
    max_memory: str = "16GB"  # For production servers with 32GB+
    
    # Threads: Match CPU cores for parallel processing
    threads: int = 8  # Match to physical CPU cores
    
    # Batch size: Optimize for throughput
    batch_size: int = 4096  # Larger batches for bulk operations
    
    # File optimization
    parquet_row_group_size: int = 120000  # Optimal for analytics
    parquet_page_size: int = 65536
    
    # Cache settings
    enable_cache: bool = True
    cache_size: str = "1GB"
    
    # Checkpoint settings
    checkpoint_interval: int = 100000  # Checkpoint every N rows

# Usage in production
config = ScalableConfig()
con = duckdb.connect("production.db", config={
    "max_memory": config.max_memory,
    "threads": config.threads,
})
```

### 7.2 Monitoring and Observability

```python
# src/monitoring/duckdb_metrics.py
import time
import logging
from typing import Callable
from functools import wraps

logger = logging.getLogger(__name__)

def monitor_query(func: Callable) -> Callable:
    """Decorator to monitor query execution time and row counts."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = get_memory_usage()
        
        try:
            result = func(*args, **kwargs)
            
            elapsed = time.time() - start_time
            memory_delta = get_memory_usage() - start_memory
            row_count = len(result) if hasattr(result, '__len__') else 'N/A'
            
            logger.info(
                f"Query {func.__name__} completed: "
                f"time={elapsed:.2f}s, rows={row_count}, memory_delta={memory_delta}MB"
            )
            
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Query {func.__name__} failed after {elapsed:.2f}s: {e}")
            raise
    
    return wrapper

def get_memory_usage() -> float:
    """Get current memory usage in MB."""
    import psutil
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

class QueryMetrics:
    """Collect and report query metrics."""
    
    def __init__(self):
        self.metrics = []
    
    def record(self, query: str, duration: float, row_count: int, 
               memory_mb: float, status: str):
        """Record a query execution."""
        self.metrics.append({
            "query": query[:100],
            "duration": duration,
            "row_count": row_count,
            "memory_mb": memory_mb,
            "status": status,
            "timestamp": time.time(),
        })
    
    def get_summary(self) -> dict:
        """Get summary statistics."""
        if not self.metrics:
            return {}
        
        durations = [m["duration"] for m in self.metrics]
        return {
            "total_queries": len(self.metrics),
            "avg_duration": sum(durations) / len(durations),
            "max_duration": max(durations),
            "min_duration": min(durations),
            "success_rate": sum(1 for m in self.metrics if m["status"] == "success") / len(self.metrics),
        }
```

### 7.3 Logging

```sql
-- Enable DuckDB logging to CSV
CALL enable_logging(storage = 'stdout');

-- Custom logging setup via Python
```

```python
# Logging configuration
import logging
import json
from datetime import datetime

class DuckDBLogger:
    """Custom logger for DuckDB operations."""
    
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.logger = logging.getLogger("duckdb")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.JSONFormatter())
        self.logger.addHandler(handler)
    
    def log_query(self, query: str, params: dict = None, user: str = "system"):
        """Log query execution."""
        self.logger.info({
            "event": "query_executed",
            "query": query[:500],  # Truncate long queries
            "params": params,
            "user": user,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def log_error(self, query: str, error: str, user: str = "system"):
        """Log query error."""
        self.logger.error({
            "event": "query_error",
            "query": query[:500],
            "error": str(error),
            "user": user,
            "timestamp": datetime.utcnow().isoformat(),
        })
```

### 7.4 Backup Strategy

```python
# scripts/duckdb/backup.py
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import duckdb

class DuckDBBackupManager:
    """Manages automated backups of DuckDB databases."""
    
    def __init__(self, db_path: str, backup_dir: str):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, backup_name: str = None) -> str:
        """Create a backup of the database."""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / f"{backup_name}.duckdb"
        
        # Use DuckDB's BACKUP command
        conn = duckdb.connect(str(self.db_path))
        conn.execute(f"BACKUP DATABASE TO '{backup_path}'")
        conn.close()
        
        return str(backup_path)
    
    def restore_backup(self, backup_path: str):
        """Restore database from backup."""
        conn = duckdb.connect(str(self.db_path))
        conn.execute(f"RESTORE DATABASE FROM '{backup_path}'")
        conn.close()
    
    def rotate_backups(self, retention_days: int = 7):
        """Delete backups older than retention period."""
        cutoff = datetime.now() - timedelta(days=retention_days)
        
        for backup_file in self.backup_dir.glob("backup_*.duckdb"):
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if mtime < cutoff:
                backup_file.unlink()
                print(f"Deleted old backup: {backup_file}")
    
    def scheduled_backup(self):
        """Run scheduled backup with rotation."""
        backup_path = self.create_backup()
        self.rotate_backups()
        return backup_path
```

### 7.5 Performance Best Practices

```python
# Best practices configuration

# 1. Use appropriate data types
CREATE TABLE example (
    -- Use INTEGER for IDs (4 bytes vs VARCHAR)
    id INTEGER PRIMARY KEY,
    -- Use DECIMAL for money (exact precision)
    price DECIMAL(10, 2),
    -- Use VARCHAR for text, not TEXT
    name VARCHAR(255),
    -- Use TIMESTAMP for datetime
    created_at TIMESTAMP,
);

# 2. Create appropriate indexes
CREATE INDEX idx_transactions_time ON fact_transactions(transaction_time);
CREATE INDEX idx_transactions_store ON fact_transactions(store_id);
CREATE INDEX idx_transactions_composite ON fact_transactions(store_id, transaction_time);

# 3. Use partitioning for large tables
CREATE TABLE fact_transactions_partitioned (
    LIKE fact_transactions INCLUDING ALL
) PARTITION BY RANGE (transaction_time);

CREATE TABLE fact_transactions_2024_q1 
    PARTITION OF fact_transactions_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

# 4. Use compression for large tables
CREATE TABLE compressed_sales (
    LIKE sales INCLUDING ALL
) WITH (compression = 'zstd');

# 5. Use sequences for ID generation
CREATE SEQUENCE customer_id_seq START 1;
CREATE TABLE customers (
    customer_id INTEGER DEFAULT nextval('customer_id_seq'),
    name VARCHAR
);
```

---

## 8. Common Problems

### 8.1 Table of Common Issues and Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| Out of memory errors | Query requires more memory than allocated | Increase `max_memory`, optimize query, add indexes |
| Slow queries on large tables | Missing indexes or poor query design | Add indexes, use EXPLAIN ANALYZE, partition tables |
| Lock contention | Concurrent writes to same database | Use separate read/write databases, use transactions properly |
| Corrupt database | System crash during write | Enable WAL mode, regular backups, VACUUM after crashes |
| Slow bulk inserts | Default settings not optimized | Use COPY command, increase batch size, disable indexes during load |
| Parquet files slow to query | Row groups too small | Repartition with larger row groups (100K-1M rows) |
| Decimal precision loss | Wrong data type used | Use DECIMAL(p,s) instead of FLOAT/DOUBLE |
| Time zone issues | Implicit timezone conversion | Always use TIMESTAMPTZ, be explicit about time zones |

### 8.2 Troubleshooting Guide

#### Problem: "Out of Memory" Error

```python
# Diagnosis: Check current memory settings
con = duckdb.connect("retail.db")
print(con.execute("SELECT * FROM duckdb_settings() WHERE name LIKE '%memory%'").df())

# Solution 1: Increase memory limit
con = duckdb.connect("retail.db", config={"max_memory": "8GB"})

# Solution 2: Enable disk spilling for large queries
con = duckdb.connect("retail.db", config={
    "max_memory": "4GB",
    "temp_directory": "/path/to/spill/dir"
})

# Solution 3: Optimize the query
# Instead of: SELECT * FROM huge_table
# Use: SELECT only needed columns
result = con.sql("""
    SELECT date, SUM(revenue) 
    FROM fact_transactions 
    WHERE store_id = 'ST001'
    GROUP BY date
""").df()
```

#### Problem: Slow Query Performance

```python
# Step 1: Analyze the query plan
query_plan = con.execute("EXPLAIN SELECT * FROM fact_transactions WHERE store_id = 'ST001'").fetchall()
print(query_plan)

# Step 2: Check for missing indexes
existing_indexes = con.execute("SELECT * FROM duckdb_indexes()").df()
print(existing_indexes)

# Step 3: Add appropriate indexes
con.execute("CREATE INDEX idx_store_id ON fact_transactions(store_id)")

# Step 4: Check statistics
con.execute("ANALYZE fact_transactions")

# Step 5: Check for data skew
data_distribution = con.execute("""
    SELECT store_id, COUNT(*) as cnt 
    FROM fact_transactions 
    GROUP BY store_id 
    ORDER BY cnt DESC 
    LIMIT 10
""").df()
print(data_distribution)
```

#### Problem: Database Lock Timeout

```python
# Check for active connections
con = duckdb.connect("retail.db")
active_connections = con.execute("SELECT * FROM duckdb_connections()").df()
print(active_connections)

# Use proper transaction management
with con.transaction():
    con.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    con.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
    # Auto-commits on successful exit

# For long-running operations, use read-only mode
read_con = duckdb.connect("retail.db", read_only=True)
result = read_con.execute("SELECT SUM(revenue) FROM sales").fetchone()
```

### 8.3 Error Handling Patterns

```python
# Robust error handling
import duckdb
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class DuckDBError(Exception):
    """Base exception for DuckDB operations."""
    pass

class QueryError(DuckDBError):
    """Query execution error."""
    pass

class ConnectionError(DuckDBError):
    """Connection error."""
    pass

class ValidationError(DuckDBError):
    """Data validation error."""
    pass

def safe_query(query: str, params: Optional[tuple] = None, 
               max_retries: int = 3) -> list:
    """Execute query with retry logic."""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            con = duckdb.connect("retail.db")
            result = con.execute(query, params).fetchall()
            con.close()
            return result
        except duckdb.IOException as e:
            last_error = e
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            import time
            time.sleep(2 ** attempt)  # Exponential backoff
    
    raise QueryError(f"Query failed after {max_retries} attempts: {last_error}")

def validate_schema(table_name: str, expected_schema: dict) -> bool:
    """Validate table schema matches expected structure."""
    con = duckdb.connect("retail.db")
    
    actual = con.execute(f"DESCRIBE {table_name}").fetchall()
    con.close()
    
    for col_name, col_type in expected_schema.items():
        if col_name not in [a[0] for a in actual]:
            raise ValidationError(f"Missing column: {col_name}")
    
    return True
```

---

## 9. Performance Optimization

### 9.1 Query Tuning

```python
# Advanced query optimization techniques

# 1. Predicate Pushdown - Filters are applied as early as possible
# Good: Filter before join
query_good = """
    SELECT s.store_name, SUM(t.revenue)
    FROM fact_transactions t
    JOIN dim_stores s ON t.store_id = s.store_id
    WHERE t.transaction_time >= '2024-01-01'
      AND s.region = 'Northeast'
    GROUP BY s.store_name
"""

# 2. Avoid SELECT * - Only fetch needed columns
query_optimized = """
    SELECT 
        DATE_TRUNC('day', transaction_time) as date,
        SUM(revenue) as daily_revenue
    FROM fact_transactions
    WHERE transaction_time >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY 1
"""

# 3. Use APPROXIMATE functions for large datasets
query_approx = """
    SELECT 
        APPROX_COUNT_DISTINCT(customer_id) as unique_customers
    FROM fact_transactions
    WHERE transaction_time >= CURRENT_DATE - INTERVAL '90 days'
"""

# 4. Use window functions instead of self-joins
query_window = """
    WITH daily AS (
        SELECT DATE_TRUNC('day', transaction_time) as date, SUM(revenue) as revenue
        FROM fact_transactions
        GROUP BY 1
    )
    SELECT 
        date,
        revenue,
        LAG(revenue, 7) OVER (ORDER BY date) as revenue_7d_ago,
        revenue - LAG(revenue, 7) OVER (ORDER BY date) as revenue_change
    FROM daily
"""

# 5. Use MATERIALIZED views for expensive aggregations
con.execute("""
    CREATE MATERIALIZED VIEW monthly_sales AS
    SELECT 
        DATE_TRUNC('month', transaction_time) as month,
        store_id,
        category,
        SUM(revenue) as total_revenue,
        SUM(quantity) as total_units
    FROM fact_transactions
    GROUP BY 1, 2, 3
""")

# Query materialized view instead of computing each time
result = con.execute("SELECT * FROM monthly_sales WHERE month >= '2024-01-01'").df()
```

### 9.2 Vectorization Configuration

```python
# Vectorization settings
con = duckdb.connect("retail.db", config={
    # Vector size: 2048 is default, can tune based on CPU
    # Larger vectors = better CPU cache utilization
    # Smaller vectors = more parallelism
    
    # Enable SIMD operations (automatic in most cases)
    "force_index_join": False,
    
    # Nested loop join threshold
    "nested_loop_join_threshold": 1000,
    
    # Enable parallel query execution
    "threads": 8,
})

# Check vectorization in query plan
plan = con.execute("EXPLAIN SELECT * FROM fact_transactions LIMIT 1").fetchall()
print(plan)
# Look for "VectorSize" in the plan output
```

### 9.3 Parallelism Settings

```python
# Parallel query execution configuration

# Determine optimal thread count
import os
optimal_threads = os.cpu_count()  # Or use psutil for better accuracy

con = duckdb.connect("retail.db", config={
    "threads": optimal_threads,
})

# For bulk operations, consider:
# - Single-threaded for small data (< 100K rows)
# - Multi-threaded for medium data (100K - 10M rows)
# - Distributed for large data (> 10M rows)

# Force parallel execution for analysis
con.execute("SET threads TO 8")
con.execute("SET enable_parallel_optimizer TO true")

# Monitor parallel execution
result = con.execute("EXPLAIN ANALYZE SELECT COUNT(*) FROM fact_transactions").df()
print(result)
```

### 9.4 Extension Performance

```python
# Use extensions for specific optimization needs

# HTTPFS extension for parallel S3 reads
con.execute("INSTALL httpfs; LOAD httpfs;")

# For S3 data, configure for parallel reads
con.execute("SET s3_uploader_thread_amount TO 8")

# Iceberg extension for table format optimization
con.execute("INSTALL iceberg; LOAD iceberg;")

# Spatial extension for geospatial queries
con.execute("INSTALL spatial; LOAD spatial;")

# For ML workloads
con.execute("INSTALL ml; LOAD ml;")

# Arrow integration for zero-copy reads
import pyarrow as pa
table = pa.ipc.open_file('data.arrow').read_all()
con.execute("CREATE VIEW df AS SELECT * FROM table")
```

### 9.5 Memory Tuning

```python
# Memory optimization strategies

# 1. Streaming large results
con = duckdb.connect("retail.db")
result_stream = con.execute("""
    SELECT * FROM fact_transactions 
    WHERE transaction_time >= '2023-01-01'
""")

# Process in batches
batch_size = 100000
while True:
    batch = result_stream.fetchmany(batch_size)
    if not batch:
        break
    process_batch(batch)

# 2. External aggregation for large GROUP BY
con.execute("SET enable_external_aggregation TO true")

# 3. Spill to disk for large sorts
con.execute("SET external_sort_threshold TO 2GB")

# 4. Memory-mapped I/O for large files
con.execute("SET memory_map TO true")

# 5. Monitor memory usage
memory_info = con.execute("""
    SELECT 
        peak_memory_usage(),
        peak_memory_usage_bytes()
""").fetchone()
print(f"Peak memory: {memory_info[0]}")
```

---

## 10. Security

### 10.1 Authentication and Authorization

```python
# Authentication using Quack extension (DuckDB's auth system)

# Install Quack extension
con.execute("INSTALL quack FROM 'community';")
con.execute("LOAD quack;")

# Define authentication function
con.execute("""
    CREATE OR REPLACE FUNCTION my_auth(auth_token VARCHAR)
    RETURNS BOOLEAN
    AS $$
        -- Validate against auth service
        RETURN validate_token(auth_token);
    $$
    LANGUAGE python;
""")

# Set authentication hook
con.execute("PRAGMA authentication='my_auth';")

# Authorization: Row-level security
con.execute("""
    CREATE POLICY store_isolation ON fact_transactions
    USING (store_id = current_user_store());
""")
```

### 10.2 Database Encryption

```sql
-- Attach encrypted database
ATTACH 'retail_encrypted.db' AS enc_db (
    ENCRYPTION_KEY 'your-256-bit-key-here'
);

-- DuckDB uses AES-256 GCM encryption by default

-- For faster encryption with httpfs
LOAD httpfs;
```

```python
# Python example for encrypted databases
import duckdb

# Create encrypted database
con = duckdb.connect("encrypted_retail.db")
con.execute("SET encryption_key = 'your-256-bit-key-here'")
con.execute("CREATE TABLE sensitive_data (id INTEGER, data VARCHAR)")
con.close()

# Open encrypted database
con = duckdb.connect("encrypted_retail.db", config={
    "encryption_key": "your-256-bit-key-here"
})
result = con.execute("SELECT * FROM sensitive_data").df()
```

### 10.3 Secrets Management

```python
# Secrets management for cloud storage

# Store secrets in environment variables (recommended)
import os

# S3 secrets
os.environ['S3_ACCESS_KEY_ID'] = 'your-access-key'
os.environ['S3_SECRET_ACCESS_KEY'] = 'your-secret-key'

# In DuckDB, use secrets
con.execute("CREATE SECRET s3_secret (TYPE S3, KEY_ID env('S3_ACCESS_KEY_ID'), SECRET env('S3_SECRET_ACCESS_KEY'));")

# Azure secrets
os.environ['AZURE_STORAGE_KEY'] = 'your-azure-key'
con.execute("CREATE SECRET azure_secret (TYPE AZURE, ACCOUNT_NAME 'myaccount', ACCOUNT_KEY env('AZURE_STORAGE_KEY'));")

# GCP secrets
con.execute("CREATE SECRET gcp_secret (TYPE GCS, KEY_FILE '/path/to/gcp-key.json'));")
```

### 10.4 SQL Injection Prevention

```python
# Always use parameterized queries

# BAD - SQL injection vulnerable
query = f"SELECT * FROM customers WHERE customer_id = '{user_input}'"
con.execute(query)

# GOOD - Parameterized query
query = "SELECT * FROM customers WHERE customer_id = ?"
con.execute(query, params=[user_input])

# For multiple parameters
query = "SELECT * FROM sales WHERE store_id = ? AND transaction_date > ?"
con.execute(query, params=['ST001', '2024-01-01'])

# Using named parameters
query = "SELECT * FROM sales WHERE store_id = :store_id AND amount > :min_amount"
con.execute(query, params={'store_id': 'ST001', 'min_amount': 100})
```

### 10.5 File Permissions

```bash
# Set appropriate file permissions (Unix/Linux)
chmod 600 retail_analytics.db          # Owner read/write only
chmod 700 data/duckdb/                 # Directory access only
chmod 600 config/duckdb_credentials    # Credentials file

# For backups
chmod 700 backups/                     # Restrict backup access
```

---

## 11. Monitoring

### 11.1 Key Metrics to Track

```python
# src/monitoring/metrics.py
import time
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime

@dataclass
class DuckDBMetrics:
    """DuckDB metrics collector."""
    
    queries_executed: int = 0
    queries_failed: int = 0
    total_query_time: float = 0.0
    total_rows_returned: int = 0
    peak_memory_mb: float = 0.0
    current_connections: int = 0
    active_transactions: int = 0
    
    # Per-query history
    query_history: List[Dict] = field(default_factory=list)
    
    def record_query(self, query: str, duration: float, 
                     rows: int, memory_mb: float, status: str):
        """Record a query execution."""
        self.queries_executed += 1
        self.total_query_time += duration
        self.total_rows_returned += rows
        self.peak_memory_mb = max(self.peak_memory_mb, memory_mb)
        
        if status == "failed":
            self.queries_failed += 1
        
        self.query_history.append({
            "timestamp": datetime.now().isoformat(),
            "query_hash": hash(query[:100]),
            "duration": duration,
            "rows": rows,
            "memory_mb": memory_mb,
            "status": status,
        })
    
    def get_stats(self) -> Dict:
        """Get current statistics."""
        avg_query_time = (
            self.total_query_time / self.queries_executed 
            if self.queries_executed > 0 else 0
        )
        
        return {
            "total_queries": self.queries_executed,
            "failed_queries": self.queries_failed,
            "success_rate": (
                (self.queries_executed - self.queries_failed) / 
                self.queries_executed * 100 
                if self.queries_executed > 0 else 0
            ),
            "avg_query_time_ms": avg_query_time * 1000,
            "total_rows_returned": self.total_rows_returned,
            "peak_memory_mb": self.peak_memory_mb,
        }
    
    def get_slow_queries(self, threshold_ms: float = 1000) -> List[Dict]:
        """Get queries slower than threshold."""
        return [
            q for q in self.query_history 
            if q["duration"] * 1000 > threshold_ms
        ]
```

### 11.2 Alerts Configuration

```python
# src/monitoring/alerts.py
import logging
from typing import Callable, List

class AlertManager:
    """Manage alerts for DuckDB metrics."""
    
    def __init__(self):
        self.alert_rules: List[AlertRule] = []
        self.handlers: List[Callable] = []
    
    def add_rule(self, name: str, condition: Callable, 
                 severity: str, message: str):
        """Add an alert rule."""
        self.alert_rules.append({
            "name": name,
            "condition": condition,
            "severity": severity,  # critical, warning, info
            "message": message,
        })
    
    def add_handler(self, handler: Callable):
        """Add an alert handler (e.g., email, Slack, PagerDuty)."""
        self.handlers.append(handler)
    
    def check(self, metrics: DuckDBMetrics):
        """Check all alert rules against current metrics."""
        stats = metrics.get_stats()
        
        for rule in self.alert_rules:
            if rule["condition"](stats):
                alert = {
                    "rule": rule["name"],
                    "severity": rule["severity"],
                    "message": rule["message"].format(**stats),
                    "timestamp": datetime.now().isoformat(),
                }
                
                for handler in self.handlers:
                    handler(alert)


# Define alert rules
alert_manager = AlertManager()

alert_manager.add_rule(
    name="high_failure_rate",
    condition=lambda s: s["success_rate"] < 95,
    severity="critical",
    message="Query failure rate is {failed_queries}/{total_queries} ({success_rate:.1f}%)"
)

alert_manager.add_rule(
    name="slow_queries",
    condition=lambda s: s["avg_query_time_ms"] > 5000,
    severity="warning",
    message="Average query time is {avg_query_time_ms:.0f}ms"
)

alert_manager.add_rule(
    name="high_memory",
    condition=lambda s: s["peak_memory_mb"] > 8000,
    severity="warning",
    message="Peak memory usage is {peak_memory_mb:.0f}MB"
)


def slack_alert_handler(alert: Dict):
    """Send alert to Slack."""
    import requests
    
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    
    color = {
        "critical": "danger",
        "warning": "warning", 
        "info": "good"
    }.get(alert["severity"], "good")
    
    payload = {
        "attachments": [{
            "color": color,
            "title": f"DuckDB Alert: {alert['rule']}",
            "text": alert["message"],
            "ts": alert["timestamp"],
        }]
    }
    
    requests.post(webhook_url, json=payload)


alert_manager.add_handler(slack_alert_handler)
```

### 11.3 Dashboards

```python
# Example dashboard queries for Grafana

# Dashboard 1: Query Performance
QUERY_PERFORMANCE = """
SELECT 
    DATE_TRUNC('minute', start_time) as time,
    COUNT(*) as query_count,
    AVG(duration_ms) as avg_duration_ms,
    MAX(duration_ms) as p99_duration_ms,
    SUM(rows) as total_rows
FROM query_log
WHERE start_time >= NOW() - INTERVAL '1 hour'
GROUP BY 1
ORDER BY 1
"""

# Dashboard 2: Memory Usage
MEMORY_USAGE = """
SELECT 
    current_memory_usage() / 1024 / 1024 / 1024 as memory_gb,
    peak_memory_usage() / 1024 / 1024 / 1024 as peak_memory_gb,
    total_memory_size() / 1024 / 1024 / 1024 as total_allocated_gb
"""

# Dashboard 3: Table Statistics
TABLE_STATS = """
SELECT 
    table_name,
    estimated_size() / 1024 / 1024 as size_mb,
    row_count,
    index_size() / 1024 / 1024 as index_size_mb
FROM information_schema.tables
WHERE table_schema = 'main'
ORDER BY estimated_size() DESC
"""

# Dashboard 4: Connection Status
CONNECTION_STATUS = """
SELECT 
    process_id,
    start_time,
    query,
    memory_usage() / 1024 / 1024 as memory_mb
FROM duckdb_connections()
WHERE not finished
"""
```

---

## 12. Testing Strategy

### 12.1 Unit Testing

```python
# tests/unit/test_aggregation_cache.py
import pytest
import duckdb
import pandas as pd
from datetime import datetime, timedelta
import sys
sys.path.insert(0, 'src')

from analytics.aggregation_cache import AggregationCache

@pytest.fixture
def test_db():
    """Create a test database."""
    con = duckdb.connect(":memory:")
    
    # Create test tables
    con.execute("""
        CREATE TABLE fact_transactions (
            transaction_id VARCHAR,
            transaction_time TIMESTAMP,
            store_id VARCHAR,
            revenue DECIMAL(10,2),
            quantity INTEGER
        )
    """)
    
    # Insert test data
    test_data = [
        ("TXN001", datetime(2024, 1, 1, 10, 0), "ST001", 100.00, 2),
        ("TXN002", datetime(2024, 1, 1, 11, 0), "ST001", 150.00, 3),
        ("TXN003", datetime(2024, 1, 1, 10, 0), "ST002", 200.00, 4),
    ]
    
    con.executemany(
        "INSERT INTO fact_transactions VALUES (?, ?, ?, ?, ?)",
        test_data
    )
    
    yield con
    con.close()

def test_hourly_sales_aggregation(test_db):
    """Test hourly sales aggregation."""
    cache = AggregationCache(":memory:")
    
    # Process transactions
    cache.con.execute("""
        CREATE TABLE hourly_sales AS
        SELECT 
            DATE_TRUNC('hour', transaction_time) as hour,
            store_id,
            SUM(revenue) as total_revenue,
            SUM(quantity) as total_units
        FROM fact_transactions
        GROUP BY 1, 2
    """)
    
    result = cache.con.execute("SELECT * FROM hourly_sales").df()
    
    assert len(result) == 2  # Two stores
    assert result[result['store_id'] == 'ST001']['total_revenue'].iloc[0] == 250.00
    assert result[result['store_id'] == 'ST002']['total_revenue'].iloc[0] == 200.00

def test_dashboard_data_query(test_db):
    """Test dashboard data retrieval."""
    cache = AggregationCache(":memory:")
    cache.con.execute("""
        INSERT INTO hourly_sales VALUES 
        ('2024-01-01 10:00:00', 'ST001', 250.00, 5)
    """)
    
    result = cache.get_dashboard_data("ST001")
    
    assert len(result) == 1
    assert result['total_revenue'].iloc[0] == 250.00

def test_empty_result_handling(test_db):
    """Test handling of empty results."""
    cache = AggregationCache(":memory:")
    
    result = cache.get_dashboard_data("NONEXISTENT")
    
    assert len(result) == 0
```

### 12.2 Integration Testing

```python
# tests/integration/test_duckdb_etl.py
import pytest
import duckdb
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, 'src')

from etl.duckdb_preprocessor import RetailDataPreprocessor

@pytest.fixture
def test_config(tmp_path):
    """Create test configuration."""
    return {
        'processed_db': str(tmp_path / "test_processed.db"),
        'raw_path': str(tmp_path / "raw"),
        'warehouse_path': str(tmp_path / "warehouse"),
    }

@pytest.fixture
def sample_parquet(tmp_path):
    """Create sample Parquet file."""
    df = pd.DataFrame({
        'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
        'transaction_time': pd.date_range('2024-01-01', periods=3, freq='h'),
        'store_id': ['ST001', 'ST001', 'ST002'],
        'revenue': [100.0, 150.0, 200.0],
        'quantity': [1, 2, 3],
    })
    
    path = tmp_path / "raw" / "sales_2024-01-01.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    
    return str(path)

def test_preprocessor_initialization(test_config):
    """Test preprocessor initialization."""
    preprocessor = RetailDataPreprocessor(test_config)
    
    assert preprocessor.config == test_config
    assert preprocessor.con is not None

def test_daily_sales_processing(test_config, sample_parquet, tmp_path):
    """Test daily sales processing."""
    # Update config with actual parquet path
    test_config['raw_path'] = str(tmp_path / "raw")
    test_config['warehouse_path'] = str(tmp_path / "warehouse")
    
    preprocessor = RetailDataPreprocessor(test_config)
    
    # This should process without errors
    # Note: actual execution depends on the raw data structure
    # In real tests, you'd mock or create proper test data

def test_parquet_export(test_config, tmp_path):
    """Test Parquet export functionality."""
    preprocessor = RetailDataPreprocessor(test_config)
    
    # Create test data
    preprocessor.con.execute("""
        CREATE TABLE test_data AS 
        SELECT * FROM range(10) AS t(id)
    """)
    
    # Export
    export_path = str(tmp_path / "export.parquet")
    preprocessor.con.execute(f"""
        COPY test_data TO '{export_path}' (FORMAT PARQUET)
    """)
    
    assert Path(export_path).exists()
```

### 12.3 Performance Testing

```python
# tests/performance/test_query_performance.py
import pytest
import time
import duckdb
import pandas as pd
import numpy as np

class TestQueryPerformance:
    """Performance tests for DuckDB queries."""
    
    @pytest.fixture
    def large_dataset(self):
        """Create a large test dataset."""
        con = duckdb.connect(":memory:")
        
        # Generate 10 million rows
        n_rows = 10_000_000
        
        df = pd.DataFrame({
            'transaction_id': [f'TXN{i:010d}' for i in range(n_rows)],
            'transaction_time': pd.date_range(
                '2023-01-01', 
                periods=n_rows, 
                freq='1min'
            ),
            'store_id': np.random.choice(['ST001', 'ST002', 'ST003', 'ST004'], n_rows),
            'product_id': np.random.choice([f'P{i:05d}' for i in range(1000)], n_rows),
            'revenue': np.random.uniform(10, 1000, n_rows),
            'quantity': np.random.randint(1, 10, n_rows),
        })
        
        con.execute("CREATE TABLE fact_transactions AS SELECT * FROM df")
        
        yield con
        con.close()
    
    def test_aggregation_performance(self, large_dataset):
        """Test aggregation query performance."""
        query = """
            SELECT 
                store_id,
                DATE_TRUNC('day', transaction_time) as date,
                SUM(revenue) as total_revenue,
                COUNT(*) as transaction_count
            FROM fact_transactions
            GROUP BY store_id, 2
        """
        
        start = time.time()
        result = large_dataset.execute(query).fetchall()
        elapsed = time.time() - start
        
        # Should complete in under 5 seconds for 10M rows
        assert elapsed < 5.0, f"Query took {elapsed:.2f}s, expected < 5s"
        assert len(result) > 0
    
    def test_join_performance(self, large_dataset):
        """Test join query performance."""
        # Create dimension table
        large_dataset.execute("""
            CREATE TABLE dim_stores AS
            SELECT store_id, store_name, region 
            FROM (VALUES ('ST001', 'Store 1', 'North'), 
                         ('ST002', 'Store 2', 'South'),
                         ('ST003', 'Store 3', 'East'),
                         ('ST004', 'Store 4', 'West')) AS t(id, name, region)
        """)
        
        query = """
            SELECT 
                s.region,
                SUM(t.revenue) as total_revenue
            FROM fact_transactions t
            JOIN dim_stores s ON t.store_id = s.store_id
            GROUP BY s.region
        """
        
        start = time.time()
        result = large_dataset.execute(query).fetchall()
        elapsed = time.time() - start
        
        # Should complete in under 10 seconds
        assert elapsed < 10.0
        assert len(result) == 4
    
    def test_window_function_performance(self, large_dataset):
        """Test window function performance."""
        query = """
            WITH daily AS (
                SELECT 
                    DATE_TRUNC('day', transaction_time) as date,
                    SUM(revenue) as daily_revenue
                FROM fact_transactions
                GROUP BY 1
            )
            SELECT 
                date,
                daily_revenue,
                AVG(daily_revenue) OVER (
                    ORDER BY date 
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                ) as rolling_7d_avg
            FROM daily
            ORDER BY date
        """
        
        start = time.time()
        result = large_dataset.execute(query).fetchall()
        elapsed = time.time() - start
        
        assert elapsed < 8.0, f"Window query took {elapsed:.2f}s"
```

### 12.4 Test Data Management

```python
# tests/fixtures/test_data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class TestDataGenerator:
    """Generate realistic test data for DuckDB testing."""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.seed = seed
    
    def generate_transactions(self, n: int, 
                               start_date: datetime = datetime(2024, 1, 1)) -> pd.DataFrame:
        """Generate realistic transaction data."""
        
        stores = [f'ST{i:03d}' for i in range(1, 51)]  # 50 stores
        categories = ['Electronics', 'Clothing', 'Food', 'Home', 'Sports']
        products = {
            'Electronics': [f'E{i:04d}' for i in range(1, 201)],
            'Clothing': [f'C{i:04d}' for i in range(1, 301)],
            'Food': [f'F{i:04d}' for i in range(1, 501)],
            'Home': [f'H{i:04d}' for i in range(1, 151)],
            'Sports': [f'S{i:04d}' for i in range(1, 101)],
        }
        
        data = []
        for i in range(n):
            category = np.random.choice(categories)
            product_id = np.random.choice(products[category])
            
            data.append({
                'transaction_id': f'TXN{i:012d}',
                'transaction_time': start_date + timedelta(
                    minutes=np.random.randint(0, 525600)  # Up to 1 year
                ),
                'store_id': np.random.choice(stores),
                'customer_id': f'CUST{np.random.randint(1, 100001):06d}' 
                               if np.random.random() > 0.1 else None,  # 10% anonymous
                'product_id': product_id,
                'category': category,
                'quantity': np.random.randint(1, 10),
                'unit_price': np.random.uniform(5, 500),
                'revenue': 0,  # Calculated below
            })
        
        df = pd.DataFrame(data)
        df['revenue'] = df['quantity'] * df['unit_price']
        df['revenue'] = df['revenue'].round(2)
        
        return df.sort_values('transaction_time').reset_index(drop=True)
    
    def generate_stores(self, n: int = 50) -> pd.DataFrame:
        """Generate store dimension data."""
        regions = ['Northeast', 'Southeast', 'Midwest', 'Southwest', 'West']
        store_types = ['mall', 'outlet', 'standalone', 'flagship']
        
        return pd.DataFrame({
            'store_id': [f'ST{i:03d}' for i in range(1, n + 1)],
            'store_name': [f'Store {i}' for i in range(1, n + 1)],
            'region': np.random.choice(regions, n),
            'city': [f'City {i}' for i in range(1, n + 1)],
            'state': np.random.choice(['NY', 'CA', 'TX', 'FL', 'IL', 'PA'], n),
            'store_type': np.random.choice(store_types, n),
            'opened_date': [
                datetime(2010, 1, 1) + timedelta(days=np.random.randint(0, 5000))
                for _ in range(n)
            ],
        })
    
    def save_to_parquet(self, df: pd.DataFrame, path: str):
        """Save DataFrame to Parquet."""
        df.to_parquet(path, index=False)
```

---

## 13. Interview Preparation

### 13.1 Beginner Questions (30)

**Q1: What is DuckDB and what is it used for?**

A: DuckDB is an in-process, embeddable analytical database management system (DBMS) designed for Online Analytical Processing (OLAP). It is used for running complex analytical queries on data, often directly on files like Parquet or CSV without needing to load data into a traditional database first. It's popular in data science, analytics pipelines, and embedded analytics applications.

**Q2: How does DuckDB differ from SQLite?**

A: Key differences:
- **Purpose**: DuckDB is optimized for analytical queries (OLAP), while SQLite is optimized for transactional queries (OLTP)
- **Storage**: DuckDB uses columnar storage, SQLite uses row-based storage
- **Execution**: DuckDB uses vectorized execution, SQLite uses row-by-row execution
- **Performance**: For aggregations and joins, DuckDB is typically 10-100x faster than SQLite
- **Use case**: DuckDB for analytics pipelines, dashboards, ETL; SQLite for embedded/mobile applications

**Q3: What is vectorized execution?**

A: Vectorized execution processes batches of rows (typically 2048 rows per batch) at a time rather than processing one row at a time. This approach:
- Reduces function call overhead
- Enables CPU SIMD operations for parallel processing
- Improves cache locality
- Results in significantly faster analytical queries

**Q4: What is columnar storage?**

A: Columnar storage organizes data by columns rather than rows. Each column is stored separately, allowing:
- Only reading columns needed for a query (column pruning)
- Better compression (similar values compress together)
- Faster aggregations (all values of one column are contiguous)

**Q5: How do you create a table in DuckDB?**

```sql
CREATE TABLE sales (
    transaction_id VARCHAR PRIMARY KEY,
    transaction_time TIMESTAMP NOT NULL,
    store_id VARCHAR NOT NULL,
    revenue DECIMAL(10, 2),
    quantity INTEGER DEFAULT 1
);
```

**Q6: What is the difference between VARCHAR and TEXT in DuckDB?**

A: In DuckDB, VARCHAR and TEXT are essentially the same type. VARCHAR(n) is an alias that specifies a maximum length, but DuckDB doesn't enforce it. TEXT is unbounded. For compatibility with other databases, VARCHAR is preferred.

**Q7: How do you load data from a Parquet file?**

```sql
-- Method 1: Create table from Parquet
CREATE TABLE sales AS SELECT * FROM read_parquet('sales.parquet');

-- Method 2: Query directly
SELECT * FROM read_parquet('sales.parquet') WHERE revenue > 100;

-- Method 3: Query with glob
SELECT * FROM read_parquet('s3://bucket/sales/*.parquet');
```

**Q8: What is the purpose of the EXPLAIN statement?**

A: EXPLAIN shows the query execution plan without actually executing the query. It helps understand how DuckDB will process the query, including:
- Join order
- Filter pushdown
- Index usage
- Parallelization strategy

```sql
EXPLAIN SELECT * FROM sales WHERE store_id = 'ST001';
```

**Q9: How do you create an index in DuckDB?**

```sql
CREATE INDEX idx_store_id ON sales(store_id);
CREATE INDEX idx_time_store ON sales(transaction_time, store_id);
```

**Q10: What are DuckDB extensions?**

A: Extensions add capabilities to DuckDB:
- `httpfs`: Read files from HTTP/S3/GCS
- `parquet`: Read/write Parquet files
- `iceberg`: Read Iceberg tables
- `spatial`: Geospatial operations
- `postgres`: Connect to PostgreSQL
- `mysql`: Connect to MySQL

```sql
INSTALL httpfs;
LOAD httpfs;
```

**Q11: How do you connect to DuckDB from Python?**

```python
import duckdb

# In-memory database
con = duckdb.connect()

# File-based database
con = duckdb.connect('retail.db')

# With configuration
con = duckdb.connect('retail.db', config={'max_memory': '4GB'})

# Execute queries
result = con.execute('SELECT * FROM sales LIMIT 10').fetchall()
result_df = con.execute('SELECT * FROM sales').df()
```

**Q12: What is DuckDB's approach to transactions?**

A: DuckDB supports full ACID transactions:
```python
con.begin()
try:
    con.execute("INSERT INTO sales VALUES ('TXN001', 100.00)")
    con.execute("COMMIT")
except:
    con.execute("ROLLBACK")
```

**Q13: How do you export data to Parquet?**

```sql
COPY (SELECT * FROM sales WHERE date >= '2024-01-01')
TO 'sales_2024.parquet'
(FORMAT PARQUET, COMPRESSION 'zstd');
```

**Q14: What is the difference between COUNT(*), COUNT(col), and COUNT(DISTINCT col)?**

- `COUNT(*)`: Counts all rows including NULLs
- `COUNT(col)`: Counts non-NULL values in the column
- `COUNT(DISTINCT col)`: Counts unique non-NULL values

**Q15: What window functions does DuckDB support?**

DuckDB supports standard window functions:
- Ranking: `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`
- Navigation: `LAG()`, `LEAD()`, `FIRST_VALUE()`, `LAST_VALUE()`
- Aggregation: `SUM() OVER`, `AVG() OVER`, etc.
- Distribution: `NTILE()`, `PERCENT_RANK()`

**Q16: How do you handle NULL values in DuckDB?**

```sql
-- COALESCE: Return first non-NULL
SELECT COALESCE(discount, 0) FROM sales;

-- NULLIF: Return NULL if values are equal
SELECT NULLIF(quantity, 0) FROM sales;

-- IFNULL: SQLite-style
SELECT IFNULL(name, 'Unknown') FROM products;

-- IS NULL / IS NOT NULL
SELECT * FROM sales WHERE discount IS NOT NULL;
```

**Q17: What is a CTE (Common Table Expression)?**

```sql
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', transaction_time) as month,
        SUM(revenue) as total_revenue
    FROM sales
    GROUP BY 1
)
SELECT * FROM monthly_sales WHERE total_revenue > 100000;
```

**Q18: How do you perform a JOIN in DuckDB?**

```sql
-- INNER JOIN
SELECT s.*, p.product_name
FROM sales s
JOIN products p ON s.product_id = p.product_id;

-- LEFT JOIN
SELECT s.*, p.product_name
FROM sales s
LEFT JOIN products p ON s.product_id = p.product_id;

-- Multiple joins
SELECT *
FROM sales s
JOIN products p ON s.product_id = p.product_id
JOIN stores st ON s.store_id = st.store_id;
```

**Q19: What is the difference between UNION and UNION ALL?**

- `UNION`: Combines results and removes duplicates
- `UNION ALL`: Combines results keeping all rows (faster)

**Q20: How do you use GROUP BY with HAVING?**

```sql
SELECT 
    store_id,
    SUM(revenue) as total_revenue
FROM sales
GROUP BY store_id
HAVING SUM(revenue) > 100000;
```

**Q21: What date/time functions does DuckDB support?**

```sql
-- DATE_TRUNC
SELECT DATE_TRUNC('month', transaction_time) FROM sales;

-- DATE_PART / EXTRACT
SELECT EXTRACT(YEAR FROM transaction_time) FROM sales;

-- Current date/time
SELECT CURRENT_DATE, CURRENT_TIMESTAMP, NOW();

-- Interval arithmetic
SELECT transaction_time + INTERVAL '7 days' FROM sales;
```

**Q22: What is the purpose of CHECK constraints?**

```sql
CREATE TABLE sales (
    revenue DECIMAL(10,2) CHECK (revenue >= 0),
    quantity INTEGER CHECK (quantity > 0)
);
```

**Q23: How do you use CASE statements?**

```sql
SELECT 
    product_name,
    CASE 
        WHEN price < 10 THEN 'Budget'
        WHEN price < 100 THEN 'Mid-range'
        ELSE 'Premium'
    END as price_category
FROM products;
```

**Q24: What is DuckDB's default vector size?**

A: 2048 rows per vector. This is configurable but 2048 provides optimal CPU cache utilization for most workloads.

**Q25: How do you create a view?**

```sql
CREATE VIEW high_value_sales AS
SELECT * FROM sales WHERE revenue > 1000;

-- Query the view
SELECT * FROM high_value_sales;
```

**Q26: What is the difference between a view and a materialized view?**

- **View**: Virtual table, computed each time it's queried
- **Materialized View**: Pre-computed and stored, must be refreshed

```sql
-- View
CREATE VIEW daily_totals AS SELECT DATE_TRUNC('day', t) as day, SUM(r) FROM t GROUP BY 1;

-- Materialized View
CREATE MATERIALIZED VIEW daily_totals_mv AS SELECT DATE_TRUNC('day', t) as day, SUM(r) FROM t GROUP BY 1;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW daily_totals_mv;
```

**Q27: How do you handle string functions?**

```sql
-- Concatenation
SELECT CONCAT(first_name, ' ', last_name) FROM customers;

-- String length
SELECT LENGTH(product_name) FROM products;

-- Substring
SELECT SUBSTRING(product_name, 1, 10) FROM products;

-- Upper/Lower
SELECT UPPER(store_name), LOWER(email) FROM stores;
```

**Q28: What is the DuckDB relational API in Python?**

```python
rel = con.sql("SELECT * FROM sales WHERE revenue > 100")
result = rel.filter("store_id = 'ST001'").aggregate("SUM(revenue) as total").df()
```

**Q29: How do you configure DuckDB memory settings?**

```python
con = duckdb.connect(config={
    'max_memory': '8GB',
    'threads': 4,
    'temp_directory': '/tmp/duckdb_spill'
})
```

**Q30: What file formats does DuckDB support?**

A: DuckDB supports:
- Parquet (read/write)
- CSV (read/write with auto-detection)
- JSON (read/write)
- Arrow (zero-copy)
- HDF5
- Excel (via extension)
- Database files (.duckdb)

---

### 13.2 Intermediate Questions (30)

**Q31: Explain DuckDB's query optimization process.**

A: DuckDB's optimizer performs:
1. **Parsing**: SQL to AST
2. **Binding**: Resolve table/column names
3. **Logical Planning**: Generate logical operators
4. **Cost-based Optimization**: Reorder joins, push predicates
5. **Physical Planning**: Convert to physical operators
6. **Code Generation**: Compile query execution

**Q32: How does predicate pushdown improve performance?**

A: Predicate pushdown moves filter conditions as close to the data source as possible. For example, when querying a Parquet file:

```sql
SELECT * FROM read_parquet('sales.parquet') WHERE store_id = 'ST001';
```

DuckDB reads only the `store_id` column and filters rows, avoiding reading the entire file.

**Q33: What is the difference between OLAP and OLTP?**

| Aspect | OLAP | OLTP |
|--------|------|------|
| Purpose | Analytical queries | Transaction processing |
| Data size | Historical, large | Current, small |
| Queries | Complex aggregations | Simple inserts/updates |
| Response time | Seconds to minutes | Milliseconds |
| Data model | Star/Snowflake | Normalized |

**Q34: How do you optimize a slow GROUP BY query?**

1. Ensure columns used in GROUP BY are indexed
2. Use appropriate data types (avoid VARCHAR for grouping if possible)
3. Pre-aggregate data in materialized views
4. Consider using APPROX_COUNT_DISTINCT for large datasets
5. Enable parallel execution with proper thread settings

```sql
-- Use parallel execution
SET threads TO 8;

-- Use approximate counts for very large datasets
SELECT APPROX_COUNT_DISTINCT(customer_id) FROM huge_table;
```

**Q35: What is the Arrow integration with DuckDB?**

A: DuckDB has native Apache Arrow support for zero-copy data exchange:

```python
import pyarrow as pa

# Export to Arrow
arrow_table = con.execute("SELECT * FROM sales").arrow()

# Export to pandas (uses Arrow under the hood)
df = con.execute("SELECT * FROM sales").df()

# Zero-copy from pandas
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3]})
con.execute("CREATE TABLE sales AS SELECT * FROM df")
```

**Q36: How do Iceberg tables work in DuckDB?**

```sql
INSTALL iceberg;
LOAD iceberg;

-- Query Iceberg table
SELECT * FROM iceberg('s3://bucket/table/metadata.json');

-- Query with partition filter
SELECT * FROM iceberg('s3://bucket/table', version=5);
```

**Q37: What is the pg_catalog integration?**

A: DuckDB provides PostgreSQL-compatible system catalogs:

```sql
-- Information schema
SELECT * FROM information_schema.tables;
SELECT * FROM information_schema.columns WHERE table_name = 'sales';

-- DuckDB-specific
SELECT * FROM duckdb_tables();
SELECT * FROM duckdb_columns();
SELECT * FROM duckdb_indexes();
```

**Q38: How do you implement incremental data loading?**

```python
class IncrementalLoader:
    def __init__(self, con, table_name):
        self.con = con
        self.table_name = table_name
    
    def get_last_update(self):
        result = self.con.execute(f"""
            SELECT MAX(updated_at) FROM {self.table_name}
        """).fetchone()
        return result[0] if result[0] else '1970-01-01'
    
    def load_incremental(self, source_query, key_column):
        last_key = self.con.execute(f"""
            SELECT MAX({key_column}) FROM {self.table_name}
        """).fetchone()[0]
        
        if last_key:
            return self.con.execute(f"""
                {source_query} WHERE {key_column} > '{last_key}'
            """).df()
        return self.con.execute(source_query).df()
```

**Q39: How do you handle schema evolution in DuckDB?**

```python
# Add column
con.execute("ALTER TABLE sales ADD COLUMN discount_percent DOUBLE");

# Rename column
con.execute("ALTER TABLE sales RENAME COLUMN discount_percent TO discount");

# Drop column
con.execute("ALTER TABLE sales DROP COLUMN old_column");

# Change column type
con.execute("ALTER TABLE sales ALTER revenue TYPE DOUBLE");
```

**Q40: What is the difference between DISTINCT and GROUP BY for deduplication?**

- `GROUP BY` is more flexible and can be combined with aggregations
- `DISTINCT` is simpler for removing duplicates
- Performance is similar for simple cases

```sql
-- Both return unique stores
SELECT DISTINCT store_id FROM sales;
SELECT store_id FROM sales GROUP BY store_id;

-- GROUP BY can do more
SELECT store_id, COUNT(*) as cnt FROM sales GROUP BY store_id;
```

**Q41: How do you implement row-level security?**

```sql
-- Create policy based on user context
CREATE TABLE sales (
    store_id VARCHAR,
    revenue DECIMAL(10,2)
);

CREATE POLICY store_isolation ON sales
USING (store_id = current_setting('app.current_store_id'));
```

**Q42: What are the best practices for Parquet file sizes?**

A: Optimal Parquet configuration:
- Row group size: 100K-1M rows
- File size: 100MB-10GB
- Compression: ZSTD or Snappy
- Use `COPY` with compression:

```sql
COPY sales TO 'sales.parquet' (
    FORMAT PARQUET,
    COMPRESSION 'zstd',
    ROW_GROUP_SIZE 100000
);
```

**Q43: How does DuckDB handle concurrent access?**

A: DuckDB uses:
- File-based locking for concurrent connections
- MVCC (Multi-Version Concurrency Control) for transactions
- Writer-preferring mode by default

```python
# Multiple read connections
con1 = duckdb.connect('retail.db', read_only=True)
con2 = duckdb.connect('retail.db', read_only=True)

# Single writer
con_writer = duckdb.connect('retail.db')
```

**Q44: How do you tune DuckDB for read-heavy workloads?**

```python
con = duckdb.connect('retail.db', config={
    'max_memory': '8GB',
    'threads': 8,
})

# Enable cache
con.execute("SET enable_cache = true")

# Create covering indexes for common queries
con.execute("CREATE INDEX idx_covering ON sales(store_id, transaction_time, revenue)")
```

**Q45: What is the difference between lazy and eager execution?**

- **Lazy**: Expressions are not evaluated until materialization is needed
- **Eager**: Expressions are evaluated immediately

DuckDB uses lazy execution for optimization:

```python
# This doesn't execute until you fetch
rel = con.sql("SELECT * FROM sales WHERE revenue > 100")
filtered = rel.filter("store_id = 'ST001'")  # Still not executed
result = filtered.df()  # Now it executes
```

**Q46: How do you debug query performance issues?**

```sql
-- Step 1: Get query plan
EXPLAIN ANALYZE SELECT ...;

-- Step 2: Check statistics
SELECT * FROM duckdb.table_statistics('sales');

-- Step 3: Check for missing indexes
SELECT * FROM duckdb_indexes() WHERE table_name = 'sales';

-- Step 4: Profile specific operators
PRAGMA enable_profiling;
PRAGMA profile_output = '/tmp/profile.json';
```

**Q47: What is the difference between a sequence and auto-increment?**

```sql
-- Sequence (PostgreSQL-style)
CREATE SEQUENCE customer_id_seq START 1;
INSERT INTO customers VALUES (nextval('customer_id_seq'), 'John');

-- DuckDB doesn't have AUTOINCREMENT, use DEFAULT
CREATE TABLE customers (
    id INTEGER DEFAULT nextval('customer_id_seq'),
    name VARCHAR
);
```

**Q48: How do you implement slowly changing dimensions?**

```sql
-- Type 2 SCD: Add effective date ranges
ALTER TABLE dim_products ADD COLUMN effective_from TIMESTAMP;
ALTER TABLE dim_products ADD COLUMN effective_to TIMESTAMP;
ALTER TABLE dim_products ADD COLUMN is_current BOOLEAN;

-- Insert new version
INSERT INTO dim_products 
SELECT *, CURRENT_TIMESTAMP, NULL, true 
FROM products WHERE product_id = 'P001';

-- Update previous version
UPDATE dim_products 
SET effective_to = CURRENT_TIMESTAMP, is_current = false
WHERE product_id = 'P001' AND is_current = true;
```

**Q49: What is the difference between LATERAL JOIN and normal JOIN?**

```sql
-- LATERAL allows correlated subqueries in FROM
SELECT 
    s.store_id,
    daily.total_revenue
FROM stores s,
LATERAL (
    SELECT SUM(revenue) as total_revenue
    FROM sales
    WHERE store_id = s.store_id
    AND transaction_time >= CURRENT_DATE - INTERVAL '30 days'
) daily;
```

**Q50: How do you handle timezone-aware timestamps?**

```sql
-- Create timestamp with timezone
CREATE TABLE sales (
    sale_time TIMESTAMPTZ
);

-- Store in UTC, convert on display
SELECT 
    sale_time,
    sale_time AT TIME ZONE 'America/New_York' as ny_time
FROM sales;
```

**Q51: What is the performance impact of NULL values?**

A: NULLs have minimal performance impact in DuckDB due to:
- Bit-packed null indicators
- Vectorized processing handles nulls efficiently
- Use `WHERE col IS NOT NULL` when you don't need NULL handling

**Q52: How do you implement a custom aggregate function?**

```python
from duckdb import AggregateFunction

class ModeAggregate(AggregateFunction):
    name = "mode"
    
    def state(self, input, state):
        # Count occurrences
        return state
    
    def combine(self, state1, state2):
        return state1 + state2
    
    def finalize(self, state):
        return max(state, key=state.get)

# Register and use
con.create_function("mode", ModeAggregate())
```

**Q53: What is the difference between RANGE and ROWS in window frames?**

```sql
-- ROWS: Physical rows
SELECT 
    day,
    revenue,
    SUM(revenue) OVER (
        ORDER BY day 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as rolling_3d
FROM daily_sales;

-- RANGE: Logical range of values
SELECT 
    day,
    revenue,
    SUM(revenue) OVER (
        ORDER BY day 
        RANGE BETWEEN INTERVAL '2 days' PRECEDING AND CURRENT ROW
    ) as rolling_3d_range
FROM daily_sales;
```

**Q54: How do you optimize LIKE queries?**

```sql
-- Use prefix matching when possible
LIKE 'ST001%'  -- Can use index
LIKE '%001'    -- Cannot use index (suffix)

-- For complex patterns, consider full-text search
-- or prefix trie indexes
```

**Q55: What is the duckdb_storage extension?**

```sql
-- Check storage info
SELECT * FROM duckdb_storage_info('retail.db');

-- Get table storage statistics
SELECT * FROM duckdb_table_storage_info('sales');
```

**Q56: How do you handle data skew in aggregations?**

```sql
-- If some stores have much more data
-- Option 1: Pre-aggregate at store level
WITH store_agg AS (
    SELECT store_id, DATE_TRUNC('day', t) as day, SUM(revenue) as rev
    FROM sales GROUP BY 1, 2
)
SELECT day, SUM(rev) FROM store_agg GROUP BY 1;

-- Option 2: Use parallel aggregation hints
PRAGMA force_index_join;
```

**Q57: What is the difference between merge and append join strategies?**

```sql
-- Configure join strategy
SET join_strategy = 'merge';  -- or 'hash', 'nested_loop'
```

**Q58: How do you use DuckDB with pandas efficiently?**

```python
# Method 1: SQL to pandas
df = con.execute("SELECT * FROM sales").df()

# Method 2: Register pandas as table
con.execute("CREATE TABLE sales AS SELECT * FROM df")

# Method 3: Use DuckDB's native functions for pandas
con.execute("SELECT * FROM df WHERE revenue > 100")
```

**Q59: What is the Parquet row group size impact?**

A: Row group size affects parallelization:
- Smaller groups (< 5K rows): Poor performance
- Medium groups (5K-100K): Suboptimal
- Large groups (100K-1M): Optimal
- Above 1M: Marginal gains

**Q60: How do you migrate from SQLite to DuckDB?**

```python
import sqlite3
import duckdb

# Read SQLite data
sqlite_con = sqlite3.connect('old.db')
df = sqlite_con.execute('SELECT * FROM sales').df()
sqlite_con.close()

# Write to DuckDB
duckdb_con = duckdb.connect('new.db')
duckdb_con.execute('CREATE TABLE sales AS SELECT * FROM df')
```

---

### 13.3 Advanced Questions (30)

**Q61: How does DuckDB's vectorized execution engine work internally?**

A: DuckDB's execution engine:
1. **Vector Batch**: Each operator processes vectors of 2048 rows
2. **Columnar Layout**: Data stored column-wise for cache efficiency
3. **SIMD Operations**: CPU vector instructions process entire vectors
4. **Code Generation**: Query plans compiled to optimized machine code
5. **Pipeline Breaking**: Materialization only when necessary

```mermaid
flowchart TD
    subgraph "Vector Processing"
        V1["Vector 1: [v1, v2, ..., v2048]"]
        V2["Vector 2: [v1, v2, ..., v2048]"]
    end
    
    subgraph "Operators"
        F["Filter"]
        G["GroupBy"]
        A["Aggregate"]
    end
    
    V1 --> F --> G --> A
```

**Q62: Explain DuckDB's cost-based optimizer architecture.**

A: The optimizer:
1. **Rule-based optimizations**: Constant folding, predicate pushdown
2. **Cost model**: Estimates CPU/IO costs for each plan
3. **Join reordering**: Considers different join orders
4. **Statistics**: Uses table/column statistics for cardinality estimation
5. **Plan enumeration**: Explores plan space with memoization

**Q63: How do you implement a custom DuckDB extension?**

```cpp
// extension.cpp
#include "duckdb.hpp"

namespace duckdb {

void LoadInternal(DuckDB &db) {
    db.extension->RegisterFunction("my_function", my_function_impl);
}

}

extern "C" {
void* entrypoint(void *ref) {
    return new duckdb::Extension("my_extension", LoadInternal);
}
}
```

```python
# Install and load
con.execute("INSTALL 'extension.duckdb_extension';")
con.execute("LOAD 'extension';")
```

**Q64: What is DuckDB's approach to query compilation?**

A: DuckDB uses:
1. **Expression JIT**: Compile expressions to native code
2. **Vector JIT**: Generate specialized vector operations
3. **Adaptive Execution**: Re-optimize based on runtime feedback

```sql
-- Enable JIT compilation
SET enable_jit = true;
SET jit_level = 'O3';
```

**Q65: How does DuckDB handle out-of-memory situations?**

```python
# Configure memory limits
con = duckdb.connect(config={
    'max_memory': '4GB',
    'temp_directory': '/path/to/spill',  # Enable disk spilling
})

# DuckDB automatically spills to temp_directory when memory exceeded
```

**Q66: Explain DuckDB's transaction isolation levels.**

A: DuckDB supports:
- **Read Committed**: Default, consistent reads within transactions
- **Serializable**: Full serializability (slower)
- **Snapshot Isolation**: Consistent snapshot per transaction

```sql
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT * FROM sales;
COMMIT;
```

**Q67: How do you implement exactly-once semantics with DuckDB?**

```python
class ExactlyOnceProcessor:
    def __init__(self, con):
        self.con = con
        self._init_checkpoint_table()
    
    def _init_checkpoint_table(self):
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                job_id VARCHAR,
                processed_until TIMESTAMP,
                PRIMARY KEY (job_id)
            )
        """)
    
    def process(self, job_id, data_df):
        # Get checkpoint
        checkpoint = self.con.execute("""
            SELECT processed_until FROM checkpoints WHERE job_id = ?
        """, params=[job_id]).fetchone()
        
        start_time = checkpoint[0] if checkpoint else '1970-01-01'
        
        # Process only new data
        new_data = data_df[data_df['timestamp'] > start_time]
        
        if len(new_data) > 0:
            # Process
            self._do_process(new_data)
            
            # Update checkpoint
            max_time = new_data['timestamp'].max()
            self.con.execute("""
                INSERT OR REPLACE INTO checkpoints VALUES (?, ?)
            """, params=[job_id, max_time])
```

**Q68: What is the difference between physical and logical replication?**

A: DuckDB doesn't have built-in replication. For enterprise use:
- **Logical**: Export/import using Parquet files
- **Physical**: File-level backup/restore
- **Custom**: Implement using change data capture

**Q69: How does DuckDB's optimizer handle correlated subqueries?**

A: DuckDB decorrelates subqueries when possible:
```sql
-- May be decorrelated
SELECT * FROM sales s
WHERE EXISTS (SELECT 1 FROM products p WHERE p.id = s.product_id);

-- Gets rewritten to join
SELECT DISTINCT s.* FROM sales s
JOIN products p ON p.id = s.product_id;
```

**Q70: What is the performance implication of different join algorithms?**

| Algorithm | Best For | Complexity |
|-----------|----------|------------|
| Hash Join | Large tables | O(n) memory |
| Merge Join | Pre-sorted data | O(n log n) |
| Nested Loop | Small tables | O(n*m) |

**Q71: How do you tune DuckDB for geospatial workloads?**

```sql
LOAD spatial;

-- Create spatial index
CREATE INDEX idx_spatial ON stores USING RTREE(geometry);

-- Spatial query
SELECT s.*, st.geometry 
FROM sales s, stores st
WHERE ST_Contains(st.geometry, ST_Point(s.lon, s.lat));
```

**Q72: What is DuckDB's approach to approximate query processing?**

```sql
-- Use APPROX functions for massive datasets
SELECT 
    APPROX_COUNT_DISTINCT(customer_id),
    APPROX_QUANTILE(revenue, 0.5),
    APPROX_Mean(revenue)
FROM huge_sales;

-- For large GROUP BY, use sampling
SELECT store_id, SUM(revenue) * 100
FROM (SELECT * FROM sales USING SAMPLE 1 PERCENT)
GROUP BY store_id;
```

**Q73: How do you implement time-travel queries?**

```sql
-- Use backup/restore for historical versions
-- Create timestamped backup
BACKUP DATABASE TO 'backup_2024_01_01.duckdb';

-- Query historical data
ATTACH 'backup_2024_01_01.duckdb' AS history;
SELECT * FROM history.sales AS OF '2024-01-01';
```

**Q74: What is the difference between pushdown and pullup optimization?**

- **Pushdown**: Move operations closer to data source
- **Pullup**: Move operations higher in the plan

DuckDB uses both: filters pushed down, aggregations pulled up.

**Q75: How does DuckDB handle data type coercion?**

```sql
-- Implicit coercion
SELECT 1 + '1';  -- Works, returns 2

-- Explicit cast
SELECT CAST('2024-01-01' AS DATE);

-- Try cast (returns NULL on failure)
SELECT TRY_CAST('not a date' AS DATE);  -- Returns NULL
```

**Q76: What is the impact of statistics on query planning?**

A: DuckDB maintains statistics for:
- Row counts
- Null counts
- Min/Max values
- Histograms

```sql
-- Update statistics
ANALYZE sales;

-- Check statistics
SELECT * FROM duckdb_table_statistics('sales');
```

**Q77: How do you implement custom scan operators?**

```python
# Custom function scanning
con.create_view("custom_scan", my_custom_scan_function)

# Register Python scan function
@duckdb.scalar_function
def custom_scan(path):
    # Custom file parsing logic
    return parse_custom_format(path)
```

**Q78: What is the difference between streaming and materialized execution?**

A: DuckDB uses:
- **Streaming**: Continuous data flow through operators (pipelined)
- **Materialized**: Entire intermediate result stored (blocks pipeline)

**Q79: How do you handle schema drift in ETL pipelines?**

```python
class SchemaDriftHandler:
    def __init__(self, con):
        self.con = con
    
    def auto_migrate(self, table_name, new_df):
        # Get current schema
        current = self.con.execute(f"DESCRIBE {table_name}").df()
        
        # Get new schema
        new_schema = pd.DataFrame({
            'column_name': new_df.columns,
            'column_type': [str(t) for t in new_df.dtypes]
        })
        
        # Add missing columns
        for _, row in new_schema.iterrows():
            if row['column_name'] not in current['column_name'].values:
                self.con.execute(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN {row['column_name']} {row['column_type']}
                """)
```

**Q80: Explain DuckDB's memory allocator design.**

A: DuckDB uses:
1. **Custom allocator**: Respects cache hierarchy
2. **Data frame allocator**: Batch allocation for vectors
3. **Temporary allocator**: For intermediate results
4. **Set_needle allocator**: Small object optimization

**Q81: How do you optimize for Append-only workloads?**

```python
# Use append-only optimizations
con.execute("SET cache_temperature TO 'cold'")

# For streaming data, batch inserts
batch_size = 10000
for batch in chunks(large_df, batch_size):
    con.execute("INSERT INTO sales SELECT * FROM batch")
```

**Q82: What is the performance impact of VARCHAR vs INTEGER keys?**

A: INTEGER keys are significantly faster:
- 4 bytes vs variable (20+ bytes average for UUIDs)
- Faster hashing, sorting, joining
- Better cache utilization

**Q83: How does DuckDB handle CPU cache efficiency?**

A: DuckDB optimizes cache usage:
- Vector size matches L1/L2 cache
- Columnar storage for sequential access
- Prefetching for predictable access patterns
- Cache-conscious hash tables

**Q84: What is the difference between graceful and forceful shutdown?**

```python
# Graceful: Checkpoint and close
con.execute("CHECKPOINT")
con.close()

# Forceful: May lose uncommitted data
import os
os.kill(pid, 9)  # Not recommended
```

**Q85: How do you implement hot reload of configuration?**

```python
# Reload without restart
con.execute("SET max_memory TO '8GB'")
con.execute("SET threads TO 4")

# Check current settings
settings = con.execute("SELECT * FROM duckdb_settings()").df()
```

**Q86: What is the impact of parallel degree on memory usage?**

A: Higher parallelism:
- More threads = more memory (each thread has own state)
- Better CPU utilization
- Diminishing returns after CPU saturation

```python
# Calculate optimal threads
import os
optimal_threads = os.cpu_count()

# But limit memory per thread
memory_per_thread = "1GB"
total_memory = f"{optimal_threads}GB"
```

**Q87: How do you implement custom compression?**

```sql
-- Use custom compression for specific columns
CREATE TABLE sensitive_data (
    id INTEGER,
    data BLOB COMPRESSION 'zstd'
);

-- Or use encrypted columns
CREATE TABLE secrets (
    api_key VARCHAR ENCRYPTION 'aes'
);
```

**Q88: What is DuckDB's approach to query cancellation?**

```python
import threading

# Long-running query with cancellation
cancel_event = threading.Event()

def run_query():
    con.execute("SELECT * FROM huge_table", cancel=event)

def cancel_query():
    cancel_event.set()

# Thread runs query, main thread can cancel
```

**Q89: How do you handle very wide tables (100+ columns)?**

```sql
-- Query only needed columns (projection pushdown)
SELECT col1, col2, col50 FROM wide_table;

-- Or create columnar subset
CREATE TABLE subset AS 
SELECT col1, col2, col50 FROM wide_table;
```

**Q90: What is the difference between EXPLAIN and EXPLAIN ANALYZE?**

- `EXPLAIN`: Shows planned operators with estimated costs
- `EXPLAIN ANALYZE`: Executes query and shows actual runtime statistics

---

### 13.4 Scenario-Based Questions (20)

**Q91: You have a 100GB Parquet file. How do you query it efficiently?**

A: 
```python
# 1. Use predicate pushdown - only read needed columns
result = con.sql("""
    SELECT store_id, SUM(revenue)
    FROM 'sales_100gb.parquet'
    WHERE transaction_date >= '2024-01-01'
    GROUP BY store_id
""").df()

# 2. Ensure Parquet has proper row groups
# If not, repartition first
con.execute(f"""
    COPY (SELECT * FROM 'sales_100gb.parquet')
    TO 'sales_repartitioned/'
    (FORMAT PARQUET, PER_THREAD_OUTPUT, ROW_GROUP_SIZE 100000)
""")

# 3. Use parallel reading
con.execute("SET threads TO 8")
```

**Q92: Your dashboard query takes 30 seconds. How do you optimize it?**

A:
```python
# Step 1: Analyze query plan
plan = con.execute("EXPLAIN ANALYZE <slow_query>").df()

# Step 2: Common optimizations
# - Create materialized view
con.execute("""
    CREATE MATERIALIZED VIEW dashboard_metrics AS
    SELECT 
        DATE_TRUNC('hour', transaction_time) as hour,
        store_id,
        SUM(revenue) as revenue,
        COUNT(*) as transactions
    FROM fact_transactions
    GROUP BY 1, 2
""")

# - Add indexes
con.execute("CREATE INDEX idx_hour ON fact_transactions(transaction_time)")

# - Use pre-aggregated table
# Refresh hourly
```

**Q93: How do you implement real-time dashboards with DuckDB?**

A:
```python
class RealTimeDashboard:
    def __init__(self):
        self.con = duckdb.connect("realtime.db")
        self._init_schema()
    
    def _init_schema(self):
        # Pre-aggregate table
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS hourly_rollup (
                hour TIMESTAMP,
                store_id VARCHAR,
                revenue DECIMAL(12,2),
                units INTEGER,
                transactions INTEGER,
                PRIMARY KEY (hour, store_id)
            )
        """)
    
    def process_streaming_data(self, batch_df):
        # Upsert new data
        self.con.execute("""
            INSERT INTO hourly_rollup 
            SELECT 
                DATE_TRUNC('hour', transaction_time),
                store_id,
                SUM(revenue),
                SUM(quantity),
                COUNT(*)
            FROM batch_df
            GROUP BY 1, 2
            ON CONFLICT(hour, store_id) DO UPDATE SET
                revenue = hourly_rollup.revenue + excluded.revenue,
                units = hourly_rollup.units + excluded.units,
                transactions = hourly_rollup.transactions + excluded.transactions
        """)
    
    def get_dashboard_data(self, store_id):
        return self.con.execute("""
            SELECT * FROM hourly_rollup
            WHERE store_id = ?
            ORDER BY hour DESC
            LIMIT 168
        """, params=[store_id]).df()
```

**Q94: How do you migrate a 10TB data warehouse to use DuckDB?**

A: Phased approach:
```python
class MigrationManager:
    def __init__(self, source_conn, target_conn):
        self.source = source_conn
        self.target = target_conn
    
    def migrate_in_chunks(self, table, chunk_size=1000000):
        # Get total rows
        total = self.source.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        
        for offset in range(0, total, chunk_size):
            # Extract chunk
            chunk = self.source.execute(f"""
                SELECT * FROM {table}
                LIMIT {chunk_size} OFFSET {offset}
            """).df()
            
            # Export to Parquet
            chunk.to_parquet(f'/tmp/migration/{table}_{offset}.parquet')
            
            # Load to DuckDB
            self.target.execute(f"""
                COPY (SELECT * FROM '/tmp/migration/{table}_{offset}.parquet')
                TO '/tmp/duckdb/{table}'
                (FORMAT PARQUET, APPEND)
            """)
            
            print(f"Migrated {min(offset + chunk_size, total)}/{total}")
    
    def validate_migration(self):
        # Compare row counts
        source_count = self.source.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        target_count = self.target.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        
        assert source_count == target_count
        
        # Compare sums
        source_sum = self.source.execute("SELECT SUM(revenue) FROM sales").fetchone()[0]
        target_sum = self.target.execute("SELECT SUM(revenue) FROM sales").fetchone()[0]
        
        assert abs(source_sum - target_sum) < 0.01
```

**Q95: Your ETL pipeline is bottlenecked. How do you diagnose?**

A:
```python
# 1. Profile the pipeline
import time

stages = ['extract', 'transform', 'load']

for stage in stages:
    start = time.time()
    getattr(self, f'do_{stage}')()
    elapsed = time.time() - start
    
    print(f"{stage}: {elapsed:.2f}s")

# 2. Common bottlenecks and solutions:
# - Slow extraction: Increase parallelism, use batch reads
# - Slow transformation: Vectorize operations, reduce data movement
# - Slow loading: Use COPY command, disable indexes, batch inserts
```

**Q96: How do you implement ACID compliance for financial transactions?**

A:
```python
class FinancialTransaction:
    def __init__(self, con):
        self.con = con
    
    def transfer(self, from_account, to_account, amount):
        # Use serializable isolation
        with self.con.cursor() as cur:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            
            try:
                # Debit source
                cur.execute("""
                    UPDATE accounts 
                    SET balance = balance - ?
                    WHERE account_id = ? AND balance >= ?
                """, params=[amount, from_account, amount])
                
                if cur.rowcount == 0:
                    raise ValueError("Insufficient funds")
                
                # Credit destination
                cur.execute("""
                    UPDATE accounts 
                    SET balance = balance + ?
                    WHERE account_id = ?
                """, params=[amount, to_account])
                
                # Record transaction
                cur.execute("""
                    INSERT INTO transactions VALUES (?, ?, ?, ?)
                """, params=[from_account, to_account, amount, datetime.now()])
                
                cur.execute("COMMIT")
                
            except Exception as e:
                cur.execute("ROLLBACK")
                raise
```

**Q97: How do you handle late-arriving data in aggregations?**

A:
```python
class LateArrivingDataHandler:
    def __init__(self, con):
        self.con = con
        self.watermark = None
    
    def process_batch(self, batch_df, event_time_col='event_time'):
        # Calculate watermark (e.g., 1 day late tolerance)
        max_event_time = batch_df[event_time_col].max()
        new_watermark = max_event_time - timedelta(days=1)
        
        if self.watermark is None:
            self.watermark = new_watermark
        
        # Get late-arriving data (before watermark)
        late_data = batch_df[batch_df[event_time_col] < self.watermark]
        on_time_data = batch_df[batch_df[event_time_col] >= self.watermark]
        
        if len(late_data) > 0:
            # Recalculate affected aggregations
            self._recalculate(late_data, event_time_col)
        
        # Insert on-time data
        self._insert(on_time_data)
        
        self.watermark = new_watermark
    
    def _recalculate(self, late_data, event_time_col):
        # Delete old aggregates
        affected_hours = late_data[event_time_col].dt.floor('H').unique()
        for hour in affected_hours:
            self.con.execute(f"""
                DELETE FROM hourly_aggregates WHERE hour = '{hour}'
            """)
        
        # Recalculate from source
        self.con.execute(f"""
            INSERT INTO hourly_aggregates
            SELECT DATE_TRUNC('hour', event_time), SUM(value)
            FROM fact_data
            WHERE DATE_TRUNC('hour', event_time) = '{hour}'
            GROUP BY 1
        """)
```

**Q98: Your DuckDB crashes under memory pressure. How do you prevent this?**

A:
```python
class MemorySafeProcessor:
    def __init__(self, max_memory='2GB'):
        self.max_memory = max_memory
        self.con = duckdb.connect(config={
            'max_memory': max_memory,
            'temp_directory': '/path/to/spill',
        })
    
    def safe_aggregate(self, query):
        # Check available memory
        stats = self.con.execute("""
            SELECT 
                {max_memory} - current_memory_usage() as available
        """).fetchone()
        
        if stats[0] < 1024 * 1024 * 1024:  # Less than 1GB
            # Process in chunks
            return self._chunked_aggregate(query)
        
        return self.con.execute(query).df()
    
    def _chunked_aggregate(self, query):
        results = []
        for chunk in self._get_chunks():
            chunk_result = self.con.execute(query, params=[chunk])
            results.append(chunk_result)
        
        return pd.concat(results)
```

**Q99: How do you implement a slowly changing dimension Type 2?**

A:
```sql
-- SCD Type 2: Full history tracking
CREATE TABLE dim_products_scd2 (
    product_key SERIAL,
    product_id VARCHAR,
    product_name VARCHAR,
    category VARCHAR,
    effective_from TIMESTAMP,
    effective_to TIMESTAMP,
    is_current BOOLEAN,
    version INTEGER
);

-- Insert new version
CREATE OR REPLACE FUNCTION insert_product_scd2(product_row)
AS $$
    -- Expire current version
    UPDATE dim_products_scd2 
    SET effective_to = CURRENT_TIMESTAMP, 
        is_current = false
    WHERE product_id = product_row.product_id 
      AND is_current = true;
    
    -- Insert new version
    INSERT INTO dim_products_scd2 VALUES (
        DEFAULT,
        product_row.*,
        CURRENT_TIMESTAMP,
        NULL,
        true,
        (SELECT COALESCE(MAX(version), 0) + 1 
         FROM dim_products_scd2 
         WHERE product_id = product_row.product_id)
    );
$$ LANGUAGE SQL;
```

**Q100: How do you audit data changes in DuckDB?**

A:
```python
class AuditLogger:
    def __init__(self, con):
        self.con = con
        self._init_audit_table()
    
    def _init_audit_table(self):
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                audit_id BIGSERIAL,
                table_name VARCHAR,
                operation VARCHAR,
                old_values JSON,
                new_values JSON,
                changed_by VARCHAR,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def log_change(self, table, operation, old_row, new_row, user):
        self.con.execute("""
            INSERT INTO audit_log 
            (table_name, operation, old_values, new_values, changed_by)
            VALUES (?, ?, ?, ?, ?)
        """, params=[
            table, 
            operation,
            json.dumps(old_row) if old_row else None,
            json.dumps(new_row) if new_row else None,
            user
        ])
    
    def get_history(self, table, primary_key):
        return self.con.execute("""
            SELECT * FROM audit_log
            WHERE table_name = ?
              AND new_values->>'id' = ?
            ORDER BY changed_at DESC
        """, params=[table, primary_key]).df()
```

**Q101: How do you implement a incremental materialized view?**

A:
```python
class IncrementalMaterializedView:
    def __init__(self, con, name, definition, key_columns):
        self.con = con
        self.name = name
        self.definition = definition
        self.key_columns = key_columns
        self.last_refresh = None
    
    def refresh(self, source_table):
        if self.last_refresh is None:
            # Full refresh
            self.con.execute(f"""
                CREATE OR REPLACE TABLE {self.name} AS {self.definition}
            """)
        else:
            # Incremental refresh
            # Delete changed rows
            self.con.execute(f"""
                DELETE FROM {self.name}
                WHERE EXISTS (
                    SELECT 1 FROM ({self.definition}) new
                    WHERE {" AND ".join(f"{self.name}.{k} = new.{k}" for k in self.key_columns)}
                )
            """)
            
            # Insert updated rows
            self.con.execute(f"""
                INSERT INTO {self.name}
                SELECT * FROM ({self.definition}) new
                WHERE EXISTS (
                    SELECT 1 FROM {source_table} src
                    WHERE {" AND ".join(f"src.{k} = new.{k}" for k in self.key_columns)}
                      AND src.updated_at > '{self.last_refresh}'
                )
            """)
        
        self.last_refresh = datetime.now()
```

**Q102: Your Parquet files have different schemas. How do you handle this?**

A:
```python
class SchemaEvolutionHandler:
    def __init__(self, con):
        self.con = con
    
    def auto_union(self, file_paths):
        """Automatically handle schema differences in Parquet files."""
        # Collect all schemas
        schemas = []
        for path in file_paths:
            schema = self.con.execute(f"""
                SELECT * FROM '{path}' WHERE 1=0
            """).description
            schemas.append(set(c[0] for c in schema))
        
        # Get union of all columns
        all_columns = set.union(*schemas)
        
        # Read each file and fill missing columns with NULL
        for path in file_paths:
            file_schema = self.con.execute(f"DESCRIBE SELECT * FROM '{path}'").df()
            
            missing = all_columns - set(file_schema['column_name'])
            if missing:
                # Create view with NULL columns
                cols = ', '.join(f'"{c}"' for c in file_schema['column_name'])
                for col in missing:
                    cols += f', NULL as "{col}"'
                
                self.con.execute(f"""
                    CREATE VIEW extended AS 
                    SELECT {cols} FROM '{path}'
                """)
            else:
                self.con.execute(f"CREATE VIEW extended AS SELECT * FROM '{path}'")
        
        # Union all
        return self.con.execute("SELECT * FROM extended UNION ALL").df()
```

**Q103: How do you implement row-level security for multi-tenant data?**

A:
```python
class MultiTenantSecurity:
    def __init__(self, con):
        self.con = con
        self.current_tenant = None
    
    def set_tenant(self, tenant_id):
        self.current_tenant = tenant_id
        self.con.execute(f"SET CURRENT_TENANT = '{tenant_id}'")
    
    def execute_tenant_query(self, query):
        if self.current_tenant is None:
            raise ValueError("Tenant not set")
        
        # Automatically add tenant filter
        # This would need custom query parsing for production
        tenant_filtered = f"""
            WITH tenant_data AS (
                SELECT * FROM ({query}) t
                WHERE tenant_id = '{self.current_tenant}'
            )
            SELECT * FROM tenant_data
        """
        
        return self.con.execute(tenant_filtered).df()
```

**Q104: How do you backfill historical data efficiently?**

A:
```python
class HistoricalBackfill:
    def __init__(self, con):
        self.con = con
        self.checkpoint_table = 'backfill_checkpoints'
    
    def backfill(self, target_table, source_query, 
                  date_column, start_date, end_date, batch_days=7):
        """Backfill data in configurable batches."""
        current = start_date
        
        while current < end_date:
            batch_end = current + timedelta(days=batch_days)
            
            # Check if already done
            checkpoint = self.con.execute(f"""
                SELECT status FROM {self.checkpoint_table}
                WHERE date_range = ?
            """, params=[(current, batch_end)]).fetchone()
            
            if checkpoint and checkpoint[0] == 'complete':
                current = batch_end
                continue
            
            try:
                # Process batch
                batch_query = f"""
                    {source_query}
                    WHERE {date_column} >= '{current}'
                      AND {date_column} < '{batch_end}'
                """
                
                # Delete existing
                self.con.execute(f"""
                    DELETE FROM {target_table}
                    WHERE {date_column} >= '{current}'
                      AND {date_column} < '{batch_end}'
                """)
                
                # Insert new
                self.con.execute(f"""
                    INSERT INTO {target_table}
                    {batch_query}
                """)
                
                # Mark complete
                self._save_checkpoint(current, batch_end, 'complete')
                
            except Exception as e:
                self._save_checkpoint(current, batch_end, f'failed: {e}')
                raise
            
            current = batch_end
    
    def _save_checkpoint(self, start, end, status):
        self.con.execute(f"""
            INSERT OR REPLACE INTO {self.checkpoint_table}
            VALUES (?, ?, ?)
        """, params=[str(start), str(end), status])
```

**Q105: How do you implement exactly-once delivery for streaming data?**

A:
```python
class ExactlyOnceStream:
    def __init__(self, con):
        self.con = con
        self._init_tables()
    
    def _init_tables(self):
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS processed_events (
                event_id VARCHAR PRIMARY KEY,
                processed_at TIMESTAMP,
                CHECKPOINT BIGINT
            )
        """)
    
    def process_event(self, event):
        event_id = event['id']
        
        # Idempotent check
        existing = self.con.execute("""
            SELECT 1 FROM processed_events WHERE event_id = ?
        """, params=[event_id]).fetchone()
        
        if existing:
            return None  # Already processed
        
        # Process with deduplication
        self.con.execute("""
            INSERT INTO processed_events VALUES (?, ?, ?)
        """, params=[event_id, datetime.now(), event.get('checkpoint')])
        
        return self._do_process(event)
    
    def reprocess(self, event_id):
        """Reprocess a specific event."""
        # Remove old record
        self.con.execute("""
            DELETE FROM processed_events WHERE event_id = ?
        """, params=[event_id])
        
        # Re-fetch and process
        event = self._fetch_event(event_id)
        return self.process_event(event)
```

---

### 13.5 Architecture Questions (20)

**Q106: When would you choose DuckDB over a data warehouse?**

A: Choose DuckDB when:
- Data is on local files (Parquet, CSV)
- No BI tool integration needed
- Need embedded analytics in application
- Team is Python-centric
- Data volume < 100TB
- Low latency requirements
- No complex multi-user concurrency needs

Choose Data Warehouse when:
- Need SQL client connectivity
- Team is SQL-centric
- Complex BI integrations
- Need enterprise features (governance, audit)
- Petabyte scale
- Multi-team access

**Q107: How would you scale DuckDB for large datasets?**

A: Scaling strategies:
```python
# 1. Vertical: Increase resources
con = duckdb.connect(config={
    'max_memory': '64GB',
    'threads': 16,
})

# 2. Partitioning: Split data by time/location
CREATE TABLE sales_partitioned (...) PARTITION BY RANGE (transaction_date);

# 3. Materialized views: Pre-compute expensive aggregations
CREATE MATERIALIZED VIEW monthly AS SELECT ... GROUP BY ...;

# 4. External aggregation: Spill large aggregations to disk
SET enable_external_aggregation = true;

# 5. Distributed: For petabyte scale, consider using 
#    - MotherDuck (cloud service)
#    - Co-operative queries across instances
```

**Q108: Design a real-time analytics architecture with DuckDB.**

A:
```mermaid
flowchart TD
    subgraph "Ingestion"
        KAFKA["Kafka"]
        FLINK["Flink Processor"]
    end
    
    subgraph "DuckDB Layer"
        STREAM["Stream Aggregator\n(Every 1 min)"]
        CACHE["Aggregation Cache\n(Materialized Views)"]
        ARCHIVE["Archive Storage\n(Parquet)"]
    end
    
    subgraph "Query Layer"
        API["FastAPI"]
        DASH["Grafana"]
    end
    
    KAFKA --> FLINK
    FLINK --> STREAM
    STREAM --> CACHE
    STREAM --> ARCHIVE
    CACHE --> API
    ARCHIVE --> DASH
```

**Q109: How does DuckDB fit in a lambda architecture?**

A:
```mermaid
flowchart LR
    subgraph "Speed Layer"
        KAFKA["Kafka"]
        FLINK["Flink"]
        DUCK_FAST["DuckDB\n(In-memory)"]
    end
    
    subgraph "Batch Layer"
        S3["S3"]
        SPARK["Spark"]
        DUCK_BATCH["DuckDB\n(Historical)"]
    end
    
    subgraph "Serving Layer"
        MERGE["Merge View"]
        QUERY["Query API"]
    end
    
    KAFKA --> FLINK --> DUCK_FAST
    S3 --> SPARK --> DUCK_BATCH
    DUCK_FAST & DUCK_BATCH --> MERGE --> QUERY
```

**Q110: What are the trade-offs between DuckDB and ClickHouse?**

| Aspect | DuckDB | ClickHouse |
|--------|--------|------------|
| Deployment | Embedded | Distributed cluster |
| Scaling | Vertical | Horizontal |
| SQL compatibility | PostgreSQL-like | Native |
| Performance | Excellent | Excellent |
| Operational overhead | None | High |
| Real-time inserts | Limited | Excellent |
| Use case | Embedded/ETL | Data warehouse |

**Q111: Design a data lakehouse with DuckDB.**

A:
```python
class LakehouseManager:
    """DuckDB as the analytics engine for a lakehouse."""
    
    def __init__(self, con):
        self.con = con
    
    def setup_lakehouse(self, base_path):
        # Bronze: Raw data
        self.con.execute(f"""
            CREATE TABLE bronze_sales AS 
            SELECT * FROM read_parquet('{base_path}/raw/sales/*.parquet')
        """)
        
        # Silver: Cleaned and standardized
        self.con.execute("""
            CREATE TABLE silver_sales AS
            SELECT 
                transaction_id,
                TRY_CAST(store_id AS VARCHAR) as store_id,
                TRY_CAST(revenue AS DOUBLE) as revenue,
                transaction_time
            FROM bronze_sales
            WHERE revenue > 0
        """)
        
        # Gold: Business-level aggregates
        self.con.execute("""
            CREATE TABLE gold_daily_sales AS
            SELECT 
                DATE_TRUNC('day', transaction_time) as date,
                store_id,
                SUM(revenue) as daily_revenue,
                COUNT(*) as transactions
            FROM silver_sales
            GROUP BY 1, 2
        """)
    
    def time_travel_query(self, table, as_of):
        """Query historical version of a table."""
        return self.con.execute(f"""
            SELECT * FROM {table} AS OF TIMESTAMP '{as_of}'
        """).df()
```

**Q112: How would you implement CDC (Change Data Capture) with DuckDB?**

A:
```python
class CDCHandler:
    """Handle CDC from various sources."""
    
    def __init__(self, con):
        self.con = con
    
    def apply_changes(self, changes_df, target_table, key_columns):
        """
        Apply CDC changes to target table.
        changes_df should have: operation (INSERT/UPDATE/DELETE), and all columns.
        """
        for _, change in changes_df.iterrows():
            op = change['operation']
            data = {k: v for k, v in change.items() if k not in ['operation']}
            
            if op == 'INSERT':
                self._insert(target_table, data)
            elif op == 'UPDATE':
                self._update(target_table, data, key_columns)
            elif op == 'DELETE':
                self._delete(target_table, data, key_columns)
    
    def _insert(self, table, data):
        cols = ', '.join(data.keys())
        vals = ', '.join(['?' for _ in data])
        self.con.execute(f"INSERT INTO {table} ({cols}) VALUES ({vals})", 
                        params=list(data.values()))
    
    def _update(self, table, data, key_columns):
        key_vals = {k: data[k] for k in key_columns}
        non_key = {k: v for k, v in data.items() if k not in key_columns}
        
        set_clause = ', '.join(f"{k} = ?" for k in non_key.keys())
        where_clause = ' AND '.join(f"{k} = ?" for k in key_columns)
        
        self.con.execute(f"""
            UPDATE {table} SET {set_clause} WHERE {where_clause}
        """, params=list(non_key.values()) + list(key_vals.values()))
```

**Q113: What is the role of DuckDB in a modern data stack?**

A:
```
┌─────────────────────────────────────────────────────────────────────┐
│                        Modern Data Stack                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐  │
│  │  Sources    │───▶│  Ingestion  │───▶│  Transformation Layer   │  │
│  │  (Apps, IoT)│    │  (Kafka,   │    │  (Flink, Spark, dbt)   │  │
│  └─────────────┘    │   CDC)     │    └───────────┬─────────────┘  │
│                     └─────────────┘                │               │
│                                                    ▼               │
│  ┌─────────────────────────────────────────────────────────────────┤
│  │                                                                 │
│  │    ┌─────────────────────────────────────────────────────────┐ │
│  │    │              DuckDB Analytics Layer                      │ │
│  │    │  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐   │ │
│  │    │  │ Embedded │  │ ETL/Pre-proc │  │ ML Feature Store  │   │ │
│  │    │  │ Analytics│  │ Acceleration │  │                   │   │ │
│  │    │  └──────────┘  └──────────────┘  └───────────────────┘   │ │
│  │    └─────────────────────────────────────────────────────────┘ │
│  │                            │                                    │
│  │                            ▼                                    │
│  │    ┌─────────────────────────────────────────────────────────┐ │
│  │    │              Downstream Systems                          │ │
│  │    │  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐   │ │
│  │    │  │ Data     │  │ Dashboards  │  │ ML Training       │   │ │
│  │    │  │ Warehouse│  │ & Reports   │  │                   │   │ │
│  │    │  └──────────┘  └──────────────┘  └───────────────────┘   │ │
│  │    └─────────────────────────────────────────────────────────┘ │
│  └─────────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────────┘
```

**Q114: How does DuckDB compare to using pandas for analytics?**

| Aspect | DuckDB | pandas |
|--------|--------|-------|
| Data size | Handles larger-than-memory | Limited to RAM |
| Query optimization | Yes | No |
| SQL support | Native | Via pandas |
| Parallelism | Automatic multi-core | Manual |
| Memory efficiency | Columnar, compressed | Row-based |
| Performance (large data) | 10-100x faster | Slows significantly |

**Q115: Design a multi-stage ETL pipeline using DuckDB.**

A:
```python
class ETLPipeline:
    """Multi-stage ETL with DuckDB."""
    
    def __init__(self, config):
        self.extraction = ExtractionStage(config)
        self.transformation = TransformationStage(config)
        self.loading = LoadingStage(config)
        self.quality = QualityChecks(config)
    
    def run(self):
        # Stage 1: Extract
        raw_data = self.extraction.extract_from_kafka()
        self.extraction.save_raw(raw_data)
        
        # Stage 2: Quality check
        self.quality.check_raw_data()
        
        # Stage 3: Transform
        transformed = self.transformation.clean(raw_data)
        enriched = self.transformation.enrich(transformed)
        aggregated = self.transformation.aggregate(enriched)
        
        # Stage 4: Load
        self.loading.load_to_warehouse(aggregated)
        self.loading.update_materialized_views()
        
        # Stage 5: Final quality
        self.quality.check_final_output()
        
        # Stage 6: Cleanup
        self.extraction.archive_raw_data()
        self.quality.send_notifications()

class ExtractionStage:
    def extract_from_kafka(self):
        # Read from Kafka topic
        return read_kafka_topic('transactions')
    
    def save_raw(self, data):
        # Save as Parquet
        data.to_parquet('s3://bucket/raw/transactions.parquet')

class TransformationStage:
    def clean(self, data):
        return data.dropna(subset=['revenue', 'transaction_time'])
    
    def enrich(self, data):
        # Add product info
        products = self.get_dim_products()
        return data.merge(products, on='product_id')
    
    def aggregate(self, data):
        return data.groupby(['date', 'store_id']).agg({
            'revenue': 'sum',
            'quantity': 'sum'
        }).reset_index()

class QualityChecks:
    def check_raw_data(self):
        # Row count check
        assert len(raw_data) > 0
        # Null check
        assert raw_data['revenue'].notna().all()
```

**Q116: What are the considerations for DuckDB in a microservices architecture?**

A:
```
┌─────────────────────────────────────────────────────────────────────┐
│                    Microservices Architecture                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────┐          ┌────────────────┐                     │
│  │ Order Service  │          │ Inventory Svc  │                     │
│  │                │          │                │                     │
│  │ DuckDB: Local  │          │ DuckDB: Local  │                     │
│  │ aggregations   │          │ stock levels   │                     │
│  └───────┬────────┘          └───────┬────────┘                     │
│          │                            │                              │
│          └──────────┬─────────────────┘                              │
│                      ▼                                               │
│          ┌─────────────────────┐                                      │
│          │   API Gateway       │                                      │
│          │                     │                                      │
│          │  Aggregates from    │                                      │
│          │  multiple services  │                                      │
│          └─────────────────────┘                                      │
│                      │                                                │
│          ┌───────────┴───────────┐                                    │
│          ▼                       ▼                                    │
│  ┌────────────────┐     ┌────────────────┐                            │
│  │ Analytics DB   │     │ Reporting DB   │                            │
│  │ (DuckDB)       │     │ (DuckDB)       │                            │
│  │                │     │                │                            │
│  │ Pre-computed   │     │ Ad-hoc         │                            │
│  │ metrics        │     │ analysis       │                            │
│  └────────────────┘     └────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
```

**Q117: How do you design for disaster recovery with DuckDB?**

A:
```python
class DisasterRecovery:
    def __init__(self, primary_path, replica_path):
        self.primary_path = primary_path
        self.replica_path = replica_path
    
    def create_replica(self):
        """Create a read replica for DR."""
        # Backup primary
        backup_path = f"{self.replica_path}/backup_{datetime.now():%Y%m%d}.duckdb"
        shutil.copy2(self.primary_path, backup_path)
        
        # Also export to Parquet for cross-platform recovery
        con = duckdb.connect(self.primary_path)
        
        for table in con.execute("SHOW TABLES").fetchall():
            table_name = table[0]
            con.execute(f"""
                COPY (SELECT * FROM {table_name})
                TO '{self.replica_path}/{table_name}.parquet'
                (FORMAT PARQUET, COMPRESSION 'zstd')
            """)
    
    def failover(self):
        """Switch to replica."""
        # Promote replica
        shutil.copy2(
            f"{self.replica_path}/latest_backup.duckdb",
            self.primary_path
        )
    
    def point_in_time_recovery(self, target_time):
        """Recover to specific point in time."""
        # Find closest backup before target time
        backups = sorted(Path(self.replica_path).glob("backup_*.duckdb"))
        
        for backup in reversed(backups):
            if backup.stat().st_mtime < target_time.timestamp():
                return duckdb.connect(str(backup))
        
        raise ValueError("No backup found before target time")
```

**Q118: What is DuckDB's role in a streaming architecture?**

A:
```
┌─────────────────────────────────────────────────────────────────────┐
│                    Streaming Architecture with DuckDB               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────┐     ┌──────────────────────────────────────────┐     │
│  │  Sources   │────▶│           Streaming Platform            │     │
│  │            │     │                                          │     │
│  │ POS        │     │  ┌─────────┐    ┌─────────┐    ┌───────┐  │     │
│  │ IoT        │────▶│  │ Kafka   │───▶│ Flink   │───▶│ Sinks │  │     │
│  │ Web        │     │  └─────────┘    └─────────┘    └───┬───┘  │     │
│  └────────────┘     │                                   │      │     │
│                     └───────────────────────────────────┼──────┘     │
│                                                         │            │
│    ┌─────────────────────────────────────────────────────▼──────┐    │
│    │                   DuckDB Layer                             │    │
│    │  ┌────────────────┐  ┌─────────────────┐  ┌─────────────┐  │    │
│    │  │ Real-time      │  │ Pre-aggregation │  │ ML Feature  │  │    │
│    │  │ Queries        │  │ (Hourly/Daily)  │  │ Store       │  │    │
│    │  │                │  │                 │  │             │  │    │
│    │  │ Sub-second     │  │ Rollup tables   │  │ Online      │  │    │
│    │  │ response       │  │                 │  │ features    │  │    │
│    │  └────────────────┘  └─────────────────┘  └─────────────┘  │    │
│    └─────────────────────────────────────────────────────────────┘    │
│                              │                                         │
│    ┌─────────────────────────┴───────────────────────────────┐      │
│    │                  Query/Dashboard Layer                    │      │
│    │   ┌─────────────┐    ┌─────────────┐    ┌──────────────┐  │      │
│    │   │ Dashboards  │    │ Alerting    │    │ Ad-hoc       │  │      │
│    │   │ (Grafana)   │    │             │    │ Analysis     │  │      │
│    │   └─────────────┘    └─────────────┘    └──────────────┘  │      │
│    └───────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

**Q119: How do you design a feature store with DuckDB?**

A:
```python
class FeatureStore:
    """ML Feature Store using DuckDB."""
    
    def __init__(self, con):
        self.con = con
        self._init_schema()
    
    def _init_schema(self):
        # Entity definitions
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                entity_id VARCHAR PRIMARY KEY,
                entity_type VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Feature definitions
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS feature_definitions (
                feature_name VARCHAR PRIMARY KEY,
                entity_type VARCHAR,
                feature_type VARCHAR,
                description VARCHAR
            )
        """)
        
        # Feature values (time-series)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS feature_values (
                entity_id VARCHAR,
                feature_name VARCHAR,
                value DOUBLE,
                event_time TIMESTAMP,
                PRIMARY KEY (entity_id, feature_name, event_time)
            )
        """)
    
    def register_feature(self, name, entity_type, feature_type, description):
        self.con.execute("""
            INSERT INTO feature_definitions VALUES (?, ?, ?, ?)
        """, params=[name, entity_type, feature_type, description])
    
    def write_feature(self, entity_id, feature_name, value, event_time):
        self.con.execute("""
            INSERT INTO feature_values VALUES (?, ?, ?, ?)
        """, params=[entity_id, feature_name, value, event_time])
    
    def get_latest_features(self, entity_id, feature_names):
        """Get latest feature values for an entity."""
        placeholders = ', '.join(['?' for _ in feature_names])
        
        return self.con.execute(f"""
            SELECT f.feature_name, f.value, f.event_time
            FROM feature_values f
            INNER JOIN (
                SELECT feature_name, MAX(event_time) as max_time
                FROM feature_values
                WHERE entity_id = ?
                  AND feature_name IN ({placeholders})
                GROUP BY feature_name
            ) latest ON f.feature_name = latest.feature_name
                    AND f.event_time = latest.max_time
            WHERE f.entity_id = ?
        """, params=[entity_id] + feature_names + [entity_id]).df()
    
    def get_feature_history(self, entity_id, feature_name, 
                           start_time, end_time):
        """Get feature history for training."""
        return self.con.execute("""
            SELECT event_time, value
            FROM feature_values
            WHERE entity_id = ?
              AND feature_name = ?
              AND event_time BETWEEN ? AND ?
            ORDER BY event_time
        """, params=[entity_id, feature_name, start_time, end_time]).df()
    
    def compute_point_in_time_features(self, entity_id, feature_names, 
                                        as_of_time):
        """Get features as they were at a specific point in time."""
        placeholders = ', '.join(['?' for _ in feature_names])
        
        return self.con.execute(f"""
            SELECT f.feature_name, f.value
            FROM feature_values f
            INNER JOIN (
                SELECT feature_name, MAX(event_time) as max_time
                FROM feature_values
                WHERE entity_id = ?
                  AND feature_name IN ({placeholders})
                  AND event_time <= ?
                GROUP BY feature_name
            ) latest ON f.feature_name = latest.feature_name
                    AND f.event_time = latest.max_time
            WHERE f.entity_id = ?
        """, params=[entity_id, as_of_time] + feature_names + [entity_id]).df()
```

**Q120: How do you design for 99.99% uptime with DuckDB?**

A:
```python
class HighAvailabilitySetup:
    """Design for high availability."""
    
    def __init__(self):
        self.primary = duckdb.connect("primary.db")
        self.replica = duckdb.connect("replica.db", read_only=True)
    
    def health_check(self):
        """Check health of primary."""
        try:
            # Check can write
            self.primary.execute("SELECT 1")
            # Check can read
            self.replica.execute("SELECT 1")
            # Check replication lag
            lag = self._get_replication_lag()
            return {'status': 'healthy', 'lag': lag}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    def auto_failover(self):
        """Automatic failover to replica."""
        health = self.health_check()
        
        if health['status'] == 'unhealthy':
            # Promote replica
            self.replica.execute("CHECKPOINT")
            
            # Update connection
            self.primary = duckdb.connect("replica.db")
            self.replica = duckdb.connect("primary.db", read_only=True)
            
            # Alert
            send_alert("Failover completed")
    
    def _get_replication_lag(self):
        # Compare latest transaction times
        primary_time = self.primary.execute(
            "SELECT MAX(event_time) FROM events"
        ).fetchone()[0]
        
        replica_time = self.replica.execute(
            "SELECT MAX(event_time) FROM events"
        ).fetchone()[0]
        
        return (primary_time - replica_time).total_seconds()
```

**Q121: What is DuckDB's approach to query federation?**

A: DuckDB can federate queries across multiple data sources:

```python
# Attach external databases
con = duckdb.connect()

# PostgreSQL
con.execute("ATTACH 'postgresql://user:pass@host:5432/db' AS pg_db")

# SQLite
con.execute("ATTACH 'sqlite:legacy.db' AS sqlite_db")

# Other DuckDB databases
con.execute("ATTACH 'analytics.db' AS analytics")

# Query across sources
result = con.execute("""
    SELECT 
        pg.sales.*,
        sqlite.customers.name
    FROM pg_db.sales
    JOIN sqlite_db.customers ON pg.sales.customer_id = sqlite.customers.id
""").df()
```

**Q122: Design a metrics pipeline with DuckDB.**

A:
```python
class MetricsPipeline:
    """Real-time metrics calculation."""
    
    def __init__(self, con):
        self.con = con
        self._init_metrics_tables()
    
    def _init_metrics_tables(self):
        # Raw metrics
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS raw_metrics (
                metric_name VARCHAR,
                value DOUBLE,
                labels JSON,
                timestamp TIMESTAMP
            )
        """)
        
        # Pre-aggregated metrics
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS agg_metrics_1m (
                metric_name VARCHAR,
                labels JSON,
                min_val DOUBLE,
                max_val DOUBLE,
                sum_val DOUBLE,
                count BIGINT,
                timestamp TIMESTAMP,
                PRIMARY KEY (metric_name, labels, timestamp)
            )
        """)
    
    def record_metric(self, metric_name, value, labels=None):
        labels_json = json.dumps(labels) if labels else '{}'
        self.con.execute("""
            INSERT INTO raw_metrics VALUES (?, ?, ?, ?)
        """, params=[metric_name, value, labels_json, datetime.now()])
    
    def aggregate_1m(self):
        """Rollup to 1-minute aggregates."""
        self.con.execute("""
            INSERT INTO agg_metrics_1m
            SELECT 
                metric_name,
                labels,
                MIN(value),
                MAX(value),
                SUM(value),
                COUNT(*),
                DATE_TRUNC('minute', timestamp)
            FROM raw_metrics
            WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '2 minutes'
            GROUP BY 1, 2, 7
            ON CONFLICT(metric_name, labels, timestamp) 
            DO UPDATE SET
                min_val = LEAST(agg_metrics_1m.min_val, excluded.min_val),
                max_val = GREATEST(agg_metrics_1m.max_val, excluded.max_val),
                sum_val = agg_metrics_1m.sum_val + excluded.sum_val,
                count = agg_metrics_1m.count + excluded.count
        """)
    
    def get_metric(self, metric_name, duration='1h'):
        return self.con.execute("""
            SELECT 
                timestamp,
                min_val,
                max_val,
                sum_val / count as avg_val
            FROM agg_metrics_1m
            WHERE metric_name = ?
              AND timestamp >= CURRENT_TIMESTAMP - INTERVAL ?
            ORDER BY timestamp
        """, params=[metric_name, duration]).df()
```

**Q123: How do you handle schema evolution in production?**

A:
```python
class SchemaEvolution:
    """Handle schema changes without downtime."""
    
    def __init__(self, con):
        self.con = con
    
    def add_column_safe(self, table, column, dtype):
        """Add column with zero downtime."""
        # Step 1: Add column as nullable
        self.con.execute(f"""
            ALTER TABLE {table} ADD COLUMN {column} {dtype}
        """)
        
        # Step 2: Backfill (optional, in batches)
        self._backfill_column(table, column)
        
        # Step 3: Add NOT NULL constraint (after backfill)
        # This is safe because existing rows have values
    
    def _backfill_column(self, table, column, batch_size=10000):
        # Get rows without the new column
        while True:
            result = self.con.execute(f"""
                SELECT * FROM {table}
                WHERE {column} IS NULL
                LIMIT ?
            """, params=[batch_size]).df()
            
            if len(result) == 0:
                break
            
            # Compute values for these rows
            computed = self._compute_column_values(result)
            
            # Update
            for idx, row in computed.iterrows():
                self.con.execute(f"""
                    UPDATE {table} 
                    SET {column} = ?
                    WHERE {table}.rowid = ?
                """, params=[row[column], row['rowid']])
    
    def migrate_column_type(self, table, column, new_type):
        """Change column type safely."""
        # Add new column
        self.con.execute(f"""
            ALTER TABLE {table} ADD COLUMN {column}_new {new_type}
        """)
        
        # Copy data
        self.con.execute(f"""
            UPDATE {table} SET {column}_new = TRY_CAST({column}, '{new_type}')
        """)
        
        # Verify
        null_count = self.con.execute(f"""
            SELECT COUNT(*) FROM {table} WHERE {column}_new IS NULL AND {column} IS NOT NULL
        """).fetchone()[0]
        
        if null_count > 0:
            raise ValueError(f"Migration would lose {null_count} rows")
        
        # Swap columns
        self.con.execute(f"""
            ALTER TABLE {table} DROP COLUMN {column}
        """)
        self.con.execute(f"""
            ALTER TABLE {table} RENAME COLUMN {column}_new TO {column}
        """)
```

**Q124: What is the CAP theorem trade-off for DuckDB?**

A: DuckDB as an embedded database makes specific trade-offs:
- **Consistency**: Strong (ACID transactions)
- **Availability**: Limited (single-instance, file locking)
- **Partition Tolerance**: Not applicable (not distributed)

For distributed scenarios:
- DuckDB is not CP or AP by itself
- Use replication for read availability
- Use external coordination (ZooKeeper) for CP
- Consider MotherDuck or custom solutions for distributed deployments

**Q125: Design a data quality framework with DuckDB.**

A:
```python
class DataQualityFramework:
    """Automated data quality checks."""
    
    def __init__(self, con):
        self.con = con
        self.rules = []
        self._init_results_table()
    
    def _init_results_table(self):
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS quality_results (
                check_id VARCHAR,
                table_name VARCHAR,
                check_type VARCHAR,
                status VARCHAR,
                failed_rows BIGINT,
                error_message VARCHAR,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def add_rule(self, name, check_type, params):
        """Register a quality rule."""
        self.rules.append({
            'name': name,
            'check_type': check_type,
            'params': params
        })
    
    def check_nulls(self, table, column):
        """Check for NULL values."""
        result = self.con.execute(f"""
            SELECT COUNT(*) FROM {table} WHERE {column} IS NULL
        """).fetchone()[0]
        
        return {
            'table': table,
            'column': column,
            'check_type': 'null_check',
            'failed_rows': result,
            'status': 'pass' if result == 0 else 'fail'
        }
    
    def check_uniqueness(self, table, column):
        """Check for duplicate values."""
        duplicates = self.con.execute(f"""
            SELECT {column}, COUNT(*) as cnt
            FROM {table}
            GROUP BY {column}
            HAVING COUNT(*) > 1
        """).fetchall()
        
        return {
            'table': table,
            'column': column,
            'check_type': 'uniqueness',
            'failed_rows': len(duplicates),
            'duplicates': duplicates[:10],
            'status': 'pass' if len(duplicates) == 0 else 'fail'
        }
    
    def check_referential_integrity(self, child_table, child_col, 
                                     parent_table, parent_col):
        """Check foreign key relationship."""
        orphans = self.con.execute(f"""
            SELECT COUNT(*) FROM {child_table}
            WHERE {child_col} NOT IN (
                SELECT {parent_col} FROM {parent_table}
            )
        """).fetchone()[0]
        
        return {
            'check_type': 'referential_integrity',
            'failed_rows': orphans,
            'status': 'pass' if orphans == 0 else 'fail'
        }
    
    def run_all_checks(self):
        """Execute all registered rules."""
        results = []
        for rule in self.rules:
            if rule['check_type'] == 'null_check':
                result = self.check_nulls(rule['table'], rule['column'])
            elif rule['check_type'] == 'uniqueness':
                result = self.check_uniqueness(rule['table'], rule['column'])
            elif rule['check_type'] == 'referential_integrity':
                result = self.check_referential_integrity(**rule['params'])
            
            result['check_id'] = rule['name']
            results.append(result)
            
            # Store result
            self._store_result(result)
        
        return results
```

---

### 13.6 Debugging Questions (10)

**Q126: Query returns wrong results. How do you debug?**

A:
```python
# Step 1: Check query logic with simple data
result = con.execute("""
    SELECT * FROM sales WHERE 1=1 LIMIT 5
""").df()
print(result)

# Step 2: Check filters individually
result = con.execute("SELECT * FROM sales WHERE store_id = 'ST001'").df()
print(f"Rows with store_id filter: {len(result)}")

result = con.execute("SELECT * FROM sales WHERE revenue > 100").df()
print(f"Rows with revenue filter: {len(result)}")

# Step 3: Verify JOIN conditions
result = con.execute("""
    SELECT s.*, p.name 
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    WHERE s.product_id IS NOT NULL
""").df()

# Step 4: Check for NULL handling issues
result = con.execute("""
    SELECT COUNT(*) FROM sales WHERE store_id = NULL  -- Always FALSE!
""").fetchone()

result = con.execute("""
    SELECT COUNT(*) FROM sales WHERE store_id IS NULL  -- Correct
""").fetchone()

# Step 5: Use EXPLAIN to verify plan
print(con.execute("EXPLAIN <problematic_query>").fetchall())
```

**Q127: Out of memory error on large query. Debug.**

A:
```python
# Step 1: Check current memory settings
print(con.execute("SELECT * FROM duckdb_settings() WHERE name LIKE '%memory%'").df())

# Step 2: Check what's consuming memory
print(con.execute("SELECT current_memory_usage()").fetchone())
print(con.execute("SELECT peak_memory_usage()").fetchone())

# Step 3: Run EXPLAIN ANALYZE
print(con.execute("EXPLAIN ANALYZE <query>").df())

# Step 4: Reduce query scope
# Instead of full table
result = con.execute("""
    SELECT DATE_TRUNC('day', t), SUM(revenue)
    FROM sales
    WHERE transaction_time BETWEEN ? AND ?
    GROUP BY 1
""", params=['2024-01-01', '2024-01-31']).df()

# Step 5: Increase memory or enable spilling
con = duckdb.connect(config={
    'max_memory': '8GB',
    'temp_directory': '/path/to/spill'
})
```

**Q128: Query is slow. Profile it.**

A:
```python
# Step 1: Enable profiling
con.execute("SET enable_profiling = true")
con.execute("SET profiling_output = '/tmp/profile.json'")

# Step 2: Run query
result = con.execute("SELECT * FROM huge_table GROUP BY category").df()

# Step 3: Read profile
import json
with open('/tmp/profile.json') as f:
    profile = json.load(f)
    print(json.dumps(profile, indent=2))

# Step 4: Check for warnings
warnings = profile.get('warnings', [])
for w in warnings:
    print(f"Warning: {w}")

# Step 5: Common fixes:
# - Add index
con.execute("CREATE INDEX idx ON huge_table(category)")
# - Increase threads
con.execute("SET threads = 8")
# - Use smarter aggregation
```

**Q129: Data import is failing. Debug.**

A:
```python
# Step 1: Verify file exists and is readable
import os
print(os.path.exists('data.parquet'))
print(os.path.getsize('data.parquet'))

# Step 2: Check file format
result = con.execute("SELECT * FROM read_parquet('data.parquet') LIMIT 0").description
print(result)

# Step 3: Try with explicit options
con.execute("""
    COPY sales FROM 'data.parquet'
    (FORMAT PARQUET, AUTO_DETECT TRUE)
""")

# Step 4: Check for schema mismatch
existing = con.execute("DESCRIBE sales").df()
new_schema = con.execute("DESCRIBE SELECT * FROM 'data.parquet'").df()

# Compare
print("Existing:", existing['column_name'].tolist())
print("New:", new_schema['column_name'].tolist())

# Step 5: Handle schema differences
con.execute("""
    COPY sales FROM 'data.parquet'
    (FORMAT PARQUET, columns={'id': 'id', 'revenue': 'revenue'})
""")
```

**Q130: Transaction deadlock. Resolve.**

A:
```python
# Step 1: Check for active transactions
print(con.execute("SELECT * FROM duckdb_active_transactions()").df())

# Step 2: Identify blocking
# Connection 1
con1 = duckdb.connect("retail.db")
con1.begin()
con1.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")

# Connection 2 waits...

# Step 3: Resolve - use proper lock ordering
# Always update tables in same order
# BAD: Thread A updates A then B, Thread B updates B then A
# GOOD: Both threads update A then B

# Step 4: Use explicit locking
con1.execute("BEGIN TRANSACTION")
con1.execute("SELECT * FROM accounts WHERE id = 1 FOR UPDATE")  # Explicit lock

# Step 5: Timeout for locks
con.execute("SET lock_timeout = '30s'")
```

---

## 14. Hands-on Exercises

### Level 1: Basic Operations

**Exercise 1.1: Create Your First DuckDB Database**

```python
import duckdb

# Create database and table
con = duckdb.connect("retail.db")

# Create sales table
con.execute("""
    CREATE TABLE sales (
        transaction_id VARCHAR,
        transaction_date DATE,
        store_id VARCHAR,
        product_id VARCHAR,
        quantity INTEGER,
        unit_price DECIMAL(10,2),
        revenue DECIMAL(10,2)
    )
""")

# Insert sample data
con.execute("""
    INSERT INTO sales VALUES 
    ('TXN001', '2024-01-15', 'ST001', 'PROD001', 2, 25.00, 50.00),
    ('TXN002', '2024-01-15', 'ST001', 'PROD002', 1, 100.00, 100.00),
    ('TXN003', '2024-01-16', 'ST002', 'PROD001', 3, 25.00, 75.00)
""")

# Query the data
result = con.execute("SELECT * FROM sales").df()
print(result)

# Aggregation
result = con.execute("""
    SELECT 
        store_id,
        SUM(revenue) as total_revenue,
        COUNT(*) as transaction_count
    FROM sales
    GROUP BY store_id
""").df()
print(result)

con.close()
```

**Exercise 1.2: Query Parquet Files**

```python
import duckdb
import pandas as pd

# Create sample data and save as Parquet
df = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=100),
    'store_id': ['ST001', 'ST002'] * 50,
    'revenue': [100 + i % 20 for i in range(100)]
})
df.to_parquet('sales_data.parquet', index=False)

# Query Parquet directly
con = duckdb.connect()

result = con.execute("""
    SELECT 
        store_id,
        AVG(revenue) as avg_revenue,
        MIN(revenue) as min_revenue,
        MAX(revenue) as max_revenue
    FROM 'sales_data.parquet'
    GROUP BY store_id
""").df()
print(result)

# Filter during read (predicate pushdown)
result = con.execute("""
    SELECT * FROM 'sales_data.parquet'
    WHERE store_id = 'ST001' AND revenue > 110
""").df()
print(result)

con.close()
```

### Level 2: Intermediate Analysis

**Exercise 2.1: Time-Series Analysis**

```python
import duckdb
import pandas as pd
from datetime import datetime, timedelta

# Create time-series data
dates = pd.date_range('2024-01-01', periods=365, freq='D')
data = pd.DataFrame({
    'date': dates,
    'store_id': ['ST001'] * 365,
    'daily_revenue': [1000 + i % 100 + (i % 7) * 10 for i in range(365)]
})
data.to_parquet('time_series.parquet', index=False)

con = duckdb.connect()

# Daily to monthly aggregation
result = con.execute("""
    SELECT 
        DATE_TRUNC('month', date) as month,
        SUM(daily_revenue) as monthly_revenue,
        AVG(daily_revenue) as avg_daily_revenue
    FROM 'time_series.parquet'
    GROUP BY 1
    ORDER BY 1
""").df()
print("Monthly Summary:")
print(result)

# Calculate month-over-month growth
result = con.execute("""
    WITH monthly AS (
        SELECT 
            DATE_TRUNC('month', date) as month,
            SUM(daily_revenue) as revenue
        FROM 'time_series.parquet'
        GROUP BY 1
    )
    SELECT 
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY month) as prev_month,
        revenue - LAG(revenue) OVER (ORDER BY month) as growth,
        (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month) * 100 as growth_pct
    FROM monthly
""").df()
print("\nGrowth Analysis:")
print(result)

con.close()
```

**Exercise 2.2: Customer Segmentation**

```python
import duckdb
import pandas as pd

# Create customer transaction data
customers = pd.DataFrame({
    'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'total_purchases': [1500, 300, 8000, 200, 4500],
    'visit_count': [10, 3, 25, 2, 15],
    'last_purchase_days_ago': [5, 30, 2, 60, 7]
})
customers.to_parquet('customers.parquet', index=False)

con = duckdb.connect()

# Segment customers
result = con.execute("""
    SELECT 
        customer_id,
        name,
        total_purchases,
        visit_count,
        last_purchase_days_ago,
        CASE 
            WHEN total_purchases >= 5000 THEN 'VIP'
            WHEN total_purchases >= 1000 THEN 'Regular'
            WHEN total_purchases >= 200 THEN 'Occasional'
            ELSE 'Inactive'
        END as segment,
        CASE 
            WHEN last_purchase_days_ago <= 7 THEN 'Active'
            WHEN last_purchase_days_ago <= 30 THEN 'Recent'
            ELSE 'Churned'
        END as activity_status
    FROM 'customers.parquet'
    ORDER BY total_purchases DESC
""").df()
print("Customer Segmentation:")
print(result)

# Aggregate by segment
result = con.execute("""
    WITH customer_segments AS (
        SELECT 
            customer_id,
            total_purchases,
            visit_count,
            last_purchase_days_ago,
            CASE 
                WHEN total_purchases >= 5000 THEN 'VIP'
                WHEN total_purchases >= 1000 THEN 'Regular'
                WHEN total_purchases >= 200 THEN 'Occasional'
                ELSE 'Inactive'
            END as segment
        FROM 'customers.parquet'
    )
    SELECT 
        segment,
        COUNT(*) as customer_count,
        SUM(total_purchases) as total_revenue,
        AVG(visit_count) as avg_visits,
        AVG(last_purchase_days_ago) as avg_days_since_purchase
    FROM customer_segments
    GROUP BY segment
""").df()
print("\nSegment Summary:")
print(result)

con.close()
```

### Level 3: Advanced ETL and Optimization

**Exercise 3.1: Build an ETL Pipeline**

```python
import duckdb
import pandas as pd
from datetime import datetime

# Simulate raw data
raw_sales = pd.DataFrame({
    'transaction_id': [f'TXN{i:06d}' for i in range(1000)],
    'transaction_time': pd.date_range('2024-01-01', periods=1000, freq='10min'),
    'store_id': ['ST001', 'ST002', 'ST003'] * 334,
    'product_id': [f'P{i:04d}' for i in range(1000)],
    'quantity': [1, 2, 3, 4, 5] * 200,
    'unit_price': [10.0, 20.0, 30.0, 40.0, 50.0] * 200,
    'customer_id': [f'C{i:04d}' for i in range(1000)]
})
raw_sales['revenue'] = raw_sales['quantity'] * raw_sales['unit_price']

# Add some data quality issues
raw_sales.loc[0, 'quantity'] = -1  # Invalid
raw_sales.loc[100, 'unit_price'] = 0  # Invalid
raw_sales.loc[200, 'store_id'] = None  # NULL

# Save raw data
raw_sales.to_parquet('raw_sales.parquet', index=False)

# Build ETL pipeline
class ETL:
    def __init__(self, con):
        self.con = con
    
    def extract(self, source_path):
        """Load raw data."""
        return self.con.execute(f"""
            SELECT * FROM '{source_path}'
        """).df()
    
    def transform(self, df):
        """Clean and validate data."""
        # Create cleaned version
        cleaned = df[
            (df['quantity'] > 0) &
            (df['unit_price'] > 0) &
            (df['store_id'].notna())
        ].copy()
        
        # Add derived fields
        cleaned['date'] = cleaned['transaction_time'].dt.date
        cleaned['hour'] = cleaned['transaction_time'].dt.hour
        cleaned['day_of_week'] = cleaned['transaction_time'].dt.dayofweek
        
        return cleaned
    
    def load(self, df, target_table):
        """Load to target table."""
        self.con.execute(f"DROP TABLE IF EXISTS {target_table}")
        self.con.execute(f"CREATE TABLE {target_table} AS SELECT * FROM df")
    
    def run(self, source, target):
        print(f"[{datetime.now()}] Extracting...")
        df = self.extract(source)
        print(f"[{datetime.now()}] Extracted {len(df)} rows")
        
        print(f"[{datetime.now()}] Transforming...")
        df = self.transform(df)
        print(f"[{datetime.now()}] Transformed {len(df)} rows (removed {len(raw_sales) - len(df)} invalid)")
        
        print(f"[{datetime.now()}] Loading...")
        self.load(df, target)
        print(f"[{datetime.now()}] Complete!")

# Run pipeline
con = duckdb.connect()
etl = ETL(con)
etl.run('raw_sales.parquet', 'cleaned_sales')

# Verify results
print("\nCleaned Data Sample:")
print(con.execute("SELECT * FROM cleaned_sales LIMIT 5").df())

print("\nDaily Summary:")
print(con.execute("""
    SELECT 
        date,
        COUNT(*) as transactions,
        SUM(revenue) as total_revenue
    FROM cleaned_sales
    GROUP BY date
    ORDER BY date
""").df())

con.close()
```

**Exercise 3.2: Query Optimization Challenge**

```python
import duckdb
import pandas as pd
import time

# Create large dataset
n_rows = 1_000_000
large_df = pd.DataFrame({
    'transaction_id': [f'TXN{i:010d}' for i in range(n_rows)],
    'transaction_date': pd.date_range('2023-01-01', periods=n_rows, freq='1min'),
    'store_id': ['ST' + str(i % 100).zfill(3) for i in range(n_rows)],
    'category': ['CatA', 'CatB', 'CatC', 'CatD'] * (n_rows // 4),
    'revenue': [100 + i % 500 for i in range(n_rows)]
})
large_df.to_parquet('large_sales.parquet', index=False)

con = duckdb.connect()

# Challenge: Optimize this query
# Original (slow)
print("Running unoptimized query...")
start = time.time()
result1 = con.execute("""
    SELECT 
        store_id,
        category,
        DATE_TRUNC('day', transaction_date) as day,
        SUM(revenue) as total_revenue,
        COUNT(*) as transaction_count
    FROM 'large_sales.parquet'
    WHERE store_id IN ('ST001', 'ST002', 'ST003')
    GROUP BY store_id, category, 3
    ORDER BY 3, 1, 2
""").df()
print(f"Unoptimized time: {time.time() - start:.2f}s")

# Optimization 1: Use EXTRACT instead of DATE_TRUNC
print("\nRunning optimized query (EXTRACT)...")
start = time.time()
result2 = con.execute("""
    SELECT 
        store_id,
        category,
        CAST(transaction_date AS DATE) as day,
        SUM(revenue) as total_revenue,
        COUNT(*) as transaction_count
    FROM 'large_sales.parquet'
    WHERE store_id IN ('ST001', 'ST002', 'ST003')
    GROUP BY store_id, category, 3
    ORDER BY 3, 1, 2
""").df()
print(f"EXTRACT optimization time: {time.time() - start:.2f}s")

# Optimization 2: Pre-filter with S3 (if using S3)
# Or create indexed table
print("\nRunning with pre-filtered table...")
con.execute("""
    CREATE TABLE filtered_sales AS
    SELECT * FROM 'large_sales.parquet'
    WHERE store_id IN ('ST001', 'ST002', 'ST003')
""")
con.execute("CREATE INDEX idx_store ON filtered_sales(store_id)")

start = time.time()
result3 = con.execute("""
    SELECT 
        store_id,
        category,
        CAST(transaction_date AS DATE) as day,
        SUM(revenue) as total_revenue,
        COUNT(*) as transaction_count
    FROM filtered_sales
    GROUP BY store_id, category, 3
    ORDER BY 3, 1, 2
""").df()
print(f"Pre-filtered table time: {time.time() - start:.2f}s")

con.close()
```

### Level 4: Production-Grade Implementation

**Exercise 4.1: Build a Real-Time Analytics Dashboard Backend**

```python
import duckdb
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import threading

class RealTimeAnalyticsBackend:
    """Production-grade real-time analytics backend."""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db = duckdb.connect(db_path)
        self._init_schema()
        self._lock = threading.Lock()
        
    def _init_schema(self):
        """Initialize database schema."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id VARCHAR,
                transaction_time TIMESTAMP,
                store_id VARCHAR,
                category VARCHAR,
                revenue DECIMAL(10,2),
                quantity INTEGER,
                customer_id VARCHAR
            )
        """)
        
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS hourly_metrics (
                hour TIMESTAMP,
                store_id VARCHAR,
                category VARCHAR,
                revenue DECIMAL(12,2),
                units INTEGER,
                transactions INTEGER,
                unique_customers INTEGER,
                PRIMARY KEY (hour, store_id, category)
            )
        """)
        
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS daily_metrics (
                date DATE,
                store_id VARCHAR,
                category VARCHAR,
                revenue DECIMAL(12,2),
                units INTEGER,
                transactions INTEGER,
                PRIMARY KEY (date, store_id, category)
            )
        """)
        
        # Create indexes
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_txn_time 
            ON transactions(transaction_time)
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_txn_store 
            ON transactions(store_id)
        """)
    
    def ingest_transaction(self, txn: Dict):
        """Ingest a single transaction."""
        with self._lock:
            self.db.execute("""
                INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?)
            """, params=[
                txn['transaction_id'],
                txn['transaction_time'],
                txn['store_id'],
                txn['category'],
                txn['revenue'],
                txn['quantity'],
                txn.get('customer_id')
            ])
            
            # Update hourly metrics
            hour = txn['transaction_time'].replace(minute=0, second=0, microsecond=0)
            
            # Upsert hourly metrics
            self.db.execute("""
                INSERT INTO hourly_metrics VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(hour, store_id, category) DO UPDATE SET
                    revenue = hourly_metrics.revenue + excluded.revenue,
                    units = hourly_metrics.units + excluded.units,
                    transactions = hourly_metrics.transactions + 1
            """, params=[
                hour,
                txn['store_id'],
                txn['category'],
                txn['revenue'],
                txn['quantity'],
                1,
                1 if txn.get('customer_id') else 0
            ])
    
    def ingest_batch(self, transactions: List[Dict]):
        """Ingest a batch of transactions efficiently."""
        if not transactions:
            return
        
        df = pd.DataFrame(transactions)
        
        with self._lock:
            # Bulk insert
            self.db.execute("""
                INSERT INTO transactions 
                SELECT * FROM df
            """)
            
            # Aggregate hourly
            hour = datetime.fromisoformat(
                transactions[0]['transaction_time']
            ).replace(minute=0, second=0, microsecond=0)
            
            self.db.execute("""
                INSERT INTO hourly_metrics
                SELECT 
                    ? as hour,
                    store_id,
                    category,
                    SUM(revenue),
                    SUM(quantity),
                    COUNT(*),
                    COUNT(DISTINCT customer_id)
                FROM df
                GROUP BY 2, 3
                ON CONFLICT(hour, store_id, category) DO UPDATE SET
                    revenue = hourly_metrics.revenue + excluded.revenue,
                    units = hourly_metrics.units + excluded.units,
                    transactions = hourly_metrics.transactions + excluded.transactions
            """, params=[hour])
    
    def get_store_dashboard(self, store_id: str, hours: int = 24) -> Dict:
        """Get dashboard data for a store."""
        result = self.db.execute("""
            SELECT 
                hour,
                SUM(revenue) as revenue,
                SUM(transactions) as transactions,
                SUM(unique_customers) as customers
            FROM hourly_metrics
            WHERE store_id = ?
              AND hour >= CURRENT_TIMESTAMP - INTERVAL '? hours'
            GROUP BY hour
            ORDER BY hour DESC
        """, params=[store_id, hours]).df()
        
        # Calculate trends
        if len(result) >= 2:
            current_revenue = result.iloc[0]['revenue']
            previous_revenue = result.iloc[min(24, len(result))-1]['revenue']
            trend = (current_revenue - previous_revenue) / previous_revenue * 100
        else:
            trend = 0
        
        return {
            'store_id': store_id,
            'period_hours': hours,
            'current_revenue': float(result['revenue'].sum()),
            'current_transactions': int(result['transactions'].sum()),
            'current_customers': int(result['customers'].sum()),
            'trend_vs_previous': round(trend, 2),
            'hourly_data': result.to_dict('records')
        }
    
    def get_category_performance(self, start_date: datetime, 
                                  end_date: datetime) -> pd.DataFrame:
        """Get category performance for date range."""
        return self.db.execute("""
            SELECT 
                category,
                DATE_TRUNC('day', hour) as date,
                SUM(revenue) as revenue,
                SUM(transactions) as transactions
            FROM hourly_metrics
            WHERE hour BETWEEN ? AND ?
            GROUP BY category, 2
            ORDER BY 2, 1
        """, params=[start_date, end_date]).df()
    
    def close(self):
        """Close database connection."""
        self.db.close()

# Usage example
backend = RealTimeAnalyticsBackend()

# Simulate real-time ingestion
for i in range(100):
    backend.ingest_transaction({
        'transaction_id': f'TXN{i:06d}',
        'transaction_time': datetime.now().isoformat(),
        'store_id': f'ST00{i % 3 + 1}',
        'category': ['Electronics', 'Clothing', 'Food'][i % 3],
        'revenue': 100 + (i % 50) * 10,
        'quantity': i % 3 + 1,
        'customer_id': f'CUST{i % 20:04d}'
    })

# Get dashboard data
dashboard = backend.get_store_dashboard('ST001', hours=24)
print(f"Store: {dashboard['store_id']}")
print(f"Revenue: ${dashboard['current_revenue']:.2f}")
print(f"Trend: {dashboard['trend_vs_previous']}%")

backend.close()
```

---

## 15. Real Enterprise Use Cases

### 15.1 Retail Analytics Platform

**Company Profile**: Large retail chain with 500+ stores

**Challenge**: Real-time inventory and sales visibility across all stores

**Solution**: DuckDB as the analytics acceleration layer

```mermaid
flowchart TD
    subgraph "Legacy Systems"
        POS["POS Systems"]
        ERP["SAP ERP"]
        WMS["Warehouse System"]
    end
    
    subgraph "Data Platform"
        KAFKA["Kafka"]
        FLINK["Flink"]
    end
    
    subgraph "DuckDB Layer"
        ADC["Aggregation Cache"]
        INV["Inventory DB"]
        REP["Reporting DB"]
    end
    
    subgraph "Consumption"
        DASH["Dashboards"]
        API["Mobile App"]
        EXCEL["Excel Reports"]
    end
    
    POS & ERP & WMS --> KAFKA
    KAFKA --> FLINK
    FLINK --> ADC & INV
    ADC --> DASH & API & EXCEL
    
    style DuckDB fill:#f96
```

**Results**:
- 90% reduction in dashboard load time (30s → 3s)
- 60% reduction in data warehouse costs
- Real-time visibility into inventory levels
- Excel users migrated to live dashboards

### 15.2 Financial Services - Risk Calculations

**Company**: Investment management firm

**Challenge**: Calculate portfolio risk metrics in near real-time

**Solution**: DuckDB for in-process risk calculations

```python
class PortfolioRiskCalculator:
    """Calculate portfolio risk metrics using DuckDB."""
    
    def __init__(self, con):
        self.con = con
    
    def calculate_var(self, portfolio_id, confidence=0.95, days=1):
        """Calculate Value at Risk."""
        return self.con.execute("""
            WITH portfolio_returns AS (
                SELECT 
                    date,
                    portfolio_id,
                    daily_return,
                    AVG(daily_return) OVER (
                        PARTITION BY portfolio_id 
                        ORDER BY date 
                        ROWS BETWEEN 30 PRECEDING AND CURRENT ROW
                    ) as rolling_avg,
                    STDDEV(daily_return) OVER (
                        PARTITION BY portfolio_id 
                        ORDER BY date 
                        ROWS BETWEEN 30 PRECEDING AND CURRENT ROW
                    ) as rolling_std
                FROM portfolio_returns
                WHERE portfolio_id = ?
            )
            SELECT 
                portfolio_id,
                AVG(rolling_avg) as mean_return,
                AVG(rolling_std) as volatility,
                AVG(rolling_avg) - ? * AVG(rolling_std) * SQRT(?) as var_95
            FROM portfolio_returns
            GROUP BY portfolio_id
        """, params=[portfolio_id, confidence, days]).df()
    
    def calculate_sharpe_ratio(self, portfolio_id, risk_free_rate=0.02):
        """Calculate Sharpe ratio."""
        return self.con.execute("""
            WITH performance AS (
                SELECT 
                    AVG(daily_return) * 252 as annualized_return,
                    STDDEV(daily_return) * SQRT(252) as annualized_volatility
                FROM portfolio_returns
                WHERE portfolio_id = ?
                  AND date >= CURRENT_DATE - INTERVAL '1 year'
            )
            SELECT 
                portfolio_id,
                (annualized_return - ?) / annualized_volatility as sharpe_ratio
            FROM performance
        """, params=[portfolio_id, risk_free_rate]).df()
```

### 15.3 Healthcare - Patient Data Analytics

**Use Case**: Real-time hospital bed management and patient flow analytics

```python
class HospitalAnalytics:
    """Healthcare analytics using DuckDB."""
    
    def __init__(self):
        self.con = duckdb.connect(":memory:")
        self._init_schema()
    
    def _init_schema(self):
        self.con.execute("""
            CREATE TABLE patient_admissions (
                admission_id VARCHAR,
                patient_id VARCHAR,
                admission_time TIMESTAMP,
                department VARCHAR,
                bed_id VARCHAR,
                discharge_time TIMESTAMP
            )
        """)
        
        self.con.execute("""
            CREATE TABLE bed_status (
                bed_id VARCHAR,
                department VARCHAR,
                status VARCHAR,
                last_updated TIMESTAMP
            )
        """)
    
    def get_bed_availability(self, department: str = None):
        """Get real-time bed availability."""
        query = """
            SELECT 
                b.department,
                b.status,
                COUNT(*) as bed_count
            FROM bed_status b
        """
        
        if department:
            query += f" WHERE b.department = '{department}'"
        
        query += " GROUP BY 1, 2"
        
        return self.con.execute(query).df()
    
    def calculate_avg_length_of_stay(self, department: str):
        """Calculate average length of stay by department."""
        return self.con.execute("""
            SELECT 
                department,
                AVG(discharge_time - admission_time) as avg_los,
                PERCENTILE_CONT(0.5) WITHIN GROUP (
                    ORDER BY discharge_time - admission_time
                ) as median_los,
                MAX(discharge_time - admission_time) as max_los
            FROM patient_admissions
            WHERE department = ?
              AND discharge_time IS NOT NULL
            GROUP BY department
        """, params=[department]).df()
```

### 15.4 Gaming Analytics

**Use Case**: Real-time player behavior analysis and monetization tracking

```python
class GamingAnalytics:
    """Game analytics using DuckDB."""
    
    def __init__(self):
        self.con = duckdb.connect(":memory:")
    
    def track_player_session(self, events_df):
        """Process player session events."""
        self.con.execute("CREATE TABLE IF NOT EXISTS session_events AS SELECT * FROM events_df")
    
    def calculate_retention(self, cohort_date, days=[1, 7, 30]):
        """Calculate retention rates for a cohort."""
        retention_data = []
        
        for day in days:
            result = self.con.execute(f"""
                SELECT 
                    COUNT(DISTINCT player_id) as retained_players
                FROM session_events
                WHERE DATE(session_start) = '{cohort_date}'
                  AND EXISTS (
                      SELECT 1 FROM session_events s2
                      WHERE s2.player_id = session_events.player_id
                        AND DATE(s2.session_start) = '{cohort_date}' + INTERVAL '{day} days'
                  )
            """).fetchone()
            
            retention_data.append({
                'cohort': cohort_date,
                'day': day,
                'retention_rate': result[0] / total_players * 100 if total_players else 0
            })
        
        return pd.DataFrame(retention_data)
    
    def calculate_lifetime_value(self):
        """Calculate player lifetime value."""
        return self.con.execute("""
            WITH player_revenue AS (
                SELECT 
                    player_id,
                    SUM(revenue) as total_revenue,
                    COUNT(*) as sessions,
                    MIN(session_start) as first_session,
                    MAX(session_start) as last_session,
                    MAX(session_start) - MIN(session_start) as lifetime_days
                FROM session_events
                WHERE event_type = 'purchase'
                GROUP BY player_id
            )
            SELECT 
                AVG(total_revenue) as avg_ltv,
                AVG(lifetime_days) as avg_lifetime_days,
                AVG(total_revenue) / NULLIF(AVG(lifetime_days), 0) as daily_value
            FROM player_revenue
        """).df()
```

### 15.5 IoT Sensor Data Analysis

**Use Case**: Manufacturing plant equipment monitoring and predictive maintenance

```python
class SensorAnalytics:
    """IoT sensor analytics using DuckDB."""
    
    def __init__(self):
        self.con = duckdb.connect(":memory:")
    
    def detect_anomalies(self, equipment_id, metric, threshold_std=3):
        """Detect anomalies in sensor readings."""
        return self.con.execute(f"""
            WITH stats AS (
                SELECT 
                    AVG({metric}) as mean,
                    STDDEV({metric}) as std
                FROM sensor_readings
                WHERE equipment_id = ?
                  AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
            )
            SELECT 
                sr.timestamp,
                sr.{metric},
                s.mean,
                s.std,
                ABS(sr.{metric} - s.mean) / s.std as z_score
            FROM sensor_readings sr, stats s
            WHERE sr.equipment_id = ?
              AND sr.timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
              AND ABS(sr.{metric} - s.mean) / s.std > ?
            ORDER BY z_score DESC
        """, params=[equipment_id, equipment_id, threshold_std]).df()
    
    def predict_maintenance(self, equipment_id):
        """Predict maintenance needs based on sensor patterns."""
        return self.con.execute("""
            WITH sensor_trends AS (
                SELECT 
                    equipment_id,
                    sensor_type,
                    timestamp,
                    value,
                    LAG(value) OVER w as prev_value,
                    value - LAG(value) OVER w as trend,
                    AVG(value) OVER (
                        PARTITION BY equipment_id, sensor_type 
                        ORDER BY timestamp 
                        ROWS BETWEEN 100 PRECEDING AND CURRENT ROW
                    ) as rolling_avg
                FROM sensor_readings
                WHERE equipment_id = ?
            )
            SELECT 
                equipment_id,
                sensor_type,
                MAX(timestamp) as last_reading,
                AVG(trend) as avg_trend,
                CASE 
                    WHEN AVG(trend) > 0.1 THEN 'Needs Maintenance'
                    ELSE 'Normal'
                END as status
            FROM sensor_trends
            GROUP BY 1, 2
        """, params=[equipment_id]).df()
```

---

## 16. Design Decisions

### 16.1 DuckDB vs SQLite

| Aspect | DuckDB | SQLite |
|--------|--------|--------|
| **Primary Use Case** | Analytical queries (OLAP) | Transactional queries (OLTP) |
| **Storage Model** | Columnar | Row-based |
| **Execution Engine** | Vectorized | Row-by-row |
| **Compression** | Built-in, automatic | Limited |
| **SQL Features** | Advanced analytics, window functions | Basic SQL |
| **Performance (Aggregations)** | 10-100x faster | Slow |
| **Performance (Inserts)** | Slower | Faster |
| **File Size** | Larger (columnar) | Smaller |
| **Concurrency** | Limited (file locking) | Limited |
| **Embedded Size** | ~10MB | ~1MB |
| **JSON Support** | Excellent | Limited |

**Verdict**: Use DuckDB for analytics, ETL, data processing. Use SQLite for embedded/mobile applications requiring simple CRUD.

### 16.2 DuckDB vs PostgreSQL

| Aspect | DuckDB | PostgreSQL |
|--------|--------|-----------|
| **Architecture** | Embedded, in-process | Server-based |
| **Scaling** | Vertical only | Horizontal + Vertical |
| **Connections** | Single process | Multi-process |
| **Administration** | None | Significant |
| **SQL Compatibility** | PostgreSQL-like | Full PostgreSQL |
| **Extensions** | Growing ecosystem | Rich ecosystem |
| **Real-time Inserts** | Limited | Excellent |
| **Analytical Performance** | Excellent | Good |
| **Deployment Complexity** | None | High |
| **Cost** | Free (Apache 2.0) | Free / Supabase/Co了一片 |

**Verdict**: Use DuckDB for embedded analytics, ETL acceleration, local data processing. Use PostgreSQL for production applications requiring multi-user access, complex queries, and enterprise features.

### 16.3 DuckDB vs ClickHouse

| Aspect | DuckDB | ClickHouse |
|--------|--------|------------|
| **Architecture** | Embedded | Distributed cluster |
| **Deployment** | Single library | Complex cluster setup |
| **Scaling** | Vertical | Horizontal |
| **Real-time Inserts** | Limited | Excellent |
| **Query Latency** | Sub-second | Sub-millisecond |
| **SQL Dialect** | PostgreSQL-like | Native |
| **Updates/Deletes** | Limited | Full support |
| **Operational Overhead** | None | High |
| **Cost** | Low (single machine) | High (cluster) |

**Verdict**: Use DuckDB for data processing pipelines, embedded analytics, prototyping. Use ClickHouse for massive-scale production data warehouses requiring real-time inserts and sub-millisecond queries.

### 16.4 When to Use Each

```mermaid
flowchart TD
    Start["What are you building?"]
    
    Embedded["Embedded analytics\nin application?"]
    ETL["ETL pipeline\nacceleration?"]
    Warehouse["Data warehouse\nreplacement?"]
    Analytics["Interactive\nanalytics?"]
    
    DuckDB_Choice1["DuckDB ✓"]
    DuckDB_Choice2["DuckDB ✓"]
    ClickHouse["ClickHouse"]
    Postgres["PostgreSQL"]
    Spark["Spark/Dask"]
    
    Start --> Embedded
    Start --> ETL
    Start --> Warehouse
    Start --> Analytics
    
    Embedded --> DuckDB_Choice1
    ETL --> DuckDB_Choice2
    ETL --> Spark
    
    Warehouse --> ClickHouse
    Warehouse --> Postgres
    
    Analytics --> DuckDB_Choice2
    Analytics --> Postgres
    
    style DuckDB_Choice1 fill:#90EE90
    style DuckDB_Choice2 fill:#90EE90
```

---

## 17. Business Value

### 17.1 Cost Reduction

| Cost Factor | Before (Traditional DW) | After (DuckDB) |
|-------------|-------------------------|----------------|
| Infrastructure | $50K/month (AWS Redshift) | $5K/month (EC2) |
| Licenses | $20K/month | $0 (Apache 2.0) |
| DBA Overhead | 2 FTEs | 0.5 FTE |
| Data Transfer | $10K/month | $2K/month |
| **Total Monthly** | **$80K** | **$7.5K** |

**Savings: 90% reduction in analytics infrastructure costs**

### 17.2 Performance Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Dashboard Load Time | 45s | 2s | 22.5x faster |
| ETL Pipeline Duration | 4 hours | 25 minutes | 9.6x faster |
| Ad-hoc Query Time | 30s | 1.5s | 20x faster |
| Report Generation | 10 minutes | 30 seconds | 20x faster |

### 17.3 Business Outcomes

1. **Faster Decision Making**
   - Real-time visibility into sales and inventory
   - Reduced time from data to insight (from days to minutes)

2. **Reduced Technical Debt**
   - Simpler architecture (fewer moving parts)
   - Easier onboarding for new engineers
   - Reduced maintenance burden

3. **Increased Analyst Productivity**
   - Self-service analytics without waiting for data engineering
   - Direct querying of data files
   - Reduced dependency on data warehouse team

4. **Better Customer Experience**
   - Real-time product recommendations
   - Dynamic pricing based on demand
   - Personalized marketing campaigns

---

## 18. Future Improvements

### 18.1 Emerging Extensions

| Extension | Purpose | Status |
|-----------|---------|--------|
| **Iceberg** | Table format support | Stable |
| **Delta Lake** | Table format support | Beta |
| **Hudi** | Table format support | Planning |
| **Postgres FDW** | Foreign data wrapper | Stable |
| **MySQL FDW** | MySQL integration | Stable |
| **MongoDB FDW** | MongoDB integration | Beta |
| **Redis** | Cache integration | Planning |

### 18.2 Cloud Integration

**MotherDuck**: Managed DuckDB service
- Shared data layer
- Query federation
- Managed upgrades
- Enterprise security

```python
# Connect to MotherDuck
con = duckdb.connect("md:")

# Query shared data
result = con.execute("SELECT * FROM shared_db.sales").df()
```

### 18.3 ML Integration

```python
# DuckDB ML extension
con.execute("INSTALL ml; LOAD ml;")

# In-database model training
con.execute("""
    CREATE MODEL revenue_forecast
    FROM sales_data
    TARGET revenue
    FEATURES store_id, category, day_of_week, is_holiday
    USING regressor
""")

# Make predictions
result = con.execute("""
    SELECT *, PREDICT(revenue_forecast) as predicted_revenue
    FROM future_scenarios
""").df()
```

### 18.4 Performance Roadmap

| Feature | Current | Planned |
|---------|---------|---------|
| Parallel Writes | Limited | Full |
| Partition Pruning | Basic | Advanced |
| Cost-based Optimization | Good | Excellent |
| SIMD Utilization | SSE/AVX | AVX-512, Neon |
| Memory Management | Configurable | Adaptive |

---

## 19. References

### Official Documentation
- [DuckDB Documentation](https://duckdb.org/docs)
- [DuckDB SQL Reference](https://duckdb.org/docs/sql)
- [DuckDB Python API](https://duckdb.org/docs/api/python)

### Key Papers
- "DuckDB: An Embeddable Analytical Database" - Raasveldt & Mühleisen (2019)
- "Vectorized Query Execution" - Kersten et al.
- "Columnar Storage for Analytical Workloads"

### Learning Resources
- [DuckDB Examples](https://github.com/duckdb/duckdb/tree/main/examples)
- [Awesome DuckDB](https://github.com/davidgasquez/awesome-duckdb)
- [DuckDB Community Notebooks](https://duckdb.org/nb/)

### Blog Posts
- "Why DuckDB is the Future of Analytics"
- "Building Analytics Pipelines with DuckDB"
- "DuckDB vs Polars: A Comparison"

---

## 20. Skills Demonstrated

### Technical Skills

1. **Database Design**
   - Schema design for analytical workloads
   - Star and snowflake schema modeling
   - Index strategies for query optimization

2. **SQL Proficiency**
   - Complex aggregations and window functions
   - CTEs and subqueries
   - Advanced JOIN patterns
   - Query optimization with EXPLAIN

3. **Python Integration**
   - DuckDB Python API
   - Pandas integration
   - Connection management
   - Error handling

4. **Data Engineering**
   - ETL pipeline design
   - Incremental data loading
   - Schema evolution handling
   - Data quality frameworks

5. **Performance Optimization**
   - Query profiling
   - Memory management
   - Parallel execution
   - Index design

6. **System Architecture**
   - Microservices integration
   - Streaming architecture patterns
   - Lambda/Kappa architecture
   - Feature store design

### Business Skills

7. **Problem Solving**
   - Translating business requirements to technical solutions
   - Performance troubleshooting
   - Data quality management

8. **Communication**
   - Documenting technical decisions
   - Explaining complex concepts
   - Presenting findings

9. **Best Practices**
   - Security considerations
   - Production monitoring
   - Disaster recovery

---

*Document Version: 1.0*
*Last Updated: July 2026*
*Author: Enterprise Analytics Team*
