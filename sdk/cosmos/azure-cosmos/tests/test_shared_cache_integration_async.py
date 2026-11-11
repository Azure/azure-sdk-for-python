# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Async integration tests for the shared partition key range cache and PKRange namedtuple.

Async counterparts of test_shared_cache_integration.py, validating that the async
CosmosClient shares the routing map cache correctly, that clear_cache() works
transparently, and that PKRange namedtuples are compatible with all async operations.
"""

import unittest
import uuid
from unittest.mock import AsyncMock, Mock

import pytest

import test_config
from azure.cosmos.aio import CosmosClient
from azure.cosmos._routing.aio.routing_map_provider import (
    PartitionKeyRangeCache,
    _shared_routing_map_cache,
    _shared_cache_refcounts,
)


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
class TestSharedCacheIntegrationAsync(unittest.IsolatedAsyncioTestCase):
    """Async integration tests requiring the Cosmos emulator."""

    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    async def asyncSetUp(self):
        self.client1 = CosmosClient(self.host, self.master_key)
        self.db = self.client1.get_database_client(self.TEST_DATABASE_ID)
        self.container = self.db.get_container_client(self.TEST_CONTAINER_ID)
        for i in range(20):
            await self.container.upsert_item(
                {"id": f"async-cache-item-{i}", "pk": f"pk-{i % 5}", "value": i}
            )

    async def asyncTearDown(self):
        for i in range(20):
            try:
                await self.container.delete_item(f"async-cache-item-{i}", partition_key=f"pk-{i % 5}")
            except Exception:
                pass
        await self.client1.close()

    def _get_routing_provider(self, client):
        return client.client_connection._routing_map_provider

    def _get_cache_dict(self, client):
        return self._get_routing_provider(client)._collection_routing_map_by_item

    async def _populate_cache(self, client, container):
        """Force PK range cache population by directly calling the routing-map provider."""
        provider = self._get_routing_provider(client)
        await provider.get_routing_map(container.container_link, feed_options=None)

    async def test_multi_client_shared_cache_reads_async(self):
        """Async: Two clients to the same endpoint share the routing map."""
        async with CosmosClient(self.host, self.master_key) as client2:
            container2 = client2.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)

            await self.container.read_item("async-cache-item-0", partition_key="pk-0")

            cache1 = self._get_cache_dict(self.client1)
            cache2 = self._get_cache_dict(client2)
            self.assertIs(cache1, cache2)

            result = await container2.read_item("async-cache-item-1", partition_key="pk-1")
            self.assertEqual(result["id"], "async-cache-item-1")

    async def test_multi_client_shared_cache_queries_async(self):
        """Async: Client2 uses cached routing map populated by client1 for queries."""
        async with CosmosClient(self.host, self.master_key) as client2:
            container2 = client2.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)

            await self._populate_cache(self.client1, self.container)

            cache = self._get_cache_dict(self.client1)
            self.assertTrue(len(cache) > 0, "Cache should be populated after routing-map fetch")

            results = []
            async for item in container2.query_items(
                "SELECT * FROM c WHERE c.pk = 'pk-0'"
            ):
                results.append(item)
            self.assertTrue(len(results) > 0)

    async def test_clear_cache_triggers_repopulation_async(self):
        """Async: After clear_cache(), the next routing-map fetch transparently re-populates."""
        await self._populate_cache(self.client1, self.container)
        cache = self._get_cache_dict(self.client1)
        self.assertTrue(len(cache) > 0)

        provider = self._get_routing_provider(self.client1)
        provider.clear_cache()
        self.assertEqual(len(cache), 0)

        await self._populate_cache(self.client1, self.container)
        cache = self._get_cache_dict(self.client1)
        self.assertTrue(len(cache) > 0, "Cache should be re-populated after fetch")

    async def test_clear_cache_propagates_to_shared_clients_async(self):
        """Async: clear_cache() preserves dict identity for all sharing clients."""
        async with CosmosClient(self.host, self.master_key) as client2:
            container2 = client2.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)

            await self.container.read_item("async-cache-item-0", partition_key="pk-0")

            self._get_routing_provider(self.client1).clear_cache()

            cache1 = self._get_cache_dict(self.client1)
            cache2 = self._get_cache_dict(client2)
            self.assertIs(cache1, cache2, "Both clients should reference the same dict after clear_cache")
            self.assertEqual(len(cache1), 0)

            result = await container2.read_item("async-cache-item-2", partition_key="pk-2")
            self.assertEqual(result["id"], "async-cache-item-2")

    async def test_different_endpoints_isolated_with_emulator_async(self):
        """Async: Emulator client cache is isolated from a different endpoint."""
        class DummyClient:
            url_connection = "https://other-async-account.documents.azure.com:443/"

        dummy_cache = PartitionKeyRangeCache(DummyClient())
        dummy_cache._collection_routing_map_by_item["dummy-coll"] = "dummy-data"

        await self.container.read_item("async-cache-item-0", partition_key="pk-0")
        emulator_cache = self._get_cache_dict(self.client1)

        self.assertNotIn("dummy-coll", emulator_cache)
        self.assertIn("dummy-coll", dummy_cache._collection_routing_map_by_item)

    async def test_pkrange_survives_full_crud_lifecycle_async(self):
        """Async: All CRUD operations work correctly with PKRange-based routing maps."""
        crud_id = f"async-crud-{uuid.uuid4()}"

        item = await self.container.create_item({"id": crud_id, "pk": "crud-pk", "data": "test"})
        self.assertEqual(item["id"], crud_id)

        read = await self.container.read_item(crud_id, partition_key="crud-pk")
        self.assertEqual(read["data"], "test")

        read["data"] = "updated"
        replaced = await self.container.replace_item(crud_id, read)
        self.assertEqual(replaced["data"], "updated")

        results = []
        async for r in self.container.query_items(
            f"SELECT * FROM c WHERE c.id = '{crud_id}'"
        ):
            results.append(r)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["data"], "updated")

        read["data"] = "upserted"
        upserted = await self.container.upsert_item(read)
        self.assertEqual(upserted["data"], "upserted")

        await self.container.delete_item(crud_id, partition_key="crud-pk")
        with self.assertRaises(Exception):
            await self.container.read_item(crud_id, partition_key="crud-pk")

        # Async point reads / writes don't always populate the routing-map
        # cache the way sync does (cf. _populate_cache helper). Drive a
        # routing-aware operation so the cache assertion below is meaningful.
        await self._populate_cache(self.client1, self.container)
        cache = self._get_cache_dict(self.client1)
        self.assertTrue(len(cache) > 0)

    async def test_pkrange_in_change_feed_async(self):
        """Async: Change feed operations work with PKRange-based routing maps."""
        cf_id = f"async-cf-{uuid.uuid4()}"
        await self.container.create_item({"id": cf_id, "pk": "cf-pk", "data": "change-feed-test"})

        results = []
        async for item in self.container.query_items_change_feed(
            start_time="Beginning",
            partition_key="cf-pk"
        ):
            results.append(item)
        self.assertTrue(len(results) > 0, "Change feed should return results")

        all_results = []
        async for item in self.container.query_items_change_feed(start_time="Beginning"):
            all_results.append(item)
        self.assertTrue(len(all_results) > 0, "Cross-partition change feed should return results")

        await self.container.delete_item(cf_id, partition_key="cf-pk")


@pytest.mark.asyncio
async def test_shared_cache_teardown_preserves_other_client_lifetime():
    endpoint = "https://shared-cache-teardown.documents.azure.com:443/"
    connection = Mock(url_connection=endpoint)
    retained = PartitionKeyRangeCache(connection)
    owned = PartitionKeyRangeCache(connection)
    following = None
    case = TestSharedCacheIntegrationAsync("test_clear_cache_triggers_repopulation_async")
    case.host = endpoint
    case.container = Mock(delete_item=AsyncMock())
    case.client1 = Mock(close=AsyncMock(side_effect=owned.release))

    try:
        await case.asyncTearDown()
        following = PartitionKeyRangeCache(connection)
        retained.release()
        cache = following._collection_routing_map_by_item
        cache["collection"] = "routing-map"
        following.clear_cache()
        assert len(cache) == 0
        assert cache is retained._collection_routing_map_by_item
        assert _shared_routing_map_cache[endpoint] is cache
        assert _shared_cache_refcounts[endpoint] == 1
        case.client1.close.assert_awaited_once()
    finally:
        owned.release()
        retained.release()
        if following is not None:
            following.release()


if __name__ == "__main__":
    unittest.main()
