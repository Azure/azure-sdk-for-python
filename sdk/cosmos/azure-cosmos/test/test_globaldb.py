﻿# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.


import time
import unittest
from urllib.parse import urlparse

import pytest

import azure.cosmos._global_endpoint_manager as global_endpoint_manager
import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import _endpoint_discovery_retry_policy, _retry_utility, documents, exceptions, \
    DatabaseProxy, ContainerProxy
from azure.cosmos.http_constants import HttpHeaders, StatusCodes, SubStatusCodes


#   TODO: These tests need to be properly configured in the pipeline with locational endpoints.
#    For now we use the is_not_default_host() method to skip regional checks.


def is_not_default_host(endpoint):
    if endpoint == test_config.TestConfig.host:
        return False
    return True


def _mock_execute_function(function, *args, **kwargs):
    response = test_config.FakeResponse({'x-ms-substatus': SubStatusCodes.WRITE_FORBIDDEN})
    raise exceptions.CosmosHttpResponseError(
        status_code=StatusCodes.FORBIDDEN,
        message="Write Forbidden",
        response=response)


def _mock_get_database_account(url_connection):
    database_account = documents.DatabaseAccount()
    return database_account


@pytest.mark.cosmosEmulator
class TestGlobalDB(unittest.TestCase):
    host = test_config.TestConfig.global_host
    write_location_host = test_config.TestConfig.write_location_host
    read_location_host = test_config.TestConfig.read_location_host
    read_location2_host = test_config.TestConfig.read_location2_host
    masterKey = test_config.TestConfig.global_masterKey

    write_location = test_config.TestConfig.write_location
    read_location = test_config.TestConfig.read_location
    read_location2 = test_config.TestConfig.read_location2

    configs = test_config.TestConfig

    client: cosmos_client.CosmosClient = None
    test_db: DatabaseProxy = None
    test_coll: ContainerProxy = None

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
            return (
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.test_db = cls.client.get_database_client(cls.configs.TEST_DATABASE_ID)
        cls.test_coll = cls.test_db.get_container_client(cls.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

    def test_global_db_read_write_endpoints(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.EnableEndpointDiscovery = False

        client = cosmos_client.CosmosClient(TestGlobalDB.host, TestGlobalDB.masterKey,
                                            connection_policy=connection_policy)

        document_definition = {'id': 'doc',
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}

        # When EnableEndpointDiscovery is False, WriteEndpoint is set to the endpoint passed while creating the client instance
        created_document = self.test_coll.create_item(document_definition)
        self.assertEqual(client.client_connection.WriteEndpoint, TestGlobalDB.host)

        # Delay to get these resources replicated to read location due to Eventual consistency
        time.sleep(5)

        self.test_coll.read_item(item=created_document, partition_key=created_document['pk'])
        content_location = str(client.client_connection.last_response_headers[HttpHeaders.ContentLocation])

        content_location_url = urlparse(content_location)
        host_url = urlparse(TestGlobalDB.host)

        # When EnableEndpointDiscovery is False, ReadEndpoint is set to the endpoint passed while creating the client instance
        self.assertEqual(str(content_location_url.hostname), str(host_url.hostname))
        self.assertEqual(client.client_connection.ReadEndpoint, TestGlobalDB.host)

        connection_policy.EnableEndpointDiscovery = True
        document_definition['id'] = 'doc2'

        client = cosmos_client.CosmosClient(TestGlobalDB.host, TestGlobalDB.masterKey,
                                            connection_policy=connection_policy)

        database = client.get_database_client(self.configs.TEST_DATABASE_ID)
        container = database.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

        # When EnableEndpointDiscovery is True, WriteEndpoint is set to the write endpoint
        created_document = container.create_item(document_definition)
        if is_not_default_host(TestGlobalDB.write_location_host):
            self.assertEqual(client.client_connection.WriteEndpoint, TestGlobalDB.write_location_host)

        # Delay to get these resources replicated to read location due to Eventual consistency
        time.sleep(5)

        container.read_item(item=created_document, partition_key=created_document['pk'])
        content_location = str(client.client_connection.last_response_headers[HttpHeaders.ContentLocation])

        content_location_url = urlparse(content_location)
        write_location_url = urlparse(TestGlobalDB.write_location_host)

        # If no preferred locations is set, we return the write endpoint as ReadEndpoint for better latency performance
        if is_not_default_host(TestGlobalDB.write_location_host):
            self.assertEqual(str(content_location_url.hostname), str(write_location_url.hostname))
            self.assertEqual(client.client_connection.ReadEndpoint, TestGlobalDB.write_location_host)

    def test_global_db_endpoint_discovery(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.EnableEndpointDiscovery = False

        read_location_client = cosmos_client.CosmosClient(self.read_location_host,
                                                          self.masterKey,
                                                          connection_policy=connection_policy)

        document_definition = {'id': 'doc1',
                               'name': 'sample document',
                               'key': 'value'}

        database = read_location_client.get_database_client(self.configs.TEST_DATABASE_ID)
        container = database.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

        # Create Document will fail for the read location client since it has EnableEndpointDiscovery set to false, and hence the request will directly go to
        # the endpoint that was used to create the client instance(which happens to be a read endpoint)
        if is_not_default_host(self.read_location_host):
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
        read_location_client = cosmos_client.CosmosClient(self.read_location_host,
                                                          self.masterKey,
                                                          connection_policy=connection_policy)

        database = read_location_client.get_database_client(self.configs.TEST_DATABASE_ID)
        container = database.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

        # CreateDocument call will go to the WriteEndpoint as EnableEndpointDiscovery is set to True and client will resolve the right endpoint based on the operation
        created_document = container.create_item(document_definition)
        self.assertEqual(created_document['id'], document_definition['id'])

    def test_global_db_preferred_locations(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.EnableEndpointDiscovery = True

        client = cosmos_client.CosmosClient(self.host, self.masterKey,
                                            connection_policy=connection_policy)

        document_definition = {'id': 'doc3',
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}

        database = client.get_database_client(self.configs.TEST_DATABASE_ID)
        container = database.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

        created_document = container.create_item(document_definition)
        self.assertEqual(created_document['id'], document_definition['id'])

        # Delay to get these resources replicated to read location due to Eventual consistency
        time.sleep(5)

        item = container.read_item(item=created_document, partition_key=created_document['pk'])
        content_location = str(client.client_connection.last_response_headers[HttpHeaders.ContentLocation])

        content_location_url = urlparse(content_location)
        write_location_url = urlparse(self.write_location_host)

        # If no preferred locations is set, we return the write endpoint as ReadEndpoint for better latency performance
        if is_not_default_host(self.write_location_host):
            self.assertEqual(str(content_location_url.hostname), str(write_location_url.hostname))
            self.assertEqual(client.client_connection.ReadEndpoint, self.write_location_host)

        if is_not_default_host(self.read_location2):  # Client init will fail if no read location given
            connection_policy.PreferredLocations = [self.read_location2]

            client = cosmos_client.CosmosClient(self.host, self.masterKey,
                                                connection_policy=connection_policy)

            database = client.get_database_client(self.configs.TEST_DATABASE_ID)
            container = database.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

            document_definition['id'] = 'doc4'
            created_document = container.create_item(document_definition)

            # Delay to get these resources replicated to read location due to Eventual consistency
            time.sleep(5)

            container.read_item(item=created_document, partition_key=created_document['pk'])
            content_location = str(client.client_connection.last_response_headers[HttpHeaders.ContentLocation])

            content_location_url = urlparse(content_location)
            read_location2_url = urlparse(self.read_location2_host)

            # Test that the preferred location is set as ReadEndpoint instead of default write endpoint when no preference is set
            self.assertEqual(str(content_location_url.hostname), str(read_location2_url.hostname))
            self.assertEqual(client.client_connection.ReadEndpoint, self.read_location2_host)

    def test_global_db_endpoint_assignments(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.EnableEndpointDiscovery = False

        client = cosmos_client.CosmosClient(self.host, self.masterKey,
                                            connection_policy=connection_policy)

        # When EnableEndpointDiscovery is set to False, both Read and Write Endpoints point to endpoint passed while creating the client instance
        self.assertEqual(client.client_connection.WriteEndpoint, self.host)
        self.assertEqual(client.client_connection.ReadEndpoint, self.host)

        connection_policy.EnableEndpointDiscovery = True
        client = cosmos_client.CosmosClient(self.host, self.masterKey,
                                            connection_policy=connection_policy)

        # If no preferred locations is set, we return the write endpoint as ReadEndpoint for better latency performance, write endpoint is set as expected
        self.assertEqual(client.client_connection.WriteEndpoint,
                         client.client_connection.ReadEndpoint)
        if is_not_default_host(self.write_location_host):
            self.assertEqual(client.client_connection.WriteEndpoint,
                             self.write_location_host)

        if is_not_default_host(self.read_location2):
            connection_policy.PreferredLocations = [self.read_location2]
            client = cosmos_client.CosmosClient(self.host, self.masterKey,
                                                connection_policy=connection_policy)

            # Test that the preferred location is set as ReadEndpoint instead of default write endpoint when no preference is set
            self.assertEqual(client.client_connection._global_endpoint_manager.WriteEndpoint,
                             self.write_location_host)
            self.assertEqual(client.client_connection._global_endpoint_manager.ReadEndpoint,
                             self.read_location2_host)

    def test_global_db_update_locations_cache(self):
        client = cosmos_client.CosmosClient(self.host, self.masterKey)

        writable_locations = [{'name': self.write_location,
                               'databaseAccountEndpoint': self.write_location_host}]
        readable_locations = [{'name': self.read_location,
                               'databaseAccountEndpoint': self.read_location_host},
                              {'name': self.read_location2,
                               'databaseAccountEndpoint': self.read_location2_host}]

        if (is_not_default_host(self.write_location_host)
                and is_not_default_host(self.read_location_host)
                and is_not_default_host(self.read_location2_host)):
            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(
                writable_locations, readable_locations)

            # If no preferred locations is set, we return the write endpoint as ReadEndpoint for better latency performance, write endpoint is set as expected
            self.assertEqual(write_endpoint, self.write_location_host)
            self.assertEqual(read_endpoint, self.write_location_host)

            writable_locations = []
            readable_locations = []

            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(
                writable_locations, readable_locations)

            # If writable_locations and readable_locations are empty, both Read and Write Endpoints point to endpoint passed while creating the client instance
            self.assertEqual(write_endpoint, self.host)
            self.assertEqual(read_endpoint, self.host)

            writable_locations = [{'name': self.write_location,
                                   'databaseAccountEndpoint': self.write_location_host}]
            readable_locations = []

            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(
                writable_locations, readable_locations)

            # If there are no readable_locations, we use the write endpoint as ReadEndpoint
            self.assertEqual(write_endpoint, self.write_location_host)
            self.assertEqual(read_endpoint, self.write_location_host)

            writable_locations = []
            readable_locations = [{'name': self.read_location,
                                   'databaseAccountEndpoint': self.read_location_host}]

            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(
                writable_locations, readable_locations)

            # If there are no writable_locations, both Read and Write Endpoints point to endpoint passed while creating the client instance
            self.assertEqual(write_endpoint, self.host)
            self.assertEqual(read_endpoint, self.host)

            writable_locations = [{'name': self.write_location,
                                   'databaseAccountEndpoint': self.write_location_host}]
            readable_locations = [{'name': self.read_location,
                                   'databaseAccountEndpoint': self.read_location_host},
                                  {'name': self.read_location2,
                                   'databaseAccountEndpoint': self.read_location2_host}]

            connection_policy = documents.ConnectionPolicy()
            connection_policy.PreferredLocations = [self.read_location2]

            client = cosmos_client.CosmosClient(self.host, self.masterKey,
                                                connection_policy=connection_policy)

            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(
                writable_locations, readable_locations)

            # Test that the preferred location is set as ReadEndpoint instead of default write endpoint when no preference is set
            self.assertEqual(write_endpoint, self.write_location_host)
            self.assertEqual(read_endpoint, self.read_location2_host)

            writable_locations = [{'name': self.write_location,
                                   'databaseAccountEndpoint': self.write_location_host},
                                  {'name': self.read_location2,
                                   'databaseAccountEndpoint': self.read_location2_host}]
            readable_locations = [{'name': self.read_location,
                                   'databaseAccountEndpoint': self.read_location_host}]

            connection_policy = documents.ConnectionPolicy()
            connection_policy.PreferredLocations = [self.read_location2]

            client = cosmos_client.CosmosClient(self.host, self.masterKey,
                                                connection_policy=connection_policy)

            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(
                writable_locations, readable_locations)

            # Test that the preferred location is chosen from the WriteLocations if it's not present in the ReadLocations
            self.assertEqual(write_endpoint, self.write_location_host)
            self.assertEqual(read_endpoint, self.read_location2_host)

            writable_locations = [{'name': self.write_location,
                                   'databaseAccountEndpoint': self.write_location_host}]
            readable_locations = [{'name': self.read_location,
                                   'databaseAccountEndpoint': self.read_location_host},
                                  {'name': self.read_location2,
                                   'databaseAccountEndpoint': self.read_location2_host}]

            connection_policy.EnableEndpointDiscovery = False
            client = cosmos_client.CosmosClient(self.host, self.masterKey,
                                                connection_policy=connection_policy)

            write_endpoint, read_endpoint = client.client_connection._global_endpoint_manager.location_cache.update_location_cache(
                writable_locations, readable_locations)

            # If EnableEndpointDiscovery is False, both Read and Write Endpoints point to endpoint passed while creating the client instance
            self.assertEqual(write_endpoint, self.host)
            self.assertEqual(read_endpoint, self.host)

    def test_global_db_locational_endpoint_parser(self):
        url_endpoint = 'https://contoso.documents.azure.com:443/'
        location_name = 'East US'

        # Creating a locational endpoint from the location name using the parser method
        locational_endpoint = global_endpoint_manager._GlobalEndpointManager.GetLocationalEndpoint(url_endpoint,
                                                                                                   location_name)
        self.assertEqual(locational_endpoint, 'https://contoso-EastUS.documents.azure.com:443/')

        url_endpoint = 'https://Contoso.documents.azure.com:443/'
        location_name = 'East US'

        # Note that the host name gets lowercased as the urlparser in Python doesn't retains the casing
        locational_endpoint = global_endpoint_manager._GlobalEndpointManager.GetLocationalEndpoint(url_endpoint,
                                                                                                   location_name)
        self.assertEqual(locational_endpoint, 'https://contoso-EastUS.documents.azure.com:443/')

    def test_global_db_endpoint_discovery_retry_policy_mock(self):
        client = cosmos_client.CosmosClient(self.host, self.masterKey)

        self.OriginalExecuteFunction = _retry_utility.ExecuteFunction
        _retry_utility.ExecuteFunction = _mock_execute_function

        self.OriginalGetDatabaseAccount = client.client_connection.GetDatabaseAccount
        client.client_connection.GetDatabaseAccount = _mock_get_database_account

        max_retry_attempt_count = 10
        retry_after_in_milliseconds = 500

        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Max_retry_attempt_count = max_retry_attempt_count
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Retry_after_in_milliseconds = (
            retry_after_in_milliseconds)

        document_definition = {'id': 'doc7',
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}

        database = client.get_database_client(self.configs.TEST_DATABASE_ID)
        container = database.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

        self.__AssertHTTPFailureWithStatus(
            StatusCodes.FORBIDDEN,
            SubStatusCodes.WRITE_FORBIDDEN,
            container.create_item,
            document_definition)

        _retry_utility.ExecuteFunction = self.OriginalExecuteFunction


if __name__ == '__main__':
    unittest.main()
