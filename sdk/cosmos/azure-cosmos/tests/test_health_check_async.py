# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
import time
import unittest
import uuid
from typing import List

import pytest
import pytest_asyncio
from azure.core.exceptions import ServiceRequestError

import test_config
from azure.cosmos import DatabaseAccount, _location_cache

from azure.cosmos._location_cache import RegionalRoutingContext
from azure.cosmos.aio import CosmosClient, _global_endpoint_manager_async, _cosmos_client_connection_async, \
    _retry_utility_async

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

@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestHealthCheckAsync:
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID

    async def test_health_check_success_startup_async(self, setup):
        # checks at startup that we perform a health check on all the necessary endpoints
        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_health_check = _cosmos_client_connection_async.CosmosClientConnection.health_check
        mock_health_check = self.MockHealthCheckProbe()
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(REGIONS))
        _cosmos_client_connection_async.CosmosClientConnection.health_check = mock_health_check
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=REGIONS)
            # this will setup the location cache
            await client.__aenter__()
            await asyncio.sleep(10) # give some time for the background health check to complete
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection_async.CosmosClientConnection.health_check = self.original_health_check
        expected_regional_routing_context = []

        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        assert mock_health_check.counter == 2
        endpoint = locational_endpoint
        expected_regional_routing_context.append(RegionalRoutingContext(endpoint))
        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        expected_regional_routing_context.append(RegionalRoutingContext(locational_endpoint))
        read_regional_routing_context = client.client_connection._global_endpoint_manager.location_cache.read_regional_routing_contexts
        assert read_regional_routing_context == expected_regional_routing_context
        await client.close()

    async def test_health_check_failure_startup_async(self, setup):
        # checks at startup that the health check will mark endpoints as unavailable if it gets an error
        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(REGIONS))
        # don't mock database account check because we want it to fail and the emulator doesn't have extra regions
        try:
            client = CosmosClient(self.host, self.masterKey, preferred_locations=REGIONS)
            # this will setup the location cache
            await client.__aenter__()
            await asyncio.sleep(10) # give some time for the background health check to complete
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
        expected_endpoints = []

        for region in REGIONS:
            locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, region)
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

    async def test_health_check_success_async(self, setup):
        # checks the background health check works as expected when all endpoints healthy
        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_health_check = _cosmos_client_connection_async.CosmosClientConnection.health_check
        self.original_preferred_locations = setup[COLLECTION].client_connection.connection_policy.PreferredLocations
        setup[COLLECTION].client_connection.connection_policy.PreferredLocations = REGIONS
        mock_get_database_account_check = self.MockHealthCheckProbe()
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(REGIONS))
        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _cosmos_client_connection_async.CosmosClientConnection.health_check = mock_get_database_account_check
        async def mock_execute_function(function, *args, **kwargs):
            if args:
                args[4].url = args[4].url.replace('-eastus', '').replace('-westus', '')
                args[1].location_endpoint_to_route = args[1].location_endpoint_to_route.replace('-eastus', '').replace('-westus', '')
                if args[1].endpoint_override:
                    args[1].endpoint_override = args[1].endpoint_override.replace('-eastus', '').replace('-westus', '')
            return await self.OriginalExecuteFunction(function, *args, **kwargs)
        _retry_utility_async.ExecuteFunctionAsync = mock_execute_function

        try:
            setup[COLLECTION].client_connection._global_endpoint_manager.startup = False
            setup[COLLECTION].client_connection._global_endpoint_manager.refresh_needed = True
            for i in range(2):
                await setup[COLLECTION].create_item(body={'id': 'item' + str(uuid.uuid4()), 'pk': 'pk'})
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection_async.CosmosClientConnection.health_check = self.original_health_check
            setup[COLLECTION].client_connection.connection_policy.PreferredLocations = self.original_preferred_locations
            _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        expected_regional_routing_contexts = []

        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)

        assert mock_get_database_account_check.counter == 2
        expected_regional_routing_contexts.append(RegionalRoutingContext(locational_endpoint))
        locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        expected_regional_routing_contexts.append(RegionalRoutingContext(locational_endpoint))
        read_regional_routing_context = setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.read_regional_routing_contexts
        assert read_regional_routing_context == expected_regional_routing_contexts


    async def test_health_check_failure_async(self, setup):
        # checks the background health check works as expected when all endpoints unhealthy - it should mark the endpoints unavailable
        setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint.clear()
        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = (
            self.MockGetDatabaseAccount(REGIONS))
        self.original_health_check = _cosmos_client_connection_async.CosmosClientConnection.health_check
        self.original_preferred_locations = setup[COLLECTION].client_connection.connection_policy.PreferredLocations
        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        mock_health_check_error = self.MockHealthCheckError()
        _cosmos_client_connection_async.CosmosClientConnection.health_check = mock_health_check_error
        setup[COLLECTION].client_connection.connection_policy.PreferredLocations = REGIONS
        async def mock_execute_function(function, *args, **kwargs):
            if args:
                args[4].url = args[4].url.replace('-eastus', '').replace('-westus', '')
                args[1].location_endpoint_to_route = args[1].location_endpoint_to_route.replace('-eastus', '').replace('-westus', '')
                if args[1].endpoint_override:
                    args[1].endpoint_override = args[1].endpoint_override.replace('-eastus', '').replace('-westus', '')
            return await self.OriginalExecuteFunction(function, *args, **kwargs)

        _retry_utility_async.ExecuteFunctionAsync = mock_execute_function

        try:
            setup[COLLECTION].client_connection._global_endpoint_manager.startup = False
            setup[COLLECTION].client_connection._global_endpoint_manager.refresh_needed = True
            # Trigger the background health check
            await setup[COLLECTION].create_item(body={'id': 'item' + str(uuid.uuid4()), 'pk': 'pk'})

            # Poll until the background task marks the endpoints as unavailable
            start_time = time.time()
            while (len(setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) < len(
                    REGIONS) and time.time() - start_time < 10):
                await asyncio.sleep(0.1)
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            setup[COLLECTION].client_connection.connection_policy.PreferredLocations = self.original_preferred_locations
            _cosmos_client_connection_async.CosmosClientConnection.health_check = self.original_health_check
            _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction

        num_unavailable_endpoints = len(REGIONS)
        unavailable_endpoint_info = setup[COLLECTION].client_connection._global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint
        assert len(unavailable_endpoint_info) == num_unavailable_endpoints
        write_endpoints = {
            _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        }

        for endpoint, info in unavailable_endpoint_info.items():
            assert _location_cache.EndpointOperationType.ReadType in info["operationType"]
            if endpoint in write_endpoints:
                assert _location_cache.EndpointOperationType.WriteType in info["operationType"]
            else:
                assert _location_cache.EndpointOperationType.WriteType not in info["operationType"]

    async def mock_health_check(self, **kwargs):
        await asyncio.sleep(100)

    async def mock_health_check_failure(self, **kwargs):
        await asyncio.sleep(1)
        raise Exception("Mock health check failure")

    class MockHealthCheckProbe(object):
        def __init__(self):
            self.counter = 0
            self.index = 0

        async def __call__(self, endpoint):
            self.index += 1
            self.counter += 1

    class MockHealthCheckError(object):
        async def __call__(self, endpoint):
            raise ServiceRequestError("Mock health check failure")

    class MockGetDatabaseAccount(object):
        def __init__(
                self,
                regions: List[str],
        ):
            self.regions = regions

        async def __call__(self, endpoint):
            read_regions = self.regions
            read_locations = []
            for loc in read_regions:
                locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(endpoint, loc)
                account_endpoint = locational_endpoint
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

if __name__ == '__main__':
    unittest.main()
