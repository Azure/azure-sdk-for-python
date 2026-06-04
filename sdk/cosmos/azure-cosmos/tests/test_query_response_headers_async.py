# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
import os
import tracemalloc
import unittest
import uuid
from collections.abc import Mapping

import pytest
from azure.core.utils import CaseInsensitiveDict

import test_config
from azure.cosmos._cosmos_responses import CosmosAsyncItemPaged
from azure.cosmos.aio import CosmosClient, DatabaseProxy
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQueryResponseHeadersAsync(unittest.IsolatedAsyncioTestCase):
    """Tests for async query response headers functionality."""

    created_db: DatabaseProxy = None
    client: CosmosClient = None
    config = test_config.TestConfig
    host = config.host
    masterKey = config.masterKey
    TEST_DATABASE_ID = config.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        cls.use_multiple_write_locations = False
        if os.environ.get("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER", "False") == "True":
            cls.use_multiple_write_locations = True

    async def asyncSetUp(self):
        # Key-auth client for control-plane (container create/delete)
        self.key_client = CosmosClient(
            self.host, self.masterKey, multiple_write_locations=self.use_multiple_write_locations
        )
        await self.key_client.__aenter__()
        self.key_db = self.key_client.get_database_client(self.TEST_DATABASE_ID)

        # AAD data client for data-plane operations (queries, item create)
        self.client = self.config.create_data_client_async()
        await self.client.__aenter__()
        self.created_db = self.client.get_database_client(self.TEST_DATABASE_ID)

    async def asyncTearDown(self):
        await self.client.close()
        await self.key_client.close()

    async def _create_container_for_test(self, container_id, partition_key):
        """Create container via key-auth, return AAD data-plane proxy."""
        # container creation is control-plane; uses key-auth key_db.
        await self.key_db.create_container(container_id, partition_key)
        return self.created_db.get_container_client(container_id)

    async def _delete_container_for_test(self, container_id):
        """Delete container via key-auth."""
        # container deletion is control-plane; uses key-auth key_db.
        await self.key_db.delete_container(container_id)

    async def test_query_response_headers_single_page_async(self):
        """Test that response headers are captured for a single page query."""
        cid = "test_headers_single_async_" + str(uuid.uuid4())

        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            # Create a few items
            for i in range(5):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

            query = "SELECT * FROM c WHERE c.pk = @pk"
            query_iterable = created_collection.query_items(
                query=query,
                parameters=[{"name": "@pk", "value": "test"}],
                partition_key="test"
            )

            # Iterate through items using async for loop (pagination)
            items = []
            async for item in query_iterable:
                items.append(item)

            # Verify items were returned
            assert len(items) == 5

            # Verify response headers were captured
            response_headers = query_iterable.get_response_headers()
            assert response_headers is not None

            # Verify headers contain expected fields
            assert "x-ms-request-charge" in response_headers
            assert "x-ms-activity-id" in response_headers

        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_multiple_pages_async(self):
        """Test that response headers reflect the last page in a paginated query."""
        cid = "test_headers_multi_async_" + str(uuid.uuid4())

        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            # Create enough items to span multiple pages
            num_items = 15
            for i in range(num_items):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

            query = "SELECT * FROM c WHERE c.pk = @pk"
            # Use small page size to force multiple pages
            query_iterable = created_collection.query_items(
                query=query,
                parameters=[{"name": "@pk", "value": "test"}],
                partition_key="test",
                max_item_count=5  # Force pagination with 5 items per page
            )

            # Iterate through items using async for loop (pagination)
            items = []
            async for item in query_iterable:
                items.append(item)

            # Verify all items were returned
            assert len(items) == num_items

            # Verify response headers contain the last page's headers
            response_headers = query_iterable.get_response_headers()
            assert response_headers is not None
            assert "x-ms-request-charge" in response_headers
            assert "x-ms-activity-id" in response_headers

        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_empty_result_async(self):
        """Test that response headers are captured even when query returns no results."""
        cid = "test_headers_empty_async_" + str(uuid.uuid4())

        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            # Create an item with different pk
            await created_collection.create_item(body={"pk": "other", "id": "item_1"})

            query = "SELECT * FROM c WHERE c.pk = @pk"
            query_iterable = created_collection.query_items(
                query=query,
                parameters=[{"name": "@pk", "value": "nonexistent"}],
                partition_key="nonexistent"
            )

            # Iterate through items (should be empty)
            items = []
            async for item in query_iterable:
                items.append(item)

            # Verify no items were returned
            assert len(items) == 0

            # The key is that the method doesn't throw an error
            # and the headers are populated since an HTTP request was made
            response_headers = query_iterable.get_response_headers()
            assert "x-ms-request-charge" in response_headers

        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_with_query_metrics_async(self):
        """Test that query metrics are included in response headers when enabled."""
        cid = "test_headers_metrics_async_" + str(uuid.uuid4())

        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            # Create items
            for i in range(5):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

            query = "SELECT * FROM c WHERE c.pk = @pk"
            query_iterable = created_collection.query_items(
                query=query,
                parameters=[{"name": "@pk", "value": "test"}],
                partition_key="test",
                populate_query_metrics=True
            )

            # Iterate through items
            items = []
            async for item in query_iterable:
                items.append(item)

            assert len(items) == 5

            # Verify response headers contain query metrics
            response_headers = query_iterable.get_response_headers()
            assert response_headers is not None

            # Check for query metrics header
            metrics_header_name = "x-ms-documentdb-query-metrics"
            assert metrics_header_name in response_headers

            # Validate metrics header is well-formed
            metrics_header = response_headers[metrics_header_name]
            metrics = metrics_header.split(";")
            assert len(metrics) > 1
            assert all("=" in x for x in metrics)

        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_by_page_iteration_async(self):
        """Test response headers update per page, verified via x-ms-item-count."""
        cid = "test_headers_by_page_async_" + str(uuid.uuid4())

        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            # 7 items with max_item_count=3 gives pages of 3, 3, 1
            num_items = 7
            for i in range(num_items):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

            query = "SELECT * FROM c WHERE c.pk = @pk"
            query_iterable = created_collection.query_items(
                query=query,
                parameters=[{"name": "@pk", "value": "test"}],
                partition_key="test",
                max_item_count=3
            )

            # Iterate by page, tracking item counts from headers
            all_items = []
            item_counts = []
            async for page in query_iterable.by_page():
                page_items = [item async for item in page]
                all_items.extend(page_items)

                headers = query_iterable.get_response_headers()
                assert headers is not None
                assert "x-ms-item-count" in headers
                item_counts.append(int(headers["x-ms-item-count"]))

            # Verify all items retrieved
            assert len(all_items) == num_items

            # The last page should have fewer items than the page size,
            # proving headers are overwritten per page.
            # max_item_count is a hint, so pages may have fewer items than requested.
            assert len(item_counts) > 1
            assert sum(item_counts) == num_items
            assert item_counts[-1] < item_counts[0]

        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_long_pagination_bounded_memory_async(self):
        """Paging through many pages does not grow the response-headers
        state on the iterator: the headers dict size stays close to the
        first page and overall memory growth stays under a small ceiling."""
        cid = "test_headers_long_pagination_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            num_items = 200
            for i in range(num_items):
                await created_collection.create_item(
                    body={"pk": "test", "id": f"item_{i:04d}", "value": i}
                )

            query_iterable = created_collection.query_items(
                query="SELECT * FROM c WHERE c.pk = @pk",
                parameters=[{"name": "@pk", "value": "test"}],
                partition_key="test",
                max_item_count=2,
            )

            # Read the first page outside the memory window so one-time
            # client setup is not counted as growth.
            page_iter = query_iterable.by_page()
            first_page = await page_iter.__anext__()
            first_page_items = [item async for item in first_page]
            baseline_headers = query_iterable.get_response_headers()
            assert baseline_headers is not None

            tracemalloc.start()
            snapshot_before = tracemalloc.take_snapshot()

            page_count = 1
            header_sizes = [len(baseline_headers)]
            all_keys_seen = set(baseline_headers.keys())
            all_items = list(first_page_items)

            async for page in page_iter:
                page_items = [item async for item in page]
                all_items.extend(page_items)
                page_count += 1
                headers = query_iterable.get_response_headers()
                assert headers is not None
                header_sizes.append(len(headers))
                all_keys_seen.update(headers.keys())

            snapshot_after = tracemalloc.take_snapshot()
            top_stats = snapshot_after.compare_to(snapshot_before, "lineno")
            memory_growth = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
            tracemalloc.stop()

            # Make sure we really paginated and read all the items back.
            assert page_count >= 20, (
                "Expected many pages, got {}.".format(page_count)
            )
            assert len(all_items) == num_items

            # The headers dict on any single page stays close to the first
            # page's size, even after many pages.
            max_header_size = max(header_sizes)
            assert max_header_size <= len(baseline_headers) + 8, (
                "Headers dict grew across pagination (max={}, baseline={}).".format(
                    max_header_size, len(baseline_headers)
                )
            )

            # The total set of header names seen across all pages stays
            # bounded; it does not grow proportional to page count.
            assert len(all_keys_seen) <= len(baseline_headers) + 16, (
                "Header name set grew across pagination (seen={}, baseline={}).".format(
                    len(all_keys_seen), len(baseline_headers)
                )
            )

            # Memory growth should stay well under a 2 MiB ceiling.
            ceiling_bytes = 2 * 1024 * 1024
            assert memory_growth < ceiling_bytes, (
                "Memory grew by {} bytes over {} pages (ceiling {} bytes).".format(
                    memory_growth, page_count, ceiling_bytes,
                )
            )

        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_returns_copies_async(self):
        """Test that get_response_headers returns copies, not references."""
        cid = "test_headers_copies_async_" + str(uuid.uuid4())

        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            await created_collection.create_item(body={"pk": "test", "id": "item_1"})

            query = "SELECT * FROM c"
            query_iterable = created_collection.query_items(
                query=query,
                partition_key="test"
            )

            # Iterate
            async for item in query_iterable:
                pass

            # Get headers twice
            headers1 = query_iterable.get_response_headers()
            headers2 = query_iterable.get_response_headers()

            # They should be distinct objects
            assert headers1 is not headers2

            # Modifying one should not affect the other
            headers1["test-key"] = "test-value"
            assert "test-key" not in headers2

        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_concurrent_async(self):
        """Test that response headers are captured correctly when multiple async queries run concurrently.
        
        This test verifies that each query operation captures its own headers independently,
        without interference from concurrent queries. This is the key thread-safety guarantee.
        """
        cid = "test_headers_concurrent_async_" + str(uuid.uuid4())

        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            # Create items with different partition keys
            num_partitions = 5
            items_per_partition = 10
            for pk_idx in range(num_partitions):
                for item_idx in range(items_per_partition):
                    await created_collection.create_item(
                        body={"pk": f"partition_{pk_idx}", "id": f"item_{pk_idx}_{item_idx}", "value": item_idx}
                    )

            async def run_query(partition_key: str, query_id: int):
                """Run a query and capture its headers."""
                query = "SELECT * FROM c WHERE c.pk = @pk"
                query_iterable = created_collection.query_items(
                    query=query,
                    parameters=[{"name": "@pk", "value": partition_key}],
                    partition_key=partition_key,
                    max_item_count=2,  # Small page size to ensure multiple pages
                    populate_query_metrics=True
                )

                # Consume all items
                items = [item async for item in query_iterable]
                headers = query_iterable.get_response_headers()

                return {
                    "query_id": query_id,
                    "partition_key": partition_key,
                    "item_count": len(items),
                    "headers": headers
                }

            # Run multiple queries concurrently using asyncio.gather
            num_queries = 10
            tasks = []
            for i in range(num_queries):
                partition_key = f"partition_{i % num_partitions}"
                tasks.append(run_query(partition_key, i))

            results = await asyncio.gather(*tasks)

            # Verify all queries got results
            assert len(results) == num_queries

            # Verify each query captured headers correctly
            for result in results:
                assert result["item_count"] == items_per_partition, \
                    f"Query {result['query_id']} got wrong item count"
                assert "x-ms-request-charge" in result["headers"], \
                    f"Query {result['query_id']} headers missing x-ms-request-charge"

            # Verify that different queries have independent header dicts
            if len(results) >= 2:
                assert results[0]["headers"] is not results[1]["headers"]

        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_high_concurrency_async(self):
        """Test with high concurrency to stress-test the thread-safety.
        
        This test specifically targets the race condition that would occur if headers
        were captured from a shared client.last_response_headers after fetch operations.
        """
        cid = "test_headers_stress_async_" + str(uuid.uuid4())

        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            # Create enough items to ensure multiple pages
            for i in range(50):
                await created_collection.create_item(
                    body={"pk": "shared", "id": f"item_{i}", "value": i}
                )

            # Use an event to synchronize all coroutines
            start_event = asyncio.Event()

            async def run_synchronized_query(query_id: int):
                """Run a query with synchronization to maximize overlap."""
                query_iterable = created_collection.query_items(
                    query="SELECT * FROM c WHERE c.pk = @pk",
                    parameters=[{"name": "@pk", "value": "shared"}],
                    partition_key="shared",
                    max_item_count=5,  # Small pages = more fetches
                    populate_query_metrics=True
                )

                # Wait for the start signal
                await start_event.wait()

                # Now all coroutines fetch concurrently
                items = [item async for item in query_iterable]
                headers = query_iterable.get_response_headers()

                return {
                    "query_id": query_id,
                    "item_count": len(items),
                    "request_charge": float(headers.get("x-ms-request-charge", 0))
                }

            # Create tasks but don't start fetching yet
            num_concurrent = 20
            tasks = [run_synchronized_query(i) for i in range(num_concurrent)]

            # Schedule all tasks
            gathered = asyncio.gather(*tasks)

            # Give tasks time to reach the wait point
            await asyncio.sleep(0.1)

            # Signal all to start simultaneously
            start_event.set()

            # Wait for all to complete
            results = await gathered

            # Verify all queries completed correctly
            assert len(results) == num_concurrent
            for result in results:
                assert result["item_count"] == 50, \
                    f"Query {result['query_id']} should have gotten all 50 items"
                assert result["request_charge"] > 0, \
                    f"Query {result['query_id']} should have positive request charge"

        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_before_iteration_returns_empty_async(self):
        """Headers must be an empty dict when no async page has been fetched yet."""
        cid = "test_headers_preiter_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            await created_collection.create_item(body={"pk": "test", "id": "item_1"})

            query_iterable = created_collection.query_items(
                query="SELECT * FROM c",
                partition_key="test",
            )

            # No iteration yet, so the dict must be empty (and not None).
            headers = query_iterable.get_response_headers()
            assert isinstance(headers, CaseInsensitiveDict)
            assert len(headers) == 0
        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_match_last_response_hook_invocation_async(self):
        """The headers returned after async iteration must match the headers
        handed to the last response_hook call."""
        cid = "test_headers_hookparity_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            for i in range(12):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

            captured_pages = []

            def hook(headers, _result):
                captured_pages.append(dict(headers))

            query_iterable = created_collection.query_items(
                query="SELECT * FROM c WHERE c.pk = @pk",
                parameters=[{"name": "@pk", "value": "test"}],
                partition_key="test",
                max_item_count=4,
                response_hook=hook,
            )

            items = [item async for item in query_iterable]
            assert len(items) == 12
            assert len(captured_pages) > 0

            final_headers = query_iterable.get_response_headers()
            assert final_headers["x-ms-request-charge"] == captured_pages[-1]["x-ms-request-charge"]
            assert final_headers["x-ms-activity-id"] == captured_pages[-1]["x-ms-activity-id"]
        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_return_type_is_dict_not_list_async(self):
        """The getter returns a single dict (not a list), and the old
        get_last_response_headers method is not available."""
        cid = "test_headers_returntype_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            await created_collection.create_item(body={"pk": "test", "id": "item_1"})

            query_iterable = created_collection.query_items(
                query="SELECT * FROM c",
                partition_key="test",
            )
            assert isinstance(query_iterable, CosmosAsyncItemPaged)

            _ = [item async for item in query_iterable]
            headers = query_iterable.get_response_headers()

            assert isinstance(headers, CaseInsensitiveDict)
            assert not isinstance(headers, list)
            assert not hasattr(query_iterable, "get_last_response_headers")
        finally:
            await self._delete_container_for_test(cid)

    async def test_read_all_items_response_headers_async(self):
        """read_all_items pagers expose the same headers contract as queries."""
        cid = "test_headers_readall_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            for i in range(8):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            paged = created_collection.read_all_items(max_item_count=3)
            items = [item async for item in paged]
            assert len(items) == 8

            if hasattr(paged, "get_response_headers"):
                headers = paged.get_response_headers()
                assert isinstance(headers, CaseInsensitiveDict)
                assert "x-ms-request-charge" in headers
        finally:
            await self._delete_container_for_test(cid)

    # -- response_hook parity across every paged and point surface ----------
    #
    # Previously only query_items had explicit parity coverage between the
    # headers handed to a per-call response_hook and the headers returned
    # by the pager or CosmosDict. The tests below extend that same
    # guarantee to read_all_items, the change feed, point CRUD, and the
    # database and container query surfaces.

    async def test_response_hook_parity_read_all_items_async(self):
        """Headers handed to the last response_hook invocation on async
        read_all_items must match the pager's get_response_headers()."""
        cid = "test_hookparity_readall_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            for i in range(10):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            captured = []

            def hook(headers, _result):
                captured.append(dict(headers))

            paged = created_collection.read_all_items(max_item_count=3, response_hook=hook)
            items = [item async for item in paged]
            assert len(items) == 10
            assert len(captured) > 0, "response_hook must fire at least once"

            final_headers = paged.get_response_headers()
            assert "x-ms-request-charge" in final_headers
            assert final_headers["x-ms-request-charge"] == captured[-1]["x-ms-request-charge"]
            assert final_headers["x-ms-activity-id"] == captured[-1]["x-ms-activity-id"]
        finally:
            await self._delete_container_for_test(cid)

    async def test_response_hook_parity_query_items_change_feed_async(self):
        """Headers handed to the response_hook on async change feed must
        match the pager's get_response_headers() when the pager exposes
        one (some change-feed pager flavors don't)."""
        cid = "test_hookparity_cf_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            for i in range(6):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            captured = []

            def hook(headers, _result):
                captured.append(dict(headers))

            paged = created_collection.query_items_change_feed(
                start_time="Beginning",
                max_item_count=2,
                response_hook=hook,
            )
            items = [item async for item in paged]
            assert len(items) >= 6
            assert len(captured) > 0, "response_hook must fire at least once"

            assert "x-ms-request-charge" in captured[-1]

            if hasattr(paged, "get_response_headers"):
                final_headers = paged.get_response_headers()
                if "x-ms-request-charge" in final_headers:
                    assert (
                        final_headers["x-ms-request-charge"]
                        == captured[-1]["x-ms-request-charge"]
                    )
        finally:
            await self._delete_container_for_test(cid)

    async def test_response_hook_parity_point_ops_async(self):
        """For every async point CRUD method, the headers handed to the
        response_hook must match the returned CosmosDict's
        get_response_headers() (and ``delete_item`` returns no body)."""
        cid = "test_hookparity_point_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            # create_item
            captured.clear()
            created = await created_collection.create_item(
                body={"pk": "p", "id": "doc1", "value": 1},
                response_hook=hook,
            )
            assert len(captured) == 1
            assert (
                created.get_response_headers()["x-ms-request-charge"]
                == captured[0]["x-ms-request-charge"]
            )

            # read_item
            captured.clear()
            read = await created_collection.read_item(
                item="doc1", partition_key="p", response_hook=hook,
            )
            assert len(captured) == 1
            assert (
                read.get_response_headers()["x-ms-request-charge"]
                == captured[0]["x-ms-request-charge"]
            )

            # replace_item
            captured.clear()
            replaced = await created_collection.replace_item(
                item="doc1",
                body={"pk": "p", "id": "doc1", "value": 2},
                response_hook=hook,
            )
            assert len(captured) == 1
            assert (
                replaced.get_response_headers()["x-ms-request-charge"]
                == captured[0]["x-ms-request-charge"]
            )

            # upsert_item
            captured.clear()
            upserted = await created_collection.upsert_item(
                body={"pk": "p", "id": "doc1", "value": 3},
                response_hook=hook,
            )
            assert len(captured) == 1
            assert (
                upserted.get_response_headers()["x-ms-request-charge"]
                == captured[0]["x-ms-request-charge"]
            )

            # delete_item: returns None, but the hook still fires once.
            captured.clear()
            await created_collection.delete_item(
                item="doc1", partition_key="p", response_hook=hook,
            )
            assert len(captured) == 1
            assert "x-ms-request-charge" in captured[0]
        finally:
            await self._delete_container_for_test(cid)

    async def test_response_hook_parity_query_databases_and_query_containers_async(self):
        """Async query_databases and query_containers fire their hook once
        after the iterable is returned (the hook fires before the caller
        walks the iterable). ``query_databases`` passes one arg (just
        headers); ``query_containers`` passes two (headers, paged); accept
        both via ``*args``.

        We pin: the hook fires exactly once for each surface, and the
        captured payload is a Mapping. We deliberately do *not* pin a
        specific header like ``x-ms-request-charge`` because the hook
        fires with ``client_connection.last_response_headers`` at the
        moment the pager is constructed, which can be a stale value from
        an earlier request when nothing has yet flowed through this
        specific query."""

        captured_db = []

        def hook_db(*args):
            captured_db.append(args[0])

        db_pager = self.client.query_databases(
            query="SELECT * FROM root r",
            response_hook=hook_db,
        )
        _ = [item async for item in db_pager]
        assert len(captured_db) == 1, "query_databases hook must fire exactly once"
        assert isinstance(captured_db[0], Mapping)

        captured_c = []

        def hook_c(*args):
            captured_c.append(args[0])

        c_pager = self.created_db.query_containers(
            query="SELECT * FROM root r",
            response_hook=hook_c,
        )
        _ = [item async for item in c_pager]
        assert len(captured_c) == 1, "query_containers hook must fire exactly once"
        assert isinstance(captured_c[0], Mapping)

    async def test_response_hook_fires_at_least_once_for_every_paged_surface_async(self):
        """A response_hook attached to any async paged data-plane surface must
        fire at least once, and every captured payload must be a Mapping."""

        cid = "test_hookfires_paged_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            for i in range(6):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            async def _run(surface_name, build_pager):
                captured = []

                def hook(headers, _result):
                    captured.append(dict(headers))

                pager = build_pager(hook)
                _ = [item async for item in pager]
                assert len(captured) > 0, f"{surface_name} response_hook never fired"
                for payload in captured:
                    assert isinstance(payload, Mapping), \
                        f"{surface_name} hook received non-Mapping payload"

            await _run(
                "query_items",
                lambda h: created_collection.query_items(
                    query="SELECT * FROM c",
                    partition_key="test",
                    response_hook=h,
                ),
            )
            await _run(
                "read_all_items",
                lambda h: created_collection.read_all_items(
                    max_item_count=2,
                    response_hook=h,
                ),
            )
            await _run(
                "query_items_change_feed",
                lambda h: created_collection.query_items_change_feed(
                    start_time="Beginning",
                    max_item_count=2,
                    response_hook=h,
                ),
            )
        finally:
            await self._delete_container_for_test(cid)

    # -- response_hook parity for patch_item / execute_item_batch (async) --
    #
    # Both methods accept a response_hook keyword. The hook must fire
    # exactly once per call and receive the same response headers that
    # the returned wrapper exposes via get_response_headers().

    async def test_response_hook_parity_patch_item_async(self):
        # Async patch_item must fire its response_hook once with headers
        # that match the returned wrapper.
        cid = "test_hookparity_patch_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(
            cid, PartitionKey(path="/pk")
        )
        try:
            await created_collection.create_item(
                body={"pk": "p", "id": "doc-patch", "value": 1}
            )

            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            patched = await created_collection.patch_item(
                item="doc-patch",
                partition_key="p",
                patch_operations=[
                    {"op": "replace", "path": "/value", "value": 99}
                ],
                response_hook=hook,
            )

            assert len(captured) == 1
            patched_headers = patched.get_response_headers()
            assert (
                patched_headers["x-ms-request-charge"]
                == captured[0]["x-ms-request-charge"]
            )
            assert (
                patched_headers["x-ms-activity-id"]
                == captured[0]["x-ms-activity-id"]
            )
            assert patched["value"] == 99
        finally:
            await self._delete_container_for_test(cid)

    async def test_response_hook_parity_execute_item_batch_async(self):
        # Async execute_item_batch must fire its response_hook once with
        # headers that match the returned wrapper.
        cid = "test_hookparity_batch_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(
            cid, PartitionKey(path="/pk")
        )
        try:
            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            batch_ops = [
                ("create", ({"pk": "p", "id": "batch-doc-1", "value": 1},)),
                ("upsert", ({"pk": "p", "id": "batch-doc-2", "value": 2},)),
            ]

            result = await created_collection.execute_item_batch(
                batch_operations=batch_ops,
                partition_key="p",
                response_hook=hook,
            )

            assert len(captured) == 1
            result_headers = result.get_response_headers()
            assert (
                result_headers["x-ms-request-charge"]
                == captured[0]["x-ms-request-charge"]
            )
            assert (
                result_headers["x-ms-activity-id"]
                == captured[0]["x-ms-activity-id"]
            )
            assert len(result) == 2
        finally:
            await self._delete_container_for_test(cid)


if __name__ == "__main__":
    unittest.main()
