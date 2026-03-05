# The MIT License (MIT)
# Copyright (c) 2026 Microsoft Corporation

"""Benchmark test fixtures for async query parallelization.

These tests measure the performance impact of max_degree_of_parallelism
on cross-partition queries. They require a live Cosmos DB account and are
skipped when ACCOUNT_HOST/ACCOUNT_KEY are not set.

Run with:
    pytest tests/test_query_parallelization_benchmark_async.py -v -m cosmosQuery --no-header

Set environment variables:
    ACCOUNT_HOST, ACCOUNT_KEY, COSMOS_DATABASE, COSMOS_CONTAINER
"""


import os
import time
import uuid
import logging

import pytest
import pytest_asyncio

logger = logging.getLogger(__name__)

# Skip entire module if no Cosmos DB credentials are available
_SKIP_REASON = "ACCOUNT_HOST and ACCOUNT_KEY environment variables required"
_SKIP = not os.environ.get("ACCOUNT_HOST") or not os.environ.get("ACCOUNT_KEY")

ENDPOINT = os.environ.get("ACCOUNT_HOST", "")
KEY = os.environ.get("ACCOUNT_KEY", "")
DATABASE = os.environ.get("COSMOS_DATABASE", "benchmark_db")
CONTAINER = os.environ.get("COSMOS_CONTAINER", "benchmark_container")


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def cosmos_container():
    """Provide an async container client for benchmark tests."""
    from azure.cosmos.aio import CosmosClient
    from azure.cosmos.partition_key import PartitionKey
    from azure.cosmos._routing.routing_range import Range

    async with CosmosClient(ENDPOINT, KEY) as client:
        # Create database if needed
        database = await client.create_database_if_not_exists(DATABASE)
        # Delete and recreate container to ensure correct indexing policy
        try:
            await database.delete_container(CONTAINER)
        except Exception:  # noqa: BLE001
            pass
        indexing_policy = {
            "includedPaths": [{"path": "/*"}],
            "excludedPaths": [{"path": "/\"_etag\"/?"}],
        }
        container = await database.create_container(
            id=CONTAINER,
            partition_key=PartitionKey(path="/partitionKey"),
            offer_throughput=50000,  # High throughput to force multiple physical partitions
            indexing_policy=indexing_policy,
        )

        # Log the number of physical partitions
        pk_ranges = await container.client_connection._routing_map_provider \
            .get_overlapping_ranges(
                container.container_link,
                [Range("", "FF", True, False)])
        num_physical_partitions = len(pk_ranges)
        logger.info(f"Container created with {num_physical_partitions} physical partitions "
                     f"(50000 RU/s)")

        # Populate with test data — 5000 items across 200 logical partitions
        num_items = 5000
        num_logical_partitions = 200
        logger.info(f"Populating container with {num_items} items across "
                     f"{num_logical_partitions} logical partitions...")
        for i in range(num_items):
            doc = {
                "id": str(uuid.uuid4()),
                "partitionKey": f"pk_{i % num_logical_partitions}",
                "numValue": i,
                "category": f"cat_{i % 10}",
                "description": f"Benchmark doc {i}",
            }
            await container.create_item(body=doc)

        # Verify items are spread across physical partitions by querying per-range
        items_per_range: dict[str, int] = {}
        for pkr in pk_ranges:
            range_id = pkr["id"]
            count_query = container.query_items(
                query="SELECT VALUE COUNT(1) FROM c",
                partition_key_range_id=range_id,
            )
            count = 0
            async for result in count_query:
                count = result
            items_per_range[range_id] = count

        empty_ranges = [rid for rid, cnt in items_per_range.items() if cnt == 0]
        logger.info(f"Item distribution across {num_physical_partitions} physical partitions: "
                     f"{items_per_range}")
        if empty_ranges:
            logger.warning(f"WARNING: {len(empty_ranges)} physical partition(s) have 0 items: "
                           f"{empty_ranges}")
        assert not empty_ranges, (
            f"{len(empty_ranges)} of {num_physical_partitions} physical partitions "
            f"have no items — benchmark results will not reflect true parallelism"
        )

        yield container

        # Cleanup
        try:
            await database.delete_container(CONTAINER)
        except Exception:  # noqa: BLE001
            pass


@pytest.mark.cosmosQuery
@pytest.mark.skipif(_SKIP, reason=_SKIP_REASON)
class TestParallelQueryBenchmarks:
    """Benchmark tests for parallel cross-partition queries."""

    @pytest.mark.asyncio(loop_scope="module")
    @pytest.mark.parametrize("max_degree", [0, 1, 2, 4, 8])
    async def test_cross_partition_scan_benchmark(self, cosmos_container, max_degree):
        """Benchmark: cross-partition SELECT * with varying parallelism."""
        total_ru = 0.0
        item_count = 0

        def hook(headers, _body):
            nonlocal total_ru
            total_ru += float(headers.get("x-ms-request-charge", "0"))

        start = time.perf_counter()
        items = cosmos_container.query_items(
            query="SELECT * FROM c",
            max_degree_of_parallelism=max_degree,
            response_hook=hook,
        )
        async for _ in items:
            item_count += 1
        elapsed = time.perf_counter() - start

        items_per_sec = item_count / elapsed if elapsed > 0 else 0
        logger.info(
            f"scan degree={max_degree}: {elapsed:.3f}s, {total_ru:.1f} RU, "
            f"{item_count} items, {items_per_sec:.1f} items/s"
        )

    @pytest.mark.asyncio(loop_scope="module")
    @pytest.mark.parametrize("max_degree", [0, 1, 2, 4, 8])
    async def test_cross_partition_order_by_benchmark(self, cosmos_container, max_degree):
        """Benchmark: cross-partition ORDER BY with varying parallelism."""
        total_ru = 0.0
        item_count = 0

        def hook(headers, _body):
            nonlocal total_ru
            total_ru += float(headers.get("x-ms-request-charge", "0"))

        start = time.perf_counter()
        items = cosmos_container.query_items(
            query="SELECT * FROM c ORDER BY c.numValue",
            max_degree_of_parallelism=max_degree,
            response_hook=hook,
        )
        async for _ in items:
            item_count += 1
        elapsed = time.perf_counter() - start

        items_per_sec = item_count / elapsed if elapsed > 0 else 0
        logger.info(
            f"order_by degree={max_degree}: {elapsed:.3f}s, {total_ru:.1f} RU, "
            f"{item_count} items, {items_per_sec:.1f} items/s"
        )

    @pytest.mark.asyncio(loop_scope="module")
    @pytest.mark.parametrize("max_degree", [0, 1, 2, 4, 8])
    async def test_cross_partition_filter_benchmark(self, cosmos_container, max_degree):
        """Benchmark: cross-partition query with filter and varying parallelism."""
        total_ru = 0.0
        item_count = 0

        def hook(headers, _body):
            nonlocal total_ru
            total_ru += float(headers.get("x-ms-request-charge", "0"))

        start = time.perf_counter()
        items = cosmos_container.query_items(
            query="SELECT * FROM c WHERE c.category = 'cat_5'",
            max_degree_of_parallelism=max_degree,
            response_hook=hook,
        )
        async for _ in items:
            item_count += 1
        elapsed = time.perf_counter() - start

        items_per_sec = item_count / elapsed if elapsed > 0 else 0
        logger.info(
            f"filter degree={max_degree}: {elapsed:.3f}s, {total_ru:.1f} RU, "
            f"{item_count} items, {items_per_sec:.1f} items/s"
        )

    @pytest.mark.asyncio(loop_scope="module")
    @pytest.mark.parametrize("max_degree", [0, 2, 4])
    async def test_result_consistency_across_degrees(self, cosmos_container, max_degree):
        """Verify that parallel queries return the same results as serial queries."""
        # Run serial query
        serial_items = []
        items = cosmos_container.query_items(
            query="SELECT c.id FROM c ORDER BY c.numValue",
            max_degree_of_parallelism=0,
        )
        async for item in items:
            serial_items.append(item["id"])

        # Run parallel query
        parallel_items = []
        items = cosmos_container.query_items(
            query="SELECT c.id FROM c ORDER BY c.numValue",
            max_degree_of_parallelism=max_degree,
        )
        async for item in items:
            parallel_items.append(item["id"])

        assert serial_items == parallel_items, (
            f"Results differ between degree=0 and degree={max_degree}: "
            f"serial={len(serial_items)} items, parallel={len(parallel_items)} items"
        )
