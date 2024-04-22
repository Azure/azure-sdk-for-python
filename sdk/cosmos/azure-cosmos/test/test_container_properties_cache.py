# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test.
"""

import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosEmulator
class TestContainerPropertiesCache(unittest.TestCase):
    """Python CRUD Tests.
        """

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []
    client: cosmos_client.CosmosClient = None

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

                :Parameters:
                    - `status_code`: int
                    - `func`: function
                """
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            self.assertEqual(inst.status_code, status_code)

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.databaseForTest = cls.client.get_database_client(cls.configs.TEST_DATABASE_ID)

    def test_container_properties_cache(self):
        client = self.client
        database_name = self.configs.TEST_DATABASE_ID
        container_name = str(uuid.uuid4())
        container_pk = "PK"
        # Create The Container
        try:
            client.get_database_client(database_name).create_container(id=container_name, partition_key=PartitionKey(
                path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            pass
        # Delete The cache as this is meant to test calling operations on a preexisting container
        # and not a freshly made one
        client.client_connection.collection_properties_cache = {}
        # We will hot path operations to verify cache persists
        # This will extract partition key from the item body, which will need partition key definition from
        # container properties. We test to check the cache is empty since we just created the container
        self.assertTrue(client.client_connection.collection_properties_cache == {})
        client.get_database_client(database_name).get_container_client(container_name).create_item(
            body={'id': 'item1', container_pk: 'value'})
        # Since the cache was empty, it should have called a container read to get properties. So now Cache should
        # be populated and available even when we don't have a container instance
        self.assertTrue(client.client_connection.collection_properties_cache != {})
        self.databaseForTest.delete_container(container_name)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True:  # raised by sys.exit(True) when tests failed
            raise
