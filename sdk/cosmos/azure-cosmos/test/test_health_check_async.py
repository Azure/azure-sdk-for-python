import unittest
import uuid

import pytest
import pytest_asyncio
from azure.cosmos import DatabaseAccount, _location_cache, PartitionKey

from azure.cosmos._location_cache import DualEndpoint
from azure.cosmos.aio import CosmosClient, _global_endpoint_manager_async, _cosmos_client_connection_async
from test import test_config

COLLECTION = "created_collection"
REGION_1 = "East US"
REGION_2 = "West US"

@pytest_asyncio.fixture()
async def setup():
    if (TestHealthCheckAsync.masterKey == '[YOUR_KEY_HERE]' or
            TestHealthCheckAsync.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")

    client = CosmosClient(TestHealthCheckAsync.host, TestHealthCheckAsync.masterKey, consistency_level="Session")
    created_database = client.get_database_client(TestHealthCheckAsync.TEST_DATABASE_ID)
    created_collection = created_database.get_container_client(TestHealthCheckAsync.TEST_CONTAINER_SINGLE_PARTITION_ID)
    yield {
        COLLECTION: created_collection
    }

    await client.close()




def preferred_locations():
    return [([]), ([REGION_1, REGION_2])]


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestHealthCheckAsync:
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID

    @pytest.mark.parametrize("preferred_location", preferred_locations())
    async def test_effective_preferred_regions_async(self, setup, preferred_location):

        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_getDatabaseAccountCheck = _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.MockGetDatabaseAccount
        _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck = self.MockGetDatabaseAccount
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=preferred_location)
            # this will setup the location cache
            await client.client_connection._global_endpoint_manager.force_refresh_on_startup(None)
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck = self.original_getDatabaseAccountCheck
        expected_dual_endpoints = []
        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        expected_dual_endpoints.append(DualEndpoint(locational_endpoint, locational_endpoint))
        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        expected_dual_endpoints.append(DualEndpoint(locational_endpoint, locational_endpoint))
        read_dual_endpoints = client.client_connection._global_endpoint_manager.location_cache.read_dual_endpoints
        assert read_dual_endpoints == expected_dual_endpoints

    @pytest.mark.parametrize("preferred_location", preferred_locations())
    async def test_health_check_success_async(self, setup, preferred_location):

        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_getDatabaseAccountCheck = _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.MockGetDatabaseAccount
        _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck = self.MockGetDatabaseAccountCheck()
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=preferred_location)
            # this will setup the location cache
            await client.client_connection._global_endpoint_manager.endpoint_health_check(None)
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck = self.original_getDatabaseAccountCheck
        expected_dual_endpoints = []
        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        expected_dual_endpoints.append(DualEndpoint(locational_endpoint, locational_endpoint))
        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        expected_dual_endpoints.append(DualEndpoint(locational_endpoint, locational_endpoint))
        read_dual_endpoints = client.client_connection._global_endpoint_manager.location_cache.read_dual_endpoints
        assert read_dual_endpoints == expected_dual_endpoints



    class MockGetDatabaseAccountCheck(object):
        def __init__(self):
            self.counter = 0

        async def __call__(self, endpoint):
            locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(TestHealthCheckAsync.host, REGION_1)
            assert endpoint == locational_endpoint

            assert self.counter <= 1

            self.counter += 1



    async def MockGetDatabaseAccount(self, endpoint):
        read_regions = [REGION_1, REGION_2]
        read_locations = []
        for loc in read_regions:
            locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(endpoint, loc)
            read_locations.append({'databaseAccountEndpoint': locational_endpoint, 'name': loc})
        write_regions = [REGION_1]
        write_locations = []
        for loc in write_regions:
            locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(endpoint, loc)
            write_locations.append({'databaseAccountEndpoint': locational_endpoint, 'name': loc})
        multi_write = False

        db_acc = DatabaseAccount()
        db_acc.DatabasesLink = "/dbs/"
        db_acc.MediaLink = "/media/"
        db_acc._ReadableLocations = read_locations
        db_acc._WritableLocations = write_locations
        db_acc._EnableMultipleWritableLocations = multi_write
        db_acc.ConsistencyPolicy = {"defaultConsistencyLevel": "Session"}
        return db_acc

if __name__ == '__main__':
    unittest.main()
