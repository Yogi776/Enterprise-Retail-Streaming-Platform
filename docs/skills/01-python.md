# Python Programming Language

## 1. Overview

### What is Python?

Python is a high-level, interpreted programming language founded by Guido van Rossum in 1991. It emphasizes code readability through its use of significant indentation and provides dynamic typing, garbage collection, and a comprehensive standard library. Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.

### Why was it created?

Guido van Rossum created Python in 1989-1991 at Centrum Wiskunde & Informatica (CWI) in the Netherlands as a successor to the ABC language. The goal was to create a language that was:
- Easy to read and understand
- Powerful enough to be useful for system administration and application development
- Capable of exception handling and interfacing with the Amoeba operating system

### What business problem does it solve?

Python solves critical enterprise problems:
- **Rapid Development**: 5-10x faster development cycles compared to compiled languages
- **Integration**: Connects disparate systems through extensive library ecosystem
- **Data Processing**: Handles massive datasets efficiently for analytics pipelines
- **Automation**: Reduces manual work through scripting and orchestration
- **ML/AI**: Powers machine learning and artificial intelligence initiatives

### Why do enterprises use it?

Fortune 500 companies choose Python because:
- Netflix uses it for 50% of their backend services and recommendation systems
- Dropbox processes 500M+ files using Python infrastructure
- Instagram serves 1B+ users with Django (Python web framework)
- Spotify uses Python for backend services and data pipelines
- JPMorgan's Athena platform processes millions of trades daily in Python

---

## 2. Core Concepts

### Python Execution Model

```mermaid
flowchart TD
    A[Source Code .py] --> B[Parser]
    B --> C[Python Compiler]
    C --> D[Bytecode .pyc]
    D --> E[Python Virtual Machine PVM]
    E --> F[Operating System]
    F --> G[Hardware]
```

### Key Concepts with Examples

**Variables and Data Types**
```python
# Primitive Types
integer: int = 42
floating_point: float = 3.14
boolean: bool = True
string: str = "Enterprise Retail"

# Complex Types
list: list[int] = [1, 2, 3, 4, 5]
dictionary: dict[str, Any] = {"product": "SKU123", "price": 29.99}
set: set[str] = {"apple", "banana", "orange"}
tuple: tuple[str, int] = ("SKU123", 100)
```

**Object-Oriented Programming**
```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Product:
    sku: str
    name: str
    price: float
    category_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    def calculate_margin(self, cost: float) -> float:
        return (self.price - cost) / self.price * 100
    
    def to_dict(self) -> dict:
        return {
            "sku": self.sku,
            "name": self.name,
            "price": self.price,
            "margin": self.calculate_margin
        }
```

**Context Managers and Resource Management**
```python
# File handling with context manager
with open("sales_data.csv", "r") as file:
    data = file.read()
    # File automatically closed after block

# Database connection management
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

**Async/Await for Concurrent Operations**
```python
import asyncio
from typing import List

async def fetch_product_data(sku: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"/api/products/{sku}") as response:
            return await response.json()

async def fetch_all_products(skus: List[str]) -> List[dict]:
    tasks = [fetch_product_data(sku) for sku in skus]
    return await asyncio.gather(*tasks)
```

**Generator and Iterator Patterns**
```python
def streaming_orders_processor(orders: list[dict]):
    """Memory-efficient processing of large datasets"""
    for order in orders:
        yield process_single_order(order)

def batch_processor(batch_size: int = 1000):
    """Batch generator for chunk processing"""
    offset = 0
    while True:
        batch = db.query(
            "SELECT * FROM orders LIMIT ? OFFSET ?",
            batch_size, offset
        )
        if not batch:
            break
        yield batch
        offset += batch_size
```

---

## 3. Why This Project Uses It

The Enterprise Retail Streaming Platform uses Python extensively for the following reasons:

**1. Stream Processing with Apache Flink**
- Flink's DataStream API is natively implemented in Java
- However, the platform uses Python for:
  - Flink SQL queries and transformations
  - Stateful function implementations via Python Table API
  - Data enrichment functions and user-defined functions (UDFs)

**2. Data Engineering and ETL Pipelines**
- Apache Airflow (Python) orchestrates all data pipelines
- Python's pandas and polars libraries for data transformation
- Great Expectations for data quality validation

**3. GraphQL API Layer**
- Graphene-Python library for implementing GraphQL schemas
- Strawberry GraphQL for type-safe GraphQL implementations
- Ariadne for schema-first GraphQL development

**4. Machine Learning and Analytics**
- Scikit-learn for demand forecasting models
- XGBoost for inventory optimization
- Prophet for seasonal trend analysis
- PyTorch for recommendation engines

**5. Infrastructure as Code**
- Terraform configurations validated with Python scripts
- Ansible playbooks written in Python
- Custom AWS Lambda functions in Python

**6. Real-Time Analytics**
- Apache Kafka Connect handlers in Python
- Faust (Python stream processing library) for micro-batch pipelines
- Redis Streams consumer applications

**7. Observability and Monitoring**
- Prometheus client library for metrics exposition
- OpenTelemetry instrumentation in Python services
- Custom alerting and anomaly detection scripts

---

## 4. Architecture Position

Python occupies multiple layers in the platform architecture:

```mermaid
flowchart TB
    subgraph Sources["Data Sources"]
        POS[POS Systems]
        ECOM[E-Commerce Platform]
        CRM[CRM System]
        INV[Inventory System]
    end

    subgraph Ingestion["Ingestion Layer"]
        KAFKA[Apache Kafka]
    end

    subgraph StreamProcess["Stream Processing Layer"]
        FLINK[Apache Flink]
        PYTHON_UDF[Python UDFs]
        FAUST[Faust Streams]
    end

    subgraph Storage["Storage Layer"]
        ICEBERG[Apache Iceberg]
        POSTGRES[PostgreSQL]
        MINIO[MinIO S3]
    end

    subgraph Query["Query & Serve Layer"]
        TRINO[Trino]
        GRAPHQL[GraphQL API]
    end

    subgraph Application["Application Layer"]
        NEXTJS[Next.js Frontend]
        PYTHON_BE[Python Backend]
    end

    subgraph ML["ML & Analytics"]
        SKLEARN[Scikit-learn]
        PROPHET[Prophet]
        SUPERSET[Superset]
    end

    Sources --> Ingestion
    Ingestion --> StreamProcess
    StreamProcess --> Storage
    Storage --> Query
    Query --> Application
    Application --> ML
    FLINK <--> PYTHON_UDF
    TRINO --> PYTHON_BE
    PYTHON_BE --> GRAPHQL
    PYTHON_BE --> NEXTJS
```

---

## 5. Folder Structure

```
retail-streaming-platform/
├── src/
│   ├── python/                     # Python source code
│   │   ├── __init__.py
│   │   ├── config/                 # Configuration management
│   │   │   ├── __init__.py
│   │   │   ├── settings.py         # Application settings
│   │   │   ├── database.py         # Database configuration
│   │   │   └── kafka.py            # Kafka configuration
│   │   ├── models/                 # Data models
│   │   │   ├── __init__.py
│   │   │   ├── product.py          # Product model
│   │   │   ├── order.py            # Order model
│   │   │   ├── customer.py         # Customer model
│   │   │   └── inventory.py        # Inventory model
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── product_service.py
│   │   │   ├── order_service.py
│   │   │   ├── analytics_service.py
│   │   │   └── enrichment_service.py
│   │   ├── api/                    # API layer
│   │   │   ├── __init__.py
│   │   │   ├── graphql/            # GraphQL schemas
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schema.py
│   │   │   │   ├── types.py
│   │   │   │   ├── queries.py
│   │   │   │   └── mutations.py
│   │   │   └── rest/               # REST endpoints
│   │   │       ├── __init__.py
│   │   │       └── health.py
│   │   ├── pipeline/               # Data pipelines
│   │   │   ├── __init__.py
│   │   │   ├── extractors/
│   │   │   ├── transformers/
│   │   │   └── loaders/
│   │   ├── ml/                     # Machine learning
│   │   │   ├── __init__.py
│   │   │   ├── models/
│   │   │   ├── features/
│   │   │   └── training/
│   │   ├── utils/                  # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── logging.py
│   │   │   ├── tracing.py
│   │   │   └── retry.py
│   │   └── tests/                 # Unit tests
│   │       ├── __init__.py
│   │       ├── unit/
│   │       └── integration/
├── scripts/
│   ├── setup_python_env.sh
│   ├── run_tests.py
│   └── generate_types.py
├── pyproject.toml                  # Poetry project configuration
├── requirements.txt                # pip dependencies
├── Dockerfile.python               # Python service Dockerfile
├── docker-compose.python.yml
├── Makefile
└── README.md
```

---

## 6. Implementation Walkthrough

### Configuration Management

**pyproject.toml (Poetry)**
```toml
[tool.poetry]
name = "retail-streaming-platform"
version = "1.0.0"
description = "Enterprise Retail Streaming Platform"
authors = ["Enterprise Engineering Team"]

[tool.poetry.dependencies]
python = "^3.11"
# Web Framework
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
starlette = "^0.34.0"

# GraphQL
strawberry-graphql = "^0.217.0"
graphene = "^3.3"

# Database
psycopg2-binary = "^2.9.9"
asyncpg = "^0.29.0"
sqlalchemy = "^2.0.25"
alembic = "^1.13.1"

# Kafka & Streaming
aiokafka = "^0.10.0"
faust = "^1.13.0"
kafka-python = "^2.0.2"

# Data Processing
pandas = "^2.2.0"
polars = "^0.20.0"
pyarrow = "^15.0.0"

# Validation & Testing
pydantic = "^2.5.3"
pydantic-settings = "^2.1.0"
pytest = "^7.4.4"
pytest-asyncio = "^0.23.3"
pytest-cov = "^4.1.0"

# Observability
prometheus-client = "^0.19.0"
opentelemetry-api = "^1.22.0"
opentelemetry-sdk = "^1.22.0"
opentelemetry-instrumentation-fastapi = "^0.43b0"

# Cloud Storage
boto3 = "^1.34.0"
minio = "^7.2.0"

# ML
scikit-learn = "^1.4.0"
xgboost = "^2.0.3"
prophet = "^1.1.5"

[tool.poetry.group.dev.dependencies]
black = "^24.1.0"
isort = "^5.13.2"
mypy = "^1.8.0"
ruff = "^0.1.13"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Environment Variables

**.env.example**
```bash
# Application
APP_ENV=production
APP_NAME=retail-streaming-platform
APP_VERSION=1.0.0
LOG_LEVEL=INFO

# Database
DATABASE_HOST=postgres.internal
DATABASE_PORT=5432
DATABASE_NAME=retail_analytics
DATABASE_USER=app_service
DATABASE_PASSWORD=<secret>
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka-1:9092,kafka-2:9092,kafka-3:9092
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_SASL_USERNAME=<secret>
KAFKA_SASL_PASSWORD=<secret>
KAFKA_CONSUMER_GROUP=retail-platform-consumer
KAFKA_AUTO_OFFSET_RESET=earliest

# MinIO / S3
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=<secret>
S3_SECRET_KEY=<secret>
S3_BUCKET_NAME=retail-data
S3_REGION=us-east-1

# GraphQL
GRAPHQL_PATH=/graphql
GRAPHQL_PLAYGROUND=True

# ML Model Paths
MODEL_REGISTRY_PATH=s3://retail-models/
DEMAND_FORECAST_MODEL_PATH=models/demand_forecast_v2.pkl
INVENTORY_MODEL_PATH=models/inventory_optimization.pkl

# Observability
OTEL_SERVICE_NAME=retail-python-service
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
PROMETHEUS_PORT=9090
```

### Docker Setup

**Dockerfile.python**
```dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

FROM base as builder

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (production only)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev

FROM base as production

WORKDIR /app

# Copy built artifacts
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create non-root user
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash appuser

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()"

# Run application
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.python.yml**
```yaml
version: '3.8'

services:
  python-api:
    build:
      context: .
      dockerfile: Dockerfile.python
      target: production
    container_name: retail-python-api
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=${APP_ENV}
      - DATABASE_HOST=${DATABASE_HOST}
      - DATABASE_PORT=${DATABASE_PORT}
      - KAFKA_BOOTSTRAP_SERVERS=${KAFKA_BOOTSTRAP_SERVERS}
      - S3_ENDPOINT_URL=${S3_ENDPOINT_URL}
    env_file:
      - .env
    volumes:
      - ./src:/app/src:ro
    depends_on:
      - postgres
      - kafka
      - minio
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health').raise_for_status()"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - retail-network

  python-worker:
    build:
      context: .
      dockerfile: Dockerfile.python
      target: production
    container_name: retail-python-worker
    command: ["python", "-m", "faust", "-A", "src.pipeline.faust_app", "agent"]
    environment:
      - APP_ENV=${APP_ENV}
      - KAFKA_BOOTSTRAP_SERVERS=${KAFKA_BOOTSTRAP_SERVERS}
    env_file:
      - .env
    depends_on:
      - kafka
    restart: unless-stopped
    networks:
      - retail-network

networks:
  retail-network:
    driver: bridge
```

### Application Lifecycle

**Main Application Entry Point (src/api/main.py)**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from src.config.settings import get_settings
from src.api.graphql.schema import schema
from src.api.rest.health import router as health_router
from src.utils.logging import setup_logging
from src.utils.tracing import setup_tracing

settings = get_settings()
setup_logging(level=settings.log_level)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize connections
    await initialize_database_pool()
    await initialize_kafka_consumers()
    initialize_model_registry()
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_database_connections()
    await close_kafka_consumers()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(graphql_router, prefix="/graphql")

# OpenTelemetry instrumentation
FastAPIInstrumentor.instrument_app(app)

@app.get("/")
async def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }
```

### Startup and Shutdown Sequences

**Startup Sequence:**
1. Load environment variables via Pydantic Settings
2. Initialize logging and tracing
3. Create database connection pool
4. Initialize Kafka consumer groups
5. Load ML models into memory
6. Start FastAPI server
7. Begin background Faust workers

**Shutdown Sequence:**
1. Stop accepting new requests
2. Complete in-flight requests (30s timeout)
3. Flush pending Kafka messages
4. Save model state to registry
5. Close database connections gracefully
6. Exit process

---

## 7. Production Best Practices

### Scalability

**Horizontal Scaling**
```python
# Use multiple worker processes with uvicorn
# In docker-compose:
# command: ["uvicorn", "src.api.main:app", "--workers", "4", "--host", "0.0.0.0"]

# Use gunicorn as process manager
# gunicorn.conf.py
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5
```

**Connection Pooling**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### Monitoring

**Custom Metrics**
```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Business metrics
ORDERS_PROCESSED = Counter('orders_processed_total', 'Total orders processed')
ACTIVE_PRODUCTS = Gauge('active_products', 'Number of active products')
INVENTORY_ALERTS = Counter('inventory_alerts_total', 'Total inventory alerts')

# Usage in code
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response
```

### Logging

**Structured Logging Configuration**
```python
import logging
import json
from datetime import datetime
from typing import Any

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_data["user_id"] = record.user_id
        
        return json.dumps(log_data)

def setup_logging(level: str = "INFO"):
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Set third-party loggers to WARNING
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
```

### Security

**Secrets Management**
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database credentials from environment or secrets manager
    database_password: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @classmethod
    def from_aws_secrets(cls, secret_name: str) -> "Settings":
        import boto3
        client = boto3.client("secretsmanager")
        secret = client.get_secret_value(SecretId=secret_name)
        return cls(**json.loads(secret["SecretString"]))
```

**Input Validation**
```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class OrderInput(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50, pattern=r"^[A-Z0-9-]+$")
    quantity: int = Field(..., ge=1, le=10000)
    unit_price: float = Field(..., gt=0)
    customer_id: Optional[str] = None
    
    @validator("sku")
    def validate_sku(cls, v):
        if not v.startswith(("PROD-", "SKU-", "ITEM-")):
            raise ValueError("SKU must start with PROD-, SKU-, or ITEM-")
        return v.upper()
    
    @validator("unit_price")
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Price cannot be negative")
        return round(v, 2)
```

---

## 8. Common Problems

| Problem | Cause | Resolution | Best Practice |
|---------|-------|------------|---------------|
| **Memory leaks in long-running workers** | Unclosed database connections, accumulated objects in memory | Use context managers, implement connection pool recycling | Set `max_requests` and restart workers periodically |
| **Slow startup time** | Loading large ML models synchronously | Load models lazily, use model warmup endpoint | Pre-load models in Dockerfile COPY, use model registry |
| **GIL contention in multi-threaded code** | Python's Global Interpreter Lock prevents true parallelism | Use multiprocessing, async/await, or move CPU-bound work to C extensions | Use `uvicorn --workers` for multi-process deployment |
| **Database connection exhaustion** | Connection pool too small, connections not returned | Increase pool size, ensure all connections closed in finally blocks | Use `pool_pre_ping=True`, monitor `pool_overflow` |
| **Serialization errors with Pydantic** | Mismatched types between API and database models | Use explicit serializers, validate at boundaries | Create separate API vs DB models |
| **Circular imports** | Poor module organization | Use lazy imports, restructure imports | Follow clean architecture dependency injection |
| **Environment variable typos** | No validation of required vars | Use Pydantic Settings with validation | Fail fast on missing required configuration |
| **Slow pytest suite** | Database fixtures not properly scoped | Use session-scoped fixtures, parallel test execution | Run tests with `pytest-xdist`, mock external services |

---

## 9. Performance Optimization

### Memory Optimization

**Object Pooling**
```python
from contextlib import contextmanager
from queue import Queue, Empty
import threading

class ObjectPool:
    def __init__(self, factory, max_size=10):
        self.factory = factory
        self.max_size = max_size
        self._pool = Queue(max_size)
        self._lock = threading.Lock()
    
    def acquire(self):
        try:
            return self._pool.get_nowait()
        except Empty:
            return self.factory()
    
    def release(self, obj):
        try:
            self._pool.put_nowait(obj)
        except:
            pass  # Pool full, discard object

# Usage for expensive object creation
model_pool = ObjectPool(lambda: load_model(), max_size=3)

async def get_model():
    model = model_pool.acquire()
    try:
        yield model
    finally:
        model_pool.release(model)
```

**Lazy Evaluation**
```python
from functools import lru_cache, cached_property
from typing import Iterator

class DataPipeline:
    def __init__(self, data_source):
        self.data_source = data_source
    
    @cached_property
    def expensive_transform(self):
        # Only computed once, then cached
        return self._compute_expensive_transform()
    
    def stream_processing(self, batch_size=1000) -> Iterator[list]:
        """Memory-efficient streaming"""
        offset = 0
        while True:
            batch = self.data_source.fetch(offset, batch_size)
            if not batch:
                break
            yield [self._transform(item) for item in batch]
            offset += batch_size
```

### CPU Optimization

**NumPy and Vectorization**
```python
import numpy as np
import pandas as pd

# Slow: Python loops
def calculate_revenue_python(orders):
    revenue = 0
    for order in orders:
        revenue += order["quantity"] * order["price"]
    return revenue

# Fast: NumPy vectorization
def calculate_revenue_numpy(orders):
    return np.sum(orders["quantity"] * orders["price"])

# pandas vectorization
def calculate_revenue_pandas(orders_df):
    return (orders_df["quantity"] * orders_df["price"]).sum()
```

**Concurrent Processing**
```python
import asyncio
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

def cpu_intensive_task(data):
    # CPU-bound work
    return expensive_computation(data)

# For CPU-bound: use ProcessPoolExecutor
with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
    results = list(executor.map(cpu_intensive_task, data_chunks))

# For I/O-bound: use asyncio
async def io_intensive_task(data):
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[
            fetch_data(session, url) for url in data["urls"]
        ])
    return results
```

### Batching and Caching

**Batch Processing Pattern**
```python
from typing import Iterator, List, TypeVar
import asyncio

T = TypeVar('T')

async def batch_process(
    items: Iterator[T],
    batch_size: int = 100,
    max_concurrent: int = 10
) -> List[dict]:
    """Process items in batches with concurrency control"""
    semaphore = asyncio.Semaphore(max_concurrent)
    batches = []
    current_batch = []
    
    for item in items:
        current_batch.append(item)
        if len(current_batch) >= batch_size:
            batches.append(current_batch)
            current_batch = []
    
    if current_batch:
        batches.append(current_batch)
    
    async def process_batch(batch):
        async with semaphore:
            return await process(batch)
    
    results = await asyncio.gather(*[process_batch(b) for b in batches])
    return results

# Usage with chunking
def chunked_iterator(data: List, chunk_size: int) -> Iterator[List]:
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]
```

**Redis Caching**
```python
import redis.asyncio as redis
import json
from functools import wraps
from typing import Any, Callable

redis_client = redis.from_url("redis://localhost:6379")

def cache_result(ttl: int = 300):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            await redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            return result
        return wrapper
    return decorator

@cache_result(ttl=600)
async def get_product_analytics(sku: str, date_range: str):
    # Expensive computation
    return await compute_analytics(sku, date_range)
```

### Partitioning Strategies

```python
from typing import List, Callable, TypeVar
from concurrent.futures import ThreadPoolExecutor

T = TypeVar('T')
R = TypeVar('R')

def partition_work(
    items: List[T],
    num_partitions: int,
    worker_func: Callable[[List[T]], List[R]]
) -> List[List[R]]:
    """Partition work across multiple threads"""
    chunk_size = (len(items) + num_partitions - 1) // num_partitions
    partitions = [
        items[i:i + chunk_size] 
        for i in range(0, len(items), chunk_size)
    ]
    
    with ThreadPoolExecutor(max_workers=num_partitions) as executor:
        results = list(executor.map(worker_func, partitions))
    
    return results

# Usage for parallel data processing
def process_partition(orders: List[dict]) -> List[dict]:
    return [calculate_order_metrics(o) for o in orders]

all_results = partition_work(
    orders, 
    num_partitions=8, 
    worker_func=process_partition
)
```

---

## 10. Security

### Authentication

**JWT Authentication**
```python
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta

security = HTTPBearer()

class AuthService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(hours=1))
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

auth_service = AuthService(secret_key=settings.jwt_secret)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    return {"user_id": user_id, "roles": payload.get("roles", [])}
```

**Role-Based Access Control (RBAC)**
```python
from enum import Enum
from functools import wraps
from fastapi import HTTPException

class Role(Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    STORE_MANAGER = "store_manager"
    VIEWER = "viewer"

ROLE_PERMISSIONS = {
    Role.ADMIN: ["read", "write", "delete", "admin"],
    Role.ANALYST: ["read", "write"],
    Role.STORE_MANAGER: ["read", "write"],
    Role.VIEWER: ["read"]
}

def require_roles(*roles: Role):
    def decorator(func):
        @wraps(func)
        async def wrapper(current_user: dict = Depends(get_current_user), *args, **kwargs):
            user_roles = [Role(r) for r in current_user.get("roles", [])]
            
            if not any(role in roles for role in user_roles):
                raise HTTPException(
                    status_code=403,
                    detail=f"Requires one of roles: {[r.value for r in roles]}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@app.get("/admin/users")
@require_roles(Role.ADMIN)
async def list_users(current_user: dict = Depends(get_current_user)):
    return {"users": []}
```

### Encryption

**Encryption at Rest**
```python
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode

class EncryptionService:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    @classmethod
    def generate_key(cls) -> bytes:
        return Fernet.generate_key()
    
    def encrypt(self, data: str) -> str:
        encrypted = self.cipher.encrypt(data.encode())
        return b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        decoded = b64decode(encrypted_data.encode())
        return self.cipher.decrypt(decoded).decode()

# Usage with PII fields
import pgp as encryption

class CustomerService:
    def __init__(self):
        self.encryption_service = EncryptionService(
            settings.encryption_key
        )
    
    async def create_customer(self, customer_data: dict) -> dict:
        # Encrypt PII before storage
        customer_data["email"] = self.encryption_service.encrypt(
            customer_data["email"]
        )
        customer_data["phone"] = self.encryption_service.encrypt(
            customer_data["phone"]
        )
        
        return await self.db.insert("customers", customer_data)
```

**TLS/SSL Configuration**
```python
# For HTTP clients (requests/aiohttp)
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED
ssl_context.load_verify_locations("/path/to/ca-bundle.crt")

async def fetch_secure(url: str) -> dict:
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=ssl_context)
    ) as session:
        async with session.get(url) as response:
            return await response.json()

# For database connections
DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/db?ssl=true&sslmode=require"
```

### Secrets Management

**AWS Secrets Manager Integration**
```python
import boto3
import json
from functools import lru_cache

class SecretsManager:
    def __init__(self, region_name: str = "us-east-1"):
        self.client = boto3.client("secretsmanager", region_name=region_name)
    
    @lru_cache(maxsize=1)
    def get_secret(self, secret_name: str) -> dict:
        response = self.client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    
    def get_database_credentials(self) -> dict:
        return self.get_secret("prod/retail/database")
    
    def get_kafka_credentials(self) -> dict:
        return self.get_secret("prod/retail/kafka")

secrets_manager = SecretsManager()

# Usage in Settings
class Settings(BaseSettings):
    database_password: str
    
    @classmethod
    def from_secrets(cls):
        db_creds = secrets_manager.get_database_credentials()
        return cls(database_password=db_creds["password"])
```

---

## 11. Monitoring

### Metrics

**Prometheus Metrics Library**
```python
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, 
    Info, Enum, CollectorRegistry
)
from prometheus_client.registry import REGISTRY

# Custom metrics
HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency distribution",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

ACTIVE_CONNECTIONS = Gauge(
    "active_database_connections",
    "Number of active database connections",
    ["database"]
)

QUEUE_DEPTH = Gauge(
    "kafka_consumer_queue_depth",
    "Messages waiting in consumer queue",
    ["consumer_group", "topic"]
)

PROCESSING_LATENCY = Summary(
    "order_processing_latency_seconds",
    "Time to process individual orders",
    ["store_id"]
)

# Service info
SERVICE_INFO = Info(
    "retail_platform_service",
    "Service version and environment"
)
SERVICE_INFO.info({
    "version": settings.app_version,
    "environment": settings.app_env
})

# Business metrics Enum
PipelineStatus = Enum(
    "data_pipeline_status",
    "Current status of data pipelines",
    ["pipeline_name"],
    states=["running", "stopped", "error", "unknown"]
)
```

**Custom Business Metrics**
```python
class BusinessMetrics:
    def __init__(self):
        self.orders_total = Counter(
            "retail_orders_total",
            "Total orders processed",
            ["store_id", "channel"]
        )
        self.revenue = Counter(
            "retail_revenue_total",
            "Total revenue processed",
            ["store_id", "category"]
        )
        self.inventory_ratio = Gauge(
            "inventory_stock_ratio",
            "Current inventory to sales ratio",
            ["store_id", "product_category"]
        )
        self.forecast_accuracy = Histogram(
            "demand_forecast_error_percentage",
            "Demand forecast error",
            ["product_category"],
            buckets=(1, 5, 10, 15, 20, 25, 50)
        )
    
    def record_order(self, store_id: str, channel: str, amount: float):
        self.orders_total.labels(store_id=store_id, channel=channel).inc()
        self.revenue.labels(store_id=store_id, category="general").inc(amount)
    
    def record_forecast_error(self, category: str, error_pct: float):
        self.forecast_accuracy.labels(product_category=category).observe(error_pct)

metrics = BusinessMetrics()
```

### Alerts

**Alert Rules (Prometheus/AlertManager)**
```yaml
groups:
  - name: retail_platform
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status_code=~"5.."}[5m]) / 
          rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"
      
      # Service down
      - alert: ServiceDown
        expr: up{job="retail-python-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
      
      # High latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95, 
            rate(http_request_duration_seconds_bucket[5m])
          ) > 2.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API latency"
          description: "95th percentile latency is {{ $value }}s"
      
      # Connection pool exhaustion
      - alert: DatabaseConnectionPoolExhausted
        expr: |
          active_database_connections / pool_size >= 0.9
        for: 2m
        labels:
          severity: warning
```

### Dashboards

**Grafana Dashboard JSON**
```json
{
  "dashboard": {
    "title": "Retail Platform - Python Services",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "gauge",
        "targets": [
          {
            "expr": "rate(http_requests_total{status_code=~\"5..\"}[5m]) / rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "P95 Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Active Connections",
        "type": "stat",
        "targets": [
          {
            "expr": "active_database_connections"
          }
        ]
      }
    ]
  }
}
```

### Health Checks

**Liveness and Readiness Probes**
```python
from fastapi import FastAPI, Response
from pydantic import BaseModel
import psycopg2
import kafka

app = FastAPI()

class HealthStatus(BaseModel):
    status: str
    checks: dict

@app.get("/health/live")
async def liveness():
    """Basic liveness check - is the process running?"""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    """Readiness check - is the service ready to handle requests?"""
    checks = {}
    is_ready = True
    
    # Database check
    try:
        conn = psycopg2.connect(settings.database_url)
        conn.close()
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
        is_ready = False
    
    # Kafka check
    try:
        producer = kafka.KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            request_timeout_ms=5000
        )
        producer.close()
        checks["kafka"] = "healthy"
    except Exception as e:
        checks["kafka"] = f"unhealthy: {str(e)}"
        is_ready = False
    
    # S3/MinIO check
    try:
        s3_client.head_bucket(Bucket=settings.s3_bucket)
        checks["storage"] = "healthy"
    except Exception as e:
        checks["storage"] = f"unhealthy: {str(e)}"
        is_ready = False
    
    status_code = 200 if is_ready else 503
    return HealthStatus(status="ready" if is_ready else "not_ready", checks=checks)
```

### Logging and Tracing

**OpenTelemetry Integration**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import Status, StatusCode

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer_provider = trace.get_tracer_provider()

otlp_exporter = OTLPSpanExporter(
    endpoint="http://otel-collector:4317",
    insecure=True
)
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

tracer = trace.get_tracer(__name__)

# Custom span creation
@app.middleware("http")
async def tracing_middleware(request: Request, call_next):
    with tracer.start_as_current_span(
        f"{request.method} {request.url.path}",
        kind=trace.SpanKind.SERVER
    ) as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        span.set_attribute("http.host", request.headers.get("host", ""))
        
        try:
            response = await call_next(request)
            span.set_attribute("http.status_code", response.status_code)
            return response
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise

# Add request ID to logs
import uuid

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    # Add to logging context
    structlog.contextvars.clear()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

---

## 12. Testing Strategy

### Unit Testing

**pytest Configuration**
```python
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
filterwarnings =
    ignore::DeprecationWarning
```

**Unit Test Example**
```python
# tests/unit/test_order_service.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.services.order_service import OrderService
from src.models.order import Order, OrderStatus
from src.exceptions import OrderNotFoundError, InsufficientInventoryError

class TestOrderService:
    @pytest.fixture
    def order_service(self):
        return OrderService(
            order_repository=Mock(),
            inventory_service=Mock(),
            notification_service=Mock()
        )
    
    @pytest.fixture
    def sample_order(self):
        return Order(
            id="order-123",
            sku="SKU-001",
            quantity=5,
            unit_price=29.99,
            customer_id="cust-456",
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow()
        )
    
    def test_calculate_order_total(self, order_service, sample_order):
        total = order_service.calculate_order_total(sample_order)
        assert total == 149.95
    
    def test_calculate_order_total_with_discount(self, order_service, sample_order):
        sample_order.discount = 10.0  # $10 discount
        total = order_service.calculate_order_total(sample_order)
        assert total == 139.95
    
    @pytest.mark.asyncio
    async def test_create_order_success(self, order_service, sample_order):
        order_service.inventory_service.check_availability = AsyncMock(return_value=True)
        order_service.order_repository.create = AsyncMock(return_value=sample_order)
        
        result = await order_service.create_order(
            sku="SKU-001",
            quantity=5,
            customer_id="cust-456"
        )
        
        assert result.id == "order-123"
        assert result.status == OrderStatus.PENDING
        order_service.inventory_service.check_availability.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_order_insufficient_inventory(self, order_service):
        order_service.inventory_service.check_availability = AsyncMock(return_value=False)
        
        with pytest.raises(InsufficientInventoryError):
            await order_service.create_order(
                sku="SKU-001",
                quantity=1000,
                customer_id="cust-456"
            )
```

**Mocking Strategies**
```python
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import pytest

# Synchronous mocking
def test_sync_mocking():
    mock_repository = Mock()
    mock_repository.get_by_id.return_value = {"id": 1, "name": "Test"}
    
    service = MyService(repository=mock_repository)
    result = service.get_item(1)
    
    assert result["name"] == "Test"
    mock_repository.get_by_id.assert_called_once_with(1)

# Async mocking
@pytest.mark.asyncio
async def test_async_mocking():
    mock_client = AsyncMock()
    mock_client.fetch.return_value = {"data": "test"}
    
    service = MyAsyncService(http_client=mock_client)
    result = await service.fetch_data("http://api.example.com")
    
    assert result == {"data": "test"}

# Patch decorator
@patch("src.services.external_api.requests.get")
def test_patch_decorator(mock_get):
    mock_get.return_value.json.return_value = {"price": 29.99}
    
    result = get_product_price("SKU-001")
    
    assert result == 29.99
    mock_get.assert_called_once()
```

### Integration Testing

**Test Containers**
```python
# tests/integration/conftest.py
import pytest
import testcontainers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="module")
def postgres_container():
    with testcontainers.postgres.Postgres() as postgres:
        yield postgres

@pytest.fixture(scope="module")
def db_engine(postgres_container):
    engine = create_engine(postgres_container.get_connection_url())
    yield engine
    engine.dispose()

@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
```

**Integration Test Example**
```python
# tests/integration/test_order_flow.py
import pytest
from httpx import AsyncClient
from app import create_app

@pytest.fixture
async def app_client():
    app = await create_app()
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_complete_order_flow(app_client):
    # Create order
    response = await app_client.post("/api/v1/orders", json={
        "sku": "SKU-001",
        "quantity": 5,
        "customer_id": "cust-123"
    })
    assert response.status_code == 201
    order = response.json()
    order_id = order["id"]
    
    # Get order
    response = await app_client.get(f"/api/v1/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["id"] == order_id
    
    # Cancel order
    response = await app_client.delete(f"/api/v1/orders/{order_id}")
    assert response.status_code == 200
    
    # Verify cancellation
    response = await app_client.get(f"/api/v1/orders/{order_id}")
    assert response.json()["status"] == "cancelled"
```

### End-to-End Testing

**E2E with Playwright**
```python
# tests/e2e/test_retail_platform.py
import pytest
from playwright.async_api import async_playwright

@pytest.fixture
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        yield browser
        await browser.close()

@pytest.fixture
async def authenticated_page(browser):
    page = await browser.new_page()
    # Perform authentication
    await page.goto("http://localhost:3000/login")
    await page.fill("[name=email]", "test@example.com")
    await page.fill("[name=password]", "testpassword")
    await page.click("[type=submit]")
    await page.wait_for_url("**/dashboard")
    yield page
    await page.close()

@pytest.mark.asyncio
async def test_order_creation_flow(authenticated_page):
    # Navigate to order form
    await authenticated_page.click('text=New Order')
    
    # Fill order form
    await authenticated_page.select_option('[name=sku]', 'SKU-001')
    await authenticated_page.fill('[name=quantity]', '5')
    
    # Submit and verify
    await authenticated_page.click('text=Submit Order')
    await authenticated_page.wait_for_selector('.order-confirmation')
    
    confirmation = await authenticated_page.text_content('.order-confirmation')
    assert "Order #" in confirmation
```

### Load Testing

**locustfile.py**
```python
from locust import HttpUser, task, between
import random

class RetailPlatformUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "email": "loadtest@example.com",
            "password": "loadtest123"
        })
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def browse_products(self):
        self.client.get("/api/v1/products", headers=self.headers)
    
    @task(2)
    def view_product(self):
        sku = f"SKU-{random.randint(1, 1000):03d}"
        self.client.get(f"/api/v1/products/{sku}", headers=self.headers)
    
    @task(1)
    def create_order(self):
        self.client.post("/api/v1/orders", headers=self.headers, json={
            "sku": f"SKU-{random.randint(1, 1000):03d}",
            "quantity": random.randint(1, 10)
        })
    
    @task(1)
    def view_dashboard(self):
        self.client.get("/api/v1/dashboard", headers=self.headers)
```

### Failure Testing

**Chaos Engineering**
```python
# tests/chaos/test_database_failures.py
import pytest
from unittest.mock import patch
from sqlalchemy.exc import OperationalError

@pytest.mark.asyncio
async def test_graceful_database_failure():
    with patch('app.database.get_session') as mock_get_session:
        mock_get_session.side_effect = OperationalError(
            "Connection refused", None, None
        )
        
        response = await ac.get("/api/v1/products")
        
        # Should return 503, not 500
        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_circuit_breaker_opens():
    circuit_breaker = CircuitBreaker(failure_threshold=3)
    
    # Trigger failures
    for _ in range(3):
        with pytest.raises(ServiceUnavailable):
            circuit_breaker.call(failing_service)
    
    # Circuit should be open
    assert circuit_breaker.state == CircuitState.OPEN
    
    # Subsequent calls should be fast-failed
    start = time.time()
    with pytest.raises(CircuitOpenError):
        circuit_breaker.call(failing_service)
    assert time.time() - start < 0.1  # Fast fail
```

---

## 13. Interview Preparation

### Beginner Questions (30)

**Q1: What is the difference between a list and a tuple in Python?**
A: Lists are mutable (can be modified after creation), while tuples are immutable (cannot be modified after creation). This makes tuples more memory-efficient and can be used as dictionary keys. Lists use more memory and can grow/shrink dynamically, while tuples have fixed sizes.

```python
my_list = [1, 2, 3]  # Mutable
my_tuple = (1, 2, 3)  # Immutable

my_list[0] = 10  # OK
# my_tuple[0] = 10  # TypeError
```

**Q2: What is the difference between `==` and `is`?**
A: `==` checks for value equality (calls `__eq__` method), while `is` checks for identity (whether two variables point to the same object in memory).

```python
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)  # True (same values)
print(a is b)  # False (different objects)

c = a
print(a is c)  # True (same object)
```

**Q3: What is a Python decorator?**
A: A decorator is a function that modifies the behavior of another function or method. It uses the `@` syntax and wraps the original function.

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before function")
        result = func(*args, **kwargs)
        print("After function")
        return result
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# Output:
# Before function
# Hello!
# After function
```

**Q4: What is the purpose of `__init__.py` files in Python?**
A: They mark directories as Python packages. They can also execute initialization code when the package is imported and define the `__all__` variable to control wildcard imports.

**Q5: What is the difference between `append()` and `extend()`?**
A: `append()` adds a single element to the end of a list, while `extend()` adds all elements from an iterable.

```python
a = [1, 2]
a.append([3, 4])  # [1, 2, [3, 4]]
a.extend([5, 6]) # [1, 2, [3, 4], 5, 6]
```

**Q6: What is a dictionary comprehension?**
A: A concise way to create dictionaries using a single line of code with key-value pairs.

```python
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

**Q7: What is the Global Interpreter Lock (GIL)?**
A: The GIL is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecode simultaneously. This means CPU-bound Python code doesn't benefit from threading.

**Q8: How do you handle exceptions in Python?**
A: Using try-except blocks:

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Generic error: {e}")
else:
    print("No errors")
finally:
    print("Cleanup")
```

**Q9: What is the difference between `range()` and `enumerate()`?**
A: `range()` generates a sequence of numbers, while `enumerate()` adds an index to an iterable.

```python
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

for i, val in enumerate(['a', 'b', 'c']):
    print(f"{i}: {val}")  # 0: a, 1: b, 2: c
```

**Q10: What is a lambda function?**
A: An anonymous, single-expression function defined with the `lambda` keyword.

```python
square = lambda x: x ** 2
print(square(5))  # 25
```

**Q11: What is the difference between `args` and `**kwargs`?**
A: `*args` collects positional arguments as a tuple, `**kwargs` collects keyword arguments as a dictionary.

```python
def func(*args, **kwargs):
    print(args)   # tuple
    print(kwargs)  # dict

func(1, 2, 3, name="test", age=25)
# (1, 2, 3)
# {'name': 'test', 'age': 25}
```

**Q12: What is method resolution order (MRO)?**
A: The order in which Python looks for a method in a class hierarchy. In multiple inheritance, it determines which parent's method is called first.

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass
print(D.__mro__)  # Shows the hierarchy
```

**Q13: What is a context manager and why use it?**
A: A context manager ensures resources are properly acquired and released. The `with` statement uses context managers.

```python
with open('file.txt', 'r') as f:
    content = f.read()
# File is automatically closed here
```

**Q14: What is the difference between `strip()` and `split()`?**
A: `strip()` removes whitespace from both ends of a string. `split()` divides a string into a list based on a delimiter.

```python
"  hello  ".strip()  # "hello"
"a,b,c".split(",")   # ["a", "b", "c"]
```

**Q15: How do you create a singleton in Python?**
A: Using a class with `__new__` method or a decorator, or using a module (module approach is simplest and most Pythonic).

```python
class Singleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Q16: What is the purpose of `self`?**
A: `self` refers to the instance of a class. It's the first parameter of instance methods and allows access to instance attributes and other methods.

**Q17: What are `*args` and `**kwargs` used for?**
A: They allow functions to accept variable numbers of arguments. `*args` for variable positional arguments, `**kwargs` for variable keyword arguments.

**Q18: What is the difference between `copy()` and `deepcopy()`?**
A: `copy()` creates a shallow copy (copies references to nested objects), while `deepcopy()` creates a true copy of all nested objects.

**Q19: What is a generator in Python?**
A: A generator is a function that yields values lazily using the `yield` keyword. It produces values one at a time and only computes them when needed.

```python
def count_up_to(n):
    i = 1
    while i <= n:
        yield i
        i += 1

for num in count_up_to(3):
    print(num)  # 1, 2, 3
```

**Q20: What is the purpose of `__str__` and `__repr__`?**
A: `__str__` provides a human-readable string representation, used by `str()` and `print()`. `__repr__` provides an unambiguous representation, used by `repr()` and debugging.

**Q21: What is a frozenset?**
A: An immutable version of a set. Once created, elements cannot be added or removed. It can be used as dictionary keys or elements of other sets.

**Q22: How do you reverse a list in Python?**
A: Multiple ways:
```python
a = [1, 2, 3]
print(a[::-1])  # [3, 2, 1] (slicing)
print(list(reversed(a)))  # [3, 2, 1]
a.reverse()  # In-place
```

**Q23: What is duck typing?**
A: A programming style where type is determined by presence of methods/attributes rather than the actual type. "If it walks like a duck and quacks like a duck, it's a duck."

**Q24: What is the difference between `isinstance()` and `type()`?**
A: `isinstance()` checks if an object is an instance of a class or tuple of classes (including inheritance). `type()` returns the exact type.

```python
isinstance(5, int)  # True
type(5) == int       # True
class Dog(int): pass
isinstance(Dog(5), int)  # True (due to inheritance)
type(Dog(5)) == int      # False
```

**Q25: What is a closures in Python?**
A: A closure is a nested function that remembers the values from the enclosing scope even after the outer function has finished executing.

```python
def outer(x):
    def inner(y):
        return x + y
    return inner

add_5 = outer(5)
print(add_5(10))  # 15
```

**Q26: What is the difference between `map()` and `filter()`?**
A: `map()` applies a function to all items and returns the results. `filter()` selects items based on a condition.

```python
nums = [1, 2, 3, 4, 5]
list(map(lambda x: x*2, nums))   # [2, 4, 6, 8, 10]
list(filter(lambda x: x%2==0, nums))  # [2, 4]
```

**Q27: What are dataclasses and why use them?**
A: Decorated classes that automatically generate `__init__`, `__repr__`, and `__eq__` methods. They reduce boilerplate for data-holding classes.

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
```

**Q28: What is the purpose of `pass`?**
A: `pass` is a null operation used as a placeholder when a statement is syntactically required but no action is needed.

**Q29: How do you handle missing dictionary keys?**
A: Use `.get()` method with default value, or `collections.defaultdict`.

```python
d = {'a': 1}
d.get('b', 0)  # 0
from collections import defaultdict
d = defaultdict(int)  # Returns 0 for missing keys
```

**Q30: What is the difference between `private`, `protected`, and `public` attributes?**
A: Python doesn't enforce access modifiers. Convention: `_protected` (internal use), `__private` (name mangling to `_ClassName__attr`), `public` (no underscore).

---

### Intermediate Questions (30)

**Q1: Explain the Python data model and magic methods.**
A: Magic methods (dunder methods) are special methods with double underscores that allow objects to interact with Python's built-in operations. Examples: `__init__`, `__str__`, `__repr__`, `__len__`, `__getitem__`, `__iter__`, `__call__`, `__enter__`, `__exit__`, `__add__`, `__eq__`.

**Q2: What is the difference between coroutines and generators?**
A: Generators produce values lazily with `yield`. Coroutines can also receive values using `.send()` and are used for async programming with `async/await`.

**Q3: How does the `with` statement work internally?**
A: The `with` statement uses the context manager protocol via `__enter__` and `__exit__` methods. The `contextlib` module provides helpers like `@contextmanager` decorator.

**Q4: Explain Python's memory management.**
A: Python uses private heap space for memory allocation. The GC (garbage collector) handles reference counting and cyclic garbage collection. Memory is allocated in blocks with pools containing pages.

**Q5: What are descriptors in Python?**
A: Objects that define how attribute access works. Implementing `__get__`, `__set__`, and `__delete__` creates a descriptor. Property, method, and classmethod are built-in descriptors.

**Q6: How do metaclasses work?**
A: Metaclasses are classes whose instances are classes. They control class creation and can add logic during class definition. The default metaclass is `type`.

```python
class MyMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs['created_by'] = 'MyMeta'
        return super().__new__(cls, name, bases, attrs)

class MyClass(metaclass=MyMeta):
    pass

print(MyClass.created_by)  # MyMeta
```

**Q7: What is the difference between `__getattr__` and `__getattribute__`?**
A: `__getattribute__` is called for EVERY attribute access. `__getattr__` is called only when the attribute is not found through normal means.

**Q8: Explain the Liskov Substitution Principle in Python context.**
A: Objects of a superclass should be replaceable with objects of a subclass without breaking the application. In Python, this means subclasses should maintain the contract of parent classes.

**Q9: What are abstract base classes (ABCs)?**
A: Classes from the `abc` module that cannot be instantiated directly. They define abstract methods that must be implemented by concrete subclasses.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass
```

**Q10: How do you implement a thread-safe singleton?**
A: Using threading.Lock or the Borg pattern.

```python
import threading

class ThreadSafeSingleton:
    _lock = threading.Lock()
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

**Q11: What is the difference between asyncio, threading, and multiprocessing?**
A: asyncio uses cooperative multitasking with a single thread. threading uses preemptive multitasking with shared memory. multiprocessing uses separate processes with separate memory.

**Q12: Explain the observer pattern in Python.**
A: A design pattern where an object (subject) maintains a list of dependents (observers) and notifies them of state changes. Can be implemented with callbacks, `weakref`, or the `observer` library.

**Q13: What are weak references and when would you use them?**
A: References that don't prevent garbage collection of the referenced object. Useful for caches and observer lists to avoid memory leaks.

```python
import weakref

class Cache:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()
```

**Q14: How does the `functools.lru_cache` work?**
A: It wraps a function with a memoizing callable that saves up to `maxsize` recent calls. Uses a dictionary internally keyed by arguments.

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)
```

**Q15: What is method dispatch and multiple dispatch?**
A: Method dispatch selects which implementation of a method to call based on argument types. Python only supports single dispatch (first argument). `functools.singledispatch` implements single dispatch.

**Q16: Explain Python's iteration protocol.**
A: Objects implement `__iter__()` returning an iterator, which has `__next__()`. For loops call `iter()` to get iterator, then `next()` repeatedly until StopIteration.

**Q17: What are slots and how do they improve memory?**
A: `__slots__` restricts class attributes to those specified, preventing `__dict__` creation and saving memory.

```python
class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

**Q18: How do you implement a thread-safe queue?**
A: Use `queue.Queue` which is thread-safe, or `collections.deque` with locks for specific use cases.

**Q19: What is the difference between `wait()` and `notify()`?**
A: `wait()` suspends execution until another thread calls `notify()` or `notify_all()`. These are methods of `threading.Condition`.

**Q20: Explain the producer-consumer pattern in Python.**
A: Uses a `queue.Queue` to decouple producers (create work) from consumers (process work). Thread-safe communication between threads.

**Q21: What are coroutine scheduling strategies?**
A: Event loop schedules coroutines based on I/O readiness (epoll, kqueue, select). Can use `asyncio.gather()`, `asyncio.create_task()`, or `asyncio.wait()`.

**Q22: How do you prevent circular imports in Python?**
A: Restructure imports (import inside function), use `TYPE_CHECKING`, or use lazy imports.

```python
from __future__ import annotations  # Postpones evaluation
```

**Q23: What is the difference between `concurrency` and `parallelism`?**
A: Concurrency handles multiple tasks by switching between them (useful for I/O). Parallelism executes multiple tasks simultaneously (useful for CPU-bound work).

**Q24: Explain the adapter pattern in Python.**
A: Converts interface of a class into another interface expected by client. Python's built-in `io` module uses this pattern extensively.

**Q25: What is the difference between `classmethod` and `staticmethod`?**
A: `classmethod` receives the class as first argument, can be called on class or instance. `staticmethod` doesn't receive implicit first argument.

**Q26: How do you implement rate limiting in Python?**
A: Using token bucket algorithm, Redis with sliding window, or `asyncio` with locks and sleep calculations.

**Q27: What are namedtuples and when use them?**
A: Lightweight object types with named fields for better readability. More memory-efficient than regular tuples.

```python
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])
p = Point(1, 2)
print(p.x, p.y)
```

**Q28: Explain the command pattern in Python.**
A: Encapsulates a request as an object, allowing parameterization, queuing, and logging of commands.

**Q29: What is the difference between `deepcopy` and `copy` for nested objects?**
A: Shallow copy shares references to nested objects. Deep copy creates new objects recursively for all nested structures.

**Q30: How does `__del__` work and its pitfalls?**
A: Destructor called when object is garbage collected. Not deterministic (depends on GC). Don't use for critical cleanup; use context managers instead.

---

### Advanced Questions (30)

**Q1: How would you implement a custom memory allocator in Python?**
A: Python's memory allocator (pymalloc) uses a三层 architecture: arena (256KB), pool (4KB pages), and block (8-512 bytes). Custom allocators can override `__malloc__`, `__free__` or use `ctypes` for direct memory management.

**Q2: Explain Python's GIL and its impact on multi-threaded performance.**
A: GIL prevents simultaneous execution of Python bytecode by multiple threads. CPU-bound code doesn't benefit from threading. I/O-bound code can still benefit through cooperative waiting.

**Q3: How do you implement a lock-free data structure in Python?**
A: Using atomic operations from `threading` module, `queue.Queue` (lock-free for certain operations), or `multiprocessing` with shared memory.

**Q4: What is the difference between `cpython`, `pypy`, and other implementations?**
A: CPython is the reference implementation in C. PyPy uses JIT compilation for speed. Others include Jython (JVM), IronPython (.NET), and MicroPython (embedded).

**Q5: How does the asyncio event loop work internally?**
A: Single-threaded loop using `select()`/`epoll()` for I/O multiplexing. Maintains task queue, runs callbacks when I/O ready, handles timers.

**Q6: Explain how you would profile and optimize a Python application.**
A: Use `cProfile` for CPU profiling, `memory_profiler` for memory, `line_profiler` for line-by-line. Tools: `py-spy`, `scalene`, `aio-libs` for async.

**Q7: What is a greenlet and how does it differ from asyncio?**
A: Greenlet provides micro-threads with explicit switching. Unlike asyncio, doesn't need async/await syntax. `gevent` uses greenlets with monkey-patching.

**Q8: How do you implement hot reloading in Python?**
A: Using `importlib.reload()`, watch files with `watchdog`, or frameworks like FastAPI's hot reload. Django's runserver handles this with stat watchers.

**Q9: Explain the implementation of `asyncpg` for async database access.**
A: Uses libpq's async interface, connection pooling with greenlets, prepared statement caching, and zero-copy binary protocol for PostgreSQL.

**Q10: What are the implications of Python's reference counting?**
A: Immediate memory reclamation (no GC pauses) but vulnerable to circular references. Must disable during C extension operations.

**Q11: How do you implement a custom protocol in Python?**
A: Implement magic methods (`__getitem__`, `__iter__`, etc.) to make objects behave like built-in types. Use `collections.abc` for protocol verification.

**Q12: Explain Python's Unicode handling and string encoding.**
A: Python 3 str is Unicode. Encoding converts to bytes (UTF-8 default). `ord()`, `chr()` for code points. `encode()`, `decode()` for byte conversions.

**Q13: What is the difference between `__new__` and `__init__`?**
A: `__new__` creates and returns instance, `__init__` initializes it. `__new__` is called first and is responsible for returning the object.

```python
class Singleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Q14: How does the decorator pattern work with functools.wraps?**
A: `wraps` copies metadata from wrapped function to wrapper, preserving name, docstring, and attributes.

**Q15: Explain Python's exception chaining and how `raise from` works.**
A: `raise X from Y` chains exceptions: Y is the cause, X is the effect. Useful for custom exception transformations.

**Q16: What is the difference between `classmethod`, `staticmethod`, and instance methods?**
A: Instance methods receive `self`. Class methods receive `cls`. Static methods don't receive implicit first argument.

**Q17: How do you implement a thread pool with `concurrent.futures`?**
A: Use `ThreadPoolExecutor` for I/O-bound work, `ProcessPoolExecutor` for CPU-bound work.

```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as executor:
    results = executor.map(compute_function, data)
```

**Q18: Explain the implementation of `dataclasses` and its limitations.**
A: Uses `__annotations__` and metaclass to generate methods. Limitations: no validation, can't easily inherit.

**Q19: What are protocol classes and structural subtyping?**
A: From `typing` module, protocols define interfaces for structural typing. Classes implementing the methods satisfy the protocol without explicit inheritance.

**Q20: How do you handle database connection pooling at scale?**
A: Use `sqlalchemy` async pools, `asyncpg` pools, `aiosql` for async, connection lifetimed with context managers, pool size tuning based on load.

**Q21: What is the difference between `__slots__` and `__dict__`?**
A: `__slots__` prevents `__dict__` creation, saving ~40% memory per instance. Disables dynamic attribute addition.

**Q22: Explain the implementation of Python's property decorator.**
A: Uses descriptor protocol. `property()` returns a descriptor that calls `__get__` and `__set__` on the decorated function.

**Q23: How do you implement zero-copy serialization in Python?**
A: Use `struct` module, `array` module, or memoryviews with `bytearray`. Avoid creating intermediate objects.

**Q24: What is the difference between `atexit` and `try/finally` for cleanup?**
A: `atexit` registers callbacks for interpreter shutdown. `try/finally` only works within the current scope.

**Q25: Explain how you would implement a custom garbage collection strategy.**
A: Use `gc` module to configure thresholds, manually trigger collection, implement weakref callbacks for resource cleanup.

**Q26: What are the security implications of `pickle`?**
A: Never unpickle untrusted data - can execute arbitrary code. Use `json`, `msgpack`, or `protobuf` for untrusted data.

**Q27: How do you implement a thread-safe singleton with double-checked locking?**
A: First check without lock, second check with lock. Ensures thread safety while minimizing lock contention.

**Q28: Explain Python's memory allocator arenas and pools.**
A: 256KB arenas contain 4KB pools, pools contain blocks of 8-512 bytes. Small allocations go to appropriate block size pool.

**Q29: What is the difference between `sys.setrecursionlimit` and tail recursion?**
A: Python doesn't optimize tail recursion. `sys.setrecursionlimit` controls C stack size but can't overcome lack of TCO.

**Q30: How do you implement custom import hooks?**
A: Create a meta_path finder with `find_module()` and `load_module()`. Use `importlib.abc.Loader` for cleaner implementation.

---

### Scenario-Based Questions (20)

**Q1: You're processing a 100GB file. How do you do it efficiently in Python?**
A: Use streaming/chunked processing with generators. Never load entire file. Use `pandas` with `chunksize`, `itertools.islice`, or memory-mapped files.

```python
def process_large_file(filepath, chunk_size=10000):
    for chunk in pd.read_csv(filepath, chunksize=chunk_size):
        yield transform(chunk)
```

**Q2: Your application crashes with a MemoryError. How do you debug it?**
A: Use `memory_profiler`, check for memory leaks (accumulated objects), use `tracemalloc`, check large data structure creation, use weakrefs for caches.

**Q3: How would you design a rate limiter for an API?**
A: Token bucket algorithm with Redis backend. Store tokens per user, check and decrement atomically, refill based on time elapsed.

**Q4: Your async application is slow. How do you profile it?**
A: Use `aio-libs` tools, `py-spy` with async support, `asyncio` built-in debugging, check for blocking calls in async code.

**Q5: How do you handle database migrations in a running production system?**
A: Expand/contract pattern, backward-compatible migrations, feature flags, blue-green deployments, no-downtime migration tools like Alembic.

**Q6: Design a system to process 1 million events per second.**
A: Use message queue (Kafka) for buffering, batch processing, horizontal scaling, connection pooling, async I/O, and possibly C extensions.

**Q7: How would you implement exactly-once semantics in Python?**
A: Use idempotent operations, transaction logs, deduplication with unique IDs, or use Kafka's transactions.

**Q8: Your application has a race condition. How do you find and fix it?**
A: Add more logging, use `threading.RLock` instead of `Lock`, check shared state access patterns, use lock-free algorithms if possible.

**Q9: How do you handle backward compatibility when changing APIs?**
A: Version APIs, maintain old endpoints with deprecation warnings, use adapters, feature flags, and comprehensive testing.

**Q10: Design a caching strategy for a Python microservice.**
A: Multi-level cache (local + Redis), cache-aside pattern, TTL-based expiration, cache warming, invalidation strategies.

**Q11: How would you handle secrets in a Python application?**
A: Environment variables, secrets managers (AWS, Vault), never commit secrets, encrypt at rest, use short-lived credentials.

**Q12: Your application has high latency variability. How do you investigate?**
A: Add structured logging with timestamps, profile with `cProfile`, check for GC pauses, network timeouts, connection pool contention.

**Q13: How do you implement graceful shutdown in a Python service?**
A: Handle SIGTERM, stop accepting requests, complete in-flight requests, flush buffers, close connections, exit cleanly.

**Q14: Design an idempotent payment processing system.**
A: Use idempotency keys, store processed transaction IDs, return cached results for duplicate requests, use database transactions.

**Q15: How do you handle timezone-aware datetime in Python?**
A: Always use `datetime.timezone.utc` or `pytz`, store as UTC, convert to local only at display layer, use `zoneinfo` in Python 3.9+.

**Q16: Your application uses too much CPU. How do you optimize?**
A: Profile with `cProfile`, optimize hot paths, use `numba` for numerical code, move CPU-bound work to separate processes.

**Q17: How do you implement a circuit breaker in Python?**
A: Track failure counts, open circuit after threshold, half-open state to test recovery, timeout-based state transitions.

**Q18: Design a retry mechanism with exponential backoff.**
A: Start with small delay, multiply by backoff factor, add jitter, cap maximum delay, use decorator for easy application.

**Q19: How would you handle 10,000 concurrent WebSocket connections?**
A: Use async frameworks (FastAPI, Starlette), non-blocking I/O, connection pooling, horizontal scaling with load balancer.

**Q20: Your application's memory grows over time. How do you debug memory leaks?**
A: Use `tracemalloc`, `objgraph`, check for unclosed resources, accumulated caches, global state, or event listener buildup.

---

### Architecture Questions (20)

**Q1: Design a real-time analytics pipeline architecture in Python.**
A: Kafka for ingestion, Flink or Faust for stream processing, Redis for real-time cache, PostgreSQL for OLAP, GraphQL for serving.

**Q2: How would you design a multi-tenant SaaS application in Python?**
A: Database per tenant or schema per tenant, tenant ID in all queries, tenant isolation at middleware level, tenant-specific caching.

**Q3: Design a CQRS pattern implementation in Python.**
A: Separate read and write models, event sourcing for writes, materialized views for reads, asynchronous synchronization.

**Q4: How do you implement event-driven microservices in Python?**
A: Use message broker (Kafka/RabbitMQ), define event schemas, implement event handlers, use saga pattern for distributed transactions.

**Q5: Design a job queue system in Python.**
A: Use Celery or RQ with Redis, define tasks, configure retry policies, monitor with flower, use dead letter queues.

**Q6: How would you implement API versioning in a Python REST service?**
A: URL path versioning (/api/v1/), header versioning, or content negotiation. Maintain backward compatibility within versions.

**Q7: Design a GraphQL subscription system in Python.**
A: Use WebSockets for real-time, implement subscription resolvers, use pub/sub for message distribution, handle connection lifecycle.

**Q8: How do you implement service mesh patterns in Python?**
A: Use sidecar proxies, implement circuit breakers, retries, timeouts at client level, use envoy or similar proxy.

**Q9: Design a feature flag system in Python.**
A: Store flags in database or Redis, evaluate at runtime, use percentage rollouts, A/B testing support, admin UI.

**Q10: How would you implement eventual consistency in a Python distributed system?**
A: Use async messaging, implement compensation actions, track version vectors, provide conflict resolution.

**Q11: Design a search functionality with Elasticsearch in Python.**
A: Index documents, use async clients, implement search-as-you-type, handle indexing delays, use aggregations for faceted search.

**Q12: How do you implement saga pattern for distributed transactions in Python?**
A: Define saga steps, implement compensating transactions, use orchestrator or choreography approach, handle failures.

**Q13: Design a real-time notification system in Python.**
A: WebSocket connections, Redis pub/sub for distribution, notification templates, preference management, delivery tracking.

**Q14: How would you implement database read replicas in Python?**
A: Route reads to replicas, writes to primary, handle replication lag, use connection pooler, implement retry for stale reads.

**Q15: Design a data warehouse ETL pipeline in Python.**
A: Extract from sources, transform with pandas/spark, load to warehouse, schedule with Airflow, monitor data quality.

**Q16: How do you implement a webhook delivery system in Python?**
A: Store webhook subscriptions, queue deliveries, implement retry with backoff, track delivery status, provide webhook logs.

**Q17: Design a multi-stage deployment pipeline in Python.**
A: Build artifacts, deploy to staging, run integration tests, deploy to production with blue-green or canary, rollback capability.

**Q18: How would you implement rate limiting across distributed Python services?**
A: Use Redis for centralized counter, sliding window algorithm, per-service token buckets synchronized via Redis.

**Q19: Design a file processing pipeline in Python.**
A: Accept uploads, validate files, process in workers, store results, notify completion via webhooks or polling.

**Q20: How do you implement health checks for a Python microservice?**
A: Implement /health/live and /health/ready endpoints, check dependencies, return 200/503 based on status, integrate with orchestrator.

---

### Debugging Questions (10)

**Q1: Why does `my_dict.get('key')` return None instead of raising KeyError?**
A: The `get()` method returns None (or a default) for missing keys, unlike `my_dict['key']` which raises KeyError.

**Q2: Why are your async functions not running concurrently?**
A: Missing `await` on async calls, using blocking `time.sleep()` instead of `asyncio.sleep()`, not using `asyncio.gather()`.

**Q3: Why does `list.append()` inside a loop not work as expected?**
A: Likely appending the same mutable object reference. Use `.copy()` or list comprehension.

**Q4: How do you debug a hanging Python program?**
A: Send SIGQUIT (`kill -3`) for stack traces, use `py-spy`, check for deadlocks with `faulthandler`, use deadlock detection tools.

**Q5: Why does `json.dumps()` fail on datetime objects?**
A: datetime is not JSON serializable by default. Use `default` parameter or serialize to ISO format first.

```python
json.dumps(data, default=str)
```

**Q6: Why are your database connections not being returned to the pool?**
A: Missing `session.close()` or not using context manager, exceptions not caught, connections not properly released.

**Q7: Why does `pytest` report tests passed but they seem to fail?**
A: Check for missing assertions, fixtures not properly scoped, test isolation issues, mock not properly applied.

**Q8: How do you find which line is causing an exception in async code?**
A: Use full traceback, check for masked exceptions, use `traceback.print_exc()`, enable asyncio debug mode.

**Q9: Why does `urllib.request.urlopen()` hang when the server is down?**
A: Default timeout is None (infinite). Set explicit timeout, use connection pooling, implement retry with timeout.

**Q10: Why is your memory usage much higher than expected?**
A: Memory fragmentation, string interning, accumulated caches, object pools, or holding references in closures/classes.

---

## 14. Hands-on Exercises

### Level 1: Basic

**Exercise 1.1: Build a Simple REST API**
```python
# Create a FastAPI application with endpoints for:
# - GET /products - List all products
# - GET /products/{sku} - Get product by SKU
# - POST /products - Create a new product
# - DELETE /products/{sku} - Delete a product

# Requirements:
# - Use Pydantic models for request/response
# - Use in-memory storage (dictionary)
# - Add proper HTTP status codes
# - Add OpenAPI documentation
```

**Exercise 1.2: Implement a Data Pipeline**
```python
# Build a pipeline that:
# - Reads from a CSV file
# - Transforms data (clean, normalize, validate)
# - Writes to another CSV file
# - Reports statistics (rows processed, errors, etc.)
```

**Exercise 1.3: Create a Context Manager**
```python
# Implement a context manager for:
# - Database connection handling
# - File operations with automatic cleanup
# - Timer/performance measurement
```

**Exercise 1.4: Build a Basic Calculator Class**
```python
# Create a Calculator class with:
# - Basic operations (add, subtract, multiply, divide)
# - History of operations
# - Support for method chaining
```

### Level 2: Intermediate

**Exercise 2.1: Build an Event-Driven Order Processor**
```python
# Requirements:
# - Accept orders via REST API
# - Publish events to Kafka
# - Process orders asynchronously
# - Update order status
# - Send notifications
```

**Exercise 2.2: Implement a Caching Layer**
```python
# Build a multi-level cache:
# - L1: In-memory LRU cache
# - L2: Redis cache
# - Cache invalidation
# - TTL management
# - Cache statistics
```

**Exercise 2.3: Create a Data Validation Library**
```python
# Build a validation library:
# - Define schemas for data validation
# - Support nested objects
# - Custom validators
# - Error messages
# - Transform data during validation
```

**Exercise 2.4: Implement a Rate Limiter**
```python
# Build a rate limiter:
# - Token bucket algorithm
# - Per-user rate limiting
# - Redis backend
# - Sliding window
# - Distributed rate limiting
```

### Level 3: Advanced

**Exercise 3.1: Build a Real-Time Analytics Dashboard**
```python
# Requirements:
# - WebSocket for real-time updates
# - Kafka consumer for events
# - Redis for real-time state
# - Frontend with charts
# - Support multiple concurrent users
```

**Exercise 3.2: Implement a Custom ORM**
```python
# Build a lightweight ORM:
# - Model definition with field types
# - CRUD operations
# - Query builder
# - Relationship handling
# - Migration support
```

**Exercise 3.3: Create a Distributed Task Queue**
```python
# Build a task queue:
# - Task definition and registration
# - Worker pool management
# - Task scheduling (delayed, periodic)
# - Retry logic with backoff
# - Result storage
# - Dead letter queue
```

**Exercise 3.4: Implement a GraphQL Server**
```python
# Build a GraphQL API:
# - Schema definition
# - Queries and mutations
# - Subscriptions for real-time
# - Authentication/authorization
# - Performance: dataloader for N+1
```

### Level 4: Production

**Exercise 4.1: Design a Multi-Region Data Platform**
```python
# Requirements:
# - Global data replication
# - Latency-based routing
# - Conflict resolution
# - Data sovereignty compliance
# - Disaster recovery
```

**Exercise 4.2: Build a Self-Healing System**
```python
# Implement self-healing:
# - Health checks at multiple levels
# - Automatic restart on failure
# - Circuit breakers
# - Graceful degradation
# - Alert integration
```

**Exercise 4.3: Create a Real-Time ML Inference Pipeline**
```python
# Build an ML pipeline:
# - Model serving
# - Feature computation
# - A/B testing framework
# - Shadow mode deployment
# - Performance monitoring
# - Model drift detection
```

**Exercise 4.4: Design a Zero-Downtime Deployment System**
```python
# Requirements:
# - Blue-green deployments
# - Canary releases
# - Database migrations
# - Rollback mechanisms
# - Traffic shifting
# - Feature flags integration
```

---

## 15. Real Enterprise Use Cases

### Amazon
Amazon uses Python extensively for:
- **Recommendation Engine**: Python-based ML models analyze customer behavior to personalize product recommendations. The system processes billions of events daily.
- **Inventory Management**: Python scripts optimize warehouse logistics and predict stock requirements across 300+ fulfillment centers.
- **Price Optimization**: Real-time pricing algorithms in Python adjust prices based on demand, competitor prices, and inventory levels.

### Walmart
Walmart's Python use cases include:
- **Supply Chain Optimization**: Python models predict demand across 10,000+ stores, optimizing inventory and reducing waste by $1B+ annually.
- **Fraud Detection**: ML systems in Python analyze 100M+ transactions daily to identify fraudulent patterns.
- **Spark Analytics**: PySpark pipelines process customer data for loyalty programs and personalized marketing.

### Netflix
Netflix relies on Python for:
- **Recommendation Algorithms**: Python-based collaborative filtering and neural networks serve 230M+ subscribers.
- **Personalization**: Real-time content recommendation based on viewing history, ratings, and browsing behavior.
- **Media Workflow**: Python automation orchestrates video encoding, thumbnail generation, and content delivery.

### Uber
Uber uses Python for:
- **Surge Pricing**: Dynamic pricing algorithms in Python balance supply and demand in real-time.
- **Fraud Analysis**: Machine learning models detect fraudulent rides and payments.
- **Eats Recommendation Engine**: Restaurant and dish recommendations powered by Python ML models.

### LinkedIn
LinkedIn's Python applications:
- **People You May Know**: Graph algorithms in Python suggest professional connections.
- **Job Recommendations**: ML models match candidates with suitable job postings.
- **Content Feed Ranking**: Python-based ranking algorithms personalize the LinkedIn feed.

### Airbnb
Airbnb uses Python for:
- **Search Ranking**: ML models in Python rank listings based on relevance, quality, and user preferences.
- **Dynamic Pricing**: Python algorithms help hosts set competitive prices based on demand, seasonality, and location.
- **Risk Assessment**: Fraud detection systems analyze booking patterns to identify risky transactions.

### Stripe
Stripe's Python infrastructure:
- **Payment Processing**: Python services handle millions of API requests for payment processing.
- **Revenue Recognition**: Accounting automation in Python tracks and reports revenue.
- **Fraud Detection**: ML models analyze transaction patterns to prevent fraudulent payments.

---

## 16. Design Decisions

### Python vs Java

| Aspect | Python | Java |
|--------|--------|------|
| **Development Speed** | Faster (5-10x) | Slower |
| **Runtime Speed** | Slower (interpreted) | Faster (compiled to bytecode) |
| **Type Safety** | Dynamic typing (optional static via mypy) | Static typing |
| **Memory Usage** | Higher (GIL, object overhead) | Lower |
| **Concurrency** | GIL limits CPU parallelism | Native threading, better parallelism |
| **Ecosystem** | Rich for data/ML | Enterprise middleware |
| **Use Case** | Data pipelines, ML, scripts | Enterprise systems, Android |

**Why Python for This Platform**: Python's rich ecosystem for data processing (pandas, polars), ML (scikit-learn, PyTorch), and stream processing (Faust, Apache Flink Python API) makes it ideal for the analytical workloads of a retail platform.

### Python vs Go

| Aspect | Python | Go |
|--------|--------|-----|
| **Concurrency** | asyncio, threading | Native goroutines |
| **Deployment** | Interpreter required | Single binary |
| **Performance** | Slower | 10-50x faster |
| **Learning Curve** | Gentle | Moderate |
| **Type System** | Dynamic (optional) | Static |

**Why Not Go for This Platform**: While Go excels at high-throughput microservices, the platform requires extensive data processing libraries and ML integration that are better supported in Python.

### Python vs Rust

| Aspect | Python | Rust |
|--------|--------|------|
| **Safety** | Runtime checks | Compile-time ownership |
| **Performance** | Slower | 10-100x faster |
| **Development Speed** | Faster | Slower |
| **ML Ecosystem** | Extensive | Limited |
| **Use Case** | Rapid development, data processing | Systems programming, performance |

**When to Use Rust**: For performance-critical components like custom data processing operators, Python is used for orchestration while Rust handles compute-intensive operations.

---

## 17. Business Value

### ROI Impact

**Development Productivity**
- Python's concise syntax reduces lines of code by 5-10x compared to Java
- Faster iteration cycles reduce time-to-market by 40-60%
- Rich libraries eliminate reinventing common functionality

**Operational Cost Reduction**
- Single language for data engineering and ML reduces team size
- AWS Lambda with Python@Edge costs $0.20 per million requests
- Containerized Python services have 30% lower memory footprint vs Java

### Performance Improvements

| Metric | Before Python | After Python Optimization |
|--------|---------------|---------------------------|
| Data Pipeline Throughput | 10K rows/sec | 150K rows/sec (polars) |
| Model Training Time | 24 hours | 4 hours (GPU + batching) |
| API Response Time (P95) | 500ms | 50ms (caching + async) |
| Development Velocity | 2 features/week | 8 features/week |

### Faster Decision Making

- Real-time analytics dashboards enable same-day decision making
- Automated reporting reduces manual effort by 80%
- Self-service analytics empowers non-technical users

### Customer Experience

- Personalized recommendations increase conversion by 15-25%
- Real-time inventory visibility reduces stockouts by 60%
- Faster checkout through optimized processing

### Operational Efficiency

- Automated data quality checks reduce bad data incidents by 90%
- Pipeline automation reduces manual intervention by 95%
- Standardized Python code base reduces onboarding time by 50%

---

## 18. Future Improvements

### Enterprise Scaling

**Horizontal Scaling**
```python
# Kubernetes HPA configuration for Python services
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: python-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: python-api
  minReplicas: 3
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Multi-Region Deployment**
- Deploy Python services across 3+ AWS regions
- Use Route 53 for latency-based routing
- Implement active-active for critical services

### Cloud-Native Deployment

**Kubernetes Operators**
```python
# Custom operator for Python ML model serving
# Use operator-sdk with Python-based reconciliation
```

**GitOps with ArgoCD**
- Infrastructure as code with Terraform
- Application deployments via GitOps
- Automated rollbacks on failure

### AI Automation

**MLOps Pipeline**
```python
# Automated ML lifecycle management
# - Model training triggers on data changes
# - Automated A/B testing
# - Model registry with versioning
# - Canary deployments for models
```

**AI-Assisted Development**
- GitHub Copilot for code generation
- Claude for documentation and code review
- Automated testing with AI-generated test cases

### Disaster Recovery

**Multi-Region Backup Strategy**
```python
# Automated cross-region replication
# - Daily snapshots to secondary region
# - Point-in-time recovery
# - RTO < 1 hour, RPO < 15 minutes
```

---

## 19. References

### Official Documentation
- [Python Official Documentation](https://docs.python.org/3/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [Python Module Index](https://docs.python.org/3/py-modindex.html)
- [Python Discord](https://discord.gg/python)

### Books
- "Fluent Python" by Luciano Ramalho
- "Python Cookbook" by David Beazley
- "Effective Python" by Brett Slatkin
- "Python Distilled" by David Beazley
- "High Performance Python" by Micha Gorelick

### Architecture Papers
- [Python's GIL: Past, Present, and Future](https://arxiv.org/abs/1909.10092)
- [Asyncio: In-Depth Analysis](https://docs.python.org/3/library/asyncio.html)
- [Python Memory Management](https://docs.python.org/3/c-api/memory.html)

### GitHub Repositories
- [Awesome Python](https://github.com/vinta/awesome-python)
- [Python Patterns](https://github.com/faif/python-patterns)
- [Public APIs](https://github.com/public-apis/public-apis)

### Conference Talks
- PyCon US (annual)
- Python Web Conference
- EuroPython
- PyData Global
- DjangoCon

---

## 20. Skills Demonstrated

| Attribute | Value |
|-----------|-------|
| **Skill Name** | Python Programming |
| **Difficulty** | 2/5 |
| **Industry Demand** | 5/5 |
| **Typical Job Roles** | Backend Engineer, Data Engineer, ML Engineer, Platform Engineer, DevOps Engineer |
| **Interview Frequency** | 5/5 |
| **Estimated Learning Time** | 3-6 months |
| **Portfolio Value** | High - demonstrates ability to build production systems |
| **Resume Keywords** | Python, FastAPI, Django, Flask, SQLAlchemy, Pandas, Pytest, AsyncIO, REST APIs, GraphQL, Microservices |
| **Related Skills** | JavaScript, SQL, Docker, Kubernetes, AWS, Data Engineering, Machine Learning |
| **Certifications** | PCEP, PCAP, PCAT, Google Cloud Professional Data Engineer, AWS Certified Developer |
| **Common Mistakes** | Not understanding async/await, ignoring type hints, poor error handling, memory leaks in loops, not using context managers |
| **Key Takeaways** | Master async programming, understand memory management, learn data processing libraries, practice testing, understand deployment patterns |
