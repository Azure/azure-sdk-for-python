import unittest
import threading
import pytest
from time import sleep

from azure.cosmos.http_constants import ResourceType
import azure.cosmos._cosmos_client_connection as cosmos_client_connection
import azure.cosmos.documents as documents
from azure.cosmos._request_object import RequestObject
from azure.cosmos._location_cache import LocationCache
import azure.cosmos.exceptions as exceptions
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes, HttpHeaders
from azure.cosmos import _retry_utility
import test_config

pytestmark = pytest.mark.cosmosEmulator


class RefreshThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super().__init__()
        self.endpoint_manager = kwargs['endpoint_manager']

    def run(self):
        self.endpoint_manager.force_refresh(None)


@pytest.mark.usefixtures("teardown")
class LocationCacheTest(unittest.TestCase):

    DEFAULT_ENDPOINT = "https://default.documents.azure.com"
    LOCATION_1_ENDPOINT = "https://location1.documents.azure.com"
    LOCATION_2_ENDPOINT = "https://location2.documents.azure.com"
    LOCATION_3_ENDPOINT = "https://location3.documents.azure.com"
    LOCATION_4_ENDPOINT = "https://location4.documents.azure.com"
    REFRESH_TIME_INTERVAL_IN_MS = 1000
    endpoint_by_location = {"location1": LOCATION_1_ENDPOINT,
                            "location2": LOCATION_2_ENDPOINT,
                            "location3": LOCATION_3_ENDPOINT,
                            "location4": LOCATION_4_ENDPOINT}

    def mock_create_db_with_flag_enabled(self, url_connection = None):
        self.database_account = self.create_database_account(True)
        return self.database_account

    def mock_create_db_with_flag_disabled(self, url_connection = None):
        self.database_account = self.create_database_account(False)
        return self.database_account

    def create_spy_client(self, use_multiple_write_locations, enable_endpoint_discovery, is_preferred_locations_list_empty):
        self.preferred_locations = ["location1", "location2", "location3", "location4"]
        connectionPolicy = documents.ConnectionPolicy()
        connectionPolicy.ConnectionRetryConfiguration = 5
        connectionPolicy.DisableSSLVerification = True
        connectionPolicy.PreferredLocations = [] if is_preferred_locations_list_empty else self.preferred_locations
        connectionPolicy.EnableEndpointDiscovery = enable_endpoint_discovery
        connectionPolicy.UseMultipleWriteLocations = use_multiple_write_locations

        client = cosmos_client_connection.CosmosClientConnection(self.DEFAULT_ENDPOINT, {'masterKey': "SomeKeyValue"}, consistency_level="Session", connection_policy=connectionPolicy)
        return client

    def test_validate_retry_on_session_not_availabe_with_disable_multiple_write_locations_and_endpoint_discovery_disabled(self):
        self.validate_retry_on_session_not_availabe_with_endpoint_discovery_disabled(False, False, False)
        self.validate_retry_on_session_not_availabe_with_endpoint_discovery_disabled(False, False, True)
        self.validate_retry_on_session_not_availabe_with_endpoint_discovery_disabled(False, True, False)
        self.validate_retry_on_session_not_availabe_with_endpoint_discovery_disabled(False, True, True)
        self.validate_retry_on_session_not_availabe_with_endpoint_discovery_disabled(True, False, False)
        self.validate_retry_on_session_not_availabe_with_endpoint_discovery_disabled(True, False, True)
        self.validate_retry_on_session_not_availabe_with_endpoint_discovery_disabled(True, True, False)
        self.validate_retry_on_session_not_availabe_with_endpoint_discovery_disabled(True, True, True)

    def validate_retry_on_session_not_availabe_with_endpoint_discovery_disabled(self, is_preferred_locations_list_empty, use_multiple_write_locations, is_read_request):
        self.counter = 0
        self.OriginalExecuteFunction = _retry_utility.ExecuteFunction
        _retry_utility.ExecuteFunction = self._MockExecuteFunctionSessionReadFailureOnce
        self.original_get_database_account = cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount
        cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount = self.mock_create_db_with_flag_enabled if use_multiple_write_locations else self.mock_create_db_with_flag_disabled
        enable_endpoint_discovery = False
        client = self.create_spy_client(use_multiple_write_locations, enable_endpoint_discovery, is_preferred_locations_list_empty)
        
        try:
            if is_read_request:
                client.ReadItem("dbs/mydb/colls/mycoll/docs/1")
            else:
                client.CreateItem("dbs/mydb/colls/mycoll/", {'id':'1'})
            self.fail()
        except exceptions.CosmosHttpResponseError as e:
            # not retried
            self.assertEqual(self.counter, 1)
            self.counter = 0
            self.assertEqual(e.status_code, StatusCodes.NOT_FOUND)
            self.assertEqual(e.sub_status, SubStatusCodes.READ_SESSION_NOTAVAILABLE)

        cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount = self.original_get_database_account
        _retry_utility.ExecuteFunction = self.OriginalExecuteFunction

    def _MockExecuteFunctionSessionReadFailureOnce(self, function, *args, **kwargs):
        self.counter += 1
        response = test_config.FakeResponse({HttpHeaders.SubStatus: SubStatusCodes.READ_SESSION_NOTAVAILABLE})
        raise exceptions.CosmosHttpResponseError(
            status_code=StatusCodes.NOT_FOUND,
            message="Read Session not available",
            response=response)

    def test_validate_retry_on_session_not_availabe_with_endpoint_discovery_enabled(self):
        # sequence of chosen endpoints: 
        #     1. Single region, No Preferred Location: 
        #        location1 (default) -> location1 (no preferred location, hence default)
        #     2. Single Region, Preferred Locations present:
        #        location1 (1st preferred location) -> location1 (1st location in DBA's WriteLocation)
        #     3. MultiRegion, Preferred Regions present:
        #        location1 (1st preferred location Read Location) -> location1 (1st location in DBA's WriteLocation) ->
        #        location2 (2nd preferred location Read Location)-> location4 (3rd preferred location Read Location)
        #self.validate_retry_on_session_not_availabe(True, False)
        #self.validate_retry_on_session_not_availabe(False, False)
        self.validate_retry_on_session_not_availabe(False, True)

    def validate_retry_on_session_not_availabe(self, is_preferred_locations_list_empty, use_multiple_write_locations):
        self.counter = 0
        self.OriginalExecuteFunction = _retry_utility.ExecuteFunction
        _retry_utility.ExecuteFunction = self._MockExecuteFunctionSessionReadFailureTwice
        self.original_get_database_account = cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount
        cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount = self.mock_create_db_with_flag_enabled if use_multiple_write_locations else self.mock_create_db_with_flag_disabled

        enable_endpoint_discovery = True
        self.is_preferred_locations_list_empty = is_preferred_locations_list_empty
        self.use_multiple_write_locations = use_multiple_write_locations
        client = self.create_spy_client(use_multiple_write_locations, enable_endpoint_discovery, is_preferred_locations_list_empty)

        try:
            client.ReadItem("dbs/mydb/colls/mycoll/docs/1")
        except exceptions.CosmosHttpResponseError as e:
            # not retried
            self.assertEqual(self.counter, 4 if use_multiple_write_locations else 2)
            self.counter = 0
            self.assertEqual(e.status_code, StatusCodes.NOT_FOUND)
            self.assertEqual(e.sub_status, SubStatusCodes.READ_SESSION_NOTAVAILABLE)

        cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount = self.original_get_database_account
        _retry_utility.ExecuteFunction = self.OriginalExecuteFunction

    def _MockExecuteFunctionSessionReadFailureTwice(self, function, *args, **kwargs):
        request = args[1]
        if self.counter == 0:
            if not self.use_multiple_write_locations:
                expected_endpoint = self.database_account.WritableLocations[0]['databaseAccountEndpoint'] if self.is_preferred_locations_list_empty else self.preferred_locations[0]
            else:
                expected_endpoint = self.endpoint_by_location[self.preferred_locations[0]]
            self.assertFalse(request.should_clear_session_token_on_session_read_failure)
        elif self.counter == 1:
            expected_endpoint = self.database_account.WritableLocations[0]['databaseAccountEndpoint']
            if not self.use_multiple_write_locations:
                self.assertTrue(request.should_clear_session_token_on_session_read_failure)
            else:
                self.assertFalse(request.should_clear_session_token_on_session_read_failure)
        elif self.counter == 2:
            expected_endpoint = self.endpoint_by_location[self.preferred_locations[1]]
            self.assertFalse(request.should_clear_session_token_on_session_read_failure)
        elif self.counter == 3:
            expected_endpoint = self.database_account.ReadableLocations[2]['databaseAccountEndpoint']
            self.assertTrue(request.should_clear_session_token_on_session_read_failure)
        self.assertEqual(expected_endpoint, request.location_endpoint_to_route)
        self.counter += 1
        response = test_config.FakeResponse({HttpHeaders.SubStatus: SubStatusCodes.READ_SESSION_NOTAVAILABLE})
        raise exceptions.CosmosHttpResponseError(
            status_code=StatusCodes.NOT_FOUND,
            message="Read Session not available",
            response=response)

    def test_validate_location_cache(self):
        self.original_get_database_account = cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount
        cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount = self.mock_get_database_account
        self.get_database_account_hit_counter = 0
        for i in range (0,8):
            use_multiple_write_locations = (i & 1) > 0
            endpoint_discovery_enabled = (i & 2) > 0
            is_preferred_list_empty = (i & 4) > 0
            self.validate_location_cache(use_multiple_write_locations, endpoint_discovery_enabled, is_preferred_list_empty)
        cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount = self.original_get_database_account

    def test_validate_write_endpoint_order_with_client_side_disable_multiple_write_location(self):
        self.original_get_database_account = cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount
        cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount = self.mock_get_database_account
        self.get_database_account_hit_counter = 0
        self.initialize(False, True, False)
        self.assertEqual(self.location_cache.get_write_endpoints()[0], self.LOCATION_1_ENDPOINT)
        self.assertEqual(self.location_cache.get_write_endpoints()[1], self.LOCATION_2_ENDPOINT)
        self.assertEqual(self.location_cache.get_write_endpoints()[2], self.LOCATION_3_ENDPOINT)
        cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount = self.original_get_database_account

    def mock_get_database_account(self, url_connection=None):
        self.get_database_account_hit_counter += 1
        return self.create_database_account(True)

    def create_database_account(self, use_multiple_write_locations):
        database_account = documents.DatabaseAccount()
        database_account._EnableMultipleWritableLocations = use_multiple_write_locations
        database_account._WritableLocations = [
                    {'name': 'location1', 'databaseAccountEndpoint': self.LOCATION_1_ENDPOINT},
                    {'name': 'location2', 'databaseAccountEndpoint': self.LOCATION_2_ENDPOINT},
                    {'name': 'location3', 'databaseAccountEndpoint': self.LOCATION_3_ENDPOINT}
                    ]
        database_account._ReadableLocations = [
                    {'name': 'location1', 'databaseAccountEndpoint': self.LOCATION_1_ENDPOINT},
                    {'name': 'location2', 'databaseAccountEndpoint': self.LOCATION_2_ENDPOINT},
                    {'name': 'location4', 'databaseAccountEndpoint': self.LOCATION_4_ENDPOINT}
                    ]
        return database_account

    def initialize(self, use_multiple_write_locations, enable_endpoint_discovery, is_preferred_locations_list_empty):
        self.database_account = self.create_database_account(use_multiple_write_locations)
        preferred_locations = ["location1", "location2", "location3"]
        self.preferred_locations = [] if is_preferred_locations_list_empty else preferred_locations
        self.location_cache = LocationCache(
                self.preferred_locations,
                self.DEFAULT_ENDPOINT,
                enable_endpoint_discovery,
                use_multiple_write_locations,
                self.REFRESH_TIME_INTERVAL_IN_MS)
        self.location_cache.perform_on_database_account_read(self.database_account)
        connectionPolicy = documents.ConnectionPolicy()
        connectionPolicy.PreferredLocations = self.preferred_locations
        connectionPolicy.ConnectionRetryConfiguration = 5
        client = cosmos_client_connection.CosmosClientConnection("", {}, consistency_level="Session", connection_policy=connectionPolicy)
        self.global_endpoint_manager = client._global_endpoint_manager

    def validate_location_cache(self, use_multiple_write_locations, endpoint_discovery_enabled, is_preferred_list_empty):
        for write_location_index in range(3):
            for read_location_index in range(2):
                self.initialize(use_multiple_write_locations, endpoint_discovery_enabled, is_preferred_list_empty)

                current_write_endpoints = self.location_cache.get_write_endpoints()
                current_read_endpoints = self.location_cache.get_read_endpoints()

                for i in range(0, read_location_index):
                    self.location_cache.mark_endpoint_unavailable_for_read(self.database_account.ReadableLocations[i]['databaseAccountEndpoint'])
                    self.global_endpoint_manager.mark_endpoint_unavailable_for_read(self.database_account.ReadableLocations[i]['databaseAccountEndpoint'])

                for i in range(0, write_location_index):
                    self.location_cache.mark_endpoint_unavailable_for_write(self.database_account.WritableLocations[i]['databaseAccountEndpoint'])
                    self.global_endpoint_manager.mark_endpoint_unavailable_for_write(self.database_account.WritableLocations[i]['databaseAccountEndpoint'])

                write_endpoint_by_location = {}
                for dba_location in self.database_account._WritableLocations:
                    write_endpoint_by_location[dba_location['name']] = dba_location['databaseAccountEndpoint']

                read_endpoint_by_location = {}
                for dba_location in self.database_account._ReadableLocations:
                    read_endpoint_by_location[dba_location['name']] = dba_location['databaseAccountEndpoint']

                available_write_endpoints = []
                for i in range(write_location_index, len(self.preferred_locations)):
                    location = self.preferred_locations[i]
                    endpoint = write_endpoint_by_location[location] if location in write_endpoint_by_location else None
                    if endpoint:
                        available_write_endpoints.append(endpoint)

                available_read_endpoints = []
                for i in range(read_location_index, len(self.preferred_locations)):
                    location = self.preferred_locations[i]
                    endpoint = read_endpoint_by_location[location] if location in read_endpoint_by_location else None
                    if endpoint:
                        available_read_endpoints.append(endpoint)

                self.validate_endpoint_refresh(use_multiple_write_locations, endpoint_discovery_enabled, available_write_endpoints, available_read_endpoints, write_location_index > 0)
                self.validate_global_endpoint_location_cache_refresh()
                self.validate_request_endpoint_resolution(use_multiple_write_locations, endpoint_discovery_enabled, available_write_endpoints, available_read_endpoints)

                # wait for TTL on unavailablity info
                sleep(1.5)

                self.assertEqual(current_write_endpoints, self.location_cache.get_write_endpoints())
                self.assertEqual(current_read_endpoints, self.location_cache.get_read_endpoints())

    def validate_global_endpoint_location_cache_refresh(self):
        self.get_database_account_hit_counter = 0
        refresh_threads = []
        for i in range(10):
            refresh_thread = RefreshThread(kwargs={'endpoint_manager':self.global_endpoint_manager})
            refresh_thread.start()
            refresh_threads.append(refresh_thread)

        for i in range(10):
            refresh_threads[i].join()

        self.assertTrue(self.get_database_account_hit_counter <= 1)

        for i in range(10):
            refresh_thread = RefreshThread(kwargs={'endpoint_manager': self.global_endpoint_manager})
            refresh_thread.start()
            refresh_thread.join()

        self.assertTrue(self.get_database_account_hit_counter <= 1)

    def validate_endpoint_refresh(self, use_multiple_write_locations, endpoint_discovery_enabled, preferred_available_write_endpoints,
                                  preferred_available_read_endpoints, is_first_write_endpoint_unavailable):
        should_refresh_endpoints = self.location_cache.should_refresh_endpoints()

        is_most_preferred_location_unavailable_for_read = False
        is_most_preferred_location_unavailable_for_write = False if use_multiple_write_locations else is_first_write_endpoint_unavailable

        if len(self.preferred_locations) > 0:
            most_preferred_read_location_name = None
            for preferred_location in self.preferred_locations:
                for read_location in self.database_account._ReadableLocations:
                    if read_location['name'] == preferred_location:
                        most_preferred_read_location_name = preferred_location
                        break
                if most_preferred_read_location_name:
                    break

            most_preferred_read_endpoint = self.endpoint_by_location[most_preferred_read_location_name]
            is_most_preferred_location_unavailable_for_read = True if len(preferred_available_read_endpoints) == 0 else preferred_available_read_endpoints[0] != most_preferred_read_endpoint

            most_preferred_write_location_name = None
            for preferred_location in self.preferred_locations:
                for write_location in self.database_account._WritableLocations:
                    if write_location['name'] == preferred_location:
                        most_preferred_write_location_name = preferred_location
                        break
                if most_preferred_write_location_name:
                    break

            most_preferred_write_endpoint = self.endpoint_by_location[most_preferred_write_location_name]

            if use_multiple_write_locations:
                is_most_preferred_location_unavailable_for_write = True if len(preferred_available_write_endpoints) == 0 else preferred_available_write_endpoints[0] != most_preferred_write_endpoint

        if not endpoint_discovery_enabled:
            self.assertFalse(should_refresh_endpoints)
        else:
            self.assertEqual(is_most_preferred_location_unavailable_for_read or is_most_preferred_location_unavailable_for_write, should_refresh_endpoints)

    def validate_request_endpoint_resolution(self, use_multiple_write_locations, endpoint_discovery_enabled,
                                             available_write_endpoints, available_read_endpoints):
        write_locations = self.database_account._WritableLocations
        if not endpoint_discovery_enabled:
            first_available_write_endpoint = self.DEFAULT_ENDPOINT
            second_available_write_endpoint = self.DEFAULT_ENDPOINT
        elif not use_multiple_write_locations:
            first_available_write_endpoint = write_locations[0]['databaseAccountEndpoint']
            second_available_write_endpoint = write_locations[1]['databaseAccountEndpoint']
        elif len(available_write_endpoints) > 1:
            first_available_write_endpoint = available_write_endpoints[0]
            second_available_write_endpoint = available_write_endpoints[1]
        elif len(available_write_endpoints) > 0:
            first_available_write_endpoint = available_write_endpoints[0]
            write_endpoint = write_locations[0]['databaseAccountEndpoint']
            second_available_write_endpoint = write_endpoint if write_endpoint != first_available_write_endpoint else available_write_endpoints[1]
        else:
            first_available_write_endpoint = self.DEFAULT_ENDPOINT
            second_available_write_endpoint = self.DEFAULT_ENDPOINT

        if not endpoint_discovery_enabled:
            first_available_read_endpoint = self.DEFAULT_ENDPOINT
        elif len(self.preferred_locations) == 0:
            first_available_read_endpoint = first_available_write_endpoint
        elif len(available_read_endpoints) > 0:
            first_available_read_endpoint = available_read_endpoints[0]
        else:
            first_available_read_endpoint = self.endpoint_by_location[self.preferred_locations[0]]

        first_write_enpoint = self.DEFAULT_ENDPOINT if not endpoint_discovery_enabled else self.database_account.WritableLocations[0]['databaseAccountEndpoint']

        second_write_enpoint = self.DEFAULT_ENDPOINT if not endpoint_discovery_enabled else self.database_account.WritableLocations[1]['databaseAccountEndpoint']

        # If current write endpoint is unavailable, write endpoints order doesn't change
        # All write requests flip-flop between current write and alternate write endpoint
        write_endpoints = self.location_cache.get_write_endpoints()
        self.assertTrue(first_available_write_endpoint == write_endpoints[0])
        self.assertTrue(second_available_write_endpoint == self.resolve_endpoint_for_write_request(ResourceType.Document, True))
        self.assertTrue(first_available_write_endpoint == self.resolve_endpoint_for_write_request(ResourceType.Document, False))
        
        # Writes to other resource types should be directed to first/second write endpoint
        self.assertTrue(first_write_enpoint == self.resolve_endpoint_for_write_request(ResourceType.Database, False))
        self.assertTrue(second_write_enpoint == self.resolve_endpoint_for_write_request(ResourceType.Database, True))

        # Reads should be directed to available read endpoints regardless of resource type
        self.assertTrue(first_available_read_endpoint == self.resolve_endpoint_for_read_request(True))
        self.assertTrue(first_available_read_endpoint == self.resolve_endpoint_for_read_request(False))

    def resolve_endpoint_for_read_request(self, master_resource_type):
        operation_type = documents._OperationType.Read
        resource_type = ResourceType.Database if master_resource_type else ResourceType.Document
        request = RequestObject(resource_type, operation_type)
        return self.location_cache.resolve_service_endpoint(request)

    def resolve_endpoint_for_write_request(self, resource_type, use_alternate_write_endpoint):
        operation_type = documents._OperationType.Create
        request = RequestObject(resource_type, operation_type)
        request.route_to_location_with_preferred_location_flag(1 if use_alternate_write_endpoint else 0, ResourceType.IsCollectionChild(resource_type))
        return self.location_cache.resolve_service_endpoint(request)
