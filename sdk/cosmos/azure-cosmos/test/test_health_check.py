import unittest
from typing import List

import pytest
import test_config
from azure.cosmos import DatabaseAccount, _location_cache, CosmosClient, _global_endpoint_manager, \
    _cosmos_client_connection

from azure.cosmos._location_cache import DualEndpoint

COLLECTION = "created_collection"
REGION_1 = "East US"
REGION_2 = "West US"

@pytest.fixture()
def setup():
    if (TestHealthCheck.masterKey == '[YOUR_KEY_HERE]' or
            TestHealthCheck.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")

    client = CosmosClient(TestHealthCheck.host, TestHealthCheck.masterKey, consistency_level="Session")
    created_database = client.get_database_client(TestHealthCheck.TEST_DATABASE_ID)
    created_collection = created_database.get_container_client(TestHealthCheck.TEST_CONTAINER_SINGLE_PARTITION_ID)
    yield {
        COLLECTION: created_collection
    }

def health_check():
    # preferred_location, use_write_global_endpoint, use_read_global_endpoint
    return [
        ([REGION_1, REGION_2], True, True),
        ([REGION_1, REGION_2], False, True),
        ([REGION_1, REGION_2], True, False),
        ([REGION_1, REGION_2], False, False)
    ]

@pytest.mark.cosmosEmulator
@pytest.mark.unittest
@pytest.mark.usefixtures("setup")
class TestHealthCheck:
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID

    @pytest.mark.parametrize("preferred_location, use_write_global_endpoint, use_read_global_endpoint", health_check())
    def test_health_check_success(self, setup, preferred_location, use_write_global_endpoint, use_read_global_endpoint):

        self.original_getDatabaseAccountStub = _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_getDatabaseAccountCheck = _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck
        regions = [REGION_1, REGION_2]
        mock_get_database_account_check = self.MockGetDatabaseAccountCheck()
        _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(regions, use_write_global_endpoint, use_read_global_endpoint))
        _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck = mock_get_database_account_check
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=preferred_location)
        finally:
            _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck = self.original_getDatabaseAccountCheck
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

    @pytest.mark.parametrize("preferred_location, use_write_global_endpoint, use_read_global_endpoint", health_check())
    def test_health_check_failure(self, setup, preferred_location, use_write_global_endpoint, use_read_global_endpoint):

        self.original_getDatabaseAccountStub = _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub
        regions = [REGION_1, REGION_2]
        _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(regions, use_write_global_endpoint, use_read_global_endpoint))
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=preferred_location)
        finally:
            _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
        expected_endpoints = []

        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        if not use_read_global_endpoint or not use_write_global_endpoint:
            expected_endpoints.append(locational_endpoint)


        unavailable_endpoint_info = client.client_connection._global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint
        assert len(unavailable_endpoint_info) == len(expected_endpoints)
        for expected_dual_endpoint in expected_endpoints:
            assert expected_dual_endpoint in unavailable_endpoint_info.keys()


    class MockGetDatabaseAccountCheck(object):
        def __init__(self):
            self.counter = 0

        def __call__(self, endpoint):
            locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(TestHealthCheck.host, REGION_1)
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

        def __call__(self, endpoint):
            read_regions = self.regions
            read_locations = []
            counter = 0
            for loc in read_regions:
                locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(endpoint, loc)
                account_endpoint = TestHealthCheck.host if self.use_read_global_endpoint and counter == 0 else locational_endpoint
                read_locations.append({'databaseAccountEndpoint': account_endpoint, 'name': loc})
                counter += 1
            write_regions = [self.regions[0]]
            write_locations = []
            for loc in write_regions:
                locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(endpoint, loc)
                account_endpoint = TestHealthCheck.host if self.use_write_global_endpoint else locational_endpoint
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
