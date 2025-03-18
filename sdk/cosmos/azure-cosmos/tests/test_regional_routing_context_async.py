# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import unittest
import uuid

import pytest

import test_config
from azure.cosmos import DatabaseAccount
from azure.cosmos._location_cache import RegionalRoutingContext
from azure.cosmos.aio import CosmosClient, _global_endpoint_manager_async


@pytest.mark.cosmosEmulator
class TestRegionalRoutingContextAsync(unittest.IsolatedAsyncioTestCase):
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    REGION1 = "West US"
    REGION2 = "East US"
    REGION3 = "West US 2"
    REGIONAL_ROUTING_CONTEXT = RegionalRoutingContext(host, "something_different")
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

    async def test_no_swaps_on_successful_request(self):
        original_get_database_account_stub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.MockGetDatabaseAccountStub
        mocked_client = CosmosClient(self.host, self.masterKey)
        db = mocked_client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_ID)
        # Mock the GetDatabaseAccountStub to return the regional endpoints

        original_read_endpoint = (mocked_client.client_connection._global_endpoint_manager
                                  .location_cache.get_read_regional_routing_context())
        try:
            await container.create_item(body={"id": str(uuid.uuid4())})
        finally:
            # Check for if there was a swap
            self.assertEqual(original_read_endpoint,
                             mocked_client.client_connection._global_endpoint_manager
                             .location_cache.get_read_regional_routing_context())
            # return it
            self.assertEqual(self.REGIONAL_ROUTING_CONTEXT.get_primary(),
                             mocked_client.client_connection._global_endpoint_manager
                             .location_cache.get_write_regional_routing_context())
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = original_get_database_account_stub
            await mocked_client.close()

    async def MockGetDatabaseAccountStub(self, endpoint):
        read_locations = []
        read_locations.append({'databaseAccountEndpoint': endpoint, 'name': "West US"})
        read_locations.append({'databaseAccountEndpoint': "some different endpoint", 'name': "East US"})
        write_regions = ["West US"]
        write_locations = []
        for loc in write_regions:
            write_locations.append({'databaseAccountEndpoint': endpoint, 'name': loc})
        multi_write = False

        db_acc = DatabaseAccount()
        db_acc.DatabasesLink = "/dbs/"
        db_acc.MediaLink = "/media/"
        db_acc._ReadableLocations = read_locations
        db_acc._WritableLocations = write_locations
        db_acc._EnableMultipleWritableLocations = multi_write
        db_acc.ConsistencyPolicy = {"defaultConsistencyLevel": "Session"}
        return db_acc
