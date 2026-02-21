# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import unittest
import uuid

import pytest

import test_config
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosEmulator
class TestRegionalRoutingContextAsync(unittest.IsolatedAsyncioTestCase):
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.created_database = self.client.get_database_client(self.TEST_DATABASE_ID)
        self.created_container = self.created_database.get_container_client(self.TEST_CONTAINER_ID)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_no_swaps_on_successful_request_async(self):
        # Make sure that getDatabaseAccount call has finished
        await self.client.__aenter__()
        original_read_endpoint = (self.client.client_connection._global_endpoint_manager
                                  .location_cache.get_read_regional_routing_context())
        await self.created_container.create_item(body={"id": str(uuid.uuid4())})
        # Check for if there was a swap
        self.assertEqual(original_read_endpoint,
                         self.client.client_connection._global_endpoint_manager
                         .location_cache.get_read_regional_routing_context())
        self.assertEqual(original_read_endpoint,
                         self.client.client_connection._global_endpoint_manager
                         .location_cache.get_write_regional_routing_context())
