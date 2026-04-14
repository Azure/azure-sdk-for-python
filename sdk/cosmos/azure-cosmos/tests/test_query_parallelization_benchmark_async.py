# The MIT License (MIT)
# Copyright (c) 2026 Microsoft Corporation

"""Benchmark test fixtures for async query parallelization.

These tests measure the performance impact of max_concurrency
on cross-partition queries. They require a live Cosmos DB account and are
skipped when ACCOUNT_HOST/ACCOUNT_KEY are not set.

Run with:
    pytest tests/test_query_parallelization_benchmark_async.py -v -m cosmosQuery --no-header

Set environment variables:
    ACCOUNT_HOST, ACCOUNT_KEY, COSMOS_DATABASE, COSMOS_CONTAINER
"""


import math
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
            offer_throughput=100000,  # High throughput to force multiple physical partitions
            indexing_policy=indexing_policy,
        )

        # Log the number of physical partitions
        pk_ranges = await container.client_connection._routing_map_provider \
            .get_overlapping_ranges(
                container.container_link,
                [Range("", "FF", True, False)])
        num_physical_partitions = len(pk_ranges)
        logger.info(f"Container created with {num_physical_partitions} physical partitions "
                     f"(100000 RU/s)")

        # Populate with test data — 10000 items across 400 logical partitions
        num_items = 10000
        num_logical_partitions = 400
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
        """Benchmark: cross-partition ORDER BY with varying parallelism."""
        total_ru = 0.0
        item_count = 0

        def hook(headers, _body):
            nonlocal total_ru
            total_ru += float(headers.get("x-ms-request-charge", "0"))

        start = time.perf_counter()
        items = cosmos_container.query_items(
            query="SELECT * FROM c ORDER BY c.numValue",
            max_concurrency=max_degree,
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
            max_concurrency=max_degree,
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
        """Benchmark: cross-partition filter+ORDER BY with varying parallelism."""
        total_ru = 0.0
        item_count = 0

        def hook(headers, _body):
            nonlocal total_ru
            total_ru += float(headers.get("x-ms-request-charge", "0"))

        start = time.perf_counter()
        items = cosmos_container.query_items(
            query="SELECT * FROM c WHERE c.category = 'cat_5' ORDER BY c.numValue",
            max_concurrency=max_degree,
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
    async def test_cross_partition_page_diagnostics(self, cosmos_container):
        """Diagnostic: measure doc size, pages per partition, per-page HTTP round-trip time.

        For each physical partition, issues ORDER BY queries page-by-page and
        captures three timing layers per page:
          - server_ms:  x-ms-request-duration-ms header (server processing only)
          - client_ms:  wall-clock time to fetch the page (network + server + deserialization)
          - RU:         x-ms-request-charge per page

        Then aggregates across all partitions and computes expected e2e latency
        using the formula:  avg_client_ms * partitions * pages_per_partition / concurrency
        """
        import json
        from azure.cosmos._routing.routing_range import Range

        # ── Step 1: Sample document sizes ──
        sample_query = cosmos_container.query_items(
            query="SELECT * FROM c OFFSET 0 LIMIT 10",
            max_concurrency=0,
        )
        sample_docs = []
        async for doc in sample_query:
            sample_docs.append(doc)
        doc_sizes = [len(json.dumps(doc).encode("utf-8")) for doc in sample_docs]
        avg_doc_bytes = sum(doc_sizes) / len(doc_sizes) if doc_sizes else 0
        logger.info(
            f"doc_sizes: sample={len(doc_sizes)}, "
            f"avg={avg_doc_bytes:.0f}B, min={min(doc_sizes)}B, max={max(doc_sizes)}B"
        )

        # ── Step 2: Get physical partition ranges ──
        pk_ranges = await cosmos_container.client_connection._routing_map_provider \
            .get_overlapping_ranges(
                cosmos_container.container_link,
                [Range("", "FF", True, False)])
        num_partitions = len(pk_ranges)

        # Accumulators
        all_client_latencies: list[float] = []   # wall-clock per page (ms)
        all_server_latencies: list[float] = []   # x-ms-request-duration-ms per page
        total_pages = 0
        total_items = 0
        total_ru = 0.0

        # ── Step 3: Per-partition page-by-page query ──
        for pkr in pk_ranges:
            range_id = pkr["id"]
            part_pages = 0
            part_items = 0
            part_ru = 0.0
            part_client_ms: list[float] = []
            part_server_ms: list[float] = []

            # Hook captures per-page RU and server-side duration
            page_ru = 0.0
            page_server_ms = 0.0

            def page_hook(headers, _body):
                nonlocal page_ru, page_server_ms
                page_ru = float(headers.get("x-ms-request-charge", "0"))
                page_server_ms = float(headers.get("x-ms-request-duration-ms", "0"))

            query_iter = cosmos_container.query_items(
                query="SELECT * FROM c ORDER BY c.numValue",
                partition_key_range_id=range_id,
                max_item_count=1000,
                response_hook=page_hook,
            )

            # Manually advance the page iterator so we can time each HTTP fetch
            page_iter = query_iter.by_page().__aiter__()
            while True:
                page_ru = 0.0
                page_server_ms = 0.0

                fetch_start = time.perf_counter()
                try:
                    page = await page_iter.__anext__()
                except StopAsyncIteration:
                    break
                # Count items (already in memory, no additional HTTP calls)
                items_in_page = 0
                async for _item in page:
                    items_in_page += 1
                fetch_elapsed_ms = (time.perf_counter() - fetch_start) * 1000

                part_pages += 1
                part_items += items_in_page
                part_ru += page_ru
                part_client_ms.append(fetch_elapsed_ms)
                part_server_ms.append(page_server_ms)
                all_client_latencies.append(fetch_elapsed_ms)
                all_server_latencies.append(page_server_ms)

            total_pages += part_pages
            total_items += part_items
            total_ru += part_ru

            avg_client = sum(part_client_ms) / len(part_client_ms) if part_client_ms else 0
            avg_server = sum(part_server_ms) / len(part_server_ms) if part_server_ms else 0
            logger.info(
                f"  partition {range_id}: pages={part_pages}, items={part_items}, "
                f"ru={part_ru:.1f}, avg_client={avg_client:.1f}ms, avg_server={avg_server:.1f}ms"
            )

        # ── Step 4: Aggregate latency stats ──
        n = len(all_client_latencies)
        pages_per_partition = total_pages / num_partitions if num_partitions else 0

        def percentile(sorted_vals, pct):
            idx = max(0, math.ceil(len(sorted_vals) * pct) - 1)
            return sorted_vals[idx]

        all_client_latencies.sort()
        all_server_latencies.sort()
        avg_client_ms = sum(all_client_latencies) / n if n else 0
        avg_server_ms = sum(all_server_latencies) / n if n else 0

        logger.info(
            f"PAGE SUMMARY: partitions={num_partitions}, total_pages={total_pages}, "
            f"pages/partition={pages_per_partition:.1f}, total_items={total_items}, "
            f"total_ru={total_ru:.1f}"
        )
        logger.info(
            f"CLIENT LATENCY (HTTP round-trip): "
            f"avg={avg_client_ms:.1f}ms, "
            f"p50={percentile(all_client_latencies, 0.50):.1f}ms, "
            f"p90={percentile(all_client_latencies, 0.90):.1f}ms, "
            f"p99={percentile(all_client_latencies, 0.99):.1f}ms"
        )
        logger.info(
            f"SERVER LATENCY (x-ms-request-duration-ms): "
            f"avg={avg_server_ms:.1f}ms, "
            f"p50={percentile(all_server_latencies, 0.50):.1f}ms, "
            f"p90={percentile(all_server_latencies, 0.90):.1f}ms, "
            f"p99={percentile(all_server_latencies, 0.99):.1f}ms"
        )
        logger.info(
            f"NETWORK OVERHEAD: avg={avg_client_ms - avg_server_ms:.1f}ms "
            f"(client_avg - server_avg)"
        )

        # ── Step 5: Expected e2e using formula ──
        #   e2e ≈ avg_client_ms * partitions * pages_per_partition / concurrency
        logger.info(
            f"EXPECTED E2E: {avg_client_ms:.1f}ms * {num_partitions} partitions * "
            f"{pages_per_partition:.1f} pages/partition"
        )
        for degree in [1, 2, 4, 8]:
            expected = avg_client_ms * num_partitions * pages_per_partition / degree
            logger.info(f"  degree={degree}: ~{expected:.1f}ms")

    @pytest.mark.asyncio(loop_scope="module")
    @pytest.mark.parametrize("max_degree", [0, 1, 2, 4, 8])
    async def test_cross_partition_scan_p99_latency(self, cosmos_container, max_degree):
        """P99 e2e latency: run cross-partition ORDER BY for 10 min, record every query latency."""
        duration_sec = 600  # 10 minutes
        latencies: list[float] = []
        total_ru = 0.0
        total_items = 0

        def hook(headers, _body):
            nonlocal total_ru
            total_ru += float(headers.get("x-ms-request-charge", "0"))

        deadline = time.perf_counter() + duration_sec
        while time.perf_counter() < deadline:
            start = time.perf_counter()
            items = cosmos_container.query_items(
                query="SELECT * FROM c ORDER BY c.numValue",
                max_concurrency=max_degree,
                response_hook=hook,
            )
            count = 0
            async for _ in items:
                count += 1
            elapsed = time.perf_counter() - start

            latencies.append(elapsed)
            total_items += count

        total_ops = len(latencies)
        latencies.sort()
        p50_idx = max(0, math.ceil(total_ops * 0.50) - 1)
        p90_idx = max(0, math.ceil(total_ops * 0.90) - 1)
        p99_idx = max(0, math.ceil(total_ops * 0.99) - 1)
        p50 = latencies[p50_idx]
        p90 = latencies[p90_idx]
        p99 = latencies[p99_idx]
        avg = sum(latencies) / total_ops if total_ops else 0
        total_time = sum(latencies)

        logger.info(
            f"p99 degree={max_degree}: ops={total_ops}, "
            f"avg={avg:.3f}s, p50={p50:.3f}s, p90={p90:.3f}s, p99={p99:.3f}s, "
            f"total_ru={total_ru:.1f}, total_items={total_items}, "
            f"wall={total_time:.1f}s"
        )

    @pytest.mark.asyncio(loop_scope="module")
    @pytest.mark.parametrize("max_degree", [0, 2, 4])
    async def test_result_consistency_across_degrees(self, cosmos_container, max_degree):
        """Verify that parallel queries return the same results as serial queries."""
        # Run serial query
        serial_items = []
        items = cosmos_container.query_items(
            query="SELECT c.id FROM c ORDER BY c.numValue",
            max_concurrency=0,
        )
        async for item in items:
            serial_items.append(item["id"])

        # Run parallel query
        parallel_items = []
        items = cosmos_container.query_items(
            query="SELECT c.id FROM c ORDER BY c.numValue",
            max_concurrency=max_degree,
        )
        async for item in items:
            parallel_items.append(item["id"])

        assert serial_items == parallel_items, (
            f"Results differ between degree=0 and degree={max_degree}: "
            f"serial={len(serial_items)} items, parallel={len(parallel_items)} items"
        )
