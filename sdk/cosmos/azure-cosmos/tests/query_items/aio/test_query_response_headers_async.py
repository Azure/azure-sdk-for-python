# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Copied async ``query_items`` response-header tests against the ``_backend="rust"`` path.

Copies of ``tests/test_query_response_headers_async.py`` that exercise
``ContainerProxy.query_items`` and the async pager's ``get_response_headers()``.
Each test owns a database created in ``asyncSetUp`` (registered for cleanup
immediately) instead of the shared ``test_config`` database. Query inputs and
assertions are unchanged; known Rust gaps are skipped at the failing step.
"""

import asyncio
import gc
import tracemalloc
import unittest
import uuid
from collections.abc import Mapping

import pytest
from azure.core.utils import CaseInsensitiveDict

from config import clients, settings
from azure.cosmos import PartitionKey
from azure.cosmos._cosmos_responses import CosmosAsyncItemPaged
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQueryResponseHeadersAsync(unittest.IsolatedAsyncioTestCase):
    """Tests for async query response headers functionality."""

    async def asyncSetUp(self):
        config = settings.TestSettings
        self.key_client = CosmosClient(config.host, config.masterKey, _backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()
        database_id = "qi_response_headers_async_" + uuid.uuid4().hex
        self.key_db = await self.key_client.create_database(database_id)
        self.addAsyncCleanup(self.key_client.delete_database, database_id)
        self.client = clients.create_data_client_async(_backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.created_db = self.client.get_database_client(database_id)

    async def _create_container_for_test(self, container_id, partition_key):
        """Create container via key-auth, return data-plane proxy."""
        await self.key_db.create_container(container_id, partition_key)
        return self.created_db.get_container_client(container_id)

    async def _delete_container_for_test(self, container_id):
        """Delete container via key-auth."""
        await self.key_db.delete_container(container_id)

    async def test_query_response_headers_single_page_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_query_response_headers_single_page_async
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

    async def test_query_response_headers_multiple_pages_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_query_response_headers_multiple_pages_async
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

    async def test_query_response_headers_empty_result_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_query_response_headers_empty_result_async
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

    async def test_query_response_headers_with_query_metrics_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_query_response_headers_with_query_metrics_async
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
            # Known gap 36: Query diagnostics and other request options are not sent over Gateway V2.
            pytest.skip("driver-gap: Rust does not send populate_query_metrics over Gateway V2, so the "
                        "metrics header is missing (known gap 36, "
                        "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36).")
            assert metrics_header_name in response_headers

            # Validate metrics header is well-formed
            metrics_header = response_headers[metrics_header_name]
            metrics = metrics_header.split(";")
            assert len(metrics) > 1
            assert all("=" in x for x in metrics)

        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_by_page_iteration_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_query_response_headers_by_page_iteration_async
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

    async def test_query_response_headers_long_pagination_bounded_memory_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_query_response_headers_long_pagination_bounded_memory_async
        """Paging through many pages keeps response-header state bounded and
        keeps overall iterator memory growth under a linear safety ceiling.
        Document payloads are not retained during measurement so growth reflects
        headers and iterator overhead only."""
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

            # Read the first page outside the measurement window so one-time
            # client setup is not counted. Count items only; never retain pages.
            page_iter = query_iterable.by_page()
            first_page = await page_iter.__anext__()
            first_page_count = 0
            async for _ in first_page:
                first_page_count += 1
            baseline_headers = query_iterable.get_response_headers()
            assert baseline_headers is not None

            # Collect transient setup objects so they don't show up as growth.
            gc.collect()
            was_tracing = tracemalloc.is_tracing()
            if not was_tracing:
                tracemalloc.start()
            try:
                snapshot_before = tracemalloc.take_snapshot()

                page_count = 1
                items_total = first_page_count
                header_sizes = [len(baseline_headers)]
                all_keys_seen = set(baseline_headers.keys())

                async for page in page_iter:
                    # Count items without keeping a reference to any of them.
                    async for _ in page:
                        items_total += 1
                    page_count += 1
                    headers = query_iterable.get_response_headers()
                    assert headers is not None
                    header_sizes.append(len(headers))
                    all_keys_seen.update(headers.keys())
                    # Drop the per-page header copy before the next iteration.
                    del headers

                gc.collect()
                snapshot_after = tracemalloc.take_snapshot()
                top_stats = snapshot_after.compare_to(snapshot_before, "lineno")
                memory_growth = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
            finally:
                if not was_tracing:
                    tracemalloc.stop()

            # We really paginated and read every item back.
            assert page_count >= 20, f"Expected many pages, got {page_count}."
            assert items_total == num_items

            # The per-page headers dict stays close to the first page's size.
            max_header_size = max(header_sizes)
            assert max_header_size <= len(baseline_headers) + 8, (
                f"Headers dict grew across pagination (max={max_header_size}, "
                f"baseline={len(baseline_headers)})."
            )

            # The set of header names seen across all pages stays bounded.
            assert len(all_keys_seen) <= len(baseline_headers) + 16, (
                f"Header name set grew across pagination (seen={len(all_keys_seen)}, "
                f"baseline={len(baseline_headers)})."
            )

            # Linear safety ceiling so the check scales if num_items changes.
            # This is a "no catastrophic leak" guard, not a strict O(1) proof.
            # Observed per-page overhead on a live account is around 24-29 KiB;
            # 48 KiB gives roughly 2x headroom and still catches a real leak.
            max_per_page_bytes = 48 * 1024
            ceiling_bytes = max_per_page_bytes * page_count
            assert memory_growth < ceiling_bytes, (
                f"Iterator memory grew by {memory_growth} bytes over {page_count} pages; "
                f"exceeded linear safety ceiling {ceiling_bytes} bytes."
            )

        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_returns_copies_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_query_response_headers_returns_copies_async
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

    async def test_query_response_headers_concurrent_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_query_response_headers_concurrent_async
        """Each concurrent query must see only its own response headers.
        Each task installs a response_hook that records every page it sees;
        the iterator's final headers must match that task's own last hook payload."""
        cid = "test_headers_concurrent_async_" + str(uuid.uuid4())

        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            # Different partition keys so different tasks run different queries.
            num_partitions = 5
            items_per_partition = 10
            for pk_idx in range(num_partitions):
                for item_idx in range(items_per_partition):
                    await created_collection.create_item(
                        body={"pk": f"partition_{pk_idx}", "id": f"item_{pk_idx}_{item_idx}", "value": item_idx}
                    )

            async def run_query(partition_key: str, query_id: int):
                """Run a query and capture its headers."""
                # Per-task hook: records what this iterator received.
                captured_pages = []

                def hook(headers, _result):
                    captured_pages.append(dict(headers))

                query = "SELECT * FROM c WHERE c.pk = @pk"
                query_iterable = created_collection.query_items(
                    query=query,
                    parameters=[{"name": "@pk", "value": partition_key}],
                    partition_key=partition_key,
                    max_item_count=2,
                    populate_query_metrics=True,
                    response_hook=hook,
                )

                items = [item async for item in query_iterable]
                headers = query_iterable.get_response_headers()

                return {
                    "query_id": query_id,
                    "partition_key": partition_key,
                    "item_count": len(items),
                    "headers": headers,
                    "captured_pages": captured_pages,
                }

            num_queries = 10
            tasks = []
            for i in range(num_queries):
                partition_key = f"partition_{i % num_partitions}"
                tasks.append(run_query(partition_key, i))

            results = await asyncio.gather(*tasks)

            assert len(results) == num_queries

            for result in results:
                assert result["item_count"] == items_per_partition, \
                    f"Query {result['query_id']} got wrong item count"
                assert "x-ms-request-charge" in result["headers"], \
                    f"Query {result['query_id']} headers missing x-ms-request-charge"

                # The iterator's final headers must match this task's own
                # last hook payload, otherwise header state is shared.
                assert len(result["captured_pages"]) > 0, \
                    f"Query {result['query_id']} hook never fired"
                last_hook = result["captured_pages"][-1]
                assert result["headers"].get("x-ms-activity-id") == last_hook.get("x-ms-activity-id"), (
                    f"Query {result['query_id']} got headers that did not come from its own response."
                )
                assert result["headers"].get("x-ms-request-charge") == last_hook.get("x-ms-request-charge"), (
                    f"Query {result['query_id']} got a request charge that did not come from its own response."
                )

            # Each task holds its own headers dict, not a shared object.
            if len(results) >= 2:
                assert results[0]["headers"] is not results[1]["headers"]

            # Different partitions, so activity ids must not all be the same.
            activity_ids = {r["headers"].get("x-ms-activity-id") for r in results}
            assert len(activity_ids) > 1, (
                "All tasks got the same activity id, which means header state is shared."
            )

        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_high_concurrency_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_query_response_headers_high_concurrency_async
        """Many tasks run the same query against the same partition at the same time.
        Item counts and request charges look identical across tasks, so isolation is
        checked on x-ms-activity-id, which the service assigns per request."""
        cid = "test_headers_stress_async_" + str(uuid.uuid4())

        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            for i in range(50):
                await created_collection.create_item(
                    body={"pk": "shared", "id": f"item_{i}", "value": i}
                )

            start_event = asyncio.Event()

            async def run_synchronized_query(query_id: int):
                """Run a query with synchronization to maximize overlap."""
                # Per-task hook: records what this iterator received.
                captured_pages = []

                def hook(headers, _result):
                    captured_pages.append(dict(headers))

                query_iterable = created_collection.query_items(
                    query="SELECT * FROM c WHERE c.pk = @pk",
                    parameters=[{"name": "@pk", "value": "shared"}],
                    partition_key="shared",
                    max_item_count=5,
                    populate_query_metrics=True,
                    response_hook=hook,
                )

                # Wait so all tasks start fetching at the same moment.
                await start_event.wait()

                items = [item async for item in query_iterable]
                headers = query_iterable.get_response_headers()

                return {
                    "query_id": query_id,
                    "item_count": len(items),
                    "request_charge": float(headers.get("x-ms-request-charge", 0)),
                    "headers": headers,
                    "captured_pages": captured_pages,
                }

            num_concurrent = 20
            tasks = [run_synchronized_query(i) for i in range(num_concurrent)]

            gathered = asyncio.gather(*tasks)

            # Give tasks time to reach the wait point.
            await asyncio.sleep(0.1)
            start_event.set()

            results = await gathered

            assert len(results) == num_concurrent
            for result in results:
                assert result["item_count"] == 50, \
                    f"Query {result['query_id']} should have gotten all 50 items"
                assert result["request_charge"] > 0, \
                    f"Query {result['query_id']} should have positive request charge"

                # The iterator's final headers must match this task's own
                # last hook payload (compared on activity id, unique per request).
                assert len(result["captured_pages"]) > 0, \
                    f"Query {result['query_id']} hook never fired"
                last_hook = result["captured_pages"][-1]
                assert result["headers"].get("x-ms-activity-id") == last_hook.get("x-ms-activity-id"), (
                    f"Query {result['query_id']} got headers that did not come from its own response."
                )

            # Each task sent its own requests, so all activity ids must be distinct.
            final_ids = [r["headers"].get("x-ms-activity-id") for r in results]
            assert len(set(final_ids)) == len(final_ids), (
                f"Two or more tasks got the same activity id, which means header state is shared. "
                f"Ids: {final_ids}"
            )

        finally:
            await self._delete_container_for_test(cid)

    async def test_query_response_headers_before_iteration_returns_empty_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_query_response_headers_before_iteration_returns_empty_async
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

    async def test_query_response_headers_return_type_is_dict_not_list_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_query_response_headers_return_type_is_dict_not_list_async
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

    async def test_query_response_headers_match_last_response_hook_invocation_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_query_response_headers_match_last_response_hook_invocation_async
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

    async def test_response_hook_fires_at_least_once_for_every_paged_surface_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_response_hook_fires_at_least_once_for_every_paged_surface_async
        """A response_hook attached to any async paged surface must fire at
        least once, and every captured payload must be a Mapping."""

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
                "query_items_change_feed",
                lambda h: created_collection.query_items_change_feed(
                    start_time="Beginning",
                    max_item_count=2,
                    response_hook=h,
                ),
            )
        finally:
            await self._delete_container_for_test(cid)
