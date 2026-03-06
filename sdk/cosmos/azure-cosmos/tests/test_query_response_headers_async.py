# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
import os
import unittest
import uuid

import pytest

import test_config
from azure.cosmos.aio import CosmosClient, DatabaseProxy
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosQuery
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
        self.client = CosmosClient(
            self.host, self.masterKey, multiple_write_locations=self.use_multiple_write_locations
        )
        await self.client.__aenter__()
        self.created_db = self.client.get_database_client(self.TEST_DATABASE_ID)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_query_response_headers_single_page_async(self):
        """Test that response headers are captured for a single page query."""
        created_collection = await self.created_db.create_container(
            "test_headers_single_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
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
            assert len(response_headers) > 0

            # Verify headers contain expected fields
            first_page_headers = response_headers[0]
            assert "x-ms-request-charge" in first_page_headers
            assert "x-ms-activity-id" in first_page_headers

            # Verify get_last_response_headers works
            last_headers = query_iterable.get_last_response_headers()
            assert last_headers is not None
            assert "x-ms-request-charge" in last_headers

            # Verify that the last headers match the first page in response_headers
            # (since this is a single page query, they should be the same)
            assert last_headers.get("x-ms-activity-id") == first_page_headers.get("x-ms-activity-id")
            assert last_headers.get("x-ms-request-charge") == first_page_headers.get("x-ms-request-charge")

        finally:
            await self.created_db.delete_container(created_collection.id)

    async def test_query_response_headers_multiple_pages_async(self):
        """Test that response headers are captured for each page in a paginated query."""
        created_collection = await self.created_db.create_container(
            "test_headers_multi_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
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

            # Verify response headers were captured for multiple pages
            response_headers = query_iterable.get_response_headers()
            assert response_headers is not None
            # With 15 items and max_item_count=5, we expect at least 3 pages
            assert len(response_headers) >= 3

            # Verify each page has headers
            for i, headers in enumerate(response_headers):
                assert "x-ms-request-charge" in headers, f"Page {i} missing request charge header"
                assert "x-ms-activity-id" in headers, f"Page {i} missing activity id header"

            # Each page should have activity IDs
            activity_ids = [h.get("x-ms-activity-id") for h in response_headers]
            assert len(activity_ids) == len(response_headers)

        finally:
            await self.created_db.delete_container(created_collection.id)

    async def test_query_response_headers_empty_result_async(self):
        """Test that response headers are captured even when query returns no results."""
        created_collection = await self.created_db.create_container(
            "test_headers_empty_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
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

            # Response headers may or may not be captured depending on implementation
            # The key is that the method doesn't throw an error
            response_headers = query_iterable.get_response_headers()
            assert response_headers is not None

            # get_last_response_headers should return None or headers depending on if a request was made
            last_headers = query_iterable.get_last_response_headers()
            # This can be None if no request was made, or headers if at least one request was made

        finally:
            await self.created_db.delete_container(created_collection.id)

    async def test_query_response_headers_with_query_metrics_async(self):
        """Test that query metrics are included in response headers when enabled."""
        created_collection = await self.created_db.create_container(
            "test_headers_metrics_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
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
            assert len(response_headers) > 0

            # Check for query metrics header
            metrics_header_name = "x-ms-documentdb-query-metrics"
            first_page_headers = response_headers[0]
            assert metrics_header_name in first_page_headers

            # Validate metrics header is well-formed
            metrics_header = first_page_headers[metrics_header_name]
            metrics = metrics_header.split(";")
            assert len(metrics) > 1
            assert all("=" in x for x in metrics)

        finally:
            await self.created_db.delete_container(created_collection.id)

    async def test_query_response_headers_by_page_iteration_async(self):
        """Test response headers when using by_page() iteration."""
        created_collection = await self.created_db.create_container(
            "test_headers_by_page_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            # Create items
            num_items = 10
            for i in range(num_items):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})

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
            async for page in query_iterable.by_page():
                page_items = [item async for item in page]
                all_items.extend(page_items)
                page_count += 1

                # After each page, we can check the last response headers
                last_headers = query_iterable.get_last_response_headers()
                assert last_headers is not None
                assert "x-ms-request-charge" in last_headers

            # Verify all items retrieved
            assert len(all_items) == num_items

            # Verify we got headers for each page (at least as many as page_count)
            response_headers = query_iterable.get_response_headers()
            assert len(response_headers) >= page_count

        finally:
            await self.created_db.delete_container(created_collection.id)

    async def test_query_response_headers_returns_copies_async(self):
        """Test that get_response_headers returns copies, not references."""
        created_collection = await self.created_db.create_container(
            "test_headers_copies_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
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

            # They should be equal but not the same object
            assert len(headers1) == len(headers2)
            if len(headers1) > 0:
                # Modifying one should not affect the other
                headers1[0]["test-key"] = "test-value"
                assert "test-key" not in headers2[0]

        finally:
            await self.created_db.delete_container(created_collection.id)

    async def test_query_response_headers_concurrent_async(self):
        """Test that response headers are captured correctly when multiple async queries run concurrently.
        
        This test verifies that each query operation captures its own headers independently,
        without interference from concurrent queries. This is the key thread-safety guarantee.
        """
        created_collection = await self.created_db.create_container(
            "test_headers_concurrent_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
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
                    "header_count": len(headers),
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
                assert result["header_count"] > 0, \
                    f"Query {result['query_id']} should have captured headers"
                
                # Verify headers contain expected keys
                for header_dict in result["headers"]:
                    assert "x-ms-request-charge" in header_dict, \
                        f"Query {result['query_id']} headers missing x-ms-request-charge"

            # Verify that different queries have independent header lists
            if len(results) >= 2:
                headers_0 = results[0]["headers"]
                headers_1 = results[1]["headers"]
                
                # They should be different objects
                assert headers_0 is not headers_1
                if len(headers_0) > 0 and len(headers_1) > 0:
                    assert headers_0[0] is not headers_1[0]

        finally:
            await self.created_db.delete_container(created_collection.id)

    async def test_query_response_headers_high_concurrency_async(self):
        """Test with high concurrency to stress-test the thread-safety.
        
        This test specifically targets the race condition that would occur if headers
        were captured from a shared client.last_response_headers after fetch operations.
        """
        created_collection = await self.created_db.create_container(
            "test_headers_stress_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
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
                    "header_count": len(headers),
                    "request_charges": [
                        float(h.get("x-ms-request-charge", 0)) for h in headers
                    ]
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
                assert result["header_count"] > 0, \
                    f"Query {result['query_id']} should have captured headers"
                # Each request should have a positive request charge
                for charge in result["request_charges"]:
                    assert charge > 0, \
                        f"Query {result['query_id']} should have positive request charges"

        finally:
            await self.created_db.delete_container(created_collection.id)


if __name__ == "__main__":
    unittest.main()
