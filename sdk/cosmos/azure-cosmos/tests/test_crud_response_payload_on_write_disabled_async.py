# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test.
"""
import json
import logging
import os.path
import time
import unittest
import urllib.parse as urllib
import uuid
from typing import Any, Dict, Optional

import pytest
import requests
from azure.core import MatchConditions
from azure.core.exceptions import AzureError, ServiceResponseError
from azure.core.pipeline.transport import AsyncioRequestsTransport, AsyncioRequestsTransportResponse

import azure.cosmos._base as base
import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos.aio import CosmosClient, _retry_utility_async, DatabaseProxy
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.partition_key import PartitionKey

class CosmosResponseHeaderEnvelope:
    def __init__(self):
        self.headers: Optional[Dict[str, Any]] = None

    def capture_response_headers(self, headers: Dict[str, Any], response: Dict[str, Any]):
        self.headers = headers

class TimeoutTransport(AsyncioRequestsTransport):

    def __init__(self, response):
        self._response = response
        super(TimeoutTransport, self).__init__()

    async def send(self, *args, **kwargs):
        if kwargs.pop("passthrough", False):
            return super(TimeoutTransport, self).send(*args, **kwargs)

        time.sleep(5)
        if isinstance(self._response, Exception):
            raise self._response
        current_response = await self._response
        output = requests.Response()
        output.status_code = current_response
        response = AsyncioRequestsTransportResponse(None, output)
        return response


@pytest.mark.cosmosLong
class TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled(unittest.IsolatedAsyncioTestCase):
    """Python CRUD Tests.
    """
    client: CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []
    database_for_test: DatabaseProxy = None

    async def __assert_http_failure_with_status(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            await func(*args, **kwargs)
            self.fail('function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            assert inst.status_code == status_code

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey, no_response_on_write=True)
        self.database_for_test = self.client.get_database_client(self.configs.TEST_DATABASE_ID)
        self.logger = logging.getLogger("TestCRUDOperationsAsyncResponsePayloadOnWriteDisabledLogger")
        self.logger.setLevel(logging.DEBUG)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_database_crud_async(self):
        database_id = str(uuid.uuid4())
        created_db = await self.client.create_database(database_id)
        assert created_db.id == database_id
        # query databases.
        databases = [database async for database in self.client.query_databases(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': database_id}
            ]
        )]

        assert len(databases) > 0

        # read database.
        self.client.get_database_client(created_db.id)
        await created_db.read()

        # delete database.
        await self.client.delete_database(created_db.id)
        # read database after deletion
        read_db = self.client.get_database_client(created_db.id)
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND, read_db.read)

        database_proxy = await self.client.create_database_if_not_exists(id=database_id, offer_throughput=5000)
        assert database_id == database_proxy.id
        db_throughput = await database_proxy.get_throughput()
        assert 5000 == db_throughput.offer_throughput

        database_proxy = await self.client.create_database_if_not_exists(id=database_id, offer_throughput=6000)
        assert database_id == database_proxy.id
        db_throughput = await database_proxy.get_throughput()
        assert 5000 == db_throughput.offer_throughput

        # delete database.
        await self.client.delete_database(database_id)

    async def test_database_level_offer_throughput_async(self):
        # Create a database with throughput
        offer_throughput = 1000
        database_id = str(uuid.uuid4())
        created_db = await self.client.create_database(
            id=database_id,
            offer_throughput=offer_throughput
        )
        assert created_db.id == database_id

        # Verify offer throughput for database
        offer = await created_db.get_throughput()
        assert offer.offer_throughput == offer_throughput

        # Update database offer throughput
        new_offer_throughput = 2000
        offer = await created_db.replace_throughput(new_offer_throughput)
        assert offer.offer_throughput == new_offer_throughput

        await self.client.delete_database(database_id)

    async def test_sql_query_crud_async(self):
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
        assert 1 == len(databases)

        # query without parameters.
        databases = [database async for database in self.client.query_databases(
            query='SELECT * FROM root r WHERE r.id="database non-existing"'
        )]
        assert 0 == len(databases)

        # query with a string.
        query_string = 'SELECT * FROM root r WHERE r.id="' + db2.id + '"'
        databases = [database async for database in
                     self.client.query_databases(query=query_string)]
        assert 1 == len(databases)

        await self.client.delete_database(db1.id)
        await self.client.delete_database(db2.id)

    async def test_collection_crud_async(self):
        created_db = self.database_for_test
        collections = [collection async for collection in created_db.list_containers()]
        # create a collection
        before_create_collections_count = len(collections)
        collection_id = 'test_collection_crud ' + str(uuid.uuid4())
        collection_indexing_policy = {'indexingMode': 'consistent'}
        created_collection = await created_db.create_container(id=collection_id,
                                                               indexing_policy=collection_indexing_policy,
                                                               partition_key=PartitionKey(path="/pk", kind="Hash"))
        assert collection_id == created_collection.id

        created_properties = await created_collection.read()
        assert 'consistent' == created_properties['indexingPolicy']['indexingMode']
        assert PartitionKey(path='/pk', kind='Hash') == created_properties['partitionKey']

        # read collections after creation
        collections = [collection async for collection in created_db.list_containers()]
        assert len(collections) == before_create_collections_count + 1
        # query collections
        collections = [collection async for collection in created_db.query_containers(

            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': collection_id}
            ]
        )]

        assert len(collections) > 0
        # delete collection
        await created_db.delete_container(created_collection.id)
        # read collection after deletion
        created_container = created_db.get_container_client(created_collection.id)
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     created_container.read)

    async def test_partitioned_collection_async(self):
        created_db = self.database_for_test

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

        assert collection_definition.get('id') == created_collection.id

        created_collection_properties = await created_collection.read()
        assert collection_definition.get('partitionKey').get('paths')[0] == \
               created_collection_properties['partitionKey']['paths'][0]
        assert collection_definition.get('partitionKey').get('kind') == created_collection_properties['partitionKey'][
            'kind']

        expected_offer = await created_collection.get_throughput()

        assert expected_offer is not None

        assert expected_offer.offer_throughput == offer_throughput

        await created_db.delete_container(created_collection.id)

    async def test_partitioned_collection_quota_async(self):
        created_db = self.database_for_test

        created_collection = self.database_for_test.get_container_client(
            self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        retrieved_collection_properties = await created_collection.read(
            populate_partition_key_range_statistics=True,
            populate_quota_info=True)
        assert retrieved_collection_properties.get("statistics") is not None
        assert created_db.client_connection.last_response_headers.get("x-ms-resource-usage") is not None

    async def test_partitioned_collection_partition_key_extraction_async(self):
        created_db = self.database_for_test

        collection_id = 'test_partitioned_collection_partition_key_extraction ' + str(uuid.uuid4())
        created_collection = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/address/state', kind=documents.PartitionKind.Hash)
        )

        document_definition = {'id': 'document1A',
                               'address': {'street': '1 Microsoft Way',
                                           'city': 'Redmond',
                                           'state': 'WA',
                                           'zip code': 98052
                                           }
                               }

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._mock_execute_function
        # create document without partition key being specified
        created_document = await created_collection.create_item(body=document_definition, no_response=True)
        self.assertDictEqual(created_document,{})
        document_definition["id"]= "document1"
        created_document = await created_collection.create_item(body=document_definition, no_response=False)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        assert self.last_headers[0] == '["WA"]'
        del self.last_headers[:]

        assert created_document.get('id') == document_definition.get('id')
        assert created_document.get('address').get('state') == document_definition.get('address').get('state')

        collection_id = 'test_partitioned_collection_partition_key_extraction1 ' + str(uuid.uuid4())
        created_collection1 = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/address', kind=documents.PartitionKind.Hash)
        )

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._mock_execute_function
        # Create document with partitionkey not present as a leaf level property but a dict
        await created_collection1.create_item(document_definition)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        assert self.last_headers[0] == [{}]
        del self.last_headers[:]

        collection_id = 'test_partitioned_collection_partition_key_extraction2 ' + str(uuid.uuid4())
        created_collection2 = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/address/state/city', kind=documents.PartitionKind.Hash)
        )

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._mock_execute_function
        # Create document with partitionkey not present in the document
        await created_collection2.create_item(document_definition)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        assert self.last_headers[0] == [{}]
        del self.last_headers[:]

        await created_db.delete_container(created_collection.id)
        await created_db.delete_container(created_collection1.id)
        await created_db.delete_container(created_collection2.id)

    async def test_partitioned_collection_partition_key_extraction_special_chars_async(self):
        created_db = self.database_for_test

        collection_id = 'test_partitioned_collection_partition_key_extraction_special_chars1 ' + str(uuid.uuid4())

        created_collection1 = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/\"level\' 1*()\"/\"le/vel2\"', kind=documents.PartitionKind.Hash)
        )
        document_definition = {'id': 'document1',
                               "level' 1*()": {"le/vel2": 'val1'}
                               }

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._mock_execute_function
        await created_collection1.create_item(body=document_definition)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        assert self.last_headers[0] == '["val1"]'
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
        _retry_utility_async.ExecuteFunctionAsync = self._mock_execute_function
        # create document without partition key being specified
        await created_collection2.create_item(body=document_definition)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        assert self.last_headers[0] == '["val2"]'
        del self.last_headers[:]

        await created_db.delete_container(created_collection1.id)
        await created_db.delete_container(created_collection2.id)

    def test_partitioned_collection_path_parser(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(test_dir, "BaselineTest.PathParser.json")) as json_file:
            entries = json.loads(json_file.read())
        for entry in entries:
            parts = base.ParsePaths([entry['path']])
            assert parts == entry['parts']

        paths = ["/\"Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1\"/*"]
        parts = ["Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1", "*"]
        assert parts == base.ParsePaths(paths)

        paths = ["/'Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1'/*"]
        parts = ["Ke \\ \\\" \\\' \\? \\a \\\b \\\f \\\n \\\r \\\t \\v y1", "*"]
        assert parts == base.ParsePaths(paths)

    async def test_partitioned_collection_document_crud_and_query_async(self):
        created_collection = await self.database_for_test.create_container(str(uuid.uuid4()), PartitionKey(path="/id"))

        document_definition = {'id': 'document',
                               'key': 'value'}

        created_document = await created_collection.create_item(body=document_definition)
        self.assertDictEqual(created_document, {})
        created_document = await created_collection.upsert_item(body=document_definition)
        self.assertDictEqual(created_document, {})
        created_document = await created_collection.upsert_item(body=document_definition, no_response=True)
        self.assertDictEqual(created_document, {})
        created_document = await created_collection.upsert_item(body=document_definition, no_response=False)
        assert created_document is not {}

        assert created_document.get('id') == document_definition.get('id')
        assert created_document.get('key') == document_definition.get('key')

        # read document
        read_document = await created_collection.read_item(
            item=created_document.get('id'),
            partition_key=created_document.get('id')
        )

        assert read_document.get('id') == created_document.get('id')
        assert read_document.get('key') == created_document.get('key')

        # Read document feed doesn't require partitionKey as it's always a cross partition query
        document_list = [document async for document in created_collection.read_all_items()]
        assert 1 == len(document_list)

        # replace document
        document_definition['key'] = 'new value'

        replaced_document = await created_collection.replace_item(
            item=read_document,
            body=document_definition
        )
        self.assertDictEqual(replaced_document, {})
        replaced_document = await created_collection.replace_item(
            item=read_document,
            body=document_definition,
            no_response=True
        )
        self.assertDictEqual(replaced_document, {})
        replaced_document = await created_collection.replace_item(
            item=read_document,
            body=document_definition,
            no_response=False
        )
        assert replaced_document is not None

        assert replaced_document.get('key') == document_definition.get('key')

        # upsert document(create scenario)
        document_definition['id'] = 'document2'
        document_definition['key'] = 'value2'

        upserted_document = await created_collection.upsert_item(body=document_definition, no_response=False)

        assert upserted_document.get('id') == document_definition.get('id')
        assert upserted_document.get('key') == document_definition.get('key')

        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == 2

        # delete document
        await created_collection.delete_item(item=upserted_document, partition_key=upserted_document.get('id'))

        # query document on the partition key specified in the predicate will pass even without setting enableCrossPartitionQuery or passing in the partitionKey value
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.id=\'' + replaced_document.get('id') + '\''  # nosec
        )]
        assert len(document_list) == 1

        # cross partition query
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'')]

        assert len(document_list) == 1

        # query document by providing the partitionKey value
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            partition_key=replaced_document.get('id')
        )]

        assert len(document_list) == 1
        await self.database_for_test.delete_container(created_collection.id)

    async def test_partitioned_collection_permissions_async(self):
        created_db = self.database_for_test

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
        resource_tokens["dbs/" + created_db.id + "/colls/" + read_collection.id] = (
            read_permission.properties['_token'])

        async with CosmosClient(TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.host, resource_tokens) as restricted_client:
            print('Async Initialization')

            document_definition = {'id': 'document1',
                                   'key': 1
                                   }

            all_collection.client_connection = restricted_client.client_connection
            read_collection.client_connection = restricted_client.client_connection

            # Create document in all_collection should succeed since the partitionKey is 1 which is what specified as resourcePartitionKey in permission object and it has all permissions
            created_document = await all_collection.create_item(body=document_definition)

            # Create document in read_collection should fail since it has only read permissions for this collection
            await self.__assert_http_failure_with_status(
                StatusCodes.FORBIDDEN,
                read_collection.create_item,
                document_definition)

            document_definition['key'] = 2
            # Create document should fail since the partitionKey is 2 which is different that what is specified as resourcePartitionKey in permission object
            await self.__assert_http_failure_with_status(
                StatusCodes.FORBIDDEN,
                all_collection.create_item,
                document_definition)

            document_definition['key'] = 1
            # Delete document should succeed since the partitionKey is 1 which is what specified as resourcePartitionKey in permission object
            await all_collection.delete_item(item=created_document['id'],
                                             partition_key=document_definition['key'])

            # Delete document in read_collection should fail since it has only read permissions for this collection
            await self.__assert_http_failure_with_status(
                StatusCodes.FORBIDDEN,
                read_collection.delete_item,
                document_definition['id'],
                document_definition['id']
            )

            await self.database_for_test.delete_container(all_collection.id)
            await self.database_for_test.delete_container(read_collection.id)

    async def test_partitioned_collection_execute_stored_procedure_async(self):

        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
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

        created_sproc = await created_collection.scripts.create_stored_procedure(body=sproc)

        # Partiton Key value same as what is specified in the stored procedure body
        result = await created_collection.scripts.execute_stored_procedure(sproc=created_sproc['id'], partition_key=2)
        assert result == 1

        # Partiton Key value different than what is specified in the stored procedure body will cause a bad request(400) error
        await self.__assert_http_failure_with_status(
            StatusCodes.BAD_REQUEST,
            created_collection.scripts.execute_stored_procedure,
            created_sproc['id'])

    async def test_partitioned_collection_partition_key_value_types_async(self):

        created_db = self.database_for_test

        created_collection = created_db.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

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
        await self.__assert_http_failure_with_status(
            StatusCodes.BAD_REQUEST,
            created_collection.create_item,
            document_definition
        )

    async def test_partitioned_collection_conflict_crud_and_query_async(self):

        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        conflict_definition = {'id': 'new conflict',
                               'resourceId': 'doc1',
                               'operationType': 'create',
                               'resourceType': 'document'
                               }

        # read conflict here will return resource not found(404) since there is no conflict here
        await self.__assert_http_failure_with_status(
            StatusCodes.NOT_FOUND,
            created_collection.get_conflict,
            conflict_definition['id'],
            conflict_definition['id']
        )

        # Read conflict feed doesn't require partitionKey to be specified as it's a cross partition thing
        conflict_list = [conflict async for conflict in created_collection.list_conflicts()]
        assert len(conflict_list) == 0

        # delete conflict here will return resource not found(404) since there is no conflict here
        await self.__assert_http_failure_with_status(
            StatusCodes.NOT_FOUND,
            created_collection.delete_conflict,
            conflict_definition['id'],
            conflict_definition['id']
        )

        conflict_list = [conflict async for conflict in created_collection.query_conflicts(
            query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'')]

        assert len(conflict_list) == 0

        # query conflicts by providing the partitionKey value
        options = {'partitionKey': conflict_definition.get('id')}
        conflict_list = [conflict async for conflict in created_collection.query_conflicts(
            query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'',
            # nosec
            partition_key=conflict_definition['id']
        )]

        assert len(conflict_list) == 0

    async def test_document_crud_async(self):

        # create collection
        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # read documents
        document_list = [document async for document in created_collection.read_all_items()]
        # create a document
        before_create_documents_count = len(document_list)

        # create a document with auto ID generation
        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk'}

        created_document = await created_collection.create_item(body=document_definition,
                                                                enable_automatic_id_generation=True,
                                                                no_response=False)
        assert created_document.get('name') == document_definition['name']

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk',
                               'id': str(uuid.uuid4())}

        created_document = await created_collection.create_item(body=document_definition)
        self.assertDictEqual(created_document, {})

        document_definition["id"] = str(uuid.uuid4())
        created_document = await created_collection.create_item(body=document_definition, no_response=True)
        self.assertDictEqual(created_document, {})

        document_definition["id"] = str(uuid.uuid4())
        created_document = await created_collection.create_item(body=document_definition, no_response=False)
        assert created_document is not {}

        assert created_document.get('name') == document_definition['name']
        assert created_document.get('id') == document_definition['id']

        # duplicated documents are not allowed when 'id' is provided.
        duplicated_definition_with_id = document_definition.copy()
        await self.__assert_http_failure_with_status(StatusCodes.CONFLICT,
                                                     created_collection.create_item,
                                                     duplicated_definition_with_id)
        # read documents after creation
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 4
        # query documents
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.name=@name',
            parameters=[{'name': '@name', 'value': document_definition['name']}]
        )]
        assert document_list is not None
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.name=@name',
            parameters=[
                {'name': '@name', 'value': document_definition['name']}
            ],
            enable_scan_in_query=True
        )]
        assert document_list is not None

        # replace document.
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'
        old_etag = created_document['_etag']
        replaced_document = await created_collection.replace_item(
            item=created_document['id'],
            body=created_document
        )
        self.assertDictEqual(replaced_document, {})

        replaced_document = await created_collection.replace_item(
            item=created_document['id'],
            body=created_document,
            no_response=True
        )
        self.assertDictEqual(replaced_document, {})

        replaced_document = await created_collection.replace_item(
            item=created_document['id'],
            body=created_document,
            no_response=False
        )
        assert replaced_document is not None

        assert replaced_document['name'] == 'replaced document'
        assert replaced_document['spam'] == 'not eggs'
        assert created_document['id'] == replaced_document['id']

        # replace document based on condition
        replaced_document['name'] = 'replaced document based on condition'
        replaced_document['spam'] = 'new spam field'

        # should fail for stale etag
        await self.__assert_http_failure_with_status(
            StatusCodes.PRECONDITION_FAILED,
            created_collection.replace_item,
            replaced_document['id'],
            replaced_document,
            if_match=old_etag,
        )

        # should fail if only etag specified
        try:
            await created_collection.replace_item(
                etag=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if only etag specified")
        except ValueError:
            pass

        # should fail if only match condition specified
        try:
            await created_collection.replace_item(
                match_condition=MatchConditions.IfNotModified,
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if only match condition specified")
        except ValueError:
            pass

        try:
            await created_collection.replace_item(
                match_condition=MatchConditions.IfModified,
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if only match condition specified")
        except ValueError:
            pass

        # should fail if invalid match condition specified
        try:
            await created_collection.replace_item(
                match_condition=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if invalid match condition specified")
        except TypeError:
            pass

        # should pass for most recent etag
        headerEnvelope=CosmosResponseHeaderEnvelope()
        replaced_document_conditional = await created_collection.replace_item(
            match_condition=MatchConditions.IfNotModified,
            etag=replaced_document['_etag'],
            item=replaced_document['id'],
            body=replaced_document,
            response_hook=headerEnvelope.capture_response_headers
        )
        self.assertDictEqual(replaced_document_conditional, {})
        replaced_document_conditional = await created_collection.read_item(
            item=replaced_document['id'],
            partition_key=replaced_document['pk'])

        assert replaced_document_conditional is not None
        assert replaced_document_conditional['_etag'] == headerEnvelope.headers["etag"]
        assert replaced_document_conditional['name'] == 'replaced document based on condition'
        assert replaced_document_conditional['spam'] == 'new spam field'
        assert replaced_document_conditional['id'] == replaced_document['id']

        # read document
        one_document_from_read = await created_collection.read_item(
            item=replaced_document['id'],
            partition_key=replaced_document['pk']
        )
        assert replaced_document['id'] == one_document_from_read['id']
        # delete document
        await created_collection.delete_item(
            item=replaced_document,
            partition_key=replaced_document['pk']
        )
        # read documents after deletion
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     created_collection.read_item,
                                                     replaced_document['id'],
                                                     replaced_document['id'])

    async def test_document_upsert_async(self):

        # create collection
        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # read documents and check count
        document_list = [document async for document in created_collection.read_all_items()]
        before_create_documents_count = len(document_list)

        # create document definition
        document_definition = {'id': 'doc',
                               'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk'}

        # create document using Upsert API
        created_document = await created_collection.upsert_item(body=document_definition)
        self.assertDictEqual(created_document, {})
        created_document = await created_collection.upsert_item(body=document_definition, no_response=True)
        self.assertDictEqual(created_document, {})
        created_document = await created_collection.upsert_item(body=document_definition, no_response=False)
        assert created_document is not None

        # verify id property
        assert created_document['id'] == document_definition['id']

        # test error for non-string id
        with self.assertRaises(TypeError):
            document_definition['id'] = 7
            await created_collection.upsert_item(body=document_definition)

        # read documents after creation and verify updated count
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 1

        # update document
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'

        # should replace document since it already exists
        upserted_document = await created_collection.upsert_item(body=created_document, no_response=False)

        # verify the changed properties
        assert upserted_document['name'] == created_document['name']
        assert upserted_document['spam'] == created_document['spam']

        # verify id property
        assert upserted_document['id'] == created_document['id']

        # read documents after upsert and verify count doesn't increases again
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 1

        created_document['id'] = 'new id'

        # Upsert should create new document since the id is different
        new_document = await created_collection.upsert_item(body=created_document, no_response=False)

        # Test modified access conditions
        created_document['spam'] = 'more eggs'
        await created_collection.upsert_item(body=created_document)
        with self.assertRaises(exceptions.CosmosHttpResponseError):
            await created_collection.upsert_item(
                body=created_document,
                match_condition=MatchConditions.IfNotModified,
                etag=new_document['_etag'])

        # verify id property
        assert created_document['id'] == new_document['id']

        # read documents after upsert and verify count increases
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 2

        # delete documents
        await created_collection.delete_item(item=upserted_document, partition_key=upserted_document['pk'])
        await created_collection.delete_item(item=new_document, partition_key=new_document['pk'])

        # read documents after delete and verify count is same as original
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count

    async def test_geospatial_index_async(self):
        db = self.database_for_test
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
            query="SELECT * FROM root WHERE (ST_DISTANCE(root.Location, {type: 'Point', coordinates: [20.1, 20]}) < 20000)")]
        assert len(results) == 1
        assert 'loc1' == results[0]['id']

    # CRUD test for User resource

    async def test_user_crud_async(self):

        # Should do User CRUD operations successfully.
        # create database
        db = self.database_for_test
        # list users
        users = [user async for user in db.list_users()]
        before_create_count = len(users)
        # create user
        user_id = 'new user' + str(uuid.uuid4())
        user = await db.create_user(body={'id': user_id})
        assert user.id == user_id
        # list users after creation
        users = [user async for user in db.list_users()]
        assert len(users) == before_create_count + 1
        # query users
        results = [user async for user in db.query_users(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': user_id}
            ]
        )]
        assert results is not None

        # replace user
        replaced_user_id = 'replaced user' + str(uuid.uuid4())
        user_properties = await user.read()
        user_properties['id'] = replaced_user_id
        replaced_user = await db.replace_user(user_id, user_properties)
        assert replaced_user.id == replaced_user_id
        assert user_properties['id'] == replaced_user.id

        # read user
        user = db.get_user_client(replaced_user.id)
        assert replaced_user.id == user.id

        # delete user
        await db.delete_user(user.id)

        # read user after deletion
        deleted_user = db.get_user_client(user.id)
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     deleted_user.read)

    async def test_user_upsert_async(self):

        # create database
        db = self.database_for_test

        # read users and check count
        users = [user async for user in db.list_users()]
        before_create_count = len(users)

        # create user using Upsert API
        user_id = 'user' + str(uuid.uuid4())
        user = await db.upsert_user(body={'id': user_id})

        # verify id property
        assert user.id == user_id

        # read users after creation and verify updated count
        users = [user async for user in db.list_users()]
        assert len(users) == before_create_count + 1

        # Should replace the user since it already exists, there is no public property to change here
        user_properties = await user.read()
        upserted_user = await db.upsert_user(user_properties)

        # verify id property
        assert upserted_user.id == user.id

        # read users after upsert and verify count doesn't increase again
        users = [user async for user in db.list_users()]
        assert len(users) == before_create_count + 1

        user_properties = await user.read()
        user_properties['id'] = 'new user' + str(uuid.uuid4())
        user.id = user_properties['id']

        # Upsert should create new user since id is different
        new_user = await db.upsert_user(user_properties)

        # verify id property
        assert new_user.id == user.id

        # read users after upsert and verify count increases
        users = [user async for user in db.list_users()]
        assert len(users) == before_create_count + 2

        # delete users
        await db.delete_user(upserted_user.id)
        await db.delete_user(new_user.id)

        # read users after delete and verify count remains the same
        users = [user async for user in db.list_users()]
        assert len(users) == before_create_count

    async def test_permission_crud_async(self):

        # create database
        db = self.database_for_test
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
        assert permission.id == 'new permission'
        # list permissions after creation
        permissions = [permission async for permission in user.list_permissions()]
        assert len(permissions) == before_create_count + 1
        # query permissions
        results = [permission async for permission in user.query_permissions(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': permission.id}
            ]
        )]
        assert results is not None

        # replace permission
        change_permission = permission.properties.copy()
        permission.properties['id'] = 'replaced permission'
        permission.id = permission.properties['id']
        replaced_permission = await user.replace_permission(change_permission['id'], permission.properties)
        assert replaced_permission.id == 'replaced permission'
        assert permission.id == replaced_permission.id
        # read permission
        permission = await user.get_permission(replaced_permission.id)
        assert replaced_permission.id == permission.id
        # delete permission
        await user.delete_permission(replaced_permission.id)
        # read permission after deletion
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     user.get_permission,
                                                     permission.id)

    async def test_permission_upsert_async(self):

        # create database
        db = self.database_for_test

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
        assert created_permission.id == permission_definition['id']

        # read permissions after creation and verify updated count
        permissions = [permission async for permission in user.list_permissions()]
        assert len(permissions) == before_create_count + 1

        # update permission mode
        permission_definition['permissionMode'] = documents.PermissionMode.All

        # should repace the permission since it already exists
        upserted_permission = await user.upsert_permission(permission_definition)
        # verify id property
        assert upserted_permission.id == created_permission.id

        # verify changed property
        assert upserted_permission.permission_mode == permission_definition['permissionMode']

        # read permissions and verify count doesn't increase again
        permissions = [permission async for permission in user.list_permissions()]
        assert len(permissions) == before_create_count + 1

        # update permission id
        created_permission.properties['id'] = 'new permission'
        created_permission.id = created_permission.properties['id']
        # resource needs to be changed along with the id in order to create a new permission
        created_permission.properties['resource'] = 'dbs/N9EdAA==/colls/N9EdAIugXgA='
        created_permission.resource_link = created_permission.properties['resource']

        # should create new permission since id has changed
        new_permission = await user.upsert_permission(created_permission.properties)

        # verify id and resource property
        assert new_permission.id == created_permission.id

        assert new_permission.resource_link == created_permission.resource_link

        # read permissions and verify count increases
        permissions = [permission async for permission in user.list_permissions()]
        assert len(permissions) == before_create_count + 2

        # delete permissions
        await user.delete_permission(upserted_permission.id)
        await user.delete_permission(new_permission.id)

        # read permissions and verify count remains the same
        permissions = [permission async for permission in user.list_permissions()]
        assert len(permissions) == before_create_count

    async def test_authorization_async(self):

        async def __setup_entities():
            """
            Sets up entities for this test.

            :Parameters:
                - `client`: cosmos_client_connection.CosmosClientConnection

            :Returns:
                dict

            """
            # create database
            db = self.database_for_test
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
                no_response=False      
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
            assert permission_on_coll.properties['_token'] is not None

            # create permission for document
            permission = {
                'id': 'permission On Doc',
                'permissionMode': documents.PermissionMode.All,
                'resource': "dbs/" + db.id + "/colls/" + collection.id + "/docs/" + document["id"]
            }
            permission_on_doc = await user.create_permission(body=permission)
            assert permission_on_doc.properties['_token'] is not None

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
            async with CosmosClient(TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.host, {}) as client:
                [db async for db in client.list_databases()]
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.UNAUTHORIZED

        # Client with master key.
        async with CosmosClient(TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.host,
                                TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.masterKey) as client:
            # setup entities
            entities = await __setup_entities()
            resource_tokens = {"dbs/" + entities['db'].id + "/colls/" + entities['coll'].id:
                                   entities['permissionOnColl'].properties['_token']}

        async with CosmosClient(
                TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.host, resource_tokens) as col_client:
            db = entities['db']

            old_client_connection = db.client_connection
            db.client_connection = col_client.client_connection
            # 1. Success-- Use Col Permission to Read
            success_coll = db.get_container_client(container=entities['coll'])
            # 2. Failure-- Use Col Permission to delete
            await self.__assert_http_failure_with_status(StatusCodes.FORBIDDEN,
                                                         db.delete_container,
                                                         success_coll)
            # 3. Success-- Use Col Permission to Read All Docs
            success_documents = [document async for document in success_coll.read_all_items()]
            assert success_documents is not None
            assert len(success_documents) == 1
            # 4. Success-- Use Col Permission to Read Doc

            doc_id = entities['doc']['id']
            success_doc = await success_coll.read_item(
                item=doc_id,
                partition_key=doc_id
            )
            assert success_doc is not None
            assert success_doc['id'] == entities['doc']['id']

            # 5. Failure-- Use Col Permission to Delete Doc
            await self.__assert_http_failure_with_status(StatusCodes.FORBIDDEN,
                                                         success_coll.delete_item,
                                                         doc_id, doc_id)

            resource_tokens = {"dbs/" + entities['db'].id + "/colls/" + entities['coll'].id + "/docs/" + doc_id:
                                   entities['permissionOnDoc'].properties['_token']}

        async with CosmosClient(
                TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.host, resource_tokens) as doc_client:

            # 6. Success-- Use Doc permission to read doc
            read_doc = await doc_client.get_database_client(db.id).get_container_client(success_coll.id).read_item(
                doc_id, doc_id)
            assert read_doc["id"] == doc_id

            # 6. Success-- Use Doc permission to delete doc
            await doc_client.get_database_client(db.id).get_container_client(success_coll.id).delete_item(doc_id,
                                                                                                          doc_id)
            assert read_doc["id"] == doc_id

            db.client_connection = old_client_connection
            await db.delete_container(entities['coll'])

    async def test_trigger_crud_async(self):

        # create collection
        collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
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
                assert trigger[property] == trigger_definition[property]
            else:
                assert trigger['body'] == 'function() {var x = 10;}'

        # read triggers after creation
        triggers = [trigger async for trigger in collection.scripts.list_triggers()]
        assert len(triggers) == before_create_triggers_count + 1
        # query triggers
        triggers = [trigger async for trigger in collection.scripts.query_triggers(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': trigger_definition['id']}
            ]
        )]
        assert triggers is not None

        # replace trigger
        change_trigger = trigger.copy()
        trigger['body'] = 'function() {var x = 20;}'
        replaced_trigger = await collection.scripts.replace_trigger(change_trigger['id'], trigger)
        for property in trigger_definition:
            if property != "serverScript":
                assert replaced_trigger[property] == trigger[property]
            else:
                assert replaced_trigger['body'] == 'function() {var x = 20;}'

        # read trigger
        trigger = await collection.scripts.get_trigger(replaced_trigger['id'])
        assert replaced_trigger['id'] == trigger['id']
        # delete trigger
        await collection.scripts.delete_trigger(replaced_trigger['id'])
        # read triggers after deletion
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     collection.scripts.delete_trigger,
                                                     replaced_trigger['id'])

    async def test_udf_crud_async(self):

        # create collection
        collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
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
            assert udf[property] == udf_definition[property]

        # read udfs after creation
        udfs = [udf async for udf in collection.scripts.list_user_defined_functions()]
        assert len(udfs) == before_create_udfs_count + 1
        # query udfs
        results = [udf async for udf in collection.scripts.query_user_defined_functions(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': udf_definition['id']}
            ]
        )]
        assert results is not None
        # replace udf
        udf['body'] = 'function() {var x = 20;}'
        replaced_udf = await collection.scripts.replace_user_defined_function(udf=udf['id'], body=udf)
        for property in udf_definition:
            assert replaced_udf[property] == udf[property]
        # read udf
        udf = await collection.scripts.get_user_defined_function(replaced_udf['id'])
        assert replaced_udf['body'] == udf['body']
        # delete udf
        await collection.scripts.delete_user_defined_function(replaced_udf['id'])
        # read udfs after deletion
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     collection.scripts.get_user_defined_function,
                                                     replaced_udf['id'])

    async def test_sproc_crud_async(self):

        # create collection
        collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
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
                assert sproc[property] == sproc_definition[property]
            else:
                assert sproc['body'] == 'function() {var x = 10;}'

        # read sprocs after creation
        sprocs = [sproc async for sproc in collection.scripts.list_stored_procedures()]
        assert len(sprocs) == before_create_sprocs_count + 1
        # query sprocs
        sprocs = [sproc async for sproc in collection.scripts.query_stored_procedures(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': sproc_definition['id']}
            ]
        )]
        assert sprocs is not None
        # replace sproc
        change_sproc = sproc.copy()
        sproc['body'] = 'function() {var x = 20;}'
        replaced_sproc = await collection.scripts.replace_stored_procedure(sproc=change_sproc['id'], body=sproc)
        for property in sproc_definition:
            if property != 'serverScript':
                assert replaced_sproc[property] == sproc[property]
            else:
                assert replaced_sproc['body'] == "function() {var x = 20;}"
        # read sproc
        sproc = await collection.scripts.get_stored_procedure(replaced_sproc['id'])
        assert replaced_sproc['id'] == sproc['id']
        # delete sproc
        await collection.scripts.delete_stored_procedure(replaced_sproc['id'])
        # read sprocs after deletion
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     collection.scripts.get_stored_procedure,
                                                     replaced_sproc['id'])

    async def test_script_logging_execute_stored_procedure_async(self):

        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

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

        assert result == 'Success!'
        assert HttpHeaders.ScriptLogResults not in created_collection.scripts.client_connection.last_response_headers

        result = await created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            enable_script_logging=True,
            partition_key=1
        )

        assert result == 'Success!'
        assert urllib.quote('The value of x is 1.') == created_collection.scripts.client_connection. \
            last_response_headers.get(HttpHeaders.ScriptLogResults)

        result = await created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            enable_script_logging=False,
            partition_key=1
        )

        assert result == 'Success!'
        assert HttpHeaders.ScriptLogResults not in created_collection.scripts.client_connection.last_response_headers

    async def test_collection_indexing_policy_async(self):

        # create database
        db = self.database_for_test
        # create collection
        collection = db.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        collection_properties = await collection.read()
        assert collection_properties['indexingPolicy']['indexingMode'] == documents.IndexingMode.Consistent

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
        assert 1 == len(collection_with_indexing_policy_properties['indexingPolicy']['includedPaths'])
        assert 2 == len(collection_with_indexing_policy_properties['indexingPolicy']['excludedPaths'])

        await db.delete_container(collection_with_indexing_policy.id)

    async def test_create_default_indexing_policy_async(self):

        # create database
        db = self.database_for_test

        # no indexing policy specified
        collection = db.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        collection_properties = await collection.read()
        await self._check_default_indexing_policy_paths(collection_properties['indexingPolicy'])

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

    async def test_create_indexing_policy_with_composite_and_spatial_indexes_async(self):

        # create database
        db = self.database_for_test

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

        # TODO: Check on why custom logger was previously used here
        # custom_logger = logging.getLogger("CustomLogger")
        created_container = await db.create_container(
            id='composite_index_spatial_index' + str(uuid.uuid4()),
            indexing_policy=indexing_policy,
            partition_key=PartitionKey(path='/id', kind='Hash'),
            headers={"Foo": "bar"},
            user_agent="blah",
            user_agent_overwrite=True,
            logging_enable=True,
        )
        # TODO: check on why custom logger was used for container read.
        created_properties = await created_container.read()
        read_indexing_policy = created_properties['indexingPolicy']

        if 'localhost' in self.host or '127.0.0.1' in self.host:  # TODO: Differing result between live and emulator
            assert indexing_policy['spatialIndexes'] == read_indexing_policy['spatialIndexes']
        else:
            # All types are returned for spatial Indexes
            assert indexing_policy['spatialIndexes'] == read_indexing_policy['spatialIndexes']

        assert indexing_policy['compositeIndexes'] == read_indexing_policy['compositeIndexes']

        await db.delete_container(created_container.id)

    async def _check_default_indexing_policy_paths(self, indexing_policy):
        def __get_first(array):
            if array:
                return array[0]
            else:
                return None

        # '/_etag' is present in excluded paths by default
        assert 1 == len(indexing_policy['excludedPaths'])
        # included paths should be 1: '/'.
        assert 1 == len(indexing_policy['includedPaths'])

        root_included_path = __get_first([included_path for included_path in indexing_policy['includedPaths']
                                          if included_path['path'] == '/*'])
        assert root_included_path.get('indexes') is None

    async def test_client_request_timeout_async(self):
        # Test is flaky on Emulator
        if not ('localhost' in self.host or '127.0.0.1' in self.host):
            connection_policy = documents.ConnectionPolicy()
            # making timeout 0 ms to make sure it will throw
            connection_policy.RequestTimeout = 0.000000000001

            # client does a getDatabaseAccount on initialization, which will not time out because
            # there is a forced timeout for those calls
            async with CosmosClient(self.host, self.masterKey, connection_policy=connection_policy) as client:
                with self.assertRaises(Exception):
                    databaseForTest = client.get_database_client(self.configs.TEST_DATABASE_ID)
                    container = databaseForTest.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)
                    item = {'id': str(uuid.uuid4()), 'name': 'sample'}
                    await container.create_item(body=item)
                    await container.read_item(item=item['id'], partition_key=item['id'])
                    print('Async initialization')

    async def test_client_request_timeout_when_connection_retry_configuration_specified_async(self):
        connection_policy = documents.ConnectionPolicy()
        # making timeout 0 ms to make sure it will throw
        connection_policy.RequestTimeout = 0.000000000001
        async with CosmosClient(TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.host,
                                TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.masterKey,
                                connection_policy=connection_policy,
                                retry_total=3, retry_connect=3, retry_read=3, retry_backoff_max=0.3,
                                retry_on_status_codes=[500, 502, 504]) as client:
            with self.assertRaises(AzureError):
                databaseForTest = client.get_database_client(self.configs.TEST_DATABASE_ID)
                container = databaseForTest.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)
                item = {'id': str(uuid.uuid4()), 'name': 'sample'}
                await container.create_item(body=item)
                await container.read_item(item=item['id'], partition_key=item['id'])
                print('Async Initialization')

    async def test_query_iterable_functionality_async(self):

        collection = await self.database_for_test.create_container("query-iterable-container-async",
                                                                   PartitionKey(path="/pk"))
        doc1 = await collection.upsert_item(body={'id': 'doc1', 'prop1': 'value1'})
        self.assertDictEqual(doc1, {})
        doc1 = await collection.upsert_item(body={'id': 'doc1', 'prop1': 'value1'}, no_response=True)
        self.assertDictEqual(doc1, {})
        doc1 = await collection.upsert_item(body={'id': 'doc1', 'prop1': 'value1'}, no_response=False)
        assert doc1 is not None
        doc2 = await collection.upsert_item(body={'id': 'doc2', 'prop1': 'value2'}, no_response=False)
        doc3 = await collection.upsert_item(body={'id': 'doc3', 'prop1': 'value3'}, no_response=False)
        resources = {
            'coll': collection,
            'doc1': doc1,
            'doc2': doc2,
            'doc3': doc3
        }
        # Validate QueryIterable by converting it to a list.
        results = resources['coll'].read_all_items(max_item_count=2)
        docs = [doc async for doc in results]
        assert 3 == len(docs)
        assert resources['doc1']['id'] == docs[0]['id']
        assert resources['doc2']['id'] == docs[1]['id']
        assert resources['doc3']['id'] == docs[2]['id']

        # Validate QueryIterable iterator with 'for'.
        results = resources['coll'].read_all_items(max_item_count=2)
        counter = 0
        # test QueryIterable with 'for'.
        async for doc in results:
            counter += 1
            if counter == 1:
                assert resources['doc1']['id'] == doc['id']
            elif counter == 2:
                assert resources['doc2']['id'] == doc['id']
            elif counter == 3:
                assert resources['doc3']['id'] == doc['id']
        assert counter == 3

        # Get query results page by page.
        results = resources['coll'].read_all_items(max_item_count=2)

        page_iter = results.by_page()
        first_block = [page async for page in await page_iter.__anext__()]
        assert 2 == len(first_block)
        assert resources['doc1']['id'] == first_block[0]['id']
        assert resources['doc2']['id'] == first_block[1]['id']
        assert 1 == len([page async for page in await page_iter.__anext__()])
        with self.assertRaises(StopAsyncIteration):
            await page_iter.__anext__()

        await self.database_for_test.delete_container(collection.id)

    async def test_trigger_functionality_async(self):

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

        async def __create_triggers(collection, triggers):
            """Creates triggers.

            :Parameters:
                - `client`: cosmos_client_connection.CosmosClientConnection
                - `collection`: dict

            """
            for trigger_i in triggers:
                trigger = await collection.scripts.create_trigger(body=trigger_i)
                for property in trigger_i:
                    assert trigger[property] == trigger_i[property]

        # create database
        db = self.database_for_test
        # create collections
        collection1 = await db.create_container(id='test_trigger_functionality 1 ' + str(uuid.uuid4()),
                                                partition_key=PartitionKey(path='/key', kind='Hash'))
        collection2 = await db.create_container(id='test_trigger_functionality 2 ' + str(uuid.uuid4()),
                                                partition_key=PartitionKey(path='/key', kind='Hash'))
        collection3 = await db.create_container(id='test_trigger_functionality 3 ' + str(uuid.uuid4()),
                                                partition_key=PartitionKey(path='/key', kind='Hash'))
        # create triggers
        await __create_triggers(collection1, triggers_in_collection1)
        await __create_triggers(collection2, triggers_in_collection2)
        await __create_triggers(collection3, triggers_in_collection3)
        # create document
        triggers_1 = [trigger async for trigger in collection1.scripts.list_triggers()]
        assert len(triggers_1) == 3
        document_1_1 = await collection1.create_item(
            body={'id': 'doc1',
                  'key': 'value'},
            pre_trigger_include='t1',
            no_response=False
        )
        assert document_1_1['id'] == 'DOC1t1'

        document_1_2 = await collection1.create_item(
            body={'id': 'testing post trigger', 'key': 'value'},
            pre_trigger_include='t1',
            post_trigger_include='response1',
            no_response=False
        )
        assert document_1_2['id'] == 'TESTING POST TRIGGERt1'

        document_1_3 = await collection1.create_item(
            body={'id': 'responseheaders', 'key': 'value'},
            pre_trigger_include='t1',
            no_response=False
        )
        assert document_1_3['id'] == "RESPONSEHEADERSt1"

        triggers_2 = [trigger async for trigger in collection2.scripts.list_triggers()]
        assert len(triggers_2) == 2
        document_2_1 = await collection2.create_item(
            body={'id': 'doc2',
                  'key': 'value2'},
            pre_trigger_include='t2',
            no_response=False
        )
        assert document_2_1['id'] == 'doc2'
        document_2_2 = await collection2.create_item(
            body={'id': 'Doc3',
                  'prop': 'empty',
                  'key': 'value2'},
            pre_trigger_include='t3',
            no_response=False)
        assert document_2_2['id'] == 'doc3t3'

        triggers_3 = [trigger async for trigger in collection3.scripts.list_triggers()]
        assert len(triggers_3) == 1
        with self.assertRaises(Exception):
            await collection3.create_item(
                body={'id': 'Docoptype', 'key': 'value2'},
                post_trigger_include='triggerOpType'
            )

        await db.delete_container(collection1)
        await db.delete_container(collection2)
        await db.delete_container(collection3)

    async def test_stored_procedure_functionality_async(self):

        # create collection
        collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

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
        assert result == 999
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
        assert int(result) == 123456789
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
            parameters={'temp': 'so'},
            partition_key=1
        )
        assert result == 'aso'

    def __validate_offer_response_body(self, offer, expected_coll_link, expected_offer_type):
        # type: (Offer, str, Any) -> None
        assert offer.properties.get('id') is not None
        assert offer.properties.get('_rid') is not None
        assert offer.properties.get('_self') is not None
        assert offer.properties.get('resource') is not None
        assert offer.properties['_self'].find(offer.properties['id']) != -1
        assert expected_coll_link.strip('/') == offer.properties['resource'].strip('/')
        if expected_offer_type:
            assert expected_offer_type == offer.properties.get('offerType')

    async def test_offer_read_and_query_async(self):

        # Create database.
        db = self.database_for_test

        # Create collection.
        collection = db.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # Read the offer.
        expected_offer = await collection.get_throughput()
        collection_properties = await collection.read()
        self.__validate_offer_response_body(expected_offer, collection_properties.get('_self'), None)

    async def test_offer_replace_async(self):

        collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # Read Offer
        expected_offer = await collection.get_throughput()
        collection_properties = await collection.read()
        self.__validate_offer_response_body(expected_offer, collection_properties.get('_self'), None)
        # Replace the offer.
        replaced_offer = await collection.replace_throughput(expected_offer.offer_throughput + 100)
        collection_properties = await collection.read()
        self.__validate_offer_response_body(replaced_offer, collection_properties.get('_self'), None)
        # Check if the replaced offer is what we expect.
        assert expected_offer.properties.get('content').get('offerThroughput') + 100 == replaced_offer.properties.get(
            'content').get('offerThroughput')
        assert expected_offer.offer_throughput + 100 == replaced_offer.offer_throughput

    async def test_database_account_functionality_async(self):

        # Validate database account functionality.
        database_account = await self.client._get_database_account()
        assert database_account.DatabasesLink == '/dbs/'
        assert database_account.MediaLink == '/media/'
        if (HttpHeaders.MaxMediaStorageUsageInMB in
                self.client.client_connection.last_response_headers):
            assert database_account.MaxMediaStorageUsageInMB == self.client.client_connection.last_response_headers[
                HttpHeaders.MaxMediaStorageUsageInMB]
        if (HttpHeaders.CurrentMediaStorageUsageInMB in
                self.client.client_connection.last_response_headers):
            assert database_account.CurrentMediaStorageUsageInMB == self.client.client_connection.last_response_headers[
                HttpHeaders.CurrentMediaStorageUsageInMB]
        assert database_account.ConsistencyPolicy['defaultConsistencyLevel'] is not None

    async def test_index_progress_headers_async(self):

        created_db = self.database_for_test
        consistent_coll = created_db.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        created_container = created_db.get_container_client(container=consistent_coll)
        await created_container.read(populate_quota_info=True)
        assert HttpHeaders.LazyIndexingProgress not in created_db.client_connection.last_response_headers
        assert HttpHeaders.IndexTransformationProgress in created_db.client_connection.last_response_headers

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
        assert HttpHeaders.LazyIndexingProgress not in created_db.client_connection.last_response_headers
        assert HttpHeaders.IndexTransformationProgress in created_db.client_connection.last_response_headers

        await created_db.delete_container(none_coll)

    async def test_get_resource_with_dictionary_and_object_async(self):

        created_db = self.database_for_test

        # read database with id
        read_db = self.client.get_database_client(created_db.id)
        assert read_db.id == created_db.id

        # read database with instance
        read_db = self.client.get_database_client(created_db)
        assert read_db.id == created_db.id

        # read database with properties
        read_db = self.client.get_database_client(await created_db.read())
        assert read_db.id == created_db.id

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # read container with id
        read_container = created_db.get_container_client(created_container.id)
        assert read_container.id == created_container.id

        # read container with instance
        read_container = created_db.get_container_client(created_container)
        assert read_container.id == created_container.id

        # read container with properties
        created_properties = await created_container.read()
        read_container = created_db.get_container_client(created_properties)
        assert read_container.id == created_container.id

        created_item = await created_container.create_item({'id': '1' + str(uuid.uuid4()), 'pk': 'pk'}, no_response=False)

        # read item with id
        read_item = await created_container.read_item(item=created_item['id'], partition_key=created_item['pk'])
        assert read_item['id'] == created_item['id']

        # read item with properties
        read_item = await created_container.read_item(item=created_item, partition_key=created_item['pk'])
        assert read_item['id'], created_item['id']

        created_sproc = await created_container.scripts.create_stored_procedure({
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': 'function () { }'
        })

        # read sproc with id
        read_sproc = await created_container.scripts.get_stored_procedure(created_sproc['id'])
        assert read_sproc['id'] == created_sproc['id']

        # read sproc with properties
        read_sproc = await created_container.scripts.get_stored_procedure(created_sproc)
        assert read_sproc['id'] == created_sproc['id']

        created_trigger = await created_container.scripts.create_trigger({
            'id': 'sample trigger' + str(uuid.uuid4()),
            'serverScript': 'function() {var x = 10;}',
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        })

        # read trigger with id
        read_trigger = await created_container.scripts.get_trigger(created_trigger['id'])
        assert read_trigger['id'] == created_trigger['id']

        # read trigger with properties
        read_trigger = await created_container.scripts.get_trigger(created_trigger)
        assert read_trigger['id'] == created_trigger['id']

        created_udf = await created_container.scripts.create_user_defined_function({
            'id': 'sample udf' + str(uuid.uuid4()),
            'body': 'function() {var x = 10;}'
        })

        # read udf with id
        read_udf = await created_container.scripts.get_user_defined_function(created_udf['id'])
        assert created_udf['id'] == read_udf['id']

        # read udf with properties
        read_udf = await created_container.scripts.get_user_defined_function(created_udf)
        assert created_udf['id'] == read_udf['id']

        created_user = await created_db.create_user({
            'id': 'user' + str(uuid.uuid4())})

        # read user with id
        read_user = created_db.get_user_client(created_user.id)
        assert read_user.id == created_user.id

        # read user with instance
        read_user = created_db.get_user_client(created_user)
        assert read_user.id == created_user.id

        # read user with properties
        created_user_properties = await created_user.read()
        read_user = created_db.get_user_client(created_user_properties)
        assert read_user.id == created_user.id

        created_permission = await created_user.create_permission({
            'id': 'all permission' + str(uuid.uuid4()),
            'permissionMode': documents.PermissionMode.All,
            'resource': created_container.container_link,
            'resourcePartitionKey': [1]
        })

        # read permission with id
        read_permission = await created_user.get_permission(created_permission.id)
        assert read_permission.id == created_permission.id

        # read permission with instance
        read_permission = await created_user.get_permission(created_permission)
        assert read_permission.id == created_permission.id

        # read permission with properties
        read_permission = await created_user.get_permission(created_permission.properties)
        assert read_permission.id == created_permission.id


    async def test_delete_all_items_by_partition_key_async(self):
        # enable the test only for the emulator
        if "localhost" not in self.host and "127.0.0.1" not in self.host:
            return
        # create database
        created_db = self.database_for_test

        # create container
        created_collection = await created_db.create_container(
            id='test_delete_all_items_by_partition_key ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/pk', kind='Hash')
        )
        # Create two partition keys
        partition_key1 = "{}-{}".format("Partition Key 1", str(uuid.uuid4()))
        partition_key2 = "{}-{}".format("Partition Key 2", str(uuid.uuid4()))

        # add items for partition key 1
        for i in range(1, 3):
            newDoc = await created_collection.upsert_item(
                dict(id="item{}".format(i), pk=partition_key1)
            )
            self.assertDictEqual(newDoc, {})

        # add items for partition key 2
        pk2_item = await created_collection.upsert_item(dict(id="item{}".format(3), pk=partition_key2), no_response=False)
       
        # delete all items for partition key 1
        await created_collection.delete_all_items_by_partition_key(partition_key1)

        # check that only items from partition key 1 have been deleted
        items = [item async for item in created_collection.read_all_items()]

        # items should only have 1 item, and it should equal pk2_item
        self.assertDictEqual(pk2_item, items[0])

        # attempting to delete a non-existent partition key or passing none should not delete
        # anything and leave things unchanged
        await created_collection.delete_all_items_by_partition_key(None)

        # check that no changes were made by checking if the only item is still there
        items = [item async for item in created_collection.read_all_items()]

        # items should only have 1 item, and it should equal pk2_item
        self.assertDictEqual(pk2_item, items[0])

        await created_db.delete_container(created_collection)

    async def test_patch_operations_async(self):

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # Create item to patch
        item_id = "patch_item_" + str(uuid.uuid4())
        item = {
            "id": item_id,
            "pk": "patch_item_pk",
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        await created_container.create_item(item)
        # Define and run patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]
        patched_item = await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                                          patch_operations=operations)
        # Verify results from patch operations
        self.assertDictEqual(patched_item, {})
        patched_item = await created_container.read_item(item=item_id, partition_key="patch_item_pk")
        assert patched_item is not {}
        assert patched_item.get("color") is None
        assert patched_item.get("prop") is None
        assert patched_item.get("company") == "CosmosDB"
        assert patched_item.get("address").get("new_city") == "Atlanta"
        assert patched_item.get("number") == 10
        assert patched_item.get("favorite_color") == "yellow"

        # Negative test - attempt to replace non-existent field
        operations = [{"op": "replace", "path": "/wrong_field", "value": "wrong_value"}]
        try:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST

        # Negative test - attempt to remove non-existent field
        operations = [{"op": "remove", "path": "/wrong_field"}]
        try:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST

        # Negative test - attempt to increment non-number field
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        try:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST

        # Negative test - attempt to move from non-existent field
        operations = [{"op": "move", "from": "/wrong_field", "path": "/other_field"}]
        try:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST

    async def test_conditional_patching_async(self):

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # Create item to patch
        item_id = "conditional_patch_item_" + str(uuid.uuid4())
        item = {
            "id": item_id,
            "pk": "patch_item_pk",
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        newDoc = await created_container.create_item(item)
        self.assertDictEqual(newDoc,{})

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
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations, filter_predicate=filter_predicate)
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.PRECONDITION_FAILED

        # Run patch operations with correct filter
        filter_predicate = "from root where root.number = " + str(item.get("number"))
        patched_item = await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                                          patch_operations=operations,
                                                          filter_predicate=filter_predicate)
        # Verify results from patch operations
        self.assertDictEqual(patched_item,{})
        patched_item = await created_container.read_item(item=item_id, partition_key="patch_item_pk")
        assert patched_item is not {}
        assert patched_item.get("color") is None
        assert patched_item.get("prop") is None
        assert patched_item.get("company") == "CosmosDB"
        assert patched_item.get("address").get("new_city") == "Atlanta"
        assert patched_item.get("number") == 10
        assert patched_item.get("favorite_color") == "yellow"

    # Temporarily commenting analytical storage tests until emulator support comes.
    #
    # async def test_create_container_with_analytical_store_off(self):
    #     # don't run test, for the time being, if running against the emulator
    #     if 'localhost' in self.host or '127.0.0.1' in self.host:
    #         return

    #     created_db = self.database_for_test
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

    #     created_db = self.database_for_test
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
    #     created_db = self.database_for_test
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

    async def test_priority_level_async(self):
        # These test verify if headers for priority level are sent
        # Feature must be enabled at the account level
        # If feature is not enabled the test will still pass as we just verify the headers were sent

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        item1 = {"id": "item1", "pk": "pk1"}
        item2 = {"id": "item2", "pk": "pk2"}
        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        priority_headers = []

        # mock execute function to check if priority level set in headers

        async def priority_mock_execute_function(function, *args, **kwargs):
            if args:
                priority_headers.append(args[4].headers[HttpHeaders.PriorityLevel]
                                              if HttpHeaders.PriorityLevel in args[4].headers else '')
            return await self.OriginalExecuteFunction(function, *args, **kwargs)

        _retry_utility_async.ExecuteFunctionAsync = priority_mock_execute_function
        # upsert item with high priority
        await created_container.upsert_item(body=item1, priority="High")
        # check if the priority level was passed
        assert priority_headers[-1] == "High"
        # upsert item with low priority
        await created_container.upsert_item(body=item2, priority="Low")
        # check that headers passed low priority
        assert priority_headers[-1] == "Low"
        # Repeat for read operations
        item1_read = await created_container.read_item("item1", "pk1", priority="High")
        assert priority_headers[-1] == "High"
        item2_read = await created_container.read_item("item2", "pk2", priority="Low")
        assert priority_headers[-1] == "Low"
        # repeat for query
        query = [doc async for doc in created_container.query_items("Select * from c",
                                                                    partition_key="pk1", priority="High")]

        assert priority_headers[-1] == "High"

        # Negative Test: Verify that if we send a value other than High or Low that it will not set the header value
        # and result in bad request
        try:
            item2_read = await created_container.read_item("item2", "pk2", priority="Medium")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction

    async def _mock_execute_function(self, function, *args, **kwargs):
        if HttpHeaders.PartitionKey in args[4].headers:
            self.last_headers.append(args[4].headers[HttpHeaders.PartitionKey])
        return await self.OriginalExecuteFunction(function, *args, **kwargs)


if __name__ == '__main__':
    unittest.main()
