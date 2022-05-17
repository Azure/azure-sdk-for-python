#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from urllib.parse import urlparse

import unittest
import time
import pytest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos._global_endpoint_manager as global_endpoint_manager
from azure.cosmos import _endpoint_discovery_retry_policy, _retry_utility, PartitionKey, documents, exceptions
from azure.cosmos.http_constants import HttpHeaders, StatusCodes, SubStatusCodes
import test_config

pytestmark = [pytest.mark.cosmosEmulator, pytest.mark.globaldb]

# IMPORTANT NOTES:
  
#  	Most test cases in this file create collections in your Azure Cosmos account.
#  	Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.
  
#  	To run the global database tests, you will need to fill out values for the following variables under test_config.py
#   settings: host, masterKey, global_host, write_location_host, read_location_host, read_location2_host
#   and global_masterKey.

#   TODO: These tests need to be properly configured in the pipeline with locational endpoints.
#    For now we use the is_not_default_host() method to skip regional checks.


def is_not_default_host(endpoint):
    if endpoint == test_config._test_config.host:
        return False
    return True

@pytest.mark.usefixtures("teardown")
class Test_globaldb_tests(unittest.TestCase):

    host = test_config._test_config.global_host
    write_location_host = test_config._test_config.write_location_host
    read_location_host = test_config._test_config.read_location_host
    read_location2_host = test_config._test_config.read_location2_host
    masterKey = test_config._test_config.global_masterKey

    write_location = test_config._test_config.write_location
    read_location = test_config._test_config.read_location
    read_location2 = test_config._test_config.read_location2

    test_database_id = 'testdb'
    test_collection_id = 'testcoll'

    def __AssertHTTPFailureWithStatus(self, status_code, sub_status, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `sub_status`: int
            - `func`: function
        """
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            self.assertEqual(inst.status_code, status_code)
            self.assertEqual(inst.sub_status, sub_status)

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_GLOBAL_ENDPOINT_HERE]'):
            return(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(Test_globaldb_tests.host, Test_globaldb_tests.masterKey)
        for db in cls.client.list_databases():
            cls.client.delete_database(db)
        
        # Create the test database only when it's not already present
        query_iterable = cls.client.query_databases(query='SELECT * FROM root r WHERE r.id=\'' + Test_globaldb_tests.test_database_id + '\'')  # nosec
        it = iter(query_iterable)
        
        cls.test_db = next(it, None)
        if cls.test_db is None:
            cls.test_db = cls.client.create_database(id=Test_globaldb_tests.test_database_id)
        else:
            cls.test_db = cls.client.get_database_client(cls.test_db['id'])

        # Create the test collection only when it's not already present
        query_iterable = cls.test_db.query_containers(query='SELECT * FROM root r WHERE r.id=\'' + Test_globaldb_tests.test_collection_id + '\'')   # nosec
        it = iter(query_iterable)
        
        cls.test_coll = next(it, None)
        if cls.test_coll is None:
            cls.test_coll = cls.test_db.create_container(id=Test_globaldb_tests.test_collection_id,
                                                         partition_key=PartitionKey(path="/id"))
        else:
            cls.test_coll = cls.client.get_database_client(cls.test_coll['id'])

    def test_globaldb_read_write_endpoints(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.EnableEndpointDiscovery = False

        client = cosmos_client.CosmosClient(Test_globaldb_tests.host, Test_globaldb_tests.masterKey,
                                            connection_policy=connection_policy)

        document_definition = {'id': 'doc',
                               'name': 'sample document',
                               'key': 'value'}

        database = client.get_database_client(Test_globaldb_tests.test_database_id)
        container = database.get_container_client(Test_globaldb_tests.test_collection_id)
        
        # When EnableEndpointDiscovery is False, WriteEndpoint is set to the endpoint passed while creating the client instance
        created_document = container.create_item(document_definition)
        self.assertEqual(client.client_connection.WriteEndpoint, Test_globaldb_tests.host)
        
        # Delay to get these resources replicated to read location due to Eventual consistency
        time.sleep(5)

        container.read_item(item=created_document, partition_key=created_document['id'])
        content_location = str(client.client_connection.last_response_headers[HttpHeaders.ContentLocation])

        content_location_url = urlparse(content_location)
        host_url = urlparse(Test_globaldb_tests.host)
        
        # When EnableEndpointDiscovery is False, ReadEndpoint is set to the endpoint passed while creating the client instance
        self.assertEqual(str(content_location_url.hostname), str(host_url.hostname))
        self.assertEqual(client.client_connection.ReadEndpoint, Test_globaldb_tests.host)

        connection_policy.EnableEndpointDiscovery = True
        document_definition['id'] = 'doc2'

        client = cosmos_client.CosmosClient(Test_globaldb_tests.host, Test_globaldb_tests.masterKey,
                                            connection_policy=connection_policy)

        database = client.get_database_client(Test_globaldb_tests.test_database_id)
        container = database.get_container_client(Test_globaldb_tests.test_collection_id)

        # When EnableEndpointDiscovery is True, WriteEndpoint is set to the write endpoint
        created_document = container.create_item(document_definition)
        if is_not_default_host(Test_globaldb_tests.write_location_host):
            self.assertEqual(client.client_connection.WriteEndpoint, Test_globaldb_tests.write_location_host)
        
        # Delay to get these resources replicated to read location due to Eventual consistency
        time.sleep(5)

        container.read_item(item=created_document, partition_key=created_document['id'])
        content_location = str(client.client_connection.last_response_headers[HttpHeaders.ContentLocation])
        
        content_location_url = urlparse(content_location)
        write_location_url = urlparse(Test_globaldb_tests.write_location_host)

        # If no preferred locations is set, we return the write endpoint as ReadEndpoint for better latency performance
        if is_not_default_host(Test_globaldb_tests.write_location_host):
            self.assertEqual(str(content_location_url.hostname), str(write_location_url.hostname))
            self.assertEqual(client.client_connection.ReadEndpoint, Test_globaldb_tests.write_location_host)

    def test_globaldb_endpoint_discovery(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.EnableEndpointDiscovery = False

        read_location_client = cosmos_client.CosmosClient(Test_globaldb_tests.read_location_host,
                                                          Test_globaldb_tests.masterKey,
                                                          connection_policy=connection_policy)

        document_definition = {'id': 'doc1',
                               'name': 'sample document',
                               'key': 'value'}

        database = read_location_client.get_database_client(Test_globaldb_tests.test_database_id)
        container = database.get_container_client(Test_globaldb_tests.test_collection_id)
        
        # Create Document will fail for the read location client since it has EnableEndpointDiscovery set to false, and hence the request will directly go to 
        # the endpoint that was used to create the client instance(which happens to be a read endpoint)
        if is_not_default_host(Test_globaldb_tests.read_location_host):
            self.__AssertHTTPFailureWithStatus(
                StatusCodes.FORBIDDEN,
                SubStatusCodes.WRITE_FORBIDDEN,
                container.create_item,
                document_definition)

        # Query databases will pass for the read location client as it's a GET operation
        list(read_location_client.query_databases(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[{'name': '@id', 'value': self.test_db.id}]))

        connection_policy.EnableEndpointDiscovery = True
        read_location_client = cosmos_client.CosmosClient(Test_globaldb_tests.read_location_host,
                                                          Test_globaldb_tests.masterKey,
                                                          connection_policy=connection_policy)

        database = read_location_client.get_database_client(Test_globaldb_tests.test_database_id)
        container = database.get_container_client(Test_globaldb_tests.test_collection_id)

        # CreateDocument call will go to the WriteEndpoint as EnableEndpointDiscovery is set to True and client will resolve the right endpoint based on the operation
        created_document = container.create_item(document_definition)
        self.assertEqual(created_document['id'], document_definition['id'])

    def test_globaldb_preferred_locations(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.EnableEndpointDiscovery = True

        client = cosmos_client.CosmosClient(Test_globaldb_tests.host, Test_globaldb_tests.masterKey,
                                            connection_policy=connection_policy)
        
        document_definition = {'id': 'doc3',
                               'name': 'sample document',
                               'key': 'value'}

        database = client.get_database_client(Test_globaldb_tests.test_database_id)
        container = database.get_container_client(Test_globaldb_tests.test_collection_id)

        created_document = container.create_item(document_definition)
        self.assertEqual(created_document['id'], document_definition['id'])

        # Delay to get these resources replicated to read location due to Eventual consistency
        time.sleep(5)

        container.read_item(item=created_document, partition_key=created_document['id'])
        content_location = str(client.client_connection.last_response_headers[HttpHeaders.ContentLocation])

        content_location_url = urlparse(content_location)
        write_location_url = urlparse(Test_globaldb_tests.write_location_host)

        # If no preferred locations is set, we return the write endpoint as ReadEndpoint for better latency performance
        if is_not_default_host(Test_globaldb_tests.write_location_host):
            self.assertEqual(str(content_location_url.hostname), str(write_location_url.hostname))
            self.assertEqual(client.client_connection.ReadEndpoint, Test_globaldb_tests.write_location_host)

        if is_not_default_host(Test_globaldb_tests.read_location2):  # Client init will fail if no read location given
            connection_policy.PreferredLocations = [Test_globaldb_tests.read_location2]

            client = cosmos_client.CosmosClient(Test_globaldb_tests.host, Test_globaldb_tests.masterKey,
                                                connection_policy=connection_policy)

            database = client.get_database_client(Test_globaldb_tests.test_database_id)
            container = database.get_container_client(Test_globaldb_tests.test_collection_id)

            document_definition['id'] = 'doc4'
            created_document = container.create_item(document_definition)

            # Delay to get these resources replicated to read location due to Eventual consistency
            time.sleep(5)

            container.read_item(item=created_document, partition_key=created_document['id'])
            content_location = str(client.client_connection.last_response_headers[HttpHeaders.ContentLocation])

            content_location_url = urlparse(content_location)
            read_location2_url = urlparse(Test_globaldb_tests.read_location2_host)

            # Test that the preferred location is set as ReadEndpoint instead of default write endpoint when no preference is set
            self.assertEqual(str(content_location_url.hostname), str(read_location2_url.hostname))
            self.assertEqual(client.client_connection.ReadEndpoint, Test_globaldb_tests.read_location2_host)

    def test_globaldb_endpoint_assignments(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.EnableEndpointDiscovery = False

        client = cosmos_client.CosmosClient(Test_globaldb_tests.host, Test_globaldb_tests.masterKey,
                                            connection_policy=connection_policy)

        # When EnableEndpointDiscovery is set to False, both Read and Write Endpoints point to endpoint passed while creating the client instance
        self.assertEqual(client.client_connection.WriteEndpoint, Test_globaldb_tests.host)
        self.assertEqual(client.client_connection.ReadEndpoint, Test_globaldb_tests.host)

        connection_policy.EnableEndpointDiscovery = True
        client = cosmos_client.CosmosClient(Test_globaldb_tests.host, Test_globaldb_tests.masterKey,
                                            connection_policy=connection_policy)

        # If no preferred locations is set, we return the write endpoint as ReadEndpoint for better latency performance, write endpoint is set as expected
        self.assertEqual(client.client_connection.WriteEndpoint,
                         client.client_connection.ReadEndpoint)
        if is_not_default_host(Test_globaldb_tests.write_location_host):
            self.assertEqual(client.client_connection.WriteEndpoint,
                             Test_globaldb_tests.write_location_host)

        if is_not_default_host(Test_globaldb_tests.read_location2):
            connection_policy.PreferredLocations = [Test_globaldb_tests.read_location2]
            client = cosmos_client.CosmosClient(Test_globaldb_tests.host, Test_globaldb_tests.masterKey,
                                                connection_policy=connection_policy)

            # Test that the preferred location is set as ReadEndpoint instead of default write endpoint when no preference is set
            self.assertEqual(client.client_connection._global_endpoint_manager.WriteEndpoint,
                             Test_globaldb_tests.write_location_host)
            self.assertEqual(client.client_connection._global_endpoint_manager.ReadEndpoint,
                             Test_globaldb_tests.read_location2_host)

    def test_globaldb_update_locations_cache(self):
        client = cosmos_client.CosmosClient(Test_globaldb_tests.host, Test_globaldb_tests.masterKey)

        writable_locations = [{'name': Test_globaldb_tests.write_location, 'databaseAccountEndpoint': Test_globaldb_tests.write_location_host}]
        readable_locations = [{'name': Test_globaldb_tests.read_location, 'databaseAccountEndpoint': Test_globaldb_tests.read_location_host},
                              {'name': Test_globaldb_tests.read_location2, 'databaseAccountEndpoint': Test_globaldb_tests.read_location2_host}]

        if (is_not_default_host(Test_globaldb_tests.write_location_host)
            and is_not_default_host(Test_globaldb_tests.read_location_host)
            and is_not_default_host(Test_globaldb_tests.read_location2_host)):
            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(writable_locations, readable_locations)

            # If no preferred locations is set, we return the write endpoint as ReadEndpoint for better latency performance, write endpoint is set as expected
            self.assertEqual(write_endpoint, Test_globaldb_tests.write_location_host)
            self.assertEqual(read_endpoint, Test_globaldb_tests.write_location_host)

            writable_locations = []
            readable_locations = []

            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(writable_locations, readable_locations)

            # If writable_locations and readable_locations are empty, both Read and Write Endpoints point to endpoint passed while creating the client instance
            self.assertEqual(write_endpoint, Test_globaldb_tests.host)
            self.assertEqual(read_endpoint, Test_globaldb_tests.host)

            writable_locations = [{'name': Test_globaldb_tests.write_location, 'databaseAccountEndpoint': Test_globaldb_tests.write_location_host}]
            readable_locations = []

            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(writable_locations, readable_locations)

            # If there are no readable_locations, we use the write endpoint as ReadEndpoint
            self.assertEqual(write_endpoint, Test_globaldb_tests.write_location_host)
            self.assertEqual(read_endpoint, Test_globaldb_tests.write_location_host)

            writable_locations = []
            readable_locations = [{'name': Test_globaldb_tests.read_location, 'databaseAccountEndpoint': Test_globaldb_tests.read_location_host}]

            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(writable_locations, readable_locations)

            # If there are no writable_locations, both Read and Write Endpoints point to endpoint passed while creating the client instance
            self.assertEqual(write_endpoint, Test_globaldb_tests.host)
            self.assertEqual(read_endpoint, Test_globaldb_tests.host)

            writable_locations = [{'name': Test_globaldb_tests.write_location, 'databaseAccountEndpoint': Test_globaldb_tests.write_location_host}]
            readable_locations = [{'name': Test_globaldb_tests.read_location, 'databaseAccountEndpoint': Test_globaldb_tests.read_location_host},
                                  {'name': Test_globaldb_tests.read_location2, 'databaseAccountEndpoint': Test_globaldb_tests.read_location2_host}]

            connection_policy = documents.ConnectionPolicy()
            connection_policy.PreferredLocations = [Test_globaldb_tests.read_location2]

            client = cosmos_client.CosmosClient(Test_globaldb_tests.host, Test_globaldb_tests.masterKey,
                                                connection_policy=connection_policy)

            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(writable_locations, readable_locations)

            # Test that the preferred location is set as ReadEndpoint instead of default write endpoint when no preference is set
            self.assertEqual(write_endpoint, Test_globaldb_tests.write_location_host)
            self.assertEqual(read_endpoint, Test_globaldb_tests.read_location2_host)

            writable_locations = [{'name': Test_globaldb_tests.write_location, 'databaseAccountEndpoint': Test_globaldb_tests.write_location_host},
                                  {'name': Test_globaldb_tests.read_location2, 'databaseAccountEndpoint': Test_globaldb_tests.read_location2_host}]
            readable_locations = [{'name': Test_globaldb_tests.read_location, 'databaseAccountEndpoint': Test_globaldb_tests.read_location_host}]

            connection_policy = documents.ConnectionPolicy()
            connection_policy.PreferredLocations = [Test_globaldb_tests.read_location2]

            client = cosmos_client.CosmosClient(Test_globaldb_tests.host, Test_globaldb_tests.masterKey,
                                                connection_policy=connection_policy)

            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(writable_locations, readable_locations)

            # Test that the preferred location is chosen from the WriteLocations if it's not present in the ReadLocations
            self.assertEqual(write_endpoint, Test_globaldb_tests.write_location_host)
            self.assertEqual(read_endpoint, Test_globaldb_tests.read_location2_host)

            writable_locations = [{'name': Test_globaldb_tests.write_location, 'databaseAccountEndpoint': Test_globaldb_tests.write_location_host}]
            readable_locations = [{'name': Test_globaldb_tests.read_location, 'databaseAccountEndpoint': Test_globaldb_tests.read_location_host},
                                  {'name': Test_globaldb_tests.read_location2, 'databaseAccountEndpoint': Test_globaldb_tests.read_location2_host}]

            connection_policy.EnableEndpointDiscovery = False
            client = cosmos_client.CosmosClient(Test_globaldb_tests.host, Test_globaldb_tests.masterKey,
                                                connection_policy=connection_policy)

            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(writable_locations, readable_locations)

            # If EnableEndpointDiscovery is False, both Read and Write Endpoints point to endpoint passed while creating the client instance
            self.assertEqual(write_endpoint, Test_globaldb_tests.host)
            self.assertEqual(read_endpoint, Test_globaldb_tests.host)

    def test_globaldb_locational_endpoint_parser(self):
        url_endpoint = 'https://contoso.documents.azure.com:443/'
        location_name = 'East US'

        # Creating a locational endpoint from the location name using the parser method
        locational_endpoint = global_endpoint_manager._GlobalEndpointManager.GetLocationalEndpoint(url_endpoint, location_name)
        self.assertEqual(locational_endpoint, 'https://contoso-EastUS.documents.azure.com:443/')

        url_endpoint = 'https://Contoso.documents.azure.com:443/'
        location_name = 'East US'

        # Note that the host name gets lowercased as the urlparser in Python doesn't retains the casing 
        locational_endpoint = global_endpoint_manager._GlobalEndpointManager.GetLocationalEndpoint(url_endpoint, location_name)
        self.assertEqual(locational_endpoint, 'https://contoso-EastUS.documents.azure.com:443/')

    def test_globaldb_endpoint_discovery_retry_policy_mock(self):
        client = cosmos_client.CosmosClient(Test_globaldb_tests.host, Test_globaldb_tests.masterKey)

        self.OriginalExecuteFunction = _retry_utility.ExecuteFunction
        _retry_utility.ExecuteFunction = self._MockExecuteFunction

        self.OriginalGetDatabaseAccount = client.client_connection.GetDatabaseAccount
        client.client_connection.GetDatabaseAccount = self._MockGetDatabaseAccount

        max_retry_attempt_count = 10
        retry_after_in_milliseconds = 500

        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Max_retry_attempt_count = max_retry_attempt_count
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Retry_after_in_milliseconds = retry_after_in_milliseconds

        document_definition = {'id': 'doc7',
                               'name': 'sample document',
                               'key': 'value'}

        database = client.get_database_client(Test_globaldb_tests.test_database_id)
        container = database.get_container_client(Test_globaldb_tests.test_collection_id)

        self.__AssertHTTPFailureWithStatus(
            StatusCodes.FORBIDDEN,
            SubStatusCodes.WRITE_FORBIDDEN,
            container.create_item,
            document_definition)

        _retry_utility.ExecuteFunction = self.OriginalExecuteFunction

    def _MockExecuteFunction(self, function, *args, **kwargs):
        response = test_config.FakeResponse({'x-ms-substatus': SubStatusCodes.WRITE_FORBIDDEN})
        raise exceptions.CosmosHttpResponseError(
            status_code=StatusCodes.FORBIDDEN,
            message="Write Forbidden",
            response=response)
            
    def _MockGetDatabaseAccount(self, url_conection):
        database_account = documents.DatabaseAccount()
        return database_account


if __name__ == '__main__':
    unittest.main()
