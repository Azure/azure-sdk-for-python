# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""End to end test.
"""

import json
import logging
import os.path
import sys
import unittest
from six.moves import xrange
from struct import unpack, pack
# from six.moves.builtins import *
import time
import six

if six.PY2:
    import urllib as urllib
else:
    import urllib.parse as urllib
import uuid
import pytest
import copy
import azure.cosmos.base as base
import azure.cosmos.consistent_hash_ring as consistent_hash_ring
import azure.cosmos.documents as documents
import azure.cosmos.errors as errors
import azure.cosmos.hash_partition_resolver as hash_partition_resolver
from azure.cosmos.http_constants import HttpHeaders, StatusCodes, SubStatusCodes
import azure.cosmos.murmur_hash as murmur_hash
import azure.cosmos.range_partition_resolver as range_partition_resolver
import azure.cosmos.range as partition_range
import test.new_object_model_tests.test_config as test_config
import test.test_partition_resolver as test_partition_resolver
import azure.cosmos.base as base
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.database import Database
from azure.cosmos.container import Container
from azure.cosmos.item import Item
from azure.cosmos import PartitionKey
import test.conftest as conftest

# IMPORTANT NOTES:

#  	Most test cases in this file create collections in your Azure Cosmos account.
#  	Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.

#  	To Run the test, replace the two member fields (masterKey and host) with values
#   associated with your Azure Cosmos account.

@pytest.mark.usefixtures("teardown_new_object_model")
class CRUDTests(unittest.TestCase):
    """Python CRUD Tests.
    """

    configs = test_config._test_config
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    client = cosmos_client.CosmosClient(host, {'masterKey': masterKey}, "Session", connectionPolicy)
    databaseForTest = configs.create_database_if_not_exist(client)

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except errors.HTTPFailure as inst:
            self.assertEqual(inst.status_code, status_code)

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                    cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    def setUp(self):
        self.client = cosmos_client.CosmosClient(self.host, {'masterKey':self.masterKey}, "Session",
                                                 self.connectionPolicy)

    def test_database_crud(self):
        # read databases.
        databases = list(self.client.list_databases())
        # create a database.
        before_create_databases_count = len(databases)
        database_id = str(uuid.uuid4())
        created_db = self.client.create_database(database_id)
        self.assertEqual(created_db.id, database_id)
        # Read databases after creation.
        databases = list(self.client.list_databases())
        self.assertEqual(len(databases),
                         before_create_databases_count + 1,
                         'create should increase the number of databases')
        # query databases.
        databases = list(self.client.list_database_properties({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [
                {'name': '@id', 'value': database_id}
            ]
        }))
        self.assert_(databases,
                     'number of results for the query should be > 0')

        # read database.
        self.client.get_database(created_db.id)

        # delete database.
        self.client.delete_database(created_db.id)
        # read database after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           self.client.get_database,
                                           created_db.id)

    def test_sql_query_crud(self):
        # create two databases.
        db1 = self.client.create_database('database 1' + str(uuid.uuid4()))
        db2 = self.client.create_database('database 2' + str(uuid.uuid4()))


        conftest.database_ids_to_delete.append(db1.id)
        conftest.database_ids_to_delete.append(db2.id)

        # query with parameters.
        databases = list(self.client.list_database_properties({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [
                {'name': '@id', 'value': db1.id}
            ]
        }))
        self.assertEqual(1, len(databases), 'Unexpected number of query results.')

        # query without parameters.
        databases = list(self.client.list_database_properties({
            'query': 'SELECT * FROM root r WHERE r.id="database non-existing"'
        }))
        self.assertEqual(0, len(databases), 'Unexpected number of query results.')

        # query with a string.
        databases = list(self.client.list_database_properties('SELECT * FROM root r WHERE r.id="' + db2.id + '"'))
        self.assertEqual(1, len(databases), 'Unexpected number of query results.')

    def test_collection_crud(self):
        created_db = self.databaseForTest
        collections = list(created_db.list_containers())
        # create a collection
        before_create_collections_count = len(collections)
        collection_id = 'test_collection_crud ' + str(uuid.uuid4())
        collection_indexing_policy = {'indexingMode': 'consistent'}
        created_collection = created_db.create_container(id=collection_id,
                                                         indexing_policy=collection_indexing_policy,
                                                         partition_key=PartitionKey(path="/pk", kind="Hash"))
        self.assertEqual(collection_id, created_collection.id)
        self.assertEqual('consistent', created_collection.properties['indexingPolicy']['indexingMode'])

        # read collections after creation
        collections = list(created_db.list_containers())
        self.assertEqual(len(collections),
                         before_create_collections_count + 1,
                         'create should increase the number of collections')
        # query collections
        collections = list(created_db.list_container_properties(
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    {'name': '@id', 'value': collection_id}
                ]
            }))
        # Replacing indexing policy is allowed.
        lazy_policy = {'indexingMode': 'lazy'}
        replaced_collection = created_db.replace_container(created_collection,
                                                           partition_key=created_collection.properties['partitionKey'],
                                                           indexing_policy=lazy_policy)
        self.assertEqual('lazy', replaced_collection.properties['indexingPolicy']['indexingMode'])

        self.assertTrue(collections)
        # delete collection
        created_db.delete_container(created_collection.id)
        # read collection after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           created_db.get_container,
                                           created_collection.id)

    #TODO: add fixture to remove container at the end of test
    def test_partitioned_collection(self):
        created_db = self.databaseForTest

        collection_definition = {'id': 'test_partitioned_collection ' + str(uuid.uuid4()),
                                 'partitionKey':
                                     {
                                         'paths': ['/id'],
                                         'kind': documents.PartitionKind.Hash
                                     }
                                 }

        offer_throughput = 10100
        created_collection = created_db.create_container(id=collection_definition['id'],
                                                        partition_key=collection_definition['partitionKey'],
                                                        offer_throughput=offer_throughput)

        self.assertEqual(collection_definition.get('id'), created_collection.id)
        self.assertEqual(collection_definition.get('partitionKey').get('paths')[0],
                         created_collection.properties['partitionKey']['paths'][0])
        self.assertEqual(collection_definition.get('partitionKey').get('kind'),
                         created_collection.properties['partitionKey']['kind'])

        expected_offer = created_collection.read_offer()

        self.assertIsNotNone(expected_offer)

        self.assertEqual(expected_offer.offer_throughput, offer_throughput)

        created_db.delete_container(created_collection.id)

    def test_partitioned_collection_quota(self):
        created_db = self.databaseForTest

        created_collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)

        retrieved_collection = created_db.get_container(
            container=created_collection.id,
            populate_partition_key_range_statistics=True,
            populate_quota_info=True
        )

        self.assertIsNotNone(retrieved_collection.properties.get("statistics"))
        self.assertIsNotNone(created_db.client_connection.last_response_headers.get("x-ms-resource-usage"))

    #TODO: add fixture to remove container at the end of test
    #TODO: add check for partition key in request options using spy
    def test_partitioned_collection_partition_key_extraction(self):
        created_db = self.databaseForTest

        collection_id = 'test_partitioned_collection_partition_key_extraction ' + str(uuid.uuid4())
        created_collection = created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/address/state', kind=documents.PartitionKind.Hash)
        )

        document_definition = {'id': 'document1',
                               'address': {'street': '1 Microsoft Way',
                                           'city': 'Redmond',
                                           'state': 'WA',
                                           'zip code': 98052
                                           }
                               }

        # create document without partition key being specified
        created_document = created_collection.create_item(body=document_definition)

        self.assertEqual(created_document.get('id'), document_definition.get('id'))
        self.assertEqual(created_document.get('address').get('state'), document_definition.get('address').get('state'))

        collection_id = 'test_partitioned_collection_partition_key_extraction1 ' + str(uuid.uuid4())
        created_collection1 = created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/address', kind=documents.PartitionKind.Hash)
        )

        # Create document with partitionkey not present as a leaf level property but a dict
        created_document = created_collection1.create_item(document_definition)

        #self.assertEqual(options['partitionKey'], documents.Undefined)

        collection_id = 'test_partitioned_collection_partition_key_extraction2 ' + str(uuid.uuid4())
        created_collection2 = created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/address/state/city', kind=documents.PartitionKind.Hash)
        )

        # Create document with partitionkey not present in the document
        created_document = created_collection2.create_item(document_definition)

        #self.assertEqual(options['partitionKey'], documents.Undefined)

        created_db.delete_container(created_collection.id)
        created_db.delete_container(created_collection1.id)
        created_db.delete_container(created_collection2.id)

    #TODO: add check for partition key in request options using spy
    #TODO: add fixture to remove container at the end of test
    def test_partitioned_collection_partition_key_extraction_special_chars(self):
        created_db = self.databaseForTest

        collection_id = 'test_partitioned_collection_partition_key_extraction_special_chars1 ' + str(uuid.uuid4())

        created_collection1 = created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/\"level\' 1*()\"/\"le/vel2\"', kind=documents.PartitionKind.Hash)
        )
        document_definition = {'id': 'document1',
                               "level' 1*()": {"le/vel2": 'val1'}
                               }

        created_collection1.create_item(body=document_definition)

        #self.assertEqual(options['partitionKey'], 'val1')

        collection_definition2 = {
            'id': 'test_partitioned_collection_partition_key_extraction_special_chars2 ' + str(uuid.uuid4()),
            'partitionKey':
                {
                    'paths': ['/\'level\" 1*()\'/\'le/vel2\''],
                    'kind': documents.PartitionKind.Hash
                }
            }

        collection_id = 'test_partitioned_collection_partition_key_extraction_special_chars2 ' + str(uuid.uuid4())

        created_collection2 = created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/\'level\" 1*()\'/\'le/vel2\'', kind=documents.PartitionKind.Hash)
        )

        document_definition = {'id': 'document2',
                               'level\" 1*()': {'le/vel2': 'val2'}
                               }

        created_collection2.create_item(body=document_definition)

        #self.assertEqual(options['partitionKey'], 'val2')

        created_db.delete_container(created_collection1.id)
        created_db.delete_container(created_collection2.id)

    def test_partitioned_collection_path_parser(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(test_dir, "BaselineTest.PathParser.json")) as json_file:
            entries = json.loads(json_file.read())
        for entry in entries:
            parts = base.ParsePaths([entry['path']])
            self.assertEqual(parts, entry['parts'])

        paths = ["/\"Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1\"/*"]
        parts = ["Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1", "*"]
        self.assertEqual(parts, base.ParsePaths(paths))

        paths = ["/'Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1'/*"]
        parts = ["Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1", "*"]
        self.assertEqual(parts, base.ParsePaths(paths))

    def test_partitioned_collection_document_crud_and_query(self):
        created_db = self.databaseForTest

        created_collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)

        document_definition = {'id': 'document',
                               'key': 'value'}

        created_document = created_collection.create_item(
            body=document_definition
        )

        self.assertEqual(created_document.get('id'), document_definition.get('id'))
        self.assertEqual(created_document.get('key'), document_definition.get('key'))

        # read document
        read_document = created_collection.get_item(
            id=created_document.get('id'),
            partition_key=created_document.get('id')
        )

        self.assertEqual(read_document.get('id'), created_document.get('id'))
        self.assertEqual(read_document.get('key'), created_document.get('key'))

        # Read document feed doesn't require partitionKey as it's always a cross partition query
        documentlist = list(created_collection.list_items())
        self.assertEqual(1, len(documentlist))

        # replace document
        document_definition['key'] = 'new value'

        replaced_document = created_collection.replace_item(
            item=read_document,
            body=document_definition
        )

        self.assertEqual(replaced_document.get('key'), document_definition.get('key'))

        # upsert document(create scenario)
        document_definition['id'] = 'document2'
        document_definition['key'] = 'value2'

        upserted_document = created_collection.upsert_item(body=document_definition)

        self.assertEqual(upserted_document.get('id'), document_definition.get('id'))
        self.assertEqual(upserted_document.get('key'), document_definition.get('key'))

        documentlist = list(created_collection.list_items())
        self.assertEqual(2, len(documentlist))

        # delete document
        created_collection.delete_item(item=upserted_document, partition_key=upserted_document.get('id'))

        # query document on the partition key specified in the predicate will pass even without setting enableCrossPartitionQuery or passing in the partitionKey value
        documentlist = list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.id=\'' + replaced_document.get('id') + '\''
            }))
        self.assertEqual(1, len(documentlist))

        # query document on any property other than partitionKey will fail without setting enableCrossPartitionQuery or passing in the partitionKey value
        try:
            list(created_collection.query_items(
                {
                    'query': 'SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\''
                }))
        except Exception:
            pass

        # cross partition query
        documentlist = list(created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',
            enable_cross_partition_query=True
        ))

        self.assertEqual(1, len(documentlist))

        # query document by providing the partitionKey value
        documentlist = list(created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',
            partition_key=replaced_document.get('id')
        ))

        self.assertEqual(1, len(documentlist))


    '''
    #TODO: User class and Permission class implementations
    def test_partitioned_collection_permissions(self):
        created_db = self.databaseForTest

        collection_id = 'test_partitioned_collection_permissions all collection'

        all_collection = created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/key', kind=documents.PartitionKind.Hash)
        )

        collection_id = 'test_partitioned_collection_permissions read collection'

        read_collection = created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/key', kind=documents.PartitionKind.Hash)
        )

        user = created_db.create_user(user={'id': 'user'})

        permission_definition = {
            'id': 'all permission',
            'permissionMode': documents.PermissionMode.All,
            'resource': self.GetDocumentCollectionLink(created_db, all_collection),
            'resourcePartitionKey': [1]
        }

        all_permission = self.client.CreatePermission(self.GetUserLink(created_db, user), permission_definition)

        permission_definition = {
            'id': 'read permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': self.GetDocumentCollectionLink(created_db, read_collection),
            'resourcePartitionKey': [1]
        }

        read_permission = self.client.CreatePermission(self.GetUserLink(created_db, user), permission_definition)

        resource_tokens = {}
        # storing the resource tokens based on Resource IDs
        resource_tokens[all_collection['_rid']] = (all_permission['_token'])
        resource_tokens[read_collection['_rid']] = (read_permission['_token'])

        restricted_client = cosmos_client_connection.CosmosClientConnection(
            CRUDTests.host, {'resourceTokens': resource_tokens}, CRUDTests.connectionPolicy)

        document_definition = {'id': 'document1',
                               'key': 1
                               }

        # Create document in all_collection should succeed since the partitionKey is 1 which is what specified as resourcePartitionKey in permission object and it has all permissions
        created_document = restricted_client.CreateItem(
            self.GetDocumentCollectionLink(created_db, all_collection, False),
            document_definition)

        # Create document in read_collection should fail since it has only read permissions for this collection
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.FORBIDDEN,
            restricted_client.CreateItem,
            self.GetDocumentCollectionLink(created_db, read_collection, False),
            document_definition)

        # Read document feed should succeed for this collection. Note that I need to pass in partitionKey here since permission has resourcePartitionKey defined
        options = {'partitionKey': document_definition.get('key')}
        documentlist = list(restricted_client.ReadItems(
            self.GetDocumentCollectionLink(created_db, read_collection, False),
            options))

        self.assertEqual(0, len(documentlist))

        document_definition['key'] = 2
        options = {'partitionKey': document_definition.get('key')}
        # Create document should fail since the partitionKey is 2 which is different that what is specified as resourcePartitionKey in permission object
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.FORBIDDEN,
            restricted_client.CreateItem,
            self.GetDocumentCollectionLink(created_db, all_collection, False),
            document_definition,
            options)

        document_definition['key'] = 1
        options = {'partitionKey': document_definition.get('key')}
        # Delete document should succeed since the partitionKey is 1 which is what specified as resourcePartitionKey in permission object
        created_document = restricted_client.DeleteItem(
            self.GetDocumentLink(created_db, all_collection, created_document, False),
            options)

        # Delete document in read_collection should fail since it has only read permissions for this collection
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.FORBIDDEN,
            restricted_client.DeleteItem,
            self.GetDocumentCollectionLink(created_db, read_collection, False),
            options)

        self.client.DeleteContainer(self.GetDocumentCollectionLink(created_db, all_collection))
        self.client.DeleteContainer(self.GetDocumentCollectionLink(created_db, read_collection))

    #TODO: Execute sproc implementation
    def test_partitioned_collection_execute_stored_procedure(self):
        created_db = self.databaseForTest

        created_collection = self.configs.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)

        sproc = {
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': (
                'function () {' +
                '   var client = getContext().getCollection();' +
                '   client.createDocument(client.getSelfLink(), { id: \'testDoc\', pk : 2}, {}, function(err, docCreated, options) { ' +
                '   if(err) throw new Error(\'Error while creating document: \' + err.message);' +
                '   else {' +
                '   getContext().getResponse().setBody(1);' +
                '        }' +
                '   });}')
        }

        created_sproc = self.client.CreateStoredProcedure(
            self.GetDocumentCollectionLink(created_db, created_collection), sproc)

        # Partiton Key value same as what is specified in the stored procedure body
        self.client.ExecuteStoredProcedure(self.GetStoredProcedureLink(created_db, created_collection, created_sproc),
                                           None, {'partitionKey': 2})

        # Partiton Key value different than what is specified in the stored procedure body will cause a bad request(400) error
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            self.client.ExecuteStoredProcedure,
            self.GetStoredProcedureLink(created_db, created_collection, created_sproc),
            None,
            {'partitionKey': 3})
    '''
    def test_partitioned_collection_partition_key_value_types(self):
        created_db = self.databaseForTest

        created_collection = self.configs.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)

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

    '''
    TODO: Conflict type
    def test_partitioned_collection_conflict_crud_and_query(self):
        created_db = self.databaseForTest

        created_collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)

        conflict_definition = {'id': 'new conflict',
                               'resourceId': 'doc1',
                               'operationType': 'create',
                               'resourceType': 'document'
                               }

        # Currently, we require to have the partitionKey to be specified as part of options otherwise we get BadRequest(status code 400)
        # self.__AssertHTTPFailureWithStatus(
        #    StatusCodes.BAD_REQUEST,
        #    client.ReadConflict,
        #    self.GetConflictLink(created_db, created_collection, conflict_definition))

        # read conflict here will return resource not found(404) since there is no conflict here
        options = {'partitionKey': conflict_definition.get('id')}
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.NOT_FOUND,
            self.client.ReadConflict,
            self.GetConflictLink(created_db, created_collection, conflict_definition),
            options)

        # Read conflict feed doesn't requires partitionKey to be specified as it's a cross partition thing
        conflictlist = list(self.client.ReadConflicts(self.GetDocumentCollectionLink(created_db, created_collection)))
        self.assertEqual(0, len(conflictlist))

        # Currently, we require to have the partitionKey to be specified as part of options otherwise we get BadRequest(status code 400)
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            self.client.DeleteConflict,
            self.GetConflictLink(created_db, created_collection, conflict_definition))

        # delete conflict here will return resource not found(404) since there is no conflict here
        options = {'partitionKey': conflict_definition.get('id')}
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.NOT_FOUND,
            self.client.DeleteConflict,
            self.GetConflictLink(created_db, created_collection, conflict_definition),
            options)

        # query conflicts on any property other than partitionKey will fail without setting enableCrossPartitionQuery or passing in the partitionKey value
        try:
            list(self.client.QueryConflicts(
                self.GetDocumentCollectionLink(created_db, created_collection),
                {
                    'query': 'SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get(
                        'resourceType') + '\''
                }))
        except Exception:
            pass

        # cross partition query
        options = {'enableCrossPartitionQuery': True}
        conflictlist = list(self.client.QueryConflicts(
            self.GetDocumentCollectionLink(created_db, created_collection),
            {
                'query': 'SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\''
            }, options))

        self.assertEqual(0, len(conflictlist))

        # query conflicts by providing the partitionKey value
        options = {'partitionKey': conflict_definition.get('id')}
        conflictlist = list(self.client.QueryConflicts(
            self.GetDocumentCollectionLink(created_db, created_collection),
            {
                'query': 'SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\''
            }, options))

        self.assertEqual(0, len(conflictlist))

        #TODO: move to document test with multi partiion custom pk
        #document_definition = {'name': 'sample document',
        #                       'spam': 'eggs',
        #                       'key': 'value'}
        # Should throw an error because automatic id generation is disabled always.
        #self.__AssertHTTPFailureWithStatus(
        #    StatusCodes.BAD_REQUEST,
        #    created_collection.create_item,
        #    document_definition
        #)

    '''

    def test_document_crud(self):
        # create database
        created_db = self.databaseForTest
        # create collection
        created_collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
        # read documents
        documents = list(created_collection.list_items())
        # create a document
        before_create_documents_count = len(documents)

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
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
        documents = list(created_collection.list_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
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
            None,
            None,
            {'type': 'IfMatch', 'condition': old_etag},
        )

        # should pass for most recent etag
        replaced_document_conditional = created_collection.replace_item(
                access_condition={'type': 'IfMatch', 'condition': replaced_document['_etag']},
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
        one_document_from_read = created_collection.get_item(
            id=replaced_document['id'],
            partition_key=replaced_document['id']
        )
        self.assertEqual(replaced_document['id'],
                         one_document_from_read['id'])
        # delete document
        created_collection.delete_item(
            item=replaced_document,
            partition_key=replaced_document['id']
        )
        # read documents after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           created_collection.get_item,
                                           replaced_document['id'],
                                           replaced_document['id'])

    def test_murmur_hash(self):
        str = 'afdgdd'
        bytes = bytearray(str, encoding='utf-8')

        hash_value = murmur_hash._MurmurHash._ComputeHash(bytes)
        self.assertEqual(1099701186, hash_value)

        num = 374.0
        bytes = bytearray(pack('d', num))

        hash_value = murmur_hash._MurmurHash._ComputeHash(bytes)
        self.assertEqual(3717946798, hash_value)

        self._validate_bytes("", 0x1B873593, bytearray(b'\xEE\xA8\xA2\x67'), 1738713326)
        self._validate_bytes("1", 0xE82562E4, bytearray(b'\xD0\x92\x24\xED'), 3978597072)
        self._validate_bytes("00", 0xB4C39035, bytearray(b'\xFA\x09\x64\x1B'), 459540986)
        self._validate_bytes("eyetooth", 0x8161BD86, bytearray(b'\x98\x62\x1C\x6F'), 1864131224)
        self._validate_bytes("acid", 0x4DFFEAD7, bytearray(b'\x36\x92\xC0\xB9'), 3116405302)
        self._validate_bytes("elevation", 0x1A9E1828, bytearray(b'\xA9\xB6\x40\xDF'), 3745560233)
        self._validate_bytes("dent", 0xE73C4579, bytearray(b'\xD4\x59\xE1\xD3'), 3554761172)
        self._validate_bytes("homeland", 0xB3DA72CA, bytearray(b'\x06\x4D\x72\xBB'), 3144830214)
        self._validate_bytes("glamor", 0x8078A01B, bytearray(b'\x89\x89\xA2\xA7'), 2812447113)
        self._validate_bytes("flags", 0x4D16CD6C, bytearray(b'\x52\x87\x66\x02'), 40273746)
        self._validate_bytes("democracy", 0x19B4FABD, bytearray(b'\xE4\x55\xD6\xB0'), 2966836708)
        self._validate_bytes("bumble", 0xE653280E, bytearray(b'\xFE\xD7\xC3\x0C'), 214161406)
        self._validate_bytes("catch", 0xB2F1555F, bytearray(b'\x98\x4B\xB6\xCD'), 3451276184)
        self._validate_bytes("omnomnomnivore", 0x7F8F82B0, bytearray(b'\x38\xC4\xCD\xFF'), 4291675192)
        self._validate_bytes("The quick brown fox jumps over the lazy dog", 0x4C2DB001, bytearray(b'\x6D\xAB\x8D\xC9'),
                             3381504877)

    def _validate_bytes(self, str, seed, expected_hash_bytes, expected_value):
        hash_value = murmur_hash._MurmurHash._ComputeHash(bytearray(str, encoding='utf-8'), seed)
        bytes = bytearray(pack('I', hash_value))
        self.assertEqual(expected_value, hash_value)
        self.assertEqual(expected_hash_bytes, bytes)

    def test_get_bytes(self):
        actual_bytes = consistent_hash_ring._ConsistentHashRing._GetBytes("documentdb")
        expected_bytes = bytearray(b'\x64\x6F\x63\x75\x6D\x65\x6E\x74\x64\x62')
        self.assertEqual(expected_bytes, actual_bytes)

        actual_bytes = consistent_hash_ring._ConsistentHashRing._GetBytes("azure")
        expected_bytes = bytearray(b'\x61\x7A\x75\x72\x65')
        self.assertEqual(expected_bytes, actual_bytes)

        actual_bytes = consistent_hash_ring._ConsistentHashRing._GetBytes("json")
        expected_bytes = bytearray(b'\x6A\x73\x6F\x6E')
        self.assertEqual(expected_bytes, actual_bytes)

        actual_bytes = consistent_hash_ring._ConsistentHashRing._GetBytes("nosql")
        expected_bytes = bytearray(b'\x6E\x6F\x73\x71\x6C')
        self.assertEqual(expected_bytes, actual_bytes)

    def test_document_upsert(self):
        # create database
        created_db = self.databaseForTest

        # create collection
        created_collection = self.configs.create_single_partition_collection_if_not_exist(self.client)

        # read documents and check count
        documents = list(created_collection.list_items())
        before_create_documents_count = len(documents)

        # create document definition
        document_definition = {'id': 'doc',
                               'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value'}

        # create document using Upsert API
        created_document = created_collection.upsert_item(body=document_definition)

        # verify id property
        self.assertEqual(created_document['id'],
                         document_definition['id'])

        # read documents after creation and verify updated count
        documents = list(created_collection.list_items())
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
        documents = list(created_collection.list_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'number of documents should remain same')

        created_document['id'] = 'new id'

        # Upsert should create new document since the id is different
        new_document = created_collection.upsert_item(body=created_document)

        # verify id property
        self.assertEqual(created_document['id'],
                         new_document['id'],
                         'document id should be same')

        # read documents after upsert and verify count increases
        documents = list(created_collection.list_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 2,
            'upsert should increase the number of documents')

        # delete documents
        created_collection.delete_item(item=upserted_document, partition_key=upserted_document['id'])
        created_collection.delete_item(item=new_document, partition_key=new_document['id'])

        # read documents after delete and verify count is same as original
        documents = list(created_collection.list_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count,
            'number of documents should remain same')

    #TODO: add fixture to remove container at the end of test
    def test_spatial_index(self):
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

    '''
    def test_user_crud_self_link(self):
        self._test_user_crud(False)

    def test_user_crud_name_based(self):
        self._test_user_crud(True)

    def _test_user_crud(self, is_name_based):
        # Should do User CRUD operations successfully.
        # create database
        db = self.databaseForTest
        # list users
        users = list(self.client.ReadUsers(self.GetDatabaseLink(db, is_name_based)))
        before_create_count = len(users)
        # create user
        user_id = 'new user' + str(uuid.uuid4())
        user = self.client.CreateUser(self.GetDatabaseLink(db, is_name_based), {'id': user_id})
        self.assertEqual(user['id'], user_id, 'user id error')
        # list users after creation
        users = list(self.client.ReadUsers(self.GetDatabaseLink(db, is_name_based)))
        self.assertEqual(len(users), before_create_count + 1)
        # query users
        results = list(self.client.QueryUsers(
            self.GetDatabaseLink(db, is_name_based),
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    {'name': '@id', 'value': user_id}
                ]
            }))
        self.assertTrue(results)

        # replace user
        change_user = user.copy()
        replaced_user_id = 'replaced user' + str(uuid.uuid4())
        user['id'] = replaced_user_id
        replaced_user = self.client.ReplaceUser(self.GetUserLink(db, change_user, is_name_based), user)
        self.assertEqual(replaced_user['id'],
                         replaced_user_id,
                         'user id should change')
        self.assertEqual(user['id'],
                         replaced_user['id'],
                         'user id should stay the same')
        # read user
        user = self.client.ReadUser(self.GetUserLink(db, replaced_user, is_name_based))
        self.assertEqual(replaced_user['id'], user['id'])
        # delete user
        self.client.DeleteUser(self.GetUserLink(db, user, is_name_based))
        # read user after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           self.client.ReadUser,
                                           self.GetUserLink(db, user, is_name_based))

    # Upsert test for User resource - selflink version
    def test_user_upsert_self_link(self):
        self._test_user_upsert(False)

    # Upsert test for User resource - named based routing version
    def test_user_upsert_name_based(self):
        self._test_user_upsert(True)

    def _test_user_upsert(self, is_name_based):
        # create database
        db = self.databaseForTest

        # read users and check count
        users = list(self.client.ReadUsers(self.GetDatabaseLink(db, is_name_based)))
        before_create_count = len(users)

        # create user using Upsert API
        user_id = 'user' + str(uuid.uuid4())
        user = self.client.UpsertUser(self.GetDatabaseLink(db, is_name_based), {'id': user_id})

        # verify id property
        self.assertEqual(user['id'], user_id, 'user id error')

        # read users after creation and verify updated count
        users = list(self.client.ReadUsers(self.GetDatabaseLink(db, is_name_based)))
        self.assertEqual(len(users), before_create_count + 1)

        # Should replace the user since it already exists, there is no public property to change here
        upserted_user = self.client.UpsertUser(self.GetDatabaseLink(db, is_name_based), user)

        # verify id property
        self.assertEqual(upserted_user['id'],
                         user['id'],
                         'user id should remain same')

        # read users after upsert and verify count doesn't increases again
        users = list(self.client.ReadUsers(self.GetDatabaseLink(db, is_name_based)))
        self.assertEqual(len(users), before_create_count + 1)

        user['id'] = 'new user' + str(uuid.uuid4())

        # Upsert should create new user since id is different
        new_user = self.client.UpsertUser(self.GetDatabaseLink(db, is_name_based), user)

        # verify id property
        self.assertEqual(new_user['id'], user['id'], 'user id error')

        # read users after upsert and verify count increases
        users = list(self.client.ReadUsers(self.GetDatabaseLink(db, is_name_based)))
        self.assertEqual(len(users), before_create_count + 2)

        # delete users
        self.client.DeleteUser(self.GetUserLink(db, upserted_user, is_name_based))
        self.client.DeleteUser(self.GetUserLink(db, new_user, is_name_based))

        # read users after delete and verify count remains the same
        users = list(self.client.ReadUsers(self.GetDatabaseLink(db, is_name_based)))
        self.assertEqual(len(users), before_create_count)

    def test_permission_crud_self_link(self):
        self._test_permission_crud(False)

    def test_permission_crud_name_based(self):
        self._test_permission_crud(True)

    def _test_permission_crud(self, is_name_based):
        # Should do Permission CRUD operations successfully
        # create database
        db = self.databaseForTest
        # create user
        user = self.client.CreateUser(self.GetDatabaseLink(db, is_name_based), {'id': 'new user' + str(uuid.uuid4())})
        # list permissions
        permissions = list(self.client.ReadPermissions(self.GetUserLink(db, user, is_name_based)))
        before_create_count = len(permissions)
        permission = {
            'id': 'new permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': 'dbs/AQAAAA==/colls/AQAAAJ0fgTc='  # A random one.
        }
        # create permission
        permission = self.client.CreatePermission(self.GetUserLink(db, user, is_name_based), permission)
        self.assertEqual(permission['id'],
                         'new permission',
                         'permission id error')
        # list permissions after creation
        permissions = list(self.client.ReadPermissions(self.GetUserLink(db, user, is_name_based)))
        self.assertEqual(len(permissions), before_create_count + 1)
        # query permissions
        results = list(self.client.QueryPermissions(
            self.GetUserLink(db, user, is_name_based),
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    {'name': '@id', 'value': permission['id']}
                ]
            }))
        self.assert_(results)

        # replace permission
        change_permission = permission.copy()
        permission['id'] = 'replaced permission'
        replaced_permission = self.client.ReplacePermission(
            self.GetPermissionLink(db, user, change_permission, is_name_based),
            permission)
        self.assertEqual(replaced_permission['id'],
                         'replaced permission',
                         'permission id should change')
        self.assertEqual(permission['id'],
                         replaced_permission['id'],
                         'permission id should stay the same')
        # read permission
        permission = self.client.ReadPermission(self.GetPermissionLink(db, user, replaced_permission, is_name_based))
        self.assertEqual(replaced_permission['id'], permission['id'])
        # delete permission
        self.client.DeletePermission(self.GetPermissionLink(db, user, replaced_permission, is_name_based))
        # read permission after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           self.client.ReadPermission,
                                           self.GetPermissionLink(db, user, permission, is_name_based))

    # Upsert test for Permission resource - selflink version
    def test_permission_upsert_self_link(self):
        self._test_permission_upsert(False)

    # Upsert test for Permission resource - name based routing version
    def test_permission_upsert_name_based(self):
        self._test_permission_upsert(True)

    def _test_permission_upsert(self, is_name_based):
        # create database
        db = self.databaseForTest

        # create user
        user = self.client.CreateUser(self.GetDatabaseLink(db, is_name_based), {'id': 'new user' + str(uuid.uuid4())})

        # read permissions and check count
        permissions = list(self.client.ReadPermissions(self.GetUserLink(db, user, is_name_based)))
        before_create_count = len(permissions)

        permission_definition = {
            'id': 'permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': 'dbs/AQAAAA==/colls/AQAAAJ0fgTc='  # A random one.
        }

        # create permission using Upsert API
        created_permission = self.client.UpsertPermission(self.GetUserLink(db, user, is_name_based),
                                                          permission_definition)

        # verify id property
        self.assertEqual(created_permission['id'],
                         permission_definition['id'],
                         'permission id error')

        # read permissions after creation and verify updated count
        permissions = list(self.client.ReadPermissions(self.GetUserLink(db, user, is_name_based)))
        self.assertEqual(len(permissions), before_create_count + 1)

        # update permission mode
        permission_definition['permissionMode'] = documents.PermissionMode.All

        # should repace the permission since it already exists
        upserted_permission = self.client.UpsertPermission(self.GetUserLink(db, user, is_name_based),
                                                           permission_definition)
        # verify id property
        self.assertEqual(upserted_permission['id'],
                         created_permission['id'],
                         'permission id should remain same')

        # verify changed property
        self.assertEqual(upserted_permission['permissionMode'],
                         permission_definition['permissionMode'],
                         'permissionMode should change')

        # read permissions and verify count doesn't increases again
        permissions = list(self.client.ReadPermissions(self.GetUserLink(db, user, is_name_based)))
        self.assertEqual(len(permissions), before_create_count + 1)

        # update permission id
        created_permission['id'] = 'new permission'
        # resource needs to be changed along with the id in order to create a new permission
        created_permission['resource'] = 'dbs/N9EdAA==/colls/N9EdAIugXgA='

        # should create new permission since id has changed
        new_permission = self.client.UpsertPermission(self.GetUserLink(db, user, is_name_based),
                                                      created_permission)
        # verify id and resource property
        self.assertEqual(new_permission['id'],
                         created_permission['id'],
                         'permission id should be same')

        self.assertEqual(new_permission['resource'],
                         created_permission['resource'],
                         'permission resource should be same')

        # read permissions and verify count increases
        permissions = list(self.client.ReadPermissions(self.GetUserLink(db, user, is_name_based)))
        self.assertEqual(len(permissions), before_create_count + 2)

        # delete permissions
        self.client.DeletePermission(self.GetPermissionLink(db, user, upserted_permission, is_name_based))
        self.client.DeletePermission(self.GetPermissionLink(db, user, new_permission, is_name_based))

        # read permissions and verify count remains the same
        permissions = list(self.client.ReadPermissions(self.GetUserLink(db, user, is_name_based)))
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
            # create collection1
            collection1 = client.CreateContainer(
                db['_self'], {'id': 'test_authorization ' + str(uuid.uuid4())})
            # create document1
            document1 = client.CreateItem(collection1['_self'],
                                          {'id': 'coll1doc1',
                                           'spam': 'eggs',
                                           'key': 'value'})
            # create document 2
            document2 = client.CreateItem(
                collection1['_self'],
                {'id': 'coll1doc2', 'spam': 'eggs2', 'key': 'value2'})
            # create attachment
            dynamic_attachment = {
                'id': 'dynamic attachment',
                'media': 'http://xstore.',
                'MediaType': 'Book',
                'Author': 'My Book Author',
                'Title': 'My Book Title',
                'contentType': 'application/text'
            }
            attachment = client.CreateAttachment(document1['_self'],
                                                 dynamic_attachment)
            # create collection 2
            collection2 = client.CreateContainer(
                db['_self'],
                {'id': 'test_authorization2 ' + str(uuid.uuid4())})
            # create user1
            user1 = client.CreateUser(db['_self'], {'id': 'user1'})
            permission = {
                'id': 'permission On Coll1',
                'permissionMode': documents.PermissionMode.Read,
                'resource': collection1['_self']
            }
            # create permission for collection1
            permission_on_coll1 = client.CreatePermission(user1['_self'],
                                                          permission)
            self.assertTrue(permission_on_coll1['_token'] != None,
                            'permission token is invalid')
            permission = {
                'id': 'permission On Doc1',
                'permissionMode': documents.PermissionMode.All,
                'resource': document2['_self']
            }
            # create permission for document 2
            permission_on_doc2 = client.CreatePermission(user1['_self'],
                                                         permission)
            self.assertTrue(permission_on_doc2['_token'] != None,
                            'permission token is invalid')
            # create user 2
            user2 = client.CreateUser(db['_self'], {'id': 'user2'})
            permission = {
                'id': 'permission On coll2',
                'permissionMode': documents.PermissionMode.All,
                'resource': collection2['_self']
            }
            # create permission on collection 2
            permission_on_coll2 = client.CreatePermission(
                user2['_self'], permission)
            entities = {
                'db': db,
                'coll1': collection1,
                'coll2': collection2,
                'doc1': document1,
                'doc2': document2,
                'user1': user1,
                'user2': user2,
                'attachment': attachment,
                'permissionOnColl1': permission_on_coll1,
                'permissionOnDoc2': permission_on_doc2,
                'permissionOnColl2': permission_on_coll2
            }
            return entities

        # Client without any authorization will fail.
        client = cosmos_client_connection.CosmosClientConnection(CRUDTests.host, {}, CRUDTests.connectionPolicy)
        self.__AssertHTTPFailureWithStatus(StatusCodes.UNAUTHORIZED,
                                           list,
                                           client.ReadDatabases())
        # Client with master key.
        client = cosmos_client_connection.CosmosClientConnection(CRUDTests.host,
                                                                 {'masterKey': CRUDTests.masterKey},
                                                                 CRUDTests.connectionPolicy)
        # setup entities
        entities = __SetupEntities(client)
        resource_tokens = {}
        resource_tokens[entities['coll1']['_rid']] = (
            entities['permissionOnColl1']['_token'])
        resource_tokens[entities['doc1']['_rid']] = (
            entities['permissionOnColl1']['_token'])
        col1_client = cosmos_client_connection.CosmosClientConnection(
            CRUDTests.host, {'resourceTokens': resource_tokens}, CRUDTests.connectionPolicy)
        # 1. Success-- Use Col1 Permission to Read
        success_coll1 = col1_client.ReadContainer(
            entities['coll1']['_self'])
        # 2. Failure-- Use Col1 Permission to delete
        self.__AssertHTTPFailureWithStatus(StatusCodes.FORBIDDEN,
                                           col1_client.DeleteContainer,
                                           success_coll1['_self'])
        # 3. Success-- Use Col1 Permission to Read All Docs
        success_documents = list(col1_client.ReadItems(
            success_coll1['_self']))
        self.assertTrue(success_documents != None,
                        'error reading documents')
        self.assertEqual(len(success_documents),
                         2,
                         'Expected 2 Documents to be succesfully read')
        # 4. Success-- Use Col1 Permission to Read Col1Doc1
        success_doc = col1_client.ReadItem(entities['doc1']['_self'])
        self.assertTrue(success_doc != None, 'error reading document')
        self.assertEqual(
            success_doc['id'],
            entities['doc1']['id'],
            'Expected to read children using parent permissions')
        col2_client = cosmos_client_connection.CosmosClientConnection(
            CRUDTests.host,
            {'permissionFeed': [entities['permissionOnColl2']]}, CRUDTests.connectionPolicy)
        doc = {
            'CustomProperty1': 'BBBBBB',
            'customProperty2': 1000,
            'id': entities['doc2']['id']
        }
        success_doc = col2_client.CreateItem(
            entities['coll2']['_self'], doc)
        self.assertTrue(success_doc != None, 'error creating document')
        self.assertEqual(success_doc['CustomProperty1'],
                         doc['CustomProperty1'],
                         'document should have been created successfully')

        self.client.DeleteContainer(entities['coll1']['_self'])
        self.client.DeleteContainer(entities['coll2']['_self'])

    def test_trigger_crud_self_link(self):
        self._test_trigger_crud(False)

    def test_trigger_crud_name_based(self):
        self._test_trigger_crud(True)

    def _test_trigger_crud(self, is_name_based):
        # create database
        db = self.databaseForTest
        # create collection
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
        # read triggers
        triggers = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        # create a trigger
        before_create_triggers_count = len(triggers)
        trigger_definition = {
            'id': 'sample trigger',
            'serverScript': 'function() {var x = 10;}',
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        }
        trigger = self.client.CreateTrigger(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                            trigger_definition)
        for property in trigger_definition:
            if property != "serverScript":
                self.assertEqual(
                    trigger[property],
                    trigger_definition[property],
                    'property {property} should match'.format(property=property))
            else:
                self.assertEqual(trigger['body'],
                                 'function() {var x = 10;}')

        # read triggers after creation
        triggers = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(triggers),
                         before_create_triggers_count + 1,
                         'create should increase the number of triggers')
        # query triggers
        triggers = list(self.client.QueryTriggers(
            self.GetDocumentCollectionLink(db, collection, is_name_based),
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    {'name': '@id', 'value': trigger_definition['id']}
                ]
            }))
        self.assert_(triggers)

        # replace trigger
        change_trigger = trigger.copy()
        trigger['body'] = 'function() {var x = 20;}'
        replaced_trigger = self.client.ReplaceTrigger(
            self.GetTriggerLink(db, collection, change_trigger, is_name_based), trigger)
        for property in trigger_definition:
            if property != "serverScript":
                self.assertEqual(
                    replaced_trigger[property],
                    trigger[property],
                    'property {property} should match'.format(property=property))
            else:
                self.assertEqual(replaced_trigger['body'],
                                 'function() {var x = 20;}')

        # read trigger
        trigger = self.client.ReadTrigger(self.GetTriggerLink(db, collection, replaced_trigger, is_name_based))
        self.assertEqual(replaced_trigger['id'], trigger['id'])
        # delete trigger
        self.client.DeleteTrigger(self.GetTriggerLink(db, collection, replaced_trigger, is_name_based))
        # read triggers after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           self.client.ReadTrigger,
                                           self.GetTriggerLink(db, collection, replaced_trigger, is_name_based))

    # Upsert test for Trigger resource - selflink version
    def test_trigger_upsert_self_link(self):
        self._test_trigger_upsert(False)

    # Upsert test for Trigger resource - name based routing version
    def test_trigger_upsert_name_based(self):
        self._test_trigger_upsert(True)

    def _test_trigger_upsert(self, is_name_based):
        # create database
        db = self.databaseForTest

        # create collection
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)

        # read triggers and check count
        triggers = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        before_create_triggers_count = len(triggers)

        # create a trigger
        trigger_definition = {
            'id': 'sample trigger',
            'serverScript': 'function() {var x = 10;}',
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        }

        # create trigger using Upsert API
        created_trigger = self.client.UpsertTrigger(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                                    trigger_definition)

        # verify id property
        self.assertEqual(created_trigger['id'],
                         trigger_definition['id'])

        # read triggers after creation and verify updated count
        triggers = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(triggers),
                         before_create_triggers_count + 1,
                         'create should increase the number of triggers')

        # update trigger
        created_trigger['body'] = 'function() {var x = 20;}'

        # should replace trigger since it already exists
        upserted_trigger = self.client.UpsertTrigger(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                                     created_trigger)

        # verify id property
        self.assertEqual(created_trigger['id'],
                         upserted_trigger['id'])

        # verify changed properties
        self.assertEqual(upserted_trigger['body'],
                         created_trigger['body'])

        # read triggers after upsert and verify count remains same
        triggers = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(triggers),
                         before_create_triggers_count + 1,
                         'upsert should keep the number of triggers same')

        # update trigger
        created_trigger['id'] = 'new trigger'

        # should create new trigger since id is changed
        new_trigger = self.client.UpsertTrigger(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                                created_trigger)

        # verify id property
        self.assertEqual(created_trigger['id'],
                         new_trigger['id'])

        # read triggers after upsert and verify count increases
        triggers = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(triggers),
                         before_create_triggers_count + 2,
                         'upsert should increase the number of triggers')

        # delete triggers
        self.client.DeleteTrigger(self.GetTriggerLink(db, collection, upserted_trigger, is_name_based))
        self.client.DeleteTrigger(self.GetTriggerLink(db, collection, new_trigger, is_name_based))

        # read triggers after delete and verify count remains the same
        triggers = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(triggers),
                         before_create_triggers_count,
                         'delete should bring the number of triggers to original')

    def test_udf_crud_self_link(self):
        self._test_udf_crud(False)

    def test_udf_crud_name_based(self):
        self._test_udf_crud(True)

    def _test_udf_crud(self, is_name_based):
        # create database
        db = self.databaseForTest
        # create collection
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
        # read udfs
        udfs = list(self.client.ReadUserDefinedFunctions(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        # create a udf
        before_create_udfs_count = len(udfs)
        udf_definition = {
            'id': 'sample udf',
            'body': 'function() {var x = 10;}'
        }
        udf = self.client.CreateUserDefinedFunction(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                                    udf_definition)
        for property in udf_definition:
            self.assertEqual(
                udf[property],
                udf_definition[property],
                'property {property} should match'.format(property=property))

        # read udfs after creation
        udfs = list(self.client.ReadUserDefinedFunctions(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(udfs),
                         before_create_udfs_count + 1,
                         'create should increase the number of udfs')
        # query udfs
        results = list(self.client.QueryUserDefinedFunctions(
            self.GetDocumentCollectionLink(db, collection, is_name_based),
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    {'name': '@id', 'value': udf_definition['id']}
                ]
            }))
        self.assert_(results)
        # replace udf
        change_udf = udf.copy()
        udf['body'] = 'function() {var x = 20;}'
        replaced_udf = self.client.ReplaceUserDefinedFunction(
            self.GetUserDefinedFunctionLink(db, collection, change_udf, is_name_based), udf)
        for property in udf_definition:
            self.assertEqual(
                replaced_udf[property],
                udf[property],
                'property {property} should match'.format(property=property))
        # read udf
        udf = self.client.ReadUserDefinedFunction(
            self.GetUserDefinedFunctionLink(db, collection, replaced_udf, is_name_based))
        self.assertEqual(replaced_udf['id'], udf['id'])
        # delete udf
        self.client.DeleteUserDefinedFunction(
            self.GetUserDefinedFunctionLink(db, collection, replaced_udf, is_name_based))
        # read udfs after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           self.client.ReadUserDefinedFunction,
                                           self.GetUserDefinedFunctionLink(db, collection, replaced_udf, is_name_based))

    # Upsert test for User Defined Function resource - selflink version
    def test_udf_upsert_self_link(self):
        self._test_udf_upsert(False)

    # Upsert test for User Defined Function resource - name based routing version
    def test_udf_upsert_name_based(self):
        self._test_udf_upsert(True)

    def _test_udf_upsert(self, is_name_based):
        # create database
        db = self.databaseForTest

        # create collection
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)

        # read udfs and check count
        udfs = list(self.client.ReadUserDefinedFunctions(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        before_create_udfs_count = len(udfs)

        # create a udf definition
        udf_definition = {
            'id': 'sample udf',
            'body': 'function() {var x = 10;}'
        }

        # create udf using Upsert API
        created_udf = self.client.UpsertUserDefinedFunction(
            self.GetDocumentCollectionLink(db, collection, is_name_based),
            udf_definition)

        # verify id property
        self.assertEqual(created_udf['id'],
                         udf_definition['id'])

        # read udfs after creation and verify updated count
        udfs = list(self.client.ReadUserDefinedFunctions(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(udfs),
                         before_create_udfs_count + 1,
                         'create should increase the number of udfs')

        # update udf
        created_udf['body'] = 'function() {var x = 20;}'

        # should replace udf since it already exists
        upserted_udf = self.client.UpsertUserDefinedFunction(
            self.GetDocumentCollectionLink(db, collection, is_name_based), created_udf)

        # verify id property
        self.assertEqual(created_udf['id'],
                         upserted_udf['id'])

        # verify changed property
        self.assertEqual(upserted_udf['body'],
                         created_udf['body'])

        # read udf and verify count doesn't increases again
        udfs = list(self.client.ReadUserDefinedFunctions(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(udfs),
                         before_create_udfs_count + 1,
                         'upsert should keep the number of udfs same')

        created_udf['id'] = 'new udf'

        # should create new udf since the id is different
        new_udf = self.client.UpsertUserDefinedFunction(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                                        created_udf)

        # verify id property
        self.assertEqual(created_udf['id'],
                         new_udf['id'])

        # read udf and verify count increases
        udfs = list(self.client.ReadUserDefinedFunctions(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(udfs),
                         before_create_udfs_count + 2,
                         'upsert should keep the number of udfs same')

        # delete udfs
        self.client.DeleteUserDefinedFunction(
            self.GetUserDefinedFunctionLink(db, collection, upserted_udf, is_name_based))
        self.client.DeleteUserDefinedFunction(self.GetUserDefinedFunctionLink(db, collection, new_udf, is_name_based))

        # read udf and verify count remains the same
        udfs = list(self.client.ReadUserDefinedFunctions(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(udfs),
                         before_create_udfs_count,
                         'delete should keep the number of udfs same')

    def test_sproc_crud_self_link(self):
        self._test_sproc_crud(False)

    def test_sproc_crud_name_based(self):
        self._test_sproc_crud(True)

    def _test_sproc_crud(self, is_name_based):
        # create database
        db = self.databaseForTest
        # create collection
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
        # read sprocs
        sprocs = list(self.client.ReadStoredProcedures(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        # create a sproc
        before_create_sprocs_count = len(sprocs)
        sproc_definition = {
            'id': 'sample sproc',
            'serverScript': 'function() {var x = 10;}'
        }
        sproc = self.client.CreateStoredProcedure(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                                  sproc_definition)
        for property in sproc_definition:
            if property != "serverScript":
                self.assertEqual(
                    sproc[property],
                    sproc_definition[property],
                    'property {property} should match'.format(property=property))
            else:
                self.assertEqual(sproc['body'], 'function() {var x = 10;}')

        # read sprocs after creation
        sprocs = list(self.client.ReadStoredProcedures(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(sprocs),
                         before_create_sprocs_count + 1,
                         'create should increase the number of sprocs')
        # query sprocs
        sprocs = list(self.client.QueryStoredProcedures(
            self.GetDocumentCollectionLink(db, collection, is_name_based),
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    {'name': '@id', 'value': sproc_definition['id']}
                ]
            }))
        self.assert_(sprocs)
        # replace sproc
        change_sproc = sproc.copy()
        sproc['body'] = 'function() {var x = 20;}'
        replaced_sproc = self.client.ReplaceStoredProcedure(
            self.GetStoredProcedureLink(db, collection, change_sproc, is_name_based),
            sproc)
        for property in sproc_definition:
            if property != 'serverScript':
                self.assertEqual(
                    replaced_sproc[property],
                    sproc[property],
                    'property {property} should match'.format(property=property))
            else:
                self.assertEqual(replaced_sproc['body'],
                                 "function() {var x = 20;}")
        # read sproc
        sproc = self.client.ReadStoredProcedure(
            self.GetStoredProcedureLink(db, collection, replaced_sproc, is_name_based))
        self.assertEqual(replaced_sproc['id'], sproc['id'])
        # delete sproc
        self.client.DeleteStoredProcedure(self.GetStoredProcedureLink(db, collection, replaced_sproc, is_name_based))
        # read sprocs after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           self.client.ReadStoredProcedure,
                                           self.GetStoredProcedureLink(db, collection, replaced_sproc, is_name_based))

    # Upsert test for sproc resource - selflink version
    def test_sproc_upsert_self_link(self):
        self._test_sproc_upsert(False)

    # Upsert test for sproc resource - name based routing version
    def test_sproc_upsert_name_based(self):
        self._test_sproc_upsert(True)

    def _test_sproc_upsert(self, is_name_based):
        # create database
        db = self.databaseForTest

        # create collection
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)

        # read sprocs and check count
        sprocs = list(self.client.ReadStoredProcedures(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        before_create_sprocs_count = len(sprocs)

        # create a sproc definition
        sproc_definition = {
            'id': 'sample sproc',
            'serverScript': 'function() {var x = 10;}'
        }

        # create sproc using Upsert API
        created_sproc = self.client.UpsertStoredProcedure(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                                          sproc_definition)

        # verify id property
        self.assertEqual(created_sproc['id'],
                         sproc_definition['id'])

        # read sprocs after creation and verify updated count
        sprocs = list(self.client.ReadStoredProcedures(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(sprocs),
                         before_create_sprocs_count + 1,
                         'create should increase the number of sprocs')

        # update sproc
        created_sproc['body'] = 'function() {var x = 20;}'

        # should replace sproc since it already exists
        upserted_sproc = self.client.UpsertStoredProcedure(
            self.GetDocumentCollectionLink(db, collection, is_name_based),
            created_sproc)

        # verify id property
        self.assertEqual(created_sproc['id'],
                         upserted_sproc['id'])

        # verify changed property
        self.assertEqual(upserted_sproc['body'],
                         created_sproc['body'])

        # read sprocs after upsert and verify count remains the same
        sprocs = list(self.client.ReadStoredProcedures(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(sprocs),
                         before_create_sprocs_count + 1,
                         'upsert should keep the number of sprocs same')

        # update sproc
        created_sproc['id'] = 'new sproc'

        # should create new sproc since id is different
        new_sproc = self.client.UpsertStoredProcedure(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                                      created_sproc)

        # verify id property
        self.assertEqual(created_sproc['id'],
                         new_sproc['id'])

        # read sprocs after upsert and verify count increases
        sprocs = list(self.client.ReadStoredProcedures(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(sprocs),
                         before_create_sprocs_count + 2,
                         'upsert should keep the number of sprocs same')

        # delete sprocs
        self.client.DeleteStoredProcedure(self.GetStoredProcedureLink(db, collection, upserted_sproc, is_name_based))
        self.client.DeleteStoredProcedure(self.GetStoredProcedureLink(db, collection, new_sproc, is_name_based))

        # read sprocs after delete and verify count remains same
        sprocs = list(self.client.ReadStoredProcedures(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(sprocs),
                         before_create_sprocs_count,
                         'delete should keep the number of sprocs same')

    def test_scipt_logging_execute_stored_procedure(self):
        created_db = self.databaseForTest

        created_collection = self.configs.create_single_partition_collection_if_not_exist(self.client)

        sproc = {
            'id': 'storedProcedure' + str(uuid.uuid4()),
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

        created_sproc = self.client.CreateStoredProcedure(
            self.GetDocumentCollectionLink(created_db, created_collection), sproc)

        result = self.client.ExecuteStoredProcedure(
            self.GetStoredProcedureLink(created_db, created_collection, created_sproc), None)

        self.assertEqual(result, 'Success!')
        self.assertFalse(HttpHeaders.ScriptLogResults in self.client.last_response_headers)

        options = {'enableScriptLogging': True}
        result = self.client.ExecuteStoredProcedure(
            self.GetStoredProcedureLink(created_db, created_collection, created_sproc), None, options)

        self.assertEqual(result, 'Success!')
        self.assertEqual(urllib.quote('The value of x is 1.'),
                         self.client.last_response_headers.get(HttpHeaders.ScriptLogResults))

        options = {'enableScriptLogging': False}
        result = self.client.ExecuteStoredProcedure(
            self.GetStoredProcedureLink(created_db, created_collection, created_sproc), None, options)

        self.assertEqual(result, 'Success!')
        self.assertFalse(HttpHeaders.ScriptLogResults in self.client.last_response_headers)
    '''

    def test_collection_indexing_policy(self):
        # create database
        db = self.databaseForTest
        # create collection
        collection = db.create_container(
            id='test_collection_indexing_policy default policy' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/id', kind='Hash')
        )

        self.assertEqual(collection.properties['indexingPolicy']['indexingMode'],
                         documents.IndexingMode.Consistent,
                         'default indexing mode should be consistent')

        db.delete_container(container=collection)

        lazy_collection = db.create_container(
            id='test_collection_indexing_policy lazy collection ' + str(uuid.uuid4()),
            indexing_policy={
                'indexingMode': documents.IndexingMode.Lazy
            },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )

        self.assertEqual(lazy_collection.properties['indexingPolicy']['indexingMode'],
                         documents.IndexingMode.Lazy,
                         'indexing mode should be lazy')

        db.delete_container(container=lazy_collection)

        consistent_collection = db.create_container(
            id='test_collection_indexing_policy consistent collection ' + str(uuid.uuid4()),
            indexing_policy={
                'indexingMode': documents.IndexingMode.Consistent
            },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )

        self.assertEqual(consistent_collection.properties['indexingPolicy']['indexingMode'],
                         documents.IndexingMode.Consistent,
                         'indexing mode should be consistent')

        db.delete_container(container=consistent_collection)

        collection_with_indexing_policy = db.create_container(
            id='CollectionWithIndexingPolicy ' + str(uuid.uuid4()),
            indexing_policy={
                'automatic': True,
                'indexingMode': documents.IndexingMode.Lazy,
                'includedPaths': [
                    {
                        'path': '/',
                        'indexes': [
                            {
                                'kind': documents.IndexKind.Hash,
                                'dataType': documents.DataType.Number,
                                'precision': 2
                            }
                        ]
                    }
                ],
                'excludedPaths': [
                    {
                        'path': '/"systemMetadata"/*'
                    }
                ]
            },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )

        self.assertEqual(1,
                         len(collection_with_indexing_policy.properties['indexingPolicy']['includedPaths']),
                         'Unexpected includedPaths length')
        self.assertEqual(2,
                         len(collection_with_indexing_policy.properties['indexingPolicy']['excludedPaths']),
                         'Unexpected excluded path count')
        db.delete_container(container=collection_with_indexing_policy)

    def test_create_default_indexing_policy(self):
        # create database
        db = self.databaseForTest

        # no indexing policy specified
        collection = db.create_container(
            id='test_create_default_indexing_policy TestCreateDefaultPolicy01' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        self._check_default_indexing_policy_paths(collection.properties['indexingPolicy'])
        db.delete_container(container=collection)

        # partial policy specified
        collection = db.create_container(
            id='test_create_default_indexing_policy TestCreateDefaultPolicy01' + str(uuid.uuid4()),
            indexing_policy={
                    'indexingMode': documents.IndexingMode.Lazy, 'automatic': True
                },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        self._check_default_indexing_policy_paths(collection.properties['indexingPolicy'])
        db.delete_container(container=collection)

        # default policy
        collection = db.create_container(
            id='test_create_default_indexing_policy TestCreateDefaultPolicy03' + str(uuid.uuid4()),
            indexing_policy={},
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        self._check_default_indexing_policy_paths(collection.properties['indexingPolicy'])
        db.delete_container(container=collection)

        # missing indexes
        collection = db.create_container(
            id='test_create_default_indexing_policy TestCreateDefaultPolicy04' + str(uuid.uuid4()),
            indexing_policy={
                    'includedPaths': [
                        {
                            'path': '/*'
                        }
                    ]
                },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        self._check_default_indexing_policy_paths(collection.properties['indexingPolicy'])
        db.delete_container(container=collection)

        # missing precision
        collection = db.create_container(
            id='test_create_default_indexing_policy TestCreateDefaultPolicy05' + str(uuid.uuid4()),
            indexing_policy={
                    'includedPaths': [
                        {
                            'path': '/*',
                            'indexes': [
                                {
                                    'kind': documents.IndexKind.Hash,
                                    'dataType': documents.DataType.String
                                },
                                {
                                    'kind': documents.IndexKind.Range,
                                    'dataType': documents.DataType.Number
                                }
                            ]
                        }
                    ]
                },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        self._check_default_indexing_policy_paths(collection.properties['indexingPolicy'])
        db.delete_container(container=collection)

    def _check_default_indexing_policy_paths(self, indexing_policy):
        def __get_first(array):
            if array:
                return array[0]
            else:
                return None

        # '/_etag' is present in excluded paths by default
        self.assertEqual(1, len(indexing_policy['excludedPaths']))
        # included paths should be 1: '/'.
        self.assertEqual(1, len(indexing_policy['includedPaths']))

        root_included_path = __get_first([included_path for included_path in indexing_policy['includedPaths']
                                          if included_path['path'] == '/*'])
        self.assertEqual(0, len(root_included_path['indexes']))
        print(root_included_path['indexes'])

    def test_client_request_timeout(self):
        connection_policy = documents.ConnectionPolicy()
        # making timeout 1 ms to make sure it will throw
        connection_policy.RequestTimeout = 1
        with self.assertRaises(Exception):
            # client does a getDatabaseAccount on initialization, which will time out
            cosmos_client.CosmosClient(CRUDTests.host, {'masterKey': CRUDTests.masterKey}, "Session", connection_policy)

    def test_query_iterable_functionality(self):
        def __create_resources(client):
            """Creates resources for this test.

            :Parameters:
                - `client`: cosmos_client_connection.CosmosClientConnection

            :Returns:
                dict

            """
            collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
            doc1 = collection.create_item(body={'id': 'doc1', 'prop1': 'value1'})
            doc2 = collection.create_item(body={'id': 'doc2', 'prop1': 'value2'})
            doc3 = collection.create_item(body={'id': 'doc3', 'prop1': 'value3'})
            resources = {
                'coll': collection,
                'doc1': doc1,
                'doc2': doc2,
                'doc3': doc3
            }
            return resources

        # Validate QueryIterable by converting it to a list.
        resources = __create_resources(self.client)
        results = resources['coll'].list_items(max_item_count=2)
        docs = list(iter(results))
        self.assertEqual(3,
                         len(docs),
                         'QueryIterable should return all documents' +
                         ' using continuation')
        self.assertEqual(resources['doc1']['id'], docs[0]['id'])
        self.assertEqual(resources['doc2']['id'], docs[1]['id'])
        self.assertEqual(resources['doc3']['id'], docs[2]['id'])

        # Validate QueryIterable iterator with 'for'.
        results = resources['coll'].list_items(max_item_count=2)
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
        results = resources['coll'].list_items(max_item_count=2)
        first_block = results.fetch_next_block()
        self.assertEqual(2,
                         len(first_block),
                         'First block should have 2 entries.')
        self.assertEqual(resources['doc1']['id'], first_block[0]['id'])
        self.assertEqual(resources['doc2']['id'], first_block[1]['id'])
        self.assertEqual(1,
                         len(results.fetch_next_block()),
                         'Second block should have 1 entry.')
        self.assertEqual(0,
                         len(results.fetch_next_block()),
                         'Then its empty.')

    '''
    def test_trigger_functionality_self_link(self):
        self._test_trigger_functionality(False)

    def test_trigger_functionality_name_based(self):
        self._test_trigger_functionality(True)

    def _test_trigger_functionality(self, is_name_based):
        triggers_in_collection1 = [
            {
                'id': 't1',
                'body': (
                    'function() {' +
                    '    var item = getContext().getRequest().getBody();' +
                    '    item.id = item.id.toUpperCase() + \'t1\';' +
                    '    getContext().getRequest().setBody(item);' +
                    '}'),
                'triggerType': documents.TriggerType.Pre,
                'triggerOperation': documents.TriggerOperation.All
            },
            {
                'id': 'response1',
                'body': (
                    'function() {' +
                    '    var prebody = getContext().getRequest().getBody();' +
                    '    if (prebody.id != \'TESTING POST TRIGGERt1\')'
                    '        throw \'id mismatch\';' +
                    '    var postbody = getContext().getResponse().getBody();' +
                    '    if (postbody.id != \'TESTING POST TRIGGERt1\')'
                    '        throw \'id mismatch\';'
                    '}'),
                'triggerType': documents.TriggerType.Post,
                'triggerOperation': documents.TriggerOperation.All
            },
            {
                'id': 'response2',
                # can't be used because setValue is currently disabled
                'body': (
                    'function() {' +
                    '    var predoc = getContext().getRequest().getBody();' +
                    '    var postdoc = getContext().getResponse().getBody();' +
                    '    getContext().getResponse().setValue(' +
                    '        \'predocname\', predoc.id + \'response2\');' +
                    '    getContext().getResponse().setValue(' +
                    '        \'postdocname\', postdoc.id + \'response2\');' +
                    '}'),
                'triggerType': documents.TriggerType.Post,
                'triggerOperation': documents.TriggerOperation.All,
            }]
        triggers_in_collection2 = [
            {
                'id': "t2",
                'body': "function() { }",  # trigger already stringified
                'triggerType': documents.TriggerType.Pre,
                'triggerOperation': documents.TriggerOperation.All
            },
            {
                'id': "t3",
                'body': (
                    'function() {' +
                    '    var item = getContext().getRequest().getBody();' +
                    '    item.id = item.id.toLowerCase() + \'t3\';' +
                    '    getContext().getRequest().setBody(item);' +
                    '}'),
                'triggerType': documents.TriggerType.Pre,
                'triggerOperation': documents.TriggerOperation.All
            }]
        triggers_in_collection3 = [
            {
                'id': 'triggerOpType',
                'body': 'function() { }',
                'triggerType': documents.TriggerType.Post,
                'triggerOperation': documents.TriggerOperation.Delete,
            }]

        def __CreateTriggers(client, database, collection, triggers, is_name_based):
            """Creates triggers.

            :Parameters:
                - `client`: cosmos_client_connection.CosmosClientConnection
                - `collection`: dict

            """
            for trigger_i in triggers:
                trigger = client.CreateTrigger(self.GetDocumentCollectionLink(database, collection, is_name_based),
                                               trigger_i)
                for property in trigger_i:
                    self.assertEqual(
                        trigger[property],
                        trigger_i[property],
                        'property {property} should match'.format(property=property))

        # create database
        db = self.databaseForTest
        # create collections
        collection1 = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based), {'id': 'test_trigger_functionality 1 ' + str(uuid.uuid4())})
        collection2 = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based), {'id': 'test_trigger_functionality 2 ' + str(uuid.uuid4())})
        collection3 = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based), {'id': 'test_trigger_functionality 3 ' + str(uuid.uuid4())})
        # create triggers
        __CreateTriggers(self.client, db, collection1, triggers_in_collection1, is_name_based)
        __CreateTriggers(self.client, db, collection2, triggers_in_collection2, is_name_based)
        __CreateTriggers(self.client, db, collection3, triggers_in_collection3, is_name_based)
        # create document
        triggers_1 = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection1, is_name_based)))
        self.assertEqual(len(triggers_1), 3)
        document_1_1 = self.client.CreateItem(self.GetDocumentCollectionLink(db, collection1, is_name_based),
                                              {'id': 'doc1',
                                               'key': 'value'},
                                              {'preTriggerInclude': 't1'})
        self.assertEqual(document_1_1['id'],
                         'DOC1t1',
                         'id should be capitalized')
        document_1_2 = self.client.CreateItem(
            self.GetDocumentCollectionLink(db, collection1, is_name_based),
            {'id': 'testing post trigger'},
            {'postTriggerInclude': 'response1',
             'preTriggerInclude': 't1'})
        self.assertEqual(document_1_2['id'], 'TESTING POST TRIGGERt1')
        document_1_3 = self.client.CreateItem(self.GetDocumentCollectionLink(db, collection1, is_name_based),
                                              {'id': 'responseheaders'},
                                              {'preTriggerInclude': 't1'})
        self.assertEqual(document_1_3['id'], "RESPONSEHEADERSt1")

        triggers_2 = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection2, is_name_based)))
        self.assertEqual(len(triggers_2), 2)
        document_2_1 = self.client.CreateItem(self.GetDocumentCollectionLink(db, collection2, is_name_based),
                                              {'id': 'doc2',
                                               'key2': 'value2'},
                                              {'preTriggerInclude': 't2'})
        self.assertEqual(document_2_1['id'],
                         'doc2',
                         'id shouldn\'t change')
        document_2_2 = self.client.CreateItem(self.GetDocumentCollectionLink(db, collection2, is_name_based),
                                              {'id': 'Doc3',
                                               'prop': 'empty'},
                                              {'preTriggerInclude': 't3'})
        self.assertEqual(document_2_2['id'], 'doc3t3')

        triggers_3 = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection3, is_name_based)))
        self.assertEqual(len(triggers_3), 1)
        with self.assertRaises(Exception):
            self.client.CreateItem(self.GetDocumentCollectionLink(db, collection3, is_name_based),
                                   {'id': 'Docoptype'},
                                   {'postTriggerInclude': 'triggerOpType'})

        self.client.DeleteContainer(collection1['_self'])
        self.client.DeleteContainer(collection2['_self'])
        self.client.DeleteContainer(collection3['_self'])

    def test_stored_procedure_functionality_self_link(self):
        self._test_stored_procedure_functionality(False)

    def test_stored_procedure_functionality_name_based(self):
        self._test_stored_procedure_functionality(True)

    def _test_stored_procedure_functionality(self, is_name_based):
        # create database
        db = self.databaseForTest
        # create collection
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)

        sproc1 = {
            'id': 'storedProcedure1' + str(uuid.uuid4()),
            'body': (
                'function () {' +
                '  for (var i = 0; i < 1000; i++) {' +
                '    var item = getContext().getResponse().getBody();' +
                '    if (i > 0 && item != i - 1) throw \'body mismatch\';' +
                '    getContext().getResponse().setBody(i);' +
                '  }' +
                '}')
        }

        retrieved_sproc = self.client.CreateStoredProcedure(
            self.GetDocumentCollectionLink(db, collection, is_name_based),
            sproc1)
        result = self.client.ExecuteStoredProcedure(
            self.GetStoredProcedureLink(db, collection, retrieved_sproc, is_name_based),
            None)
        self.assertEqual(result, 999)
        sproc2 = {
            'id': 'storedProcedure2' + str(uuid.uuid4()),
            'body': (
                'function () {' +
                '  for (var i = 0; i < 10; i++) {' +
                '    getContext().getResponse().appendValue(\'Body\', i);' +
                '  }' +
                '}')
        }
        retrieved_sproc2 = self.client.CreateStoredProcedure(
            self.GetDocumentCollectionLink(db, collection, is_name_based),
            sproc2)
        result = self.client.ExecuteStoredProcedure(
            self.GetStoredProcedureLink(db, collection, retrieved_sproc2, is_name_based),
            None)
        self.assertEqual(int(result), 123456789)
        sproc3 = {
            'id': 'storedProcedure3' + str(uuid.uuid4()),
            'body': (
                'function (input) {' +
                '  getContext().getResponse().setBody(' +
                '      \'a\' + input.temp);' +
                '}')
        }
        retrieved_sproc3 = self.client.CreateStoredProcedure(
            self.GetDocumentCollectionLink(db, collection, is_name_based),
            sproc3)
        result = self.client.ExecuteStoredProcedure(
            self.GetStoredProcedureLink(db, collection, retrieved_sproc3, is_name_based),
            {'temp': 'so'})
        self.assertEqual(result, 'aso')
    '''

    def __ValidateOfferResponseBody(self, offer, expected_coll_link, expected_offer_type):
        # type: (Offer, str, Any) -> None
        self.assertIsNotNone(offer.properties['id'], 'Id cannot be null.')
        self.assertIsNotNone(offer.properties.get('_rid'), 'Resource Id (Rid) cannot be null.')
        self.assertIsNotNone(offer.properties.get('_self'), 'Self Link cannot be null.')
        self.assertIsNotNone(offer.properties.get('resource'), 'Resource Link cannot be null.')
        self.assertTrue(offer.properties['_self'].find(offer.properties['id']) != -1,
                        'Offer id not contained in offer self link.')
        self.assertEqual(expected_coll_link.strip('/'), offer.properties['resource'].strip('/'))
        if (expected_offer_type):
            self.assertEqual(expected_offer_type, offer.properties.get('offerType'))

    def test_offer_read_and_query(self):
        # Create database.
        db = self.databaseForTest

        # Create collection.
        collection = db.create_container(
            id='test_offer_read_and_query ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        # Read the offer.
        expected_offer = collection.read_offer()
        self.__ValidateOfferResponseBody(expected_offer, collection.properties.get('_self'), None)

        # Now delete the collection.
        db.delete_container(container=collection)
        # Reading fails.
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND, collection.read_offer)

    # TODO: fix on offer type
    def test_offer_replace(self):
        # Create database.
        db = self.databaseForTest
        # Create collection.
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
        # Read Offer
        expected_offer = collection.read_offer()
        self.__ValidateOfferResponseBody(expected_offer, collection.properties.get('_self'), None)
        # Replace the offer.
        replaced_offer = collection.replace_throughput(expected_offer.offer_throughput + 100)
        self.__ValidateOfferResponseBody(replaced_offer, collection.properties.get('_self'), None)
        # Check if the replaced offer is what we expect.
        self.assertEqual(expected_offer.properties.get('content').get('offerThroughput') + 100,
                         replaced_offer.properties.get('content').get('offerThroughput'))
        self.assertEqual(expected_offer.offer_throughput + 100,
                         replaced_offer.offer_throughput)

    def test_database_account_functionality(self):
        # Validate database account functionality.
        database_account = self.client.get_database_account()
        self.assertEqual(database_account.DatabasesLink, '/dbs/')
        self.assertEqual(database_account.MediaLink, '/media/')
        if (HttpHeaders.MaxMediaStorageUsageInMB in
                self.client.client_connection.last_response_headers):
            self.assertEqual(
                database_account.MaxMediaStorageUsageInMB,
                self.client.client_connection.last_response_headers[
                    HttpHeaders.MaxMediaStorageUsageInMB])
        if (HttpHeaders.CurrentMediaStorageUsageInMB in
                self.client.client_connection.last_response_headers):
            self.assertEqual(
                database_account.CurrentMediaStorageUsageInMB,
                self.client.client_connection.last_response_headers[
                    HttpHeaders.CurrentMediaStorageUsageInMB])
        self.assertIsNotNone(database_account.ConsistencyPolicy['defaultConsistencyLevel'])

    #TODO: add fixture to remove container at the end of test
    def test_index_progress_headers(self):
        created_db = self.databaseForTest
        consistent_coll = created_db.create_container(
            id='test_index_progress_headers consistent_coll ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id", kind='Hash'),
        )
        created_db.get_container(container=consistent_coll, populate_quota_info=True)
        self.assertFalse(HttpHeaders.LazyIndexingProgress in created_db.client_connection.last_response_headers)
        self.assertTrue(HttpHeaders.IndexTransformationProgress in created_db.client_connection.last_response_headers)

        lazy_coll = created_db.create_container(
            id='test_index_progress_headers lazy_coll ' + str(uuid.uuid4()),
            indexing_policy={'indexingMode': documents.IndexingMode.Lazy},
            partition_key=PartitionKey(path="/id", kind='Hash')
        )
        created_db.get_container(container=lazy_coll, populate_quota_info=True)
        self.assertTrue(HttpHeaders.LazyIndexingProgress in created_db.client_connection.last_response_headers)
        self.assertTrue(HttpHeaders.IndexTransformationProgress in created_db.client_connection.last_response_headers)

        none_coll = created_db.create_container(
            id='test_index_progress_headers none_coll ' + str(uuid.uuid4()),
            indexing_policy={
                'indexingMode': documents.IndexingMode.NoIndex,
                'automatic': False
            },
            partition_key=PartitionKey(path="/id", kind='Hash')
        )
        created_db.get_container(container=none_coll, populate_quota_info=True)
        self.assertFalse(HttpHeaders.LazyIndexingProgress in created_db.client_connection.last_response_headers)
        self.assertTrue(HttpHeaders.IndexTransformationProgress in created_db.client_connection.last_response_headers)

        created_db.delete_container(consistent_coll)
        created_db.delete_container(lazy_coll)
        created_db.delete_container(none_coll)

    def test_id_validation(self):
        # Id shouldn't end with space.
        try:
            self.client.create_database(id='id_with_space ')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id ends with a space.', e.args[0])
        # Id shouldn't contain '/'.

        try:
            self.client.create_database(id='id_with_illegal/_char')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])
        # Id shouldn't contain '\\'.

        try:
            self.client.create_database(id='id_with_illegal\\_char')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])
        # Id shouldn't contain '?'.

        try:
            self.client.create_database(id='id_with_illegal?_char')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])
        # Id shouldn't contain '#'.

        try:
            self.client.create_database(id='id_with_illegal#_char')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])

        # Id can begin with space
        db = self.client.create_database(id=' id_begin_space')
        self.assertTrue(True)

        self.client.delete_database(database=db)

    #TODO: add fixture to remove container at the end of test
    def test_id_case_validation(self):
        # create database
        created_db = self.databaseForTest

        uuid_string = str(uuid.uuid4())
        collection_id1 = 'sampleCollection ' + uuid_string
        collection_id2 = 'SampleCollection ' + uuid_string

        # Verify that no collections exist
        collections = list(created_db.list_containers())
        number_of_existing_collections = len(collections)

        # create 2 collections with different casing of IDs
        # pascalCase
        created_collection1 = created_db.create_container(
            id=collection_id1,
            partition_key=PartitionKey(path='/id', kind='Hash')
        )

        # CamelCase
        created_collection2 = created_db.create_container(
            id=collection_id2,
            partition_key=PartitionKey(path='/id', kind='Hash')
        )

        collections = list(created_db.list_containers())

        # verify if a total of 2 collections got created
        self.assertEqual(len(collections), number_of_existing_collections + 2)

        # verify that collections are created with specified IDs
        self.assertEqual(collection_id1, created_collection1.id)
        self.assertEqual(collection_id2, created_collection2.id)

        created_db.delete_container(created_collection1)
        created_db.delete_container(created_collection2)

    #TODO: add fixture to remove container at the end of test
    def test_id_unicode_validation(self):
        # create database
        created_db = self.databaseForTest

        # unicode chars in Hindi for Id which translates to: "Hindi is the national language of India"
        collection_id1 = u'हिन्दी भारत की राष्ट्रीय भाषा है'

        # Special chars for Id
        collection_id2 = "!@$%^&*()-~`'_[]{}|;:,.<>"

        # verify that collections are created with specified IDs
        created_collection1 = created_db.create_container(
            id=collection_id1,
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        created_collection2 = created_db.create_container(
            id=collection_id2,
            partition_key=PartitionKey(path='/id', kind='Hash')
        )

        self.assertEqual(collection_id1, created_collection1.id)
        self.assertEqual(collection_id2, created_collection2.id)

        created_db.delete_container(created_collection1)
        created_db.delete_container(created_collection2)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True:  # raised by sys.exit(True) when tests failed
            raise
