# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
import time
import unittest
import uuid
from typing import List

import pytest
import pytest_asyncio
import test_config
from azure.cosmos import DatabaseAccount, _location_cache

from azure.cosmos._location_cache import RegionalRoutingContext
from azure.cosmos.aio import CosmosClient, _global_endpoint_manager_async, _cosmos_client_connection_async

COLLECTION = "created_collection"
REGION_1 = "East US"
REGION_2 = "West US"
REGIONS = [REGION_1, REGION_2]

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
        (REGIONS, True, True),
        (REGIONS, False, True),
        (REGIONS, True, False),
        (REGIONS, False, False)
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
    # health check in all these tests should check the endpoints for the first two write regions and the first two read regions
    # without checking the same endpoint twice

    @pytest.mark.parametrize("preferred_location, use_write_global_endpoint, use_read_global_endpoint", health_check())
    async def test_health_check_success_startup_async(self, setup, preferred_location, use_write_global_endpoint, use_read_global_endpoint):
        # checks at startup that we perform a health check on all the necessary endpoints
        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_getDatabaseAccountCheck = _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck
        mock_get_database_account_check = self.MockGetDatabaseAccountCheck()
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(REGIONS, use_write_global_endpoint, use_read_global_endpoint))
        _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck = mock_get_database_account_check
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=preferred_location)
            # this will setup the location cache
            client.client_connection._global_endpoint_manager.refresh_needed = True
            await client.client_connection._global_endpoint_manager.refresh_endpoint_list(None)
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck = self.original_getDatabaseAccountCheck
        expected_regional_routing_context = []

        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        if use_read_global_endpoint:
            assert mock_get_database_account_check.counter == 1
        else:
            assert mock_get_database_account_check.counter == 2
        endpoint = self.host if use_read_global_endpoint else locational_endpoint
        expected_regional_routing_context.append(RegionalRoutingContext(endpoint, endpoint))
        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        expected_regional_routing_context.append(RegionalRoutingContext(locational_endpoint, locational_endpoint))
        read_regional_routing_context = client.client_connection._global_endpoint_manager.location_cache.read_regional_routing_contexts
        assert read_regional_routing_context == expected_regional_routing_context
        await client.close()

    @pytest.mark.parametrize("preferred_location, use_write_global_endpoint, use_read_global_endpoint", health_check())
    async def test_health_check_failure_startup_async(self, setup, preferred_location, use_write_global_endpoint, use_read_global_endpoint):
        # checks at startup that the health check will mark endpoints as unavailable if it gets an error
        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(REGIONS, use_write_global_endpoint, use_read_global_endpoint))
        # don't mock database account check because we want it to fail and the emulator doesn't have extra regions
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=preferred_location)
            # this will setup the location cache
            client.client_connection._global_endpoint_manager.refresh_needed = True
            await client.client_connection._global_endpoint_manager.refresh_endpoint_list(None)
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
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
        for expected_endpoint in expected_endpoints:
            assert expected_endpoint in unavailable_endpoint_info.keys()
        await client.close()

    async def test_health_check_background(self, setup):
        # makes sure the health check is in the background and doesn't block by mocking it with a large sleep value
        self.original_health_check = _global_endpoint_manager_async._GlobalEndpointManager._endpoints_health_check
        _global_endpoint_manager_async._GlobalEndpointManager._endpoints_health_check = self.mock_health_check
        start_time = time.time()
        try:
            setup[COLLECTION].client_connection._global_endpoint_manager.startup = False
            for i in range(5):
                await setup[COLLECTION].create_item(body={'id': 'item' + str(uuid.uuid4()), 'pk': 'pk'})
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._endpoints_health_check = self.original_health_check
        end_time = time.time()
        duration = end_time - start_time
        assert duration < 2, f"Test took too long: {duration} seconds"

    async def test_health_check_background_fail(self, setup):
        # makes sure exceptions in the health check aren't bubbled up but swallowed
        #  by mocking health check with an error
        self.original_health_check = _global_endpoint_manager_async._GlobalEndpointManager._endpoints_health_check
        _global_endpoint_manager_async._GlobalEndpointManager._endpoints_health_check = self.mock_health_check_failure
        try:
            setup[COLLECTION].client_connection._global_endpoint_manager.startup = False
            for i in range(20):
                await setup[COLLECTION].create_item(body={'id': 'item' + str(uuid.uuid4()), 'pk': 'pk'})
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._endpoints_health_check = self.original_health_check

    @pytest.mark.parametrize("preferred_location, use_write_global_endpoint, use_read_global_endpoint", health_check())
    async def test_health_check_success(self, setup, preferred_location, use_write_global_endpoint, use_read_global_endpoint):
        # checks the background health check works as expected when all endpoints healthy
        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_getDatabaseAccountCheck = _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck
        self.original_preferred_locations = setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.preferred_locations
        setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.preferred_locations = preferred_location
        mock_get_database_account_check = self.MockGetDatabaseAccountCheck()
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(REGIONS, use_write_global_endpoint, use_read_global_endpoint))
        _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck = mock_get_database_account_check

        try:
            setup[COLLECTION].client_connection._global_endpoint_manager.startup = False
            setup[COLLECTION].client_connection._global_endpoint_manager.refresh_needed = True
            for i in range(2):
                await setup[COLLECTION].create_item(body={'id': 'item' + str(uuid.uuid4()), 'pk': 'pk'})
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection_async.CosmosClientConnection._GetDatabaseAccountCheck = self.original_getDatabaseAccountCheck
            setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.preferred_locations = self.original_preferred_locations
        expected_regional_routing_contexts = []

        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)

        assert mock_get_database_account_check.counter > 0
        endpoint = self.host if use_read_global_endpoint else locational_endpoint
        expected_regional_routing_contexts.append(RegionalRoutingContext(endpoint, endpoint))
        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        expected_regional_routing_contexts.append(RegionalRoutingContext(locational_endpoint, locational_endpoint))
        read_regional_routing_context = setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.read_regional_routing_contexts
        assert read_regional_routing_context == expected_regional_routing_contexts


    @pytest.mark.parametrize("preferred_location, use_write_global_endpoint, use_read_global_endpoint", health_check())
    async def test_health_check_failure(self, setup, preferred_location, use_write_global_endpoint, use_read_global_endpoint):
        # checks the background health check works as expected when all endpoints unhealthy - it should mark the endpoints unavailable
        setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint.clear()
        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(REGIONS, use_write_global_endpoint, use_read_global_endpoint))
        self.original_preferred_locations = setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.preferred_locations
        setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.preferred_locations = preferred_location

        try:
            setup[COLLECTION].client_connection._global_endpoint_manager.startup = False
            setup[COLLECTION].client_connection._global_endpoint_manager.refresh_needed = True
            for i in range(2):
                await setup[COLLECTION].create_item(body={'id': 'item' + str(uuid.uuid4()), 'pk': 'pk'})
                # wait for background task to finish
                await asyncio.sleep(1)
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.preferred_locations = self.original_preferred_locations

        if not use_write_global_endpoint:
            num_unavailable_endpoints = len(REGIONS)
        else:
            num_unavailable_endpoints = 1

        unavailable_endpoint_info = setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint
        assert len(unavailable_endpoint_info) == num_unavailable_endpoints

    async def mock_health_check(self, **kwargs):
        await asyncio.sleep(100)

    async def mock_health_check_failure(self, **kwargs):
        await asyncio.sleep(1)
        raise Exception("Mock health check failure")

    class MockGetDatabaseAccountCheck(object):
        def __init__(self):
            self.counter = 0
            self.index = 0

        async def __call__(self, endpoint):
            self.index += 1
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
