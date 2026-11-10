# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid
from time import sleep
from typing import List
from unittest.mock import patch

import pytest
import test_config
from azure.cosmos import (
    DatabaseAccount,
    documents,
    _location_cache,
    CosmosClient,
    _global_endpoint_manager,
    _cosmos_client_connection,
)

from azure.cosmos._location_cache import RegionalRoutingContext

COLLECTION = "created_collection"
REGION_1 = "East US"
REGION_2 = "West US"
REGIONS = [REGION_1, REGION_2]


def _assert_startup_health_checks(probe, connection, expected_endpoints):
    endpoints = [call.args[1] for call in probe.call_args_list if call.args[0] is connection]
    assert len(endpoints) == 2, [(id(call.args[0]), call.args[1]) for call in probe.call_args_list]
    assert set(endpoints) == set(expected_endpoints)


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

    def test_health_check_success(self, setup):
        # checks at startup that we perform a health check on all the necessary endpoints
        with patch.object(
            _global_endpoint_manager._GlobalEndpointManager,
            "_GetDatabaseAccountStub",
            self.MockGetDatabaseAccount(REGIONS),
        ), patch.object(_cosmos_client_connection.CosmosClientConnection, "health_check", autospec=True) as probe:
            with CosmosClient(self.host, self.masterKey, preferred_locations=REGIONS) as client:
                manager = client.client_connection._global_endpoint_manager
                assert manager._refresh_thread is not None
                manager._refresh_thread.join(timeout=3)
                assert not manager._refresh_thread.is_alive()
                endpoints = [
                    _location_cache.LocationCache.GetLocationalEndpoint(self.host, region) for region in REGIONS
                ]
                _assert_startup_health_checks(probe, client.client_connection, endpoints)
                assert manager.location_cache.read_regional_routing_contexts == [
                    RegionalRoutingContext(endpoint) for endpoint in endpoints
                ]

    def test_health_check_failure(self, setup):
        # checks at startup that the health check will mark endpoints as unavailable if it gets an error
        self.original_getDatabaseAccountStub = _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub
        _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(REGIONS))
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=REGIONS)
            # give some time for the health check to finish
            sleep(10)
        finally:
            _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
        expected_endpoints = []

        for region in REGIONS:
            locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, region)
            expected_endpoints.append(locational_endpoint)

        unavailable_endpoint_info = client.client_connection._global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint
        assert len(unavailable_endpoint_info) == len(expected_endpoints)
        for expected_regional_routing_contexts in expected_endpoints:
            assert expected_regional_routing_contexts in unavailable_endpoint_info.keys()

    def test_health_check_timeouts_on_unavailable_endpoints(self, setup):
        # checks that the health check changes the timeouts when the endpoints were previously unavailable
        self.original_getDatabaseAccountStub = _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_health_check = _cosmos_client_connection.CosmosClientConnection.health_check
        mock_health_check = self.MockHealthCheckProbe(setup[COLLECTION].client_connection, True)
        _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(REGIONS))
        _cosmos_client_connection.CosmosClientConnection.health_check = mock_health_check
        setup[COLLECTION].client_connection._global_endpoint_manager.refreshed_needed = True
        # mark endpoint as unavailable for read
        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(TestHealthCheck.host, REGION_1)
        setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.mark_endpoint_unavailable_for_read(
            locational_endpoint, True)
        self.original_preferred_locations = setup[COLLECTION].client_connection.connection_policy.PreferredLocations
        setup[COLLECTION].client_connection.connection_policy.PreferredLocations = REGIONS
        try:
            setup[COLLECTION].create_item(body={'id': 'item' + str(uuid.uuid4()), 'pk': 'pk'})
        finally:
            _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection.CosmosClientConnection.health_check = self.original_health_check
            setup[COLLECTION].client_connection.connection_policy.PreferredLocations = self.original_preferred_locations

    class MockHealthCheckProbe(object):
        def __init__(self, client_connection=None, endpoint_unavailable=False):
            self.counter = 0
            self.client_connection = client_connection


        def __call__(self, endpoint):
            self.counter += 1

    class MockGetDatabaseAccount(object):
        def __init__(
                self,
                regions: List[str],
        ):
            self.regions = regions

        def __call__(self, endpoint):
            read_regions = self.regions
            read_locations = []
            for loc in read_regions:
                locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(endpoint, loc)
                account_endpoint =  locational_endpoint
                read_locations.append({'databaseAccountEndpoint': account_endpoint, 'name': loc})
            write_regions = [self.regions[0]]
            write_locations = []
            for loc in write_regions:
                locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(endpoint, loc)
                account_endpoint = locational_endpoint
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


    def test_force_refresh_on_startup_with_none_should_fetch_database_account(self, setup):
        """Verifies that calling force_refresh_on_startup(None) fetches the database account
        instead of crashing with AttributeError on NoneType._WritableLocations.
        """
        self.original_getDatabaseAccountStub = _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub
        mock_get_db_account = self.MockGetDatabaseAccount(REGIONS)
        _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = mock_get_db_account

        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=REGIONS)
            gem = client.client_connection._global_endpoint_manager

            # Simulate the startup state
            gem.startup = True
            gem.refresh_needed = True

            # This should NOT crash - it should fetch the database account
            gem.force_refresh_on_startup(None)

            # Verify the location cache was properly populated
            read_contexts = gem.location_cache.read_regional_routing_contexts
            assert len(read_contexts) > 0, "Location cache should have read endpoints after startup refresh"

        finally:
            _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub

    def test_force_refresh_on_startup_with_valid_account_uses_provided_account(self, setup):
        """Verifies that when a valid database account is provided to force_refresh_on_startup,
        it uses that account directly without making another network call.
        """
        self.original_getDatabaseAccountStub = _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub
        call_counter = {'count': 0}

        def counting_mock(self_gem, endpoint, **kwargs):
            call_counter['count'] += 1
            return self.MockGetDatabaseAccount(REGIONS)(endpoint)

        _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = counting_mock

        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=REGIONS)
            gem = client.client_connection._global_endpoint_manager

            # Get a valid database account first
            db_account = gem._GetDatabaseAccount()
            initial_call_count = call_counter['count']

            # Reset startup state
            gem.startup = True
            gem.refresh_needed = True

            # Call with valid account - should NOT make another network call
            gem.force_refresh_on_startup(db_account)

            # Since we provided a valid account, no additional GetDatabaseAccount call should be made
            assert call_counter['count'] == initial_call_count, \
                "Should not call _GetDatabaseAccount when valid account is provided"

        finally:
            _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub


@pytest.mark.cosmosEmulator
@pytest.mark.unittest
def test_health_check_probe_isolation():
    connections = []
    managers = []
    try:
        for regions in (REGIONS, [REGION_1]):
            connection = object.__new__(_cosmos_client_connection.CosmosClientConnection)
            connection.connection_policy = documents.ConnectionPolicy()
            connection.connection_policy.PreferredLocations = regions
            connection.url_connection = test_config.TestConfig.host
            connections.append(connection)
            managers.append(_global_endpoint_manager._GlobalEndpointManager(connection))

        with patch.object(_cosmos_client_connection.CosmosClientConnection, "health_check", autospec=True) as probe:
            for manager, regions in zip(managers, (REGIONS, [REGION_1])):
                account = TestHealthCheck.MockGetDatabaseAccount(regions)(manager.DefaultEndpoint)
                manager.force_refresh_on_startup(account)
            for manager in managers:
                assert manager._refresh_thread is not None
                manager._refresh_thread.join(timeout=3)
                assert not manager._refresh_thread.is_alive()

            endpoints = [
                _location_cache.LocationCache.GetLocationalEndpoint(test_config.TestConfig.host, region)
                for region in REGIONS
            ]
            assert len(probe.call_args_list) == 3
            _assert_startup_health_checks(probe, connections[0], endpoints)

            connections[0].health_check(endpoints[0])
            with pytest.raises(AssertionError):
                _assert_startup_health_checks(probe, connections[0], endpoints)
    finally:
        for manager in managers:
            manager.executor.shutdown(wait=False, cancel_futures=True)


if __name__ == '__main__':
    unittest.main()
