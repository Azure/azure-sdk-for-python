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


@pytest.mark.cosmosAADLong
@pytest.mark.cosmosLong
class TestCRUDContainerOperationsAsync(unittest.IsolatedAsyncioTestCase):
    """Python CRUD Tests.
    """
    client: CosmosClient = None
    key_client: CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []
    database_for_test: DatabaseProxy = None
    key_databaseForTest: DatabaseProxy = None
    data_databaseForTest: DatabaseProxy = None

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
        # Key/data client migration scaffolding (async parity with `test_crud_container.py`):
        # - `key_client` / `key_databaseForTest` (key-auth) handles control-plane-heavy tests.
        # - `client` / `data_databaseForTest` (AAD-or-key, based on test config) is initialized
        #   for incremental per-test data-plane migration.
        # Current default keeps `database_for_test = key_databaseForTest` for stability.
        self.key_client, self.key_databaseForTest, self.client, self.data_databaseForTest = (
            test_config.TestConfig.create_test_clients_async(self.configs.TEST_DATABASE_ID))
        await self.key_client.__aenter__()
        await self.client.__aenter__()
        self.database_for_test = self.key_databaseForTest

    async def _create_container_for_test(self, *args, **kwargs):
        # Container create routes through key-auth key_databaseForTest.
        container_ref = await self.key_databaseForTest.create_container(*args, **kwargs)
        return self.database_for_test.get_container_client(container_ref.id)

    async def _delete_container_for_test(self, *args, **kwargs):
        # Container delete routes through key-auth key_databaseForTest.
        return await self.key_databaseForTest.delete_container(*args, **kwargs)

    async def asyncTearDown(self):
        await self.client.close()
        await self.key_client.close()

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
        created_db = self.key_databaseForTest
        data_db = self.data_databaseForTest

        collection_id = 'test_partitioned_collection_partition_key_extraction ' + str(uuid.uuid4())
        created_collection_ref = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/address/state', kind=documents.PartitionKind.Hash)
        )
        created_collection = data_db.get_container_client(created_collection_ref.id)

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
        created_collection1_ref = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/address', kind=documents.PartitionKind.Hash)
        )
        created_collection1 = data_db.get_container_client(created_collection1_ref.id)

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._mock_execute_function
        # Create document with partitionkey not present as a leaf level property but a dict
        await created_collection1.create_item(document_definition)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        assert self.last_headers[0] == [{}]
        del self.last_headers[:]

        collection_id = 'test_partitioned_collection_partition_key_extraction2 ' + str(uuid.uuid4())
        created_collection2_ref = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/address/state/city', kind=documents.PartitionKind.Hash)
        )
        created_collection2 = data_db.get_container_client(created_collection2_ref.id)

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
        created_db = self.key_databaseForTest
        data_db = self.data_databaseForTest

        collection_id = 'test_partitioned_collection_partition_key_extraction_special_chars1 ' + str(uuid.uuid4())

        created_collection1_ref = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/\"level\' 1*()\"/\"le/vel2\"', kind=documents.PartitionKind.Hash)
        )
        created_collection1 = data_db.get_container_client(created_collection1_ref.id)
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

        created_collection2_ref = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/\'level\" 1*()\'/\'le/vel2\'', kind=documents.PartitionKind.Hash)
        )
        created_collection2 = data_db.get_container_client(created_collection2_ref.id)

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
        created_collection_ref = await self.key_databaseForTest.create_container(
            str(uuid.uuid4()), PartitionKey(path="/id")
        )
        created_collection = self.data_databaseForTest.get_container_client(created_collection_ref.id)

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
        await self.key_databaseForTest.delete_container(created_collection.id)

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

