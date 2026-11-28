# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Copy the two item-read assertions from the original dictionary/object CRUD test.

Source: tests/test_crud.py::TestCRUDOperations::
test_get_resource_with_dictionary_and_object. Only its item setup and reads
are copied; database/container/script/conflict assertions belong to other APIs.
The original source is unchanged. The fixture owns its database and client.
"""

import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from config.clients import create_data_client, create_setup_client


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperations(unittest.TestCase):
    def setUp(self):
        # Key client owns the database and container; the data client (AAD in
        # AAD lanes) does item work, as in the original.
        self.key_client = create_setup_client(_backend="rust")
        self.addCleanup(self.key_client.close)
        self.client = create_data_client(_backend="rust")
        self.addCleanup(self.client.close)
        key_database = self.key_client.create_database("read_dictionary_" + uuid.uuid4().hex)
        self.addCleanup(self.key_client.delete_database, key_database.id)
        print(f"\nOwned read-test database: {key_database.id}")
        key_database.create_container("orders", partition_key=PartitionKey(path="/pk"))
        self.container = self.client.get_database_client(key_database.id).get_container_client("orders")

    def test_get_resource_with_dictionary_and_object_rust(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_get_resource_with_dictionary_and_object
        created_container = self.container
        created_item = created_container.create_item({'id': '1' + str(uuid.uuid4()), 'pk': 'pk'})

        # read item with id
        read_item = created_container.read_item(item=created_item['id'], partition_key=created_item['pk'])
        self.assertEqual(read_item['id'], created_item['id'])

        # read item with properties
        read_item = created_container.read_item(item=created_item, partition_key=created_item['pk'])
        self.assertEqual(read_item['id'], created_item['id'])
