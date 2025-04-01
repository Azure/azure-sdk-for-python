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
class TestCRUDContainerOperationsAsync(unittest.IsolatedAsyncioTestCase):
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
        self.client = CosmosClient(self.host, self.masterKey)
        self.database_for_test = self.client.get_database_client(self.configs.TEST_DATABASE_ID)

    async def asyncTearDown(self):
        await self.client.close()

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

        document_definition = {'id': 'document1',
                               'address': {'street': '1 Microsoft Way',
                                           'city': 'Redmond',
                                           'state': 'WA',
                                           'zip code': 98052
                                           }
                               }

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._mock_execute_function
        # create document without partition key being specified
        created_document = await created_collection.create_item(body=document_definition)
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

        assert replaced_document.get('key') == document_definition.get('key')

        # upsert document(create scenario)
        document_definition['id'] = 'document2'
        document_definition['key'] = 'value2'

        upserted_document = await created_collection.upsert_item(body=document_definition)

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

        async with CosmosClient(TestCRUDContainerOperationsAsync.host, resource_tokens) as restricted_client:
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
        # TODO: Check why custom logger was previously used
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
        # TODO: Check why custom logger was previously used for container read
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
            pre_trigger_include='t1'
        )
        assert document_1_1['id'] == 'DOC1t1'

        document_1_2 = await collection1.create_item(
            body={'id': 'testing post trigger', 'key': 'value'},
            pre_trigger_include='t1',
            post_trigger_include='response1',
        )
        assert document_1_2['id'] == 'TESTING POST TRIGGERt1'

        document_1_3 = await collection1.create_item(
            body={'id': 'responseheaders', 'key': 'value'},
            pre_trigger_include='t1'
        )
        assert document_1_3['id'] == "RESPONSEHEADERSt1"

        triggers_2 = [trigger async for trigger in collection2.scripts.list_triggers()]
        assert len(triggers_2) == 2
        document_2_1 = await collection2.create_item(
            body={'id': 'doc2',
                  'key': 'value2'},
            pre_trigger_include='t2'
        )
        assert document_2_1['id'] == 'doc2'
        document_2_2 = await collection2.create_item(
            body={'id': 'Doc3',
                  'prop': 'empty',
                  'key': 'value2'},
            pre_trigger_include='t3')
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

    async def _mock_execute_function(self, function, *args, **kwargs):
        if HttpHeaders.PartitionKey in args[4].headers:
            self.last_headers.append(args[4].headers[HttpHeaders.PartitionKey])
        return await self.OriginalExecuteFunction(function, *args, **kwargs)


if __name__ == '__main__':
    unittest.main()
