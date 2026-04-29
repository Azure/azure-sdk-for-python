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
class TestChangeFeedResponseHeadersAsync(unittest.IsolatedAsyncioTestCase):
    """Tests for async change feed response headers functionality.

    Verifies that ``query_items_change_feed()`` on the async client returns a
    ``CosmosAsyncItemPaged`` exposing thread-safe ``get_response_headers()`` and
    ``get_last_response_headers()`` methods, and that the ``etag`` header on the
    last page can be used as a checkpoint without reaching into private state.
    """

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

    async def test_change_feed_response_headers_single_page_async(self):
        """Test that response headers are captured for a single-page change feed read."""
        created_collection = await self.created_db.create_container(
            "test_cf_headers_single_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            for i in range(5):
                await created_collection.create_item(
                    body={"pk": "test", "id": f"item_{i}", "value": i}
                )

            change_feed = created_collection.query_items_change_feed(
                start_time="Beginning",
                partition_key="test",
            )

            items = [item async for item in change_feed]
            self.assertEqual(len(items), 5)

            response_headers = change_feed.get_response_headers()
            self.assertIsNotNone(response_headers)
            self.assertGreater(len(response_headers), 0)

            first_page_headers = response_headers[0]
            self.assertIn("x-ms-request-charge", first_page_headers)
            self.assertIn("x-ms-activity-id", first_page_headers)
            self.assertIn("etag", first_page_headers)

            last_headers = change_feed.get_last_response_headers()
            self.assertIsNotNone(last_headers)
            self.assertIn("etag", last_headers)
            self.assertTrue(last_headers["etag"])

        finally:
            await self.created_db.delete_container(created_collection.id)

    async def test_change_feed_response_headers_multiple_pages_async(self):
        """Test that response headers are captured for each page in a paginated change feed read."""
        created_collection = await self.created_db.create_container(
            "test_cf_headers_multi_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            num_items = 15
            for i in range(num_items):
                await created_collection.create_item(
                    body={"pk": "test", "id": f"item_{i}", "value": i}
                )

            change_feed = created_collection.query_items_change_feed(
                start_time="Beginning",
                partition_key="test",
                max_item_count=5,
            )

            items = [item async for item in change_feed]
            self.assertEqual(len(items), num_items)

            response_headers = change_feed.get_response_headers()
            self.assertIsNotNone(response_headers)
            self.assertGreaterEqual(len(response_headers), 3)

            for i, headers in enumerate(response_headers):
                self.assertIn("x-ms-request-charge", headers, f"Page {i} missing request charge header")
                self.assertIn("x-ms-activity-id", headers, f"Page {i} missing activity id header")
                self.assertIn("etag", headers, f"Page {i} missing etag continuation header")

        finally:
            await self.created_db.delete_container(created_collection.id)

    async def test_change_feed_response_headers_empty_result_async(self):
        """Test that response headers are exposed safely when the change feed has no new items."""
        created_collection = await self.created_db.create_container(
            "test_cf_headers_empty_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            change_feed = created_collection.query_items_change_feed(
                start_time="Now",
                partition_key="test",
            )

            items = [item async for item in change_feed]
            self.assertEqual(len(items), 0)

            response_headers = change_feed.get_response_headers()
            self.assertIsNotNone(response_headers)

            last_headers = change_feed.get_last_response_headers()
            if last_headers is not None:
                self.assertTrue(hasattr(last_headers, "get"))

        finally:
            await self.created_db.delete_container(created_collection.id)

    async def test_change_feed_etag_as_checkpoint_async(self):
        """Verify the etag captured via get_last_response_headers can be used as a checkpoint."""
        created_collection = await self.created_db.create_container(
            "test_cf_headers_etag_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            for i in range(3):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            first_pass = created_collection.query_items_change_feed(
                start_time="Beginning",
                partition_key="test",
            )
            first_items = [item async for item in first_pass]
            self.assertEqual(len(first_items), 3)

            checkpoint = first_pass.get_last_response_headers()["etag"]
            self.assertIsNotNone(checkpoint)
            self.assertTrue(checkpoint)

            for i in range(3, 6):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            second_pass = created_collection.query_items_change_feed(
                continuation=checkpoint,
                partition_key="test",
            )
            second_items = [item async for item in second_pass]
            new_ids = {item["id"] for item in second_items}
            self.assertTrue({"item_3", "item_4", "item_5"}.issubset(new_ids))

        finally:
            await self.created_db.delete_container(created_collection.id)

    async def test_change_feed_response_headers_by_page_iteration_async(self):
        """Test response headers when using by_page() iteration on a change feed."""
        created_collection = await self.created_db.create_container(
            "test_cf_headers_by_page_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            num_items = 10
            for i in range(num_items):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            change_feed = created_collection.query_items_change_feed(
                start_time="Beginning",
                partition_key="test",
                max_item_count=3,
            )

            all_items = []
            page_count = 0
            async for page in change_feed.by_page():
                page_items = [item async for item in page]
                all_items.extend(page_items)
                page_count += 1

                last_headers = change_feed.get_last_response_headers()
                self.assertIsNotNone(last_headers)
                self.assertIn("etag", last_headers)

            self.assertEqual(len(all_items), num_items)

            response_headers = change_feed.get_response_headers()
            self.assertGreaterEqual(len(response_headers), page_count)

        finally:
            await self.created_db.delete_container(created_collection.id)

    async def test_change_feed_response_headers_returns_copies_async(self):
        """Test that get_response_headers returns copies, not references."""
        created_collection = await self.created_db.create_container(
            "test_cf_headers_copies_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            await created_collection.create_item(body={"pk": "test", "id": "item_1"})

            change_feed = created_collection.query_items_change_feed(
                start_time="Beginning",
                partition_key="test",
            )

            async for _ in change_feed:
                pass

            headers1 = change_feed.get_response_headers()
            headers2 = change_feed.get_response_headers()

            self.assertEqual(len(headers1), len(headers2))
            if len(headers1) > 0:
                headers1[0]["test-key"] = "test-value"
                self.assertNotIn("test-key", headers2[0])

        finally:
            await self.created_db.delete_container(created_collection.id)

    async def test_change_feed_response_headers_concurrent_async(self):
        """Test concurrent change feed reads using asyncio.gather to verify isolation per call."""
        created_collection = await self.created_db.create_container(
            "test_cf_headers_concurrent_async_" + str(uuid.uuid4()), PartitionKey(path="/pk")
        )
        try:
            num_partitions = 5
            items_per_partition = 10
            for pk_idx in range(num_partitions):
                for item_idx in range(items_per_partition):
                    await created_collection.create_item(
                        body={"pk": f"partition_{pk_idx}", "id": f"item_{pk_idx}_{item_idx}"}
                    )

            async def run_change_feed(partition_key: str):
                change_feed = created_collection.query_items_change_feed(
                    start_time="Beginning",
                    partition_key=partition_key,
                    max_item_count=2,
                )
                items = [item async for item in change_feed]
                headers = change_feed.get_response_headers()
                return {
                    "partition_key": partition_key,
                    "item_count": len(items),
                    "header_count": len(headers),
                    "headers": headers,
                }

            tasks = [
                run_change_feed(f"partition_{i % num_partitions}") for i in range(10)
            ]
            results = await asyncio.gather(*tasks)

            self.assertEqual(len(results), 10)
            for i, result in enumerate(results):
                self.assertEqual(
                    result["item_count"],
                    items_per_partition,
                    f"Task {i} got wrong item count",
                )
                self.assertGreater(
                    result["header_count"], 0, f"Task {i} should have captured headers"
                )
                for header_dict in result["headers"]:
                    self.assertIn(
                        "x-ms-request-charge",
                        header_dict,
                        f"Task {i} headers missing x-ms-request-charge",
                    )

            if len(results) >= 2:
                headers_0 = results[0]["headers"]
                headers_1 = results[1]["headers"]
                self.assertIsNot(headers_0, headers_1)
                if len(headers_0) > 0 and len(headers_1) > 0:
                    self.assertIsNot(headers_0[0], headers_1[0])

        finally:
            await self.created_db.delete_container(created_collection.id)


if __name__ == "__main__":
    unittest.main()
