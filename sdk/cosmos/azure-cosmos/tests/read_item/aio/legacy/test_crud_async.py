# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Copy the item-read portion of the original async dictionary/object CRUD test.

Source: tests/test_crud_async.py::TestCRUDOperationsAsync::
test_get_resource_with_dictionary_and_object_async. Unrelated resource and
script assertions are not included. Item setup, the delay, reads and assertions
are retained; the original source is unchanged.
"""

from asyncio import sleep
import os
import unittest
import uuid

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient


class TestCRUDOperationsAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust",
        )
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.database = await self.client.create_database("read_dictionary_" + uuid.uuid4().hex)
        self.addAsyncCleanup(self.client.delete_database, self.database.id)
        print(f"\nOwned read-test database: {self.database.id}")
        self.container = await self.database.create_container("orders", partition_key=PartitionKey(path="/pk"))

    async def test_get_resource_with_dictionary_and_object_async(self):
        created_container = self.container
        created_item = await created_container.create_item({'id': '1' + str(uuid.uuid4()), 'pk': 'pk'})
        await sleep(5)

        # read item with id
        read_item = await created_container.read_item(item=created_item['id'], partition_key=created_item['pk'])
        assert read_item['id'] == created_item['id']

        # read item with properties
        read_item = await created_container.read_item(item=created_item, partition_key=created_item['pk'])
        assert read_item['id'] == created_item['id']
