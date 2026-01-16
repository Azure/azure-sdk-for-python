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


class TestHighVolumeOperations:
    """High-volume benchmark tests inspired by prototype project."""

    @pytest.mark.benchmark(group="high-volume", warmup=True, min_rounds=3)
    def test_create_100_items(self, benchmark, benchmark_container, backend_mode):
        """Benchmark creating 100 items across 10 partitions."""
        def create_100_items():
            for i in range(100):
                item = {
                    "id": f"hv-create-{uuid.uuid4().hex}",
                    "pk": f"partition_{i % 10}",
                    "name": f"Product {i}",
                    "category": "electronics",
                    "price": 99.99 + i,
                    "description": f"Description for item {i}" * 3,
                    "tags": ["tag1", "tag2", "tag3"],
                }
                try:
                    benchmark_container.create_item(item)
                except Exception:
                    pass

        benchmark.extra_info['backend'] = backend_mode
        benchmark.extra_info['operation_count'] = 100
        benchmark(create_100_items)

    @pytest.mark.benchmark(group="high-volume", warmup=True, min_rounds=3)
    def test_read_100_items(self, benchmark, benchmark_container, backend_mode):
        """Benchmark reading 100 items by ID."""
        # Pre-create items to read
        item_ids = []
        for i in range(100):
            item_id = f"hv-read-{i}-{uuid.uuid4().hex[:8]}"
            item = {"id": item_id, "pk": f"partition_{i % 10}", "value": i}
            try:
                benchmark_container.create_item(item)
                item_ids.append((item_id, f"partition_{i % 10}"))
            except Exception:
                pass

        def read_100_items():
            for item_id, pk in item_ids:
                try:
                    benchmark_container.read_item(item_id, partition_key=pk)
                except Exception:
                    pass

        benchmark.extra_info['backend'] = backend_mode
        benchmark.extra_info['operation_count'] = len(item_ids)
        benchmark(read_100_items)

        # Cleanup
        for item_id, pk in item_ids:
            try:
                benchmark_container.delete_item(item_id, partition_key=pk)
            except Exception:
                pass

    @pytest.mark.benchmark(group="high-volume", warmup=True, min_rounds=3)
    def test_upsert_50_items(self, benchmark, benchmark_container, backend_mode):
        """Benchmark upserting 50 items (mix of create and update)."""
        def upsert_50_items():
            for i in range(50):
                item = {
                    "id": f"hv-upsert-{i % 25}",  # Reuse some IDs to test update path
                    "pk": f"partition_{i % 10}",
                    "name": f"Upserted Product {i}",
                    "value": i * 2,
                }
                try:
                    benchmark_container.upsert_item(item)
                except Exception:
                    pass

        benchmark.extra_info['backend'] = backend_mode
        benchmark.extra_info['operation_count'] = 50
        benchmark(upsert_50_items)


# NOTE: TestQueryOperations is commented out because query_items() was NOT migrated to Rust in Phase 1.
# These tests would not show meaningful Python vs Rust performance differences.
# Uncomment when query_items() is migrated in a future phase.

# class TestQueryOperations:
#     """Benchmark query operations - key test for Rust performance."""
#
#     @pytest.mark.benchmark(group="query", warmup=True, min_rounds=3)
#     def test_query_single_partition(self, benchmark, benchmark_container, backend_mode):
#         """Benchmark querying items in a single partition."""
#         # Pre-create items to query
#         for i in range(20):
#             item = {
#                 "id": f"query-sp-{i}-{uuid.uuid4().hex[:8]}",
#                 "pk": "query-partition-1",
#                 "value": i,
#                 "category": "test"
#             }
#             try:
#                 benchmark_container.create_item(item)
#             except Exception:
#                 pass
#
#         def query_partition():
#             query = "SELECT * FROM c WHERE c.category = 'test'"
#             results = benchmark_container.query_items(
#                 query=query,
#                 partition_key="query-partition-1"
#             )
#             # Consume results
#             _ = list(results)
#
#         benchmark.extra_info['backend'] = backend_mode
#         benchmark(query_partition)
#
#     @pytest.mark.benchmark(group="query", warmup=True, min_rounds=3)
#     def test_query_10_partitions(self, benchmark, benchmark_container, backend_mode):
#         """Benchmark querying items across 10 partitions."""
#         # Pre-create items across partitions
#         for i in range(50):
#             item = {
#                 "id": f"query-mp-{i}-{uuid.uuid4().hex[:8]}",
#                 "pk": f"query-partition-{i % 10}",
#                 "value": i,
#                 "searchable": True
#             }
#             try:
#                 benchmark_container.create_item(item)
#             except Exception:
#                 pass
#
#         def query_10_partitions():
#             for p in range(10):
#                 query = "SELECT * FROM c WHERE c.searchable = true"
#                 results = benchmark_container.query_items(
#                     query=query,
#                     partition_key=f"query-partition-{p}"
#                 )
#                 # Consume results
#                 _ = list(results)
#
#         benchmark.extra_info['backend'] = backend_mode
#         benchmark.extra_info['partition_count'] = 10
#         benchmark(query_10_partitions)


class TestMixedWorkload:
    """Benchmark mixed workload - simulates real application patterns."""

    @pytest.mark.benchmark(group="mixed", warmup=True, min_rounds=3)
    def test_mixed_workload_100_ops(self, benchmark, benchmark_container, backend_mode):
        """
        Benchmark mixed workload: 100 operations
        - 40% creates
        - 30% reads
        - 20% upserts
        - 10% deletes
        """
        # Pre-create some items for read/update/delete operations
        existing_items = []
        for i in range(30):
            item_id = f"mixed-pre-{i}-{uuid.uuid4().hex[:8]}"
            item = {"id": item_id, "pk": f"mixed-pk-{i % 5}", "value": i}
            try:
                benchmark_container.create_item(item)
                existing_items.append((item_id, f"mixed-pk-{i % 5}"))
            except Exception:
                pass

        def mixed_workload():
            read_idx = 0
            delete_idx = 0

            for i in range(100):
                pk = f"mixed-pk-{i % 5}"

                if i % 10 < 4:  # 40% creates
                    item = {
                        "id": f"mixed-new-{uuid.uuid4().hex}",
                        "pk": pk,
                        "name": f"Mixed Item {i}",
                        "value": i
                    }
                    try:
                        benchmark_container.create_item(item)
                    except Exception:
                        pass

                elif i % 10 < 7:  # 30% reads
                    if read_idx < len(existing_items):
                        item_id, item_pk = existing_items[read_idx % len(existing_items)]
                        try:
                            benchmark_container.read_item(item_id, partition_key=item_pk)
                        except Exception:
                            pass
                        read_idx += 1

                elif i % 10 < 9:  # 20% upserts
                    item = {
                        "id": f"mixed-upsert-{i % 10}",
                        "pk": pk,
                        "name": f"Upserted {i}",
                        "value": i * 2
                    }
                    try:
                        benchmark_container.upsert_item(item)
                    except Exception:
                        pass

                else:  # 10% deletes
                    if delete_idx < len(existing_items):
                        item_id, item_pk = existing_items[delete_idx]
                        try:
                            benchmark_container.delete_item(item_id, partition_key=item_pk)
                        except Exception:
                            pass
                        delete_idx += 1

        benchmark.extra_info['backend'] = backend_mode
        benchmark.extra_info['operation_count'] = 100
        benchmark.extra_info['create_pct'] = 40
        benchmark.extra_info['read_pct'] = 30
        benchmark.extra_info['upsert_pct'] = 20
        benchmark.extra_info['delete_pct'] = 10
        benchmark(mixed_workload)


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
    report.append("| Operation | Python (ms) | Rust (ms) | Speedup | Improvement |")
    report.append("|-----------|-------------|-----------|---------|-------------|")

    python_benchmarks = {b["name"]: b["stats"] for b in python_data.get("benchmarks", [])}
    rust_benchmarks = {b["name"]: b["stats"] for b in rust_data.get("benchmarks", [])}

    total_py_time = 0
    total_rust_time = 0

    for name, py_stats in sorted(python_benchmarks.items()):
        if name in rust_benchmarks:
            rust_stats = rust_benchmarks[name]
            py_mean = py_stats["mean"] * 1000  # Convert to ms
            rust_mean = rust_stats["mean"] * 1000

            total_py_time += py_mean
            total_rust_time += rust_mean

            speedup = py_mean / rust_mean if rust_mean > 0 else 0
            improvement = ((py_mean - rust_mean) / py_mean) * 100 if py_mean > 0 else 0

            speedup_emoji = "🚀" if speedup > 1.1 else "⚖️" if speedup > 0.9 else "🐌"

            report.append(f"| {name} | {py_mean:.3f} | {rust_mean:.3f} | {speedup_emoji} {speedup:.2f}x | {improvement:.1f}% |")

    # Add totals
    if total_rust_time > 0:
        overall_speedup = total_py_time / total_rust_time
        overall_improvement = ((total_py_time - total_rust_time) / total_py_time) * 100
        report.append("|-----------|-------------|-----------|---------|-------------|")
        report.append(f"| **TOTAL** | **{total_py_time:.3f}** | **{total_rust_time:.3f}** | **{overall_speedup:.2f}x** | **{overall_improvement:.1f}%** |")

    report.append("\n## Summary\n")
    if overall_speedup > 1:
        report.append(f"🎉 **Rust backend is {overall_speedup:.2f}x faster overall!**\n")
    else:
        report.append(f"⚠️ Python backend was faster in this run.\n")

    with open(output_file, "w") as f:
        f.write("\n".join(report))

    print(f"Report generated: {output_file}")
    return overall_speedup


def run_comparison_benchmarks():
    """
    Run benchmarks for both Python and Rust backends and generate comparison.

    Usage:
        python -c "from tests.benchmarks.test_benchmark_phase1 import run_comparison_benchmarks; run_comparison_benchmarks()"
    """
    import subprocess
    import sys
    import os

    # Get the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))

    print("=" * 70)
    print("PHASE 1 BENCHMARK COMPARISON")
    print("Python (Pure Python) vs Rust Backend")
    print("=" * 70)

    # Run Python backend benchmarks
    print("\n[1/3] Running benchmarks with PURE PYTHON backend...")
    env_py = os.environ.copy()
    env_py["COSMOS_USE_RUST_BACKEND"] = "false"

    result_py = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/benchmarks/test_benchmark_phase1.py",
         "-v", "--benchmark-json=benchmark_python.json",
         "--benchmark-disable-gc"],
        cwd=project_root,
        env=env_py,
        capture_output=True,
        text=True
    )

    if result_py.returncode != 0:
        print(f"Python benchmark failed: {result_py.stderr}")
        return

    # Run Rust backend benchmarks
    print("\n[2/3] Running benchmarks with RUST backend...")
    env_rs = os.environ.copy()
    env_rs["COSMOS_USE_RUST_BACKEND"] = "true"

    result_rs = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/benchmarks/test_benchmark_phase1.py",
         "-v", "--benchmark-json=benchmark_rust.json",
         "--benchmark-disable-gc"],
        cwd=project_root,
        env=env_rs,
        capture_output=True,
        text=True
    )

    if result_rs.returncode != 0:
        print(f"Rust benchmark failed: {result_rs.stderr}")
        return

    # Generate comparison report
    print("\n[3/3] Generating comparison report...")
    py_results = os.path.join(project_root, "benchmark_python.json")
    rs_results = os.path.join(project_root, "benchmark_rust.json")
    report_file = os.path.join(project_root, "BENCHMARK_COMPARISON.md")

    speedup = generate_comparison_report(py_results, rs_results, report_file)

    print("\n" + "=" * 70)
    if speedup > 1:
        print(f"🎉 RUST IS {speedup:.2f}x FASTER THAN PURE PYTHON!")
    else:
        print(f"⚠️ Python was faster in this run (speedup: {speedup:.2f}x)")
    print("=" * 70)
    print(f"\nDetailed report: {report_file}")


if __name__ == "__main__":
    # Run benchmarks when executed directly
    pytest.main([__file__, "-v", "--benchmark-only"])

