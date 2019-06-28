import json
import os.path
import unittest
import uuid
import pytest
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents
import azure.cosmos.errors as errors
import azure.cosmos.base as base
import azure.cosmos.constants as constants
import azure.cosmos.retry_options as retry_options
from azure.cosmos.http_constants import HttpHeaders, StatusCodes, SubStatusCodes
import azure.cosmos.retry_utility as retry_utility
import test_config

pytestmark = pytest.mark.cosmosEmulator

@pytest.mark.usefixtures("teardown")
class MultiMasterTests(unittest.TestCase):

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy
    counter = 0
    last_headers = []

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
        client = cosmos_client.CosmosClient(MultiMasterTests.host, {'masterKey': MultiMasterTests.masterKey}, connectionPolicy)
        
        created_collection = test_config._test_config.create_multi_partition_collection_with_custom_pk_if_not_exist(client)
        document_definition = { 'id': 'doc' + str(uuid.uuid4()),
                                'pk': 'pk',
                                'name': 'sample document',
                                'operation': 'insertion'}
        created_document = client.CreateItem(created_collection['_self'], document_definition)

        sproc_definition = {
            'id': 'sample sproc' + str(uuid.uuid4()),
            'serverScript': 'function() {var x = 10;}'
        }
        sproc = client.CreateStoredProcedure(created_collection['_self'], sproc_definition)

        client.ExecuteStoredProcedure(sproc['_self'], None, {'partitionKey':'pk'})

        client.ReadItem(created_document['_self'], {'partitionKey':'pk'})

        created_document['operation'] = 'replace'
        replaced_document = client.ReplaceItem(created_document['_self'], created_document)

        replaced_document['operation'] = 'upsert'
        upserted_document = client.UpsertItem(created_collection['_self'], replaced_document)

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
