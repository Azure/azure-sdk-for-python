# The MIT License (MIT)
# Copyright (c) 2026 Microsoft Corporation

"""Benchmark test fixtures for async query parallelization.

These tests measure the performance impact of max_degree_of_parallelism
on cross-partition queries. They require a live Cosmos DB account and are
skipped by default (mark with pytest.mark.benchmark).

Run with:
    pytest tests/test_query_parallelization_benchmark_async.py -v -m benchmark --no-header

Set environment variables:
    COSMOS_ENDPOINT, COSMOS_KEY, COSMOS_DATABASE, COSMOS_CONTAINER
"""


import os
import time
import uuid
import logging

import pytest

logger = logging.getLogger(__name__)

# Skip entire module if no Cosmos DB credentials are available
pytestmark = [
    pytest.mark.benchmark,
    pytest.mark.asyncio,
    pytest.mark.skipif(
        not os.environ.get("COSMOS_ENDPOINT") or not os.environ.get("COSMOS_KEY"),
        reason="COSMOS_ENDPOINT and COSMOS_KEY environment variables required"
    ),
]

ENDPOINT = os.environ.get("COSMOS_ENDPOINT", "")
KEY = os.environ.get("COSMOS_KEY", "")
DATABASE = os.environ.get("COSMOS_DATABASE", "benchmark_db")
CONTAINER = os.environ.get("COSMOS_CONTAINER", "benchmark_container")


@pytest.fixture(scope="module")
async def cosmos_container():
    """Provide an async container client for benchmark tests."""
    from azure.cosmos.aio import CosmosClient
    from azure.cosmos.partition_key import PartitionKey

    async with CosmosClient(ENDPOINT, KEY) as client:
        # Create database if needed
        database = await client.create_database_if_not_exists(DATABASE)
        # Create container if needed
        container = await database.create_container_if_not_exists(
            id=CONTAINER,
            partition_key=PartitionKey(path="/partitionKey"),
            offer_throughput=10000,  # Use reasonable throughput for benchmarks
        )

        # Populate with test data if empty
        count_items = container.query_items(query="SELECT VALUE COUNT(1) FROM c")
        count = 0
        async for result in count_items:
            count = result

        if count < 200:
            logger.info("Populating container with 500 items for benchmarks...")
            for i in range(500):
                doc = {
                    "id": str(uuid.uuid4()),
                    "partitionKey": f"pk_{i % 50}",
                    "value": i,
                    "category": f"cat_{i % 10}",
                    "description": f"Benchmark doc {i}",
                }
                await container.create_item(body=doc)

        yield container


class TestParallelQueryBenchmarks:
    """Benchmark tests for parallel cross-partition queries."""

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
            query="SELECT * FROM c ORDER BY c.value",
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

    @pytest.mark.parametrize("max_degree", [0, 2, 4])
    async def test_result_consistency_across_degrees(self, cosmos_container, max_degree):
        """Verify that parallel queries return the same results as serial queries."""
        # Run serial query
        serial_items = []
        items = cosmos_container.query_items(
            query="SELECT c.id FROM c ORDER BY c.value",
            max_degree_of_parallelism=0,
        )
        async for item in items:
            serial_items.append(item["id"])

        # Run parallel query
        parallel_items = []
        items = cosmos_container.query_items(
            query="SELECT c.id FROM c ORDER BY c.value",
            max_degree_of_parallelism=max_degree,
        )
        async for item in items:
            parallel_items.append(item["id"])

        assert serial_items == parallel_items, (
            f"Results differ between degree=0 and degree={max_degree}: "
            f"serial={len(serial_items)} items, parallel={len(parallel_items)} items"
        )
