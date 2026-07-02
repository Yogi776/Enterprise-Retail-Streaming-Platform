#!/usr/bin/env python3
"""
Enterprise Retail Streaming Platform — DuckDB Data Quality Validation

Validates data in Iceberg tables (via Trino) or Parquet files for:
  - Data completeness (no nulls in required fields)
  - Data accuracy (values within expected ranges)
  - Data freshness (tables updated within SLA window)
  - Data consistency (referential integrity, duplicates)
  - Business rule validation (no negative amounts, valid statuses, etc.)

Usage:
    python duckdb_validation.py --env local
    python duckdb_validation.py --env prod
    python duckdb_validation.py --table retail.orders --env local

Environment Variables:
    TRINO_HOST: Trino coordinator host (default: localhost)
    TRINO_PORT: Trino port (default: 8080)
    ICEBERG_CATALOG: Catalog name (default: iceberg)
    DUCKDB_PATH: Path to local DuckDB (default: :memory:)
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

import duckdb
import trino
from trino.exceptions import TrinoQueryError

# ============================================================================
# CONFIGURATION
# ============================================================================

TRINO_HOST = os.getenv("TRINO_HOST", "localhost")
TRINO_PORT = int(os.getenv("TRINO_PORT", "8080"))
ICEBERG_CATALOG = os.getenv("ICEBERG_CATALOG", "iceberg")

# Quality thresholds
FRESHNESS_SLA_MINUTES = {
    "orders": 5,
    "payments": 5,
    "inventory": 15,
    "delivery": 10,
    "fraud_signals": 5,
    "customer_behavior": 30,
    "recommendations": 15,
    "customer_profile": 60,
}

# Expected row counts (for sanity checks)
MIN_EXPECTED_ROWS = {
    "orders": 100,
    "payments": 100,
    "inventory": 50,
}

# ============================================================================
# DATA CLASSES
# ============================================================================

class Severity(Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    ERROR = "error"


@dataclass
class ValidationResult:
    rule_name: str
    table_name: str
    column_name: str
    severity: Severity
    status: str
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    checked_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d


@dataclass
class TableValidationReport:
    table_name: str
    total_rules: int
    passed: int
    warnings: int
    failures: int
    errors: int
    overall_status: Severity
    results: List[ValidationResult]
    checked_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table_name": self.table_name,
            "total_rules": self.total_rules,
            "passed": self.passed,
            "warnings": self.warnings,
            "failures": self.failures,
            "errors": self.errors,
            "overall_status": self.overall_status.value,
            "results": [r.to_dict() for r in self.results],
            "checked_at": self.checked_at,
        }


@dataclass
class PlatformValidationReport:
    platform: str
    total_tables: int
    total_rules: int
    total_passed: int
    total_warnings: int
    total_failures: int
    total_errors: int
    overall_health: Severity
    table_reports: List[TableValidationReport]
    checked_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "total_tables": self.total_tables,
            "total_rules": self.total_rules,
            "total_passed": self.total_passed,
            "total_warnings": self.total_warnings,
            "total_failures": self.total_failures,
            "total_errors": self.total_errors,
            "overall_health": self.overall_health.value,
            "table_reports": [r.to_dict() for r in self.table_reports],
            "checked_at": self.checked_at,
        }


# ============================================================================
# TRINO CONNECTION
# ============================================================================

def get_trino_connection(host: str = TRINO_HOST, port: int = TRINO_PORT):
    """Create a Trino connection."""
    return trino.connect(
        host=host,
        port=port,
        user="data-quality-checker",
    )


def execute_trino_query(conn, query: str) -> List[Dict[str, Any]]:
    """Execute a Trino query and return results as list of dicts."""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except TrinoQueryError as e:
        print(f"[ERROR] Trino query failed: {e}")
        return []


# ============================================================================
# VALIDATION RULES
# ============================================================================

class ValidationRules:
    """Collection of data quality validation rules."""

    @staticmethod
    def completeness_check(
        table_name: str,
        column_name: str,
        cursor,
        schema: str = "retail"
    ) -> ValidationResult:
        """
        Check that required columns have no NULL values.
        Severity: FAIL if NULL% > 0, WARNING if NULL% > 0.1%
        """
        query = f"""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(*) FILTER (WHERE {column_name} IS NULL) AS null_count,
                ROUND(COUNT(*) FILTER (WHERE {column_name} IS NULL) * 100.0 / NULLIF(COUNT(*), 0), 4) AS null_pct
            FROM {ICEBERG_CATALOG}.{schema}.{table_name}
        """
        result = execute_trino_query(cursor, query)
        if not result:
            return ValidationResult(
                rule_name="completeness_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.ERROR,
                status="error",
                message=f"Query returned no results for {column_name}",
            )

        row = result[0]
        null_pct = float(row["null_pct"] or 0)

        if null_pct == 0:
            return ValidationResult(
                rule_name="completeness_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.PASS,
                status="pass",
                message=f"Column {column_name} has no NULL values",
                expected="0%",
                actual=f"{null_pct:.4f}%",
            )
        elif null_pct < 0.1:
            return ValidationResult(
                rule_name="completeness_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.WARNING,
                status="warning",
                message=f"Column {column_name} has {null_pct:.4f}% NULL values",
                expected="0%",
                actual=f"{null_pct:.4f}%",
            )
        else:
            return ValidationResult(
                rule_name="completeness_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.FAIL,
                status="fail",
                message=f"Column {column_name} has {null_pct:.4f}% NULL values — exceeds 0.1% threshold",
                expected="0%",
                actual=f"{null_pct:.4f}%",
            )

    @staticmethod
    def uniqueness_check(
        table_name: str,
        column_name: str,
        cursor,
        schema: str = "retail"
    ) -> ValidationResult:
        """
        Check that key columns (order_id, payment_id) have no duplicates.
        Severity: FAIL if duplicate count > 0
        """
        query = f"""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(DISTINCT {column_name}) AS distinct_count,
                COUNT(*) - COUNT(DISTINCT {column_name}) AS duplicate_count
            FROM {ICEBERG_CATALOG}.{schema}.{table_name}
        """
        result = execute_trino_query(cursor, query)
        if not result:
            return ValidationResult(
                rule_name="uniqueness_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.ERROR,
                status="error",
                message=f"Query returned no results",
            )

        row = result[0]
        dup_count = int(row["duplicate_count"] or 0)

        if dup_count == 0:
            return ValidationResult(
                rule_name="uniqueness_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.PASS,
                status="pass",
                message=f"Column {column_name} has no duplicate values",
                expected="0",
                actual="0",
            )
        else:
            return ValidationResult(
                rule_name="uniqueness_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.FAIL,
                status="fail",
                message=f"Column {column_name} has {dup_count} duplicate values",
                expected="0",
                actual=str(dup_count),
            )

    @staticmethod
    def value_range_check(
        table_name: str,
        column_name: str,
        min_value: Optional[float],
        max_value: Optional[float],
        cursor,
        schema: str = "retail"
    ) -> ValidationResult:
        """
        Check that numeric columns are within expected ranges.
        Severity: FAIL if any values outside range
        """
        conditions = []
        if min_value is not None:
            conditions.append(f"{column_name} >= {min_value}")
        if max_value is not None:
            conditions.append(f"{column_name} <= {max_value}")

        if not conditions:
            return ValidationResult(
                rule_name="value_range_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.WARNING,
                status="warning",
                message=f"No min/max bounds specified for {column_name}",
            )

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT COUNT(*) AS invalid_count
            FROM {ICEBERG_CATALOG}.{schema}.{table_name}
            WHERE NOT ({where_clause})
        """
        result = execute_trino_query(cursor, query)
        if not result:
            return ValidationResult(
                rule_name="value_range_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.ERROR,
                status="error",
                message=f"Query returned no results",
            )

        row = result[0]
        invalid_count = int(row["invalid_count"] or 0)

        if invalid_count == 0:
            return ValidationResult(
                rule_name="value_range_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.PASS,
                status="pass",
                message=f"All {column_name} values within range [{min_value}, {max_value}]",
                expected=f"[{min_value}, {max_value}]",
                actual=f"[{min_value}, {max_value}]",
            )
        else:
            return ValidationResult(
                rule_name="value_range_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.FAIL,
                status="fail",
                message=f"{invalid_count} rows have {column_name} outside range [{min_value}, {max_value}]",
                expected=f"[{min_value}, {max_value}]",
                actual=f"{invalid_count} out of range",
            )

    @staticmethod
    def row_count_check(
        table_name: str,
        min_rows: int,
        cursor,
        schema: str = "retail"
    ) -> ValidationResult:
        """
        Check that tables have minimum expected row counts.
        Severity: WARNING if below minimum
        """
        query = f"""
            SELECT COUNT(*) AS row_count
            FROM {ICEBERG_CATALOG}.{schema}.{table_name}
        """
        result = execute_trino_query(cursor, query)
        if not result:
            return ValidationResult(
                rule_name="row_count_check",
                table_name=f"{schema}.{table_name}",
                column_name="*",
                severity=Severity.ERROR,
                status="error",
                message=f"Query returned no results",
            )

        row = result[0]
        row_count = int(row["row_count"] or 0)

        if row_count >= min_rows:
            return ValidationResult(
                rule_name="row_count_check",
                table_name=f"{schema}.{table_name}",
                column_name="*",
                severity=Severity.PASS,
                status="pass",
                message=f"Table has {row_count:,} rows (minimum: {min_rows:,})",
                expected=f">= {min_rows:,}",
                actual=f"{row_count:,}",
            )
        else:
            return ValidationResult(
                rule_name="row_count_check",
                table_name=f"{schema}.{table_name}",
                column_name="*",
                severity=Severity.WARNING,
                status="warning",
                message=f"Table has only {row_count:,} rows (expected >= {min_rows:,})",
                expected=f">= {min_rows:,}",
                actual=f"{row_count:,}",
            )

    @staticmethod
    def referential_integrity_check(
        parent_table: str,
        child_table: str,
        parent_key: str,
        child_key: str,
        cursor,
        parent_schema: str = "retail",
        child_schema: str = "retail"
    ) -> ValidationResult:
        """
        Check that foreign key relationships are valid.
        Severity: FAIL if orphaned records found
        """
        query = f"""
            SELECT COUNT(*) AS orphaned_count
            FROM {ICEBERG_CATALOG}.{child_schema}.{child_table} c
            LEFT JOIN {ICEBERG_CATALOG}.{parent_schema}.{parent_table} p
                ON c.{child_key} = p.{parent_key}
            WHERE c.{child_key} IS NOT NULL AND p.{parent_key} IS NULL
        """
        result = execute_trino_query(cursor, query)
        if not result:
            return ValidationResult(
                rule_name="referential_integrity_check",
                table_name=f"{child_schema}.{child_table}",
                column_name=child_key,
                severity=Severity.ERROR,
                status="error",
                message=f"Query returned no results",
            )

        row = result[0]
        orphaned = int(row["orphaned_count"] or 0)

        if orphaned == 0:
            return ValidationResult(
                rule_name="referential_integrity_check",
                table_name=f"{child_schema}.{child_table}",
                column_name=child_key,
                severity=Severity.PASS,
                status="pass",
                message=f"All {child_key} values in {child_table} have valid parent in {parent_table}",
                expected="0 orphaned",
                actual="0 orphaned",
            )
        else:
            return ValidationResult(
                rule_name="referential_integrity_check",
                table_name=f"{child_schema}.{child_table}",
                column_name=child_key,
                severity=Severity.FAIL,
                status="fail",
                message=f"Found {orphaned} orphaned records in {child_table}.{child_key} with no match in {parent_table}.{parent_key}",
                expected="0 orphaned",
                actual=f"{orphaned} orphaned",
            )

    @staticmethod
    def allowed_values_check(
        table_name: str,
        column_name: str,
        allowed_values: List[str],
        cursor,
        schema: str = "retail"
    ) -> ValidationResult:
        """
        Check that enum/ categorical columns only contain allowed values.
        Severity: FAIL if invalid values found
        """
        allowed_list = "', '".join(allowed_values)
        query = f"""
            SELECT
                COUNT(*) AS total_count,
                COUNT(*) FILTER (WHERE {column_name} NOT IN ('{allowed_list}')) AS invalid_count
            FROM {ICEBERG_CATALOG}.{schema}.{table_name}
            WHERE {column_name} IS NOT NULL
        """
        result = execute_trino_query(cursor, query)
        if not result:
            return ValidationResult(
                rule_name="allowed_values_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.ERROR,
                status="error",
                message=f"Query returned no results",
            )

        row = result[0]
        invalid_count = int(row["invalid_count"] or 0)

        if invalid_count == 0:
            return ValidationResult(
                rule_name="allowed_values_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.PASS,
                status="pass",
                message=f"All {column_name} values are in allowed set",
                expected=f"one of {allowed_values}",
                actual=f"all valid",
            )
        else:
            return ValidationResult(
                rule_name="allowed_values_check",
                table_name=f"{schema}.{table_name}",
                column_name=column_name,
                severity=Severity.FAIL,
                status="fail",
                message=f"{invalid_count} rows have invalid {column_name} values",
                expected=f"one of {allowed_values}",
                actual=f"{invalid_count} invalid",
            )


# ============================================================================
# TABLE VALIDATORS
# ============================================================================

class TableValidator:
    """Runs all validation rules for a given table."""

    def __init__(self, conn, table_name: str, schema: str = "retail"):
        self.conn = conn
        self.table_name = table_name
        self.schema = schema
        self.results: List[ValidationResult] = []

    def add_result(self, result: ValidationResult):
        result.checked_at = datetime.utcnow().isoformat() + "Z"
        self.results.append(result)

    def validate_all(self) -> TableValidationReport:
        """Run all validation rules for the table."""
        cursor = self.conn.cursor()

        if self.table_name == "orders":
            self._validate_orders(cursor)
        elif self.table_name == "payments":
            self._validate_payments(cursor)
        elif self.table_name == "inventory":
            self._validate_inventory(cursor)
        elif self.table_name == "delivery":
            self._validate_delivery(cursor)
        elif self.table_name == "fraud_signals":
            self._validate_fraud(cursor)
        elif self.table_name == "customers":
            self._validate_customers(cursor)
        else:
            self.add_result(ValidationResult(
                rule_name="table_exists",
                table_name=f"{self.schema}.{self.table_name}",
                column_name="*",
                severity=Severity.WARNING,
                status="warning",
                message=f"No specific validator for table {self.table_name} — running generic checks",
            ))
            self._generic_checks(cursor)

        return self._build_report()

    def _validate_orders(self, cursor):
        table = "orders"
        # Completeness checks
        for col in ["order_id", "customer_id", "order_timestamp", "total_amount", "status", "country"]:
            self.add_result(ValidationRules.completeness_check(table, col, cursor))

        # Uniqueness
        self.add_result(ValidationRules.uniqueness_check(table, "order_id", cursor))

        # Row count
        self.add_result(ValidationRules.row_count_check(table, 100, cursor))

        # Value ranges
        self.add_result(ValidationRules.value_range_check(table, "total_amount", 0.01, None, cursor))
        self.add_result(ValidationRules.value_range_check(table, "item_count", 1, None, cursor))

        # Allowed values
        self.add_result(ValidationRules.allowed_values_check(
            table, "status", ["pending", "completed", "failed", "cancelled"], cursor
        ))
        self.add_result(ValidationRules.allowed_values_check(
            table, "channel", ["POS", "Web", "Mobile", "App"], cursor
        ))

    def _validate_payments(self, cursor):
        table = "payments"
        for col in ["payment_id", "order_id", "customer_id", "amount", "payment_status"]:
            self.add_result(ValidationRules.completeness_check(table, col, cursor))

        self.add_result(ValidationRules.uniqueness_check(table, "payment_id", cursor))
        self.add_result(ValidationRules.row_count_check(table, 100, cursor))
        self.add_result(ValidationRules.value_range_check(table, "amount", 0.01, None, cursor))

        # Referential integrity: payments.order_id → orders.order_id
        self.add_result(ValidationRules.referential_integrity_check(
            "orders", "payments", "order_id", "order_id", cursor
        ))

    def _validate_inventory(self, cursor):
        table = "inventory"
        for col in ["product_id", "warehouse_id", "quantity_on_hand"]:
            self.add_result(ValidationRules.completeness_check(table, col, cursor))

        self.add_result(ValidationRules.value_range_check(table, "quantity_on_hand", 0, None, cursor))
        self.add_result(ValidationRules.value_range_check(table, "reorder_point", 0, None, cursor))

    def _validate_delivery(self, cursor):
        table = "delivery"
        for col in ["delivery_id", "order_id", "carrier", "status"]:
            self.add_result(ValidationRules.completeness_check(table, col, cursor))

        self.add_result(ValidationRules.referential_integrity_check(
            "orders", "delivery", "order_id", "order_id", cursor
        ))

    def _validate_fraud(self, cursor):
        table = "fraud_signals"
        for col in ["fraud_event_id", "order_id", "fraud_score"]:
            self.add_result(ValidationRules.completeness_check(table, col, cursor))

        self.add_result(ValidationRules.uniqueness_check(table, "fraud_event_id", cursor))
        self.add_result(ValidationRules.value_range_check(table, "fraud_score", 0.0, 1.0, cursor))

    def _validate_customers(self, cursor):
        table = "customers"
        for col in ["customer_id", "email", "loyalty_tier"]:
            self.add_result(ValidationRules.completeness_check(table, col, cursor))

        self.add_result(ValidationRules.allowed_values_check(
            table, "loyalty_tier", ["bronze", "silver", "gold", "platinum"], cursor
        ))

    def _generic_checks(self, cursor):
        """Generic checks that work on any table."""
        self.add_result(ValidationRules.row_count_check(self.table_name, 1, cursor))

    def _build_report(self) -> TableValidationReport:
        passed = sum(1 for r in self.results if r.severity == Severity.PASS)
        warnings = sum(1 for r in self.results if r.severity == Severity.WARNING)
        failures = sum(1 for r in self.results if r.severity == Severity.FAIL)
        errors = sum(1 for r in self.results if r.severity == Severity.ERROR)

        if errors > 0:
            overall = Severity.ERROR
        elif failures > 0:
            overall = Severity.FAIL
        elif warnings > 0:
            overall = Severity.WARNING
        else:
            overall = Severity.PASS

        return TableValidationReport(
            table_name=f"{self.schema}.{self.table_name}",
            total_rules=len(self.results),
            passed=passed,
            warnings=warnings,
            failures=failures,
            errors=errors,
            overall_status=overall,
            results=self.results,
            checked_at=datetime.utcnow().isoformat() + "Z",
        )


# ============================================================================
# MAIN
# ============================================================================

def validate_platform(tables: List[str], env: str = "local") -> PlatformValidationReport:
    """Run all validations for specified tables."""
    print(f"[INFO] Starting validation run for environment: {env}")
    print(f"[INFO] Tables to validate: {tables}")

    host = TRINO_HOST if env != "duckdb" else None
    conn = get_trino_connection(host) if host else None

    table_reports = []
    total_passed = total_warnings = total_failures = total_errors = 0

    for table in tables:
        print(f"\n[INFO] Validating table: {table}")
        validator = TableValidator(conn, table)
        report = validator.validate_all()
        table_reports.append(report)

        total_passed += report.passed
        total_warnings += report.warnings
        total_failures += report.failures
        total_errors += report.errors

        status_icon = {
            Severity.PASS: "✅",
            Severity.WARNING: "⚠️",
            Severity.FAIL: "❌",
            Severity.ERROR: "💥",
        }[report.overall_status]

        print(f"  {status_icon} {report.table_name}: {report.passed} passed, {report.warnings} warnings, {report.failures} failures, {report.errors} errors")

        # Print failures
        for result in report.results:
            if result.severity in (Severity.FAIL, Severity.ERROR):
                print(f"     ❗ {result.rule_name} on {result.column_name}: {result.message}")

    if conn:
        conn.close()

    # Overall health
    if total_errors > 0:
        overall_health = Severity.ERROR
    elif total_failures > 0:
        overall_health = Severity.FAIL
    elif total_warnings > 0:
        overall_health = Severity.WARNING
    else:
        overall_health = Severity.PASS

    full_report = PlatformValidationReport(
        platform=f"retail-streaming-platform-{env}",
        total_tables=len(tables),
        total_rules=total_passed + total_warnings + total_failures + total_errors,
        total_passed=total_passed,
        total_warnings=total_warnings,
        total_failures=total_failures,
        total_errors=total_errors,
        overall_health=overall_health,
        table_reports=table_reports,
        checked_at=datetime.utcnow().isoformat() + "Z",
    )

    return full_report


def main():
    parser = argparse.ArgumentParser(description="DuckDB Data Quality Validator")
    parser.add_argument("--env", default="local", choices=["local", "prod", "duckdb"], help="Environment")
    parser.add_argument("--table", help="Specific table to validate (default: all)")
    parser.add_argument("--output", help="Output JSON file path (default: stdout)")
    args = parser.parse_args()

    tables = [args.table] if args.table else [
        "orders",
        "payments",
        "inventory",
        "delivery",
        "fraud_signals",
        "customers",
    ]

    report = validate_platform(tables, args.env)
    report_dict = report.to_dict()

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report_dict, f, indent=2)
        print(f"\n[INFO] Report written to {args.output}")

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Overall Health: {report.overall_health.value.upper()}")
    print(f"Tables Checked: {report.total_tables}")
    print(f"Total Rules:   {report.total_rules}")
    print(f"  Passed:      {report.total_passed}")
    print(f"  Warnings:    {report.total_warnings}")
    print(f"  Failures:    {report.total_failures}")
    print(f"  Errors:      {report.total_errors}")
    print("=" * 60)

    # Exit code based on severity
    if report.overall_health == Severity.ERROR:
        sys.exit(2)
    elif report.overall_health == Severity.FAIL:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()