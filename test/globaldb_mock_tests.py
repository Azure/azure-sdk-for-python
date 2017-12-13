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

import unittest
import json

import pydocumentdb.document_client as document_client
import pydocumentdb.documents as documents
import pydocumentdb.errors as errors
import pydocumentdb.constants as constants
import pydocumentdb.http_constants as http_constants
import pydocumentdb.global_endpoint_manager as global_endpoint_manager
import pydocumentdb.retry_utility as retry_utility
import test.test_config as test_config

location_changed = False

class MockGlobalEndpointManager:
    def __init__(self, client):
        self.Client = client
        self.DefaultEndpoint = client.url_connection        
        self._ReadEndpoint = client.url_connection
        self._WriteEndpoint = client.url_connection
        self.EnableEndpointDiscovery = client.connection_policy.EnableEndpointDiscovery
        self.IsEndpointCacheInitialized = False
        self.refresh_count = 0
        self.DatabaseAccountAvailable = True
    
    def RefreshEndpointList(self):
        global location_changed

        if not location_changed:
            database_account = self.GetDatabaseAccount1()
        else:
            database_account = self.GetDatabaseAccount2()

        if self.DatabaseAccountAvailable is False:
            database_account = None
            writable_locations = []
            readable_locations = []
        else:
            writable_locations = database_account.WritableLocations        
            readable_locations = database_account.ReadableLocations
        
        self._WriteEndpoint, self._ReadEndpoint = self.UpdateLocationsCache(writable_locations, readable_locations)

    @property
    def ReadEndpoint(self):
        if not self.IsEndpointCacheInitialized:
            self.RefreshEndpointList()

        return self._ReadEndpoint

    @property
    def WriteEndpoint(self):
        if not self.IsEndpointCacheInitialized:
            self.RefreshEndpointList()

        return self._WriteEndpoint

    def GetDatabaseAccount1(self):
        database_account = documents.DatabaseAccount()
        database_account._ReadableLocations = [{'name' : Test_globaldb_mock_tests.read_location, 'databaseAccountEndpoint' : Test_globaldb_mock_tests.read_location_host}]
        database_account._WritableLocations = [{'name' : Test_globaldb_mock_tests.write_location, 'databaseAccountEndpoint' : Test_globaldb_mock_tests.write_location_host}]
        
        return database_account

    def GetDatabaseAccount2(self):
        database_account = documents.DatabaseAccount()
        database_account._ReadableLocations = [{'name' : Test_globaldb_mock_tests.write_location, 'databaseAccountEndpoint' : Test_globaldb_mock_tests.write_location_host}]
        database_account._WritableLocations = [{'name' : Test_globaldb_mock_tests.read_location, 'databaseAccountEndpoint' : Test_globaldb_mock_tests.read_location_host}]
        
        return database_account

    def UpdateLocationsCache(self, writable_locations, readable_locations):
        if len(writable_locations) == 0:
            write_endpoint = self.DefaultEndpoint
        else:
            write_endpoint = writable_locations[0][constants._Constants.DatabaseAccountEndpoint]

        if len(readable_locations) == 0:
            read_endpoint = write_endpoint
        else:
            read_endpoint = writable_locations[0][constants._Constants.DatabaseAccountEndpoint]

        return write_endpoint, read_endpoint



class Test_globaldb_mock_tests(unittest.TestCase):
    
    host = test_config._test_config.global_host
    write_location_host = test_config._test_config.write_location_host
    read_location_host = test_config._test_config.read_location_host
    masterKey = test_config._test_config.global_masterKey

    write_location = test_config._test_config.write_location
    read_location = test_config._test_config.read_location

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_GLOBAL_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure DocumentDB account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    def setUp(self):
        self.endpoint_discovery_retry_count = 0
        
        # Copying the original objects and functions before assigning the mock versions of them
        self.OriginalGetDatabaseAccountStub = global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub
        self.OriginalGlobalEndpointManager = global_endpoint_manager._GlobalEndpointManager
        self.OriginalExecuteFunction = retry_utility._ExecuteFunction

        # Make pydocumentdb use the MockGlobalEndpointManager
        global_endpoint_manager._GlobalEndpointManager = MockGlobalEndpointManager

    def tearDown(self):
        # Restoring the original objects and functions
        global_endpoint_manager._GlobalEndpointManager = self.OriginalGlobalEndpointManager
        global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.OriginalGetDatabaseAccountStub
        retry_utility._ExecuteFunction = self.OriginalExecuteFunction
    
    def MockExecuteFunction(self, function, *args, **kwargs):
        global location_changed

        if self.endpoint_discovery_retry_count == 2:
            retry_utility._ExecuteFunction = self.OriginalExecuteFunction
            return (json.dumps([{ 'id': 'mock database' }]), None)
        else:
            self.endpoint_discovery_retry_count += 1
            location_changed = True
            raise errors.HTTPFailure(http_constants.HttpStatusCodes.FORBIDDEN, "Forbidden", {'x-ms-substatus' : 3})

    def MockGetDatabaseAccountStub(self, endpoint):
        raise errors.HTTPFailure(http_constants.HttpStatusCodes.SERVICE_UNAVAILABLE, "Service unavailable")
    
    def MockCreateDatabase(self, client, database):
        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self.MockExecuteFunction
        client.CreateDatabase(database)

    def test_globaldb_endpoint_discovery_retry_policy(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.EnableEndpointDiscovery = True

        write_location_client = document_client.DocumentClient(Test_globaldb_mock_tests.write_location_host, {'masterKey': Test_globaldb_mock_tests.masterKey}, connection_policy)
        self.assertEqual(write_location_client._global_endpoint_manager.WriteEndpoint, Test_globaldb_mock_tests.write_location_host)
        
        self.MockCreateDatabase(write_location_client, { 'id': 'mock database' })

        self.assertEqual(write_location_client._global_endpoint_manager.WriteEndpoint, Test_globaldb_mock_tests.read_location_host)

    def test_globaldb_database_account_unavailable(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.EnableEndpointDiscovery = True

        client = document_client.DocumentClient(Test_globaldb_mock_tests.host, {'masterKey': Test_globaldb_mock_tests.masterKey}, connection_policy)

        self.assertEqual(client._global_endpoint_manager.WriteEndpoint, Test_globaldb_mock_tests.write_location_host)
        self.assertEqual(client._global_endpoint_manager.ReadEndpoint, Test_globaldb_mock_tests.write_location_host)

        global_endpoint_manager._GlobalEndpointManager._GetDatabaseAccountStub = self.MockGetDatabaseAccountStub
        client._global_endpoint_manager.DatabaseAccountAvailable = False
        
        client._global_endpoint_manager.RefreshEndpointList()

        self.assertEqual(client._global_endpoint_manager.WriteEndpoint, Test_globaldb_mock_tests.host)
        self.assertEqual(client._global_endpoint_manager.ReadEndpoint, Test_globaldb_mock_tests.host)

if __name__ == '__main__':
    unittest.main()
