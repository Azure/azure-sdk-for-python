# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid
from typing import List

import pytest
import test_config
from azure.cosmos import DatabaseAccount, _location_cache, CosmosClient, _global_endpoint_manager, \
    _cosmos_client_connection

from azure.cosmos._location_cache import RegionalRoutingContext

COLLECTION = "created_collection"
REGION_1 = "East US"
REGION_2 = "West US"
REGIONS = [REGION_1, REGION_2]

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
        (REGIONS, True, True),
        (REGIONS, False, True),
        (REGIONS, True, False),
        (REGIONS, False, False)
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
    # health check in all these tests should check the endpoints for the first two write regions and the first two read regions
    # without checking the same endpoint twice

    @pytest.mark.parametrize("preferred_location, use_write_global_endpoint, use_read_global_endpoint", health_check())
    def test_health_check_success(self, setup, preferred_location, use_write_global_endpoint, use_read_global_endpoint):
        # checks at startup that we perform a health check on all the necessary endpoints
        self.original_getDatabaseAccountStub = _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_getDatabaseAccountCheck = _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck
        mock_get_database_account_check = self.MockGetDatabaseAccountCheck()
        _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(REGIONS, use_write_global_endpoint, use_read_global_endpoint))
        _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck = mock_get_database_account_check
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=preferred_location)
            # this will setup the location cache
            client.client_connection._global_endpoint_manager.refresh_needed = True
            client.client_connection._global_endpoint_manager.refresh_endpoint_list(None)
        finally:
            _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck = self.original_getDatabaseAccountCheck
        expected_regional_routing_contexts = []

        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        if use_read_global_endpoint:
            assert mock_get_database_account_check.counter == 1
        else:
            assert mock_get_database_account_check.counter == 2
        endpoint = self.host if use_read_global_endpoint else locational_endpoint
        expected_regional_routing_contexts.append(RegionalRoutingContext(endpoint, endpoint))
        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        expected_regional_routing_contexts.append(RegionalRoutingContext(locational_endpoint, locational_endpoint))
        read_regional_routing_contexts = client.client_connection._global_endpoint_manager.location_cache.read_regional_routing_contexts
        assert read_regional_routing_contexts == expected_regional_routing_contexts

    @pytest.mark.parametrize("preferred_location, use_write_global_endpoint, use_read_global_endpoint", health_check())
    def test_health_check_failure(self, setup, preferred_location, use_write_global_endpoint, use_read_global_endpoint):
        # checks at startup that the health check will mark endpoints as unavailable if it gets an error
        self.original_getDatabaseAccountStub = _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub
        _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(REGIONS, use_write_global_endpoint, use_read_global_endpoint))
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=preferred_location)
            # this will setup the location cache
            client.client_connection._global_endpoint_manager.refresh_needed = True
            client.client_connection._global_endpoint_manager.refresh_endpoint_list(None)
        finally:
            _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
        expected_endpoints = []

        if not use_read_global_endpoint:
            for region in REGIONS:
                locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, region)
                expected_endpoints.append(locational_endpoint)
        else:
            locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
            expected_endpoints.append(locational_endpoint)

        unavailable_endpoint_info = client.client_connection._global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint
        assert len(unavailable_endpoint_info) == len(expected_endpoints)
        for expected_regional_routing_contexts in expected_endpoints:
            assert expected_regional_routing_contexts in unavailable_endpoint_info.keys()

    def test_health_check_timeouts_on_unavailable_endpoints(self, setup):
        # checks that the health check changes the timeouts when the endpoints were previously unavailable
        self.original_getDatabaseAccountStub = _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_getDatabaseAccountCheck = _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck
        mock_get_database_account_check = self.MockGetDatabaseAccountCheck(setup[COLLECTION].client_connection, True)
        _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(REGIONS, False, False))
        _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck = mock_get_database_account_check
        setup[COLLECTION].client_connection._global_endpoint_manager.refreshed_needed = True
        # mark endpoint as unavailable for read
        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(TestHealthCheck.host, REGION_1)
        setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.mark_endpoint_unavailable_for_read(
            locational_endpoint, True)
        self.original_preferred_locations = setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.preferred_locations
        setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.preferred_locations = REGIONS
        try:
            setup[COLLECTION].create_item(body={'id': 'item' + str(uuid.uuid4()), 'pk': 'pk'})
        finally:
            _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck = self.original_getDatabaseAccountCheck
            setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.preferred_locations = self.original_preferred_locations

    class MockGetDatabaseAccountCheck(object):
        def __init__(self, client_connection=None, endpoint_unavailable=False):
            self.counter = 0
            self.client_connection = client_connection
            self.endpoint_unavailable = endpoint_unavailable
            self.index = 0


        def __call__(self, endpoint):
            if self.endpoint_unavailable:
                assert self.client_connection.connection_policy.DBAReadTimeout == 1
            self.index -= 1
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
