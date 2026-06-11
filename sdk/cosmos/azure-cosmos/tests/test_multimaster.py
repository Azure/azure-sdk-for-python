# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import unittest
import uuid

import pytest

import azure.cosmos._constants as constants
import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import _retry_utility
from azure.cosmos.http_constants import HttpHeaders


@pytest.mark.cosmosEmulator
class TestMultiMaster(unittest.TestCase):
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    counter = 0
    last_headers = []
    configs = test_config.TestConfig

    def test_tentative_writes_header_present(self):
        self.last_headers = []
        self.EnableMultipleWritableLocations = True
        self._validate_tentative_write_headers()
        TestMultiMaster.connectionPolicy.UseMultipleWriteLocations = False

    def test_tentative_writes_header_not_present(self):
        self.last_headers = []
        self.EnableMultipleWritableLocations = False
        self._validate_tentative_write_headers()
        TestMultiMaster.connectionPolicy.UseMultipleWriteLocations = False

    def _validate_tentative_write_headers(self):
        self.counter = 0  # Reset counter for each test run
        self.OriginalExecuteFunction = _retry_utility.ExecuteFunction
        _retry_utility.ExecuteFunction = self._MockExecuteFunction
        try:
            connectionPolicy = TestMultiMaster.connectionPolicy
            connectionPolicy.UseMultipleWriteLocations = True
            client = cosmos_client.CosmosClient(TestMultiMaster.host, TestMultiMaster.masterKey,
                                                consistency_level="Session",
                                                connection_policy=connectionPolicy)

            created_db = client.get_database_client(self.configs.TEST_DATABASE_ID)

            created_collection = created_db.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

            document_definition = {'id': 'doc' + str(uuid.uuid4()),
                                   'pk': 'pk',
                                   'name': 'sample document',
                                   'operation': 'insertion'}
            created_document = created_collection.create_item(body=document_definition)

            sproc_definition = {
                'id': 'sample sproc' + str(uuid.uuid4()),
                'serverScript': 'function() {var x = 10;}'
            }
            sproc = created_collection.scripts.create_stored_procedure(body=sproc_definition)

            created_collection.scripts.execute_stored_procedure(
                sproc=sproc['id'],
                partition_key='pk'
            )

            created_collection.read_item(
                item=created_document,
                partition_key='pk'
            )

            created_document['operation'] = 'replace'
            replaced_document = created_collection.replace_item(
                item=created_document['id'],
                body=created_document
            )

            replaced_document['operation'] = 'upsert'
            upserted_document = created_collection.upsert_item(body=replaced_document)

            created_collection.delete_item(
                item=upserted_document,
                partition_key='pk'
            )

            is_allow_tentative_writes_set = self.EnableMultipleWritableLocations is True

            # Count operations with the tentative writes header
            headers_with_tentative_writes = sum(1 for h in self.last_headers if h)

            if is_allow_tentative_writes_set:
                # When multi-write is enabled, at least 6 write operations should have the header:
                # create_item, create_stored_procedure, execute_stored_procedure,
                # replace_item, upsert_item, delete_item
                self.assertGreaterEqual(headers_with_tentative_writes, 6,
                    f"Expected at least 6 write operations with tentative writes header, "
                    f"got {headers_with_tentative_writes}")
            else:
                # When multi-write is disabled, no operations should have the header
                self.assertEqual(headers_with_tentative_writes, 0,
                    f"Expected 0 operations with tentative writes header, "
                    f"got {headers_with_tentative_writes}")
        finally:
            _retry_utility.ExecuteFunction = self.OriginalExecuteFunction

    def _MockExecuteFunction(self, function, *args, **kwargs):
        self.counter += 1
        if self.counter == 1:
            return {constants._Constants.EnableMultipleWritableLocations: self.EnableMultipleWritableLocations}, {}
        else:
            if len(args) > 0:
                self.last_headers.append(HttpHeaders.AllowTentativeWrites in args[4].headers
                                         and args[4].headers[HttpHeaders.AllowTentativeWrites] == 'true')
            return self.OriginalExecuteFunction(function, *args, **kwargs)


if __name__ == '__main__':
    unittest.main()
