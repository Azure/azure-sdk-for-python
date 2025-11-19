# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test.
"""
import logging
import threading
import time
import unittest
import urllib.parse as urllib
import uuid
import os

import pytest
import requests
from azure.core import MatchConditions
from azure.core.exceptions import AzureError, ServiceResponseError, ServiceRequestError
from azure.core.pipeline.transport import RequestsTransport, RequestsTransportResponse
from urllib3.util.retry import Retry

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import _retry_utility
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.partition_key import PartitionKey


class TimeoutTransport(RequestsTransport):

    def __init__(self, response, passthrough=False):
        self._response = response
        self.passthrough = passthrough
        super(TimeoutTransport, self).__init__()

    def send(self, *args, **kwargs):
        if self.passthrough:
            return super(TimeoutTransport, self).send(*args, **kwargs)

        time.sleep(5)
        if isinstance(self._response, Exception):
            raise self._response
        output = requests.Response()
        output.status_code = self._response
        response = RequestsTransportResponse(None, output)
        return response

@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
class TestCRUDOperations(unittest.TestCase):
    """Python CRUD Tests.
    """

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []
    client: cosmos_client.CosmosClient = None

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            self.assertEqual(inst.status_code, status_code)

    @classmethod
    def setUpClass(cls):
        use_multiple_write_locations = False
        if os.environ.get("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER", "False") == "True":
            use_multiple_write_locations = True
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, multiple_write_locations=use_multiple_write_locations)
        cls.databaseForTest = cls.client.get_database_client(cls.configs.TEST_DATABASE_ID)

    def test_partitioned_collection_document_crud_and_query(self):
        created_db = self.databaseForTest

        created_collection = created_db.create_container("crud-query-container", partition_key=PartitionKey("/pk"))

        document_definition = {'id': 'document',
                               'key': 'value',
                               'pk': 'pk'}

        created_document = created_collection.create_item(
            body=document_definition
        )

        self.assertEqual(created_document.get('id'), document_definition.get('id'))
        self.assertEqual(created_document.get('key'), document_definition.get('key'))

        # read document
        read_document = created_collection.read_item(
            item=created_document.get('id'),
            partition_key=created_document.get('pk')
        )

        self.assertEqual(read_document.get('id'), created_document.get('id'))
        self.assertEqual(read_document.get('key'), created_document.get('key'))

        # Read document feed doesn't require partitionKey as it's always a cross partition query
        documentlist = list(created_collection.read_all_items())
        self.assertEqual(1, len(documentlist))

        # replace document
        document_definition['key'] = 'new value'

        replaced_document = created_collection.replace_item(
            item=read_document,
            body=document_definition
        )

        self.assertEqual(replaced_document.get('key'), document_definition.get('key'))

        # upsert document(create scenario)
        new_document_definition = {'id': 'document2',
                               'key': 'value2',
                               'pk': 'pk'}

        upserted_document = created_collection.upsert_item(body=new_document_definition)

        self.assertEqual(upserted_document.get('id'), new_document_definition.get('id'))
        self.assertEqual(upserted_document.get('key'), new_document_definition.get('key'))

        documentlist = list(created_collection.read_all_items())
        self.assertEqual(2, len(documentlist))

        # delete document
        created_collection.delete_item(item=upserted_document, partition_key=upserted_document.get('pk'))

        # query document on the partition key specified in the predicate will pass even without setting enableCrossPartitionQuery or passing in the partitionKey value
        documentlist = list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.id=\'' + replaced_document.get('id') + '\''  # nosec
            }, enable_cross_partition_query=True))
        self.assertEqual(1, len(documentlist))

        # query document on any property other than partitionKey will fail without setting enableCrossPartitionQuery or passing in the partitionKey value
        try:
            list(created_collection.query_items(
                {
                    'query': 'SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\''  # nosec
                }))
        except Exception:
            pass

        # cross partition query
        documentlist = list(created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            enable_cross_partition_query=True
        ))

        self.assertEqual(1, len(documentlist))

        # query document by providing the partitionKey value
        documentlist = list(created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            partition_key=replaced_document.get('pk')
        ))

        self.assertEqual(1, len(documentlist))
        created_db.delete_container(created_collection.id)

    def test_partitioned_collection_execute_stored_procedure(self):
        created_collection = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        document_id = str(uuid.uuid4())

        sproc = {
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': (
                    'function () {' +
                    '   var client = getContext().getCollection();' +
                    '   client.createDocument(client.getSelfLink(), { id: "' + document_id + '", pk : 2}, ' +
                    '   {}, function(err, docCreated, options) { ' +
                    '   if(err) throw new Error(\'Error while creating document: \' + err.message);' +
                    '   else {' +
                    '   getContext().getResponse().setBody(1);' +
                    '        }' +
                    '   });}')
        }

        created_sproc = created_collection.scripts.create_stored_procedure(sproc)

        # Partition Key value same as what is specified in the stored procedure body
        result = created_collection.scripts.execute_stored_procedure(sproc=created_sproc['id'], partition_key=2)
        self.assertEqual(result, 1)

        # Partition Key value different than what is specified in the stored procedure body will cause a bad request(400) error
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            created_collection.scripts.execute_stored_procedure,
            created_sproc['id'],
            3)

    def test_script_logging_execute_stored_procedure(self):
        created_collection = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        stored_proc_id = 'storedProcedure-1-' + str(uuid.uuid4())

        sproc = {
            'id': stored_proc_id,
            'body': (
                    'function () {' +
                    '   var mytext = \'x\';' +
                    '   var myval = 1;' +
                    '   try {' +
                    '       console.log(\'The value of %s is %s.\', mytext, myval);' +
                    '       getContext().getResponse().setBody(\'Success!\');' +
                    '   }' +
                    '   catch (err) {' +
                    '       getContext().getResponse().setBody(\'inline err: [\' + err.number + \'] \' + err);' +
                    '   }'
                    '}')
        }

        created_sproc = created_collection.scripts.create_stored_procedure(sproc)

        result = created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            partition_key=1
        )

        self.assertEqual(result, 'Success!')
        self.assertFalse(
            HttpHeaders.ScriptLogResults in created_collection.scripts.client_connection.last_response_headers)

        result = created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            enable_script_logging=True,
            partition_key=1
        )

        self.assertEqual(result, 'Success!')
        self.assertEqual(urllib.quote('The value of x is 1.'),
                         created_collection.scripts.client_connection.last_response_headers.get(
                             HttpHeaders.ScriptLogResults))

        result = created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            enable_script_logging=False,
            partition_key=1
        )

        self.assertEqual(result, 'Success!')
        self.assertFalse(
            HttpHeaders.ScriptLogResults in created_collection.scripts.client_connection.last_response_headers)

    def test_stored_procedure_functionality(self):
        # create database
        db = self.databaseForTest
        # create collection
        collection = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        stored_proc_id = 'storedProcedure-1-' + str(uuid.uuid4())

        sproc1 = {
            'id': stored_proc_id,
            'body': (
                    'function () {' +
                    '  for (var i = 0; i < 1000; i++) {' +
                    '    var item = getContext().getResponse().getBody();' +
                    '    if (i > 0 && item != i - 1) throw \'body mismatch\';' +
                    '    getContext().getResponse().setBody(i);' +
                    '  }' +
                    '}')
        }

        retrieved_sproc = collection.scripts.create_stored_procedure(sproc1)
        result = collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc['id'],
            partition_key=1
        )
        self.assertEqual(result, 999)
        stored_proc_id_2 = 'storedProcedure-2-' + str(uuid.uuid4())
        sproc2 = {
            'id': stored_proc_id_2,
            'body': (
                    'function () {' +
                    '  for (var i = 0; i < 10; i++) {' +
                    '    getContext().getResponse().appendValue(\'Body\', i);' +
                    '  }' +
                    '}')
        }
        retrieved_sproc2 = collection.scripts.create_stored_procedure(sproc2)
        result = collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc2['id'],
            partition_key=1
        )
        self.assertEqual(int(result), 123456789)
        stored_proc_id_3 = 'storedProcedure-3-' + str(uuid.uuid4())
        sproc3 = {
            'id': stored_proc_id_3,
            'body': (
                    'function (input) {' +
                    '  getContext().getResponse().setBody(' +
                    '      \'a\' + input.temp);' +
                    '}')
        }
        retrieved_sproc3 = collection.scripts.create_stored_procedure(sproc3)
        result = collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc3['id'],
            params={'temp': 'so'},
            partition_key=1
        )
        self.assertEqual(result, 'aso')

    def test_partitioned_collection_permissions(self):
        created_db = self.databaseForTest

        collection_id = 'test_partitioned_collection_permissions all collection' + str(uuid.uuid4())

        all_collection = created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/key', kind=documents.PartitionKind.Hash)
        )

        collection_id = 'test_partitioned_collection_permissions read collection' + str(uuid.uuid4())

        read_collection = created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/key', kind=documents.PartitionKind.Hash)
        )

        user = created_db.create_user(body={'id': 'user' + str(uuid.uuid4())})

        permission_definition = {
            'id': 'all permission',
            'permissionMode': documents.PermissionMode.All,
            'resource': all_collection.container_link,
            'resourcePartitionKey': [1]
        }

        all_permission = user.create_permission(body=permission_definition)

        permission_definition = {
            'id': 'read permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': read_collection.container_link,
            'resourcePartitionKey': [1]
        }

        read_permission = user.create_permission(body=permission_definition)

        resource_tokens = {}
        # storing the resource tokens based on Resource IDs
        resource_tokens["dbs/" + created_db.id + "/colls/" + all_collection.id] = (all_permission.properties['_token'])
        resource_tokens["dbs/" + created_db.id + "/colls/" + read_collection.id] = (
            read_permission.properties['_token'])

        restricted_client = cosmos_client.CosmosClient(
            TestCRUDOperations.host, resource_tokens, "Session", connection_policy=TestCRUDOperations.connectionPolicy)

        document_definition = {'id': 'document1',
                               'key': 1
                               }

        all_collection.client_connection = restricted_client.client_connection
        read_collection.client_connection = restricted_client.client_connection

        # Create document in all_collection should succeed since the partitionKey is 1 which is what specified as resourcePartitionKey in permission object and it has all permissions
        created_document = all_collection.create_item(body=document_definition)

        # Create document in read_collection should fail since it has only read permissions for this collection
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.FORBIDDEN,
            read_collection.create_item,
            document_definition)

        document_definition['key'] = 2
        # Create document should fail since the partitionKey is 2 which is different that what is specified as resourcePartitionKey in permission object
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.FORBIDDEN,
            all_collection.create_item,
            document_definition)

        document_definition['key'] = 1
        # Delete document should succeed since the partitionKey is 1 which is what specified as resourcePartitionKey in permission object
        created_document = all_collection.delete_item(item=created_document['id'],
                                                      partition_key=document_definition['key'])

        # Delete document in read_collection should fail since it has only read permissions for this collection
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.FORBIDDEN,
            read_collection.delete_item,
            document_definition['id'],
            document_definition['id']
        )

        created_db.delete_container(all_collection)
        created_db.delete_container(read_collection)

    def test_partitioned_collection_partition_key_value_types(self):
        created_db = self.databaseForTest

        created_collection = created_db.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': None,
                               'spam': 'eggs'}

        # create document with partitionKey set as None here
        created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'spam': 'eggs'}

        # create document with partitionKey set as Undefined here
        created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': True,
                               'spam': 'eggs'}

        # create document with bool partitionKey
        created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 'value',
                               'spam': 'eggs'}

        # create document with string partitionKey
        created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 100,
                               'spam': 'eggs'}

        # create document with int partitionKey
        created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 10.50,
                               'spam': 'eggs'}

        # create document with float partitionKey
        created_collection.create_item(body=document_definition)

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'pk': 'value'}

        # Should throw an error because automatic id generation is disabled always.
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            created_collection.create_item,
            document_definition
        )

    def test_document_crud(self):
        # create database
        created_db = self.databaseForTest
        # create collection
        created_collection = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # read documents
        documents = list(created_collection.read_all_items())
        # create a document
        before_create_documents_count = len(documents)

        # create a document with auto ID generation
        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk'}

        no_response = created_collection.create_item(body=document_definition, enable_automatic_id_generation=True, no_response=True)
        self.assertDictEqual(no_response, {})

        created_document = created_collection.create_item(body=document_definition, enable_automatic_id_generation=True)
        self.assertEqual(created_document.get('name'),
                         document_definition['name'])

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk',
                               'id': str(uuid.uuid4())}

        created_document = created_collection.create_item(body=document_definition)
        self.assertEqual(created_document.get('name'),
                         document_definition['name'])
        self.assertEqual(created_document.get('id'),
                         document_definition['id'])

        # duplicated documents are not allowed when 'id' is provided.
        duplicated_definition_with_id = document_definition.copy()
        self.__AssertHTTPFailureWithStatus(StatusCodes.CONFLICT,
                                           created_collection.create_item,
                                           duplicated_definition_with_id)
        # read documents after creation
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 3,
            'create should increase the number of documents')
        # query documents
        documents = list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.name=@name',
                'parameters': [
                    {'name': '@name', 'value': document_definition['name']}
                ]
            }, enable_cross_partition_query=True
        ))
        self.assertTrue(documents)
        documents = list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.name=@name',
                'parameters': [
                    {'name': '@name', 'value': document_definition['name']}
                ],
            }, enable_cross_partition_query=True,
            enable_scan_in_query=True
        ))
        self.assertTrue(documents)
        # replace document.
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'
        old_etag = created_document['_etag']
        replaced_document = created_collection.replace_item(
            item=created_document['id'],
            body=created_document
        )
        self.assertEqual(replaced_document['name'],
                         'replaced document',
                         'document id property should change')
        self.assertEqual(replaced_document['spam'],
                         'not eggs',
                         'property should have changed')
        self.assertEqual(created_document['id'],
                         replaced_document['id'],
                         'document id should stay the same')

        # replace document based on condition
        replaced_document['name'] = 'replaced document based on condition'
        replaced_document['spam'] = 'new spam field'

        # should fail for stale etag
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.PRECONDITION_FAILED,
            created_collection.replace_item,
            replaced_document['id'],
            replaced_document,
            if_match=old_etag,
        )

        # should fail if only etag specified
        with self.assertRaises(ValueError):
            created_collection.replace_item(
                etag=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document
            )

        # should fail if only match condition specified
        with self.assertRaises(ValueError):
            created_collection.replace_item(
                match_condition=MatchConditions.IfNotModified,
                item=replaced_document['id'],
                body=replaced_document
            )
        with self.assertRaises(ValueError):
            created_collection.replace_item(
                match_condition=MatchConditions.IfModified,
                item=replaced_document['id'],
                body=replaced_document
            )

        # should fail if invalid match condition specified
        with self.assertRaises(TypeError):
            created_collection.replace_item(
                match_condition=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document
            )

        # should pass for most recent etag
        replaced_document_conditional = created_collection.replace_item(
            match_condition=MatchConditions.IfNotModified,
            etag=replaced_document['_etag'],
            item=replaced_document['id'],
            body=replaced_document
        )
        self.assertEqual(replaced_document_conditional['name'],
                         'replaced document based on condition',
                         'document id property should change')
        self.assertEqual(replaced_document_conditional['spam'],
                         'new spam field',
                         'property should have changed')
        self.assertEqual(replaced_document_conditional['id'],
                         replaced_document['id'],
                         'document id should stay the same')
        # read document
        one_document_from_read = created_collection.read_item(
            item=replaced_document['id'],
            partition_key=replaced_document['pk']
        )
        self.assertEqual(replaced_document['id'],
                         one_document_from_read['id'])
        # delete document
        created_collection.delete_item(
            item=replaced_document,
            partition_key=replaced_document['pk']
        )
        # read documents after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           created_collection.read_item,
                                           replaced_document['id'],
                                           replaced_document['id'])

    def test_read_collection_only_once(self):
        # Add filter to the filtered diagnostics handler
        mock_handler = test_config.MockHandler()
        logger = logging.getLogger("azure.cosmos")
        logger.setLevel(logging.INFO)
        logger.addHandler(mock_handler)

        client = cosmos_client.CosmosClient(self.host, self.masterKey)
        database = client.get_database_client(self.configs.TEST_DATABASE_ID)
        container = database.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

        def upsert_worker():
            # Synchronously perform the upsert item operation
            container.upsert_item(body={'id': str(uuid.uuid4()), 'name': f'sample-'})

        # Perform 10 concurrent upserts
        threads = []
        for i in range(10):
            t = threading.Thread(target=upsert_worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        assert sum("'x-ms-thinclient-proxy-resource-type': 'colls'" in response.message for response in mock_handler.messages) == 1


    def test_document_upsert(self):
        # create database
        created_db = self.databaseForTest

        # create collection
        created_collection = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # read documents and check count
        documents = list(created_collection.read_all_items())
        before_create_documents_count = len(documents)

        # create document definition
        document_definition = {'id': 'doc',
                               'name': 'sample document',
                               'spam': 'eggs',
                               'pk': 'pk',
                               'key': 'value'}

        # create document using Upsert API
        created_document = created_collection.upsert_item(body=document_definition)

        # verify id property
        self.assertEqual(created_document['id'],
                         document_definition['id'])

        # test error for non-string id
        with self.assertRaises(TypeError):
            document_definition['id'] = 7
            created_collection.upsert_item(body=document_definition)

        # read documents after creation and verify updated count
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'create should increase the number of documents')

        # update document
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'

        # should replace document since it already exists
        upserted_document = created_collection.upsert_item(body=created_document)

        # verify the changed properties
        self.assertEqual(upserted_document['name'],
                         created_document['name'],
                         'document name property should change')
        self.assertEqual(upserted_document['spam'],
                         created_document['spam'],
                         'property should have changed')

        # verify id property
        self.assertEqual(upserted_document['id'],
                         created_document['id'],
                         'document id should stay the same')

        # read documents after upsert and verify count doesn't increases again
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'number of documents should remain same')

        created_document['id'] = 'new id'

        # Upsert should create new document since the id is different
        new_document = created_collection.upsert_item(body=created_document)

        # Test modified access conditions
        created_document['spam'] = 'more eggs'
        created_collection.upsert_item(body=created_document)
        with self.assertRaises(exceptions.CosmosHttpResponseError):
            created_collection.upsert_item(
                body=created_document,
                match_condition=MatchConditions.IfNotModified,
                etag=new_document['_etag'])

        # verify id property
        self.assertEqual(created_document['id'],
                         new_document['id'],
                         'document id should be same')

        # read documents after upsert and verify count increases
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 2,
            'upsert should increase the number of documents')

        # delete documents
        created_collection.delete_item(item=upserted_document, partition_key=upserted_document['pk'])
        created_collection.delete_item(item=new_document, partition_key=new_document['pk'])

        # read documents after delete and verify count is same as original
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count,
            'number of documents should remain same')

    def test_geospatial_index(self):
        db = self.databaseForTest
        # partial policy specified
        collection = db.create_container(
            id='collection with spatial index ' + str(uuid.uuid4()),
            indexing_policy={
                'includedPaths': [
                    {
                        'path': '/"Location"/?',
                        'indexes': [
                            {
                                'kind': 'Spatial',
                                'dataType': 'Point'
                            }
                        ]
                    },
                    {
                        'path': '/'
                    }
                ]
            },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        collection.create_item(
            body={
                'id': 'loc1',
                'Location': {
                    'type': 'Point',
                    'coordinates': [20.0, 20.0]
                }
            }
        )
        collection.create_item(
            body={
                'id': 'loc2',
                'Location': {
                    'type': 'Point',
                    'coordinates': [100.0, 100.0]
                }
            }
        )
        results = list(collection.query_items(
            query="SELECT * FROM root WHERE (ST_DISTANCE(root.Location, {type: 'Point', coordinates: [20.1, 20]}) < 20000)",
            enable_cross_partition_query=True
        ))
        self.assertEqual(1, len(results))
        self.assertEqual('loc1', results[0]['id'])

        db.delete_container(container=collection)

    # CRUD test for User resource
    def test_user_crud(self):
        # Should do User CRUD operations successfully.
        # create database
        db = self.databaseForTest
        # list users
        users = list(db.list_users())
        before_create_count = len(users)
        # create user
        user_id = 'new user' + str(uuid.uuid4())
        user = db.create_user(body={'id': user_id})
        self.assertEqual(user.id, user_id, 'user id error')
        # list users after creation
        users = list(db.list_users())
        self.assertEqual(len(users), before_create_count + 1)
        # query users
        results = list(db.query_users(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': user_id}
            ]
        ))
        self.assertTrue(results)

        # replace user
        replaced_user_id = 'replaced user' + str(uuid.uuid4())
        user_properties = user.read()
        user_properties['id'] = replaced_user_id
        replaced_user = db.replace_user(user_id, user_properties)
        self.assertEqual(replaced_user.id,
                         replaced_user_id,
                         'user id should change')
        self.assertEqual(user_properties['id'],
                         replaced_user.id,
                         'user id should stay the same')
        # read user
        user = db.get_user_client(replaced_user.id)
        self.assertEqual(replaced_user.id, user.id)
        # delete user
        db.delete_user(user.id)
        # read user after deletion
        deleted_user = db.get_user_client(user.id)
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           deleted_user.read)

    def test_user_upsert(self):
        # create database
        db = self.databaseForTest

        # read users and check count
        users = list(db.list_users())
        before_create_count = len(users)

        # create user using Upsert API
        user_id = 'user' + str(uuid.uuid4())
        user = db.upsert_user(body={'id': user_id})

        # verify id property
        self.assertEqual(user.id, user_id, 'user id error')

        # read users after creation and verify updated count
        users = list(db.list_users())
        self.assertEqual(len(users), before_create_count + 1)

        # Should replace the user since it already exists, there is no public property to change here
        user_properties = user.read()
        upserted_user = db.upsert_user(user_properties)

        # verify id property
        self.assertEqual(upserted_user.id,
                         user.id,
                         'user id should remain same')

        # read users after upsert and verify count doesn't increases again
        users = list(db.list_users())
        self.assertEqual(len(users), before_create_count + 1)

        user_properties = user.read()
        user_properties['id'] = 'new user' + str(uuid.uuid4())
        user.id = user_properties['id']

        # Upsert should create new user since id is different
        new_user = db.upsert_user(user_properties)

        # verify id property
        self.assertEqual(new_user.id, user.id, 'user id error')

        # read users after upsert and verify count increases
        users = list(db.list_users())
        self.assertEqual(len(users), before_create_count + 2)

        # delete users
        db.delete_user(upserted_user.id)
        db.delete_user(new_user.id)

        # read users after delete and verify count remains the same
        users = list(db.list_users())
        self.assertEqual(len(users), before_create_count)

    def test_permission_crud(self):
        # Should do Permission CRUD operations successfully
        # create database
        db = self.databaseForTest
        # create user
        user = db.create_user(body={'id': 'new user' + str(uuid.uuid4())})
        # list permissions
        permissions = list(user.list_permissions())
        before_create_count = len(permissions)
        permission = {
            'id': 'new permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': 'dbs/AQAAAA==/colls/AQAAAJ0fgTc='  # A random one.
        }
        # create permission
        permission = user.create_permission(permission)
        self.assertEqual(permission.id,
                         'new permission',
                         'permission id error')
        # list permissions after creation
        permissions = list(user.list_permissions())
        self.assertEqual(len(permissions), before_create_count + 1)
        # query permissions
        results = list(user.query_permissions(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': permission.id}
            ]
        ))
        self.assertTrue(results)

        # replace permission
        change_permission = permission.properties.copy()
        permission.properties['id'] = 'replaced permission'
        permission.id = permission.properties['id']
        replaced_permission = user.replace_permission(change_permission['id'], permission.properties)
        self.assertEqual(replaced_permission.id,
                         'replaced permission',
                         'permission id should change')
        self.assertEqual(permission.id,
                         replaced_permission.id,
                         'permission id should stay the same')
        # read permission
        permission = user.get_permission(replaced_permission.id)
        self.assertEqual(replaced_permission.id, permission.id)
        # delete permission
        user.delete_permission(replaced_permission.id)
        # read permission after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           user.get_permission,
                                           permission.id)

    def test_permission_upsert(self):
        # create database
        db = self.databaseForTest

        # create user
        user = db.create_user(body={'id': 'new user' + str(uuid.uuid4())})

        # read permissions and check count
        permissions = list(user.list_permissions())
        before_create_count = len(permissions)

        permission_definition = {
            'id': 'permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': 'dbs/AQAAAA==/colls/AQAAAJ0fgTc='  # A random one.
        }

        # create permission using Upsert API
        created_permission = user.upsert_permission(permission_definition)

        # verify id property
        self.assertEqual(created_permission.id,
                         permission_definition['id'],
                         'permission id error')

        # read permissions after creation and verify updated count
        permissions = list(user.list_permissions())
        self.assertEqual(len(permissions), before_create_count + 1)

        # update permission mode
        permission_definition['permissionMode'] = documents.PermissionMode.All

        # should repace the permission since it already exists
        upserted_permission = user.upsert_permission(permission_definition)
        # verify id property
        self.assertEqual(upserted_permission.id,
                         created_permission.id,
                         'permission id should remain same')

        # verify changed property
        self.assertEqual(upserted_permission.permission_mode,
                         permission_definition['permissionMode'],
                         'permissionMode should change')

        # read permissions and verify count doesn't increases again
        permissions = list(user.list_permissions())
        self.assertEqual(len(permissions), before_create_count + 1)

        # update permission id
        created_permission.properties['id'] = 'new permission'
        created_permission.id = created_permission.properties['id']
        # resource needs to be changed along with the id in order to create a new permission
        created_permission.properties['resource'] = 'dbs/N9EdAA==/colls/N9EdAIugXgA='
        created_permission.resource_link = created_permission.properties['resource']

        # should create new permission since id has changed
        new_permission = user.upsert_permission(created_permission.properties)

        # verify id and resource property
        self.assertEqual(new_permission.id,
                         created_permission.id,
                         'permission id should be same')

        self.assertEqual(new_permission.resource_link,
                         created_permission.resource_link,
                         'permission resource should be same')

        # read permissions and verify count increases
        permissions = list(user.list_permissions())
        self.assertEqual(len(permissions), before_create_count + 2)

        # delete permissions
        user.delete_permission(upserted_permission.id)
        user.delete_permission(new_permission.id)

        # read permissions and verify count remains the same
        permissions = list(user.list_permissions())
        self.assertEqual(len(permissions), before_create_count)

    def test_authorization(self):
        def __SetupEntities(client):
            """
            Sets up entities for this test.

            :Parameters:
                - `client`: cosmos_client_connection.CosmosClientConnection

            :Returns:
                dict

            """
            # create database
            db = self.databaseForTest
            # create collection
            collection = db.create_container(
                id='test_authorization' + str(uuid.uuid4()),
                partition_key=PartitionKey(path='/id', kind='Hash')
            )
            # create document1
            document = collection.create_item(
                body={'id': 'doc1',
                      'spam': 'eggs',
                      'key': 'value'},
            )

            # create user
            user = db.create_user(body={'id': 'user' + str(uuid.uuid4())})

            # create permission for collection
            permission = {
                'id': 'permission On Coll',
                'permissionMode': documents.PermissionMode.Read,
                'resource': "dbs/" + db.id + "/colls/" + collection.id
            }
            permission_on_coll = user.create_permission(body=permission)
            self.assertIsNotNone(permission_on_coll.properties['_token'],
                                 'permission token is invalid')

            # create permission for document
            permission = {
                'id': 'permission On Doc',
                'permissionMode': documents.PermissionMode.All,
                'resource': "dbs/" + db.id + "/colls/" + collection.id + "/docs/" + document["id"]
            }
            permission_on_doc = user.create_permission(body=permission)
            self.assertIsNotNone(permission_on_doc.properties['_token'],
                                 'permission token is invalid')

            entities = {
                'db': db,
                'coll': collection,
                'doc': document,
                'user': user,
                'permissionOnColl': permission_on_coll,
                'permissionOnDoc': permission_on_doc,
            }
            return entities

        # Client without any authorization will fail.
        try:
            cosmos_client.CosmosClient(TestCRUDOperations.host, {}, "Session",
                                       connection_policy=TestCRUDOperations.connectionPolicy)
            raise Exception("Test did not fail as expected.")
        except exceptions.CosmosHttpResponseError as error:
            self.assertEqual(error.status_code, StatusCodes.UNAUTHORIZED)

        # Client with master key.
        client = cosmos_client.CosmosClient(TestCRUDOperations.host,
                                            TestCRUDOperations.masterKey,
                                            "Session",
                                            connection_policy=TestCRUDOperations.connectionPolicy)
        # setup entities
        entities = __SetupEntities(client)
        resource_tokens = {"dbs/" + entities['db'].id + "/colls/" + entities['coll'].id:
                               entities['permissionOnColl'].properties['_token']}
        col_client = cosmos_client.CosmosClient(
            TestCRUDOperations.host, resource_tokens, "Session", connection_policy=TestCRUDOperations.connectionPolicy)
        db = entities['db']

        old_client_connection = db.client_connection
        db.client_connection = col_client.client_connection
        # 1. Success-- Use Col Permission to Read
        success_coll = db.get_container_client(container=entities['coll'])
        # 2. Failure-- Use Col Permission to delete
        self.__AssertHTTPFailureWithStatus(StatusCodes.FORBIDDEN,
                                           db.delete_container,
                                           success_coll)
        # 3. Success-- Use Col Permission to Read All Docs
        success_documents = list(success_coll.read_all_items())
        self.assertTrue(success_documents != None,
                        'error reading documents')
        self.assertEqual(len(success_documents),
                         1,
                         'Expected 1 Document to be successfully read')
        # 4. Success-- Use Col Permission to Read Doc

        docId = entities['doc']['id']
        success_doc = success_coll.read_item(
            item=docId,
            partition_key=docId
        )
        self.assertTrue(success_doc != None, 'error reading document')
        self.assertEqual(
            success_doc['id'],
            entities['doc']['id'],
            'Expected to read children using parent permissions')

        # 5. Failure-- Use Col Permission to Delete Doc
        self.__AssertHTTPFailureWithStatus(StatusCodes.FORBIDDEN,
                                           success_coll.delete_item,
                                           docId, docId)

        resource_tokens = {"dbs/" + entities['db'].id + "/colls/" + entities['coll'].id + "/docs/" + docId:
                               entities['permissionOnDoc'].properties['_token']}

        doc_client = cosmos_client.CosmosClient(
            TestCRUDOperations.host, resource_tokens, "Session", connection_policy=TestCRUDOperations.connectionPolicy)

        # 6. Success-- Use Doc permission to read doc
        read_doc = doc_client.get_database_client(db.id).get_container_client(success_coll.id).read_item(docId, docId)
        self.assertEqual(read_doc["id"], docId)

        # 6. Success-- Use Doc permission to delete doc
        doc_client.get_database_client(db.id).get_container_client(success_coll.id).delete_item(docId, docId)
        self.assertEqual(read_doc["id"], docId)

        db.client_connection = old_client_connection
        db.delete_container(entities['coll'])

    def test_client_request_timeout(self):
        # Test is flaky on Emulator
        if not ('localhost' in self.host or '127.0.0.1' in self.host):
            connection_policy = documents.ConnectionPolicy()
            # making timeout 0 ms to make sure it will throw
            connection_policy.RequestTimeout = 0.000000000001

            # client does a getDatabaseAccount on initialization, which will not time out because
            # there is a forced timeout for those calls
            client = cosmos_client.CosmosClient(TestCRUDOperations.host, TestCRUDOperations.masterKey, "Session",
                                                connection_policy=connection_policy)
            with self.assertRaises(Exception):
                databaseForTest = client.get_database_client(self.configs.TEST_DATABASE_ID)
                container = databaseForTest.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)
                container.create_item(body={'id': str(uuid.uuid4()), 'name': 'sample'})

    def test_read_timeout_async(self):
        connection_policy = documents.ConnectionPolicy()
        # making timeout 0 ms to make sure it will throw
        connection_policy.DBAReadTimeout = 0.000000000001
        with self.assertRaises(ServiceResponseError):
            # this will make a get database account call
            with cosmos_client.CosmosClient(self.host, self.masterKey, connection_policy=connection_policy):
                print('initialization')

    def test_client_request_timeout_when_connection_retry_configuration_specified(self):
        connection_policy = documents.ConnectionPolicy()
        # making timeout 0 ms to make sure it will throw
        connection_policy.RequestTimeout = 0.000000000001
        connection_policy.ConnectionRetryConfiguration = Retry(
            total=3,
            read=3,
            connect=3,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 504)
        )
        # client does a getDatabaseAccount on initialization, which will not time out because
        # there is a forced timeout for those calls
        with cosmos_client.CosmosClient(self.host, self.masterKey, connection_policy=connection_policy) as client:
            with self.assertRaises(AzureError):
                databaseForTest = client.get_database_client(self.configs.TEST_DATABASE_ID)
                container = databaseForTest.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)
                container.create_item(body={'id': str(uuid.uuid4()), 'name': 'sample'})

    # TODO: Skipping this test to debug later
    @unittest.skip
    def test_client_connection_retry_configuration(self):
        total_time_for_two_retries = self.initialize_client_with_connection_core_retry_config(2)
        total_time_for_three_retries = self.initialize_client_with_connection_core_retry_config(3)
        self.assertGreater(total_time_for_three_retries, total_time_for_two_retries)

    def initialize_client_with_connection_core_retry_config(self, retries):
        start_time = time.time()
        try:
            cosmos_client.CosmosClient(
                "https://localhost:9999",
                TestCRUDOperations.masterKey,
                "Session",
                retry_total=retries,
                retry_read=retries,
                retry_connect=retries,
                retry_status=retries)
            self.fail()
        except AzureError as e:
            end_time = time.time()
            return end_time - start_time

    def test_timeout_on_connection_error(self):
        # Connection Refused: This is an active rejection from the target machine's operating system. It receives your
        # connection request but immediately sends back a response indicating that no process is listening on that port.
        # This is a fast failure.
        # Connection Timeout Setting: This occurs when your connection request receives no response at all within a
        # specified period. The client gives up waiting. This typically happens if the target machine is down,
        # unreachable due to network configuration, or a firewall is silently dropping the packets.
        # so in the below test connection_timeout setting has no bearing on the test outcome
        # catching both exceptions to make the test the test reliable in different environment as
        # the underlying operating system and network stack handle the connection attempt to a non-existent port in different ways

        with self.assertRaises((exceptions.CosmosClientTimeoutError, ServiceRequestError)):
            cosmos_client.CosmosClient(
                "https://localhost:9999",
                TestCRUDOperations.masterKey,
                retry_total=50,
                connection_timeout=100,
                timeout=10)

    def test_timeout_on_read_operation(self):
        error_response = ServiceResponseError("Read timeout")
        # Initialize transport with passthrough enabled for client setup
        timeout_transport = TimeoutTransport(error_response, passthrough=True)

        client = cosmos_client.CosmosClient(
            self.host, self.masterKey, "Session", transport=timeout_transport)
        timeout_transport.passthrough = False
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            client.create_database_if_not_exists("test", timeout=2)

    def test_timeout_on_throttling_error(self):
        # Throttling(429): Keeps retrying -> Eventually times out -> CosmosClientTimeoutError
        status_response = 429  # Uses Cosmos custom retry
        timeout_transport = TimeoutTransport(status_response, passthrough=True)
        client = cosmos_client.CosmosClient(
            self.host, self.masterKey, "Session", transport=timeout_transport)

        timeout_transport.passthrough = False
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            client.create_database_if_not_exists("test", timeout=30)

        databases = client.list_databases(timeout=29)
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            list(databases)

    def test_inner_exceptions_on_timeout(self):
        # Throttling(429): Keeps retrying -> Eventually times out -> CosmosClientTimeoutError
        status_response = 429  # Uses Cosmos custom retry
        timeout_transport = TimeoutTransport(status_response, passthrough=True)
        client = cosmos_client.CosmosClient(
            self.host, self.masterKey, "Session", transport=timeout_transport)

        timeout_transport.passthrough = False
        with self.assertRaises(exceptions.CosmosClientTimeoutError) as cm:
            client.create_database_if_not_exists("test", timeout=30)

        # Verify the inner_exception is set and is a 429 error
        self.assertIsNotNone(cm.exception.inner_exception)
        self.assertIsInstance(cm.exception.inner_exception, exceptions.CosmosHttpResponseError)
        self.assertEqual(cm.exception.inner_exception.status_code, 429)

    def test_timeout_for_read_items(self):
        """Test that timeout is properly maintained across multiple partition requests for a single logical operation
        read_items is different as the results of this api are not paginated and we present the complete result set
        """

        # Create a container with multiple partitions
        created_container = self.databaseForTest.create_container(
            id='multi_partition_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=11000
        )
        pk_ranges = list(created_container.client_connection._ReadPartitionKeyRanges(
            created_container.container_link))
        self.assertGreater(len(pk_ranges), 1, "Container should have multiple physical partitions.")

        # 2. Create items across different logical partitions
        items_to_read = []
        all_item_ids = set()
        for i in range(200):
            doc_id = f"item_{i}_{uuid.uuid4()}"
            pk = i % 10
            all_item_ids.add(doc_id)
            created_container.create_item({'id': doc_id, 'pk': pk, 'data': i})
            items_to_read.append((doc_id, pk))

        # Create a custom transport that introduces delays
        class DelayedTransport(RequestsTransport):
            def __init__(self, delay_per_request=2):
                self.delay_per_request = delay_per_request
                self.request_count = 0
                super().__init__()

            def send(self, request, **kwargs):
                self.request_count += 1
                # Delay each request to simulate slow network
                time.sleep(self.delay_per_request)
                return super().send(request, **kwargs)

        # Verify timeout fails when cumulative time exceeds limit
        delayed_transport = DelayedTransport(delay_per_request=2)
        client_with_delay = cosmos_client.CosmosClient(
            self.host,
            self.masterKey,
            transport=delayed_transport
        )
        container_with_delay = client_with_delay.get_database_client(
            self.databaseForTest.id
        ).get_container_client(created_container.id)

        start_time = time.time()
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            # This should timeout because multiple partition requests * 2s delay > 5s timeout
            list(container_with_delay.read_items(
                items = items_to_read,
                timeout = 5  # 5 second total timeout
            ))

        elapsed_time = time.time() - start_time

        # Should fail close to 5 seconds (not wait for all requests)
        self.assertLess(elapsed_time, 7)  # Allow some overhead
        self.assertGreater(elapsed_time, 5)  # Should wait at least close to timeout

        # Verify operation succeeds when no timeout is passed(default is close to 7 days)
        start_time = time.time()
        # add few more items
        for i in range(500):
            doc_id = f"item_{i}_{uuid.uuid4()}"
            pk = i % 10
            all_item_ids.add(doc_id)
            created_container.create_item({'id': doc_id, 'pk': pk, 'data': i})
            items_to_read.append((doc_id, pk))

        items = list(container_with_delay.read_items(
            items=items_to_read,
        ))

        elapsed_time = time.time() - start_time


    def test_timeout_for_paged_request(self):
        """Test that timeout applies to each individual page request, not cumulatively"""

        # Create container and add items
        created_container = self.databaseForTest.create_container(
            id='paged_timeout_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk")
        )

        # Create enough items to ensure multiple pages
        for i in range(100):
            created_container.create_item({'id': f'item_{i}', 'pk': i % 10, 'data': 'x' * 1000})

        # Create a transport that delays each request
        class DelayedTransport(RequestsTransport):
            def __init__(self, delay_seconds=3):
                self.delay_seconds = delay_seconds
                super().__init__()

            def send(self, request, **kwargs):
                time.sleep(self.delay_seconds)
                return super().send(request, **kwargs)

        # Test with delayed transport
        delayed_transport = DelayedTransport(delay_seconds=3)
        client_with_delay = cosmos_client.CosmosClient(
            self.host, self.masterKey, transport=delayed_transport
        )
        container_with_delay = client_with_delay.get_database_client(
            self.databaseForTest.id
        ).get_container_client(created_container.id)

        # Test 1: Timeout should apply per page
        item_pages = container_with_delay.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True,
            max_item_count=10,  # Small page size
            timeout=5  # Pass timeout here
        ).by_page()

        # First page should succeed with 5s timeout (3s delay < 5s timeout)
        first_page = list(next(item_pages))
        self.assertGreater(len(first_page), 0)

        # Second page should also succeed (timeout resets per page)
        second_page = list(next(item_pages))
        self.assertGreater(len(second_page), 0)

        # Test 2: Timeout too short should fail
        item_pages_short_timeout = container_with_delay.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True,
            max_item_count=10,
            timeout=2  # 2s timeout < 3s delay, should fail
        ).by_page()

        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            list(next(item_pages_short_timeout))

        # Cleanup
        self.databaseForTest.delete_container(created_container.id)

    def test_timeout_for_point_operation(self):
        """Test that point operations respect client timeout"""

        # Create a container for testing
        created_container = self.databaseForTest.create_container(
            id='point_op_timeout_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk")
        )

        # Create a test item
        test_item = {
            'id': 'test_item_1',
            'pk': 'partition1',
            'data': 'test_data'
        }
        created_container.create_item(test_item)

        # Test 1: Short timeout should fail
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            created_container.read_item(
                item='test_item_1',
                partition_key='partition1',
                timeout=0.00000002  # very small timeout to force failure
            )

        # Test 2: Long timeout should succeed
        result = created_container.read_item(
            item='test_item_1',
            partition_key='partition1',
            timeout=3.0
        )
        self.assertEqual(result['id'], 'test_item_1')

    def test_point_operation_read_timeout(self):
        """Test that point operations respect client provided read timeout"""

        # Create a container for testing
        container = self.databaseForTest.create_container(
            id='point_op_timeout_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk")
        )

        # Create a test item
        test_item = {
            'id': 'test_item_1',
            'pk': 'partition1',
            'data': 'test_data'
        }
        container.create_item(test_item)
        try:
            container.read_item(
                item='test_item_1',
                partition_key='partition1',
                read_timeout=0.000003
            )
        except Exception as e:
            print(f"Exception is {e}")

    # TODO: for read timeouts azure-core returns a ServiceResponseError, needs to be fixed in azure-core and then this test can be enabled
    @unittest.skip
    def test_query_operation_single_partition_read_timeout(self):
        """Test that timeout is properly maintained across multiple network requests for a single logical operation
        """
        # Create a container with multiple partitions
        container = self.databaseForTest.create_container(
            id='single_partition_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
        )
        single_partition_key = 0

        large_string = 'a' * 1000  # 1KB string
        for i in range(500):  # Insert 500 documents
            container.create_item({
                'id': f'item_{i}',
                'pk': single_partition_key,
                'data': large_string,
                'order_field': i
            })

        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            items = list(container.query_items(
                query="SELECT * FROM c ORDER BY c.order_field ASC",
                max_item_count=100,
                read_timeout=0.00005,
                partition_key=single_partition_key
            ))
            self.assertEqual(len(items), 500)

    # TODO: for read timeouts azure-core returns a ServiceResponseError, needs to be fixed in azure-core and then this test can be enabled
    @unittest.skip
    def test_query_operation_cross_partition_read_timeout(self):
        """Test that timeout is properly maintained across multiple partition requests for a single logical operation
        """
        # Create a container with multiple partitions
        container = self.databaseForTest.create_container(
            id='multi_partition_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=11000
        )

        # 2. Create large documents to increase payload size
        large_string = 'a' * 1000  # 1KB string
        for i in range(500):  # Insert 500 documents
            container.create_item({
                'id': f'item_{i}',
                'pk': i % 2,
                'data': large_string,
                'order_field': i
            })

        pk_ranges = list(container.client_connection._ReadPartitionKeyRanges(
            container.container_link))

        self.assertGreater(len(pk_ranges), 1, "Container should have multiple physical partitions.")
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            # This should timeout because of multiple partition requests
            list(container.query_items(
                query="SELECT * FROM c ORDER BY c.order_field ASC",
                enable_cross_partition_query=True,
                max_item_count=100,
                read_timeout=0.00005,
            ))
        # This shouldn't result in any error because the default 65seconds is respected

        items = list(container.query_items(
             query="SELECT * FROM c ORDER BY c.order_field ASC",
             enable_cross_partition_query=True,
             max_item_count=100,
        ))
        self.assertEqual(len(items), 500)


    def test_query_iterable_functionality(self):
        collection = self.databaseForTest.create_container("query-iterable-container",
                                                           partition_key=PartitionKey("/pk"))

        doc1 = collection.create_item(body={'id': 'doc1', 'prop1': 'value1', 'pk': 'pk'})
        doc2 = collection.create_item(body={'id': 'doc2', 'prop1': 'value2', 'pk': 'pk'})
        doc3 = collection.create_item(body={'id': 'doc3', 'prop1': 'value3', 'pk': 'pk'})
        resources = {
            'coll': collection,
            'doc1': doc1,
            'doc2': doc2,
            'doc3': doc3
        }

        results = resources['coll'].read_all_items(max_item_count=2)
        docs = list(iter(results))
        self.assertEqual(3,
                         len(docs),
                         'QueryIterable should return all documents' +
                         ' using continuation')
        self.assertEqual(resources['doc1']['id'], docs[0]['id'])
        self.assertEqual(resources['doc2']['id'], docs[1]['id'])
        self.assertEqual(resources['doc3']['id'], docs[2]['id'])

        # Validate QueryIterable iterator with 'for'.
        results = resources['coll'].read_all_items(max_item_count=2)
        counter = 0
        # test QueryIterable with 'for'.
        for doc in iter(results):
            counter += 1
            if counter == 1:
                self.assertEqual(resources['doc1']['id'],
                                 doc['id'],
                                 'first document should be doc1')
            elif counter == 2:
                self.assertEqual(resources['doc2']['id'],
                                 doc['id'],
                                 'second document should be doc2')
            elif counter == 3:
                self.assertEqual(resources['doc3']['id'],
                                 doc['id'],
                                 'third document should be doc3')
        self.assertEqual(counter, 3)

        # Get query results page by page.
        results = resources['coll'].read_all_items(max_item_count=2)

        page_iter = results.by_page()
        first_block = list(next(page_iter))
        self.assertEqual(2, len(first_block), 'First block should have 2 entries.')
        self.assertEqual(resources['doc1']['id'], first_block[0]['id'])
        self.assertEqual(resources['doc2']['id'], first_block[1]['id'])
        self.assertEqual(1, len(list(next(page_iter))), 'Second block should have 1 entry.')
        with self.assertRaises(StopIteration):
            next(page_iter)

        self.databaseForTest.delete_container(collection.id)

    def test_get_resource_with_dictionary_and_object(self):
        created_db = self.databaseForTest

        # read database with id
        read_db = self.client.get_database_client(created_db.id)
        self.assertEqual(read_db.id, created_db.id)

        # read database with instance
        read_db = self.client.get_database_client(created_db)
        self.assertEqual(read_db.id, created_db.id)

        # read database with properties
        read_db = self.client.get_database_client(created_db.read())
        self.assertEqual(read_db.id, created_db.id)

        created_container = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # read container with id
        read_container = created_db.get_container_client(created_container.id)
        self.assertEqual(read_container.id, created_container.id)

        # read container with instance
        read_container = created_db.get_container_client(created_container)
        self.assertEqual(read_container.id, created_container.id)

        # read container with properties
        created_properties = created_container.read()
        read_container = created_db.get_container_client(created_properties)
        self.assertEqual(read_container.id, created_container.id)

        created_item = created_container.create_item({'id': '1' + str(uuid.uuid4()), 'pk': 'pk'})

        # read item with id
        read_item = created_container.read_item(item=created_item['id'], partition_key=created_item['pk'])
        self.assertEqual(read_item['id'], created_item['id'])

        # read item with properties
        read_item = created_container.read_item(item=created_item, partition_key=created_item['pk'])
        self.assertEqual(read_item['id'], created_item['id'])

        created_sproc = created_container.scripts.create_stored_procedure({
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': 'function () { }'
        })

        # read sproc with id
        read_sproc = created_container.scripts.get_stored_procedure(created_sproc['id'])
        self.assertEqual(read_sproc['id'], created_sproc['id'])

        # read sproc with properties
        read_sproc = created_container.scripts.get_stored_procedure(created_sproc)
        self.assertEqual(read_sproc['id'], created_sproc['id'])

        created_trigger = created_container.scripts.create_trigger({
            'id': 'sample trigger' + str(uuid.uuid4()),
            'serverScript': 'function() {var x = 10;}',
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        })

        # read trigger with id
        read_trigger = created_container.scripts.get_trigger(created_trigger['id'])
        self.assertEqual(read_trigger['id'], created_trigger['id'])

        # read trigger with properties
        read_trigger = created_container.scripts.get_trigger(created_trigger)
        self.assertEqual(read_trigger['id'], created_trigger['id'])

        created_udf = created_container.scripts.create_user_defined_function({
            'id': 'sample udf' + str(uuid.uuid4()),
            'body': 'function() {var x = 10;}'
        })

        # read udf with id
        read_udf = created_container.scripts.get_user_defined_function(created_udf['id'])
        self.assertEqual(created_udf['id'], read_udf['id'])

        # read udf with properties
        read_udf = created_container.scripts.get_user_defined_function(created_udf)
        self.assertEqual(created_udf['id'], read_udf['id'])

        created_user = created_db.create_user({
            'id': 'user' + str(uuid.uuid4())
        })

        # read user with id
        read_user = created_db.get_user_client(created_user.id)
        self.assertEqual(read_user.id, created_user.id)

        # read user with instance
        read_user = created_db.get_user_client(created_user)
        self.assertEqual(read_user.id, created_user.id)

        # read user with properties
        created_user_properties = created_user.read()
        read_user = created_db.get_user_client(created_user_properties)
        self.assertEqual(read_user.id, created_user.id)

        created_permission = created_user.create_permission({
            'id': 'all permission' + str(uuid.uuid4()),
            'permissionMode': documents.PermissionMode.All,
            'resource': created_container.container_link,
            'resourcePartitionKey': [1]
        })

        # read permission with id
        read_permission = created_user.get_permission(created_permission.id)
        self.assertEqual(read_permission.id, created_permission.id)

        # read permission with instance
        read_permission = created_user.get_permission(created_permission)
        self.assertEqual(read_permission.id, created_permission.id)

        # read permission with properties
        read_permission = created_user.get_permission(created_permission.properties)
        self.assertEqual(read_permission.id, created_permission.id)

    def test_delete_all_items_by_partition_key(self):
        # enable the test only for the emulator
        if "localhost" not in self.host and "127.0.0.1" not in self.host:
            return
        # create database
        created_db = self.databaseForTest

        # create container
        created_collection = created_db.create_container(
            id='test_delete_all_items_by_partition_key ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/pk', kind='Hash')
        )
        # Create two partition keys
        partition_key1 = "{}-{}".format("Partition Key 1", str(uuid.uuid4()))
        partition_key2 = "{}-{}".format("Partition Key 2", str(uuid.uuid4()))

        # add items for partition key 1
        for i in range(1, 3):
            created_collection.upsert_item(
                dict(id="item{}".format(i), pk=partition_key1)
            )

        # add items for partition key 2

        pk2_item = created_collection.upsert_item(dict(id="item{}".format(3), pk=partition_key2))

        # delete all items for partition key 1
        created_collection.delete_all_items_by_partition_key(partition_key1)

        # check that only items from partition key 1 have been deleted
        items = list(created_collection.read_all_items())

        # items should only have 1 item, and it should equal pk2_item
        self.assertDictEqual(pk2_item, items[0])

        # attempting to delete a non-existent partition key or passing none should not delete
        # anything and leave things unchanged
        created_collection.delete_all_items_by_partition_key(None)

        # check that no changes were made by checking if the only item is still there
        items = list(created_collection.read_all_items())

        # items should only have 1 item, and it should equal pk2_item
        self.assertDictEqual(pk2_item, items[0])

        created_db.delete_container(created_collection)

    def test_patch_operations(self):
        created_container = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        pkValue = "patch_item_pk" + str(uuid.uuid4())
        # Create item to patch
        item = {
            "id": "patch_item",
            "pk": pkValue,
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        created_container.create_item(item)
        # Define and run patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]
        patched_item = created_container.patch_item(item="patch_item", partition_key=pkValue,
                                                    patch_operations=operations)
        # Verify results from patch operations
        self.assertTrue(patched_item.get("color") is None)
        self.assertTrue(patched_item.get("prop") is None)
        self.assertEqual(patched_item.get("company"), "CosmosDB")
        self.assertEqual(patched_item.get("address").get("new_city"), "Atlanta")
        self.assertEqual(patched_item.get("number"), 10)
        self.assertEqual(patched_item.get("favorite_color"), "yellow")

        # Negative test - attempt to replace non-existent field
        operations = [{"op": "replace", "path": "/wrong_field", "value": "wrong_value"}]
        try:
            created_container.patch_item(item="patch_item", partition_key=pkValue, patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, StatusCodes.BAD_REQUEST)

        # Negative test - attempt to remove non-existent field
        operations = [{"op": "remove", "path": "/wrong_field"}]
        try:
            created_container.patch_item(item="patch_item", partition_key=pkValue, patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, StatusCodes.BAD_REQUEST)

        # Negative test - attempt to increment non-number field
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        try:
            created_container.patch_item(item="patch_item", partition_key=pkValue, patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, StatusCodes.BAD_REQUEST)

        # Negative test - attempt to move from non-existent field
        operations = [{"op": "move", "from": "/wrong_field", "path": "/other_field"}]
        try:
            created_container.patch_item(item="patch_item", partition_key=pkValue, patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, StatusCodes.BAD_REQUEST)

    def test_conditional_patching(self):
        created_container = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # Create item to patch
        pkValue = "patch_item_pk" + str(uuid.uuid4())
        item = {
            "id": "conditional_patch_item",
            "pk": pkValue,
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        created_container.create_item(item)

        # Define patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]

        # Run patch operations with wrong filter
        num_false = item.get("number") + 1
        filter_predicate = "from root where root.number = " + str(num_false)
        try:
            created_container.patch_item(item="conditional_patch_item", partition_key=pkValue,
                                         patch_operations=operations, filter_predicate=filter_predicate)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, StatusCodes.PRECONDITION_FAILED)

        # Run patch operations with correct filter
        filter_predicate = "from root where root.number = " + str(item.get("number"))
        patched_item = created_container.patch_item(item="conditional_patch_item", partition_key=pkValue,
                                                    patch_operations=operations, filter_predicate=filter_predicate)
        # Verify results from patch operations
        self.assertTrue(patched_item.get("color") is None)
        self.assertTrue(patched_item.get("prop") is None)
        self.assertEqual(patched_item.get("company"), "CosmosDB")
        self.assertEqual(patched_item.get("address").get("new_city"), "Atlanta")
        self.assertEqual(patched_item.get("number"), 10)
        self.assertEqual(patched_item.get("favorite_color"), "yellow")

    # Temporarily commenting analytical storage tests until emulator support comes.
    # def test_create_container_with_analytical_store_off(self):
    #     # don't run test, for the time being, if running against the emulator
    #     if 'localhost' in self.host or '127.0.0.1' in self.host:
    #         return

    #     created_db = self.databaseForTest
    #     collection_id = 'test_create_container_with_analytical_store_off_' + str(uuid.uuid4())
    #     collection_indexing_policy = {'indexingMode': 'consistent'}
    #     created_recorder = RecordDiagnostics()
    #     created_collection = created_db.create_container(id=collection_id,
    #                                                      indexing_policy=collection_indexing_policy,
    #                                                      partition_key=PartitionKey(path="/pk", kind="Hash"),
    #                                                      response_hook=created_recorder)
    #     properties = created_collection.read()
    #     ttl_key = "analyticalStorageTtl"
    #     self.assertTrue(ttl_key not in properties or properties[ttl_key] == None)

    # def test_create_container_with_analytical_store_on(self):
    #     # don't run test, for the time being, if running against the emulator
    #     if 'localhost' in self.host or '127.0.0.1' in self.host:
    #         return

    #     created_db = self.databaseForTest
    #     collection_id = 'test_create_container_with_analytical_store_on_' + str(uuid.uuid4())
    #     collection_indexing_policy = {'indexingMode': 'consistent'}
    #     created_recorder = RecordDiagnostics()
    #     created_collection = created_db.create_container(id=collection_id,
    #                                                      analytical_storage_ttl=-1,
    #                                                      indexing_policy=collection_indexing_policy,
    #                                                      partition_key=PartitionKey(path="/pk", kind="Hash"),
    #                                                      response_hook=created_recorder)
    #     properties = created_collection.read()
    #     ttl_key = "analyticalStorageTtl"
    #     self.assertTrue(ttl_key in properties and properties[ttl_key] == -1)

    # def test_create_container_if_not_exists_with_analytical_store_on(self):
    #     # don't run test, for the time being, if running against the emulator
    #     if 'localhost' in self.host or '127.0.0.1' in self.host:
    #         return

    #     # first, try when we know the container doesn't exist.
    #     created_db = self.databaseForTest
    #     collection_id = 'test_create_container_if_not_exists_with_analytical_store_on_' + str(uuid.uuid4())
    #     collection_indexing_policy = {'indexingMode': 'consistent'}
    #     created_recorder = RecordDiagnostics()
    #     created_collection = created_db.create_container_if_not_exists(id=collection_id,
    #                                                                    analytical_storage_ttl=-1,
    #                                                                    indexing_policy=collection_indexing_policy,
    #                                                                    partition_key=PartitionKey(path="/pk", kind="Hash"),
    #                                                                    response_hook=created_recorder)
    #     properties = created_collection.read()
    #     ttl_key = "analyticalStorageTtl"
    #     self.assertTrue(ttl_key in properties and properties[ttl_key] == -1)

    #     # next, try when we know the container DOES exist. This way both code paths are tested.
    #     created_collection = created_db.create_container_if_not_exists(id=collection_id,
    #                                                                    analytical_storage_ttl=-1,
    #                                                                    indexing_policy=collection_indexing_policy,
    #                                                                    partition_key=PartitionKey(path="/pk", kind="Hash"),
    #                                                                    response_hook=created_recorder)
    #     properties = created_collection.read()
    #     ttl_key = "analyticalStorageTtl"
    #     self.assertTrue(ttl_key in properties and properties[ttl_key] == -1)

    def test_priority_level(self):
        # These test verify if headers for priority level are sent
        # Feature must be enabled at the account level
        # If feature is not enabled the test will still pass as we just verify the headers were sent
        created_container = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        item1 = {"id": "item1", "pk": "pk1"}
        item2 = {"id": "item2", "pk": "pk2"}
        self.OriginalExecuteFunction = _retry_utility.ExecuteFunction
        priority_headers = []

        # mock execute function to check if priority level set in headers

        def priority_mock_execute_function(function, *args, **kwargs):
            if args:
                priority_headers.append(args[4].headers[HttpHeaders.PriorityLevel]
                                              if HttpHeaders.PriorityLevel in args[4].headers else '')
            return self.OriginalExecuteFunction(function, *args, **kwargs)

        _retry_utility.ExecuteFunction = priority_mock_execute_function
        # upsert item with high priority
        created_container.upsert_item(body=item1, priority="High")
        # check if the priority level was passed
        self.assertEqual(priority_headers[-1], "High")
        # upsert item with low priority
        created_container.upsert_item(body=item2, priority="Low")
        # check that headers passed low priority
        self.assertEqual(priority_headers[-1], "Low")
        # Repeat for read operations
        item1_read = created_container.read_item("item1", "pk1", priority="High")
        self.assertEqual(priority_headers[-1], "High")
        item2_read = created_container.read_item("item2", "pk2", priority="Low")
        self.assertEqual(priority_headers[-1], "Low")
        # repeat for query
        query = list(created_container.query_items("Select * from c", partition_key="pk1", priority="High"))

        self.assertEqual(priority_headers[-1], "High")

        # Negative Test: Verify that if we send a value other than High or Low that it will not set the header value
        # and result in bad request
        try:
            item2_read = created_container.read_item("item2", "pk2", priority="Medium")
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, StatusCodes.BAD_REQUEST)
        _retry_utility.ExecuteFunction = self.OriginalExecuteFunction

    def _MockExecuteFunction(self, function, *args, **kwargs):
        if HttpHeaders.PartitionKey in args[4].headers:
            self.last_headers.append(args[4].headers[HttpHeaders.PartitionKey])
        return self.OriginalExecuteFunction(function, *args, **kwargs)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True:  # raised by sys.exit(True) when tests failed
            raise
