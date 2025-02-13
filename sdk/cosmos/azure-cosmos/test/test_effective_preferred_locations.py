from typing import List

import pytest
import test_config
from azure.cosmos import DatabaseAccount, _location_cache, CosmosClient, _global_endpoint_manager, \
    _cosmos_client_connection

from azure.cosmos._location_cache import RegionalEndpoint

COLLECTION = "created_collection"
REGION_1 = "East US"
REGION_2 = "West US"
REGION_3 = "West US 2"
ACCOUNT_REGIONS = [REGION_1, REGION_2, REGION_3]

@pytest.fixture()
def setup():
    if (TestPreferredLocations.masterKey == '[YOUR_KEY_HERE]' or
            TestPreferredLocations.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")

    client = CosmosClient(TestPreferredLocations.host, TestPreferredLocations.masterKey, consistency_level="Session")
    created_database = client.get_database_client(TestPreferredLocations.TEST_DATABASE_ID)
    created_collection = created_database.get_container_client(TestPreferredLocations.TEST_CONTAINER_SINGLE_PARTITION_ID)
    yield {
        COLLECTION: created_collection
    }

def preferred_locations():
    return [([]), ([REGION_1, REGION_2]), ([REGION_1]), ([REGION_2, REGION_3]), ([REGION_1, REGION_2, REGION_3])]

@pytest.mark.cosmosEmulator
@pytest.mark.unittest
@pytest.mark.usefixtures("setup")
class TestPreferredLocations:
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID

    @pytest.mark.parametrize("preferred_location", preferred_locations())
    def test_effective_preferred_regions(self, setup, preferred_location):

        self.original_getDatabaseAccountStub = _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_getDatabaseAccountCheck = _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck
        _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.MockGetDatabaseAccount(ACCOUNT_REGIONS)
        _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck = self.MockGetDatabaseAccount(ACCOUNT_REGIONS)
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=preferred_location)
            # this will setup the location cache
            client.client_connection._global_endpoint_manager.force_refresh(None)
        finally:
            _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck = self.original_getDatabaseAccountCheck
        expected_dual_endpoints = []

        if preferred_location:
            expected_locations = preferred_location
        else:
            expected_locations = ACCOUNT_REGIONS

        for location in expected_locations:
            locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, location)
            expected_dual_endpoints.append(RegionalEndpoint(locational_endpoint, locational_endpoint))

        read_dual_endpoints = client.client_connection._global_endpoint_manager.location_cache.read_regional_endpoints
        assert read_dual_endpoints == expected_dual_endpoints

    class MockGetDatabaseAccount(object):
        def __init__(
                self,
                regions: List[str],
        ):
            self.regions = regions

        def __call__(self, endpoint):
            read_regions = self.regions
            read_locations = []
            counter = 0
            for loc in read_regions:
                locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(endpoint, loc)
                read_locations.append({'databaseAccountEndpoint': locational_endpoint, 'name': loc})
                counter += 1
            write_regions = [self.regions[0]]
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
