# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Copy the two item-read assertions from the original dictionary/object CRUD test.

Source: tests/test_crud.py::TestCRUDOperations::
test_get_resource_with_dictionary_and_object. Only its item setup and reads
are copied; database/container/script/conflict assertions belong to other APIs.
The original source is unchanged. The fixture owns its database and client.
"""

import os
import unittest
import uuid

from azure.cosmos import CosmosClient, PartitionKey


class TestCRUDOperations(unittest.TestCase):
    def setUp(self):
        self.client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust",
        )
        self.addCleanup(self.client.close)
        self.database = self.client.create_database("read_dictionary_" + uuid.uuid4().hex)
        self.addCleanup(self.client.delete_database, self.database.id)
        print(f"\nOwned read-test database: {self.database.id}")
        self.container = self.database.create_container("orders", partition_key=PartitionKey(path="/pk"))

    def test_get_resource_with_dictionary_and_object(self):
        created_container = self.container
        created_item = created_container.create_item({'id': '1' + str(uuid.uuid4()), 'pk': 'pk'})

        # read item with id
        read_item = created_container.read_item(item=created_item['id'], partition_key=created_item['pk'])
        self.assertEqual(read_item['id'], created_item['id'])

        # read item with properties
        read_item = created_container.read_item(item=created_item, partition_key=created_item['pk'])
        self.assertEqual(read_item['id'], created_item['id'])
