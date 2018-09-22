import unittest
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents
import azure.cosmos.errors as errors
from requests.exceptions import ConnectionError
from azure.cosmos.http_constants import HttpHeaders, StatusCodes, SubStatusCodes
import azure.cosmos.retry_utility as retry_utility

class TestStreamingFailover(unittest.TestCase):

    DEFAULT_ENDPOINT = "https://geotest.documents.azure.com:443/"
    MASTER_KEY = "SomeKeyValue"
    WRITE_ENDPOINT = "https://geotest-WestUS.documents.azure.com:443/"
    WRITE_ENDPOINT2 = "https://geotest-CentralUS.documents.azure.com:443/"
    READ_ENDPOINT1 = "https://geotest-SouthCentralUS.documents.azure.com:443/"
    READ_ENDPOINT2 = "https://geotest-EastUS.documents.azure.com:443/"
    WRITE_ENDPOINT_NAME = "West US"
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
        
        client = cosmos_client.CosmosClient(self.DEFAULT_ENDPOINT, {'masterKey': self.MASTER_KEY}, connection_policy)
        
        document_definition = { 'id': 'doc',
                                'name': 'sample document',
                                'key': 'value'} 

        created_document = {}
        try :
            created_document = client.CreateItem("dbs/mydb/colls/mycoll", {'id':'new Doc'})
            self.fail()
        except ConnectionError as err:
            print("Connection error occurred as expected.")

        self.assertDictEqual(created_document, {})

        self.assertEqual(self.counter, 7)
        for i in range(0,6):
            if i % 2 == 0:
                self.assertEqual(self.endpoint_sequence[i], self.READ_ENDPOINT1)
            else:
                self.assertEqual(self.endpoint_sequence[i], self.READ_ENDPOINT2)

        cosmos_client.CosmosClient.GetDatabaseAccount = self.original_get_database_account
        retry_utility._ExecuteFunction = self.OriginalExecuteFunction
        

    def mock_get_database_account(self, url_connection = None):
        database_account = documents.DatabaseAccount()
        database_account._EnableMultipleWritableLocations = True
        database_account._WritableLocations = [
                    {'name': self.WRITE_ENDPOINT_NAME, 'databaseAccountEndpoint': self.WRITE_ENDPOINT},
                    {'name': self.WRITE_ENDPOINT_NAME2, 'databaseAccountEndpoint': self.WRITE_ENDPOINT2}
                    ]
        database_account._ReadableLocations = [
                    {'name': self.READ_ENDPOINT_NAME1, 'databaseAccountEndpoint': self.READ_ENDPOINT1},
                    {'name': self.READ_ENDPOINT_NAME2, 'databaseAccountEndpoint': self.READ_ENDPOINT2}
                    ]
        return database_account

    def _MockExecuteFunctionEndpointDiscover(self, function, *args, **kwargs):
        self.counter += 1
        if self.counter >= 7:
            return self.OriginalExecuteFunction(function, *args, **kwargs)
        else:
            self.endpoint_sequence.append(args[1].location_endpoint_to_route)
            raise errors.HTTPFailure(StatusCodes.FORBIDDEN, "Request is not permitted in this region", {HttpHeaders.SubStatus: SubStatusCodes.WRITE_FORBIDDEN})



