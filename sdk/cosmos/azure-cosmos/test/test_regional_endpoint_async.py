# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import unittest
import uuid

import pytest

from azure.cosmos.aio import CosmosClient, _global_endpoint_manager_async
from azure.cosmos import PartitionKey, DatabaseAccount
from azure.cosmos._location_cache import RegionalEndpoint
from test import test_config


@pytest.mark.cosmosEmulator
class TestRegionalEndpoints(unittest.IsolatedAsyncioTestCase):
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    REGION1 = "West US"
    REGION2 = "East US"
    REGION3 = "West US 2"
    REGIONAL_ENDPOINT = RegionalEndpoint(host, "something_different")
    TEST_DATABASE_ID = "test_regional_endpoint_db" + str(uuid.uuid4())
    TEST_CONTAINER_ID = "test_regional_endpoint_container" + str(uuid.uuid4())

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = CosmosClient(cls.host, cls.masterKey)

    async def asyncSetUp(self):
        self.created_database = await self.client.create_database_if_not_exists(self.TEST_DATABASE_ID)
        self.created_container = await self.created_database.create_container_if_not_exists(self.TEST_CONTAINER_ID,
                                                                                        PartitionKey(path="/id"))
    @classmethod
    async def asyncTearDown(cls):
        await cls.client.delete_database(cls.TEST_DATABASE_ID)


    async def test_no_swaps_on_successful_request(self):
        original_get_database_account_stub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.MockGetDatabaseAccountStub
        mocked_client = CosmosClient(self.host, self.masterKey)
        db = mocked_client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_ID)
        # Mock the GetDatabaseAccountStub to return the regional endpoints

        original_read_endpoint = (mocked_client.client_connection._global_endpoint_manager
                                  .location_cache.get_read_regional_endpoint())
        try:
            await container.create_item(body={"id": "1"})
        finally:
            # Check for if there was a swap
            self.assertEqual(original_read_endpoint,
                             mocked_client.client_connection._global_endpoint_manager
                             .location_cache.get_read_regional_endpoint())
            # return it
            self.assertEqual(self.REGIONAL_ENDPOINT.get_current(),
                             mocked_client.client_connection._global_endpoint_manager
                             .location_cache.get_write_regional_endpoint())
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = original_get_database_account_stub



    async def MockGetDatabaseAccountStub(self, endpoint):
        read_locations = []
        read_locations.append({'databaseAccountEndpoint': endpoint, 'name': "West US"})
        read_locations.append({'databaseAccountEndpoint': "some different endpoint", 'name': "West US"})
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