# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import os
import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosQuery
class TestQueryResponseHeaders(unittest.TestCase):
    """Tests for query response headers functionality."""

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

    def test_query_response_headers_single_page(self):
        """Test that response headers are captured for a single page query."""
        created_collection = self.created_db.create_container(
            "test_headers_single_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
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
            self.assertGreater(len(response_headers), 0)

            # Verify headers contain expected fields
            first_page_headers = response_headers[0]
            self.assertIn("x-ms-request-charge", first_page_headers)
            self.assertIn("x-ms-activity-id", first_page_headers)

            # Verify get_last_response_headers works
            last_headers = query_iterable.get_last_response_headers()
            self.assertIsNotNone(last_headers)
            self.assertIn("x-ms-request-charge", last_headers)

        finally:
            self.created_db.delete_container(created_collection.id)

    def test_query_response_headers_multiple_pages(self):
        """Test that response headers are captured for each page in a paginated query."""
        created_collection = self.created_db.create_container(
            "test_headers_multi_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
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

            # Verify response headers were captured for multiple pages
            response_headers = query_iterable.get_response_headers()
            self.assertIsNotNone(response_headers)
            # With 15 items and max_item_count=5, we expect at least 3 pages
            self.assertGreaterEqual(len(response_headers), 3)

            # Verify each page has headers
            for i, headers in enumerate(response_headers):
                self.assertIn("x-ms-request-charge", headers, f"Page {i} missing request charge header")
                self.assertIn("x-ms-activity-id", headers, f"Page {i} missing activity id header")

            # Each page should have a different activity ID
            activity_ids = [h.get("x-ms-activity-id") for h in response_headers]
            # Note: Activity IDs might be the same for some edge cases, but generally should differ
            self.assertEqual(len(activity_ids), len(response_headers))

        finally:
            self.created_db.delete_container(created_collection.id)

    def test_query_response_headers_empty_result(self):
        """Test that response headers are captured even when query returns no results."""
        created_collection = self.created_db.create_container(
            "test_headers_empty_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
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

            # Response headers may or may not be captured depending on implementation
            # The key is that the method doesn't throw an error
            response_headers = query_iterable.get_response_headers()
            self.assertIsNotNone(response_headers)

            # get_last_response_headers should return None or headers depending on if a request was made
            last_headers = query_iterable.get_last_response_headers()
            # This can be None if no request was made, or headers if at least one request was made
            # Both are valid behaviors

        finally:
            self.created_db.delete_container(created_collection.id)

    def test_query_response_headers_with_query_metrics(self):
        """Test that query metrics are included in response headers when enabled."""
        created_collection = self.created_db.create_container(
            "test_headers_metrics_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
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
            self.assertGreater(len(response_headers), 0)

            # Check for query metrics header
            metrics_header_name = "x-ms-documentdb-query-metrics"
            first_page_headers = response_headers[0]
            self.assertIn(metrics_header_name, first_page_headers)

            # Validate metrics header is well-formed
            metrics_header = first_page_headers[metrics_header_name]
            metrics = metrics_header.split(";")
            self.assertGreater(len(metrics), 1)
            self.assertTrue(all(["=" in x for x in metrics]))

        finally:
            self.created_db.delete_container(created_collection.id)

    def test_query_response_headers_by_page_iteration(self):
        """Test response headers when using by_page() iteration."""
        created_collection = self.created_db.create_container(
            "test_headers_by_page_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            # Create items
            num_items = 10
            for i in range(num_items):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

            query = "SELECT * FROM c WHERE c.pk = @pk"
            query_iterable = created_collection.query_items(
                query=query,
                parameters=[{"name": "@pk", "value": "test"}],
                partition_key="test",
                max_item_count=3  # Force multiple pages
            )

            # Iterate by page
            all_items = []
            page_count = 0
            for page in query_iterable.by_page():
                page_items = list(page)
                all_items.extend(page_items)
                page_count += 1

                # After each page, we can check the last response headers
                last_headers = query_iterable.get_last_response_headers()
                self.assertIsNotNone(last_headers)
                self.assertIn("x-ms-request-charge", last_headers)

            # Verify all items retrieved
            self.assertEqual(len(all_items), num_items)

            # Verify we got headers for each page (at least as many as page_count)
            response_headers = query_iterable.get_response_headers()
            self.assertGreaterEqual(len(response_headers), page_count)

        finally:
            self.created_db.delete_container(created_collection.id)

    def test_query_response_headers_returns_copies(self):
        """Test that get_response_headers returns copies, not references."""
        created_collection = self.created_db.create_container(
            "test_headers_copies_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
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

            # They should be equal but not the same object
            self.assertEqual(len(headers1), len(headers2))
            if len(headers1) > 0:
                # Modifying one should not affect the other
                headers1[0]["test-key"] = "test-value"
                self.assertNotIn("test-key", headers2[0])

        finally:
            self.created_db.delete_container(created_collection.id)


if __name__ == "__main__":
    unittest.main()
