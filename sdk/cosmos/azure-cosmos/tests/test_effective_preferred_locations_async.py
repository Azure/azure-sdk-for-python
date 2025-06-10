from typing import List

import pytest
import pytest_asyncio

import test_config
from azure.cosmos import DatabaseAccount, _location_cache

from azure.cosmos._location_cache import RegionalEndpoint
from azure.cosmos.aio import _global_endpoint_manager_async, _cosmos_client_connection_async, CosmosClient

COLLECTION = "created_collection"
REGION_1 = "East US"
REGION_2 = "West US"
REGION_3 = "West US 2"
ACCOUNT_REGIONS = [REGION_1, REGION_2, REGION_3]

@pytest_asyncio.fixture()
async def setup():
    if (TestPreferredLocationsAsync.masterKey == '[YOUR_KEY_HERE]' or
            TestPreferredLocationsAsync.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")

    client = CosmosClient(TestPreferredLocationsAsync.host, TestPreferredLocationsAsync.masterKey, consistency_level="Session")
    created_database = client.get_database_client(TestPreferredLocationsAsync.TEST_DATABASE_ID)
    created_collection = created_database.get_container_client(TestPreferredLocationsAsync.TEST_CONTAINER_SINGLE_PARTITION_ID)
    yield {
        COLLECTION: created_collection
    }
    await client.close()

def preferred_locations():
    host = test_config.TestConfig.host
    locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(host, REGION_2)
    return [
        ([], host),
        ([REGION_1, REGION_2], host),
        ([REGION_1], host),
        ([REGION_2, REGION_3], host),
        ([REGION_1, REGION_2, REGION_3], host),
        ([], locational_endpoint),
        ([REGION_2], locational_endpoint),
        ([REGION_3, REGION_1], locational_endpoint),
        ([REGION_1, REGION_3], locational_endpoint),
        ([REGION_1, REGION_2, REGION_3], locational_endpoint)
    ]

@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestPreferredLocationsAsync:
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID

    @pytest.mark.parametrize("preferred_location, default_endpoint", preferred_locations())
    async def test_effective_preferred_regions_async(self, setup, preferred_location, default_endpoint):

        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_getDatabaseAccountCheck = _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.MockGetDatabaseAccount(ACCOUNT_REGIONS)
        _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck = self.MockGetDatabaseAccount(ACCOUNT_REGIONS)
        try:
            client = CosmosClient(default_endpoint, self.masterKey, preferred_locations=preferred_location)
            # this will setup the location cache
            await client.client_connection._global_endpoint_manager.force_refresh(None)
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck = self.original_getDatabaseAccountCheck
        expected_dual_endpoints = []

        # if preferred location set should use that
        if preferred_location:
            expected_locations = preferred_location
        # if client created with regional endpoint preferred locations, only use hub region
        elif default_endpoint != self.host:
            expected_locations = ACCOUNT_REGIONS[:1]
        # if client created with global endpoint and no preferred locations, use all regions
        else:
            expected_locations = ACCOUNT_REGIONS

        for location in expected_locations:
            locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, location)
            if default_endpoint == self.host or preferred_location:
                expected_dual_endpoints.append(RegionalEndpoint(locational_endpoint, locational_endpoint))
            else:
                expected_dual_endpoints.append(RegionalEndpoint(locational_endpoint, default_endpoint))

        read_dual_endpoints = client.client_connection._global_endpoint_manager.location_cache.read_regional_endpoints
        assert read_dual_endpoints == expected_dual_endpoints

    class MockGetDatabaseAccount(object):
        def __init__(
                self,
                regions: List[str],
        ):
            self.regions = regions

        async def __call__(self, endpoint):
            read_regions = self.regions
            read_locations = []
            counter = 0
            for loc in read_regions:
                locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(TestPreferredLocationsAsync.host, loc)
                read_locations.append({'databaseAccountEndpoint': locational_endpoint, 'name': loc})
                counter += 1
            write_regions = [self.regions[0]]
            write_locations = []
            for loc in write_regions:
                locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(TestPreferredLocationsAsync.host, loc)
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
