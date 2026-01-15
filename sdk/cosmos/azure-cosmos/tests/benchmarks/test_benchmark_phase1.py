# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Phase 1 Benchmark Tests

This module benchmarks the performance of operations comparing
Python-only vs Rust-backed implementations.

Usage:
    # Install pytest-benchmark
    pip install pytest-benchmark

    # Run with Python backend (baseline)
    $env:COSMOS_USE_RUST_BACKEND = "false"
    pytest tests/benchmarks/test_benchmark_phase1.py -v --benchmark-json=python_baseline.json

    # Run with Rust backend
    $env:COSMOS_USE_RUST_BACKEND = "true"
    pytest tests/benchmarks/test_benchmark_phase1.py -v --benchmark-json=rust_results.json

    # Compare results
    pytest-benchmark compare python_baseline.json rust_results.json
"""

import os
import uuid
import pytest
from typing import Generator

# Check if benchmark module is available
try:
    import pytest_benchmark
    BENCHMARK_AVAILABLE = True
except ImportError:
    BENCHMARK_AVAILABLE = False

import test_config
from azure.cosmos import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError


# Skip all tests if benchmark is not available
pytestmark = pytest.mark.skipif(
    not BENCHMARK_AVAILABLE,
    reason="pytest-benchmark is required. Install with: pip install pytest-benchmark"
)


@pytest.fixture(scope="module")
def backend_mode() -> str:
    """Get the current backend mode."""
    return os.environ.get("COSMOS_USE_RUST_BACKEND", "false")


@pytest.fixture(scope="module")
def cosmos_client() -> Generator[CosmosClient, None, None]:
    """Create a Cosmos DB client for benchmarking."""
    configs = test_config.TestConfig
    if configs.masterKey == '[YOUR_KEY_HERE]' or configs.host == '[YOUR_ENDPOINT_HERE]':
        pytest.skip("Cosmos DB credentials not configured")

    client = CosmosClient(configs.host, configs.masterKey)
    yield client


@pytest.fixture(scope="module")
def benchmark_database(cosmos_client: CosmosClient) -> Generator:
    """Create a benchmark database."""
    db_name = f"benchmark-db-{uuid.uuid4().hex[:8]}"
    db = cosmos_client.create_database(db_name)
    yield db

    # Cleanup
    try:
        cosmos_client.delete_database(db_name)
    except CosmosResourceNotFoundError:
        pass


@pytest.fixture(scope="module")
def benchmark_container(benchmark_database) -> Generator:
    """Create a benchmark container."""
    container_name = f"benchmark-container-{uuid.uuid4().hex[:8]}"
    container = benchmark_database.create_container(
        container_name,
        PartitionKey(path="/pk")
    )
    yield container

    # Cleanup
    try:
        benchmark_database.delete_container(container_name)
    except CosmosResourceNotFoundError:
        pass


@pytest.fixture
def sample_item() -> dict:
    """Create a sample item for benchmarking."""
    return {
        "id": f"item-{uuid.uuid4().hex[:8]}",
        "pk": "benchmark-pk",
        "name": "Benchmark Item",
        "value": 12345,
        "nested": {
            "level1": {
                "level2": {
                    "data": "nested value"
                }
            }
        },
        "array": [1, 2, 3, 4, 5],
        "description": "This is a sample item for benchmarking the Cosmos DB SDK"
    }


class TestDatabaseOperations:
    """Benchmark database operations."""

    @pytest.mark.benchmark(group="database", warmup=True)
    def test_create_delete_database(self, benchmark, cosmos_client, backend_mode):
        """Benchmark database creation and deletion."""
        def create_and_delete():
            db_name = f"bench-{uuid.uuid4().hex[:8]}"
            cosmos_client.create_database(db_name)
            cosmos_client.delete_database(db_name)

        benchmark.extra_info['backend'] = backend_mode
        benchmark(create_and_delete)

    @pytest.mark.benchmark(group="database", warmup=True)
    def test_get_database_client(self, benchmark, cosmos_client, benchmark_database, backend_mode):
        """Benchmark getting a database client reference."""
        db_id = benchmark_database.id

        def get_db():
            cosmos_client.get_database_client(db_id)

        benchmark.extra_info['backend'] = backend_mode
        benchmark(get_db)


class TestContainerOperations:
    """Benchmark container operations."""

    @pytest.mark.benchmark(group="container", warmup=True)
    def test_create_delete_container(self, benchmark, benchmark_database, backend_mode):
        """Benchmark container creation and deletion."""
        def create_and_delete():
            container_name = f"bench-{uuid.uuid4().hex[:8]}"
            benchmark_database.create_container(
                container_name,
                PartitionKey(path="/pk")
            )
            benchmark_database.delete_container(container_name)

        benchmark.extra_info['backend'] = backend_mode
        benchmark(create_and_delete)

    @pytest.mark.benchmark(group="container", warmup=True)
    def test_get_container_client(self, benchmark, benchmark_database, benchmark_container, backend_mode):
        """Benchmark getting a container client reference."""
        container_id = benchmark_container.id

        def get_container():
            benchmark_database.get_container_client(container_id)

        benchmark.extra_info['backend'] = backend_mode
        benchmark(get_container)


class TestItemOperations:
    """Benchmark item CRUD operations."""

    @pytest.mark.benchmark(group="item-create", warmup=True)
    def test_create_item(self, benchmark, benchmark_container, backend_mode):
        """Benchmark item creation."""
        def create_item():
            item = {
                "id": f"item-{uuid.uuid4().hex}",
                "pk": "benchmark-pk",
                "value": 12345
            }
            benchmark_container.create_item(item)

        benchmark.extra_info['backend'] = backend_mode
        benchmark(create_item)

    @pytest.mark.benchmark(group="item-read", warmup=True)
    def test_read_item(self, benchmark, benchmark_container, backend_mode):
        """Benchmark item reading."""
        # Create an item to read
        item_id = f"read-bench-{uuid.uuid4().hex[:8]}"
        item = {"id": item_id, "pk": "benchmark-pk", "value": 999}
        benchmark_container.create_item(item)

        def read_item():
            benchmark_container.read_item(item_id, partition_key="benchmark-pk")

        benchmark.extra_info['backend'] = backend_mode
        benchmark(read_item)

        # Cleanup
        benchmark_container.delete_item(item_id, partition_key="benchmark-pk")

    @pytest.mark.benchmark(group="item-upsert", warmup=True)
    def test_upsert_item(self, benchmark, benchmark_container, backend_mode):
        """Benchmark item upserting."""
        item_id = f"upsert-bench-{uuid.uuid4().hex[:8]}"
        counter = [0]

        def upsert_item():
            counter[0] += 1
            item = {
                "id": item_id,
                "pk": "benchmark-pk",
                "value": counter[0]
            }
            benchmark_container.upsert_item(item)

        benchmark.extra_info['backend'] = backend_mode
        benchmark(upsert_item)

        # Cleanup
        try:
            benchmark_container.delete_item(item_id, partition_key="benchmark-pk")
        except CosmosResourceNotFoundError:
            pass

    @pytest.mark.benchmark(group="item-replace", warmup=True)
    def test_replace_item(self, benchmark, benchmark_container, backend_mode):
        """Benchmark item replacement."""
        # Create an item to replace
        item_id = f"replace-bench-{uuid.uuid4().hex[:8]}"
        item = {"id": item_id, "pk": "benchmark-pk", "value": 0}
        benchmark_container.create_item(item)
        counter = [0]

        def replace_item():
            counter[0] += 1
            updated_item = {
                "id": item_id,
                "pk": "benchmark-pk",
                "value": counter[0]
            }
            benchmark_container.replace_item(item_id, updated_item)

        benchmark.extra_info['backend'] = backend_mode
        benchmark(replace_item)

        # Cleanup
        benchmark_container.delete_item(item_id, partition_key="benchmark-pk")

    @pytest.mark.benchmark(group="item-delete", warmup=True)
    def test_delete_item(self, benchmark, benchmark_container, backend_mode):
        """Benchmark item deletion."""
        items_to_delete = []

        # Pre-create items to delete
        for i in range(200):  # Create enough for warmup + benchmark
            item_id = f"delete-bench-{i}-{uuid.uuid4().hex[:8]}"
            item = {"id": item_id, "pk": "benchmark-pk", "value": i}
            benchmark_container.create_item(item)
            items_to_delete.append(item_id)

        idx = [0]

        def delete_item():
            if idx[0] < len(items_to_delete):
                benchmark_container.delete_item(
                    items_to_delete[idx[0]],
                    partition_key="benchmark-pk"
                )
                idx[0] += 1

        benchmark.extra_info['backend'] = backend_mode
        benchmark(delete_item)


class TestBatchOperations:
    """Benchmark batch operations."""

    @pytest.mark.benchmark(group="batch", warmup=True)
    def test_create_multiple_items(self, benchmark, benchmark_container, backend_mode):
        """Benchmark creating multiple items in sequence."""
        def create_batch():
            for i in range(10):
                item = {
                    "id": f"batch-{uuid.uuid4().hex}",
                    "pk": "benchmark-pk",
                    "value": i
                }
                benchmark_container.create_item(item)

        benchmark.extra_info['backend'] = backend_mode
        benchmark(create_batch)


class TestJsonSerializationOverhead:
    """Benchmark JSON serialization which is a key benefit of Rust."""

    @pytest.mark.benchmark(group="json", warmup=True)
    def test_large_item_create(self, benchmark, benchmark_container, backend_mode):
        """Benchmark creating a large item (tests serialization)."""
        def create_large_item():
            large_item = {
                "id": f"large-{uuid.uuid4().hex}",
                "pk": "benchmark-pk",
                "data": {f"field_{i}": f"value_{i}" for i in range(100)},
                "array": list(range(100)),
                "nested": {
                    "level1": {
                        "level2": {
                            "level3": {
                                "data": "deeply nested value"
                            }
                        }
                    }
                }
            }
            benchmark_container.create_item(large_item)

        benchmark.extra_info['backend'] = backend_mode
        benchmark(create_large_item)


def generate_comparison_report(python_results: str, rust_results: str, output_file: str = "comparison_report.md"):
    """
    Generate a comparison report from benchmark results.

    Usage:
        from test_benchmark_phase1 import generate_comparison_report
        generate_comparison_report("python_baseline.json", "rust_results.json")
    """
    import json

    with open(python_results) as f:
        python_data = json.load(f)

    with open(rust_results) as f:
        rust_data = json.load(f)

    # Create comparison table
    report = ["# Benchmark Comparison Report\n"]
    report.append("## Python vs Rust Backend Performance\n")
    report.append("| Operation | Python (ms) | Rust (ms) | Improvement |")
    report.append("|-----------|-------------|-----------|-------------|")

    python_benchmarks = {b["name"]: b["stats"] for b in python_data.get("benchmarks", [])}
    rust_benchmarks = {b["name"]: b["stats"] for b in rust_data.get("benchmarks", [])}

    for name, py_stats in python_benchmarks.items():
        if name in rust_benchmarks:
            rust_stats = rust_benchmarks[name]
            py_mean = py_stats["mean"] * 1000  # Convert to ms
            rust_mean = rust_stats["mean"] * 1000
            improvement = ((py_mean - rust_mean) / py_mean) * 100

            report.append(f"| {name} | {py_mean:.3f} | {rust_mean:.3f} | {improvement:.1f}% faster |")

    with open(output_file, "w") as f:
        f.write("\n".join(report))

    print(f"Report generated: {output_file}")


if __name__ == "__main__":
    # Run benchmarks when executed directly
    pytest.main([__file__, "-v", "--benchmark-only"])

