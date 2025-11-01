# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
from typing import List

import pytest
import pytest_asyncio
from azure.core.exceptions import ServiceRequestError

import test_config
from azure.cosmos import DatabaseAccount, _location_cache
from azure.cosmos._location_cache import RegionalRoutingContext

from azure.cosmos.aio import _global_endpoint_manager_async, _cosmos_client_connection_async, CosmosClient
from _fault_injection_transport_async import FaultInjectionTransportAsync
from azure.cosmos.exceptions import CosmosHttpResponseError
from test_circuit_breaker_emulator import COLLECTION
from test_effective_preferred_locations import REGION_1, REGION_2, REGION_3, ACCOUNT_REGIONS, construct_item, error


@pytest_asyncio.fixture()
async def setup():
    if (TestPreferredLocationsAsync.master_key == '[YOUR_KEY_HERE]' or
            TestPreferredLocationsAsync.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")

    client = CosmosClient(TestPreferredLocationsAsync.host, TestPreferredLocationsAsync.master_key, consistency_level="Session")
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

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestPreferredLocationsAsync:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID
    partition_key = test_config.TestConfig.TEST_CONTAINER_PARTITION_KEY

    async def setup_method_with_custom_transport(self, custom_transport, error_lambda, default_endpoint=host, **kwargs):
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               (FaultInjectionTransportAsync.predicate_targets_region(r, uri_down) or
                               FaultInjectionTransportAsync.predicate_targets_region(r, self.host)))
        custom_transport.add_fault(predicate,
                                   error_lambda)
        client = CosmosClient(default_endpoint,
                              self.master_key,
                              multiple_write_locations=True,
                              transport=custom_transport, **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        return {"client": client, "db": db, "col": container}

    @pytest.mark.cosmosEmulator
    @pytest.mark.parametrize("preferred_location, default_endpoint", preferred_locations())
    async def test_effective_preferred_regions_async(self, setup, preferred_location, default_endpoint):

        self.original_getDatabaseAccountStub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_getDatabaseAccountCheck = _cosmos_client_connection_async.CosmosClientConnection.health_check
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.MockGetDatabaseAccount(ACCOUNT_REGIONS)
        _cosmos_client_connection_async.CosmosClientConnection.health_check = self.MockGetDatabaseAccount(ACCOUNT_REGIONS)
        try:
            client = CosmosClient(default_endpoint, self.master_key, preferred_locations=preferred_location)
            # this will setup the location cache
            await client.__aenter__()
        finally:
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection_async.CosmosClientConnection.health_check = self.original_getDatabaseAccountCheck
        expected_endpoints = []

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
            expected_endpoints.append(RegionalRoutingContext(locational_endpoint))

        read_endpoints = client.client_connection._global_endpoint_manager.location_cache.read_regional_routing_contexts
        assert read_endpoints == expected_endpoints

    @pytest.mark.cosmosMultiRegion
    @pytest.mark.parametrize("error", error())
    async def test_read_no_preferred_locations_with_errors_async(self, setup, error):
        container = setup[COLLECTION]
        item_to_read = construct_item()
        await container.create_item(item_to_read)

        # setup fault injection so that first account region fails
        custom_transport = FaultInjectionTransportAsync()
        expected = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0,
            error
        ))
        try:
            fault_setup = await self.setup_method_with_custom_transport(custom_transport=custom_transport, error_lambda=error_lambda)
            fault_container = fault_setup["col"]
            response = await fault_container.read_item(item=item_to_read["id"], partition_key=item_to_read[self.partition_key])
            request = response.get_response_headers()["_request"]
            # Validate the response comes from another region meaning that the account locations were used
            assert request.url.startswith(expected)

            # should fail if using excluded locations because no where to failover to
            with pytest.raises(CosmosHttpResponseError):
                await fault_container.read_item(item=item_to_read["id"], partition_key=item_to_read[self.partition_key], excluded_locations=[REGION_2])

        finally:
            await fault_setup["client"].close()

    @pytest.mark.cosmosMultiRegion
    async def test_write_no_preferred_locations_with_errors_async(self, setup):
        # setup fault injection so that first account region fails
        custom_transport = FaultInjectionTransportAsync()
        expected = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_region_down())

        try:
            fault_setup = await self.setup_method_with_custom_transport(custom_transport=custom_transport, error_lambda=error_lambda)
            fault_container = fault_setup["col"]
            response = await fault_container.create_item(body=construct_item())
            request = response.get_response_headers()["_request"]
            # Validate the response comes from another region meaning that the account locations were used
            assert request.url.startswith(expected)

            # should fail if using excluded locations because no where to failover to
            with pytest.raises(ServiceRequestError):
                await fault_container.create_item(body=construct_item(), excluded_locations=[REGION_2])

        finally:
            await fault_setup["client"].close()

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
