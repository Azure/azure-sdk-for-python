# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy, ContainerProxy
from azure.cosmos._routing import routing_range as routing_range
from azure.cosmos._routing.routing_map_provider import PartitionKeyRangeCache


@pytest.mark.cosmosEmulator
class TestRoutingMapEndToEnd(unittest.TestCase):
    """Routing Map Functionalities end-to-end Tests.
    """

    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    configs = test_config.TestConfig
    client: cosmos_client.CosmosClient = None
    created_database: DatabaseProxy = None
    created_container: ContainerProxy = None
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    TEST_COLLECTION_ID = configs.TEST_SINGLE_PARTITION_CONTAINER_ID

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.created_database = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.created_container = cls.created_database.get_container_client(cls.TEST_COLLECTION_ID)
        cls.collection_link = cls.created_container.container_link

    def test_read_partition_key_ranges(self):
        partition_key_ranges = list(self.client.client_connection._ReadPartitionKeyRanges(self.collection_link))
        self.assertEqual(1, len(partition_key_ranges))

    def test_routing_map_provider(self):
        partition_key_ranges = list(self.client.client_connection._ReadPartitionKeyRanges(self.collection_link))

        routing_mp = PartitionKeyRangeCache(self.client.client_connection)
        overlapping_partition_key_ranges = routing_mp.get_overlapping_ranges(
            self.collection_link, routing_range.Range("", "FF", True, False))
        self.assertEqual(len(overlapping_partition_key_ranges), len(partition_key_ranges))
        self.assertEqual(overlapping_partition_key_ranges, partition_key_ranges)


if __name__ == "__main__":
    unittest.main()
