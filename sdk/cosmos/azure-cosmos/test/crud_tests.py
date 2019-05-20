<<<<<<< HEAD
﻿#The MIT License (MIT)
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
=======
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
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

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
<<<<<<< HEAD
=======

>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
if six.PY2:
    import urllib as urllib
else:
    import urllib.parse as urllib
import uuid
import pytest
<<<<<<< HEAD
import azure.cosmos.base as base
import azure.cosmos.consistent_hash_ring as consistent_hash_ring
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import azure.cosmos.hash_partition_resolver as hash_partition_resolver
from azure.cosmos.http_constants import HttpHeaders, StatusCodes, SubStatusCodes
import azure.cosmos.murmur_hash as murmur_hash
import azure.cosmos.range_partition_resolver as range_partition_resolver
import azure.cosmos.range as partition_range
import test_config
import test_partition_resolver
import azure.cosmos.base as base


#IMPORTANT NOTES: 
  
#  	Most test cases in this file create collections in your Azure Cosmos account.
#  	Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.
  
#  	To Run the test, replace the two member fields (masterKey and host) with values 
=======
import azure.cosmos.consistent_hash_ring as consistent_hash_ring
import azure.cosmos.documents as documents
import azure.cosmos.errors as errors
from azure.cosmos.http_constants import HttpHeaders, StatusCodes, SubStatusCodes
import azure.cosmos.murmur_hash as murmur_hash
import test.test_config as test_config
import azure.cosmos.base as base
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.partition_key import PartitionKey
import test.conftest as conftest
import azure.cosmos.retry_utility as retry_utility

# IMPORTANT NOTES:

#  	Most test cases in this file create collections in your Azure Cosmos account.
#  	Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.

#  	To Run the test, replace the two member fields (masterKey and host) with values
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
#   associated with your Azure Cosmos account.

@pytest.mark.usefixtures("teardown")
class CRUDTests(unittest.TestCase):
    """Python CRUD Tests.
    """

    configs = test_config._test_config
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
<<<<<<< HEAD
    client = cosmos_client.CosmosClient(host, {'masterKey': masterKey}, connectionPolicy)
    databseForTest = configs.create_database_if_not_exist(client)
=======
    client = cosmos_client.CosmosClient(host, {'masterKey': masterKey}, "Session", connectionPolicy)
    databaseForTest = configs.create_database_if_not_exist(client)
    last_headers = []
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

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
<<<<<<< HEAD
                cls.host == '[YOUR_ENDPOINT_HERE]'):
=======
                    cls.host == '[YOUR_ENDPOINT_HERE]'):
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    def setUp(self):
<<<<<<< HEAD
        self.client = cosmos_client.CosmosClient(self.host, {'masterKey': self.masterKey}, self.connectionPolicy)

    def test_database_crud_self_link(self):
        self._test_database_crud(False)

    def test_database_crud_name_based(self):
        self._test_database_crud(True)

    def _test_database_crud(self, is_name_based):
        # read databases.
        databases = list(self.client.ReadDatabases())
        # create a database.
        before_create_databases_count = len(databases)
        database_definition = { 'id': str(uuid.uuid4()) }
        created_db = self.client.CreateDatabase(database_definition)
        self.assertEqual(created_db['id'], database_definition['id'])
        # Read databases after creation.
        databases = list(self.client.ReadDatabases())
=======
        self.client = cosmos_client.CosmosClient(self.host, {'masterKey':self.masterKey}, "Session",
                                                 self.connectionPolicy)
    def test_database_crud(self):
        # read databases.
        databases = list(self.client.list_database_properties())
        # create a database.
        before_create_databases_count = len(databases)
        database_id = str(uuid.uuid4())
        created_db = self.client.create_database(database_id)
        self.assertEqual(created_db.id, database_id)
        # Read databases after creation.
        databases = list(self.client.list_database_properties())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(len(databases),
                         before_create_databases_count + 1,
                         'create should increase the number of databases')
        # query databases.
<<<<<<< HEAD
        databases = list(self.client.QueryDatabases({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [
                { 'name':'@id', 'value': database_definition['id'] }
=======
        databases = list(self.client.query_databases({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [
                {'name': '@id', 'value': database_id}
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
            ]
        }))
        self.assert_(databases,
                     'number of results for the query should be > 0')

        # read database.
<<<<<<< HEAD
        self.client.ReadDatabase(self.GetDatabaseLink(created_db, is_name_based))

        # delete database.
        self.client.DeleteDatabase(self.GetDatabaseLink(created_db, is_name_based))
        # read database after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           self.client.ReadDatabase,
                                           self.GetDatabaseLink(created_db, is_name_based))

    def test_sql_query_crud(self):
        # create two databases.
        db1 = self.client.CreateDatabase({ 'id': 'database 1' })
        db2 = self.client.CreateDatabase({ 'id': 'database 2' })
        # query with parameters.
        databases = list(self.client.QueryDatabases({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [
                { 'name':'@id', 'value': 'database 1' }
=======
        self.client.get_database(created_db.id)

        # delete database.
        self.client.delete_database(created_db.id)
        # read database after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           self.client.get_database,
                                           created_db.id)

    def test_database_level_offer_throughput(self):
        # Create a database with throughput
        offer_throughput = 1000
        database_id = str(uuid.uuid4())
        created_db = self.client.create_database(
            id=database_id,
            offer_throughput=offer_throughput
        )
        self.assertEqual(created_db.id, database_id)

        conftest.database_ids_to_delete.append(created_db.id)

        # Verify offer throughput for database
        offer = created_db.read_offer()
        self.assertEquals(offer.offer_throughput, offer_throughput)

        # Update database offer throughput
        new_offer_throughput = 2000
        offer = created_db.replace_throughput(new_offer_throughput)
        self.assertEquals(offer.offer_throughput, new_offer_throughput)

    def test_sql_query_crud(self):
        # create two databases.
        db1 = self.client.create_database('database 1' + str(uuid.uuid4()))
        db2 = self.client.create_database('database 2' + str(uuid.uuid4()))

        conftest.database_ids_to_delete.append(db1.id)
        conftest.database_ids_to_delete.append(db2.id)

        # query with parameters.
        databases = list(self.client.query_databases({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [
                {'name': '@id', 'value': db1.id}
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
            ]
        }))
        self.assertEqual(1, len(databases), 'Unexpected number of query results.')

        # query without parameters.
<<<<<<< HEAD
        databases = list(self.client.QueryDatabases({
=======
        databases = list(self.client.query_databases({
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
            'query': 'SELECT * FROM root r WHERE r.id="database non-existing"'
        }))
        self.assertEqual(0, len(databases), 'Unexpected number of query results.')

        # query with a string.
<<<<<<< HEAD
        databases = list(self.client.QueryDatabases('SELECT * FROM root r WHERE r.id="database 2"'))
        self.assertEqual(1, len(databases), 'Unexpected number of query results.')

        self.client.DeleteDatabase(db1['_self'])
        self.client.DeleteDatabase(db2['_self'])

    def test_collection_crud_self_link(self):
        self._test_collection_crud(False)

    def test_collection_crud_name_based(self):
        self._test_collection_crud(True)

    def _test_collection_crud(self, is_name_based):
        created_db = self.databseForTest
        collections = list(self.client.ReadContainers(self.GetDatabaseLink(created_db, is_name_based)))
        # create a collection
        before_create_collections_count = len(collections)
        collection_definition = { 'id': 'test_collection_crud ' + str(uuid.uuid4()), 'indexingPolicy': {'indexingMode': 'consistent'} }
        created_collection = self.client.CreateContainer(self.GetDatabaseLink(created_db, is_name_based),
                                                     collection_definition)
        self.assertEqual(collection_definition['id'], created_collection['id'])
        self.assertEqual('consistent', created_collection['indexingPolicy']['indexingMode'])

        # read collections after creation
        collections = list(self.client.ReadContainers(self.GetDatabaseLink(created_db, is_name_based)))
=======
        databases = list(self.client.query_databases('SELECT * FROM root r WHERE r.id="' + db2.id + '"'))
        self.assertEqual(1, len(databases), 'Unexpected number of query results.')

    def test_collection_crud(self):
        created_db = self.databaseForTest
        collections = list(created_db.list_container_properties())
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
        collections = list(created_db.list_container_properties())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(len(collections),
                         before_create_collections_count + 1,
                         'create should increase the number of collections')
        # query collections
<<<<<<< HEAD
        collections = list(self.client.QueryContainers(
            self.GetDatabaseLink(created_db, is_name_based),
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    { 'name':'@id', 'value': collection_definition['id'] }
=======
        collections = list(created_db.query_containers(
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    {'name': '@id', 'value': collection_id}
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
                ]
            }))
        # Replacing indexing policy is allowed.
        lazy_policy = {'indexingMode': 'lazy'}
<<<<<<< HEAD
        created_collection['indexingPolicy'] = lazy_policy
        replaced_collection = self.client.ReplaceContainer(self.GetDocumentCollectionLink(created_db, created_collection, is_name_based), created_collection)
        self.assertEqual('lazy', replaced_collection['indexingPolicy']['indexingMode'])
        # Replacing collection Id should fail.
        change_collection = created_collection.copy()
        change_collection['id'] = 'try_change_id'
        self.__AssertHTTPFailureWithStatus(StatusCodes.BAD_REQUEST,
                                           self.client.ReplaceContainer,
                                           self.GetDocumentCollectionLink(created_db, created_collection, is_name_based),
                                           change_collection)

        self.assertTrue(collections)
        # delete collection
        self.client.DeleteContainer(self.GetDocumentCollectionLink(created_db, created_collection, is_name_based))
        # read collection after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           self.client.ReadContainer,
                                           self.GetDocumentCollectionLink(created_db, created_collection, is_name_based))

    
    def test_partitioned_collection(self):
        created_db = self.databseForTest

        collection_definition = {   'id': 'test_partitioned_collection ' + str(uuid.uuid4()),
                                    'partitionKey': 
                                    {   
                                        'paths': ['/id'],
                                        'kind': documents.PartitionKind.Hash
                                    }
                                }

        options = { 'offerThroughput': 10100 }

        created_collection = self.client.CreateContainer(self.GetDatabaseLink(created_db),
                                collection_definition, 
                                options)
        
        self.assertEqual(collection_definition.get('id'), created_collection.get('id'))
        self.assertEqual(collection_definition.get('partitionKey').get('paths')[0], created_collection.get('partitionKey').get('paths')[0])
        self.assertEqual(collection_definition.get('partitionKey').get('kind'), created_collection.get('partitionKey').get('kind'))

        offers = self.GetCollectionOffers(self.client, created_collection['_rid'])
        
        self.assertEqual(1, len(offers))
        expected_offer = offers[0]
        self.assertEqual(expected_offer.get('content').get('offerThroughput'), options.get('offerThroughput'))

        self.client.DeleteContainer(self.GetDocumentCollectionLink(created_db, created_collection))

    def test_partitioned_collection_quota(self):
        created_db = self.databseForTest

        options = { 'offerThroughput': 20000 }

        created_collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)

        read_options = { 'populatePartitionKeyRangeStatistics': True, 'populateQuotaInfo': True}

        retrieved_collection = self.client.ReadContainer(created_collection.get('_self'), read_options)

        self.assertTrue(retrieved_collection.get("statistics") != None)
        self.assertTrue(self.client.last_response_headers.get("x-ms-resource-usage") != None)

    def test_partitioned_collection_partition_key_extraction(self):
        created_db = self.databseForTest
        
        collection_definition = {   'id': 'test_partitioned_collection_partition_key_extraction ' + str(uuid.uuid4()),
                                    'partitionKey': 
                                    {   
                                        'paths': ['/address/state'],
                                        'kind': documents.PartitionKind.Hash
                                    }
                                }

        created_collection = self.client.CreateContainer(self.GetDatabaseLink(created_db),
                                collection_definition)

        document_definition = {'id': 'document1',
                               'address' : { 'street' : '1 Microsoft Way',
                                             'city' : 'Redmond',
                                             'state' : 'WA',
                                             'zip code' : 98052
                                           }
                               }

        # create document without partition key being specified
        created_document = self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection),
            document_definition)
=======
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

        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunction
        # create document without partition key being specified
        created_document = created_collection.create_item(body=document_definition)
        retry_utility._ExecuteFunction = self.OriginalExecuteFunction
        self.assertEquals(self.last_headers[1], '["WA"]')
        del self.last_headers[:]
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        self.assertEqual(created_document.get('id'), document_definition.get('id'))
        self.assertEqual(created_document.get('address').get('state'), document_definition.get('address').get('state'))

<<<<<<< HEAD
        # create document by specifying a different partition key in options than what's in the document will result in BadRequest(status code 400)
        document_definition['id'] = 'document2'
        options = { 'partitionKey': 'NY' }

        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            self.client.CreateItem,
            self.GetDocumentCollectionLink(created_db, created_collection),
            document_definition,
            options)

        collection_definition1 = {   'id': 'test_partitioned_collection_partition_key_extraction1 ' + str(uuid.uuid4()),
                                    'partitionKey': 
                                    {   
                                        'paths': ['/address'],
                                        'kind': documents.PartitionKind.Hash
                                    }
                                }

        created_collection1 = self.client.CreateContainer(self.GetDatabaseLink(created_db),
                                collection_definition1)

        # Create document with partitionkey not present as a leaf level property but a dict
        options = {}
        created_document = self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection1),
            document_definition, options)

        self.assertEqual(options['partitionKey'], documents.Undefined)

        collection_definition2 = {   'id': 'test_partitioned_collection_partition_key_extraction2 ' + str(uuid.uuid4()),
                                    'partitionKey': 
                                    {   
                                        'paths': ['/address/state/city'],
                                        'kind': documents.PartitionKind.Hash
                                    }
                                }

        created_collection2 = self.client.CreateContainer(self.GetDatabaseLink(created_db),
                                collection_definition2)

        # Create document with partitionkey not present in the document
        options = {}
        created_document = self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection2),
            document_definition, options)

        self.assertEqual(options['partitionKey'], documents.Undefined)

        self.client.DeleteContainer(self.GetDocumentCollectionLink(created_db, created_collection))
        self.client.DeleteContainer(self.GetDocumentCollectionLink(created_db, created_collection1))
        self.client.DeleteContainer(self.GetDocumentCollectionLink(created_db, created_collection2))
        
    def test_partitioned_collection_partition_key_extraction_special_chars(self):
        created_db = self.databseForTest

        collection_definition1 = {   'id': 'test_partitioned_collection_partition_key_extraction_special_chars1 ' + str(uuid.uuid4()),
                                    'partitionKey': 
                                    {   
                                        'paths': ['/\"level\' 1*()\"/\"le/vel2\"'],
                                        'kind': documents.PartitionKind.Hash
                                    }
                                }
        
        created_collection1 = self.client.CreateContainer(self.GetDatabaseLink(created_db),
                                collection_definition1)

        document_definition = {'id': 'document1',
                               "level' 1*()" : { "le/vel2" : 'val1' }
                              }

        options = {}
        self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection1),
            document_definition, options)

        self.assertEqual(options['partitionKey'], 'val1')

        collection_definition2 = {   'id': 'test_partitioned_collection_partition_key_extraction_special_chars2 ' + str(uuid.uuid4()),
                                    'partitionKey': 
                                    {   
                                        'paths': ['/\'level\" 1*()\'/\'le/vel2\''],
                                        'kind': documents.PartitionKind.Hash
                                    }
                                }
        
        created_collection2 = self.client.CreateContainer(self.GetDatabaseLink(created_db),
                                collection_definition2)

        document_definition = {'id': 'document2',
                               'level\" 1*()' : { 'le/vel2' : 'val2' }
                              }

        options = {}
        self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection2),
            document_definition, options)

        self.assertEqual(options['partitionKey'], 'val2')

        self.client.DeleteContainer(self.GetDocumentCollectionLink(created_db, created_collection1))
        self.client.DeleteContainer(self.GetDocumentCollectionLink(created_db, created_collection2))
=======
        collection_id = 'test_partitioned_collection_partition_key_extraction1 ' + str(uuid.uuid4())
        created_collection1 = created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/address', kind=documents.PartitionKind.Hash)
        )

        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunction
        # Create document with partitionkey not present as a leaf level property but a dict
        created_document = created_collection1.create_item(document_definition)
        retry_utility._ExecuteFunction = self.OriginalExecuteFunction
        self.assertEquals(self.last_headers[1], [{}])
        del self.last_headers[:]

        #self.assertEqual(options['partitionKey'], documents.Undefined)

        collection_id = 'test_partitioned_collection_partition_key_extraction2 ' + str(uuid.uuid4())
        created_collection2 = created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/address/state/city', kind=documents.PartitionKind.Hash)
        )

        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunction
        # Create document with partitionkey not present in the document
        created_document = created_collection2.create_item(document_definition)
        retry_utility._ExecuteFunction = self.OriginalExecuteFunction
        self.assertEquals(self.last_headers[1], [{}])
        del self.last_headers[:]

        #self.assertEqual(options['partitionKey'], documents.Undefined)

        created_db.delete_container(created_collection.id)
        created_db.delete_container(created_collection1.id)
        created_db.delete_container(created_collection2.id)

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

        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunction
        created_document = created_collection1.create_item(body=document_definition)
        retry_utility._ExecuteFunction = self.OriginalExecuteFunction
        self.assertEquals(self.last_headers[1], '["val1"]')
        del self.last_headers[:]

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

        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunction
        # create document without partition key being specified
        created_document = created_collection2.create_item(body=document_definition)
        retry_utility._ExecuteFunction = self.OriginalExecuteFunction
        self.assertEquals(self.last_headers[1], '["val2"]')
        del self.last_headers[:]

        created_db.delete_container(created_collection1.id)
        created_db.delete_container(created_collection2.id)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

    def test_partitioned_collection_path_parser(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(test_dir, "BaselineTest.PathParser.json")) as json_file:
            entries = json.loads(json_file.read())
        for entry in entries:
            parts = base.ParsePaths([entry['path']])
            self.assertEqual(parts, entry['parts'])

        paths = ["/\"Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1\"/*"]
<<<<<<< HEAD
        parts = [ "Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1", "*" ]
        self.assertEqual(parts, base.ParsePaths(paths))

        paths = ["/'Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1'/*"]
        parts = [ "Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1", "*" ]
        self.assertEqual(parts, base.ParsePaths(paths))

    def test_partitioned_collection_document_crud_and_query(self):
        created_db = self.databseForTest
        
=======
        parts = ["Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1", "*"]
        self.assertEqual(parts, base.ParsePaths(paths))

        paths = ["/'Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1'/*"]
        parts = ["Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1", "*"]
        self.assertEqual(parts, base.ParsePaths(paths))

    def test_partitioned_collection_document_crud_and_query(self):
        created_db = self.databaseForTest

>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        created_collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)

        document_definition = {'id': 'document',
                               'key': 'value'}

<<<<<<< HEAD
        created_document = self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection),
            document_definition)
=======
        created_document = created_collection.create_item(
            body=document_definition
        )
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        self.assertEqual(created_document.get('id'), document_definition.get('id'))
        self.assertEqual(created_document.get('key'), document_definition.get('key'))

<<<<<<< HEAD
        # For ReadDocument, we require to have the partitionKey to be specified as part of options otherwise we get BadRequest(status code 400)
        #self.__AssertHTTPFailureWithStatus(
        #    StatusCodes.BAD_REQUEST,
        #    client.ReadItem,
        #    self.GetDocumentLink(created_db, created_collection, created_document))

        # read document
        options = { 'partitionKey': document_definition.get('id') }
        read_document = self.client.ReadItem(
            self.GetDocumentLink(created_db, created_collection, created_document), 
            options)
=======
        # read document
        read_document = created_collection.get_item(
            item=created_document.get('id'),
            partition_key=created_document.get('id')
        )
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        self.assertEqual(read_document.get('id'), created_document.get('id'))
        self.assertEqual(read_document.get('key'), created_document.get('key'))

        # Read document feed doesn't require partitionKey as it's always a cross partition query
<<<<<<< HEAD
        documentlist = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, created_collection)))
=======
        documentlist = list(created_collection.list_item_properties())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(1, len(documentlist))

        # replace document
        document_definition['key'] = 'new value'

<<<<<<< HEAD
        replaced_document = self.client.ReplaceItem(
            self.GetDocumentLink(created_db, created_collection, created_document),
            document_definition)
=======
        replaced_document = created_collection.replace_item(
            item=read_document,
            body=document_definition
        )
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        self.assertEqual(replaced_document.get('key'), document_definition.get('key'))

        # upsert document(create scenario)
        document_definition['id'] = 'document2'
        document_definition['key'] = 'value2'

<<<<<<< HEAD
        upserted_document = self.client.UpsertItem(self.GetDocumentCollectionLink(created_db, created_collection),
            document_definition)
=======
        upserted_document = created_collection.upsert_item(body=document_definition)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        self.assertEqual(upserted_document.get('id'), document_definition.get('id'))
        self.assertEqual(upserted_document.get('key'), document_definition.get('key'))

<<<<<<< HEAD
        documentlist = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, created_collection)))
        self.assertEqual(2, len(documentlist))

        # For DeleteDocument, we require to have the partitionKey to be specified as part of options otherwise we get BadRequest(status code 400)
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            self.client.DeleteItem,
            self.GetDocumentLink(created_db, created_collection, upserted_document))

        # delete document
        options = { 'partitionKey': upserted_document.get('id') }
        self.client.DeleteItem(
            self.GetDocumentLink(created_db, created_collection, upserted_document), 
            options)

        # query document on the partition key specified in the predicate will pass even without setting enableCrossPartitionQuery or passing in the partitionKey value
        documentlist = list(self.client.QueryItems(
            self.GetDocumentCollectionLink(created_db, created_collection),
=======
        documentlist = list(created_collection.list_item_properties())
        self.assertEqual(2, len(documentlist))

        # delete document
        created_collection.delete_item(item=upserted_document, partition_key=upserted_document.get('id'))

        # query document on the partition key specified in the predicate will pass even without setting enableCrossPartitionQuery or passing in the partitionKey value
        documentlist = list(created_collection.query_items(
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
            {
                'query': 'SELECT * FROM root r WHERE r.id=\'' + replaced_document.get('id') + '\''
            }))
        self.assertEqual(1, len(documentlist))

        # query document on any property other than partitionKey will fail without setting enableCrossPartitionQuery or passing in the partitionKey value
        try:
<<<<<<< HEAD
            list(self.client.QueryItems(
                self.GetDocumentCollectionLink(created_db, created_collection),
=======
            list(created_collection.query_items(
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
                {
                    'query': 'SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\''
                }))
        except Exception:
            pass

        # cross partition query
<<<<<<< HEAD
        options = { 'enableCrossPartitionQuery': True }
        documentlist = list(self.client.QueryItems(
            self.GetDocumentCollectionLink(created_db, created_collection),
            {
                'query': 'SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\''
            }, options))
=======
        documentlist = list(created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',
            enable_cross_partition_query=True
        ))
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        self.assertEqual(1, len(documentlist))

        # query document by providing the partitionKey value
<<<<<<< HEAD
        options = { 'partitionKey': replaced_document.get('id') }
        documentlist = list(self.client.QueryItems(
            self.GetDocumentCollectionLink(created_db, created_collection),
            {
                'query': 'SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\''
            }, options))
=======
        documentlist = list(created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',
            partition_key=replaced_document.get('id')
        ))
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        self.assertEqual(1, len(documentlist))

    def test_partitioned_collection_permissions(self):
<<<<<<< HEAD
        created_db = self.databseForTest

        collection_definition = {   'id': 'sample collection ' + str(uuid.uuid4()),
                                    'partitionKey': 
                                    {   
                                        'paths': ['/key'],
                                        'kind': documents.PartitionKind.Hash
                                    }
                                }

        collection_definition['id'] = 'test_partitioned_collection_permissions all collection'
        
        all_collection = self.client.CreateContainer(self.GetDatabaseLink(created_db),
                                collection_definition)

        collection_definition['id'] = 'test_partitioned_collection_permissions read collection'

        read_collection = self.client.CreateContainer(self.GetDatabaseLink(created_db),
                                collection_definition)

        user = self.client.CreateUser(self.GetDatabaseLink(created_db), { 'id': 'user' })
=======
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

        user = created_db.create_user(body={'id': 'user'})
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        permission_definition = {
            'id': 'all permission',
            'permissionMode': documents.PermissionMode.All,
<<<<<<< HEAD
            'resource': self.GetDocumentCollectionLink(created_db, all_collection),
            'resourcePartitionKey' : [1]
        }

        all_permission = self.client.CreatePermission(self.GetUserLink(created_db, user), permission_definition)
=======
            'resource': all_collection.container_link,
            'resourcePartitionKey': [1]
        }

        all_permission = user.create_permission(body=permission_definition)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        permission_definition = {
            'id': 'read permission',
            'permissionMode': documents.PermissionMode.Read,
<<<<<<< HEAD
            'resource': self.GetDocumentCollectionLink(created_db, read_collection),
            'resourcePartitionKey' : [1]
        }

        read_permission = self.client.CreatePermission(self.GetUserLink(created_db, user), permission_definition)

        resource_tokens = {}
        # storing the resource tokens based on Resource IDs
        resource_tokens[all_collection['_rid']] = (all_permission['_token'])
        resource_tokens[read_collection['_rid']] = (read_permission['_token'])
        
        restricted_client = cosmos_client.CosmosClient(
            CRUDTests.host, {'resourceTokens': resource_tokens}, CRUDTests.connectionPolicy)
=======
            'resource': read_collection.container_link,
            'resourcePartitionKey': [1]
        }

        read_permission = user.create_permission(body=permission_definition)

        resource_tokens = {}
        # storing the resource tokens based on Resource IDs
        resource_tokens[urllib.quote(all_collection.id)] = (all_permission.properties['_token'])
        resource_tokens[urllib.quote(read_collection.id)] = (read_permission.properties['_token'])

        restricted_client = cosmos_client.CosmosClient(
            CRUDTests.host, {'resourceTokens': resource_tokens}, "Session", CRUDTests.connectionPolicy)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        document_definition = {'id': 'document1',
                               'key': 1
                               }
<<<<<<< HEAD
        
        # Create document in all_collection should succeed since the partitionKey is 1 which is what specified as resourcePartitionKey in permission object and it has all permissions
        created_document = restricted_client.CreateItem(
            self.GetDocumentCollectionLink(created_db, all_collection, False),
            document_definition)
=======

        all_collection.client_connection = restricted_client.client_connection
        read_collection.client_connection = restricted_client.client_connection

        # Create document in all_collection should succeed since the partitionKey is 1 which is what specified as resourcePartitionKey in permission object and it has all permissions
        created_document = all_collection.create_item(body=document_definition)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        # Create document in read_collection should fail since it has only read permissions for this collection
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.FORBIDDEN,
<<<<<<< HEAD
            restricted_client.CreateItem,
            self.GetDocumentCollectionLink(created_db, read_collection, False),
            document_definition)

        # Read document feed should succeed for this collection. Note that I need to pass in partitionKey here since permission has resourcePartitionKey defined
        options = { 'partitionKey': document_definition.get('key') }
        documentlist = list(restricted_client.ReadItems(
            self.GetDocumentCollectionLink(created_db, read_collection, False),
            options))

        self.assertEqual(0, len(documentlist))

        document_definition['key'] = 2
        options = { 'partitionKey': document_definition.get('key') }
        # Create document should fail since the partitionKey is 2 which is different that what is specified as resourcePartitionKey in permission object
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.FORBIDDEN,
            restricted_client.CreateItem,
            self.GetDocumentCollectionLink(created_db, all_collection, False),
            document_definition,
            options)
        
        document_definition['key'] = 1
        options = { 'partitionKey': document_definition.get('key') }
        # Delete document should succeed since the partitionKey is 1 which is what specified as resourcePartitionKey in permission object
        created_document = restricted_client.DeleteItem(
            self.GetDocumentLink(created_db, all_collection, created_document, False),
            options)
=======
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
        created_document = all_collection.delete_item(item=created_document['id'], partition_key=document_definition['key'])
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        # Delete document in read_collection should fail since it has only read permissions for this collection
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.FORBIDDEN,
<<<<<<< HEAD
            restricted_client.DeleteItem,
            self.GetDocumentCollectionLink(created_db, read_collection, False),
            options)

        self.client.DeleteContainer(self.GetDocumentCollectionLink(created_db, all_collection))
        self.client.DeleteContainer(self.GetDocumentCollectionLink(created_db, read_collection))

    def test_partitioned_collection_execute_stored_procedure(self):
        created_db = self.databseForTest
=======
            read_collection.delete_item,
            document_definition['id'],
            document_definition['id']
        )

        created_db.delete_container(all_collection)
        created_db.delete_container(read_collection)

    def test_partitioned_collection_execute_stored_procedure(self):
        created_db = self.databaseForTest
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        created_collection = self.configs.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)

        sproc = {
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': (
                'function () {' +
                '   var client = getContext().getCollection();' +
                '   client.createDocument(client.getSelfLink(), { id: \'testDoc\', pk : 2}, {}, function(err, docCreated, options) { ' +
                '   if(err) throw new Error(\'Error while creating document: \' + err.message);' +
                '   else {' +
<<<<<<< HEAD
                         '   getContext().getResponse().setBody(1);' +
=======
                '   getContext().getResponse().setBody(1);' +
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
                '        }' +
                '   });}')
        }

<<<<<<< HEAD
        created_sproc = self.client.CreateStoredProcedure(self.GetDocumentCollectionLink(created_db, created_collection), sproc)

        # Partiton Key value same as what is specified in the stored procedure body
        self.client.ExecuteStoredProcedure(self.GetStoredProcedureLink(created_db, created_collection, created_sproc),
                                               None, { 'partitionKey' : 2})
=======
        created_sproc = created_collection.scripts.create_stored_procedure(body=sproc)

        # Partiton Key value same as what is specified in the stored procedure body
        result = created_collection.scripts.execute_stored_procedure(sproc=created_sproc['id'], partition_key=2)
        self.assertEqual(result, 1)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        # Partiton Key value different than what is specified in the stored procedure body will cause a bad request(400) error
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
<<<<<<< HEAD
            self.client.ExecuteStoredProcedure,
            self.GetStoredProcedureLink(created_db, created_collection, created_sproc),
            None,
            { 'partitionKey' : 3})

    def test_partitioned_collection_attachment_crud_and_query(self):
        class ReadableStream(object):
            """Customized file-like stream.
            """

            def __init__(self, chunks = ['first chunk ', 'second chunk']):
                """Initialization.

                :Parameters:
                    - `chunks`: list

                """
                if six.PY2:
                    self._chunks = list(chunks)
                else:
                    # python3: convert to bytes
                    self._chunks = [chunk.encode() for chunk in chunks]

            def read(self, n=-1):
                """Simulates the read method in a file stream.

                :Parameters:
                    - `n`: int

                :Returns:
                    bytes or str

                """
                if self._chunks:
                    return self._chunks.pop(0)
                else:
                    return ''

            def __len__(self):
                """To make len(ReadableStream) work.
                """
                return sum([len(chunk) for chunk in self._chunks])

        db = self.databseForTest
        collection_definition = {'id': 'test_partitioned_collection_attachment_crud_and_query ' + str(uuid.uuid4()),
                                 'partitionKey': {'paths': ['/id'],'kind': 'Hash'}}

        collection = self.client.CreateContainer(db['_self'], collection_definition)
        
        document_definition = {'id': 'sample document' + str(uuid.uuid4()),
                               'key': 'value'}

        document = self.client.CreateItem(self.GetDocumentCollectionLink(db, collection),
                                         document_definition)

        content_stream = ReadableStream()
        options = { 'slug': 'sample attachment',
                    'contentType': 'application/text' }

        # Currently, we require to have the partitionKey to be specified as part of options otherwise we get BadRequest(status code 400)
        #self.__AssertHTTPFailureWithStatus(
        #    StatusCodes.BAD_REQUEST,
        #    client.CreateAttachmentAndUploadMedia,
        #    self.GetDocumentLink(db, collection, document),
        #    content_stream,
        #    options)

        content_stream = ReadableStream()
        # Setting the partitionKey as part of options is required for attachment CRUD
        options = { 'slug': 'sample attachment' + str(uuid.uuid4()),
                    'contentType': 'application/text',
                    'partitionKey' :  document_definition.get('id') }
        
        # create attachment and upload media
        attachment = self.client.CreateAttachmentAndUploadMedia(
            self.GetDocumentLink(db, collection, document), content_stream, options)

        self.assertEqual(attachment['id'], options['slug'])

        # Currently, we require to have the partitionKey to be specified as part of options otherwise we get BadRequest(status code 400)
        try:
            list(self.client.ReadAttachments(
            self.GetDocumentLink(db, collection, document)))
        except Exception:
            pass

        # Read attachment feed requires partitionKey to be passed
        options = { 'partitionKey': document_definition.get('id') }
        attachmentlist = list(self.client.ReadAttachments(
            self.GetDocumentLink(db, collection, document), options))
        self.assertEqual(1, len(attachmentlist))

        content_stream = ReadableStream()
        options = { 'slug': 'new attachment' + str(uuid.uuid4()),
                    'contentType': 'application/text' }
        # Currently, we require to have the partitionKey to be specified as part of options otherwise we get BadRequest(status code 400)
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            self.client.UpsertAttachmentAndUploadMedia,
            self.GetDocumentLink(db, collection, document),
            content_stream,
            options)

        content_stream = ReadableStream()
        # Setting the partitionKey as part of options is required for attachment CRUD
        options = { 'slug': 'new attachment' + str(uuid.uuid4()),
                    'contentType': 'application/text',
                    'partitionKey' :  document_definition.get('id') }
        
        # upsert attachment and upload media
        attachment = self.client.UpsertAttachmentAndUploadMedia(
            self.GetDocumentLink(db, collection, document), content_stream, options)

        self.assertEqual(attachment['id'], options['slug'])

        options = { 'partitionKey': document_definition.get('id') }
        attachmentlist = list(self.client.ReadAttachments(
            self.GetDocumentLink(db, collection, document), options))
        self.assertEqual(2, len(attachmentlist))

        # create attachment with media link
        dynamic_attachment = {
            'id': 'dynamic attachment' + str(uuid.uuid4()),
            'media': 'http://xstore.',
            'MediaType': 'Book',
            'Author':'My Book Author',
            'Title':'My Book Title',
            'contentType':'application/text'
        }

        # Currently, we require to have the partitionKey to be specified as part of options otherwise we get BadRequest(status code 400)
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            self.client.CreateAttachment,
            self.GetDocumentLink(db, collection, document),
            dynamic_attachment)

        # create dynamic attachment
        options = { 'partitionKey': document_definition.get('id') }
        attachment = self.client.CreateAttachment(self.GetDocumentLink(db, collection, document),
                                             dynamic_attachment, options)

        self.assertEqual(attachment['MediaType'], dynamic_attachment['MediaType'])
        self.assertEqual(attachment['Author'], dynamic_attachment['Author'])

        # Read Attachment feed
        options = { 'partitionKey': document_definition.get('id') }
        attachmentlist = list(self.client.ReadAttachments(
            self.GetDocumentLink(db, collection, document), options))
        self.assertEqual(3, len(attachmentlist))
        
        # Currently, we require to have the partitionKey to be specified as part of options otherwise we get BadRequest(status code 400)
        #self.__AssertHTTPFailureWithStatus(
        #    StatusCodes.BAD_REQUEST,
        #    client.ReadAttachment,
        #    self.GetAttachmentLink(db, collection, document, attachment))

        # Read attachment
        options = { 'partitionKey': document_definition.get('id') }
        read_attachment = self.client.ReadAttachment(self.GetAttachmentLink(db, collection, document, attachment),
                                                options)

        self.assertEqual(attachment['id'], read_attachment['id'])

        attachment['Author'] = 'new author'
        
        # Currently, we require to have the partitionKey to be specified as part of options otherwise we get BadRequest(status code 400)
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            self.client.ReplaceAttachment,
            self.GetAttachmentLink(db, collection, document, attachment),
            attachment)

        # replace the attachment
        options = { 'partitionKey': document_definition.get('id') }
        replaced_attachment = self.client.ReplaceAttachment(self.GetAttachmentLink(db, collection, document, attachment), attachment, options)
        
        self.assertEqual(attachment['id'], replaced_attachment['id'])
        self.assertEqual(attachment['Author'], replaced_attachment['Author'])

        attachment['id'] = 'new dynamic attachment' + str(uuid.uuid4())
        attachment['Title'] = 'new title'

        # Currently, we require to have the partitionKey to be specified as part of options otherwise we get BadRequest(status code 400)
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            self.client.UpsertAttachment,
            self.GetDocumentLink(db, collection, document),
            attachment)

        # upsert attachment(create scenario)
        options = { 'partitionKey': document_definition.get('id') }
        upserted_attachment = self.client.UpsertAttachment(self.GetDocumentLink(db, collection, document), attachment, options)
        
        self.assertEqual(attachment['id'], upserted_attachment['id'])
        self.assertEqual(attachment['Title'], upserted_attachment['Title'])

        # query attachments will fail without passing in the partitionKey value
        try:
            list(self.client.QueryAttachments(
                self.GetDocumentLink(db, collection, document),
                {
                    'query': 'SELECT * FROM root r WHERE r.MediaType=\'' + dynamic_attachment.get('MediaType') + '\''
                }))
        except Exception:
            pass

        # query attachments by providing the partitionKey value
        options = { 'partitionKey': document_definition.get('id') }
        attachmentlist = list(self.client.QueryAttachments(
            self.GetDocumentLink(db, collection, document),
            {
                'query': 'SELECT * FROM root r WHERE r.MediaType=\'' + dynamic_attachment.get('MediaType') + '\''
            }, options))

        self.assertEqual(2, len(attachmentlist))

        # Currently, we require to have the partitionKey to be specified as part of options otherwise we get BadRequest(status code 400)
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            self.client.DeleteAttachment,
            self.GetAttachmentLink(db, collection, document, attachment))

        # deleting attachment
        options = { 'partitionKey': document_definition.get('id') }
        self.client.DeleteAttachment(self.GetAttachmentLink(db, collection, document, attachment), options)
        self.client.DeleteContainer(collection['_self'])

    def test_partitioned_collection_partition_key_value_types(self):
        created_db = self.databseForTest

        created_collection = self.configs.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk' : None,
                               'spam': 'eggs'}

        # create document with partitionKey set as None here
        self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection),
            document_definition)
=======
            created_collection.scripts.execute_stored_procedure,
            created_sproc['id'],
            3)

    def test_partitioned_collection_partition_key_value_types(self):
        created_db = self.databaseForTest

        created_collection = created_db.create_container(
            id='test_partitioned_collection_partition_key_value_types ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/pk', kind='Hash')
        )

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': None,
                               'spam': 'eggs'}

        # create document with partitionKey set as None here
        created_collection.create_item(body=document_definition)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'spam': 'eggs'}

        # create document with partitionKey set as Undefined here
<<<<<<< HEAD
        self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection),
            document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk' : True,
                               'spam': 'eggs'}

        # create document with bool partitionKey
        self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection),
            document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk' : 'value',
                               'spam': 'eggs'}

        # create document with string partitionKey
        self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection),
            document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk' : 100,
                               'spam': 'eggs'}

        # create document with int partitionKey
        self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection),
            document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk' : 10.50,
                               'spam': 'eggs'}

        # create document with float partitionKey
        self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection),
            document_definition)

    def test_partitioned_collection_conflict_crud_and_query(self):
        created_db = self.databseForTest
=======
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

        created_db.delete_container(created_collection)

    def test_partitioned_collection_conflict_crud_and_query(self):
        created_db = self.databaseForTest
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        created_collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)

        conflict_definition = {'id': 'new conflict',
<<<<<<< HEAD
                               'resourceId' : 'doc1',
                               'operationType' : 'create',
                               'resourceType' : 'document'
                              }

        # Currently, we require to have the partitionKey to be specified as part of options otherwise we get BadRequest(status code 400)
        #self.__AssertHTTPFailureWithStatus(
        #    StatusCodes.BAD_REQUEST,
        #    client.ReadConflict,
        #    self.GetConflictLink(created_db, created_collection, conflict_definition))

        # read conflict here will return resource not found(404) since there is no conflict here
        options = { 'partitionKey': conflict_definition.get('id') }
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
        options = { 'partitionKey': conflict_definition.get('id') }
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
                    'query': 'SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\''
                }))
        except Exception:
            pass

        # cross partition query
        options = { 'enableCrossPartitionQuery': True }
        conflictlist = list(self.client.QueryConflicts(
            self.GetDocumentCollectionLink(created_db, created_collection),
            {
                'query': 'SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\''
            }, options))
        
        self.assertEqual(0, len(conflictlist))

        # query conflicts by providing the partitionKey value
        options = { 'partitionKey': conflict_definition.get('id') }
        conflictlist = list(self.client.QueryConflicts(
            self.GetDocumentCollectionLink(created_db, created_collection),
            {
                'query': 'SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\''
            }, options))

        self.assertEqual(0, len(conflictlist))

    def test_document_crud_self_link(self):
        self._test_document_crud(False)

    def test_document_crud_name_based(self):
        self._test_document_crud(True)
        
    def _test_document_crud(self, is_name_based):
        # create database
        created_db = self.databseForTest
        # create collection
        created_collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
        # read documents
        documents = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based)))

        # create a document
        before_create_documents_count = len(documents)
        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value'}
        # Should throw an error because automatic id generation is disabled.
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            self.client.CreateItem,
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based),
            document_definition,
            {'disableAutomaticIdGeneration': True})

        created_document = self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based),
            document_definition)
        self.assertEqual(created_document['name'],
                         document_definition['name'])
        self.assertTrue(created_document['id'] != None)
        # duplicated documents are allowed when 'id' is not provided.
        duplicated_document = self.client.CreateItem(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based),
            document_definition)
        self.assertEqual(duplicated_document['name'],
                         document_definition['name'])
        self.assert_(duplicated_document['id'])
        self.assertNotEqual(duplicated_document['id'],
                            created_document['id'])
        # duplicated documents are not allowed when 'id' is provided.
        duplicated_definition_with_id = document_definition.copy()
        duplicated_definition_with_id['id'] = created_document['id']
        self.__AssertHTTPFailureWithStatus(StatusCodes.CONFLICT,
                                           self.client.CreateItem,
                                           self.GetDocumentCollectionLink(created_db, created_collection, is_name_based),
                                           duplicated_definition_with_id)
        # read documents after creation
        documents = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based)))
        self.assertEqual(
            len(documents),
            before_create_documents_count + 2,
            'create should increase the number of documents')
        # query documents
        documents = list(self.client.QueryItems(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based),
            {
                'query': 'SELECT * FROM root r WHERE r.name=@name',
                'parameters': [
                    { 'name':'@name', 'value':document_definition['name'] }
                ]
            }))
        self.assert_(documents)
        documents = list(self.client.QueryItems(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based),
            {
                'query': 'SELECT * FROM root r WHERE r.name=@name',
                'parameters': [
                    { 'name':'@name', 'value':document_definition['name'] }
                ]
            },
            { 'enableScanInQuery': True}))
        self.assert_(documents)
=======
                               'resourceId': 'doc1',
                               'operationType': 'create',
                               'resourceType': 'document'
                               }

        # read conflict here will return resource not found(404) since there is no conflict here
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.NOT_FOUND,
            created_collection.get_conflict,
            conflict_definition['id'],
            conflict_definition['id']
        )

        # Read conflict feed doesn't requires partitionKey to be specified as it's a cross partition thing
        conflictlist = list(created_collection.list_conflicts())
        self.assertEqual(0, len(conflictlist))

        # delete conflict here will return resource not found(404) since there is no conflict here
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.NOT_FOUND,
            created_collection.delete_conflict,
            conflict_definition['id'],
            conflict_definition['id']
        )

        # query conflicts on any property other than partitionKey will fail without setting enableCrossPartitionQuery or passing in the partitionKey value
        try:
            list(created_collection.query_conflicts(
                    query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get(
                        'resourceType') + '\''
                ))
        except Exception:
            pass

        conflictlist = list(created_collection.query_conflicts(
                query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'',
                enable_cross_partition_query=True
        ))

        self.assertEqual(0, len(conflictlist))

        # query conflicts by providing the partitionKey value
        options = {'partitionKey': conflict_definition.get('id')}
        conflictlist = list(created_collection.query_conflicts(
            query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'',
            partition_key=conflict_definition['id']
        ))

        self.assertEqual(0, len(conflictlist))

    def test_document_crud(self):
        # create database
        created_db = self.databaseForTest
        # create collection
        created_collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)
        # read documents
        documents = list(created_collection.list_item_properties())
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
        documents = list(created_collection.list_item_properties())
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
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        # replace document.
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'
        old_etag = created_document['_etag']
<<<<<<< HEAD
        replaced_document = self.client.ReplaceItem(
            self.GetDocumentLink(created_db, created_collection, created_document, is_name_based),
            created_document)
=======
        replaced_document = created_collection.replace_item(
            item=created_document['id'],
            body=created_document
        )
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(replaced_document['name'],
                         'replaced document',
                         'document id property should change')
        self.assertEqual(replaced_document['spam'],
                         'not eggs',
                         'property should have changed')
        self.assertEqual(created_document['id'],
                         replaced_document['id'],
                         'document id should stay the same')
<<<<<<< HEAD
        
        #replace document based on condition
        replaced_document['name'] = 'replaced document based on condition'
        replaced_document['spam'] = 'new spam field'

        #should fail for stale etag
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.PRECONDITION_FAILED, self.client.ReplaceItem,
                self.GetDocumentLink(created_db, created_collection, replaced_document, is_name_based),
                replaced_document, { 'accessCondition' : { 'type': 'IfMatch', 'condition': old_etag } })

        #should pass for most recent etag
        replaced_document_conditional = self.client.ReplaceItem(
            self.GetDocumentLink(created_db, created_collection, replaced_document, is_name_based),
            replaced_document, { 'accessCondition' : { 'type': 'IfMatch', 'condition': replaced_document['_etag'] } })
=======

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
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
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
<<<<<<< HEAD
        one_document_from_read = self.client.ReadItem(
            self.GetDocumentLink(created_db, created_collection, replaced_document, is_name_based))
        self.assertEqual(replaced_document['id'],
                         one_document_from_read['id'])
        # delete document
        self.client.DeleteItem(self.GetDocumentLink(created_db, created_collection, replaced_document, is_name_based))
        # read documents after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           self.client.ReadItem,
                                           self.GetDocumentLink(created_db, created_collection, replaced_document, is_name_based))

    def test_partitioning(self):
        # create test database
        created_db = self.databseForTest
        
        # Create bunch of collections participating in partitioning
        collection0 = self.client.CreateContainer(
            self.GetDatabaseLink(created_db, True),
            { 'id': 'test_partitioning coll_0' + str(uuid.uuid4()) })
        collection1 = self.client.CreateContainer(
            self.GetDatabaseLink(created_db, True),
            { 'id': 'test_partitioning coll_1' + str(uuid.uuid4())})
        collection2 = self.client.CreateContainer(
            self.GetDatabaseLink(created_db, True),
            { 'id': 'test_partitioning coll_2' + str(uuid.uuid4())})

        # Register the collection links for partitioning through partition resolver
        collection_links = [self.GetDocumentCollectionLink(created_db, collection0, True), self.GetDocumentCollectionLink(created_db, collection1, True), self.GetDocumentCollectionLink(created_db, collection2, True)]
        partition_resolver = test_partition_resolver.TestPartitionResolver(collection_links)
        self.client.RegisterPartitionResolver(self.GetDatabaseLink(created_db, True), partition_resolver)

        # create a document using the document definition
        document_definition = { 'id': '0',
                                'name': 'sample document',
                                'key': 'value' }
        
        self.client.CreateItem(
            self.GetDatabaseLink(created_db, True),
            document_definition)

        # Read the documents in collection1 and verify that the count is 1 now
        documents = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, collection0, True)))
        self.assertEqual(1, len(documents))
        
        # Verify that it contains the document with Id 0
        self.assertEqual('0', documents[0]['id'])

        document_definition['id'] = '1'

        self.client.CreateItem(
            self.GetDatabaseLink(created_db, True),
            document_definition)

        # Read the documents in collection1 and verify that the count is 1 now
        documents = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, collection1, True)))
        self.assertEqual(1, len(documents))

        # Verify that it contains the document with Id 1
        self.assertEqual('1', documents[0]['id'])

        document_definition['id'] = '2'

        self.client.CreateItem(
            self.GetDatabaseLink(created_db, True),
            document_definition)

        # Read the documents in collection2 and verify that the count is 1 now
        documents = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, collection2, True)))
        self.assertEqual(1, len(documents))

        # Verify that it contains the document with Id 2
        self.assertEqual('2', documents[0]['id'])

        # Updating the value of "key" property to test UpsertDocument(replace scenario)
        document_definition['id'] = '0'
        document_definition['key'] = 'new value'

        self.client.UpsertItem(
            self.GetDatabaseLink(created_db, True),
            document_definition)

        # Read the documents in collection0 and verify that the count is still 1
        documents = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, collection0, True)))
        self.assertEqual(1, len(documents))

        # Verify that it contains the document with new key value
        self.assertEqual(document_definition['key'], documents[0]['key'])

        # Query documents in all collections(since no partition key specified) using query string
        documents = list(self.client.QueryItems(
            self.GetDatabaseLink(created_db, True),
            {
                'query': 'SELECT * FROM root r WHERE r.id=\'2\''
            }))
        self.assertEqual(1, len(documents))

        # Updating the value of id property to test UpsertDocument(create scenario)
        document_definition['id'] = '4'

        self.client.UpsertItem(
            self.GetDatabaseLink(created_db, True),
            document_definition)

        # Read the documents in collection1 and verify that the count is 2 now
        documents = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, collection1, True)))
        self.assertEqual(2, len(documents))

        # Query documents in all collections(since no partition key specified) using query spec
        documents = list(self.client.QueryItems(
            self.GetDatabaseLink(created_db, True),
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    { 'name':'@id', 'value':document_definition['id'] }
                ]
            }))
        self.assertEqual(1, len(documents))

        # Query documents in collection(with partition key of '4' specified) which resolves to collection1
        documents = list(self.client.QueryItems(
            self.GetDatabaseLink(created_db, True),
            {
                'query': 'SELECT * FROM root r'
            }, {}, document_definition['id']))
        self.assertEqual(2, len(documents))

        # Query documents in collection(with partition key '5' specified) which resolves to collection2 but non existent document in that collection
        documents = list(self.client.QueryItems(
            self.GetDatabaseLink(created_db, True),
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    { 'name':'@id', 'value':document_definition['id'] }
                ]
            }, {}, '5'))
        self.assertEqual(0, len(documents))

        self.client.DeleteContainer(collection0['_self'])
        self.client.DeleteContainer(collection1['_self'])
        self.client.DeleteContainer(collection2['_self'])
    
    # Partitioning test(with paging)
    def test_partition_paging(self):
        # create test database
        created_db = self.databseForTest
        
        # Create bunch of collections participating in partitioning
        collection0 = self.client.CreateContainer(
            self.GetDatabaseLink(created_db, True),
            { 'id': 'test_partition_paging coll_0 ' + str(uuid.uuid4()) })
        collection1 = self.client.CreateContainer(
            self.GetDatabaseLink(created_db, True),
            { 'id': 'test_partition_paging coll_1 ' + str(uuid.uuid4()) })
        
        # Register the collection links for partitioning through partition resolver
        collection_links = [self.GetDocumentCollectionLink(created_db, collection0, True), self.GetDocumentCollectionLink(created_db, collection1, True)]
        partition_resolver = test_partition_resolver.TestPartitionResolver(collection_links)
        self.client.RegisterPartitionResolver(self.GetDatabaseLink(created_db, True), partition_resolver)
        
        # Create document definition used to create documents
        document_definition = { 'id': '0',
                                'name': 'sample document',
                                'key': 'value' }
        
        # Create 10 documents each with a different id starting from 0 to 9
        for i in xrange(0, 10):
            document_definition['id'] = str(i)
            self.client.CreateItem(
                self.GetDatabaseLink(created_db, True),
                document_definition)

        # Query the documents to ensure that you get the correct count(no paging)
        documents = list(self.client.QueryItems(
            self.GetDatabaseLink(created_db, True),
            {
                'query': 'SELECT * FROM root r WHERE r.id < \'7\''
            }))
        self.assertEqual(7, len(documents))

        # Query the documents with maxItemCount to restrict the max number of documents returned
        queryIterable = self.client.QueryItems(
            self.GetDatabaseLink(created_db, True),
            {
                'query': 'SELECT * FROM root r WHERE r.id < \'7\''
            }, {'maxItemCount':3})

        # Query again and count the number of documents(with paging)
        docCount = 0
        for _ in queryIterable:
            docCount += 1

        self.assertEqual(7, docCount)

        # Query again to test fetch_next_block to ensure that it returns the correct number of documents everytime it's called
        queryIterable = self.client.QueryItems(
            self.GetDatabaseLink(created_db, True),
            {
                'query': 'SELECT * FROM root r WHERE r.id < \'7\''
            }, {'maxItemCount':3})

        # Documents with id 0, 2, 4(in collection0)
        self.assertEqual(3, len(queryIterable.fetch_next_block()))

        # Documents with id 6(in collection0)
        self.assertEqual(1, len(queryIterable.fetch_next_block()))

        # Documents with id 1, 3, 5(in collection1)
        self.assertEqual(3, len(queryIterable.fetch_next_block()))

        # No more documents
        self.assertEqual(0, len(queryIterable.fetch_next_block()))

        # Set maxItemCount to -1 to lift the limit on max documents returned by the query
        queryIterable = self.client.QueryItems(
            self.GetDatabaseLink(created_db, True),
            {
                'query': 'SELECT * FROM root r WHERE r.id < \'7\''
            }, {'maxItemCount':-1})

        # Documents with id 0, 2, 4, 6(all docs in collection0 adhering to query condition)
        self.assertEqual(4, len(queryIterable.fetch_next_block()))

        # Documents with id 1, 3, 5(all docs in collection1 adhering to query condition)
        self.assertEqual(3, len(queryIterable.fetch_next_block()))

        # No more documents
        self.assertEqual(0, len(queryIterable.fetch_next_block()))

        self.client.DeleteContainer(collection0['_self'])
        self.client.DeleteContainer(collection1['_self'])
        
    def test_hash_partition_resolver(self):
        created_db = self.databseForTest
        
        # Create bunch of collections participating in partitioning
        collection0 = { 'id': 'coll_0 ' + str(uuid.uuid4()) }
        collection1 = { 'id': 'coll_1 ' + str(uuid.uuid4()) }

        collection_links = [self.GetDocumentCollectionLink(created_db, collection0, True), self.GetDocumentCollectionLink(created_db, collection1, True)]

        id_partition_key_extractor = lambda document: document['id']
        
        hashpartition_resolver = hash_partition_resolver.HashPartitionResolver(id_partition_key_extractor, collection_links)

        # create a document using the document definition
        document_definition = { 'id': '0',
                                'name': 'sample document',
                                'key': 'value' }
        
        document_definition['id'] = '2'

        collection_link = hashpartition_resolver.ResolveForCreate(document_definition)

        read_collection_links = hashpartition_resolver.ResolveForRead(document_definition['id'])

        self.assertEqual(1, len(read_collection_links))
        self.assertEqual(collection_link, read_collection_links[0])

    def test_consistent_hash_ring(self):
        created_db = { 'id': 'db' }

        collection_links = list()
        expected_partition_list = list()
        
        total_collections_count = 2

        collection = { 'id': 'coll' }

        for i in xrange(0, total_collections_count):
            collection['id'] = 'coll' + str(i)
            collection_link = self.GetDocumentCollectionLink(created_db, collection, True)
            collection_links.append(collection_link)

        expected_partition_list.append(('dbs/db/colls/coll0', 1076200484))
        expected_partition_list.append(('dbs/db/colls/coll0', 1302652881))
        expected_partition_list.append(('dbs/db/colls/coll0', 2210251988))
        expected_partition_list.append(('dbs/db/colls/coll1', 2341558382))
        expected_partition_list.append(('dbs/db/colls/coll0', 2348251587))
        expected_partition_list.append(('dbs/db/colls/coll0', 2887945459))
        expected_partition_list.append(('dbs/db/colls/coll1', 2894403633))
        expected_partition_list.append(('dbs/db/colls/coll1', 3031617259))
        expected_partition_list.append(('dbs/db/colls/coll1', 3090861424))
        expected_partition_list.append(('dbs/db/colls/coll1', 4222475028))

        id_partition_key_extractor = lambda document: document['id']
        
        hashpartition_resolver = hash_partition_resolver.HashPartitionResolver(id_partition_key_extractor, collection_links, 5)

        actual_partition_list = hashpartition_resolver.consistent_hash_ring._GetSerializedPartitionList()

        self.assertEqual(len(expected_partition_list), len(actual_partition_list))

        for i in xrange(0, len(expected_partition_list)):
            self.assertEqual(actual_partition_list[i][0], expected_partition_list[i][0])
            self.assertEqual(actual_partition_list[i][1], expected_partition_list[i][1])

        # Querying for a document and verifying that it's in the expected collection
        read_collection_links = hashpartition_resolver.ResolveForRead("beadledom")

        self.assertEqual(1, len(read_collection_links))

        collection['id'] = 'coll1'
        collection_link = self.GetDocumentCollectionLink(created_db, collection, True)

        self.assertTrue(collection_link in read_collection_links)

        # Querying for a document and verifying that it's in the expected collection
        read_collection_links = hashpartition_resolver.ResolveForRead("999")

        self.assertEqual(1, len(read_collection_links))

        collection['id'] = 'coll0'
        collection_link = self.GetDocumentCollectionLink(created_db, collection, True)

        self.assertTrue(collection_link in read_collection_links)
=======
        one_document_from_read = created_collection.get_item(
            item=replaced_document['id'],
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
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

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
<<<<<<< HEAD
        self._validate_bytes("The quick brown fox jumps over the lazy dog", 0x4C2DB001, bytearray(b'\x6D\xAB\x8D\xC9'), 3381504877)
=======
        self._validate_bytes("The quick brown fox jumps over the lazy dog", 0x4C2DB001, bytearray(b'\x6D\xAB\x8D\xC9'),
                             3381504877)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

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

<<<<<<< HEAD
    def test_range_partition_resolver(self):
        # create test database
        created_db = self.databseForTest
        
        # Create bunch of collections participating in partitioning
        collection0 = { 'id': 'coll_0' }
        collection1 = { 'id': 'coll_1' }
        collection2 = { 'id': 'coll_2' }

        collection_links = [self.GetDocumentCollectionLink(created_db, collection0, True), self.GetDocumentCollectionLink(created_db, collection1, True), self.GetDocumentCollectionLink(created_db, collection2, True)]
        
        val_partition_key_extractor = lambda document: document['val']

        ranges =[partition_range.Range(0,400), partition_range.Range(401,800), partition_range.Range(501,1200)]

        partition_map = dict([(ranges[0],collection_links[0]), (ranges[1],collection_links[1]), (ranges[2],collection_links[2])])

        rangepartition_resolver = range_partition_resolver.RangePartitionResolver(val_partition_key_extractor, partition_map)
        
        # create a document using the document definition
        document_definition = { 'id': '0',
                                'name': 'sample document',
                                'val': 0 }
        
        document_definition['val'] = 400

        collection_link = rangepartition_resolver.ResolveForCreate(document_definition)
        self.assertEquals(collection_links[0], collection_link)

        read_collection_links = rangepartition_resolver.ResolveForRead(600)

        self.assertEqual(2, len(read_collection_links))
        self.assertTrue(collection_links[1] in read_collection_links)
        self.assertTrue(collection_links[2] in read_collection_links)

        read_collection_links = rangepartition_resolver.ResolveForRead(partition_range.Range(250, 500))

        self.assertEqual(2, len(read_collection_links))
        self.assertTrue(collection_links[0] in read_collection_links)
        self.assertTrue(collection_links[1] in read_collection_links)

        read_collection_links = rangepartition_resolver.ResolveForRead(list([partition_range.Range(250, 500), partition_range.Range(600, 1000)]))

        self.assertEqual(3, len(read_collection_links))
        self.assertTrue(collection_links[0] in read_collection_links)
        self.assertTrue(collection_links[1] in read_collection_links)
        self.assertTrue(collection_links[2] in read_collection_links)

        read_collection_links = rangepartition_resolver.ResolveForRead(list([50, 100, 600, 1000]))

        self.assertEqual(3, len(read_collection_links))
        self.assertTrue(collection_links[0] in read_collection_links)
        self.assertTrue(collection_links[1] in read_collection_links)
        self.assertTrue(collection_links[2] in read_collection_links)

        read_collection_links = rangepartition_resolver.ResolveForRead(list([100, None]))

        self.assertEqual(3, len(read_collection_links))
        self.assertTrue(collection_links[0] in read_collection_links)
        self.assertTrue(collection_links[1] in read_collection_links)
        self.assertTrue(collection_links[2] in read_collection_links)


    # Upsert test for Document resource - selflink version
    def test_document_upsert_self_link(self):
        self._test_document_upsert(False)

    # Upsert test for Document resource - name based routing version
    def test_document_upsert_name_based(self):
        self._test_document_upsert(True)
        
    def _test_document_upsert(self, is_name_based):
        # create database
        created_db = self.databseForTest

        # create collection
        created_collection = self.configs.create_single_partition_collection_if_not_exist(self.client)

        # read documents and check count
        documents = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based)))
=======
    def test_document_upsert(self):
        # create database
        created_db = self.databaseForTest

        # create collection
        created_collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)

        # read documents and check count
        documents = list(created_collection.list_item_properties())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        before_create_documents_count = len(documents)

        # create document definition
        document_definition = {'id': 'doc',
                               'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value'}

        # create document using Upsert API
<<<<<<< HEAD
        created_document = self.client.UpsertItem(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based),
            document_definition)
=======
        created_document = created_collection.upsert_item(body=document_definition)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

        # verify id property
        self.assertEqual(created_document['id'],
                         document_definition['id'])

        # read documents after creation and verify updated count
<<<<<<< HEAD
        documents = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based)))
=======
        documents = list(created_collection.list_item_properties())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'create should increase the number of documents')

        # update document
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'
<<<<<<< HEAD
        
        # should replace document since it already exists
        upserted_document = self.client.UpsertItem(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based),
            created_document)
        
        # verify the changed properties
        self.assertEqual(upserted_document['name'],
                         created_document['name'],
                         'document id property should change')
=======

        # should replace document since it already exists
        upserted_document = created_collection.upsert_item(body=created_document)

        # verify the changed properties
        self.assertEqual(upserted_document['name'],
                         created_document['name'],
                         'document name property should change')
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(upserted_document['spam'],
                         created_document['spam'],
                         'property should have changed')

        # verify id property
        self.assertEqual(upserted_document['id'],
                         created_document['id'],
                         'document id should stay the same')
<<<<<<< HEAD
        
        # read documents after upsert and verify count doesn't increases again
        documents = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based)))
=======

        # read documents after upsert and verify count doesn't increases again
        documents = list(created_collection.list_item_properties())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'number of documents should remain same')

        created_document['id'] = 'new id'

        # Upsert should create new document since the id is different
<<<<<<< HEAD
        new_document = self.client.UpsertItem(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based),
            created_document)
        
=======
        new_document = created_collection.upsert_item(body=created_document)

>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        # verify id property
        self.assertEqual(created_document['id'],
                         new_document['id'],
                         'document id should be same')
<<<<<<< HEAD
        
        # read documents after upsert and verify count increases
        documents = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based)))
=======

        # read documents after upsert and verify count increases
        documents = list(created_collection.list_item_properties())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(
            len(documents),
            before_create_documents_count + 2,
            'upsert should increase the number of documents')

        # delete documents
<<<<<<< HEAD
        self.client.DeleteItem(self.GetDocumentLink(created_db, created_collection, upserted_document, is_name_based))
        self.client.DeleteItem(self.GetDocumentLink(created_db, created_collection, new_document, is_name_based))

        # read documents after delete and verify count is same as original
        documents = list(self.client.ReadItems(
            self.GetDocumentCollectionLink(created_db, created_collection, is_name_based)))
=======
        created_collection.delete_item(item=upserted_document, partition_key=upserted_document['id'])
        created_collection.delete_item(item=new_document, partition_key=new_document['id'])

        # read documents after delete and verify count is same as original
        documents = list(created_collection.list_item_properties())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(
            len(documents),
            before_create_documents_count,
            'number of documents should remain same')
<<<<<<< HEAD
        

    def test_spatial_index_self_link(self):
        self._test_spatial_index(False)

    def test_spatial_index_name_based(self):
        self._test_spatial_index(True)
        
    def _test_spatial_index(self, is_name_based):
        db = self.databseForTest
        # partial policy specified
        collection = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based),
            {
                'id': 'collection with spatial index ' + str(uuid.uuid4()),
                'indexingPolicy': {
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
                }
            })
        self.client.CreateItem(self.GetDocumentCollectionLink(db, collection, is_name_based), {
            'id': 'loc1',
            'Location': {
                'type': 'Point',
                'coordinates': [ 20.0, 20.0 ]
            }
        })
        self.client.CreateItem(self.GetDocumentCollectionLink(db, collection, is_name_based), {
            'id': 'loc2',
            'Location': {
                'type': 'Point',
                'coordinates': [ 100.0, 100.0 ]
            }
        })
        results = list(self.client.QueryItems(
            self.GetDocumentCollectionLink(db, collection, is_name_based),
            "SELECT * FROM root WHERE (ST_DISTANCE(root.Location, {type: 'Point', coordinates: [20.1, 20]}) < 20000) "))
        self.assertEqual(1, len(results))
        self.assertEqual('loc1', results[0]['id'])

    
    def test_attachment_crud_self_link(self):
        self._test_attachment_crud(False)

    def test_attachment_crud_name_based(self):
        self._test_attachment_crud(True)
        
    def _test_attachment_crud(self, is_name_based):
        class ReadableStream(object):
            """Customized file-like stream.
            """

            def __init__(self, chunks = ['first chunk ', 'second chunk']):
                """Initialization.

                :Parameters:
                    - `chunks`: list

                """
                if six.PY2:
                    self._chunks = list(chunks)
                else:
                    # python3: convert to bytes
                    self._chunks = [chunk.encode() for chunk in chunks]

            def read(self, n=-1):
                """Simulates the read method in a file stream.

                :Parameters:
                    - `n`: int

                :Returns:
                    str or bytes

                """
                if self._chunks:
                    return self._chunks.pop(0)
                else:
                    return ''

            def __len__(self):
                """To make len(ReadableStream) work.
                """
                return sum([len(chunk) for chunk in self._chunks])


        # Should do attachment CRUD operations successfully
        self.client.connection_policy.MediaReadMode = documents.MediaReadMode.Buffered

        # create database
        db = self.databseForTest
        # create collection
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
        # create document
        document = self.client.CreateItem(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                         { 'id': 'sample document',
                                           'spam': 'eggs',
                                           'key': 'value' })
        # list all attachments
        attachments = list(self.client.ReadAttachments(self.GetDocumentLink(db, collection, document, is_name_based)))
        initial_count = len(attachments)
        valid_media_options = { 'slug': 'attachment name',
                                'contentType': 'application/text' }
        invalid_media_options = { 'slug': 'attachment name',
                                  'contentType': 'junt/test' }
        # create attachment with invalid content-type
        content_stream = ReadableStream()
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            self.client.CreateAttachmentAndUploadMedia,
            self.GetDocumentLink(db, collection, document, is_name_based),
            content_stream,
            invalid_media_options)
        content_stream = ReadableStream()
        # create streamed attachment with valid content-type
        valid_attachment = self.client.CreateAttachmentAndUploadMedia(
            self.GetDocumentLink(db, collection, document, is_name_based), content_stream, valid_media_options)
        self.assertEqual(valid_attachment['id'],
                         'attachment name',
                         'id of created attachment should be the'
                         ' same as the one in the request')
        content_stream = ReadableStream()
        # create colliding attachment
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.CONFLICT,
            self.client.CreateAttachmentAndUploadMedia,
            self.GetDocumentLink(db, collection, document, is_name_based),
            content_stream,
            valid_media_options)

        content_stream = ReadableStream()
        # create attachment with media link
        dynamic_attachment = {
            'id': 'dynamic attachment',
            'media': 'http://xstore.',
            'MediaType': 'Book',
            'Author':'My Book Author',
            'Title':'My Book Title',
            'contentType':'application/text'
        }
        attachment = self.client.CreateAttachment(self.GetDocumentLink(db, collection, document, is_name_based),
                                             dynamic_attachment)
        self.assertEqual(attachment['MediaType'],
                         'Book',
                         'invalid media type')
        self.assertEqual(attachment['Author'],
                         'My Book Author',
                         'invalid property value')
        # list all attachments
        attachments = list(self.client.ReadAttachments(self.GetDocumentLink(db, collection, document, is_name_based)))
        self.assertEqual(len(attachments),
                         initial_count + 2,
                         'number of attachments should\'ve increased by 2')
        attachment['Author'] = 'new author'
        # replace the attachment
        self.client.ReplaceAttachment(self.GetAttachmentLink(db, collection, document, attachment, is_name_based), attachment)
        self.assertEqual(attachment['MediaType'],
                         'Book',
                         'invalid media type')
        self.assertEqual(attachment['Author'],
                         'new author',
                         'invalid property value')
        # read attachment media
        media_response = self.client.ReadMedia(valid_attachment['media'])
        self.assertEqual(media_response,
                         'first chunk second chunk')
        content_stream = ReadableStream(['modified first chunk ',
                                         'modified second chunk'])
        # update attachment media
        self.client.UpdateMedia(valid_attachment['media'],
                           content_stream,
                           valid_media_options)
        # read attachment media after update
        # read media buffered
        media_response = self.client.ReadMedia(valid_attachment['media'])
        self.assertEqual(media_response,
                         'modified first chunk modified second chunk')
        # read media streamed
        self.client.connection_policy.MediaReadMode = (
            documents.MediaReadMode.Streamed)
        media_response = self.client.ReadMedia(valid_attachment['media'])
        self.assertEqual(media_response.read(),
                         b'modified first chunk modified second chunk')
        # share attachment with a second document
        document = self.client.CreateItem(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                         {'id': 'document 2'})
        second_attachment = {
            'id': valid_attachment['id'],
            'contentType': valid_attachment['contentType'],
            'media': valid_attachment['media'] }
        attachment = self.client.CreateAttachment(self.GetDocumentLink(db, collection, document, is_name_based),
                                             second_attachment)
        self.assertEqual(valid_attachment['id'],
                         attachment['id'],
                         'id mismatch')
        self.assertEqual(valid_attachment['media'],
                         attachment['media'],
                         'media mismatch')
        self.assertEqual(valid_attachment['contentType'],
                         attachment['contentType'],
                         'contentType mismatch')
        # deleting attachment
        self.client.DeleteAttachment(self.GetAttachmentLink(db, collection, document, attachment, is_name_based))
        # read attachments after deletion
        attachments = list(self.client.ReadAttachments(self.GetDocumentLink(db, collection, document, is_name_based)))
        self.assertEqual(len(attachments), 0)

    # Upsert test for Attachment resource - selflink version
    def test_attachment_upsert_self_link(self):
        self._test_attachment_upsert(False)

    # Upsert test for Attachment resource - name based routing version
    def test_attachment_upsert_name_based(self):
        self._test_attachment_upsert(True)
        
    def _test_attachment_upsert(self, is_name_based):
        class ReadableStream(object):
            """Customized file-like stream.
            """

            def __init__(self, chunks = ['first chunk ', 'second chunk']):
                """Initialization.

                :Parameters:
                    - `chunks`: list

                """
                if six.PY2:
                    self._chunks = list(chunks)
                else:
                    # python3: convert to bytes
                    self._chunks = [chunk.encode() for chunk in chunks]

            def read(self, n=-1):
                """Simulates the read method in a file stream.

                :Parameters:
                    - `n`: int

                :Returns:
                    str or bytes

                """
                if self._chunks:
                    return self._chunks.pop(0)
                else:
                    return ''

            def __len__(self):
                """To make len(ReadableStream) work.
                """
                return sum([len(chunk) for chunk in self._chunks])

        # create database
        db = self.databseForTest
        
        # create collection
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
        
        # create document
        document = self.client.CreateItem(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                         { 'id': 'sample document' + str(uuid.uuid4()),
                                           'spam': 'eggs',
                                           'key': 'value' })
        
        # list all attachments and check count
        attachments = list(self.client.ReadAttachments(self.GetDocumentLink(db, collection, document, is_name_based)))
        initial_count = len(attachments)
        
        valid_media_options = { 'slug': 'attachment name',
                                'contentType': 'application/text' }
        content_stream = ReadableStream()
        
        # create streamed attachment with valid content-type using Upsert API
        valid_attachment = self.client.UpsertAttachmentAndUploadMedia(
            self.GetDocumentLink(db, collection, document, is_name_based), content_stream, valid_media_options)
        
        # verify id property
        self.assertEqual(valid_attachment['id'],
                         'attachment name',
                         'id of created attachment should be the same')

        valid_media_options = { 'slug': 'new attachment name',
                                'contentType': 'application/text' }
        content_stream = ReadableStream()
        
        # Upsert should create new attachment since since id is different
        new_valid_attachment = self.client.UpsertAttachmentAndUploadMedia(
            self.GetDocumentLink(db, collection, document, is_name_based), content_stream, valid_media_options)
        
        # verify id property
        self.assertEqual(new_valid_attachment['id'],
                         'new attachment name',
                         'id of new attachment should be the same')

        # read all attachments and verify updated count
        attachments = list(self.client.ReadAttachments(self.GetDocumentLink(db, collection, document, is_name_based)))
        self.assertEqual(len(attachments),
                         initial_count + 2,
                         'number of attachments should have increased by 2')
        
        # create attachment with media link
        attachment_definition = {
            'id': 'dynamic attachment',
            'media': 'http://xstore.',
            'MediaType': 'Book',
            'Author':'My Book Author',
            'Title':'My Book Title',
            'contentType':'application/text'
        }

        # create dynamic attachment using Upsert API
        dynamic_attachment = self.client.UpsertAttachment(self.GetDocumentLink(db, collection, document, is_name_based),
                                             attachment_definition)

        # verify id property
        self.assertEqual(dynamic_attachment['id'],
                         attachment_definition['id'],
                         'id of attachment should be the same')

        # read all attachments and verify updated count
        attachments = list(self.client.ReadAttachments(self.GetDocumentLink(db, collection, document, is_name_based)))
        self.assertEqual(len(attachments),
                         initial_count + 3,
                         'number of attachments should have increased by 3')

        dynamic_attachment['Author'] = 'new author'
        
        # replace the attachment using Upsert API
        upserted_attachment = self.client.UpsertAttachment(self.GetDocumentLink(db, collection, document, is_name_based), dynamic_attachment)

        # verify id property remains same
        self.assertEqual(dynamic_attachment['id'],
                         upserted_attachment['id'],
                         'id should stay the same')

        # verify author property gets updated
        self.assertEqual(upserted_attachment['Author'],
                         dynamic_attachment['Author'],
                         'invalid property value')

        # read all attachments and verify count doesn't increases again
        attachments = list(self.client.ReadAttachments(self.GetDocumentLink(db, collection, document, is_name_based)))
        self.assertEqual(len(attachments),
                         initial_count + 3,
                         'number of attachments should remain same')

        dynamic_attachment['id'] = 'new dynamic attachment'
        
        # Upsert should create new attachment since id is different
        new_attachment = self.client.UpsertAttachment(self.GetDocumentLink(db, collection, document, is_name_based), dynamic_attachment)

        # verify id property remains same
        self.assertEqual(dynamic_attachment['id'],
                         new_attachment['id'],
                         'id should be same')

        # read all attachments and verify count increases
        attachments = list(self.client.ReadAttachments(self.GetDocumentLink(db, collection, document, is_name_based)))
        self.assertEqual(len(attachments),
                         initial_count + 4,
                         'number of attachments should have increased')

        # deleting attachments
        self.client.DeleteAttachment(self.GetAttachmentLink(db, collection, document, valid_attachment, is_name_based))
        self.client.DeleteAttachment(self.GetAttachmentLink(db, collection, document, new_valid_attachment, is_name_based))
        self.client.DeleteAttachment(self.GetAttachmentLink(db, collection, document, upserted_attachment, is_name_based))
        self.client.DeleteAttachment(self.GetAttachmentLink(db, collection, document, new_attachment, is_name_based))

        # wait to ensure deletes are propagated for multimaster enabled accounts
        if self.configs.IS_MULTIMASTER_ENABLED:
            time.sleep(2)

        # read all attachments and verify count remains same
        attachments = list(self.client.ReadAttachments(self.GetDocumentLink(db, collection, document, is_name_based)))
        self.assertEqual(len(attachments),
                         initial_count,
                         'number of attachments should remain the same')
        

    def test_user_crud_self_link(self):
        self._test_user_crud(False)

    def test_user_crud_name_based(self):
        self._test_user_crud(True)
        
    def _test_user_crud(self, is_name_based):
        # Should do User CRUD operations successfully.
        # create database
        db = self.databseForTest
        # list users
        users = list(self.client.ReadUsers(self.GetDatabaseLink(db, is_name_based)))
        before_create_count = len(users)
        # create user
        user_id = 'new user' + str(uuid.uuid4())
        user = self.client.CreateUser(self.GetDatabaseLink(db, is_name_based), { 'id': user_id })
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
                    { 'name':'@id', 'value':user_id }
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
        db = self.databseForTest
        
        # read users and check count
        users = list(self.client.ReadUsers(self.GetDatabaseLink(db, is_name_based)))
        before_create_count = len(users)
        
        # create user using Upsert API
        user_id = 'user' + str(uuid.uuid4())
        user = self.client.UpsertUser(self.GetDatabaseLink(db, is_name_based), { 'id': user_id })

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
        db = self.databseForTest
        # create user
        user = self.client.CreateUser(self.GetDatabaseLink(db, is_name_based), { 'id': 'new user' + str(uuid.uuid4())})
        # list permissions
        permissions = list(self.client.ReadPermissions(self.GetUserLink(db, user, is_name_based)))
=======

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

    # CRUD test for User resource
    def test_user_crud(self):
        # Should do User CRUD operations successfully.
        # create database
        db = self.databaseForTest
        # list users
        users = list(db.list_user_properties())
        before_create_count = len(users)
        # create user
        user_id = 'new user' + str(uuid.uuid4())
        user = db.create_user(body={'id': user_id})
        self.assertEqual(user.id, user_id, 'user id error')
        # list users after creation
        users = list(db.list_user_properties())
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
        user = user.properties
        user['id'] = replaced_user_id
        replaced_user = db.replace_user(user_id, user)
        self.assertEqual(replaced_user.id,
                         replaced_user_id,
                         'user id should change')
        self.assertEqual(user['id'],
                         replaced_user.id,
                         'user id should stay the same')
        # read user
        user = db.get_user(replaced_user.id)
        self.assertEqual(replaced_user.id, user.id)
        # delete user
        db.delete_user(user.id)
        # read user after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           db.get_user,
                                           user.id)

    def test_user_upsert(self):
        # create database
        db = self.databaseForTest

        # read users and check count
        users = list(db.list_user_properties())
        before_create_count = len(users)

        # create user using Upsert API
        user_id = 'user' + str(uuid.uuid4())
        user = db.upsert_user(body={'id': user_id})

        # verify id property
        self.assertEqual(user.id, user_id, 'user id error')

        # read users after creation and verify updated count
        users = list(db.list_user_properties())
        self.assertEqual(len(users), before_create_count + 1)

        # Should replace the user since it already exists, there is no public property to change here
        upserted_user = db.upsert_user(user.properties)

        # verify id property
        self.assertEqual(upserted_user.id,
                         user.id,
                         'user id should remain same')

        # read users after upsert and verify count doesn't increases again
        users = list(db.list_user_properties())
        self.assertEqual(len(users), before_create_count + 1)

        user.properties['id'] = 'new user' + str(uuid.uuid4())
        user.id = user.properties['id']

        # Upsert should create new user since id is different
        new_user = db.upsert_user(user.properties)

        # verify id property
        self.assertEqual(new_user.id, user.id, 'user id error')

        # read users after upsert and verify count increases
        users = list(db.list_user_properties())
        self.assertEqual(len(users), before_create_count + 2)

        # delete users
        db.delete_user(upserted_user.id)
        db.delete_user(new_user.id)

        # read users after delete and verify count remains the same
        users = list(db.list_user_properties())
        self.assertEqual(len(users), before_create_count)

    def test_permission_crud(self):
        # Should do Permission CRUD operations successfully
        # create database
        db = self.databaseForTest
        # create user
        user = db.create_user(body={'id': 'new user' + str(uuid.uuid4())})
        # list permissions
        permissions = list(user.list_permission_properties())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        before_create_count = len(permissions)
        permission = {
            'id': 'new permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': 'dbs/AQAAAA==/colls/AQAAAJ0fgTc='  # A random one.
        }
        # create permission
<<<<<<< HEAD
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
                    { 'name':'@id', 'value':permission['id'] }
                ]
            }))
        self.assert_(results)

        # replace permission
        change_permission = permission.copy()
        permission['id'] = 'replaced permission'
        replaced_permission = self.client.ReplacePermission(self.GetPermissionLink(db, user, change_permission, is_name_based),
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
        db = self.databseForTest
        
        # create user
        user = self.client.CreateUser(self.GetDatabaseLink(db, is_name_based), { 'id': 'new user' + str(uuid.uuid4())})
        
        # read permissions and check count
        permissions = list(self.client.ReadPermissions(self.GetUserLink(db, user, is_name_based)))
        before_create_count = len(permissions)
        
=======
        permission = user.create_permission(permission)
        self.assertEqual(permission.id,
                         'new permission',
                         'permission id error')
        # list permissions after creation
        permissions = list(user.list_permission_properties())
        self.assertEqual(len(permissions), before_create_count + 1)
        # query permissions
        results = list(user.query_permissions(
                query='SELECT * FROM root r WHERE r.id=@id',
                parameters=[
                    {'name': '@id', 'value': permission.id}
                ]
        ))
        self.assert_(results)

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
        permissions = list(user.list_permission_properties())
        before_create_count = len(permissions)

>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        permission_definition = {
            'id': 'permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': 'dbs/AQAAAA==/colls/AQAAAJ0fgTc='  # A random one.
        }
<<<<<<< HEAD
        
        # create permission using Upsert API
        created_permission = self.client.UpsertPermission(self.GetUserLink(db, user, is_name_based), permission_definition)
        
        # verify id property
        self.assertEqual(created_permission['id'],
                         permission_definition['id'],
                         'permission id error')
        
        # read permissions after creation and verify updated count
        permissions = list(self.client.ReadPermissions(self.GetUserLink(db, user, is_name_based)))
        self.assertEqual(len(permissions), before_create_count + 1)
        
=======

        # create permission using Upsert API
        created_permission = user.upsert_permission(permission_definition)

        # verify id property
        self.assertEqual(created_permission.id,
                         permission_definition['id'],
                         'permission id error')

        # read permissions after creation and verify updated count
        permissions = list(user.list_permission_properties())
        self.assertEqual(len(permissions), before_create_count + 1)

>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        # update permission mode
        permission_definition['permissionMode'] = documents.PermissionMode.All

        # should repace the permission since it already exists
<<<<<<< HEAD
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
=======
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
        permissions = list(user.list_permission_properties())
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
        permissions = list(user.list_permission_properties())
        self.assertEqual(len(permissions), before_create_count + 2)

        # delete permissions
        user.delete_permission(upserted_permission.id)
        user.delete_permission(new_permission.id)

        # read permissions and verify count remains the same
        permissions = list(user.list_permission_properties())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(len(permissions), before_create_count)

    def test_authorization(self):
        def __SetupEntities(client):
            """
            Sets up entities for this test.

            :Parameters:
<<<<<<< HEAD
                - `client`: cosmos_client.CosmosClient
=======
                - `client`: cosmos_client_connection.CosmosClientConnection
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

            :Returns:
                dict

            """
            # create database
<<<<<<< HEAD
            db = self.databseForTest
            # create collection1
            collection1 = client.CreateContainer(
                db['_self'], { 'id': 'test_authorization ' + str(uuid.uuid4()) })
            # create document1
            document1 = client.CreateItem(collection1['_self'],
                                              { 'id': 'coll1doc1',
                                                'spam': 'eggs',
                                                'key': 'value' })
            # create document 2
            document2 = client.CreateItem(
                collection1['_self'],
                { 'id': 'coll1doc2', 'spam': 'eggs2', 'key': 'value2' })
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
                { 'id': 'test_authorization2 ' + str(uuid.uuid4()) })
            # create user1
            user1 = client.CreateUser(db['_self'], { 'id': 'user1' })
            permission = {
                'id': 'permission On Coll1',
                'permissionMode': documents.PermissionMode.Read,
                'resource': collection1['_self']
            }
            # create permission for collection1
            permission_on_coll1 = client.CreatePermission(user1['_self'],
                                                          permission)
            self.assertTrue(permission_on_coll1['_token'] != None,
=======
            db = self.databaseForTest
            # create collection1
            collection1 = db.create_container(
                id='test_authorization' + str(uuid.uuid4()),
                partition_key=PartitionKey(path='/id', kind='Hash')
            )
            # create document1
            document1 = collection1.create_item(
                            body={'id': 'coll1doc1',
                                  'spam': 'eggs',
                                  'key': 'value'},
            )
            # create document 2
            document2 = collection1.create_item(
                body={'id': 'coll1doc2', 'spam': 'eggs2', 'key': 'value2'}
            )

            # create collection 2
            collection2 = db.create_container(
                id='test_authorization2' + str(uuid.uuid4()),
                partition_key=PartitionKey(path='/id', kind='Hash')
            )
            # create user1
            user1 = db.create_user(body={'id': 'user1'})
            permission = {
                'id': 'permission On Coll1',
                'permissionMode': documents.PermissionMode.Read,
                'resource': collection1.properties['_self']
            }
            # create permission for collection1
            permission_on_coll1 = user1.create_permission(body=permission)
            self.assertIsNotNone(permission_on_coll1.properties['_token'],
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
                            'permission token is invalid')
            permission = {
                'id': 'permission On Doc1',
                'permissionMode': documents.PermissionMode.All,
                'resource': document2['_self']
            }
            # create permission for document 2
<<<<<<< HEAD
            permission_on_doc2 = client.CreatePermission(user1['_self'],
                                                         permission)
            self.assertTrue(permission_on_doc2['_token'] != None,
                            'permission token is invalid')
            # create user 2
            user2 = client.CreateUser(db['_self'], { 'id': 'user2' })
            permission = {
                'id': 'permission On coll2',
                'permissionMode': documents.PermissionMode.All,
                'resource': collection2['_self']
            }
            # create permission on collection 2
            permission_on_coll2 = client.CreatePermission(
                user2['_self'], permission)
=======
            permission_on_doc2 = user1.create_permission(body=permission)
            self.assertIsNotNone(permission_on_doc2.properties['_token'],
                            'permission token is invalid')
            # create user 2
            user2 = db.create_user(body={'id': 'user2'})
            permission = {
                'id': 'permission On coll2',
                'permissionMode': documents.PermissionMode.All,
                'resource': collection2.properties['_self']
            }
            # create permission on collection 2
            permission_on_coll2 = user2.create_permission(body=permission)
            self.assertIsNotNone(permission_on_coll2.properties['_token'],
                            'permission token is invalid')
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
            entities = {
                'db': db,
                'coll1': collection1,
                'coll2': collection2,
                'doc1': document1,
                'doc2': document2,
                'user1': user1,
                'user2': user2,
<<<<<<< HEAD
                'attachment': attachment,
=======
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
                'permissionOnColl1': permission_on_coll1,
                'permissionOnDoc2': permission_on_doc2,
                'permissionOnColl2': permission_on_coll2
            }
            return entities

        # Client without any authorization will fail.
<<<<<<< HEAD
        client = cosmos_client.CosmosClient(CRUDTests.host, {}, CRUDTests.connectionPolicy)
        self.__AssertHTTPFailureWithStatus(StatusCodes.UNAUTHORIZED,
                                           list,
                                           client.ReadDatabases())
        # Client with master key.
        client = cosmos_client.CosmosClient(CRUDTests.host,
                                                {'masterKey': CRUDTests.masterKey}, CRUDTests.connectionPolicy)
        # setup entities
        entities = __SetupEntities(client)
        resource_tokens = {}
        resource_tokens[entities['coll1']['_rid']] = (
            entities['permissionOnColl1']['_token'])
        resource_tokens[entities['doc1']['_rid']] = (
            entities['permissionOnColl1']['_token'])
        col1_client = cosmos_client.CosmosClient(
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
=======
        client = cosmos_client.CosmosClient(CRUDTests.host, {}, "Session", CRUDTests.connectionPolicy)
        self.__AssertHTTPFailureWithStatus(StatusCodes.UNAUTHORIZED,
                                           list,
                                           client.list_database_properties())
        # Client with master key.
        client = cosmos_client.CosmosClient(CRUDTests.host,
                                            {'masterKey': CRUDTests.masterKey},
                                            "Session",
                                            CRUDTests.connectionPolicy)
        # setup entities
        entities = __SetupEntities(client)
        resource_tokens = {}
        resource_tokens[entities['coll1'].id] = (
            entities['permissionOnColl1'].properties['_token'])
        resource_tokens[entities['doc1']['id']]= (
            entities['permissionOnColl1'].properties['_token'])
        col1_client = cosmos_client.CosmosClient(
            CRUDTests.host, {'resourceTokens': resource_tokens},"Session", CRUDTests.connectionPolicy)
        db = entities['db']

        old_client_connection = db.client_connection
        db.client_connection = col1_client.client_connection
        # 1. Success-- Use Col1 Permission to Read
        success_coll1 = db.get_container(container=entities['coll1'])
        # 2. Failure-- Use Col1 Permission to delete
        self.__AssertHTTPFailureWithStatus(StatusCodes.FORBIDDEN,
                                           db.delete_container,
                                           success_coll1)
        # 3. Success-- Use Col1 Permission to Read All Docs
        success_documents = list(success_coll1.list_item_properties())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertTrue(success_documents != None,
                        'error reading documents')
        self.assertEqual(len(success_documents),
                         2,
                         'Expected 2 Documents to be succesfully read')
        # 4. Success-- Use Col1 Permission to Read Col1Doc1
<<<<<<< HEAD
        success_doc = col1_client.ReadItem(entities['doc1']['_self'])
=======
        success_doc = success_coll1.get_item(
            item=entities['doc1']['id'],
            partition_key=entities['doc1']['id']
        )
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertTrue(success_doc != None, 'error reading document')
        self.assertEqual(
            success_doc['id'],
            entities['doc1']['id'],
            'Expected to read children using parent permissions')
        col2_client = cosmos_client.CosmosClient(
            CRUDTests.host,
<<<<<<< HEAD
            { 'permissionFeed': [ entities['permissionOnColl2'] ] }, CRUDTests.connectionPolicy)
=======
            {'permissionFeed': [entities['permissionOnColl2'].properties]}, "Session", CRUDTests.connectionPolicy)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        doc = {
            'CustomProperty1': 'BBBBBB',
            'customProperty2': 1000,
            'id': entities['doc2']['id']
        }
<<<<<<< HEAD
        success_doc = col2_client.CreateItem(
            entities['coll2']['_self'], doc)
=======
        entities['coll2'].client_connection = col2_client.client_connection
        success_doc = entities['coll2'].create_item(body=doc)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertTrue(success_doc != None, 'error creating document')
        self.assertEqual(success_doc['CustomProperty1'],
                         doc['CustomProperty1'],
                         'document should have been created successfully')

<<<<<<< HEAD
        self.client.DeleteContainer(entities['coll1']['_self'])
        self.client.DeleteContainer(entities['coll2']['_self'])

    def test_trigger_crud_self_link(self):
        self._test_trigger_crud(False)

    def test_trigger_crud_name_based(self):
        self._test_trigger_crud(True)
        
    def _test_trigger_crud(self, is_name_based):
        # create database
        db = self.databseForTest
        # create collection
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
        # read triggers
        triggers = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection, is_name_based)))
=======
        db.client_connection = old_client_connection
        db.delete_container(entities['coll1'])
        db.delete_container(entities['coll2'])

    def test_trigger_crud(self):
        # create database
        db = self.databaseForTest
        # create collection
        collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)
        # read triggers
        triggers = list(collection.scripts.list_triggers())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        # create a trigger
        before_create_triggers_count = len(triggers)
        trigger_definition = {
            'id': 'sample trigger',
            'serverScript': 'function() {var x = 10;}',
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        }
<<<<<<< HEAD
        trigger = self.client.CreateTrigger(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                       trigger_definition)
=======
        trigger = collection.scripts.create_trigger(body=trigger_definition)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        for property in trigger_definition:
            if property != "serverScript":
                self.assertEqual(
                    trigger[property],
                    trigger_definition[property],
                    'property {property} should match'.format(property=property))
            else:
<<<<<<< HEAD
                    self.assertEqual(trigger['body'],
                                     'function() {var x = 10;}')

        # read triggers after creation
        triggers = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection, is_name_based)))
=======
                self.assertEqual(trigger['body'],
                                 'function() {var x = 10;}')

        # read triggers after creation
        triggers = list(collection.scripts.list_triggers())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(len(triggers),
                         before_create_triggers_count + 1,
                         'create should increase the number of triggers')
        # query triggers
<<<<<<< HEAD
        triggers = list(self.client.QueryTriggers(
            self.GetDocumentCollectionLink(db, collection, is_name_based),
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    { 'name': '@id', 'value': trigger_definition['id']}
                ]
            }))
=======
        triggers = list(collection.scripts.query_triggers(
                query='SELECT * FROM root r WHERE r.id=@id',
                parameters=[
                    {'name': '@id', 'value': trigger_definition['id']}
                ]
        ))
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assert_(triggers)

        # replace trigger
        change_trigger = trigger.copy()
        trigger['body'] = 'function() {var x = 20;}'
<<<<<<< HEAD
        replaced_trigger = self.client.ReplaceTrigger(self.GetTriggerLink(db, collection, change_trigger, is_name_based), trigger)
=======
        replaced_trigger = collection.scripts.replace_trigger(change_trigger['id'], trigger)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
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
<<<<<<< HEAD
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
        db = self.databseForTest
        
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
        upserted_trigger = self.client.UpsertTrigger(self.GetDocumentCollectionLink(db, collection, is_name_based), created_trigger)

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
        new_trigger = self.client.UpsertTrigger(self.GetDocumentCollectionLink(db, collection, is_name_based), created_trigger)

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
        db = self.databseForTest
        # create collection
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
        # read udfs
        udfs = list(self.client.ReadUserDefinedFunctions(self.GetDocumentCollectionLink(db, collection, is_name_based)))
=======
        trigger = collection.scripts.get_trigger(replaced_trigger['id'])
        self.assertEqual(replaced_trigger['id'], trigger['id'])
        # delete trigger
        collection.scripts.delete_trigger(replaced_trigger['id'])
        # read triggers after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           collection.scripts.delete_trigger,
                                           replaced_trigger['id'])

    def test_udf_crud(self):
        # create database
        db = self.databaseForTest
        # create collection
        collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)
        # read udfs
        udfs = list(collection.scripts.list_user_defined_functions())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        # create a udf
        before_create_udfs_count = len(udfs)
        udf_definition = {
            'id': 'sample udf',
            'body': 'function() {var x = 10;}'
        }
<<<<<<< HEAD
        udf = self.client.CreateUserDefinedFunction(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                               udf_definition)
        for property in udf_definition:
                self.assertEqual(
                    udf[property],
                    udf_definition[property],
                    'property {property} should match'.format(property=property))

        # read udfs after creation
        udfs = list(self.client.ReadUserDefinedFunctions(self.GetDocumentCollectionLink(db, collection, is_name_based)))
=======
        udf = collection.scripts.create_user_defined_function(body=udf_definition)
        for property in udf_definition:
            self.assertEqual(
                udf[property],
                udf_definition[property],
                'property {property} should match'.format(property=property))

        # read udfs after creation
        udfs = list(collection.scripts.list_user_defined_functions())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(len(udfs),
                         before_create_udfs_count + 1,
                         'create should increase the number of udfs')
        # query udfs
<<<<<<< HEAD
        results = list(self.client.QueryUserDefinedFunctions(
            self.GetDocumentCollectionLink(db, collection, is_name_based),
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    {'name':'@id', 'value':udf_definition['id']}
                ]
            }))
=======
        results = list(collection.scripts.query_user_defined_functions(
                query='SELECT * FROM root r WHERE r.id=@id',
                parameters=[
                    {'name': '@id', 'value': udf_definition['id']}
                ]
        ))
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assert_(results)
        # replace udf
        change_udf = udf.copy()
        udf['body'] = 'function() {var x = 20;}'
<<<<<<< HEAD
        replaced_udf = self.client.ReplaceUserDefinedFunction(self.GetUserDefinedFunctionLink(db, collection, change_udf, is_name_based), udf)
        for property in udf_definition:
                self.assertEqual(
                    replaced_udf[property],
                    udf[property],
                    'property {property} should match'.format(property=property))
        # read udf
        udf = self.client.ReadUserDefinedFunction(self.GetUserDefinedFunctionLink(db, collection, replaced_udf, is_name_based))
        self.assertEqual(replaced_udf['id'], udf['id'])
        # delete udf
        self.client.DeleteUserDefinedFunction(self.GetUserDefinedFunctionLink(db, collection, replaced_udf, is_name_based))
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
        db = self.databseForTest
        
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
        created_udf = self.client.UpsertUserDefinedFunction(self.GetDocumentCollectionLink(db, collection, is_name_based),
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
        upserted_udf = self.client.UpsertUserDefinedFunction(self.GetDocumentCollectionLink(db, collection, is_name_based), created_udf)

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
        new_udf = self.client.UpsertUserDefinedFunction(self.GetDocumentCollectionLink(db, collection, is_name_based), created_udf)

        # verify id property
        self.assertEqual(created_udf['id'],
                         new_udf['id'])
        
        # read udf and verify count increases
        udfs = list(self.client.ReadUserDefinedFunctions(self.GetDocumentCollectionLink(db, collection, is_name_based)))
        self.assertEqual(len(udfs),
                         before_create_udfs_count + 2,
                         'upsert should keep the number of udfs same')
        
        # delete udfs
        self.client.DeleteUserDefinedFunction(self.GetUserDefinedFunctionLink(db, collection, upserted_udf, is_name_based))
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
        db = self.databseForTest
        # create collection
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
        # read sprocs
        sprocs = list(self.client.ReadStoredProcedures(self.GetDocumentCollectionLink(db, collection, is_name_based)))
=======
        replaced_udf = collection.scripts.replace_user_defined_function(udf=udf['id'], body=udf)
        for property in udf_definition:
            self.assertEqual(
                replaced_udf[property],
                udf[property],
                'property {property} should match'.format(property=property))
        # read udf
        udf = collection.scripts.get_user_defined_function(replaced_udf['id'])
        self.assertEqual(replaced_udf['id'], udf['id'])
        # delete udf
        collection.scripts.delete_user_defined_function(replaced_udf['id'])
        # read udfs after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           collection.scripts.get_user_defined_function,
                                           replaced_udf['id'])

    def test_sproc_crud(self):
        # create database
        db = self.databaseForTest
        # create collection
        collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)
        # read sprocs
        sprocs = list(collection.scripts.list_stored_procedures())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        # create a sproc
        before_create_sprocs_count = len(sprocs)
        sproc_definition = {
            'id': 'sample sproc',
            'serverScript': 'function() {var x = 10;}'
        }
<<<<<<< HEAD
        sproc = self.client.CreateStoredProcedure(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                             sproc_definition)
=======
        sproc = collection.scripts.create_stored_procedure(body=sproc_definition)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        for property in sproc_definition:
            if property != "serverScript":
                self.assertEqual(
                    sproc[property],
                    sproc_definition[property],
                    'property {property} should match'.format(property=property))
            else:
                self.assertEqual(sproc['body'], 'function() {var x = 10;}')

        # read sprocs after creation
<<<<<<< HEAD
        sprocs = list(self.client.ReadStoredProcedures(self.GetDocumentCollectionLink(db, collection, is_name_based)))
=======
        sprocs = list(collection.scripts.list_stored_procedures())
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(len(sprocs),
                         before_create_sprocs_count + 1,
                         'create should increase the number of sprocs')
        # query sprocs
<<<<<<< HEAD
        sprocs = list(self.client.QueryStoredProcedures(
            self.GetDocumentCollectionLink(db, collection, is_name_based),
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters':[
                    { 'name':'@id', 'value':sproc_definition['id'] }
                ]
            }))
        self.assert_(sprocs)
        # replace sproc
        change_sproc = sproc.copy()
        sproc['body'] = 'function() {var x = 20;}'
        replaced_sproc = self.client.ReplaceStoredProcedure(self.GetStoredProcedureLink(db, collection, change_sproc, is_name_based),
                                                       sproc)
=======
        sprocs = list(collection.scripts.query_stored_procedures(
                query='SELECT * FROM root r WHERE r.id=@id',
                parameters=[
                    {'name': '@id', 'value': sproc_definition['id']}
                ]
        ))
        self.assertIsNotNone(sprocs)
        # replace sproc
        change_sproc = sproc.copy()
        sproc['body'] = 'function() {var x = 20;}'
        replaced_sproc = collection.scripts.replace_stored_procedure(sproc=change_sproc['id'], body=sproc)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
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
<<<<<<< HEAD
        sproc = self.client.ReadStoredProcedure(self.GetStoredProcedureLink(db, collection, replaced_sproc, is_name_based))
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
        db = self.databseForTest
        
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
        upserted_sproc = self.client.UpsertStoredProcedure(self.GetDocumentCollectionLink(db, collection, is_name_based),
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
        created_db = self.databseForTest

        created_collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
=======
        sproc = collection.scripts.get_stored_procedure(replaced_sproc['id'])
        self.assertEqual(replaced_sproc['id'], sproc['id'])
        # delete sproc
        collection.scripts.delete_stored_procedure(replaced_sproc['id'])
        # read sprocs after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           collection.scripts.get_stored_procedure,
                                           replaced_sproc['id'])

    def test_script_logging_execute_stored_procedure(self):
        created_db = self.databaseForTest

        created_collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

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
<<<<<<< HEAD
            }

        created_sproc = self.client.CreateStoredProcedure(self.GetDocumentCollectionLink(created_db, created_collection), sproc)

        result = self.client.ExecuteStoredProcedure(self.GetStoredProcedureLink(created_db, created_collection, created_sproc), None)

        self.assertEqual(result, 'Success!')
        self.assertFalse(HttpHeaders.ScriptLogResults in self.client.last_response_headers)

        options = { 'enableScriptLogging': True }
        result = self.client.ExecuteStoredProcedure(self.GetStoredProcedureLink(created_db, created_collection, created_sproc), None, options)

        self.assertEqual(result, 'Success!')
        self.assertEqual(urllib.quote('The value of x is 1.'), self.client.last_response_headers.get(HttpHeaders.ScriptLogResults))

        options = { 'enableScriptLogging': False }
        result = self.client.ExecuteStoredProcedure(self.GetStoredProcedureLink(created_db, created_collection, created_sproc), None, options)

        self.assertEqual(result, 'Success!')
        self.assertFalse(HttpHeaders.ScriptLogResults in self.client.last_response_headers)

    def test_collection_indexing_policy_self_link(self):
        self._test_collection_indexing_policy(False)

    def test_collection_indexing_policy_name_based(self):
        self._test_collection_indexing_policy(True)

    def _test_collection_indexing_policy(self, is_name_based):
        # create database
        db = self.databseForTest
        # create collection
        collection = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based),
            { 'id': 'test_collection_indexing_policy default policy' + str(uuid.uuid4()) })
        self.assertEqual(collection['indexingPolicy']['indexingMode'],
                         documents.IndexingMode.Consistent,
                         'default indexing mode should be consistent')
        lazy_collection_definition = {
            'id': 'test_collection_indexing_policy lazy collection ' + str(uuid.uuid4()),
            'indexingPolicy': {
                'indexingMode': documents.IndexingMode.Lazy
            }
        }
        self.client.DeleteContainer(self.GetDocumentCollectionLink(db, collection, is_name_based))
        lazy_collection = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based),
            lazy_collection_definition)
        self.assertEqual(lazy_collection['indexingPolicy']['indexingMode'],
                         documents.IndexingMode.Lazy,
                         'indexing mode should be lazy')

        consistent_collection_definition = {
            'id': 'test_collection_indexing_policy consistent collection ' + str(uuid.uuid4()),
            'indexingPolicy': {
                'indexingMode': documents.IndexingMode.Consistent
            }
        }
        self.client.DeleteContainer(self.GetDocumentCollectionLink(db, lazy_collection, is_name_based))
        consistent_collection = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based), consistent_collection_definition)
        self.assertEqual(collection['indexingPolicy']['indexingMode'],
                         documents.IndexingMode.Consistent,
                         'indexing mode should be consistent')
        collection_definition = {
            'id': 'CollectionWithIndexingPolicy',
            'indexingPolicy': {
=======
        }

        created_sproc = created_collection.scripts.create_stored_procedure(body=sproc)

        result = created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            partition_key=1
        )

        self.assertEqual(result, 'Success!')
        self.assertFalse(HttpHeaders.ScriptLogResults in created_collection.scripts.client_connection.last_response_headers)

        result = created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            enable_script_logging=True,
            partition_key=1
        )

        self.assertEqual(result, 'Success!')
        self.assertEqual(urllib.quote('The value of x is 1.'),
                         created_collection.scripts.client_connection.last_response_headers.get(HttpHeaders.ScriptLogResults))

        result = created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            enable_script_logging=False,
            partition_key=1
        )

        self.assertEqual(result, 'Success!')
        self.assertFalse(HttpHeaders.ScriptLogResults in created_collection.scripts.client_connection.last_response_headers)

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
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
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
<<<<<<< HEAD
            }
        }
        self.client.DeleteContainer(self.GetDocumentCollectionLink(db, consistent_collection, is_name_based))
        collection_with_indexing_policy = self.client.CreateContainer(self.GetDatabaseLink(db, is_name_based), collection_definition)
        self.assertEqual(1,
                         len(collection_with_indexing_policy['indexingPolicy']['includedPaths']),
                         'Unexpected includedPaths length')
        self.assertEqual(2,
                         len(collection_with_indexing_policy['indexingPolicy']['excludedPaths']),
                         'Unexpected excluded path count')
        self.client.DeleteContainer(self.GetDocumentCollectionLink(db, collection_with_indexing_policy, is_name_based))

    def test_create_default_indexing_policy_self_link(self):
        self._test_create_default_indexing_policy(False)

    def test_create_default_indexing_policy_name_based(self):
        self._test_create_default_indexing_policy(True)
        
    def _test_create_default_indexing_policy(self, is_name_based):
        # create database
        db = self.databseForTest

        # no indexing policy specified
        collection = self.client.CreateContainer(self.GetDatabaseLink(db, is_name_based),
                                                 {'id': 'test_create_default_indexing_policy TestCreateDefaultPolicy01' + str(uuid.uuid4())})
        self._check_default_indexing_policy_paths(collection['indexingPolicy'])
        self.client.DeleteContainer(collection['_self'])

        # partial policy specified
        collection = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based),
            {
                'id': 'test_create_default_indexing_policy TestCreateDefaultPolicy02' + str(uuid.uuid4()),
                'indexingPolicy': {
                    'indexingMode': documents.IndexingMode.Lazy, 'automatic': True
                }
            })
        self._check_default_indexing_policy_paths(collection['indexingPolicy'])
        self.client.DeleteContainer(collection['_self'])

        # default policy
        collection = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based),
            {
                'id': 'test_create_default_indexing_policy TestCreateDefaultPolicy03' + str(uuid.uuid4()),
                'indexingPolicy': { }
            })
        self._check_default_indexing_policy_paths(collection['indexingPolicy'])
        self.client.DeleteContainer(collection['_self'])

        # missing indexes
        collection = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based),
            {
                'id': 'test_create_default_indexing_policy TestCreateDefaultPolicy04' + str(uuid.uuid4()),
                'indexingPolicy': {
=======
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
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
                    'includedPaths': [
                        {
                            'path': '/*'
                        }
                    ]
<<<<<<< HEAD
                }
            })
        self._check_default_indexing_policy_paths(collection['indexingPolicy'])
        self.client.DeleteContainer(collection['_self'])

        # missing precision
        collection = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based),
            {
                'id': 'test_create_default_indexing_policy TestCreateDefaultPolicy05' + str(uuid.uuid4()),
                'indexingPolicy': {
=======
                },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        self._check_default_indexing_policy_paths(collection.properties['indexingPolicy'])
        db.delete_container(container=collection)

        # missing precision
        collection = db.create_container(
            id='test_create_default_indexing_policy TestCreateDefaultPolicy05' + str(uuid.uuid4()),
            indexing_policy={
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
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
<<<<<<< HEAD
                }
            })
        self._check_default_indexing_policy_paths(collection['indexingPolicy'])
        self.client.DeleteContainer(collection['_self'])
=======
                },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        self._check_default_indexing_policy_paths(collection.properties['indexingPolicy'])
        db.delete_container(container=collection)

    def test_create_indexing_policy_with_composite_and_spatial_indexes(self):
        # create database
        db = self.databaseForTest

        indexing_policy = {
            "spatialIndexes": [
                {
                    "path": "/path0/*",
                    "types": [
                        "Point",
                        "LineString",
                        "Polygon"
                    ]
                },
                {
                    "path": "/path1/*",
                    "types": [
                        "LineString",
                        "Polygon",
                        "MultiPolygon"
                    ]
                }
            ],
            "compositeIndexes": [
                [
                    {
                        "path": "/path1",
                        "order": "ascending"
                    },
                    {
                        "path": "/path2",
                        "order": "descending"
                    },
                    {
                        "path": "/path3",
                        "order": "ascending"
                    }
                ],
                [
                    {
                        "path": "/path4",
                        "order": "ascending"
                    },
                    {
                        "path": "/path5",
                        "order": "descending"
                    },
                    {
                        "path": "/path6",
                        "order": "ascending"
                    }
                ]
            ]
        }

        created_container = db.create_container(
            id='composite_index_spatial_index' + str(uuid.uuid4()),
            indexing_policy=indexing_policy,
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        read_indexing_policy = created_container.properties['indexingPolicy']
        self.assertListEqual(indexing_policy['spatialIndexes'], read_indexing_policy['spatialIndexes'])
        self.assertListEqual(indexing_policy['compositeIndexes'], read_indexing_policy['compositeIndexes'])
        db.delete_container(container=created_container)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

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
<<<<<<< HEAD
                              if included_path['path'] == '/*'])
=======
                                          if included_path['path'] == '/*'])
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(0, len(root_included_path['indexes']))
        print(root_included_path['indexes'])

    def test_client_request_timeout(self):
        connection_policy = documents.ConnectionPolicy()
<<<<<<< HEAD
        # making timeout 1 ms to make sure it will throw
        connection_policy.RequestTimeout = 1
        with self.assertRaises(Exception):
            # client does a getDatabaseAccount on initialization, which will time out
            cosmos_client.CosmosClient(CRUDTests.host,
                                                {'masterKey': CRUDTests.masterKey},
                                                connection_policy)

    def test_query_iterable_functionality(self):
        def __CreateResources(client):
            """Creates resources for this test.

            :Parameters:
                - `client`: cosmos_client.CosmosClient
=======
        # making timeout 0 ms to make sure it will throw
        connection_policy.RequestTimeout = 0
        with self.assertRaises(Exception):
            # client does a getDatabaseAccount on initialization, which will time out
            cosmos_client.CosmosClient(CRUDTests.host, {'masterKey': CRUDTests.masterKey}, "Session", connection_policy)

    def test_query_iterable_functionality(self):
        def __create_resources(client):
            """Creates resources for this test.

            :Parameters:
                - `client`: cosmos_client_connection.CosmosClientConnection
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

            :Returns:
                dict

            """
<<<<<<< HEAD
            db = self.databseForTest
            collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
            doc1 = client.CreateItem(
                collection['_self'],
                { 'id': 'doc1', 'prop1': 'value1'})
            doc2 = client.CreateItem(
                collection['_self'],
                { 'id': 'doc2', 'prop1': 'value2'})
            doc3 = client.CreateItem(
                collection['_self'],
                { 'id': 'doc3', 'prop1': 'value3'})
=======
            collection = self.configs.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
            doc1 = collection.create_item(body={'id': 'doc1', 'prop1': 'value1'})
            doc2 = collection.create_item(body={'id': 'doc2', 'prop1': 'value2'})
            doc3 = collection.create_item(body={'id': 'doc3', 'prop1': 'value3'})
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
            resources = {
                'coll': collection,
                'doc1': doc1,
                'doc2': doc2,
                'doc3': doc3
            }
            return resources

        # Validate QueryIterable by converting it to a list.
<<<<<<< HEAD
        resources = __CreateResources(self.client)
        results = self.client.ReadItems(resources['coll']['_self'],
                                       {'maxItemCount':2})
=======
        resources = __create_resources(self.client)
        results = resources['coll'].list_item_properties(max_item_count=2)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        docs = list(iter(results))
        self.assertEqual(3,
                         len(docs),
                         'QueryIterable should return all documents' +
                         ' using continuation')
        self.assertEqual(resources['doc1']['id'], docs[0]['id'])
        self.assertEqual(resources['doc2']['id'], docs[1]['id'])
        self.assertEqual(resources['doc3']['id'], docs[2]['id'])

        # Validate QueryIterable iterator with 'for'.
<<<<<<< HEAD
=======
        results = resources['coll'].list_item_properties(max_item_count=2)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
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
<<<<<<< HEAD
        results = self.client.ReadItems(resources['coll']['_self'],
                                       {'maxItemCount':2})
=======
        results = resources['coll'].list_item_properties(max_item_count=2)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
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

<<<<<<< HEAD
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
            'body': "function() { }", # trigger already stringified
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
                - `client`: cosmos_client.CosmosClient
=======
    def test_trigger_functionality(self):
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

        def __CreateTriggers(collection, triggers):
            """Creates triggers.

            :Parameters:
                - `client`: cosmos_client_connection.CosmosClientConnection
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
                - `collection`: dict

            """
            for trigger_i in triggers:
<<<<<<< HEAD
                trigger = client.CreateTrigger(self.GetDocumentCollectionLink(database, collection, is_name_based),
                                               trigger_i)
=======
                trigger = collection.scripts.create_trigger(body=trigger_i)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
                for property in trigger_i:
                    self.assertEqual(
                        trigger[property],
                        trigger_i[property],
                        'property {property} should match'.format(property=property))

        # create database
<<<<<<< HEAD
        db = self.databseForTest
        # create collections
        collection1 = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based), { 'id': 'test_trigger_functionality 1 ' + str(uuid.uuid4()) })
        collection2 = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based), { 'id': 'test_trigger_functionality 2 ' + str(uuid.uuid4()) })
        collection3 = self.client.CreateContainer(
            self.GetDatabaseLink(db, is_name_based), { 'id': 'test_trigger_functionality 3 ' + str(uuid.uuid4()) })
        # create triggers
        __CreateTriggers(self.client, db, collection1, triggers_in_collection1, is_name_based)
        __CreateTriggers(self.client, db, collection2, triggers_in_collection2, is_name_based)
        __CreateTriggers(self.client, db, collection3, triggers_in_collection3, is_name_based)
        # create document
        triggers_1 = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection1, is_name_based)))
        self.assertEqual(len(triggers_1), 3)
        document_1_1 = self.client.CreateItem(self.GetDocumentCollectionLink(db, collection1, is_name_based),
                                             { 'id': 'doc1',
                                               'key': 'value' },
                                             { 'preTriggerInclude': 't1' })
        self.assertEqual(document_1_1['id'],
                         'DOC1t1',
                         'id should be capitalized')
        document_1_2 = self.client.CreateItem(
            self.GetDocumentCollectionLink(db, collection1, is_name_based),
            { 'id': 'testing post trigger' },
            { 'postTriggerInclude': 'response1',
              'preTriggerInclude': 't1' })
        self.assertEqual(document_1_2['id'], 'TESTING POST TRIGGERt1')
        document_1_3 = self.client.CreateItem(self.GetDocumentCollectionLink(db, collection1, is_name_based),
                                             { 'id': 'responseheaders' },
                                             { 'preTriggerInclude': 't1' })
        self.assertEqual(document_1_3['id'], "RESPONSEHEADERSt1")

        triggers_2 = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection2, is_name_based)))
        self.assertEqual(len(triggers_2), 2)
        document_2_1 = self.client.CreateItem(self.GetDocumentCollectionLink(db, collection2, is_name_based),
                                             { 'id': 'doc2',
                                               'key2': 'value2' },
                                             { 'preTriggerInclude': 't2' })
        self.assertEqual(document_2_1['id'],
                         'doc2',
                         'id shouldn\'t change')
        document_2_2 = self.client.CreateItem(self.GetDocumentCollectionLink(db, collection2, is_name_based),
                                             { 'id': 'Doc3',
                                               'prop': 'empty' },
                                             { 'preTriggerInclude': 't3' })
        self.assertEqual(document_2_2['id'], 'doc3t3')

        triggers_3 = list(self.client.ReadTriggers(self.GetDocumentCollectionLink(db, collection3, is_name_based)))
        self.assertEqual(len(triggers_3), 1)
        with self.assertRaises(Exception):
            self.client.CreateItem(self.GetDocumentCollectionLink(db, collection3, is_name_based),
                                  { 'id': 'Docoptype' },
                                  { 'postTriggerInclude': 'triggerOpType' })

        self.client.DeleteContainer(collection1['_self'])
        self.client.DeleteContainer(collection2['_self'])
        self.client.DeleteContainer(collection3['_self'])

    def test_stored_procedure_functionality_self_link(self):
        self._test_stored_procedure_functionality(False)

    def test_stored_procedure_functionality_name_based(self):
        self._test_stored_procedure_functionality(True)
        
    def _test_stored_procedure_functionality(self, is_name_based):
        # create database
        db = self.databseForTest
        # create collection
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
=======
        db = self.databaseForTest
        # create collections
        pkd = PartitionKey(path='/id', kind='Hash')
        collection1 = db.create_container(id='test_trigger_functionality 1 ' + str(uuid.uuid4()), partition_key=PartitionKey(path='/key', kind='Hash'))
        collection2 = db.create_container(id='test_trigger_functionality 2 ' + str(uuid.uuid4()), partition_key=PartitionKey(path='/key', kind='Hash'))
        collection3 = db.create_container(id='test_trigger_functionality 3 ' + str(uuid.uuid4()), partition_key=PartitionKey(path='/key', kind='Hash'))
        # create triggers
        __CreateTriggers(collection1, triggers_in_collection1)
        __CreateTriggers(collection2, triggers_in_collection2)
        __CreateTriggers(collection3, triggers_in_collection3)
        # create document
        triggers_1 = list(collection1.scripts.list_triggers())
        self.assertEqual(len(triggers_1), 3)
        document_1_1 = collection1.create_item(
            body={'id': 'doc1',
                  'key': 'value'},
            pre_trigger_include='t1'
        )
        self.assertEqual(document_1_1['id'],
                         'DOC1t1',
                         'id should be capitalized')

        document_1_2 = collection1.create_item(
            body={'id': 'testing post trigger', 'key': 'value'},
            pre_trigger_include='t1',
            post_trigger_include='response1',
        )
        self.assertEqual(document_1_2['id'], 'TESTING POST TRIGGERt1')

        document_1_3 = collection1.create_item(
            body={'id': 'responseheaders', 'key': 'value'},
            pre_trigger_include='t1'
        )
        self.assertEqual(document_1_3['id'], "RESPONSEHEADERSt1")

        triggers_2 = list(collection2.scripts.list_triggers())
        self.assertEqual(len(triggers_2), 2)
        document_2_1 = collection2.create_item(
            body={'id': 'doc2',
                  'key': 'value2'},
            pre_trigger_include='t2'
        )
        self.assertEqual(document_2_1['id'],
                         'doc2',
                         'id shouldn\'t change')
        document_2_2 = collection2.create_item(
            body={'id': 'Doc3',
                  'prop': 'empty',
                  'key': 'value2'},
            pre_trigger_include='t3')
        self.assertEqual(document_2_2['id'], 'doc3t3')

        triggers_3 = list(collection3.scripts.list_triggers())
        self.assertEqual(len(triggers_3), 1)
        with self.assertRaises(Exception):
            collection3.create_item(
                body={'id': 'Docoptype', 'key': 'value2'},
                post_trigger_include='triggerOpType'
            )

        db.delete_container(collection1)
        db.delete_container(collection2)
        db.delete_container(collection3)

    def test_stored_procedure_functionality(self):
        # create database
        db = self.databaseForTest
        # create collection
        collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

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

<<<<<<< HEAD
        retrieved_sproc = self.client.CreateStoredProcedure(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                                       sproc1)
        result = self.client.ExecuteStoredProcedure(self.GetStoredProcedureLink(db, collection, retrieved_sproc, is_name_based),
                                               None)
=======
        retrieved_sproc = collection.scripts.create_stored_procedure(body=sproc1)
        result = collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc['id'],
            partition_key=1
        )
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
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
<<<<<<< HEAD
        retrieved_sproc2 = self.client.CreateStoredProcedure(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                                        sproc2)
        result = self.client.ExecuteStoredProcedure(self.GetStoredProcedureLink(db, collection, retrieved_sproc2, is_name_based),
                                               None)
=======
        retrieved_sproc2 = collection.scripts.create_stored_procedure(body=sproc2)
        result = collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc2['id'],
            partition_key=1
        )
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
        self.assertEqual(int(result), 123456789)
        sproc3 = {
            'id': 'storedProcedure3' + str(uuid.uuid4()),
            'body': (
                'function (input) {' +
<<<<<<< HEAD
                    '  getContext().getResponse().setBody(' +
                    '      \'a\' + input.temp);' +
                '}')
        }
        retrieved_sproc3 = self.client.CreateStoredProcedure(self.GetDocumentCollectionLink(db, collection, is_name_based),
                                                        sproc3)
        result = self.client.ExecuteStoredProcedure(self.GetStoredProcedureLink(db, collection, retrieved_sproc3, is_name_based),
                                               {'temp': 'so'})
        self.assertEqual(result, 'aso')

    def __ValidateOfferResponseBody(self, offer, expected_coll_link, expected_offer_type):
        self.assert_(offer.get('id'), 'Id cannot be null.')
        self.assert_(offer.get('_rid'), 'Resource Id (Rid) cannot be null.')
        self.assert_(offer.get('_self'), 'Self Link cannot be null.')
        self.assert_(offer.get('resource'), 'Resource Link cannot be null.')
        self.assertTrue(offer['_self'].find(offer['id']) != -1,
                        'Offer id not contained in offer self link.')
        self.assertEqual(expected_coll_link.strip('/'), offer['resource'].strip('/'))
        if (expected_offer_type):
            self.assertEqual(expected_offer_type, offer.get('offerType'))

    def test_offer_read_and_query(self):
        # Create database.
        db = self.databseForTest

        offers = list(self.client.ReadOffers())
        initial_count = len(offers)

        # Create collection.
        collection = self.client.CreateContainer(db['_self'], { 'id': 'test_offer_read_and_query ' + str(uuid.uuid4()) })
        offers = list(self.client.ReadOffers())
        self.assertEqual(initial_count+1, len(offers))

        offers = self.GetCollectionOffers(self.client, collection['_rid'])
        
        self.assertEqual(1, len(offers))
        expected_offer = offers[0]
        self.__ValidateOfferResponseBody(expected_offer, collection.get('_self'), None)
        # Read the offer.
        read_offer = self.client.ReadOffer(expected_offer.get('_self'))
        self.__ValidateOfferResponseBody(read_offer, collection.get('_self'), expected_offer.get('offerType'))
        # Check if the read resource is what we expected.
        self.assertEqual(expected_offer.get('id'), read_offer.get('id'))
        self.assertEqual(expected_offer.get('_rid'), read_offer.get('_rid'))
        self.assertEqual(expected_offer.get('_self'), read_offer.get('_self'))
        self.assertEqual(expected_offer.get('resource'), read_offer.get('resource'))
        # Query for the offer.

        offers = list(self.client.QueryOffers(
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    { 'name': '@id', 'value': expected_offer['id']}
                ]
            }))
        
        self.assertEqual(1, len(offers))
        query_one_offer = offers[0]
        self.__ValidateOfferResponseBody(query_one_offer, collection.get('_self'), expected_offer.get('offerType'))
        # Check if the query result is what we expected.
        self.assertEqual(expected_offer.get('id'), query_one_offer.get('id'))
        self.assertEqual(expected_offer.get('_rid'), query_one_offer.get('_rid'))
        self.assertEqual(expected_offer.get('_self'), query_one_offer.get('_self'))
        self.assertEqual(expected_offer.get('resource'), query_one_offer.get('resource'))
        # Expects an exception when reading offer with bad offer link.
        self.__AssertHTTPFailureWithStatus(StatusCodes.BAD_REQUEST, self.client.ReadOffer, expected_offer.get('_self')[:-1] + 'x')
        # Now delete the collection.
        self.client.DeleteContainer(collection.get('_self'))
        # Reading fails.
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND, self.client.ReadOffer, expected_offer.get('_self'))
        # Read feed now returns 0 results.
        offers = list(self.client.ReadOffers())
        self.assertEqual(initial_count, len(offers))

    def test_offer_replace(self):
        # Create database.
        db = self.databseForTest
        # Create collection.
        collection = self.configs.create_single_partition_collection_if_not_exist(self.client)
        offers = self.GetCollectionOffers(self.client, collection['_rid'])
        self.assertEqual(1, len(offers))
        expected_offer = offers[0]
        self.__ValidateOfferResponseBody(expected_offer, collection.get('_self'), None)
        # Replace the offer.
        offer_to_replace = dict(expected_offer)
        offer_to_replace['content']['offerThroughput'] += 100
        replaced_offer = self.client.ReplaceOffer(offer_to_replace['_self'], offer_to_replace)
        self.__ValidateOfferResponseBody(replaced_offer, collection.get('_self'), None)
        # Check if the replaced offer is what we expect.
        self.assertEqual(offer_to_replace.get('id'), replaced_offer.get('id'))
        self.assertEqual(offer_to_replace.get('_rid'), replaced_offer.get('_rid'))
        self.assertEqual(offer_to_replace.get('_self'), replaced_offer.get('_self'))
        self.assertEqual(offer_to_replace.get('resource'), replaced_offer.get('resource'))
        self.assertEqual(offer_to_replace.get('content').get('offerThroughput'), replaced_offer.get('content').get('offerThroughput'))
        # Expects an exception when replacing an offer with bad id.
        offer_to_replace_bad_id = dict(offer_to_replace)
        offer_to_replace_bad_id['_rid'] = 'NotAllowed'
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST, self.client.ReplaceOffer, offer_to_replace_bad_id['_self'], offer_to_replace_bad_id)
        # Expects an exception when replacing an offer with bad rid.
        offer_to_replace_bad_rid = dict(offer_to_replace)
        offer_to_replace_bad_rid['_rid'] = 'InvalidRid'
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST, self.client.ReplaceOffer, offer_to_replace_bad_rid['_self'], offer_to_replace_bad_rid)
        # Expects an exception when replaceing an offer with null id and rid.
        offer_to_replace_null_ids = dict(offer_to_replace)
        offer_to_replace_null_ids['id'] = None
        offer_to_replace_null_ids['_rid'] = None
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST, self.client.ReplaceOffer, offer_to_replace_null_ids['_self'], offer_to_replace_null_ids)

    def test_collection_with_offer_type(self):
        # create database
        created_db = self.databseForTest

        # create a collection
        offers = list(self.client.ReadOffers())
        before_offers_count = len(offers)
        
        collection_definition = { 'id': 'test_collection_with_offer_type ' + str(uuid.uuid4()) }
        collection = self.client.CreateContainer(created_db['_self'],
                                             collection_definition,
                                             {
                                                 'offerType': 'S2'
                                             })
        offers = list(self.client.ReadOffers())
        self.assertEqual(before_offers_count + 1, len(offers))

        offers = self.GetCollectionOffers(self.client, collection['_rid'])
        
        self.assertEqual(1, len(offers))
        expected_offer = offers[0]

        # We should have an offer of type S2.
        self.__ValidateOfferResponseBody(expected_offer, collection.get('_self'), 'S2')
        self.client.DeleteContainer(collection['_self'])

    def test_database_account_functionality(self):
        # Validate database account functionality.
        database_account = self.client.GetDatabaseAccount()
        self.assertEqual(database_account.DatabasesLink, '/dbs/')
        self.assertEqual(database_account.MediaLink, '/media/')
        if (HttpHeaders.MaxMediaStorageUsageInMB in
            self.client.last_response_headers):
            self.assertEqual(
                database_account.MaxMediaStorageUsageInMB,
                self.client.last_response_headers[
                    HttpHeaders.MaxMediaStorageUsageInMB])
        if (HttpHeaders.CurrentMediaStorageUsageInMB in
            self.client.last_response_headers):
            self.assertEqual(
                database_account.CurrentMediaStorageUsageInMB,
                self.client.last_response_headers[
                    HttpHeaders.
                    CurrentMediaStorageUsageInMB])
        self.assertTrue(
            database_account.ConsistencyPolicy['defaultConsistencyLevel']
            != None)

    def test_index_progress_headers_self_link(self):
        self._test_index_progress_headers(False)

    def test_index_progress_headers_name_based(self):
        self._test_index_progress_headers(True)
        
    def _test_index_progress_headers(self, is_name_based):
        created_db = self.databseForTest
        consistent_coll = self.client.CreateContainer(self.GetDatabaseLink(created_db, is_name_based), { 'id': 'test_index_progress_headers consistent_coll ' + str(uuid.uuid4()) })
        self.client.ReadContainer(self.GetDocumentCollectionLink(created_db, consistent_coll, is_name_based))
        self.assertFalse(HttpHeaders.LazyIndexingProgress in self.client.last_response_headers)
        self.assertTrue(HttpHeaders.IndexTransformationProgress in self.client.last_response_headers)
        lazy_coll = self.client.CreateContainer(self.GetDatabaseLink(created_db, is_name_based),
            {
                'id': 'test_index_progress_headers lazy_coll ' + str(uuid.uuid4()),
                'indexingPolicy': { 'indexingMode' : documents.IndexingMode.Lazy }
            })
        self.client.ReadContainer(self.GetDocumentCollectionLink(created_db, lazy_coll, is_name_based))
        self.assertTrue(HttpHeaders.LazyIndexingProgress in self.client.last_response_headers)
        self.assertTrue(HttpHeaders.IndexTransformationProgress in self.client.last_response_headers)
        none_coll = self.client.CreateContainer(self.GetDatabaseLink(created_db, is_name_based),
            {
                'id': 'test_index_progress_headers none_coll ' + str(uuid.uuid4()),
                'indexingPolicy': { 'indexingMode': documents.IndexingMode.NoIndex, 'automatic': False }
            })
        self.client.ReadContainer(self.GetDocumentCollectionLink(created_db, none_coll, is_name_based))
        self.assertFalse(HttpHeaders.LazyIndexingProgress in self.client.last_response_headers)
        self.assertTrue(HttpHeaders.IndexTransformationProgress in self.client.last_response_headers)

        self.client.DeleteContainer(consistent_coll['_self'])
        self.client.DeleteContainer(lazy_coll['_self'])
        self.client.DeleteContainer(none_coll['_self'])

    # To run this test, please provide your own CA certs file or download one from
    #     http://curl.haxx.se/docs/caextract.html
    #
    # def test_ssl_connection(self):
    #     connection_policy = documents.ConnectionPolicy()
    #     connection_policy.SSLConfiguration = documents.SSLConfiguration()
    #     connection_policy.SSLConfiguration.SSLCaCerts = './cacert.pem'
    #     client = cosmos_client.CosmosClient(CRUDTests.host, {'masterKey': CRUDTests.masterKey}, connection_policy)
    #     # Read databases after creation.
    #     databases = list(client.ReadDatabases())

    def test_id_validation(self):
        # Id shouldn't end with space.
        database_definition = { 'id': 'id_with_space ' }
        try:
            self.client.CreateDatabase(database_definition)
=======
                '  getContext().getResponse().setBody(' +
                '      \'a\' + input.temp);' +
                '}')
        }
        retrieved_sproc3 = collection.scripts.create_stored_procedure(body=sproc3)
        result = collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc3['id'],
            params={'temp': 'so'},
            partition_key=1
        )
        self.assertEqual(result, 'aso')

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

    def test_offer_replace(self):
        # Create database.
        db = self.databaseForTest
        # Create collection.
        collection = self.configs.create_multi_partition_collection_if_not_exist(self.client)
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
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id ends with a space.', e.args[0])
        # Id shouldn't contain '/'.
<<<<<<< HEAD
        database_definition = { 'id': 'id_with_illegal/_char' }
        try:
            self.client.CreateDatabase(database_definition)
=======

        try:
            self.client.create_database(id='id_with_illegal/_char')
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])
        # Id shouldn't contain '\\'.
<<<<<<< HEAD
        database_definition = { 'id': 'id_with_illegal\\_char' }
        try:
            self.client.CreateDatabase(database_definition)
=======

        try:
            self.client.create_database(id='id_with_illegal\\_char')
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])
        # Id shouldn't contain '?'.
<<<<<<< HEAD
        database_definition = { 'id': 'id_with_illegal?_char' }
        try:
            self.client.CreateDatabase(database_definition)
=======

        try:
            self.client.create_database(id='id_with_illegal?_char')
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])
        # Id shouldn't contain '#'.
<<<<<<< HEAD
        database_definition = { 'id': 'id_with_illegal#_char' }
        try:
            self.client.CreateDatabase(database_definition)
=======

        try:
            self.client.create_database(id='id_with_illegal#_char')
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])

        # Id can begin with space
<<<<<<< HEAD
        database_definition = { 'id': ' id_begin_space' }
        db = self.client.CreateDatabase(database_definition)
        self.assertTrue(True)

        self.client.DeleteDatabase(db['_self'])

    def test_id_case_validation(self):
        # create database
        created_db = self.databseForTest

        uuid_string = str(uuid.uuid4())
        # pascalCase
        collection_definition1 = { 'id': 'sampleCollection ' + uuid_string }

        # CamelCase
        collection_definition2 = { 'id': 'SampleCollection ' + uuid_string }

        # Verify that no collections exist
        collections = list(self.client.ReadContainers(self.GetDatabaseLink(created_db, True)))
        number_of_existing_collections = len(collections)
        
        # create 2 collections with different casing of IDs
        created_collection1 = self.client.CreateContainer(self.GetDatabaseLink(created_db, True),
                                                     collection_definition1)

        created_collection2 = self.client.CreateContainer(self.GetDatabaseLink(created_db, True),
                                                     collection_definition2)

        collections = list(self.client.ReadContainers(self.GetDatabaseLink(created_db, True)))
        
        # verify if a total of 2 collections got created
        self.assertEqual(len(collections), number_of_existing_collections + 2)
        
        # verify that collections are created with specified IDs
        self.assertEqual(collection_definition1['id'], created_collection1['id'])
        self.assertEqual(collection_definition2['id'], created_collection2['id'])

        self.client.DeleteContainer(created_collection1['_self'])
        self.client.DeleteContainer(created_collection2['_self'])

    def test_id_unicode_validation(self):
        # create database
        created_db = self.databseForTest

        # unicode chars in Hindi for Id which translates to: "Hindi is the national language of India"
        collection_definition1 = { 'id': u'हिन्दी भारत की राष्ट्रीय भाषा है' }

        # Special chars for Id
        collection_definition2 = { 'id': "!@$%^&*()-~`'_[]{}|;:,.<>" } 

        # verify that collections are created with specified IDs
        created_collection1 = self.client.CreateContainer(self.GetDatabaseLink(created_db, True),
                                                     collection_definition1)

        created_collection2 = self.client.CreateContainer(self.GetDatabaseLink(created_db, True),
                                                     collection_definition2)
        
        self.assertEqual(collection_definition1['id'], created_collection1['id'])
        self.assertEqual(collection_definition2['id'], created_collection2['id'])

        self.client.DeleteContainer(created_collection1['_self'])
        self.client.DeleteContainer(created_collection2['_self'])

    def GetDatabaseLink(self, database, is_name_based=True):
        if is_name_based:
            return 'dbs/' + database['id']
        else:
            return database['_self']

    def GetUserLink(self, database, user, is_name_based=True):
        if is_name_based:
            return self.GetDatabaseLink(database) + '/users/' + user['id']
        else:
            return user['_self']

    def GetPermissionLink(self, database, user, permission, is_name_based=True):
        if is_name_based:
            return self.GetUserLink(database, user) + '/permissions/' + permission['id']
        else:
            return permission['_self']

    def GetDocumentCollectionLink(self, database, document_collection, is_name_based=True):
        if is_name_based:
            return self.GetDatabaseLink(database) + '/colls/' + document_collection['id']
        else:
            return document_collection['_self']

    def GetDocumentLink(self, database, document_collection, document, is_name_based=True):
        if is_name_based:
            return self.GetDocumentCollectionLink(database, document_collection) + '/docs/' + document['id']
        else:
            return document['_self']

    def GetAttachmentLink(self, database, document_collection, document, attachment, is_name_based=True):
        if is_name_based:
            return self.GetDocumentLink(database, document_collection, document) + '/attachments/' + attachment['id']
        else:
            return attachment['_self']

    def GetTriggerLink(self, database, document_collection, trigger, is_name_based=True):
        if is_name_based:
            return self.GetDocumentCollectionLink(database, document_collection) + '/triggers/' + trigger['id']
        else:
            return trigger['_self']

    def GetUserDefinedFunctionLink(self, database, document_collection, user_defined_function, is_name_based=True):
        if is_name_based:
            return self.GetDocumentCollectionLink(database, document_collection) + '/udfs/' + user_defined_function['id']
        else:
            return user_defined_function['_self']

    def GetStoredProcedureLink(self, database, document_collection, stored_procedure, is_name_based=True):
        if is_name_based:
            return self.GetDocumentCollectionLink(database, document_collection) + '/sprocs/' + stored_procedure['id']
        else:
            return stored_procedure['_self']

    def GetConflictLink(self, database, document_collection, conflict, is_name_based=True):
        if is_name_based:
            return self.GetDocumentCollectionLink(database, document_collection) + '/conflicts/' + conflict['id']
        else:
            return conflict['_self']

    def GetCollectionOffers(self, client, collection_rid):
        return list(client.QueryOffers(
            {
                'query': 'SELECT * FROM root r WHERE r.offerResourceId=@offerResourceId',
                'parameters': [
                    { 'name': '@offerResourceId', 'value': collection_rid}
                ]
            }))
=======
        db = self.client.create_database(id=' id_begin_space')
        self.assertTrue(True)

        self.client.delete_database(database=db)

    def test_id_case_validation(self):
        # create database
        created_db = self.databaseForTest

        uuid_string = str(uuid.uuid4())
        collection_id1 = 'sampleCollection ' + uuid_string
        collection_id2 = 'SampleCollection ' + uuid_string

        # Verify that no collections exist
        collections = list(created_db.list_container_properties())
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

        collections = list(created_db.list_container_properties())

        # verify if a total of 2 collections got created
        self.assertEqual(len(collections), number_of_existing_collections + 2)

        # verify that collections are created with specified IDs
        self.assertEqual(collection_id1, created_collection1.id)
        self.assertEqual(collection_id2, created_collection2.id)

        created_db.delete_container(created_collection1)
        created_db.delete_container(created_collection2)

    #TODO: fix test
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

        created_db.client_connection.DeleteContainer(created_collection1.properties['_self'])
        created_db.client_connection.DeleteContainer(created_collection2.properties['_self'])

    def test_get_resource_with_dictionary_and_object(self):
        created_db = self.databaseForTest

        # read database with id
        read_db = self.client.get_database(created_db.id)
        self.assertEquals(read_db.id, created_db.id)

        # read database with instance
        read_db = self.client.get_database(created_db)
        self.assertEquals(read_db.id, created_db.id)

        # read database with properties
        read_db = self.client.get_database(created_db.properties)
        self.assertEquals(read_db.id, created_db.id)

        created_container = self.configs.create_multi_partition_collection_if_not_exist(self.client)

        # read container with id
        read_container = created_db.get_container(created_container.id)
        self.assertEquals(read_container.id, created_container.id)

        # read container with instance
        read_container = created_db.get_container(created_container)
        self.assertEquals(read_container.id, created_container.id)

        # read container with properties
        read_container = created_db.get_container(created_container.properties)
        self.assertEquals(read_container.id, created_container.id)

        created_item = created_container.create_item({'id':'1' + str(uuid.uuid4())})

        # read item with id
        read_item = created_container.get_item(item=created_item['id'], partition_key=created_item['id'])
        self.assertEquals(read_item['id'], created_item['id'])

        # read item with properties
        read_item = created_container.get_item(item=created_item, partition_key=created_item['id'])
        self.assertEquals(read_item['id'], created_item['id'])

        created_sproc = created_container.scripts.create_stored_procedure({
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': 'function () { }'
        })

        # read sproc with id
        read_sproc = created_container.scripts.get_stored_procedure(created_sproc['id'])
        self.assertEquals(read_sproc['id'], created_sproc['id'])

        # read sproc with properties
        read_sproc = created_container.scripts.get_stored_procedure(created_sproc)
        self.assertEquals(read_sproc['id'], created_sproc['id'])

        created_trigger = created_container.scripts.create_trigger({
            'id': 'sample trigger' + str(uuid.uuid4()),
            'serverScript': 'function() {var x = 10;}',
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        })

        # read trigger with id
        read_trigger = created_container.scripts.get_trigger(created_trigger['id'])
        self.assertEquals(read_trigger['id'], created_trigger['id'])

        # read trigger with properties
        read_trigger = created_container.scripts.get_trigger(created_trigger)
        self.assertEquals(read_trigger['id'], created_trigger['id'])

        created_udf = created_container.scripts.create_user_defined_function({
            'id': 'sample udf' + str(uuid.uuid4()),
            'body': 'function() {var x = 10;}'
        })

        # read udf with id
        read_udf = created_container.scripts.get_user_defined_function(created_udf['id'])
        self.assertEquals(created_udf['id'], read_udf['id'])

        # read udf with properties
        read_udf = created_container.scripts.get_user_defined_function(created_udf)
        self.assertEquals(created_udf['id'], read_udf['id'])

        created_user = created_db.create_user({
            'id': 'user' + str(uuid.uuid4())
        })

        # read user with id
        read_user = created_db.get_user(created_user.id)
        self.assertEquals(read_user.id, created_user.id)

        # read user with instance
        read_user = created_db.get_user(created_user)
        self.assertEquals(read_user.id, created_user.id)

        # read user with properties
        read_user = created_db.get_user(created_user.properties)
        self.assertEquals(read_user.id, created_user.id)

        created_permission = created_user.create_permission({
            'id': 'all permission' + str(uuid.uuid4()),
            'permissionMode': documents.PermissionMode.All,
            'resource': created_container.container_link,
            'resourcePartitionKey': [1]
        })

        # read permission with id
        read_permission = created_user.get_permission(created_permission.id)
        self.assertEquals(read_permission.id, created_permission.id)

        # read permission with instance
        read_permission = created_user.get_permission(created_permission)
        self.assertEquals(read_permission.id, created_permission.id)

        # read permission with properties
        read_permission = created_user.get_permission(created_permission.properties)
        self.assertEquals(read_permission.id, created_permission.id)

    def _MockExecuteFunction(self, function, *args, **kwargs):
        self.last_headers.append(args[5]['headers'][HttpHeaders.PartitionKey]
                                    if HttpHeaders.PartitionKey in args[5]['headers'] else '')
        return self.OriginalExecuteFunction(function, *args, **kwargs)
>>>>>>> c7c84d8e6d22bea1a86a95ee3dd2aa9a975062ef

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True:  # raised by sys.exit(True) when tests failed
            raise
