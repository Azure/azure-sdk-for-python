import unittest
import pytest
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents
import azure.cosmos.errors as errors
from requests.exceptions import ConnectionError
from azure.cosmos.http_constants import HttpHeaders, StatusCodes, SubStatusCodes
import azure.cosmos.retry_utility as retry_utility
import azure.cosmos.endpoint_discovery_retry_policy as endpoint_discovery_retry_policy
from azure.cosmos.request_object import _RequestObject
import azure.cosmos.global_endpoint_manager as global_endpoint_manager
import azure.cosmos.http_constants as http_constants

pytestmark = pytest.mark.cosmosEmulator

@pytest.mark.usefixtures("teardown")
class TestStreamingFailover(unittest.TestCase):

    DEFAULT_ENDPOINT = "https://geotest.documents.azure.com:443/"
    MASTER_KEY = "SomeKeyValue"
    WRITE_ENDPOINT1 = "https://geotest-WestUS.documents.azure.com:443/"
    WRITE_ENDPOINT2 = "https://geotest-CentralUS.documents.azure.com:443/"
    READ_ENDPOINT1 = "https://geotest-SouthCentralUS.documents.azure.com:443/"
    READ_ENDPOINT2 = "https://geotest-EastUS.documents.azure.com:443/"
    WRITE_ENDPOINT_NAME1 = "West US"
    WRITE_ENDPOINT_NAME2 = "Central US"
    READ_ENDPOINT_NAME1 = "South Central US"
    READ_ENDPOINT_NAME2 = "East US"
    preferred_regional_endpoints = [READ_ENDPOINT_NAME1, READ_ENDPOINT_NAME2]
    counter = 0
    endpoint_sequence = []

    def test_streaming_failover(self):
        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunctionEndpointDiscover
        connection_policy = documents.ConnectionPolicy()
        connection_policy.PreferredLocations = self.preferred_regional_endpoints
        connection_policy.DisableSSLVerification = True
        self.original_get_database_account = cosmos_client.CosmosClient.GetDatabaseAccount
        cosmos_client.CosmosClient.GetDatabaseAccount = self.mock_get_database_account

        client = cosmos_client.CosmosClient(self.DEFAULT_ENDPOINT, {'masterKey': self.MASTER_KEY}, connection_policy, documents.ConsistencyLevel.Eventual)

        document_definition = { 'id': 'doc',
                                'name': 'sample document',
                                'key': 'value'} 

        created_document = {}
        created_document = client.CreateItem("dbs/mydb/colls/mycoll", document_definition)
        
        self.assertDictEqual(created_document, {})
        self.assertDictEqual(client.last_response_headers, {})

        self.assertEqual(self.counter, 10)
        # First request is an initial read collection.
        # Next 8 requests hit forbidden write exceptions and the endpoint retry policy keeps 
        # flipping the resolved endpoint between the 2 write endpoints.
        # The 10th request returns the actual read document.
        for i in range(0,8):
            if i % 2 == 0:
                self.assertEqual(self.endpoint_sequence[i], self.WRITE_ENDPOINT1)
            else:
                self.assertEqual(self.endpoint_sequence[i], self.WRITE_ENDPOINT2)

        cosmos_client.CosmosClient.GetDatabaseAccount = self.original_get_database_account
        retry_utility._ExecuteFunction = self.OriginalExecuteFunction

    def mock_get_database_account(self, url_connection = None):
        database_account = documents.DatabaseAccount()
        database_account._EnableMultipleWritableLocations = True
        database_account._WritableLocations = [
                    {'name': self.WRITE_ENDPOINT_NAME1, 'databaseAccountEndpoint': self.WRITE_ENDPOINT1},
                    {'name': self.WRITE_ENDPOINT_NAME2, 'databaseAccountEndpoint': self.WRITE_ENDPOINT2}
                    ]
        database_account._ReadableLocations = [
                    {'name': self.READ_ENDPOINT_NAME1, 'databaseAccountEndpoint': self.READ_ENDPOINT1},
                    {'name': self.READ_ENDPOINT_NAME2, 'databaseAccountEndpoint': self.READ_ENDPOINT2}
                    ]
        return database_account

    def _MockExecuteFunctionEndpointDiscover(self, function, *args, **kwargs):
        self.counter += 1
        if self.counter >= 10 or ( len(args) > 0 and args[1].operation_type == documents._OperationType.Read):
            return ({}, {})
        else:
            self.endpoint_sequence.append(args[1].location_endpoint_to_route)
            raise errors.HTTPFailure(StatusCodes.FORBIDDEN, "Request is not permitted in this region", {HttpHeaders.SubStatus: SubStatusCodes.WRITE_FORBIDDEN})

    def test_retry_policy_does_not_mark_null_locations_unavailable(self):
        self.original_get_database_account = cosmos_client.CosmosClient.GetDatabaseAccount
        cosmos_client.CosmosClient.GetDatabaseAccount = self.mock_get_database_account

        client = cosmos_client.CosmosClient(self.DEFAULT_ENDPOINT, {'masterKey': self.MASTER_KEY}, None, documents.ConsistencyLevel.Eventual)
        endpoint_manager = global_endpoint_manager._GlobalEndpointManager(client)

        self.original_mark_endpoint_unavailable_for_read_function = endpoint_manager.mark_endpoint_unavailable_for_read
        endpoint_manager.mark_endpoint_unavailable_for_read = self._mock_mark_endpoint_unavailable_for_read
        self.original_mark_endpoint_unavailable_for_write_function = endpoint_manager.mark_endpoint_unavailable_for_write
        endpoint_manager.mark_endpoint_unavailable_for_write = self._mock_mark_endpoint_unavailable_for_write
        self.original_resolve_service_endpoint = endpoint_manager.resolve_service_endpoint
        endpoint_manager.resolve_service_endpoint = self._mock_resolve_service_endpoint

        # Read and write counters count the number of times the endpoint manager's
        # mark_endpoint_unavailable_for_read() and mark_endpoint_unavailable_for_read() 
        # functions were called. When a 'None' location is returned by resolve_service_endpoint(),
        # these functions  should not be called
        self._read_counter = 0
        self._write_counter = 0
        request = _RequestObject(http_constants.ResourceType.Document, documents._OperationType.Read)
        endpointDiscovery_retry_policy = endpoint_discovery_retry_policy._EndpointDiscoveryRetryPolicy(documents.ConnectionPolicy(), endpoint_manager, request)
        endpointDiscovery_retry_policy.ShouldRetry(errors.HTTPFailure(http_constants.StatusCodes.FORBIDDEN))
        self.assertEqual(self._read_counter, 0)
        self.assertEqual(self._write_counter, 0)

        self._read_counter = 0
        self._write_counter = 0
        request = _RequestObject(http_constants.ResourceType.Document, documents._OperationType.Create)
        endpointDiscovery_retry_policy = endpoint_discovery_retry_policy._EndpointDiscoveryRetryPolicy(documents.ConnectionPolicy(), endpoint_manager, request)
        endpointDiscovery_retry_policy.ShouldRetry(errors.HTTPFailure(http_constants.StatusCodes.FORBIDDEN))
        self.assertEqual(self._read_counter, 0)
        self.assertEqual(self._write_counter, 0)

        endpoint_manager.mark_endpoint_unavailable_for_read = self.original_mark_endpoint_unavailable_for_read_function
        endpoint_manager.mark_endpoint_unavailable_for_write = self.original_mark_endpoint_unavailable_for_write_function
        cosmos_client.CosmosClient.GetDatabaseAccount = self.original_get_database_account

    def _mock_mark_endpoint_unavailable_for_read(self, endpoint):
        self._read_counter += 1
        self.original_mark_endpoint_unavailable_for_read_function(endpoint)

    def _mock_mark_endpoint_unavailable_for_write(self, endpoint):
        self._write_counter += 1
        self.original_mark_endpoint_unavailable_for_write_function(endpoint)

    def _mock_resolve_service_endpoint(self, request):
        return None

