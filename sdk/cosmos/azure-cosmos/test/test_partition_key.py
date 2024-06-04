# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.partition_key as partition_key
import test_config
from azure.cosmos import DatabaseProxy


@pytest.mark.cosmosEmulator
class TestPartitionKey(unittest.TestCase):
    """Tests to verify if non-partitioned collections are properly accessed on migration with version 2018-12-31.
    """

    client: cosmos_client.CosmosClient = None
    created_db: DatabaseProxy = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.created_collection = cls.created_db.get_container_client(cls.TEST_CONTAINER_ID)

    def test_multi_partition_collection_read_document_with_no_pk(self):
        document_definition = {'id': str(uuid.uuid4())}
        self.created_collection.create_item(body=document_definition)
        read_item = self.created_collection.read_item(item=document_definition['id'],
                                                      partition_key=partition_key.NonePartitionKeyValue)
        self.assertEqual(read_item['id'], document_definition['id'])
        self.created_collection.delete_item(item=document_definition['id'],
                                            partition_key=partition_key.NonePartitionKeyValue)

    def test_hash_v2_partition_key_definition(self):
        created_container_properties = self.created_collection.read()
        self.assertEqual(created_container_properties['partitionKey']['version'], 2)

    def test_hash_v1_partition_key_definition(self):
        created_container = self.created_db.create_container(
            id='container_with_pkd_v2' + str(uuid.uuid4()),
            partition_key=partition_key.PartitionKey(path="/id", kind="Hash", version=1)
        )
        created_container_properties = created_container.read()
        self.assertEqual(created_container_properties['partitionKey']['version'], 1)
        self.created_db.delete_container(created_container)


if __name__ == '__main__':
    unittest.main()
