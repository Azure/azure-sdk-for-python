import random
from collections import OrderedDict
from typing import List

import pytest
import test_config
from azure.cosmos import DatabaseAccount, _location_cache, CosmosClient, _global_endpoint_manager, \
    _cosmos_client_connection

from azure.cosmos._location_cache import RegionalEndpoint, LocationCache

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

def create_account_endpoints_by_location(global_endpoint: str):
    locational_endpoints = []
    for region in ACCOUNT_REGIONS:
        locational_endpoints.append(_location_cache.LocationCache.GetLocationalEndpoint(global_endpoint, region))
        _location_cache.LocationCache.GetLocationalEndpoint(global_endpoint, REGION_1)
    account_endpoints_by_location = OrderedDict()
    for i, region in enumerate(ACCOUNT_REGIONS):
        # should create some with the global endpoint sometimes
        if random.random() < 0.5:
            account_endpoints_by_location[region] = RegionalEndpoint(locational_endpoints[i], global_endpoint)
        else:
            account_endpoints_by_location[region] = RegionalEndpoint(global_endpoint, locational_endpoints[i])


    return locational_endpoints, account_endpoints_by_location

def is_global_endpoint_inputs():
    global_endpoint = test_config.TestConfig.host
    locational_endpoints, account_endpoints_by_location = create_account_endpoints_by_location(global_endpoint)

    # testing if customers account name includes a region ex. contoso-eastus
    global_endpoint_2 = _location_cache.LocationCache.GetLocationalEndpoint(global_endpoint, REGION_1)
    locational_endpoints_2, account_endpoints_by_location_2 = create_account_endpoints_by_location(global_endpoint_2)

    # endpoint, locations, account_endpoints_by_location, result
    return [
        (global_endpoint, ACCOUNT_REGIONS, account_endpoints_by_location, True),
        (locational_endpoints[0], ACCOUNT_REGIONS, account_endpoints_by_location, False),
        (locational_endpoints[1], ACCOUNT_REGIONS, account_endpoints_by_location, False),
        (locational_endpoints[2], ACCOUNT_REGIONS, account_endpoints_by_location, False),
        (global_endpoint_2, ACCOUNT_REGIONS, account_endpoints_by_location_2, True),
        (locational_endpoints_2[0], ACCOUNT_REGIONS, account_endpoints_by_location_2, False),
        (locational_endpoints_2[1], ACCOUNT_REGIONS, account_endpoints_by_location_2, False),
        (locational_endpoints_2[2], ACCOUNT_REGIONS, account_endpoints_by_location_2, False)
    ]


@pytest.mark.cosmosEmulator
@pytest.mark.unittest
@pytest.mark.usefixtures("setup")
class TestPreferredLocations:
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID

    @pytest.mark.parametrize("preferred_location, default_endpoint", preferred_locations())
    def test_effective_preferred_regions(self, setup, preferred_location, default_endpoint):

        self.original_getDatabaseAccountStub = _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub
        self.original_getDatabaseAccountCheck = _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck
        _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.MockGetDatabaseAccount(ACCOUNT_REGIONS)
        _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck = self.MockGetDatabaseAccount(ACCOUNT_REGIONS)
        try:
            client = CosmosClient(default_endpoint, self.masterKey, preferred_locations=preferred_location)
            # this will setup the location cache
            client.client_connection._global_endpoint_manager.force_refresh(None)
        finally:
            _global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.original_getDatabaseAccountStub
            _cosmos_client_connection.CosmosClientConnection._GetDatabaseAccountCheck = self.original_getDatabaseAccountCheck
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


    @pytest.mark.parametrize("default_endpoint, read_locations, account_endpoints_by_location, result", is_global_endpoint_inputs())
    def test_is_global_endpoint(self, default_endpoint, read_locations, account_endpoints_by_location, result):
        assert result == LocationCache.is_global_endpoint(default_endpoint, account_endpoints_by_location, read_locations)


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
