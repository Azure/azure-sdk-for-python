# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async shared-cache integration tests that exercise query_items, on the Rust path.

The CRUD and query steps run unchanged. The originals also fill and inspect the
legacy Python partition-key-range cache, which Rust operations never use; Rust keeps
that cache inside its driver with no way to inspect it, so those steps are skipped.
Uses a test-owned database and container.
"""

import os
import unittest
import uuid

import pytest

from config import settings
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient

CACHE_NOT_OBSERVABLE = (
    "internals-only: cache step not run on Rust: the partition-key-range routing map lives in the Rust driver, "
    "which exposes no inspection hook (only _debug_cached_account_regions and attempt/retry "
    "counters); client.client_connection._routing_map_provider is the legacy cache that Rust "
    "operations never populate."
)


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
class TestSharedCacheIntegrationAsync(unittest.IsolatedAsyncioTestCase):
    """Async integration tests requiring the Cosmos emulator."""

    host = os.environ.get("ACCOUNT_HOST", settings.TestSettings.host)
    master_key = os.environ.get("ACCOUNT_KEY", settings.TestSettings.masterKey)

    async def asyncSetUp(self):
        self.client1 = CosmosClient(self.host, self.master_key, _backend="rust")
        self.TEST_DATABASE_ID = "query_shared_cache_async_" + uuid.uuid4().hex
        self.db = await self.client1.create_database(self.TEST_DATABASE_ID)
        self.container = await self.db.create_container(
            id="MultiPartitionTestContainer-" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=settings.TestSettings.THROUGHPUT_FOR_5_PARTITIONS,
        )
        self.TEST_CONTAINER_ID = self.container.id
        for i in range(20):
            await self.container.upsert_item(
                {"id": f"async-cache-item-{i}", "pk": f"pk-{i % 5}", "value": i}
            )

    async def asyncTearDown(self):
        try:
            await self.client1.delete_database(self.TEST_DATABASE_ID)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.client1.close()

    async def test_multi_client_shared_cache_queries_async_rust(self):
        # Source: tests/test_shared_cache_integration_async.py::TestSharedCacheIntegrationAsync.test_multi_client_shared_cache_queries_async
        """Async: Client2 uses cached routing map populated by client1 for queries."""
        async with CosmosClient(self.host, self.master_key, _backend="rust") as client2:
            container2 = client2.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)

            # The original fills the legacy routing-map cache via _populate_cache here and asserts
            # it is non-empty; those two steps are reported by the skip below.

            results = []
            async for item in container2.query_items(
                "SELECT * FROM c WHERE c.pk = 'pk-0'"
            ):
                results.append(item)
            self.assertTrue(len(results) > 0)

        pytest.skip(CACHE_NOT_OBSERVABLE + " The client2 query and its assertion above passed.")

    async def test_pkrange_survives_full_crud_lifecycle_async_rust(self):
        # Source: tests/test_shared_cache_integration_async.py::TestSharedCacheIntegrationAsync.test_pkrange_survives_full_crud_lifecycle_async
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

        # The original filled the legacy routing-map cache via _populate_cache, then checked it.
        pytest.skip(CACHE_NOT_OBSERVABLE + " All CRUD, delete and read-after-delete assertions above passed.")
        provider = self.client1.client_connection._routing_map_provider
        await provider.get_routing_map(self.container.container_link, feed_options=None)
        cache = provider._collection_routing_map_by_item
        self.assertTrue(len(cache) > 0)
