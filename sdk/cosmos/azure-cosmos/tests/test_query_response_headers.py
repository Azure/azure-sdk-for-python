# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import os
import threading
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy
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
        """Test that response headers are captured correctly when multiple queries run concurrently.
        
        This test verifies that each query operation captures its own headers independently,
        without interference from concurrent queries. This is the key thread-safety guarantee.
        """
        container_id = "test_headers_thread_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            # Create items with different partition keys to ensure different queries
            num_partitions = 5
            items_per_partition = 10
            for pk_idx in range(num_partitions):
                for item_idx in range(items_per_partition):
                    created_collection.create_item(
                        body={"pk": f"partition_{pk_idx}", "id": f"item_{pk_idx}_{item_idx}", "value": item_idx}
                    )

            # Results storage - each thread will store its query results here
            results = {}
            errors = []
            lock = threading.Lock()

            def run_query(partition_key: str, thread_id: int):
                """Run a query and capture its headers."""
                try:
                    query = "SELECT * FROM c WHERE c.pk = @pk"
                    query_iterable = created_collection.query_items(
                        query=query,
                        parameters=[{"name": "@pk", "value": partition_key}],
                        partition_key=partition_key,
                        max_item_count=2,  # Small page size to ensure multiple pages
                        populate_query_metrics=True
                    )

                    # Consume all items
                    items = list(query_iterable)
                    headers = query_iterable.get_response_headers()

                    with lock:
                        results[thread_id] = {
                            "partition_key": partition_key,
                            "item_count": len(items),
                            "headers": headers
                        }
                except Exception as e:
                    with lock:
                        errors.append((thread_id, str(e)))

            # Run multiple queries concurrently
            num_threads = 10
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for i in range(num_threads):
                    partition_key = f"partition_{i % num_partitions}"
                    futures.append(executor.submit(run_query, partition_key, i))
                
                # Wait for all to complete
                for future in as_completed(futures):
                    future.result()  # This will raise if the thread raised

            # Verify no errors occurred
            self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")

            # Verify all threads got results
            self.assertEqual(len(results), num_threads)

            # Verify each thread captured headers correctly
            for thread_id, result in results.items():
                self.assertEqual(result["item_count"], items_per_partition,
                    f"Thread {thread_id} got wrong item count")
                self.assertIn("x-ms-request-charge", result["headers"],
                    f"Thread {thread_id} headers missing x-ms-request-charge")

            # Verify that different threads have independent header dicts
            thread_ids = list(results.keys())
            if len(thread_ids) >= 2:
                self.assertIsNot(results[thread_ids[0]]["headers"],
                    results[thread_ids[1]]["headers"])

        finally:
            self._delete_container_for_test(container_id)

    def test_query_response_headers_concurrent_same_container(self):
        """Test concurrent queries on the same container with overlapping execution.
        
        This test specifically targets the race condition that would occur if headers
        were captured from a shared client.last_response_headers after fetch_next_block().
        """
        container_id = "test_headers_concurrent_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            # Create enough items to ensure multiple pages
            for i in range(50):
                created_collection.create_item(body={"pk": "shared", "id": f"item_{i}", "value": i})

            barrier = threading.Barrier(5)  # Synchronize 5 threads
            results = {}
            lock = threading.Lock()

            def run_synchronized_query(thread_id: int):
                """Run a query with synchronization to maximize overlap."""
                query_iterable = created_collection.query_items(
                    query="SELECT * FROM c WHERE c.pk = @pk",
                    parameters=[{"name": "@pk", "value": "shared"}],
                    partition_key="shared",
                    max_item_count=5,  # Small pages = more fetches
                    populate_query_metrics=True
                )

                # Wait for all threads to be ready
                barrier.wait()

                # Now all threads fetch concurrently
                items = list(query_iterable)
                headers = query_iterable.get_response_headers()

                with lock:
                    results[thread_id] = {
                        "item_count": len(items),
                        "request_charge": float(headers.get("x-ms-request-charge", 0))
                    }

            threads = []
            for i in range(5):
                t = threading.Thread(target=run_synchronized_query, args=(i,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join(timeout=60)

            # Verify all threads completed and got correct results
            self.assertEqual(len(results), 5)
            for thread_id, result in results.items():
                self.assertEqual(result["item_count"], 50,
                    f"Thread {thread_id} should have gotten all 50 items")
                self.assertGreater(result["request_charge"], 0,
                    f"Thread {thread_id} should have positive request charge")

        finally:
            self._delete_container_for_test(container_id)


if __name__ == "__main__":
    unittest.main()
