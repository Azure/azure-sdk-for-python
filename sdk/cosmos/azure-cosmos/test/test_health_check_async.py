import asyncio
import time
import unittest
import uuid
from typing import List

import pytest
import pytest_asyncio
import test_config
from azure.cosmos import DatabaseAccount, _location_cache

from azure.cosmos._location_cache import DualEndpoint
from azure.cosmos.aio import CosmosClient, _global_endpoint_manager_async, _cosmos_client_connection_async

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

def health_check():
    # preferred_location, use_write_global_endpoint, use_read_global_endpoint
    return [
        ([REGION_1, REGION_2], True, True),
        ([REGION_1, REGION_2], False, True),
        ([REGION_1, REGION_2], True, False),
        ([REGION_1, REGION_2], False, False)
    ]

@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestHealthCheckAsync:
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID

    @pytest.mark.parametrize("preferred_location, use_write_global_endpoint, use_read_global_endpoint", health_check())
    async def test_health_check_success_startup_async(self, setup, preferred_location, use_write_global_endpoint, use_read_global_endpoint):

        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_getDatabaseAccountCheck = _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck
        regions = [REGION_1, REGION_2]
        mock_get_database_account_check = self.MockGetDatabaseAccountCheck()
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(regions, use_write_global_endpoint, use_read_global_endpoint))
        _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck = mock_get_database_account_check
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=preferred_location)
            # this will setup the location cache
            client.client_connection._global_endpoint_manager.refresh_needed = True
            await client.client_connection._global_endpoint_manager.refresh_endpoint_list(None)
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck = self.original_getDatabaseAccountCheck
        expected_dual_endpoints = []

        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        if use_write_global_endpoint and use_read_global_endpoint:
            assert mock_get_database_account_check.counter == 0
        endpoint = self.host if use_read_global_endpoint else locational_endpoint
        expected_dual_endpoints.append(DualEndpoint(endpoint, endpoint))
        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        expected_dual_endpoints.append(DualEndpoint(locational_endpoint, locational_endpoint))
        read_dual_endpoints = client.client_connection._global_endpoint_manager.location_cache.read_dual_endpoints
        assert read_dual_endpoints == expected_dual_endpoints
        await client.close()

    @pytest.mark.parametrize("preferred_location, use_write_global_endpoint, use_read_global_endpoint", health_check())
    async def test_health_check_failure_startup_async(self, setup, preferred_location, use_write_global_endpoint, use_read_global_endpoint):

        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        regions = [REGION_1, REGION_2]
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(regions, use_write_global_endpoint, use_read_global_endpoint))
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=preferred_location)
            # this will setup the location cache
            client.client_connection._global_endpoint_manager.refresh_needed = True
            await client.client_connection._global_endpoint_manager.refresh_endpoint_list(None)
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
        expected_endpoints = []

        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        if not use_read_global_endpoint or not use_write_global_endpoint:
            expected_endpoints.append(locational_endpoint)


        unavailable_endpoint_info = client.client_connection._global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint
        assert len(unavailable_endpoint_info) == len(expected_endpoints)
        for expected_dual_endpoint in expected_endpoints:
            assert expected_dual_endpoint in unavailable_endpoint_info.keys()
        await client.close()

    async def test_health_check_background(self, setup):
        self.original_health_check = _global_endpoint_manager_async._GlobalEndpointManager._endpoints_health_check
        _global_endpoint_manager_async._GlobalEndpointManager._endpoints_health_check = self.mock_health_check
        start_time = time.time()
        try:
            for i in range(5):
                await setup[COLLECTION].create_item(body={'id': 'item' + str(uuid.uuid4()), 'pk': 'pk'})
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._endpoints_health_check = self.original_health_check
        end_time = time.time()
        duration = end_time - start_time
        assert duration < 2, f"Test took too long: {duration} seconds"

    # make background task fail, it shouldn't fail the test

    async def mock_health_check(self, **kwargs):
        await asyncio.sleep(100)

    class MockGetDatabaseAccountCheck(object):
        def __init__(self):
            self.counter = 0

        async def __call__(self, endpoint):
            locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(TestHealthCheckAsync.host, REGION_1)
            assert endpoint == locational_endpoint

            assert self.counter == 0

            self.counter += 1

    class MockGetDatabaseAccount(object):
        def __init__(
                self,
                regions: List[str],
                use_write_global_endpoint=False,
                use_read_global_endpoint=False,
        ):
            self.regions = regions
            self.use_write_global_endpoint= use_write_global_endpoint
            self.use_read_global_endpoint = use_read_global_endpoint

        async def __call__(self, endpoint):
            read_regions = self.regions
            read_locations = []
            counter = 0
            for loc in read_regions:
                locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(endpoint, loc)
                account_endpoint = TestHealthCheckAsync.host if self.use_read_global_endpoint and counter == 0 else locational_endpoint
                read_locations.append({'databaseAccountEndpoint': account_endpoint, 'name': loc})
                counter += 1
            write_regions = [self.regions[0]]
            write_locations = []
            for loc in write_regions:
                locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(endpoint, loc)
                account_endpoint = TestHealthCheckAsync.host if self.use_write_global_endpoint else locational_endpoint
                write_locations.append({'databaseAccountEndpoint': account_endpoint, 'name': loc})
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
