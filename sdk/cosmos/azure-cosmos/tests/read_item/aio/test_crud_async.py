# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Copy the item-read portion of the original async dictionary/object CRUD test.

Source: tests/test_crud_async.py::TestCRUDOperationsAsync::
test_get_resource_with_dictionary_and_object_async. Unrelated resource and
script assertions are not included. Item setup, the delay, reads and assertions
are retained; the original source is unchanged.
"""

from asyncio import sleep
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from config.clients import create_data_client_async, create_setup_client_async


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperationsAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Key client owns the database and container; the data client (AAD in
        # AAD lanes) does item work, as in the original.
        self.key_client = create_setup_client_async(_backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()
        self.client = create_data_client_async(_backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        key_database = await self.key_client.create_database("read_dictionary_" + uuid.uuid4().hex)
        self.addAsyncCleanup(self.key_client.delete_database, key_database.id)
        print(f"\nOwned read-test database: {key_database.id}")
        await key_database.create_container("orders", partition_key=PartitionKey(path="/pk"))
        self.container = self.client.get_database_client(key_database.id).get_container_client("orders")

    async def test_get_resource_with_dictionary_and_object_async_rust(self):
        # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_get_resource_with_dictionary_and_object_async
        created_container = self.container
        created_item = await created_container.create_item({'id': '1' + str(uuid.uuid4()), 'pk': 'pk'})
        await sleep(5)

        # read item with id
        read_item = await created_container.read_item(item=created_item['id'], partition_key=created_item['pk'])
        assert read_item['id'] == created_item['id']

        # read item with properties
        read_item = await created_container.read_item(item=created_item, partition_key=created_item['pk'])
        assert read_item['id'] == created_item['id']
