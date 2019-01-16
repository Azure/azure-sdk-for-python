import json
import os.path
import unittest
import uuid
import azure.cosmos.cosmos_client_connection as cosmos_client_connection
import azure.cosmos.documents as documents
import azure.cosmos.errors as errors
import azure.cosmos.base as base
import azure.cosmos.constants as constants
import azure.cosmos.retry_options as retry_options
from azure.cosmos.http_constants import HttpHeaders, StatusCodes, SubStatusCodes
import azure.cosmos.retry_utility as retry_utility
import test.test_config as test_config

class MultiMasterTests(unittest.TestCase):

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy
    test_db_name = 'sample database' 
    test_coll_name = 'sample collection ' + str(uuid.uuid4())
    counter = 0
    last_headers = []

    @classmethod
    def cleanUpTestDatabase(cls):
        global client
        client = cosmos_client_connection.CosmosClientConnection(cls.host,
                                                {'masterKey': cls.masterKey}, cls.connectionPolicy)
        query_iterable = client.QueryDatabases('SELECT * FROM root r WHERE r.id=\'' + cls.test_db_name + '\'')
        it = iter(query_iterable)

        test_db = next(it, None)
        if test_db is not None:
            client.DeleteDatabase(test_db['_self'])

    @classmethod
    def tearDownClass(cls):
        MultiMasterTests.cleanUpTestDatabase()

    def setUp(self):
        MultiMasterTests.cleanUpTestDatabase()
        self.created_db = client.CreateDatabase({ 'id': self.test_db_name })

        collection_definition = { 'id': self.test_coll_name, 'partitionKey': {'paths': ['/pk'],'kind': 'Hash'} }
        collection_options = { 'offerThroughput': 10100 }
        self.created_collection = client.CreateContainer(self.created_db['_self'], collection_definition, collection_options)

    def test_tentative_writes_header_present(self):
        self.last_headers = []
        self.EnableMultipleWritableLocations = True
        self._validate_tentative_write_headers()
        
    def test_tentative_writes_header_not_present(self):
        self.last_headers = []
        self.EnableMultipleWritableLocations = False
        self._validate_tentative_write_headers()

    def _validate_tentative_write_headers(self):
        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunction

        connectionPolicy = MultiMasterTests.connectionPolicy
        connectionPolicy.UseMultipleWriteLocations = True
        client = cosmos_client_connection.CosmosClientConnection(MultiMasterTests.host, {'masterKey': MultiMasterTests.masterKey}, connectionPolicy)

        document_definition = { 'id': 'doc',
                                'pk': 'pk',
                                'name': 'sample document',
                                'operation': 'insertion'}
        created_document = client.CreateItem(self.created_collection['_self'], document_definition)

        sproc_definition = {
            'id': 'sample sproc',
            'serverScript': 'function() {var x = 10;}'
        }
        sproc = client.CreateStoredProcedure(self.created_collection['_self'], sproc_definition)

        client.ExecuteStoredProcedure(sproc['_self'], None, {'partitionKey':'pk'})

        client.ReadItem(created_document['_self'], {'partitionKey':'pk'})

        created_document['operation'] = 'replace'
        replaced_document = client.ReplaceItem(created_document['_self'], created_document)

        replaced_document['operation'] = 'upsert'
        upserted_document = client.UpsertItem(self.created_collection['_self'], replaced_document)

        client.DeleteItem(upserted_document['_self'], {'partitionKey':'pk'})

        is_allow_tentative_writes_set = self.EnableMultipleWritableLocations == True
        # Create Document - Makes one initial call to fetch collection
        self.assertEqual(self.last_headers[0], is_allow_tentative_writes_set)
        self.assertEqual(self.last_headers[1], is_allow_tentative_writes_set)

        # Create Stored procedure
        self.assertEqual(self.last_headers[2], is_allow_tentative_writes_set)

        # Execute Stored procedure
        self.assertEqual(self.last_headers[3], is_allow_tentative_writes_set)

        # Read Document
        self.assertEqual(self.last_headers[4], is_allow_tentative_writes_set)

        # Replace Document
        self.assertEqual(self.last_headers[5], is_allow_tentative_writes_set)

        # Upsert Document
        self.assertEqual(self.last_headers[6], is_allow_tentative_writes_set)

        # Delete Document
        self.assertEqual(self.last_headers[7], is_allow_tentative_writes_set)

        retry_utility._ExecuteFunction = self.OriginalExecuteFunction

    def _MockExecuteFunction(self, function, *args, **kwargs):
        self.counter += 1
        if self.counter == 1:
            return {constants._Constants.EnableMultipleWritableLocations: self.EnableMultipleWritableLocations}, {}
        else:
            if len(args) > 0:
                self.last_headers.append(HttpHeaders.AllowTentativeWrites in args[5]['headers'] 
                                         and args[5]['headers'][HttpHeaders.AllowTentativeWrites] == 'true')
            return self.OriginalExecuteFunction(function, *args, **kwargs)

if __name__ == '__main__':
    unittest.main()
