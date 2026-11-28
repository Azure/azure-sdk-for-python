# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Main's async recreation assertions through readers warmed before recreation."""
from contextlib import AsyncExitStack
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey, exceptions
from common.throughput_fixtures import owned_database_async
from config import clients


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestContainerPropertiesCache(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        stack = AsyncExitStack()
        self.addAsyncCleanup(stack.aclose)
        setup = await stack.enter_async_context(clients.create_setup_client_async(_backend="rust"))
        self.database = await stack.enter_async_context(
            owned_database_async(setup, "read-recreate-" + uuid.uuid4().hex)
        )
        self.readers = [
            await stack.enter_async_context(clients.create_data_client_async(_backend="rust")) for _ in range(2)
        ]

    async def _recreate(self, old_paths, new_paths, old_items, new_items, old_key):
        name = "orders"
        await self.database.create_container(name, partition_key=PartitionKey(path=old_paths))
        async with clients.create_data_client_async(_backend="rust") as writer:
            container = writer.get_database_client(self.database.id).get_container_client(name)
            saved = [await container.create_item(body=item) for item in old_items]
        readers = [client.get_database_client(self.database.id).get_container_client(name) for client in self.readers]
        for reader in readers:
            await reader.read_item(saved[0]["id"], partition_key=old_key)
        await self.database.delete_container(name)
        await self.database.create_container(name, partition_key=PartitionKey(path=new_paths))
        # Explicit setup keys avoid stale-key extraction (gap 22) without resetting the readers.
        async with clients.create_data_client_async(_backend="rust") as writer:
            container = writer.get_database_client(self.database.id).get_container_client(name)
            for item in new_items:
                key = [item[path[1:]] for path in new_paths] if isinstance(new_paths, list) else item[new_paths[1:]]
                await container.create_item(body=item, request_options={"partitionKey": key})
        return saved, readers

    async def test_container_recreate_read_item_async_rust(self):
        # Source: tests/test_container_properties_cache_async.py::TestContainerPropertiesCache.test_container_recreate_read_item_async
        saved, readers = await self._recreate(
            "/PK", "/partkey",
            [{"id": "item1", "PK": "val"}, {"id": "item2", "PK": "OtherValue"}],
            [{"id": "item1", "partkey": "val"}, {"id": "item2", "partkey": "DifferentValue"}],
            "val",
        )
        item_to_read, item_to_read2 = saved
        created_container = readers[0]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            await created_container.read_item(item=item_to_read, partition_key="val")
        assert caught.exception.status_code == 404 or isinstance(
            caught.exception, exceptions.CosmosResourceNotFoundError
        )
        read_item = await created_container.read_item(item="item1", partition_key="val")
        assert read_item != item_to_read
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            await readers[1].read_item(item=item_to_read2, partition_key="OtherValue")
        assert caught.exception.status_code == 404

    async def test_container_recreate_read_item_sub_partition_async_rust(self):
        # Source: tests/test_container_properties_cache_async.py::TestContainerPropertiesCache.test_container_recreate_read_item_sub_partition_async
        saved, readers = await self._recreate(
            ["/country", "/state"], ["/county", "/city"],
            [{"id": "item1", "country": "USA", "state": "CA"},
             {"id": "item2", "country": "MEX", "state": "Michoac\u00e1n"}],
            [{"id": "item1", "county": "ventura", "city": "oxnard"}],
            ["USA", "CA"],
        )
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            await readers[0].read_item(item=saved[0], partition_key=["USA", "CA"])
        assert caught.exception.status_code == 404
