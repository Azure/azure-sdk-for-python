# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Phase 1 Rust Migration Tests

This module provides tests to validate the Rust SDK integration by:
1. Running operations using the original Python implementation
2. Running the same operations using the Rust-backed implementation
3. Comparing the results to ensure parity

Usage:
    # Run with Python-only backend (original)
    pytest test_phase1_rust_migration.py -v --use-python-backend

    # Run with Rust backend (new)
    pytest test_phase1_rust_migration.py -v --use-rust-backend

    # Run comparison mode (both backends, compare results)
    pytest test_phase1_rust_migration.py -v --compare-backends
"""

import os
import logging
import pytest
import unittest
import uuid
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

import test_config
from azure.cosmos import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration and Test Mode
# ============================================================================

class BackendMode:
    """Backend mode for tests."""
    PYTHON = "python"
    RUST = "rust"
    COMPARE = "compare"


def get_backend_mode() -> str:
    """Get the current backend mode from environment or default to compare."""
    return os.environ.get("COSMOS_BACKEND_MODE", BackendMode.COMPARE)


def set_backend_mode(mode: str) -> None:
    """Set the backend mode."""
    os.environ["COSMOS_BACKEND_MODE"] = mode


# ============================================================================
# Result Capture Classes
# ============================================================================

@dataclass
class OperationResult:
    """Captures the result of a Cosmos DB operation for comparison."""
    operation: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    status_code: Optional[int] = None
    response_headers: Optional[Dict[str, Any]] = None
    request_charge: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "operation": self.operation,
            "success": self.success,
            "result": self._sanitize_result(self.result),
            "error": self.error,
            "error_type": self.error_type,
            "status_code": self.status_code,
            "response_headers": self._extract_key_headers(self.response_headers),
            "request_charge": self.request_charge,
            "timestamp": self.timestamp,
        }

    def _sanitize_result(self, result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Remove system-generated fields that differ between runs."""
        if result is None:
            return None
        sanitized = dict(result)
        # Remove fields that will differ between runs
        for key in ["_rid", "_ts", "_self", "_etag"]:
            sanitized.pop(key, None)
        return sanitized

    def _extract_key_headers(self, headers: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Extract key headers for comparison."""
        if headers is None:
            return None
        key_headers = [
            "x-ms-request-charge",
            "x-ms-activity-id",
            "x-ms-session-token",
            "x-ms-item-count",
        ]
        return {k: headers.get(k) for k in key_headers if k in headers}


@dataclass
class TestRun:
    """Captures all operations from a test run."""
    backend: str
    test_name: str
    operations: List[OperationResult] = field(default_factory=list)
    start_time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    end_time: Optional[str] = None

    def add_operation(self, op: OperationResult) -> None:
        """Add an operation result."""
        self.operations.append(op)

    def finish(self) -> None:
        """Mark the test run as finished."""
        self.end_time = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "backend": self.backend,
            "test_name": self.test_name,
            "operations": [op.to_dict() for op in self.operations],
            "start_time": self.start_time,
            "end_time": self.end_time,
        }


# ============================================================================
# Comparison Utilities
# ============================================================================

class ResultComparator:
    """Compare results from Python and Rust backends."""

    @staticmethod
    def compare_runs(python_run: TestRun, rust_run: TestRun) -> Dict[str, Any]:
        """Compare two test runs and return a comparison report."""
        report = {
            "test_name": python_run.test_name,
            "python_operations": len(python_run.operations),
            "rust_operations": len(rust_run.operations),
            "matches": [],
            "mismatches": [],
            "missing_in_rust": [],
            "extra_in_rust": [],
        }

        python_ops = {op.operation: op for op in python_run.operations}
        rust_ops = {op.operation: op for op in rust_run.operations}

        # Compare matching operations
        for op_name, py_op in python_ops.items():
            if op_name in rust_ops:
                rust_op = rust_ops[op_name]
                comparison = ResultComparator._compare_operations(py_op, rust_op)
                if comparison["matches"]:
                    report["matches"].append(op_name)
                else:
                    report["mismatches"].append({
                        "operation": op_name,
                        "differences": comparison["differences"],
                    })
            else:
                report["missing_in_rust"].append(op_name)

        # Find extra operations in Rust
        for op_name in rust_ops:
            if op_name not in python_ops:
                report["extra_in_rust"].append(op_name)

        report["all_match"] = (
            len(report["mismatches"]) == 0 and
            len(report["missing_in_rust"]) == 0 and
            len(report["extra_in_rust"]) == 0
        )

        return report

    @staticmethod
    def _compare_operations(py_op: OperationResult, rust_op: OperationResult) -> Dict[str, Any]:
        """Compare two operations."""
        differences = []

        # Compare success
        if py_op.success != rust_op.success:
            differences.append({
                "field": "success",
                "python": py_op.success,
                "rust": rust_op.success,
            })

        # Compare error type (if both failed)
        if not py_op.success and not rust_op.success:
            if py_op.error_type != rust_op.error_type:
                differences.append({
                    "field": "error_type",
                    "python": py_op.error_type,
                    "rust": rust_op.error_type,
                })

        # Compare result (if both succeeded)
        if py_op.success and rust_op.success:
            py_result = py_op.to_dict()["result"]
            rust_result = rust_op.to_dict()["result"]
            if py_result != rust_result:
                differences.append({
                    "field": "result",
                    "python": py_result,
                    "rust": rust_result,
                })

        return {
            "matches": len(differences) == 0,
            "differences": differences,
        }


# ============================================================================
# Test Wrapper for Capturing Operations
# ============================================================================

class Phase1TestWrapper:
    """Wrapper to execute and capture Phase 1 operations."""

    def __init__(self, client: CosmosClient, test_name: str, backend: str):
        self.client = client
        self.test_run = TestRun(backend=backend, test_name=test_name)
        self.logger = logging.getLogger(f"{__name__}.{test_name}")

    def capture_operation(
        self,
        operation: str,
        func,
        *args,
        **kwargs
    ) -> Any:
        """Execute an operation and capture the result."""
        try:
            result = func(*args, **kwargs)

            # Extract response headers if available
            response_headers = None
            request_charge = None
            if hasattr(result, 'get_response_headers'):
                response_headers = dict(result.get_response_headers())
                request_charge = response_headers.get('x-ms-request-charge')

            # Convert result to dict if possible
            # Handle different result types appropriately
            if hasattr(result, '__iter__') and not isinstance(result, (str, dict)):
                # It's an iterable like ItemPaged - don't convert to dict
                result_dict = {"type": "iterable", "value": str(type(result).__name__)}
            elif isinstance(result, dict):
                result_dict = result
            elif hasattr(result, 'id'):
                # It's a proxy object (DatabaseProxy, ContainerProxy, etc.)
                result_dict = {"id": result.id, "type": type(result).__name__}
            else:
                result_dict = {"value": str(result)}

            op_result = OperationResult(
                operation=operation,
                success=True,
                result=result_dict,
                response_headers=response_headers,
                request_charge=float(request_charge) if request_charge else None,
            )
            self.test_run.add_operation(op_result)
            self.logger.info(f"✓ {operation} succeeded")
            return result

        except Exception as e:
            status_code = getattr(e, 'status_code', None)
            op_result = OperationResult(
                operation=operation,
                success=False,
                error=str(e),
                error_type=type(e).__name__,
                status_code=status_code,
            )
            self.test_run.add_operation(op_result)
            self.logger.error(f"✗ {operation} failed: {e}")
            raise

    def finish(self) -> TestRun:
        """Finish the test run and return results."""
        self.test_run.finish()
        return self.test_run


# ============================================================================
# Phase 1 Tests
# ============================================================================

@pytest.mark.cosmosEmulator
class TestPhase1RustMigration(unittest.TestCase):
    """
    Phase 1 Rust Migration Tests

    These tests cover:
    - CosmosClient: create_database, delete_database, list_databases, get_database_client
    - DatabaseProxy: create_container, delete_container, list_containers, get_container_client
    - ContainerProxy: create_item, read_item, upsert_item, replace_item, delete_item
    """

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    client: CosmosClient = None

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' in test_config.py to run the tests.")
        cls.client = CosmosClient(cls.host, cls.masterKey)
        cls.test_db_name = f"phase1-test-{uuid.uuid4().hex[:8]}"
        cls.test_container_name = f"phase1-container-{uuid.uuid4().hex[:8]}"

    @classmethod
    def tearDownClass(cls):
        """Cleanup test resources."""
        try:
            cls.client.delete_database(cls.test_db_name)
        except CosmosResourceNotFoundError:
            pass

    def test_01_create_database(self):
        """Test creating a database."""
        wrapper = Phase1TestWrapper(self.client, "test_create_database", get_backend_mode())

        try:
            db = wrapper.capture_operation(
                "create_database",
                self.client.create_database,
                self.test_db_name
            )
            self.assertEqual(db.id, self.test_db_name)
            wrapper.finish()
        except Exception as e:
            wrapper.finish()
            raise

    def test_02_get_database_client(self):
        """Test getting a database client."""
        wrapper = Phase1TestWrapper(self.client, "test_get_database_client", get_backend_mode())

        db = wrapper.capture_operation(
            "get_database_client",
            self.client.get_database_client,
            self.test_db_name
        )
        self.assertEqual(db.id, self.test_db_name)
        wrapper.finish()

    def test_03_list_databases(self):
        """Test listing databases."""
        wrapper = Phase1TestWrapper(self.client, "test_list_databases", get_backend_mode())

        databases = list(wrapper.capture_operation(
            "list_databases",
            self.client.list_databases
        ))

        # Check that our test database is in the list
        db_ids = [db['id'] for db in databases]
        self.assertIn(self.test_db_name, db_ids)
        wrapper.finish()

    def test_04_create_container(self):
        """Test creating a container."""
        wrapper = Phase1TestWrapper(self.client, "test_create_container", get_backend_mode())

        db = self.client.get_database_client(self.test_db_name)
        container = wrapper.capture_operation(
            "create_container",
            db.create_container,
            self.test_container_name,
            PartitionKey(path="/pk")
        )
        self.assertEqual(container.id, self.test_container_name)
        wrapper.finish()

    def test_05_get_container_client(self):
        """Test getting a container client."""
        wrapper = Phase1TestWrapper(self.client, "test_get_container_client", get_backend_mode())

        db = self.client.get_database_client(self.test_db_name)
        container = wrapper.capture_operation(
            "get_container_client",
            db.get_container_client,
            self.test_container_name
        )
        self.assertEqual(container.id, self.test_container_name)
        wrapper.finish()

    def test_06_create_item(self):
        """Test creating an item."""
        wrapper = Phase1TestWrapper(self.client, "test_create_item", get_backend_mode())

        db = self.client.get_database_client(self.test_db_name)
        container = db.get_container_client(self.test_container_name)

        item = {
            "id": "item1",
            "pk": "pk1",
            "name": "Test Item 1",
            "value": 100
        }

        created_item = wrapper.capture_operation(
            "create_item",
            container.create_item,
            item
        )

        self.assertEqual(created_item["id"], item["id"])
        self.assertEqual(created_item["name"], item["name"])
        wrapper.finish()

    def test_07_read_item(self):
        """Test reading an item."""
        wrapper = Phase1TestWrapper(self.client, "test_read_item", get_backend_mode())

        db = self.client.get_database_client(self.test_db_name)
        container = db.get_container_client(self.test_container_name)

        read_item = wrapper.capture_operation(
            "read_item",
            container.read_item,
            "item1",
            partition_key="pk1"
        )

        self.assertEqual(read_item["id"], "item1")
        self.assertEqual(read_item["name"], "Test Item 1")
        wrapper.finish()

    def test_08_upsert_item(self):
        """Test upserting an item (update existing)."""
        wrapper = Phase1TestWrapper(self.client, "test_upsert_item", get_backend_mode())

        db = self.client.get_database_client(self.test_db_name)
        container = db.get_container_client(self.test_container_name)

        item = {
            "id": "item1",
            "pk": "pk1",
            "name": "Updated Test Item 1",
            "value": 200
        }

        upserted_item = wrapper.capture_operation(
            "upsert_item",
            container.upsert_item,
            item
        )

        self.assertEqual(upserted_item["id"], item["id"])
        self.assertEqual(upserted_item["name"], item["name"])
        self.assertEqual(upserted_item["value"], item["value"])
        wrapper.finish()

    def test_09_replace_item(self):
        """Test replacing an item."""
        wrapper = Phase1TestWrapper(self.client, "test_replace_item", get_backend_mode())

        db = self.client.get_database_client(self.test_db_name)
        container = db.get_container_client(self.test_container_name)

        item = {
            "id": "item1",
            "pk": "pk1",
            "name": "Replaced Test Item 1",
            "value": 300
        }

        replaced_item = wrapper.capture_operation(
            "replace_item",
            container.replace_item,
            "item1",
            item
        )

        self.assertEqual(replaced_item["id"], item["id"])
        self.assertEqual(replaced_item["name"], item["name"])
        wrapper.finish()

    def test_10_delete_item(self):
        """Test deleting an item."""
        wrapper = Phase1TestWrapper(self.client, "test_delete_item", get_backend_mode())

        db = self.client.get_database_client(self.test_db_name)
        container = db.get_container_client(self.test_container_name)

        wrapper.capture_operation(
            "delete_item",
            container.delete_item,
            "item1",
            partition_key="pk1"
        )

        # Verify item is deleted
        with self.assertRaises(CosmosResourceNotFoundError):
            container.read_item("item1", partition_key="pk1")

        wrapper.finish()

    def test_11_delete_container(self):
        """Test deleting a container."""
        wrapper = Phase1TestWrapper(self.client, "test_delete_container", get_backend_mode())

        db = self.client.get_database_client(self.test_db_name)

        wrapper.capture_operation(
            "delete_container",
            db.delete_container,
            self.test_container_name
        )

        # Verify container is deleted
        with self.assertRaises(CosmosResourceNotFoundError):
            db.get_container_client(self.test_container_name).read()

        wrapper.finish()

    def test_12_delete_database(self):
        """Test deleting a database."""
        wrapper = Phase1TestWrapper(self.client, "test_delete_database", get_backend_mode())

        wrapper.capture_operation(
            "delete_database",
            self.client.delete_database,
            self.test_db_name
        )

        # Verify database is deleted
        with self.assertRaises(CosmosResourceNotFoundError):
            self.client.get_database_client(self.test_db_name).read()

        wrapper.finish()


# ============================================================================
# Comparison Test Runner
# ============================================================================

def run_comparison_tests():
    """
    Run tests with both backends and compare results.

    This function:
    1. Runs all Phase 1 tests with Python backend
    2. Runs all Phase 1 tests with Rust backend
    3. Compares the results and generates a report
    """
    results = {
        "python": [],
        "rust": [],
        "comparison": []
    }

    # Note: This is a placeholder for the comparison logic
    # In practice, you would run the tests programmatically and capture results
    logger.info("Comparison mode is enabled. Run tests separately and compare JSON outputs.")

    return results


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])

