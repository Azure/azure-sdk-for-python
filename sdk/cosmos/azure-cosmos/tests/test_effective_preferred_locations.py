# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import uuid
from typing import List

import pytest
from azure.core.exceptions import ServiceRequestError

import test_config
from azure.cosmos import DatabaseAccount, _location_cache, CosmosClient, _global_endpoint_manager, \
    _cosmos_client_connection
from azure.cosmos._location_cache import RegionalRoutingContext
from _fault_injection_transport import FaultInjectionTransport
from azure.cosmos.exceptions import CosmosHttpResponseError

COLLECTION = "created_collection"
REGION_1 = test_config.TestConfig.WRITE_LOCATION
REGION_2 = test_config.TestConfig.READ_LOCATION
REGION_3 = "West US 2"
ACCOUNT_REGIONS = [REGION_1, REGION_2, REGION_3]

@pytest.fixture()
def setup():
    if (TestPreferredLocations.master_key == '[YOUR_KEY_HERE]' or
            TestPreferredLocations.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")

    client = CosmosClient(TestPreferredLocations.host, TestPreferredLocations.master_key, consistency_level="Session")
    created_database = client.get_database_client(TestPreferredLocations.TEST_DATABASE_ID)
    created_collection = created_database.get_container_client(TestPreferredLocations.TEST_CONTAINER_SINGLE_PARTITION_ID)
    yield {
        COLLECTION: created_collection
    }

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

def construct_item():
    return {
        "id": "test_item_no_preferred_locations" + str(uuid.uuid4()),
        test_config.TestConfig.TEST_CONTAINER_PARTITION_KEY: str(uuid.uuid4())
    }

def error():
    status_codes = [503, 408, 404]
    sub_status = [0, 0, 1002]
    errors = []
    for i, status_code in enumerate(status_codes):
        errors.append(CosmosHttpResponseError(
            status_code=status_code,
            message=f"Error with status code {status_code} and substatus {sub_status[i]}",
            sub_status=sub_status[i]
        ))
    return errors

@pytest.mark.unittest
@pytest.mark.usefixtures("setup")
class TestPreferredLocations:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID
    partition_key = test_config.TestConfig.TEST_CONTAINER_PARTITION_KEY

    def setup_method_with_custom_transport(self, custom_transport, error_lambda, default_endpoint=host, **kwargs):
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        predicate = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                               (FaultInjectionTransport.predicate_targets_region(r, uri_down) or
                                FaultInjectionTransport.predicate_targets_region(r, default_endpoint)) and
                               not FaultInjectionTransport.predicate_is_operation_type(r, "ReadFeed")
                               )

        custom_transport.add_fault(predicate,
                                   error_lambda)
        client = CosmosClient(default_endpoint,
                              self.master_key,
                              multiple_write_locations=True,
                              transport=custom_transport, consistency_level="Session", **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        return {"client": client, "db": db, "col": container}

    @pytest.mark.cosmosEmulator
    @pytest.mark.parametrize("preferred_location, default_endpoint", preferred_locations())
    def test_effective_preferred_regions(self, setup, preferred_location, default_endpoint):

        self.original_getDatabaseAccountStub = _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_getDatabaseAccountCheck = _cosmos_client_connection.CosmosClientConnection.health_check
        _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.MockGetDatabaseAccount(ACCOUNT_REGIONS)
        _cosmos_client_connection.CosmosClientConnection.health_check = self.MockGetDatabaseAccount(ACCOUNT_REGIONS)
        try:
            client = CosmosClient(default_endpoint, self.master_key, preferred_locations=preferred_location)
            # this will setup the location cache
            client.client_connection._global_endpoint_manager.force_refresh_on_startup(None)
        finally:
            _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection.CosmosClientConnection.health_check = self.original_getDatabaseAccountCheck
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
    def test_read_no_preferred_locations_with_errors(self, setup, error):
        container = setup[COLLECTION]
        item_to_read = construct_item()
        container.create_item(item_to_read)

        # setup fault injection so that first account region fails
        custom_transport = FaultInjectionTransport()
        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            0,
            error
        )
        expected = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        fault_setup = self.setup_method_with_custom_transport(custom_transport=custom_transport, error_lambda=error_lambda)
        fault_container = fault_setup["col"]
        response = fault_container.read_item(item=item_to_read["id"], partition_key=item_to_read[self.partition_key])
        request = response.get_response_headers()["_request"]
        # Validate the response comes from another region meaning that the account locations were used
        assert request.url.startswith(expected)

        # should fail if using excluded locations because no where to failover to
        with pytest.raises(CosmosHttpResponseError):
            fault_container.read_item(item=item_to_read["id"], partition_key=item_to_read[self.partition_key], excluded_locations=[REGION_2])

    @pytest.mark.cosmosMultiRegion
    def test_write_no_preferred_locations_with_errors(self, setup):
        # setup fault injection so that first account region fails
        custom_transport = FaultInjectionTransport()
        expected = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        error_lambda = lambda r: FaultInjectionTransport.error_region_down()

        fault_setup = self.setup_method_with_custom_transport(custom_transport=custom_transport, error_lambda=error_lambda)
        fault_container = fault_setup["col"]
        response = fault_container.create_item(body=construct_item())
        request = response.get_response_headers()["_request"]
        # Validate the response comes from another region meaning that the account locations were used
        assert request.url.startswith(expected)

        # should fail if using excluded locations because no where to failover to
        with pytest.raises(ServiceRequestError):
            fault_container.create_item(body=construct_item(), excluded_locations=[REGION_2])

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
                locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(TestPreferredLocations.host, loc)
                read_locations.append({'databaseAccountEndpoint': locational_endpoint, 'name': loc})
                counter += 1
            write_regions = [self.regions[0]]
            write_locations = []
            for loc in write_regions:
                locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(TestPreferredLocations.host, loc)
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
