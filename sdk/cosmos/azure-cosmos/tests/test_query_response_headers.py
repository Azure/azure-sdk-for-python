# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import gc
import os
import threading
import tracemalloc
import unittest
import uuid
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from azure.core.utils import CaseInsensitiveDict

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy
from azure.cosmos._cosmos_responses import CosmosItemPaged
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQueryResponseHeaders(unittest.TestCase):
    """Tests for query response headers functionality."""

    created_db: DatabaseProxy = None
    key_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    key_client: cosmos_client.CosmosClient = None
    config = test_config.TestConfig
    host = config.host
    masterKey = config.masterKey
    TEST_DATABASE_ID = config.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        use_multiple_write_locations = False
        if os.environ.get("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER", "False") == "True":
            use_multiple_write_locations = True
        # Key-auth client for control-plane operations (create/delete containers)
        cls.key_client, cls.key_db, cls.client, cls.created_db = (
            test_config.TestConfig.create_test_clients(cls.TEST_DATABASE_ID, multiple_write_locations=use_multiple_write_locations))

    def _create_container_for_test(self, container_id, partition_key, **kwargs):
        """Create container via key-auth setup client (control-plane), return data-plane proxy."""
        # Container creation is a control-plane operation routed through key_client (key-auth).
        self.key_db.create_container(id=container_id, partition_key=partition_key, **kwargs)
        return self.created_db.get_container_client(container_id)

    def _delete_container_for_test(self, container_id):
        """Delete container via key-auth setup client (control-plane)."""
        self.key_db.delete_container(container_id)

    def test_query_response_headers_single_page(self):
        """Test that response headers are captured for a single page query."""
        container_id = "test_headers_single_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            # Create a few items
            for i in range(5):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

            query = "SELECT * FROM c WHERE c.pk = @pk"
            query_iterable = created_collection.query_items(
                query=query,
                parameters=[{"name": "@pk", "value": "test"}],
                partition_key="test"
            )

            # Iterate through items using for loop (pagination)
            items = []
            for item in query_iterable:
                items.append(item)

            # Verify items were returned
            self.assertEqual(len(items), 5)

            # Verify response headers were captured
            response_headers = query_iterable.get_response_headers()
            self.assertIsNotNone(response_headers)

            # Verify headers contain expected fields
            self.assertIn("x-ms-request-charge", response_headers)
            self.assertIn("x-ms-activity-id", response_headers)

        finally:
            self._delete_container_for_test(container_id)

    def test_query_response_headers_multiple_pages(self):
        """Test that response headers reflect the last page in a paginated query."""
        container_id = "test_headers_multi_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            # Create enough items to span multiple pages
            num_items = 15
            for i in range(num_items):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

            query = "SELECT * FROM c WHERE c.pk = @pk"
            # Use small page size to force multiple pages
            query_iterable = created_collection.query_items(
                query=query,
                parameters=[{"name": "@pk", "value": "test"}],
                partition_key="test",
                max_item_count=5  # Force pagination with 5 items per page
            )

            # Iterate through items using for loop (pagination)
            items = []
            for item in query_iterable:
                items.append(item)

            # Verify all items were returned
            self.assertEqual(len(items), num_items)

            # Verify response headers contain the last page's headers
            response_headers = query_iterable.get_response_headers()
            self.assertIsNotNone(response_headers)
            self.assertIn("x-ms-request-charge", response_headers)
            self.assertIn("x-ms-activity-id", response_headers)

        finally:
            self._delete_container_for_test(container_id)

    def test_query_response_headers_empty_result(self):
        """Test that response headers are captured even when query returns no results."""
        container_id = "test_headers_empty_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            # Create an item with different pk
            created_collection.create_item(body={"pk": "other", "id": "item_1"})

            query = "SELECT * FROM c WHERE c.pk = @pk"
            query_iterable = created_collection.query_items(
                query=query,
                parameters=[{"name": "@pk", "value": "nonexistent"}],
                partition_key="nonexistent"
            )

            # Iterate through items (should be empty)
            items = []
            for item in query_iterable:
                items.append(item)

            # Verify no items were returned
            self.assertEqual(len(items), 0)

            # The key is that the method doesn't throw an error
            # and the headers are populated since an HTTP request was made
            response_headers = query_iterable.get_response_headers()
            self.assertIn("x-ms-request-charge", response_headers)

        finally:
            self._delete_container_for_test(container_id)

    def test_query_response_headers_with_query_metrics(self):
        """Test that query metrics are included in response headers when enabled."""
        container_id = "test_headers_metrics_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            # Create items
            for i in range(5):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

            query = "SELECT * FROM c WHERE c.pk = @pk"
            query_iterable = created_collection.query_items(
                query=query,
                parameters=[{"name": "@pk", "value": "test"}],
                partition_key="test",
                populate_query_metrics=True
            )

            # Iterate through items
            items = []
            for item in query_iterable:
                items.append(item)

            self.assertEqual(len(items), 5)

            # Verify response headers contain query metrics
            response_headers = query_iterable.get_response_headers()
            self.assertIsNotNone(response_headers)

            # Check for query metrics header
            metrics_header_name = "x-ms-documentdb-query-metrics"
            self.assertIn(metrics_header_name, response_headers)

            # Validate metrics header is well-formed
            metrics_header = response_headers[metrics_header_name]
            metrics = metrics_header.split(";")
            self.assertGreater(len(metrics), 1)
            self.assertTrue(all("=" in x for x in metrics))

        finally:
            self._delete_container_for_test(container_id)

    def test_query_response_headers_by_page_iteration(self):
        """Test response headers update per page, verified via x-ms-item-count."""
        container_id = "test_headers_by_page_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            # 7 items with max_item_count=3 gives pages of 3, 3, 1
            num_items = 7
            for i in range(num_items):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

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
            for page in query_iterable.by_page():
                page_items = list(page)
                all_items.extend(page_items)

                headers = query_iterable.get_response_headers()
                self.assertIsNotNone(headers)
                self.assertIn("x-ms-item-count", headers)
                item_counts.append(int(headers["x-ms-item-count"]))

            # Verify all items retrieved
            self.assertEqual(len(all_items), num_items)

            # The last page should have fewer items than the page size,
            # proving headers are overwritten per page.
            # max_item_count is a hint, so pages may have fewer items than requested.
            self.assertGreater(len(item_counts), 1)
            self.assertEqual(sum(item_counts), num_items)
            self.assertLess(item_counts[-1], item_counts[0])

        finally:
            self._delete_container_for_test(container_id)

    def test_query_response_headers_long_pagination_bounded_memory(self):
        """Paging through many pages keeps response-header state bounded and
        keeps overall iterator memory growth under a linear safety ceiling.
        Document payloads are not retained during measurement so growth reflects
        headers and iterator overhead only."""
        container_id = "test_headers_long_pagination_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            num_items = 200
            for i in range(num_items):
                created_collection.create_item(
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
            first_page = next(page_iter)
            first_page_count = sum(1 for _ in first_page)
            baseline_headers = query_iterable.get_response_headers()
            self.assertIsNotNone(baseline_headers)

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

                for page in page_iter:
                    # Count items without keeping a reference to any of them.
                    items_total += sum(1 for _ in page)
                    page_count += 1
                    headers = query_iterable.get_response_headers()
                    self.assertIsNotNone(headers)
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
            self.assertGreaterEqual(page_count, 20, f"Expected many pages, got {page_count}.")
            self.assertEqual(items_total, num_items)

            # The per-page headers dict stays close to the first page's size.
            max_header_size = max(header_sizes)
            self.assertLessEqual(
                max_header_size, len(baseline_headers) + 8,
                f"Headers dict grew across pagination (max={max_header_size}, baseline={len(baseline_headers)}).",
            )

            # The set of header names seen across all pages stays bounded.
            self.assertLessEqual(
                len(all_keys_seen), len(baseline_headers) + 16,
                f"Header name set grew across pagination (seen={len(all_keys_seen)}, baseline={len(baseline_headers)}).",
            )

            # Linear safety ceiling so the check scales if num_items changes.
            # This is a "no catastrophic leak" guard, not a strict O(1) proof.
            # Observed per-page overhead on a live account is around 24-29 KiB;
            # 48 KiB gives roughly 2x headroom and still catches a real leak.
            max_per_page_bytes = 48 * 1024
            ceiling_bytes = max_per_page_bytes * page_count
            self.assertLess(
                memory_growth, ceiling_bytes,
                f"Iterator memory grew by {memory_growth} bytes over {page_count} pages; "
                f"exceeded linear safety ceiling {ceiling_bytes} bytes.",
            )

        finally:
            self._delete_container_for_test(container_id)

    def test_query_response_headers_returns_copies(self):
        """Test that get_response_headers returns copies, not references."""
        container_id = "test_headers_copies_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            created_collection.create_item(body={"pk": "test", "id": "item_1"})

            query = "SELECT * FROM c"
            query_iterable = created_collection.query_items(
                query=query,
                partition_key="test"
            )

            # Iterate
            for item in query_iterable:
                pass

            # Get headers twice
            headers1 = query_iterable.get_response_headers()
            headers2 = query_iterable.get_response_headers()

            # They should be distinct objects
            self.assertIsNot(headers1, headers2)

            # Modifying one should not affect the other
            headers1["test-key"] = "test-value"
            self.assertNotIn("test-key", headers2)

        finally:
            self._delete_container_for_test(container_id)

    def test_query_response_headers_thread_safety(self):
        """Each concurrent query must see only its own response headers.
        Each worker installs a response_hook that records every page it
        sees; the iterator's final headers must match that worker's own
        last hook payload."""
        container_id = "test_headers_thread_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            # Different partition keys so different threads run different queries.
            num_partitions = 5
            items_per_partition = 10
            for pk_idx in range(num_partitions):
                for item_idx in range(items_per_partition):
                    created_collection.create_item(
                        body={"pk": f"partition_{pk_idx}", "id": f"item_{pk_idx}_{item_idx}", "value": item_idx}
                    )

            results = {}
            errors = []
            lock = threading.Lock()

            def run_query(partition_key: str, thread_id: int):
                """Run a query and capture its headers."""
                try:
                    # Per-thread hook: records what this iterator received.
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

                    items = list(query_iterable)
                    headers = query_iterable.get_response_headers()

                    with lock:
                        results[thread_id] = {
                            "partition_key": partition_key,
                            "item_count": len(items),
                            "headers": headers,
                            "captured_pages": captured_pages,
                        }
                except Exception as e:
                    with lock:
                        errors.append((thread_id, str(e)))

            num_threads = 10
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for i in range(num_threads):
                    partition_key = f"partition_{i % num_partitions}"
                    futures.append(executor.submit(run_query, partition_key, i))
                for future in as_completed(futures):
                    future.result()

            self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
            self.assertEqual(len(results), num_threads)

            for thread_id, result in results.items():
                self.assertEqual(result["item_count"], items_per_partition,
                    f"Thread {thread_id} got wrong item count")
                self.assertIn("x-ms-request-charge", result["headers"],
                    f"Thread {thread_id} headers missing x-ms-request-charge")

                # The iterator's final headers must match this thread's own
                # last hook payload, otherwise header state is shared.
                self.assertGreater(
                    len(result["captured_pages"]), 0,
                    f"Thread {thread_id} hook never fired",
                )
                last_hook = result["captured_pages"][-1]
                self.assertEqual(
                    result["headers"].get("x-ms-activity-id"),
                    last_hook.get("x-ms-activity-id"),
                    f"Thread {thread_id} got headers that did not come from its own response.",
                )
                self.assertEqual(
                    result["headers"].get("x-ms-request-charge"),
                    last_hook.get("x-ms-request-charge"),
                    f"Thread {thread_id} got a request charge that did not come from its own response.",
                )

            # Each thread holds its own headers dict, not a shared object.
            thread_ids = list(results.keys())
            if len(thread_ids) >= 2:
                self.assertIsNot(results[thread_ids[0]]["headers"],
                    results[thread_ids[1]]["headers"])

            # Different partitions, so activity ids must not all be the same.
            activity_ids = {
                r["headers"].get("x-ms-activity-id") for r in results.values()
            }
            self.assertGreater(
                len(activity_ids), 1,
                "All threads got the same activity id, which means header state is shared.",
            )

        finally:
            self._delete_container_for_test(container_id)

    def test_query_response_headers_concurrent_same_container(self):
        """All threads run the same query against the same partition. Item counts
        and request charges look identical across threads, so isolation is checked
        on x-ms-activity-id, which the service assigns per request."""
        container_id = "test_headers_concurrent_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            for i in range(50):
                created_collection.create_item(body={"pk": "shared", "id": f"item_{i}", "value": i})

            barrier = threading.Barrier(5)
            results = {}
            errors = []
            lock = threading.Lock()

            def run_synchronized_query(thread_id: int):
                """Run a query with synchronization to maximize overlap."""
                try:
                    # Per-thread hook: records what this iterator received.
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

                    # Wait so all threads start fetching at the same moment.
                    barrier.wait()

                    items = list(query_iterable)
                    headers = query_iterable.get_response_headers()

                    with lock:
                        results[thread_id] = {
                            "item_count": len(items),
                            "request_charge": float(headers.get("x-ms-request-charge", 0)),
                            "headers": headers,
                            "captured_pages": captured_pages,
                        }
                except Exception as e:
                    with lock:
                        errors.append((thread_id, str(e)))

            threads = []
            for i in range(5):
                t = threading.Thread(target=run_synchronized_query, args=(i,))
                threads.append(t)
                t.start()
            for t in threads:
                t.join(timeout=60)

            # Surface any worker exceptions in the main thread.
            self.assertEqual(len(errors), 0, f"Worker errors: {errors}")

            self.assertEqual(len(results), 5)
            for thread_id, result in results.items():
                self.assertEqual(result["item_count"], 50,
                    f"Thread {thread_id} should have gotten all 50 items")
                self.assertGreater(result["request_charge"], 0,
                    f"Thread {thread_id} should have positive request charge")

                # The iterator's final headers must match this thread's own
                # last hook payload (compared on activity id, unique per request).
                self.assertGreater(
                    len(result["captured_pages"]), 0,
                    f"Thread {thread_id} hook never fired",
                )
                last_hook = result["captured_pages"][-1]
                self.assertEqual(
                    result["headers"].get("x-ms-activity-id"),
                    last_hook.get("x-ms-activity-id"),
                    f"Thread {thread_id} got headers that did not come from its own response.",
                )

            # Each thread sent its own requests, so all activity ids must be distinct.
            final_ids = [r["headers"].get("x-ms-activity-id") for r in results.values()]
            self.assertEqual(
                len(set(final_ids)), len(final_ids),
                f"Two or more threads got the same activity id, which means header state is shared. "
                f"Ids: {final_ids}",
            )

        finally:
            self._delete_container_for_test(container_id)

    def test_query_response_headers_before_iteration_returns_empty(self):
        """Headers must be an empty dict when no page has been fetched yet."""
        container_id = "test_headers_preiter_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            created_collection.create_item(body={"pk": "test", "id": "item_1"})

            query_iterable = created_collection.query_items(
                query="SELECT * FROM c",
                partition_key="test",
            )

            # No iteration yet, so the dict must be empty (and not None).
            headers = query_iterable.get_response_headers()
            self.assertIsInstance(headers, CaseInsensitiveDict)
            self.assertEqual(len(headers), 0)
        finally:
            self._delete_container_for_test(container_id)

    def test_query_response_headers_match_last_response_hook_invocation(self):
        """The headers returned after iteration must match the headers handed
        to the last response_hook call."""
        container_id = "test_headers_hookparity_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            for i in range(12):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

            captured_pages = []

            def hook(headers, _result):
                # Snapshot the headers handed to the hook for every page.
                captured_pages.append(dict(headers))

            query_iterable = created_collection.query_items(
                query="SELECT * FROM c WHERE c.pk = @pk",
                parameters=[{"name": "@pk", "value": "test"}],
                partition_key="test",
                max_item_count=4,
                response_hook=hook,
            )

            items = list(query_iterable)
            self.assertEqual(len(items), 12)

            # At least one page was fetched, so the hook fired at least once.
            self.assertGreater(len(captured_pages), 0)

            # The getter must return what the last hook invocation saw.
            final_headers = query_iterable.get_response_headers()
            self.assertEqual(
                final_headers["x-ms-request-charge"],
                captured_pages[-1]["x-ms-request-charge"],
            )
            self.assertEqual(
                final_headers["x-ms-activity-id"],
                captured_pages[-1]["x-ms-activity-id"],
            )
        finally:
            self._delete_container_for_test(container_id)

    def test_query_response_headers_return_type_is_dict_not_list(self):
        """The getter returns a single dict (not a list), and the old
        get_last_response_headers method is not available."""
        container_id = "test_headers_returntype_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            created_collection.create_item(body={"pk": "test", "id": "item_1"})

            query_iterable = created_collection.query_items(
                query="SELECT * FROM c",
                partition_key="test",
            )
            self.assertIsInstance(query_iterable, CosmosItemPaged)

            list(query_iterable)
            headers = query_iterable.get_response_headers()

            self.assertIsInstance(headers, CaseInsensitiveDict)
            self.assertNotIsInstance(headers, list)
            self.assertFalse(hasattr(query_iterable, "get_last_response_headers"))
        finally:
            self._delete_container_for_test(container_id)

    def test_read_all_items_response_headers(self):
        """read_all_items pagers expose the same headers contract as queries."""
        container_id = "test_headers_readall_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            for i in range(8):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            paged = created_collection.read_all_items(max_item_count=3)
            items = list(paged)
            self.assertEqual(len(items), 8)

            self.assertTrue(
                hasattr(paged, "get_response_headers"),
                "read_all_items pager must expose get_response_headers",
            )
            headers = paged.get_response_headers()
            self.assertIsInstance(headers, CaseInsensitiveDict)
            self.assertIn("x-ms-request-charge", headers)
        finally:
            self._delete_container_for_test(container_id)


    def test_response_hook_parity_query_items_change_feed(self):
        """Headers handed to the response_hook on query_items_change_feed
        must match the pager's get_response_headers() when the pager
        exposes one (some change-feed pager flavors don't)."""
        container_id = "test_hookparity_cf_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            for i in range(6):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            captured = []

            def hook(headers, _result):
                captured.append(dict(headers))

            paged = created_collection.query_items_change_feed(
                start_time="Beginning",
                max_item_count=2,
                response_hook=hook,
            )
            items = list(paged)
            self.assertGreaterEqual(len(items), 6)
            self.assertGreater(len(captured), 0, "response_hook must fire at least once")

            # change_feed pages always carry a request charge in the hook payload
            self.assertIn("x-ms-request-charge", captured[-1])

            # When the change-feed pager exposes get_response_headers(),
            # the last page's headers must match the last hook invocation.
            if hasattr(paged, "get_response_headers"):
                final_headers = paged.get_response_headers()
                self.assertIn("x-ms-request-charge", final_headers)
                self.assertEqual(
                    final_headers["x-ms-request-charge"],
                    captured[-1]["x-ms-request-charge"],
                )
        finally:
            self._delete_container_for_test(container_id)

    def test_response_hook_parity_point_ops(self):
        """For every point CRUD method, the headers handed to the
        response_hook must match the returned wrapper's
        get_response_headers(). delete_item returns no body."""
        container_id = "test_hookparity_point_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            # create_item
            captured.clear()
            created = created_collection.create_item(
                body={"pk": "p", "id": "doc1", "value": 1},
                response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            self.assertEqual(
                created.get_response_headers()["x-ms-request-charge"],
                captured[0]["x-ms-request-charge"],
            )

            # read_item
            captured.clear()
            read = created_collection.read_item(
                item="doc1", partition_key="p", response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            self.assertEqual(
                read.get_response_headers()["x-ms-request-charge"],
                captured[0]["x-ms-request-charge"],
            )

            # replace_item
            captured.clear()
            replaced = created_collection.replace_item(
                item="doc1",
                body={"pk": "p", "id": "doc1", "value": 2},
                response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            self.assertEqual(
                replaced.get_response_headers()["x-ms-request-charge"],
                captured[0]["x-ms-request-charge"],
            )

            # upsert_item
            captured.clear()
            upserted = created_collection.upsert_item(
                body={"pk": "p", "id": "doc1", "value": 3},
                response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            self.assertEqual(
                upserted.get_response_headers()["x-ms-request-charge"],
                captured[0]["x-ms-request-charge"],
            )

            # delete_item: returns None, but the hook still fires once with
            # the response headers from the DELETE round-trip.
            captured.clear()
            created_collection.delete_item(
                item="doc1", partition_key="p", response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            self.assertIn("x-ms-request-charge", captured[0])
        finally:
            self._delete_container_for_test(container_id)

    def test_response_hook_parity_query_databases_and_query_containers(self):
        """query_databases and query_containers fire their response_hook
        exactly once after the iterable is returned (the hook fires before
        the caller actually walks the iterable). ``query_databases`` passes
        a one-arg hook (just headers); ``query_containers`` passes two args
        (headers, paged-iterable). Accept both via ``*args``.

        We pin: the hook fires exactly once for each surface, and the
        captured payload is a Mapping. We deliberately do *not* pin a
        specific header like ``x-ms-request-charge`` because the hook
        fires with ``client_connection.last_response_headers`` at the
        moment the pager is constructed, which can be a stale value from
        an earlier request (e.g. the account probe) when nothing has yet
        flowed through this specific query."""

        captured_db = []

        def hook_db(*args):
            # query_databases: hook(headers); query_containers: hook(headers, paged)
            captured_db.append(args[0])

        db_pager = self.client.query_databases(
            query="SELECT * FROM root r",
            response_hook=hook_db,
        )
        _ = list(db_pager)
        self.assertEqual(
            len(captured_db), 1,
            "query_databases response_hook must fire exactly once",
        )
        self.assertIsInstance(captured_db[0], Mapping)

        captured_c = []

        def hook_c(*args):
            captured_c.append(args[0])

        c_pager = self.created_db.query_containers(
            query="SELECT * FROM root r",
            response_hook=hook_c,
        )
        _ = list(c_pager)
        self.assertEqual(
            len(captured_c), 1,
            "query_containers response_hook must fire exactly once",
        )
        self.assertIsInstance(captured_c[0], Mapping)

    def test_response_hook_fires_at_least_once_for_every_paged_surface(self):
        """A response_hook attached to any paged surface must fire at least
        once, and every captured payload must be a Mapping."""

        container_id = "test_hookfires_paged_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            for i in range(6):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            def _run(surface_name, build_pager):
                captured = []

                def hook(headers, _result):
                    captured.append(dict(headers))

                pager = build_pager(hook)
                list(pager)
                self.assertGreater(
                    len(captured),
                    0,
                    f"{surface_name} response_hook never fired",
                )
                for payload in captured:
                    self.assertIsInstance(
                        payload,
                        Mapping,
                        f"{surface_name} hook received non-Mapping payload",
                    )

            _run(
                "query_items",
                lambda h: created_collection.query_items(
                    query="SELECT * FROM c",
                    partition_key="test",
                    response_hook=h,
                ),
            )
            _run(
                "query_items_change_feed",
                lambda h: created_collection.query_items_change_feed(
                    start_time="Beginning",
                    max_item_count=2,
                    response_hook=h,
                ),
            )
        finally:
            self._delete_container_for_test(container_id)


    def test_response_hook_parity_patch_item(self):
        # patch_item must fire its response_hook once with headers that
        # match the returned wrapper on request charge and activity id.
        container_id = "test_hookparity_patch_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(
            container_id, PartitionKey(path="/pk")
        )
        try:
            created_collection.create_item(
                body={"pk": "p", "id": "doc-patch", "value": 1}
            )

            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            patched = created_collection.patch_item(
                item="doc-patch",
                partition_key="p",
                patch_operations=[
                    {"op": "replace", "path": "/value", "value": 99}
                ],
                response_hook=hook,
            )

            self.assertEqual(len(captured), 1)
            patched_headers = patched.get_response_headers()
            self.assertEqual(
                patched_headers["x-ms-request-charge"],
                captured[0]["x-ms-request-charge"],
            )
            self.assertEqual(
                patched_headers["x-ms-activity-id"],
                captured[0]["x-ms-activity-id"],
            )
            self.assertEqual(patched["value"], 99)
        finally:
            self._delete_container_for_test(container_id)

    def test_response_hook_parity_execute_item_batch(self):
        # execute_item_batch must fire its response_hook once with
        # headers that match the returned wrapper.
        container_id = "test_hookparity_batch_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(
            container_id, PartitionKey(path="/pk")
        )
        try:
            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            batch_ops = [
                ("create", ({"pk": "p", "id": "batch-doc-1", "value": 1},)),
                ("upsert", ({"pk": "p", "id": "batch-doc-2", "value": 2},)),
            ]

            result = created_collection.execute_item_batch(
                batch_operations=batch_ops,
                partition_key="p",
                response_hook=hook,
            )

            self.assertEqual(len(captured), 1)
            result_headers = result.get_response_headers()
            self.assertEqual(
                result_headers["x-ms-request-charge"],
                captured[0]["x-ms-request-charge"],
            )
            self.assertEqual(
                result_headers["x-ms-activity-id"],
                captured[0]["x-ms-activity-id"],
            )
            self.assertEqual(len(result), 2)
        finally:
            self._delete_container_for_test(container_id)


if __name__ == "__main__":
    unittest.main()
