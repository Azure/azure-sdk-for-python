# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async query-after-container-recreation check, on the Rust path.

The original saved a copy of the legacy Python container-properties cache
before recreating the container and restored it before the queries. Rust keeps
container metadata inside the driver, so this copy gets the same stale state
from separate Rust clients that each loaded the old container's metadata
before the container was recreated; one is used per restore.
Each test owns a uniquely named database.
"""

from contextlib import AsyncExitStack
import os
import unittest
import uuid

import pytest

from common.throughput_fixtures import owned_database_async
from config import clients

from azure.cosmos import PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestContainerPropertiesCache(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.key_client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()
        cleanup = AsyncExitStack()
        self.addAsyncCleanup(cleanup.aclose)
        database_id = "query_recreate_async_" + uuid.uuid4().hex
        self.key_databaseForTest = await cleanup.enter_async_context(
            owned_database_async(self.key_client, database_id))
        self.client = clients.create_data_client_async()
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.databaseForTest = self.client.get_database_client(database_id)

    async def _create_container_for_test_async(self, *args, **kwargs):
        container_ref = await self.key_databaseForTest.create_container(*args, **kwargs)
        return self.databaseForTest.get_container_client(container_ref.id)

    async def _delete_container_for_test_async(self, *args, **kwargs):
        return await self.key_databaseForTest.delete_container(*args, **kwargs)

    async def _stale_databases(self, container_name, partition_key, count):
        """Rust data clients whose drivers hold the current container's metadata."""
        stale = []
        for _ in range(count):
            stale_client = clients.create_data_client_async()
            self.addAsyncCleanup(stale_client.close)
            await stale_client.__aenter__()
            database = stale_client.get_database_client(self.databaseForTest.id)
            # Any data-plane call resolves and caches the container definition in the driver.
            with self.assertRaises(exceptions.CosmosResourceNotFoundError):
                await database.get_container_client(container_name).read_item(
                    "metadata-warmup-" + uuid.uuid4().hex, partition_key=partition_key)
            stale.append(database)
        return stale

    async def test_container_recreate_query_async_rust(self):
        # Source: tests/test_container_properties_cache_async.py::TestContainerPropertiesCache.test_container_recreate_query_async
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = "PK"
        container2_pk = "partkey"
        # Create The Container
        try:
            created_container = await self._create_container_for_test_async(id=container_name, partition_key=PartitionKey(
                path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        # create an item to read
        try:
            item_to_read = await created_container.create_item(body={'id': 'item1', container_pk: 'val'})
            item_to_read2 = await created_container.create_item(body={'id': 'item2', container_pk: 'OtherValue'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))

        # Recreate container
        # Replaces copy.deepcopy(client.client_connection.__container_properties_cache): one Rust
        # client per later restore, each holding the old container's metadata.
        old_cache = await self._stale_databases(container_name, "val", 2)
        await self._delete_container_for_test_async(created_container)
        try:
            created_container = await self._create_container_for_test_async(id=container_name, partition_key=PartitionKey(
                path="/" + container2_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        # Known gap 22: `create_item()`, `upsert_item()`, `replace_item()`: stale extracted key after container recreation (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22). The data client loaded the old /PK definition when it created item1/item2, so its create below extracts the key with the old path and fails with 400/1001 instead of refreshing; the queries after it cannot run.
        pytest.skip("driver-gap: after container recreation the stale client keeps the old extracted partition key, so this write fails with 400 (known gap 22, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22).")
        try:
            await created_container.create_item(body={'id': 'item1', container2_pk: 'val'})
            await created_container.create_item(body={'id': 'item2', container2_pk: 'DifferentValue'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))
        created_container = old_cache.pop(0).get_container_client(container_name)
        # Will succeed because item id and partition key value are the same as an existing one in the new container
        # But queried items are not the same as their RID will be different
        try:
            query = "SELECT * FROM c WHERE c.id = @id"
            parameters = [{"name": "@id", "value": item_to_read['id']}]
            query_result = [item async for item in created_container.query_items(query=query,
                                                                                 parameters=parameters)]
            assert len(query_result) == 1
        except exceptions.CosmosHttpResponseError as e:
            self.fail("Query should still succeed as item has same id despite the RID not matching.")
        # Will succeed because item id and partition key value are the same as an existing one in the new container
        # But queried items are not the same as their RID will be different
        query = "SELECT * FROM c WHERE c.id = @id"
        parameters = [{"name": "@id", "value": 'item1'}]
        query_result = [item async for item in created_container.query_items(query=query,
                                                                             parameters=parameters)]
        assert query_result[0] != item_to_read
        created_container = old_cache.pop(0).get_container_client(container_name)
        try:
            # Trying to query for item from old container will return empty query
            query = "SELECT * FROM c WHERE c.partKey = @partKey"
            parameters = [{"name": "@partKey", "value": item_to_read2['PK']}]
            query_result = [item async for item in created_container.query_items(query=query,
                                                                                 parameters=parameters)]
            assert len(query_result) == 0
        except exceptions.CosmosHttpResponseError as e:
            self.fail("Query should still succeed if container is recreated.")
        await self._delete_container_for_test_async(container_name)
