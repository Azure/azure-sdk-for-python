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
class TestChangeFeedResponseHeaders(unittest.TestCase):
    """Tests for change feed response headers functionality.

    These tests verify that ``query_items_change_feed()`` returns a
    ``CosmosItemPaged`` exposing thread-safe ``get_response_headers()`` and
    ``get_last_response_headers()`` methods, mirroring the contract added to
    ``query_items()``. The captured ``etag`` header on the last page is the
    continuation token customers should use to checkpoint their change feed
    progress.
    """

    created_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    config = test_config.TestConfig
    host = config.host
    masterKey = config.masterKey
    TEST_DATABASE_ID = config.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        use_multiple_write_locations = False
        if os.environ.get("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER", "False") == "True":
            use_multiple_write_locations = True
        cls.client = cosmos_client.CosmosClient(
            cls.host, cls.masterKey, multiple_write_locations=use_multiple_write_locations
        )
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)

    def test_change_feed_response_headers_single_page(self):
        """Test that response headers are captured for a single-page change feed read."""
        created_collection = self.created_db.create_container(
            "test_cf_headers_single_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            for i in range(5):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

            change_feed = created_collection.query_items_change_feed(
                start_time="Beginning",
                partition_key="test",
            )

            items = list(change_feed)
            self.assertEqual(len(items), 5)

            # Verify response headers were captured
            response_headers = change_feed.get_response_headers()
            self.assertIsNotNone(response_headers)
            self.assertGreater(len(response_headers), 0)

            # Verify headers contain expected fields, including the etag continuation token
            first_page_headers = response_headers[0]
            self.assertIn("x-ms-request-charge", first_page_headers)
            self.assertIn("x-ms-activity-id", first_page_headers)
            self.assertIn("etag", first_page_headers)

            # Verify get_last_response_headers works and exposes the etag
            last_headers = change_feed.get_last_response_headers()
            self.assertIsNotNone(last_headers)
            self.assertIn("etag", last_headers)
            self.assertTrue(last_headers["etag"])

        finally:
            self.created_db.delete_container(created_collection.id)

    def test_change_feed_response_headers_multiple_pages(self):
        """Test that response headers are captured for each page in a paginated change feed read."""
        created_collection = self.created_db.create_container(
            "test_cf_headers_multi_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            num_items = 15
            for i in range(num_items):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

            change_feed = created_collection.query_items_change_feed(
                start_time="Beginning",
                partition_key="test",
                max_item_count=5,
            )

            items = list(change_feed)
            self.assertEqual(len(items), num_items)

            response_headers = change_feed.get_response_headers()
            self.assertIsNotNone(response_headers)
            # With 15 items and max_item_count=5, we expect at least 3 pages
            self.assertGreaterEqual(len(response_headers), 3)

            for i, headers in enumerate(response_headers):
                self.assertIn("x-ms-request-charge", headers, f"Page {i} missing request charge header")
                self.assertIn("x-ms-activity-id", headers, f"Page {i} missing activity id header")
                self.assertIn("etag", headers, f"Page {i} missing etag continuation header")

        finally:
            self.created_db.delete_container(created_collection.id)

    def test_change_feed_response_headers_empty_result(self):
        """Test that response headers are exposed safely when the change feed has no new items."""
        created_collection = self.created_db.create_container(
            "test_cf_headers_empty_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            change_feed = created_collection.query_items_change_feed(
                start_time="Now",
                partition_key="test",
            )

            items = list(change_feed)
            self.assertEqual(len(items), 0)

            # The methods must not raise; they may return an empty list or a list with at least
            # one entry depending on whether the implementation made a request.
            response_headers = change_feed.get_response_headers()
            self.assertIsNotNone(response_headers)

            last_headers = change_feed.get_last_response_headers()
            # Either None (no request made) or a CaseInsensitiveDict — both are valid here.
            if last_headers is not None:
                self.assertTrue(hasattr(last_headers, "get"))

        finally:
            self.created_db.delete_container(created_collection.id)

    def test_change_feed_etag_as_checkpoint(self):
        """Verify the etag captured via get_last_response_headers can be used as a checkpoint.

        This is the user-facing scenario raised on PR #45166: customers want to read the
        continuation token (etag) without reaching into ``client_connection.last_response_headers``,
        which is not thread-safe.
        """
        created_collection = self.created_db.create_container(
            "test_cf_headers_etag_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            for i in range(3):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            first_pass = created_collection.query_items_change_feed(
                start_time="Beginning",
                partition_key="test",
            )
            first_items = list(first_pass)
            self.assertEqual(len(first_items), 3)

            checkpoint = first_pass.get_last_response_headers()["etag"]
            self.assertIsNotNone(checkpoint)
            self.assertTrue(checkpoint)

            # Add more items
            for i in range(3, 6):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            second_pass = created_collection.query_items_change_feed(
                continuation=checkpoint,
                partition_key="test",
            )
            second_items = list(second_pass)
            new_ids = {item["id"] for item in second_items}
            self.assertTrue({"item_3", "item_4", "item_5"}.issubset(new_ids))

        finally:
            self.created_db.delete_container(created_collection.id)

    def test_change_feed_response_headers_by_page_iteration(self):
        """Test response headers when using by_page() iteration on a change feed."""
        created_collection = self.created_db.create_container(
            "test_cf_headers_by_page_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            num_items = 10
            for i in range(num_items):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            change_feed = created_collection.query_items_change_feed(
                start_time="Beginning",
                partition_key="test",
                max_item_count=3,
            )

            all_items = []
            page_count = 0
            for page in change_feed.by_page():
                page_items = list(page)
                all_items.extend(page_items)
                page_count += 1

                last_headers = change_feed.get_last_response_headers()
                self.assertIsNotNone(last_headers)
                self.assertIn("etag", last_headers)

            self.assertEqual(len(all_items), num_items)

            response_headers = change_feed.get_response_headers()
            self.assertGreaterEqual(len(response_headers), page_count)

        finally:
            self.created_db.delete_container(created_collection.id)

    def test_change_feed_response_headers_returns_copies(self):
        """Test that get_response_headers returns copies, not references."""
        created_collection = self.created_db.create_container(
            "test_cf_headers_copies_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            created_collection.create_item(body={"pk": "test", "id": "item_1"})

            change_feed = created_collection.query_items_change_feed(
                start_time="Beginning",
                partition_key="test",
            )

            for _ in change_feed:
                pass

            headers1 = change_feed.get_response_headers()
            headers2 = change_feed.get_response_headers()

            self.assertEqual(len(headers1), len(headers2))
            if len(headers1) > 0:
                headers1[0]["test-key"] = "test-value"
                self.assertNotIn("test-key", headers2[0])

        finally:
            self.created_db.delete_container(created_collection.id)

    def test_change_feed_response_headers_thread_safety(self):
        """Test that response headers are captured correctly when multiple change feed reads run concurrently."""
        created_collection = self.created_db.create_container(
            "test_cf_headers_thread_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            num_partitions = 5
            items_per_partition = 10
            for pk_idx in range(num_partitions):
                for item_idx in range(items_per_partition):
                    created_collection.create_item(
                        body={"pk": f"partition_{pk_idx}", "id": f"item_{pk_idx}_{item_idx}"}
                    )

            results = {}
            errors = []
            lock = threading.Lock()

            def run_change_feed(partition_key: str, thread_id: int):
                try:
                    change_feed = created_collection.query_items_change_feed(
                        start_time="Beginning",
                        partition_key=partition_key,
                        max_item_count=2,
                    )
                    items = list(change_feed)
                    headers = change_feed.get_response_headers()

                    with lock:
                        results[thread_id] = {
                            "partition_key": partition_key,
                            "item_count": len(items),
                            "header_count": len(headers),
                            "headers": headers,
                        }
                except Exception as e:
                    with lock:
                        errors.append((thread_id, str(e)))

            num_threads = 10
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for i in range(num_threads):
                    partition_key = f"partition_{i % num_partitions}"
                    futures.append(executor.submit(run_change_feed, partition_key, i))

                for future in as_completed(futures):
                    future.result()

            self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
            self.assertEqual(len(results), num_threads)

            for thread_id, result in results.items():
                self.assertEqual(
                    result["item_count"],
                    items_per_partition,
                    f"Thread {thread_id} got wrong item count",
                )
                self.assertGreater(
                    result["header_count"], 0, f"Thread {thread_id} should have captured headers"
                )
                for header_dict in result["headers"]:
                    self.assertIn(
                        "x-ms-request-charge",
                        header_dict,
                        f"Thread {thread_id} headers missing x-ms-request-charge",
                    )

            if len(results) >= 2:
                thread_ids = list(results.keys())
                headers_0 = results[thread_ids[0]]["headers"]
                headers_1 = results[thread_ids[1]]["headers"]

                self.assertIsNot(headers_0, headers_1)
                if len(headers_0) > 0 and len(headers_1) > 0:
                    self.assertIsNot(headers_0[0], headers_1[0])

        finally:
            self.created_db.delete_container(created_collection.id)

    def test_change_feed_response_headers_concurrent_same_container(self):
        """Test concurrent change feed reads on the same container with overlapping execution.

        This test specifically targets the race condition that would occur if headers were captured
        from the shared client.last_response_headers after each fetch_next_block().
        """
        created_collection = self.created_db.create_container(
            "test_cf_headers_concurrent_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            for i in range(50):
                created_collection.create_item(body={"pk": "shared", "id": f"item_{i}"})

            barrier = threading.Barrier(5)
            results = {}
            lock = threading.Lock()

            def run_synchronized_change_feed(thread_id: int):
                change_feed = created_collection.query_items_change_feed(
                    start_time="Beginning",
                    partition_key="shared",
                    max_item_count=5,
                )

                barrier.wait()

                items = list(change_feed)
                headers = change_feed.get_response_headers()

                with lock:
                    results[thread_id] = {
                        "item_count": len(items),
                        "header_count": len(headers),
                        "request_charges": [
                            float(h.get("x-ms-request-charge", 0)) for h in headers
                        ],
                    }

            threads = []
            for i in range(5):
                t = threading.Thread(target=run_synchronized_change_feed, args=(i,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join(timeout=60)

            self.assertEqual(len(results), 5)
            for thread_id, result in results.items():
                self.assertEqual(
                    result["item_count"], 50, f"Thread {thread_id} should have gotten all 50 items"
                )
                self.assertGreater(
                    result["header_count"], 0, f"Thread {thread_id} should have captured headers"
                )
                for charge in result["request_charges"]:
                    self.assertGreater(
                        charge, 0, f"Thread {thread_id} should have positive request charges"
                    )

        finally:
            self.created_db.delete_container(created_collection.id)


if __name__ == "__main__":
    unittest.main()
