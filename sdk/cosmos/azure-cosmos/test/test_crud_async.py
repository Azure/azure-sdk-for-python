# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) 2022 Microsoft Corporation

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
import unittest
import time
from typing import Mapping
import test_config
import urllib.parse as urllib
import uuid
import pytest
from azure.core import MatchConditions
from azure.core.exceptions import AzureError, ServiceResponseError
from azure.core.pipeline.transport import RequestsTransport, RequestsTransportResponse
import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
import azure.cosmos._base as base
from azure.cosmos.aio import CosmosClient, _retry_utility_async
from azure.cosmos.diagnostics import RecordDiagnostics
from azure.cosmos.partition_key import PartitionKey
import requests
from urllib3.util.retry import Retry

pytestmark = pytest.mark.cosmosEmulator


# IMPORTANT NOTES:
#  	Most test cases in this file create collections in your Azure Cosmos account.
#  	Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.

#  	To Run the test, replace the two member fields (masterKey and host) with values
#   associated with your Azure Cosmos account.


class TimeoutTransport(RequestsTransport):

    def __init__(self, response):
        self._response = response
        super(TimeoutTransport, self).__init__()

    async def send(self, *args, **kwargs):
        if kwargs.pop("passthrough", False):
            return super(TimeoutTransport, self).send(*args, **kwargs)

        time.sleep(5)
        if isinstance(self._response, Exception):
            raise self._response
        output = requests.Response()
        output.status_code = self._response
        response = RequestsTransportResponse(None, output)
        return response


@pytest.mark.usefixtures("teardown")
class CRUDTests(unittest.TestCase):
    """Python CRUD Tests.
    """

    last_headers = []

    async def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            await func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            self.assertEqual(inst.status_code, status_code)

    @classmethod
    async def setUpClass(cls):
        cls.client = CosmosClient(cls.host, cls.masterKey, consistency_level="Session", connection_policy=cls.connectionPolicy)
        cls.databaseForTest = await cls.client.create_database_if_not_exists(test_config._test_config.TEST_DATABASE_ID)

    async def test_database_crud(self):
        # read databases.
        databases = [database async for database in self.client.list_databases()]
        # create a database.
        before_create_databases_count = len(databases)
        database_id = str(uuid.uuid4())
        created_db = await self.client.create_database(database_id)
        self.assertEqual(created_db.id, database_id)
        # Read databases after creation.
        databases = [database async for database in self.client.list_databases()]
        self.assertEqual(len(databases),
                         before_create_databases_count + 1,
                         'create should increase the number of databases')
        # query databases.
        databases = [database async for database in self.client.query_databases(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': database_id}
            ]
        )]

        self.assertTrue(len(databases) > 0)

        # read database.
        self.client.get_database_client(created_db.id)

        # delete database.
        await self.client.delete_database(created_db.id)
        # read database after deletion
        read_db = self.client.get_database_client(created_db.id)
        await self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                                 read_db.read)

        database_proxy = await self.client.create_database_if_not_exists(id=database_id, offer_throughput=10000)
        self.assertEqual(database_id, database_proxy.id)
        self.assertEqual(10000, await database_proxy.get_throughput().offer_throughput)

        database_proxy = await self.client.create_database_if_not_exists(id=database_id, offer_throughput=9000)
        self.assertEqual(database_id, database_proxy.id)
        self.assertEqual(10000, await database_proxy.get_throughput().offer_throughput)

        await self.client.delete_database(database_id)

    @pytest.mark.skip("skipping as the TestResources subscription doesn't support this offer")
    async def test_database_level_offer_throughput(self):
        # Create a database with throughput
        offer_throughput = 1000
        database_id = str(uuid.uuid4())
        created_db = await self.client.create_database(
            id=database_id,
            offer_throughput=offer_throughput
        )
        self.assertEqual(created_db.id, database_id)

        # Verify offer throughput for database
        offer = await created_db.get_throughput()
        self.assertEqual(offer.offer_throughput, offer_throughput)

        # Update database offer throughput
        new_offer_throughput = 2000
        offer = await created_db.replace_throughput(new_offer_throughput)
        self.assertEqual(offer.offer_throughput, new_offer_throughput)
        await self.client.delete_database(created_db.id)

    async def test_sql_query_crud(self):
        # create two databases.
        db1 = await self.client.create_database('database 1' + str(uuid.uuid4()))
        db2 = await self.client.create_database('database 2' + str(uuid.uuid4()))

        # query with parameters.
        databases = [database async for database in self.client.query_databases(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': db1.id}
            ]
        )]
        self.assertEqual(1, len(databases), 'Unexpected number of query results.')

        # query without parameters.
        databases = [database async for database in self.client.query_databases(
            query='SELECT * FROM root r WHERE r.id="database non-existing"'
        )]
        self.assertEqual(0, len(databases), 'Unexpected number of query results.')

        # query with a string.
        databases = [database async for database in
                     self.client.query_databases('SELECT * FROM root r WHERE r.id="' + db2.id + '"')]  # nosec
        self.assertEqual(1, len(databases), 'Unexpected number of query results.')
        await self.client.delete_database(db1.id)
        await self.client.delete_database(db2.id)

    async def test_collection_crud(self):
        created_db = self.databaseForTest
        collections = [collection async for collection in created_db.list_containers()]
        # create a collection
        before_create_collections_count = len(collections)
        collection_id = 'test_collection_crud ' + str(uuid.uuid4())
        collection_indexing_policy = {'indexingMode': 'consistent'}
        created_recorder = RecordDiagnostics()
        created_collection = await created_db.create_container(id=collection_id,
                                                               indexing_policy=collection_indexing_policy,
                                                               partition_key=PartitionKey(path="/pk", kind="Hash"),
                                                               response_hook=created_recorder)
        self.assertEqual(collection_id, created_collection.id)
        assert isinstance(created_recorder.headers, Mapping)
        assert 'Content-Type' in created_recorder.headers
        assert isinstance(created_recorder.body, Mapping)
        assert 'id' in created_recorder.body

        created_properties = await created_collection.read()
        self.assertEqual('consistent', created_properties['indexingPolicy']['indexingMode'])

        # read collections after creation
        collections = [collection async for collection in created_db.list_containers()]
        self.assertEqual(len(collections),
                         before_create_collections_count + 1,
                         'create should increase the number of collections')
        # query collections
        collections = [collection async for collection in created_db.query_containers(

            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': collection_id}
            ]
        )]

        self.assertTrue(collections)
        # delete collection
        await created_db.delete_container(created_collection.id)
        # read collection after deletion
        created_container = created_db.get_container_client(created_collection.id)
        await self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                                 created_container.read)

        container_proxy = await created_db.create_container_if_not_exists(id=created_collection.id,
                                                                    partition_key=PartitionKey(path='/id', kind='Hash'))
        self.assertEqual(created_collection.id, container_proxy.id)
        self.assertDictEqual(PartitionKey(path='/id', kind='Hash'), container_proxy._properties['partitionKey'])

        container_proxy = await created_db.create_container_if_not_exists(id=created_collection.id,
                                                                    partition_key=created_properties['partitionKey'])
        self.assertEqual(created_container.id, container_proxy.id)
        self.assertDictEqual(PartitionKey(path='/id', kind='Hash'), container_proxy._properties['partitionKey'])

        await created_db.delete_container(created_collection.id)

    async def test_partitioned_collection(self):
        created_db = self.databaseForTest

        collection_definition = {'id': 'test_partitioned_collection ' + str(uuid.uuid4()),
                                 'partitionKey':
                                     {
                                         'paths': ['/id'],
                                         'kind': documents.PartitionKind.Hash
                                     }
                                 }

        offer_throughput = 10100
        created_collection = await created_db.create_container(id=collection_definition['id'],
                                                         partition_key=collection_definition['partitionKey'],
                                                         offer_throughput=offer_throughput)

        self.assertEqual(collection_definition.get('id'), created_collection.id)

        created_collection_properties = await created_collection.read()
        self.assertEqual(collection_definition.get('partitionKey').get('paths')[0],
                         created_collection_properties['partitionKey']['paths'][0])
        self.assertEqual(collection_definition.get('partitionKey').get('kind'),
                         created_collection_properties['partitionKey']['kind'])

        expected_offer = await created_collection.get_throughput()

        self.assertIsNotNone(expected_offer)

        self.assertEqual(expected_offer.offer_throughput, offer_throughput)

        await created_db.delete_container(created_collection.id)

    async def test_partitioned_collection_quota(self):
        created_db = self.databaseForTest

        created_collection = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION)

        retrieved_collection = created_db.get_container_client(
            container=created_collection.id
        )

        retrieved_collection_properties = await retrieved_collection.read(
            populate_partition_key_range_statistics=True,
            populate_quota_info=True)
        self.assertIsNotNone(retrieved_collection_properties.get("statistics"))
        self.assertIsNotNone(created_db.client_connection.last_response_headers.get("x-ms-resource-usage"))

    async def test_partitioned_collection_partition_key_extraction(self):
        created_db = self.databaseForTest

        collection_id = 'test_partitioned_collection_partition_key_extraction ' + str(uuid.uuid4())
        created_collection = await created_db.create_container(
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

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._MockExecuteFunction
        # create document without partition key being specified
        created_document = await created_collection.create_item(body=document_definition)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        self.assertEqual(self.last_headers[1], '["WA"]')
        del self.last_headers[:]

        self.assertEqual(created_document.get('id'), document_definition.get('id'))
        self.assertEqual(created_document.get('address').get('state'), document_definition.get('address').get('state'))

        collection_id = 'test_partitioned_collection_partition_key_extraction1 ' + str(uuid.uuid4())
        created_collection1 = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/address', kind=documents.PartitionKind.Hash)
        )

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._MockExecuteFunction
        # Create document with partitionkey not present as a leaf level property but a dict
        created_document = await created_collection1.create_item(document_definition)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        self.assertEqual(self.last_headers[1], [{}])
        del self.last_headers[:]

        collection_id = 'test_partitioned_collection_partition_key_extraction2 ' + str(uuid.uuid4())
        created_collection2 = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/address/state/city', kind=documents.PartitionKind.Hash)
        )

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._MockExecuteFunction
        # Create document with partitionkey not present in the document
        created_document = await created_collection2.create_item(document_definition)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        self.assertEqual(self.last_headers[1], [{}])
        del self.last_headers[:]

        # self.assertEqual(options['partitionKey'], documents.Undefined)

        await created_db.delete_container(created_collection.id)
        await created_db.delete_container(created_collection1.id)
        await created_db.delete_container(created_collection2.id)

    async def test_partitioned_collection_partition_key_extraction_special_chars(self):
        created_db = self.databaseForTest

        collection_id = 'test_partitioned_collection_partition_key_extraction_special_chars1 ' + str(uuid.uuid4())

        created_collection1 = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/\"level\' 1*()\"/\"le/vel2\"', kind=documents.PartitionKind.Hash)
        )
        document_definition = {'id': 'document1',
                               "level' 1*()": {"le/vel2": 'val1'}
                               }

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._MockExecuteFunction
        created_document = await created_collection1.create_item(body=document_definition)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        self.assertEqual(self.last_headers[1], '["val1"]')
        del self.last_headers[:]

        collection_id = 'test_partitioned_collection_partition_key_extraction_special_chars2 ' + str(uuid.uuid4())

        created_collection2 = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/\'level\" 1*()\'/\'le/vel2\'', kind=documents.PartitionKind.Hash)
        )

        document_definition = {'id': 'document2',
                               'level\" 1*()': {'le/vel2': 'val2'}
                               }

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._MockExecuteFunction
        # create document without partition key being specified
        created_document = await created_collection2.create_item(body=document_definition)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        self.assertEqual(self.last_headers[1], '["val2"]')
        del self.last_headers[:]

        await created_db.delete_container(created_collection1.id)
        await created_db.delete_container(created_collection2.id)

    async def test_partitioned_collection_path_parser(self):
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

    async def test_partitioned_collection_document_crud_and_query(self):
        created_db = self.databaseForTest

        created_collection = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION, PartitionKey(path="/id"))

        document_definition = {'id': 'document',
                               'key': 'value'}

        created_document = await created_collection.create_item(body=document_definition)

        self.assertEqual(created_document.get('id'), document_definition.get('id'))
        self.assertEqual(created_document.get('key'), document_definition.get('key'))

        # read document
        read_document = await created_collection.read_item(
            item=created_document.get('id'),
            partition_key=created_document.get('id')
        )

        self.assertEqual(read_document.get('id'), created_document.get('id'))
        self.assertEqual(read_document.get('key'), created_document.get('key'))

        # Read document feed doesn't require partitionKey as it's always a cross partition query
        documentlist = [document async for document in created_collection.read_all_items()]
        self.assertEqual(1, len(documentlist))

        # replace document
        document_definition['key'] = 'new value'

        replaced_document = await created_collection.replace_item(
            item=read_document,
            body=document_definition
        )

        self.assertEqual(replaced_document.get('key'), document_definition.get('key'))

        # upsert document(create scenario)
        document_definition['id'] = 'document2'
        document_definition['key'] = 'value2'

        upserted_document = await created_collection.upsert_item(body=document_definition)

        self.assertEqual(upserted_document.get('id'), document_definition.get('id'))
        self.assertEqual(upserted_document.get('key'), document_definition.get('key'))

        documentlist = [document async for document in created_collection.read_all_items()]
        self.assertEqual(2, len(documentlist))

        # delete document
        await created_collection.delete_item(item=upserted_document, partition_key=upserted_document.get('id'))

        # query document on the partition key specified in the predicate will pass even without setting enableCrossPartitionQuery or passing in the partitionKey value
        documentlist = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.id=\'' + replaced_document.get('id') + '\''  # nosec
        )]
        self.assertEqual(1, len(documentlist))

        # query document on any property other than partitionKey will fail without setting enableCrossPartitionQuery or passing in the partitionKey value
        try:
            [document async for document in created_collection.query_items(
                query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\''  # nosec
            )]
        except Exception:
            pass

        # cross partition query
        documentlist = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            enable_cross_partition_query=True
        )]

        self.assertEqual(1, len(documentlist))

        # query document by providing the partitionKey value
        documentlist = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            partition_key=replaced_document.get('id')
        )]

        self.assertEqual(1, len(documentlist))

    async def test_partitioned_collection_permissions(self):
        created_db = self.databaseForTest

        collection_id = 'test_partitioned_collection_permissions all collection' + str(uuid.uuid4())

        all_collection = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/key', kind=documents.PartitionKind.Hash)
        )

        collection_id = 'test_partitioned_collection_permissions read collection' + str(uuid.uuid4())

        read_collection = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/key', kind=documents.PartitionKind.Hash)
        )

        user = await created_db.create_user(body={'id': 'user' + str(uuid.uuid4())})

        permission_definition = {
            'id': 'all permission',
            'permissionMode': documents.PermissionMode.All,
            'resource': all_collection.container_link,
            'resourcePartitionKey': [1]
        }

        all_permission = await user.create_permission(body=permission_definition)

        permission_definition = {
            'id': 'read permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': read_collection.container_link,
            'resourcePartitionKey': [1]
        }

        read_permission = await user.create_permission(body=permission_definition)

        resource_tokens = {}
        # storing the resource tokens based on Resource IDs
        resource_tokens["dbs/" + created_db.id + "/colls/" + all_collection.id] = (all_permission.properties['_token'])
        resource_tokens["dbs/" + created_db.id + "/colls/" + read_collection.id] = (read_permission.properties['_token'])

        async with CosmosClient(
            CRUDTests.host, resource_tokens, consistency_level="Session", connection_policy=CRUDTests.connectionPolicy) as restricted_client:
            print('Async Initialization')

            document_definition = {'id': 'document1',
                                   'key': 1
                                   }

            all_collection.client_connection = restricted_client.client_connection
            read_collection.client_connection = restricted_client.client_connection

            # Create document in all_collection should succeed since the partitionKey is 1 which is what specified as resourcePartitionKey in permission object and it has all permissions
            created_document = await all_collection.create_item(body=document_definition)

            # Create document in read_collection should fail since it has only read permissions for this collection
            await self.__AssertHTTPFailureWithStatus(
                StatusCodes.FORBIDDEN,
                read_collection.create_item,
                document_definition)

            document_definition['key'] = 2
            # Create document should fail since the partitionKey is 2 which is different that what is specified as resourcePartitionKey in permission object
            await self.__AssertHTTPFailureWithStatus(
                StatusCodes.FORBIDDEN,
                all_collection.create_item,
                document_definition)

            document_definition['key'] = 1
            # Delete document should succeed since the partitionKey is 1 which is what specified as resourcePartitionKey in permission object
            created_document = await all_collection.delete_item(item=created_document['id'],
                                                          partition_key=document_definition['key'])

            # Delete document in read_collection should fail since it has only read permissions for this collection
            await self.__AssertHTTPFailureWithStatus(
                StatusCodes.FORBIDDEN,
                read_collection.delete_item,
                document_definition['id'],
                document_definition['id']
            )

            await created_db.delete_container(all_collection)
            await created_db.delete_container(read_collection)

    async def test_partitioned_collection_execute_stored_procedure(self):
        created_db = self.databaseForTest

        created_collection = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_PARTITION_KEY, PartitionKey(path="/pk"))

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

        created_sproc = await created_collection.scripts.create_stored_procedure(body=sproc)

        # Partiton Key value same as what is specified in the stored procedure body
        result = await created_collection.scripts.execute_stored_procedure(sproc=created_sproc['id'], partition_key=2)
        self.assertEqual(result, 1)

        # Partiton Key value different than what is specified in the stored procedure body will cause a bad request(400) error
        await self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            created_collection.scripts.execute_stored_procedure,
            created_sproc['id'],
            3)

    async def test_partitioned_collection_partition_key_value_types(self):
        created_db = self.databaseForTest

        created_collection = await created_db.create_container(
            id='test_partitioned_collection_partition_key_value_types ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/pk', kind='Hash')
        )

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': None,
                               'spam': 'eggs'}

        # create document with partitionKey set as None here
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'spam': 'eggs'}

        # create document with partitionKey set as Undefined here
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': True,
                               'spam': 'eggs'}

        # create document with bool partitionKey
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 'value',
                               'spam': 'eggs'}

        # create document with string partitionKey
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 100,
                               'spam': 'eggs'}

        # create document with int partitionKey
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 10.50,
                               'spam': 'eggs'}

        # create document with float partitionKey
        await created_collection.create_item(body=document_definition)

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'pk': 'value'}

        # Should throw an error because automatic id generation is disabled always.
        await self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            created_collection.create_item,
            document_definition
        )

        await created_db.delete_container(created_collection)

    async def test_partitioned_collection_conflict_crud_and_query(self):
        created_db = self.databaseForTest

        created_collection = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION)

        conflict_definition = {'id': 'new conflict',
                               'resourceId': 'doc1',
                               'operationType': 'create',
                               'resourceType': 'document'
                               }

        # read conflict here will return resource not found(404) since there is no conflict here
        await self.__AssertHTTPFailureWithStatus(
            StatusCodes.NOT_FOUND,
            created_collection.read_conflict,
            conflict_definition['id'],
            conflict_definition['id']
        )

        # Read conflict feed doesn't requires partitionKey to be specified as it's a cross partition thing
        conflictlist = [conflict async for conflict in created_collection.list_conflicts()]
        self.assertEqual(0, len(conflictlist))

        # delete conflict here will return resource not found(404) since there is no conflict here
        await self.__AssertHTTPFailureWithStatus(
            StatusCodes.NOT_FOUND,
            created_collection.delete_conflict,
            conflict_definition['id'],
            conflict_definition['id']
        )

        # query conflicts on any property other than partitionKey will fail without setting enableCrossPartitionQuery or passing in the partitionKey value
        try:
            [conflict async for conflict in created_collection.query_conflicts(
                query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get(  # nosec
                    'resourceType') + '\''
            )]
        except Exception:
            pass

        conflictlist = [conflict async for conflict in created_collection.query_conflicts(
            query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'',
            # nosec
            enable_cross_partition_query=True
        )]

        self.assertEqual(0, len(conflictlist))

        # query conflicts by providing the partitionKey value
        options = {'partitionKey': conflict_definition.get('id')}
        conflictlist = [conflict async for conflict in created_collection.query_conflicts(
            query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'',
            # nosec
            partition_key=conflict_definition['id']
        )]

        self.assertEqual(0, len(conflictlist))

    async def test_document_crud(self):
        # create database
        created_db = self.databaseForTest
        # create collection
        created_collection = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION)
        # read documents
        documents = [document async for document in created_collection.read_all_items()]
        # create a document
        before_create_documents_count = len(documents)

        # create a document with auto ID generation
        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value'}

        created_document = await created_collection.create_item(body=document_definition, enable_automatic_id_generation=True)
        self.assertEqual(created_document.get('name'),
                         document_definition['name'])

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'id': str(uuid.uuid4())}

        created_document = await created_collection.create_item(body=document_definition)
        self.assertEqual(created_document.get('name'),
                         document_definition['name'])
        self.assertEqual(created_document.get('id'),
                         document_definition['id'])

        # duplicated documents are not allowed when 'id' is provided.
        duplicated_definition_with_id = document_definition.copy()
        await self.__AssertHTTPFailureWithStatus(StatusCodes.CONFLICT,
                                                 created_collection.create_item,
                                                 duplicated_definition_with_id)
        # read documents after creation
        documents = [document async for document in created_collection.read_all_items()]
        self.assertEqual(
            len(documents),
            before_create_documents_count + 2,
            'create should increase the number of documents')
        # query documents
        documents = [document async for document in created_collection.query_items(

            query='SELECT * FROM root r WHERE r.name=@name',
            parameter=[
                {'name': '@name', 'value': document_definition['name']}
            ]
            , enable_cross_partition_query=True
        )]
        self.assertTrue(documents)
        documents = [document async for document in created_collection.query_items(

            query='SELECT * FROM root r WHERE r.name=@name',
            parameter=[
                {'name': '@name', 'value': document_definition['name']}
            ]
            , enable_cross_partition_query=True,
            enable_scan_in_query=True
        )]
        self.assertTrue(documents)
        # replace document.
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'
        old_etag = created_document['_etag']
        replaced_document = await created_collection.replace_item(
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
        await self.__AssertHTTPFailureWithStatus(
            StatusCodes.PRECONDITION_FAILED,
            created_collection.replace_item,
            replaced_document['id'],
            replaced_document,
            if_match=old_etag,
        )

        # should fail if only etag specified
        with self.assertRaises(ValueError):
            await created_collection.replace_item(
                etag=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document
            )

        # should fail if only match condition specified
        with self.assertRaises(ValueError):
            await created_collection.replace_item(
                match_condition=MatchConditions.IfNotModified,
                item=replaced_document['id'],
                body=replaced_document
            )
        with self.assertRaises(ValueError):
            await created_collection.replace_item(
                match_condition=MatchConditions.IfModified,
                item=replaced_document['id'],
                body=replaced_document
            )

        # should fail if invalid match condition specified
        with self.assertRaises(TypeError):
            await created_collection.replace_item(
                match_condition=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document
            )

        # should pass for most recent etag
        replaced_document_conditional = await created_collection.replace_item(
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
        one_document_from_read = await created_collection.read_item(
            item=replaced_document['id'],
            partition_key=replaced_document['id']
        )
        self.assertEqual(replaced_document['id'],
                         one_document_from_read['id'])
        # delete document
        await created_collection.delete_item(
            item=replaced_document,
            partition_key=replaced_document['id']
        )
        # read documents after deletion
        await self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                                 created_collection.read_item,
                                                 replaced_document['id'],
                                                 replaced_document['id'])

    async def test_document_upsert(self):
        # create database
        created_db = self.databaseForTest

        # create collection
        created_collection = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION)

        # read documents and check count
        documents = [document async for document in created_collection.read_all_items()]
        before_create_documents_count = len(documents)

        # create document definition
        document_definition = {'id': 'doc',
                               'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value'}

        # create document using Upsert API
        created_document = await created_collection.upsert_item(body=document_definition)

        # verify id property
        self.assertEqual(created_document['id'],
                         document_definition['id'])

        # test error for non-string id
        with pytest.raises(TypeError):
            document_definition['id'] = 7
            await created_collection.upsert_item(body=document_definition)

        # read documents after creation and verify updated count
        documents = [document async for document in created_collection.read_all_items()]
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'create should increase the number of documents')

        # update document
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'

        # should replace document since it already exists
        upserted_document = await created_collection.upsert_item(body=created_document)

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
        documents = [document async for document in created_collection.read_all_items()]
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'number of documents should remain same')

        created_document['id'] = 'new id'

        # Upsert should create new document since the id is different
        new_document = await created_collection.upsert_item(body=created_document)

        # Test modified access conditions
        created_document['spam'] = 'more eggs'
        await created_collection.upsert_item(body=created_document)
        with pytest.raises(exceptions.CosmosHttpResponseError):
            await created_collection.upsert_item(
                body=created_document,
                match_condition=MatchConditions.IfNotModified,
                etag=new_document['_etag'])

        # verify id property
        self.assertEqual(created_document['id'],
                         new_document['id'],
                         'document id should be same')

        # read documents after upsert and verify count increases
        documents = [document async for document in created_collection.read_all_items()]
        self.assertEqual(
            len(documents),
            before_create_documents_count + 2,
            'upsert should increase the number of documents')

        # delete documents
        await created_collection.delete_item(item=upserted_document, partition_key=upserted_document['id'])
        await created_collection.delete_item(item=new_document, partition_key=new_document['id'])

        # read documents after delete and verify count is same as original
        documents = [document async for document in created_collection.read_all_items()]
        self.assertEqual(
            len(documents),
            before_create_documents_count,
            'number of documents should remain same')

    async def _test_spatial_index(self):
        db = self.databaseForTest
        # partial policy specified
        collection = await db.create_container(
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
        await collection.create_item(
            body={
                'id': 'loc1',
                'Location': {
                    'type': 'Point',
                    'coordinates': [20.0, 20.0]
                }
            }
        )
        await collection.create_item(
            body={
                'id': 'loc2',
                'Location': {
                    'type': 'Point',
                    'coordinates': [100.0, 100.0]
                }
            }
        )
        results = [result async for result in collection.query_items(
            query="SELECT * FROM root WHERE (ST_DISTANCE(root.Location, {type: 'Point', coordinates: [20.1, 20]}) < 20000)",
            enable_cross_partition_query=True
        )]
        self.assertEqual(1, len(results))
        self.assertEqual('loc1', results[0]['id'])

        await db.delete_container(container=collection)

    # CRUD test for User resource
    async def test_user_crud(self):
        # Should do User CRUD operations successfully.
        # create database
        db = self.databaseForTest
        # list users
        users = [user async for user in db.list_users()]
        before_create_count = len(users)
        # create user
        user_id = 'new user' + str(uuid.uuid4())
        user = await db.create_user(body={'id': user_id})
        self.assertEqual(user.id, user_id, 'user id error')
        # list users after creation
        users = [user async for user in db.list_users()]
        self.assertEqual(len(users), before_create_count + 1)
        # query users
        results = [user async for user in db.query_users(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': user_id}
            ]
        )]
        self.assertTrue(results)

        # replace user
        replaced_user_id = 'replaced user' + str(uuid.uuid4())
        user_properties = await user.read()
        user_properties['id'] = replaced_user_id
        replaced_user = await db.replace_user(user_id, user_properties)
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
        await db.delete_user(user.id)
        # read user after deletion
        deleted_user = db.get_user_client(user.id)
        await self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                                 deleted_user.read)

    async def test_user_upsert(self):
        # create database
        db = self.databaseForTest

        # read users and check count
        users = [user async for user in db.list_users()]
        before_create_count = len(users)

        # create user using Upsert API
        user_id = 'user' + str(uuid.uuid4())
        user = await db.upsert_user(body={'id': user_id})

        # verify id property
        self.assertEqual(user.id, user_id, 'user id error')

        # read users after creation and verify updated count
        users = [user async for user in db.list_users()]
        self.assertEqual(len(users), before_create_count + 1)

        # Should replace the user since it already exists, there is no public property to change here
        user_properties = await user.read()
        upserted_user = await db.upsert_user(user_properties)

        # verify id property
        self.assertEqual(upserted_user.id,
                         user.id,
                         'user id should remain same')

        # read users after upsert and verify count doesn't increases again
        users = [user async for user in db.list_users()]
        self.assertEqual(len(users), before_create_count + 1)

        user_properties = await user.read()
        user_properties['id'] = 'new user' + str(uuid.uuid4())
        user.id = user_properties['id']

        # Upsert should create new user since id is different
        new_user = await db.upsert_user(user_properties)

        # verify id property
        self.assertEqual(new_user.id, user.id, 'user id error')

        # read users after upsert and verify count increases
        users = [user async for user in db.list_users()]
        self.assertEqual(len(users), before_create_count + 2)

        # delete users
        await db.delete_user(upserted_user.id)
        await db.delete_user(new_user.id)

        # read users after delete and verify count remains the same
        users = [user async for user in db.list_users()]
        self.assertEqual(len(users), before_create_count)

    async def test_permission_crud(self):
        # Should do Permission CRUD operations successfully
        # create database
        db = self.databaseForTest
        # create user
        user = await db.create_user(body={'id': 'new user' + str(uuid.uuid4())})
        # list permissions
        permissions = [permission async for permission in user.list_permissions()]
        before_create_count = len(permissions)
        permission = {
            'id': 'new permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': 'dbs/AQAAAA==/colls/AQAAAJ0fgTc='  # A random one.
        }
        # create permission
        permission = await user.create_permission(permission)
        self.assertEqual(permission.id,
                         'new permission',
                         'permission id error')
        # list permissions after creation
        permissions = [permission async for permission in user.list_permissions()]
        self.assertEqual(len(permissions), before_create_count + 1)
        # query permissions
        results = [permission async for permission in user.query_permissions(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': permission.id}
            ]
        )]
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
        permission = await user.get_permission(replaced_permission.id)
        self.assertEqual(replaced_permission.id, permission.id)
        # delete permission
        await user.delete_permission(replaced_permission.id)
        # read permission after deletion
        await self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                                 user.get_permission,
                                                 permission.id)

    async def test_permission_upsert(self):
        # create database
        db = self.databaseForTest

        # create user
        user = await db.create_user(body={'id': 'new user' + str(uuid.uuid4())})

        # read permissions and check count
        permissions = [permission async for permission in user.list_permissions()]
        before_create_count = len(permissions)

        permission_definition = {
            'id': 'permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': 'dbs/AQAAAA==/colls/AQAAAJ0fgTc='  # A random one.
        }

        # create permission using Upsert API
        created_permission = await user.upsert_permission(permission_definition)

        # verify id property
        self.assertEqual(created_permission.id,
                         permission_definition['id'],
                         'permission id error')

        # read permissions after creation and verify updated count
        permissions = [permission async for permission in user.list_permissions()]
        self.assertEqual(len(permissions), before_create_count + 1)

        # update permission mode
        permission_definition['permissionMode'] = documents.PermissionMode.All

        # should repace the permission since it already exists
        upserted_permission = await user.upsert_permission(permission_definition)
        # verify id property
        self.assertEqual(upserted_permission.id,
                         created_permission.id,
                         'permission id should remain same')

        # verify changed property
        self.assertEqual(upserted_permission.permission_mode,
                         permission_definition['permissionMode'],
                         'permissionMode should change')

        # read permissions and verify count doesn't increases again
        permissions = [permission async for permission in user.list_permissions()]
        self.assertEqual(len(permissions), before_create_count + 1)

        # update permission id
        created_permission.properties['id'] = 'new permission'
        created_permission.id = created_permission.properties['id']
        # resource needs to be changed along with the id in order to create a new permission
        created_permission.properties['resource'] = 'dbs/N9EdAA==/colls/N9EdAIugXgA='
        created_permission.resource_link = created_permission.properties['resource']

        # should create new permission since id has changed
        new_permission = await user.upsert_permission(created_permission.properties)

        # verify id and resource property
        self.assertEqual(new_permission.id,
                         created_permission.id,
                         'permission id should be same')

        self.assertEqual(new_permission.resource_link,
                         created_permission.resource_link,
                         'permission resource should be same')

        # read permissions and verify count increases
        permissions = [permission async for permission in user.list_permissions()]
        self.assertEqual(len(permissions), before_create_count + 2)

        # delete permissions
        await user.delete_permission(upserted_permission.id)
        await user.delete_permission(new_permission.id)

        # read permissions and verify count remains the same
        permissions = [permission async for permission in user.list_permissions()]
        self.assertEqual(len(permissions), before_create_count)

    async def test_authorization(self):
        async def __SetupEntities(client):
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
            collection = await db.create_container(
                id='test_authorization' + str(uuid.uuid4()),
                partition_key=PartitionKey(path='/id', kind='Hash')
            )
            # create document1
            document = await collection.create_item(
                body={'id': 'doc1',
                      'spam': 'eggs',
                      'key': 'value'},
            )

            # create user
            user = await db.create_user(body={'id': 'user' + str(uuid.uuid4())})

            # create permission for collection
            permission = {
                'id': 'permission On Coll',
                'permissionMode': documents.PermissionMode.Read,
                'resource': "dbs/" + db.id + "/colls/" + collection.id
            }
            permission_on_coll = await user.create_permission(body=permission)
            self.assertIsNotNone(permission_on_coll.properties['_token'],
                                 'permission token is invalid')

            # create permission for document
            permission = {
                'id': 'permission On Doc',
                'permissionMode': documents.PermissionMode.All,
                'resource': "dbs/" + db.id + "/colls/" + collection.id + "/docs/" + document["id"]
            }
            permission_on_doc = await user.create_permission(body=permission)
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
        async with CosmosClient(CRUDTests.host, {}, consistency_level="Session", connection_policy=CRUDTests.connectionPolicy) as client:
            try:
                [db async for db in client.list_databases()]
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, StatusCodes.UNAUTHORIZED)

        # Client with master key.
        async with CosmosClient(CRUDTests.host,
                                            CRUDTests.masterKey,
                                            consistency_level="Session",
                                            connection_policy=CRUDTests.connectionPolicy) as client:
            # setup entities
            entities = await __SetupEntities(client)
            resource_tokens = {"dbs/" + entities['db'].id + "/colls/" + entities['coll'].id:
                                   entities['permissionOnColl'].properties['_token']}

        async with CosmosClient(
                CRUDTests.host, resource_tokens, consistency_level="Session", connection_policy=CRUDTests.connectionPolicy) as col_client:
            db = entities['db']

            old_client_connection = db.client_connection
            db.client_connection = col_client.client_connection
            # 1. Success-- Use Col Permission to Read
            success_coll = db.get_container_client(container=entities['coll'])
            # 2. Failure-- Use Col Permission to delete
            await self.__AssertHTTPFailureWithStatus(StatusCodes.FORBIDDEN,
                                                     db.delete_container,
                                                     success_coll)
            # 3. Success-- Use Col Permission to Read All Docs
            success_documents = [document async for document in success_coll.read_all_items()]
            self.assertTrue(success_documents != None,
                            'error reading documents')
            self.assertEqual(len(success_documents),
                             1,
                             'Expected 1 Document to be successfully read')
            # 4. Success-- Use Col Permission to Read Doc

            docId = entities['doc']['id']
            success_doc = await success_coll.read_item(
                item=docId,
                partition_key=docId
            )
            self.assertTrue(success_doc != None, 'error reading document')
            self.assertEqual(
                success_doc['id'],
                entities['doc']['id'],
                'Expected to read children using parent permissions')

            # 5. Failure-- Use Col Permission to Delete Doc
            await self.__AssertHTTPFailureWithStatus(StatusCodes.FORBIDDEN,
                                                     success_coll.delete_item,
                                                     docId, docId)

            resource_tokens = {"dbs/" + entities['db'].id + "/colls/" + entities['coll'].id + "/docs/" + docId:
                                   entities['permissionOnDoc'].properties['_token']}

        async with CosmosClient(
                CRUDTests.host, resource_tokens, consistency_level="Session", connection_policy=CRUDTests.connectionPolicy) as doc_client:

            # 6. Success-- Use Doc permission to read doc
            read_doc = await doc_client.get_database_client(db.id).get_container_client(success_coll.id).read_item(docId, docId)
            self.assertEqual(read_doc["id"], docId)

            # 6. Success-- Use Doc permission to delete doc
            await doc_client.get_database_client(db.id).get_container_client(success_coll.id).delete_item(docId, docId)
            self.assertEqual(read_doc["id"], docId)

            db.client_connection = old_client_connection
            await db.delete_container(entities['coll'])

    async def test_trigger_crud(self):
        # create database
        db = self.databaseForTest
        # create collection
        collection = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION)
        # read triggers
        triggers = [trigger async for trigger in collection.scripts.list_triggers()]
        # create a trigger
        before_create_triggers_count = len(triggers)
        trigger_definition = {
            'id': 'sample trigger',
            'serverScript': 'function() {var x = 10;}',
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        }
        trigger = await collection.scripts.create_trigger(body=trigger_definition)
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
        triggers = [trigger async for trigger in collection.scripts.list_triggers()]
        self.assertEqual(len(triggers),
                         before_create_triggers_count + 1,
                         'create should increase the number of triggers')
        # query triggers
        triggers = [trigger async for trigger in collection.scripts.query_triggers(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': trigger_definition['id']}
            ]
        )]
        self.assertTrue(triggers)

        # replace trigger
        change_trigger = trigger.copy()
        trigger['body'] = 'function() {var x = 20;}'
        replaced_trigger = await collection.scripts.replace_trigger(change_trigger['id'], trigger)
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
        trigger = await collection.scripts.get_trigger(replaced_trigger['id'])
        self.assertEqual(replaced_trigger['id'], trigger['id'])
        # delete trigger
        await collection.scripts.delete_trigger(replaced_trigger['id'])
        # read triggers after deletion
        await self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                                 collection.scripts.delete_trigger,
                                                 replaced_trigger['id'])

    async def test_udf_crud(self):
        # create database
        db = self.databaseForTest
        # create collection
        collection = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION)
        # read udfs
        udfs = [udf async for udf in collection.scripts.list_user_defined_functions()]
        # create a udf
        before_create_udfs_count = len(udfs)
        udf_definition = {
            'id': 'sample udf',
            'body': 'function() {var x = 10;}'
        }
        udf = await collection.scripts.create_user_defined_function(body=udf_definition)
        for property in udf_definition:
            self.assertEqual(
                udf[property],
                udf_definition[property],
                'property {property} should match'.format(property=property))

        # read udfs after creation
        udfs = [udf async for udf in collection.scripts.list_user_defined_functions()]
        self.assertEqual(len(udfs),
                         before_create_udfs_count + 1,
                         'create should increase the number of udfs')
        # query udfs
        results = [udf async for udf in collection.scripts.query_user_defined_functions(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': udf_definition['id']}
            ]
        )]
        self.assertTrue(results)
        # replace udf
        change_udf = udf.copy()
        udf['body'] = 'function() {var x = 20;}'
        replaced_udf = await collection.scripts.replace_user_defined_function(udf=udf['id'], body=udf)
        for property in udf_definition:
            self.assertEqual(
                replaced_udf[property],
                udf[property],
                'property {property} should match'.format(property=property))
        # read udf
        udf = await collection.scripts.get_user_defined_function(replaced_udf['id'])
        self.assertEqual(replaced_udf['id'], udf['id'])
        # delete udf
        await collection.scripts.delete_user_defined_function(replaced_udf['id'])
        # read udfs after deletion
        await self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                                 collection.scripts.get_user_defined_function,
                                                 replaced_udf['id'])

    async def test_sproc_crud(self):
        # create database
        db = self.databaseForTest
        # create collection
        collection = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION)
        # read sprocs
        sprocs = [sproc async for sproc in collection.scripts.list_stored_procedures()]
        # create a sproc
        before_create_sprocs_count = len(sprocs)
        sproc_definition = {
            'id': 'sample sproc',
            'serverScript': 'function() {var x = 10;}'
        }
        sproc = await collection.scripts.create_stored_procedure(body=sproc_definition)
        for property in sproc_definition:
            if property != "serverScript":
                self.assertEqual(
                    sproc[property],
                    sproc_definition[property],
                    'property {property} should match'.format(property=property))
            else:
                self.assertEqual(sproc['body'], 'function() {var x = 10;}')

        # read sprocs after creation
        sprocs = [sproc async for sproc in collection.scripts.list_stored_procedures()]
        self.assertEqual(len(sprocs),
                         before_create_sprocs_count + 1,
                         'create should increase the number of sprocs')
        # query sprocs
        sprocs = [sproc async for sproc in collection.scripts.query_stored_procedures(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': sproc_definition['id']}
            ]
        )]
        self.assertIsNotNone(sprocs)
        # replace sproc
        change_sproc = sproc.copy()
        sproc['body'] = 'function() {var x = 20;}'
        replaced_sproc = await collection.scripts.replace_stored_procedure(sproc=change_sproc['id'], body=sproc)
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
        sproc = await collection.scripts.get_stored_procedure(replaced_sproc['id'])
        self.assertEqual(replaced_sproc['id'], sproc['id'])
        # delete sproc
        await collection.scripts.delete_stored_procedure(replaced_sproc['id'])
        # read sprocs after deletion
        await self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                                 collection.scripts.get_stored_procedure,
                                                 replaced_sproc['id'])

    async def test_script_logging_execute_stored_procedure(self):
        created_db = self.databaseForTest

        created_collection = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION)

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

        created_sproc = await created_collection.scripts.create_stored_procedure(body=sproc)

        result = await created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            partition_key=1
        )

        self.assertEqual(result, 'Success!')
        self.assertFalse(
            HttpHeaders.ScriptLogResults in created_collection.scripts.client_connection.last_response_headers)

        result = await created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            enable_script_logging=True,
            partition_key=1
        )

        self.assertEqual(result, 'Success!')
        self.assertEqual(urllib.quote('The value of x is 1.'),
                         created_collection.scripts.client_connection.last_response_headers.get(
                             HttpHeaders.ScriptLogResults))

        result = await created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            enable_script_logging=False,
            partition_key=1
        )

        self.assertEqual(result, 'Success!')
        self.assertFalse(
            HttpHeaders.ScriptLogResults in created_collection.scripts.client_connection.last_response_headers)

    async def test_collection_indexing_policy(self):
        # create database
        db = self.databaseForTest
        # create collection
        collection = await db.create_container(
            id='test_collection_indexing_policy default policy' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/id', kind='Hash')
        )

        collection_properties = await collection.read()
        self.assertEqual(collection_properties['indexingPolicy']['indexingMode'],
                         documents.IndexingMode.Consistent,
                         'default indexing mode should be consistent')

        await db.delete_container(container=collection)

        consistent_collection = await db.create_container(
            id='test_collection_indexing_policy consistent collection ' + str(uuid.uuid4()),
            indexing_policy={
                'indexingMode': documents.IndexingMode.Consistent
            },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )

        consistent_collection_properties = await consistent_collection.read()
        self.assertEqual(consistent_collection_properties['indexingPolicy']['indexingMode'],
                         documents.IndexingMode.Consistent,
                         'indexing mode should be consistent')

        await db.delete_container(container=consistent_collection)

        collection_with_indexing_policy = await db.create_container(
            id='CollectionWithIndexingPolicy ' + str(uuid.uuid4()),
            indexing_policy={
                'automatic': True,
                'indexingMode': documents.IndexingMode.Consistent,
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

        collection_with_indexing_policy_properties = await collection_with_indexing_policy.read()
        self.assertEqual(1,
                         len(collection_with_indexing_policy_properties['indexingPolicy']['includedPaths']),
                         'Unexpected includedPaths length')
        self.assertEqual(2,
                         len(collection_with_indexing_policy_properties['indexingPolicy']['excludedPaths']),
                         'Unexpected excluded path count')
        await db.delete_container(container=collection_with_indexing_policy)

    async def test_create_default_indexing_policy(self):
        # create database
        db = self.databaseForTest

        # no indexing policy specified
        collection = await db.create_container(
            id='test_create_default_indexing_policy TestCreateDefaultPolicy01' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        collection_properties = await collection.read()
        await self._check_default_indexing_policy_paths(collection_properties['indexingPolicy'])
        await db.delete_container(container=collection)

        # partial policy specified
        collection = await db.create_container(
            id='test_create_default_indexing_policy TestCreateDefaultPolicy01' + str(uuid.uuid4()),
            indexing_policy={
                'indexingMode': documents.IndexingMode.Consistent, 'automatic': True
            },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        collection_properties = await collection.read()
        await self._check_default_indexing_policy_paths(collection_properties['indexingPolicy'])
        await db.delete_container(container=collection)

        # default policy
        collection = await db.create_container(
            id='test_create_default_indexing_policy TestCreateDefaultPolicy03' + str(uuid.uuid4()),
            indexing_policy={},
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        collection_properties = await collection.read()
        await self._check_default_indexing_policy_paths(collection_properties['indexingPolicy'])
        await db.delete_container(container=collection)

        # missing indexes
        collection = await db.create_container(
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
        collection_properties = await collection.read()
        await self._check_default_indexing_policy_paths(collection_properties['indexingPolicy'])
        await db.delete_container(container=collection)

        # missing precision
        collection = await db.create_container(
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
        collection_properties = await collection.read()
        await self._check_default_indexing_policy_paths(collection_properties['indexingPolicy'])
        await db.delete_container(container=collection)

    async def test_create_indexing_policy_with_composite_and_spatial_indexes(self):
        # create database
        db = self.databaseForTest

        indexing_policy = {
            "spatialIndexes": [
                {
                    "path": "/path0/*",
                    "types": [
                        "Point",
                        "LineString",
                        "Polygon",
                        "MultiPolygon"
                    ]
                },
                {
                    "path": "/path1/*",
                    "types": [
                        "Point",
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

        custom_logger = logging.getLogger("CustomLogger")
        created_container = await db.create_container(
            id='composite_index_spatial_index' + str(uuid.uuid4()),
            indexing_policy=indexing_policy,
            partition_key=PartitionKey(path='/id', kind='Hash'),
            headers={"Foo": "bar"},
            user_agent="blah",
            user_agent_overwrite=True,
            logging_enable=True,
            logger=custom_logger,
        )
        created_properties = await created_container.read(logger=custom_logger)
        read_indexing_policy = created_properties['indexingPolicy']

        if 'localhost' in self.host or '127.0.0.1' in self.host:  # TODO: Differing result between live and emulator
            self.assertListEqual(indexing_policy['spatialIndexes'], read_indexing_policy['spatialIndexes'])
        else:
            # All types are returned for spatial Indexes
            self.assertListEqual(indexing_policy['spatialIndexes'], read_indexing_policy['spatialIndexes'])

        self.assertListEqual(indexing_policy['compositeIndexes'], read_indexing_policy['compositeIndexes'])
        await db.delete_container(container=created_container)

    async def _check_default_indexing_policy_paths(self, indexing_policy):
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
        self.assertFalse(root_included_path.get('indexes'))

    async def test_client_request_timeout(self):
        # Test is flaky on Emulator
        if not ('localhost' in self.host or '127.0.0.1' in self.host):
            connection_policy = documents.ConnectionPolicy()
            # making timeout 0 ms to make sure it will throw
            connection_policy.RequestTimeout = 0.000000000001

            with self.assertRaises(Exception):
                # client does a getDatabaseAccount on initialization, which will time out
                async with CosmosClient(CRUDTests.host, CRUDTests.masterKey, consistency_level="Session",
                                           connection_policy=connection_policy) as client:
                    print('Async initialization')

    async def test_client_request_timeout_when_connection_retry_configuration_specified(self):
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
        with self.assertRaises(AzureError):
            # client does a getDatabaseAccount on initialization, which will time out
            async with CosmosClient(CRUDTests.host, CRUDTests.masterKey, consistency_level="Session",
                                       connection_policy=connection_policy) as client:
                print('Async Initialization')

    async def test_client_connection_retry_configuration(self):
        total_time_for_two_retries = await self.initialize_client_with_connection_urllib_retry_config(2)
        total_time_for_three_retries = await self.initialize_client_with_connection_urllib_retry_config(3)
        self.assertGreater(total_time_for_three_retries, total_time_for_two_retries)

        total_time_for_two_retries = await self.initialize_client_with_connection_core_retry_config(2)
        total_time_for_three_retries = await self.initialize_client_with_connection_core_retry_config(3)
        self.assertGreater(total_time_for_three_retries, total_time_for_two_retries)

    async def initialize_client_with_connection_urllib_retry_config(self, retries):
        retry_policy = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 504)
        )
        start_time = time.time()
        try:
            async with CosmosClient(
                "https://localhost:9999",
                CRUDTests.masterKey,
                consistency_level="Session",
                connection_retry_policy=retry_policy) as client: print('Async initialization')
            self.fail()
        except AzureError as e:
            end_time = time.time()
            return end_time - start_time

    async def initialize_client_with_connection_core_retry_config(self, retries):
        start_time = time.time()
        try:
            async with CosmosClient(
                "https://localhost:9999",
                CRUDTests.masterKey,
                consistency_level="Session",
                retry_total=retries,
                retry_read=retries,
                retry_connect=retries,
                retry_status=retries) as client: print('Async initialization')
            self.fail()
        except AzureError as e:
            end_time = time.time()
            return end_time - start_time

    async def test_absolute_client_timeout(self):
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            async with CosmosClient(
                "https://localhost:9999",
                CRUDTests.masterKey,
                consistency_level="Session",
                retry_total=3,
                timeout=1)as client: print('Async initialization')

        error_response = ServiceResponseError("Read timeout")
        timeout_transport = TimeoutTransport(error_response)
        async with CosmosClient(
            self.host, self.masterKey, consistency_level="Session", transport=timeout_transport, passthrough=True) as client: print('Async initialization')

        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            await client.create_database_if_not_exists("test", timeout=2)

        status_response = 500  # Users connection level retry
        timeout_transport = TimeoutTransport(status_response)
        async with CosmosClient(
                self.host, self.masterKey, consistency_level="Session", transport=timeout_transport, passthrough=True) as client: print(
            'Async initialization')
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            await client.create_database("test", timeout=2)

        databases = client.list_databases(timeout=2)
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            databases = [database async for database in databases]

        status_response = 429  # Uses Cosmos custom retry
        timeout_transport = TimeoutTransport(status_response)
        async with CosmosClient(
                self.host, self.masterKey, consistency_level="Session", transport=timeout_transport, passthrough=True) as client: print(
            'Async initialization')
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            await client.create_database_if_not_exists("test", timeout=2)

        databases = client.list_databases(timeout=2)
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            databases = [database async for database in databases]

    async def test_query_iterable_functionality(self):
        async def __create_resources(client):
            """Creates resources for this test.

            :Parameters:
                - `client`: cosmos_client_connection.CosmosClientConnection

            :Returns:
                dict

            """
            collection = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_PARTITION_KEY, PartitionKey(path="/pk"))
            doc1 = await collection.create_item(body={'id': 'doc1', 'prop1': 'value1'})
            doc2 = await collection.create_item(body={'id': 'doc2', 'prop1': 'value2'})
            doc3 = await collection.create_item(body={'id': 'doc3', 'prop1': 'value3'})
            resources = {
                'coll': collection,
                'doc1': doc1,
                'doc2': doc2,
                'doc3': doc3
            }
            return resources

        # Validate QueryIterable by converting it to a list.
        resources = await __create_resources(self.client)
        results = resources['coll'].read_all_items(max_item_count=2)
        docs = [doc async for doc in results]
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
        async for doc in results:
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
        first_block = [page async for page in next(page_iter)]
        self.assertEqual(2, len(first_block), 'First block should have 2 entries.')
        self.assertEqual(resources['doc1']['id'], first_block[0]['id'])
        self.assertEqual(resources['doc2']['id'], first_block[1]['id'])
        self.assertEqual(1, len([page async for page in next(page_iter)]), 'Second block should have 1 entry.')
        with self.assertRaises(StopIteration):
            next(page_iter)

    async def test_trigger_functionality(self):
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

        async def __CreateTriggers(collection, triggers):
            """Creates triggers.

            :Parameters:
                - `client`: cosmos_client_connection.CosmosClientConnection
                - `collection`: dict

            """
            async for trigger_i in triggers:
                trigger = await collection.scripts.create_trigger(body=trigger_i)
                async for property in trigger_i:
                    self.assertEqual(
                        trigger[property],
                        trigger_i[property],
                        'property {property} should match'.format(property=property))

        # create database
        db = self.databaseForTest
        # create collections
        pkd = PartitionKey(path='/id', kind='Hash')
        collection1 = await db.create_container(id='test_trigger_functionality 1 ' + str(uuid.uuid4()),
                                          partition_key=PartitionKey(path='/key', kind='Hash'))
        collection2 = await db.create_container(id='test_trigger_functionality 2 ' + str(uuid.uuid4()),
                                          partition_key=PartitionKey(path='/key', kind='Hash'))
        collection3 = await db.create_container(id='test_trigger_functionality 3 ' + str(uuid.uuid4()),
                                          partition_key=PartitionKey(path='/key', kind='Hash'))
        # create triggers
        await __CreateTriggers(collection1, triggers_in_collection1)
        await __CreateTriggers(collection2, triggers_in_collection2)
        await __CreateTriggers(collection3, triggers_in_collection3)
        # create document
        triggers_1 = [trigger async for trigger in collection1.scripts.list_triggers()]
        self.assertEqual(len(triggers_1), 3)
        document_1_1 = collection1.create_item(
            body={'id': 'doc1',
                  'key': 'value'},
            pre_trigger_include='t1'
        )
        self.assertEqual(document_1_1['id'],
                         'DOC1t1',
                         'id should be capitalized')

        document_1_2 = await collection1.create_item(
            body={'id': 'testing post trigger', 'key': 'value'},
            pre_trigger_include='t1',
            post_trigger_include='response1',
        )
        self.assertEqual(document_1_2['id'], 'TESTING POST TRIGGERt1')

        document_1_3 = await collection1.create_item(
            body={'id': 'responseheaders', 'key': 'value'},
            pre_trigger_include='t1'
        )
        self.assertEqual(document_1_3['id'], "RESPONSEHEADERSt1")

        triggers_2 = [trigger async for trigger in collection2.scripts.list_triggers()]
        self.assertEqual(len(triggers_2), 2)
        document_2_1 = await collection2.create_item(
            body={'id': 'doc2',
                  'key': 'value2'},
            pre_trigger_include='t2'
        )
        self.assertEqual(document_2_1['id'],
                         'doc2',
                         'id shouldn\'t change')
        document_2_2 = await collection2.create_item(
            body={'id': 'Doc3',
                  'prop': 'empty',
                  'key': 'value2'},
            pre_trigger_include='t3')
        self.assertEqual(document_2_2['id'], 'doc3t3')

        triggers_3 = [trigger async for trigger in collection3.scripts.list_triggers()]
        self.assertEqual(len(triggers_3), 1)
        with self.assertRaises(Exception):
            await collection3.create_item(
                body={'id': 'Docoptype', 'key': 'value2'},
                post_trigger_include='triggerOpType'
            )

        await db.delete_container(collection1)
        await db.delete_container(collection2)
        await db.delete_container(collection3)

    async def test_stored_procedure_functionality(self):
        # create database
        db = self.databaseForTest
        # create collection
        collection = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION)

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

        retrieved_sproc = await collection.scripts.create_stored_procedure(body=sproc1)
        result = await collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc['id'],
            partition_key=1
        )
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
        retrieved_sproc2 = await collection.scripts.create_stored_procedure(body=sproc2)
        result = await collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc2['id'],
            partition_key=1
        )
        self.assertEqual(int(result), 123456789)
        sproc3 = {
            'id': 'storedProcedure3' + str(uuid.uuid4()),
            'body': (
                    'function (input) {' +
                    '  getContext().getResponse().setBody(' +
                    '      \'a\' + input.temp);' +
                    '}')
        }
        retrieved_sproc3 = await collection.scripts.create_stored_procedure(body=sproc3)
        result = await collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc3['id'],
            params={'temp': 'so'},
            partition_key=1
        )
        self.assertEqual(result, 'aso')

    async def __ValidateOfferResponseBody(self, offer, expected_coll_link, expected_offer_type):
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

    async def test_offer_read_and_query(self):
        # Create database.
        db = self.databaseForTest

        # Create collection.
        collection = await db.create_container(
            id='test_offer_read_and_query ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        # Read the offer.
        expected_offer = await collection.get_throughput()
        collection_properties = await collection.read()
        await self.__ValidateOfferResponseBody(expected_offer, collection_properties.get('_self'), None)

        # Now delete the collection.
        await db.delete_container(container=collection)
        # Reading fails.
        await self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND, collection.read_offer)

    async def test_offer_replace(self):
        # Create database.
        db = self.databaseForTest
        # Create collection.
        collection = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION)
        # Read Offer
        expected_offer = await collection.get_throughput()
        collection_properties = await collection.read()
        await self.__ValidateOfferResponseBody(expected_offer, collection_properties.get('_self'), None)
        # Replace the offer.
        replaced_offer = await collection.replace_throughput(expected_offer.offer_throughput + 100)
        collection_properties = await collection.read()
        await self.__ValidateOfferResponseBody(replaced_offer, collection_properties.get('_self'), None)
        # Check if the replaced offer is what we expect.
        self.assertEqual(expected_offer.properties.get('content').get('offerThroughput') + 100,
                         replaced_offer.properties.get('content').get('offerThroughput'))
        self.assertEqual(expected_offer.offer_throughput + 100,
                         replaced_offer.offer_throughput)

    async def test_database_account_functionality(self):
        # Validate database account functionality.
        database_account = await self.client._get_database_account()
        self.assertEqual(database_account.DatabasesLink, '/dbs/')
        self.assertEqual(database_account.MediaLink, '/media/')
        if (HttpHeaders.MaxMediaStorageUsageInMB in
                await self.client.client_connection.last_response_headers):
            self.assertEqual(
                database_account.MaxMediaStorageUsageInMB,
                self.client.client_connection.last_response_headers[
                    HttpHeaders.MaxMediaStorageUsageInMB])
        if (HttpHeaders.CurrentMediaStorageUsageInMB in
                await self.client.client_connection.last_response_headers):
            self.assertEqual(
                database_account.CurrentMediaStorageUsageInMB,
                await self.client.client_connection.last_response_headers[
                    HttpHeaders.CurrentMediaStorageUsageInMB])
        self.assertIsNotNone(database_account.ConsistencyPolicy['defaultConsistencyLevel'])

    async def test_index_progress_headers(self):
        created_db = self.databaseForTest
        consistent_coll = await created_db.create_container(
            id='test_index_progress_headers consistent_coll ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id", kind='Hash'),
        )
        created_container = created_db.get_container_client(container=consistent_coll)
        await created_container.read(populate_quota_info=True)
        self.assertFalse(HttpHeaders.LazyIndexingProgress in created_db.client_connection.last_response_headers)
        self.assertTrue(HttpHeaders.IndexTransformationProgress in created_db.client_connection.last_response_headers)

        none_coll = await created_db.create_container(
            id='test_index_progress_headers none_coll ' + str(uuid.uuid4()),
            indexing_policy={
                'indexingMode': documents.IndexingMode.NoIndex,
                'automatic': False
            },
            partition_key=PartitionKey(path="/id", kind='Hash')
        )
        created_container = created_db.get_container_client(container=none_coll)
        await created_container.read(populate_quota_info=True)
        self.assertFalse(HttpHeaders.LazyIndexingProgress in created_db.client_connection.last_response_headers)
        self.assertTrue(HttpHeaders.IndexTransformationProgress in created_db.client_connection.last_response_headers)

        await created_db.delete_container(consistent_coll)
        await created_db.delete_container(none_coll)

    async def test_id_validation(self):
        # Id shouldn't end with space.
        try:
            await self.client.create_database(id='id_with_space ')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id ends with a space.', e.args[0])
        # Id shouldn't contain '/'.

        try:
            await self.client.create_database(id='id_with_illegal/_char')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])
        # Id shouldn't contain '\\'.

        try:
            await self.client.create_database(id='id_with_illegal\\_char')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])
        # Id shouldn't contain '?'.

        try:
            await self.client.create_database(id='id_with_illegal?_char')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])
        # Id shouldn't contain '#'.

        try:
            await self.client.create_database(id='id_with_illegal#_char')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])

        # Id can begin with space
        db = await self.client.create_database(id=' id_begin_space')
        self.assertTrue(True)

        await self.client.delete_database(database=db)

    async def test_id_case_validation(self):
        # create database
        created_db = self.databaseForTest

        uuid_string = str(uuid.uuid4())
        collection_id1 = 'sampleCollection ' + uuid_string
        collection_id2 = 'SampleCollection ' + uuid_string

        # Verify that no collections exist
        collections = [collection async for collection in created_db.list_containers()]
        number_of_existing_collections = len(collections)

        # create 2 collections with different casing of IDs
        # pascalCase
        created_collection1 = await created_db.create_container(
            id=collection_id1,
            partition_key=PartitionKey(path='/id', kind='Hash')
        )

        # CamelCase
        created_collection2 = await created_db.create_container(
            id=collection_id2,
            partition_key=PartitionKey(path='/id', kind='Hash')
        )

        collections = [collection async for collection in created_db.list_containers()]

        # verify if a total of 2 collections got created
        self.assertEqual(len(collections), number_of_existing_collections + 2)

        # verify that collections are created with specified IDs
        self.assertEqual(collection_id1, created_collection1.id)
        self.assertEqual(collection_id2, created_collection2.id)

        await created_db.delete_container(created_collection1)
        await created_db.delete_container(created_collection2)

    async def test_id_unicode_validation(self):
        # create database
        created_db = self.databaseForTest

        # unicode chars in Hindi for Id which translates to: "Hindi is the national language of India"
        collection_id1 = u'हिन्दी भारत की राष्ट्रीय भाषा है' # cspell:disable-line

        # Special chars for Id
        collection_id2 = "!@$%^&*()-~`'_[]{}|;:,.<>"

        # verify that collections are created with specified IDs
        created_collection1 = await created_db.create_container(
            id=collection_id1,
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        created_collection2 = await created_db.create_container(
            id=collection_id2,
            partition_key=PartitionKey(path='/id', kind='Hash')
        )

        self.assertEqual(collection_id1, created_collection1.id)
        self.assertEqual(collection_id2, created_collection2.id)

        created_collection1_properties = await created_collection1.read()
        created_collection2_properties = await created_collection2.read()

        await created_db.delete_container(created_collection1_properties)
        await created_db.delete_container(created_collection2_properties)

    async def test_get_resource_with_dictionary_and_object(self):
        created_db = self.databaseForTest

        # read database with id
        read_db = self.client.get_database_client(created_db.id)
        self.assertEqual(read_db.id, created_db.id)

        # read database with instance
        read_db = self.client.get_database_client(created_db)
        self.assertEqual(read_db.id, created_db.id)

        # read database with properties
        read_db = self.client.get_database_client(await created_db.read())
        self.assertEqual(read_db.id, created_db.id)

        created_container = await self.databaseForTest.create_container(test_config._test_config.TEST_COLLECTION_MULTI_PARTITION, PartitionKey(path="/id"))

        # read container with id
        read_container = created_db.get_container_client(created_container.id)
        self.assertEqual(read_container.id, created_container.id)

        # read container with instance
        read_container = created_db.get_container_client(created_container)
        self.assertEqual(read_container.id, created_container.id)

        # read container with properties
        created_properties = await created_container.read()
        read_container = created_db.get_container_client(created_properties)
        self.assertEqual(read_container.id, created_container.id)

        created_item = await created_container.create_item({'id': '1' + str(uuid.uuid4())})

        # read item with id
        read_item = await created_container.read_item(item=created_item['id'], partition_key=created_item['id'])
        self.assertEqual(read_item['id'], created_item['id'])

        # read item with properties
        read_item = await created_container.read_item(item=created_item, partition_key=created_item['id'])
        self.assertEqual(read_item['id'], created_item['id'])

        created_sproc = await created_container.scripts.create_stored_procedure({
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': 'function () { }'
        })

        # read sproc with id
        read_sproc = await created_container.scripts.get_stored_procedure(created_sproc['id'])
        self.assertEqual(read_sproc['id'], created_sproc['id'])

        # read sproc with properties
        read_sproc = await created_container.scripts.get_stored_procedure(created_sproc)
        self.assertEqual(read_sproc['id'], created_sproc['id'])

        created_trigger = await created_container.scripts.create_trigger({
            'id': 'sample trigger' + str(uuid.uuid4()),
            'serverScript': 'function() {var x = 10;}',
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        })

        # read trigger with id
        read_trigger = await created_container.scripts.get_trigger(created_trigger['id'])
        self.assertEqual(read_trigger['id'], created_trigger['id'])

        # read trigger with properties
        read_trigger = await created_container.scripts.get_trigger(created_trigger)
        self.assertEqual(read_trigger['id'], created_trigger['id'])

        created_udf = await created_container.scripts.create_user_defined_function({
            'id': 'sample udf' + str(uuid.uuid4()),
            'body': 'function() {var x = 10;}'
        })

        # read udf with id
        read_udf = await created_container.scripts.get_user_defined_function(created_udf['id'])
        self.assertEqual(created_udf['id'], read_udf['id'])

        # read udf with properties
        read_udf = await created_container.scripts.get_user_defined_function(created_udf)
        self.assertEqual(created_udf['id'], read_udf['id'])

        created_user = await created_db.create_user({
            'id': 'user' + str(uuid.uuid4())
        })

        # read user with id
        read_user = created_db.get_user_client(created_user.id)
        self.assertEqual(read_user.id, created_user.id)

        # read user with instance
        read_user = created_db.get_user_client(created_user)
        self.assertEqual(read_user.id, created_user.id)

        # read user with properties
        created_user_properties = await created_user.read()
        read_user = created_db.get_user_client(created_user_properties)
        self.assertEqual(read_user.id, created_user.id)

        created_permission = await created_user.create_permission({
            'id': 'all permission' + str(uuid.uuid4()),
            'permissionMode': documents.PermissionMode.All,
            'resource': created_container.container_link,
            'resourcePartitionKey': [1]
        })

        # read permission with id
        read_permission = await created_user.get_permission(created_permission.id)
        self.assertEqual(read_permission.id, created_permission.id)

        # read permission with instance
        read_permission = await created_user.get_permission(created_permission)
        self.assertEqual(read_permission.id, created_permission.id)

        # read permission with properties
        read_permission = await created_user.get_permission(created_permission.properties)
        self.assertEqual(read_permission.id, created_permission.id)

    # Commenting out delete all items by pk until pipelines support it
    # async def test_delete_all_items_by_partition_key(self):
    #     # create database
    #     created_db = self.databaseForTest
    #
    #     # create container
    #     created_collection = await created_db.create_container(
    #         id='test_delete_all_items_by_partition_key ' + str(uuid.uuid4()),
    #         partition_key=PartitionKey(path='/pk', kind='Hash')
    #     )
    #     # Create two partition keys
    #     partition_key1 = "{}-{}".format("Partition Key 1", str(uuid.uuid4()))
    #     partition_key2 = "{}-{}".format("Partition Key 2", str(uuid.uuid4()))
    #
    #     # add items for partition key 1
    #     for i in range(1, 3):
    #         await created_collection.upsert_item(
    #             dict(id="item{}".format(i), pk=partition_key1)
    #         )
    #
    #     # add items for partition key 2
    #     pk2_item = await created_collection.upsert_item(dict(id="item{}".format(3), pk=partition_key2))
    #
    #     # delete all items for partition key 1
    #     await created_collection.delete_all_items_by_partition_key(partition_key1)
    #
    #     # check that only items from partition key 1 have been deleted
    #     items = [item async for item in created_collection.read_all_items()]
    #
    #     # items should only have 1 item, and it should equal pk2_item
    #     self.assertDictEqual(pk2_item, items[0])
    #
    #     # attempting to delete a non-existent partition key or passing none should not delete
    #     # anything and leave things unchanged
    #     await created_collection.delete_all_items_by_partition_key(None)
    #
    #     # check that no changes were made by checking if the only item is still there
    #     items = [item async for item in created_collection.read_all_items()]
    #
    #     # items should only have 1 item, and it should equal pk2_item
    #     self.assertDictEqual(pk2_item, items[0])
    #
    #     await created_db.delete_container(created_collection)

    async def test_patch_operations(self):
        created_container = await self.databaseForTest.create_container_if_not_exists(id="patch_container", partition_key=PartitionKey(path="/pk"))

        #Create item to patch
        item = {
            "id": "patch_item",
            "pk": "patch_item_pk",
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        await created_container.create_item(item)
        #Define and run patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]
        patched_item = await created_container.patch_item(item="patch_item", partition_key="patch_item_pk", patch_operations=operations)
        #Verify results from patch operations
        self.assertTrue(patched_item.get("color") is None)
        self.assertTrue(patched_item.get("prop") is None)
        self.assertEqual(patched_item.get("company"), "CosmosDB")
        self.assertEqual(patched_item.get("address").get("new_city"), "Atlanta")
        self.assertEqual(patched_item.get("number"), 10)
        self.assertEqual(patched_item.get("favorite_color"), "yellow")

        #Negative test - attempt to replace non-existent field
        operations = [{"op": "replace", "path": "/wrong_field", "value": "wrong_value"}]
        try:
            await created_container.patch_item(item="patch_item", partition_key="patch_item_pk", patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, StatusCodes.BAD_REQUEST)

        #Negative test - attempt to remove non-existent field
        operations = [{"op": "remove", "path": "/wrong_field"}]
        try:
            await created_container.patch_item(item="patch_item", partition_key="patch_item_pk", patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, StatusCodes.BAD_REQUEST)

        #Negative test - attempt to increment non-number field
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        try:
            await created_container.patch_item(item="patch_item", partition_key="patch_item_pk", patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, StatusCodes.BAD_REQUEST)

        #Negative test - attempt to move from non-existent field
        operations = [{"op": "move", "from": "/wrong_field", "path": "/other_field"}]
        try:
            await created_container.patch_item(item="patch_item", partition_key="patch_item_pk", patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, StatusCodes.BAD_REQUEST)

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

    async def _MockExecuteFunction(self, function, *args, **kwargs):
        self.last_headers.append(args[4].headers[HttpHeaders.PartitionKey]
                                 if HttpHeaders.PartitionKey in args[4].headers else '')
        return await self.OriginalExecuteFunction(function, *args, **kwargs)

