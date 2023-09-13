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

"""End-to-end test.
"""

import unittest
import time
from typing import Mapping
import test_config
import uuid
import pytest
from azure.core.pipeline.transport import RequestsTransport, RequestsTransportResponse
import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.aio import CosmosClient, _retry_utility_async
from azure.cosmos.diagnostics import RecordDiagnostics
from azure.cosmos.partition_key import PartitionKey
import requests
import azure.cosmos.aio._cosmos_client as cosmos_client

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

    configs = test_config._test_config
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []
    client = None

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
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, consistency_level="Session"
                                                , connection_policy=cls.connectionPolicy)
        cls.databaseForTest = await cls.client.create_database_if_not_exists(test_config._test_config.TEST_DATABASE_ID)

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
                                                               partition_key=PartitionKey(path=["/pk1", "/pk2"],
                                                                                          kind="MultiHash"),
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
                                                                          partition_key=PartitionKey(path=['/id',
                                                                                                           '/id2',
                                                                                                           '/id3'],
                                                                                                     kind='MultiHash'))
        self.assertEqual(created_collection.id, container_proxy.id)
        self.assertDictEqual(PartitionKey(path=["/id1", "/id2", "/id3"], kind='MultiHash'),
                             container_proxy._properties['partitionKey'])

        container_proxy = await created_db.create_container_if_not_exists(id=created_collection.id,
                                                                          partition_key=created_properties[
                                                                              'partitionKey'])
        self.assertEqual(created_container.id, container_proxy.id)
        self.assertDictEqual(PartitionKey(path=["/id1", "/id2", "/id3"], kind='MultiHash'),
                             container_proxy._properties['partitionKey'])

        await created_db.delete_container(created_collection.id)

    async def test_partitioned_collection(self):
        created_db = self.databaseForTest

        collection_definition = {'id': 'test_partitioned_collection ' + str(uuid.uuid4()),
                                 'partitionKey':
                                     {
                                         'paths': ['/id', '/pk'],
                                         'kind': documents.PartitionKind.MultiHash,
                                         'version': 2
                                     }
                                 }

        offer_throughput = 10100
        created_collection = await created_db.create_container(id=collection_definition['id'],
                                                               partition_key=collection_definition['partitionKey'],
                                                               offer_throughput=offer_throughput)

        self.assertEqual(collection_definition.get('id'), created_collection.id)

        created_collection_properties = await created_collection.read()
        self.assertEqual(collection_definition.get('partitionKey').get('paths'),
                         created_collection_properties['partitionKey']['paths'])
        self.assertEqual(collection_definition.get('partitionKey').get('kind'),
                         created_collection_properties['partitionKey']['kind'])

        expected_offer = await created_collection.get_throughput()

        self.assertIsNotNone(expected_offer)

        self.assertEqual(expected_offer.offer_throughput, offer_throughput)

        await created_db.delete_container(created_collection.id)

    async def test_partitioned_collection_partition_key_extraction(self):
        created_db = self.databaseForTest

        collection_id = 'test_partitioned_collection_partition_key_extraction ' + str(uuid.uuid4())
        created_collection = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path=['/address/state', '/address/city'], kind=documents.PartitionKind.MultiHash)
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
        self.assertEqual(self.last_headers[1], '["WA", "Redmond"]')
        del self.last_headers[:]

        self.assertEqual(created_document.get('id'), document_definition.get('id'))
        self.assertEqual(created_document.get('address').get('state'), document_definition.get('address').get('state'))

        collection_id = 'test_partitioned_collection_partition_key_extraction1 ' + str(uuid.uuid4())
        created_collection1 = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path=['/address/state/city', '/address/city/state'],
                                       kind=documents.PartitionKind.MultiHash)
        )

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._MockExecuteFunction
        # Create document with partitionkey not present in the document
        try:
            created_document = await created_collection1.create_item(document_definition)
            _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
            self.assertFalse(True, 'Operation Should Fail.')
        except ValueError as error:
            self.assertEqual(str(error), "Undefined Value in MultiHash PartitionKey.")

        await created_db.delete_container(created_collection.id)
        await created_db.delete_container(created_collection1.id)

    async def test_partitioned_collection_partition_key_extraction_special_chars(self):
        created_db = self.databaseForTest

        collection_id = 'test_partitioned_collection_partition_key_extraction_special_chars1 ' + str(uuid.uuid4())

        created_collection1 = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path=['/\"first level\' 1*()\"/\"le/vel2\"',
                                             '/\"second level\' 1*()\"/\"le/vel2\"'],
                                       kind=documents.PartitionKind.MultiHash)
        )
        document_definition = {'id': 'document1',
                               "first level' 1*()": {"le/vel2": 'val1'},
                               "second level' 1*()": {"le/vel2": 'val2'}
                               }

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._MockExecuteFunction
        created_document = await created_collection1.create_item(body=document_definition)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        self.assertEqual(self.last_headers[1], '["val1", "val2"]')
        del self.last_headers[:]

        collection_definition2 = {
            'id': 'test_partitioned_collection_partition_key_extraction_special_chars2 ' + str(uuid.uuid4()),
            'partitionKey':
                {
                    'paths': ['/\'first level\" 1*()\'/\'first le/vel2\'',
                              '/\'second level\" 1*()\'/\'second le/vel2\''],
                    'kind': documents.PartitionKind.MultiHash
                }
        }

        collection_id = 'test_partitioned_collection_partition_key_extraction_special_chars2 ' + str(uuid.uuid4())

        created_collection2 = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path=collection_definition2["partitionKey"]["paths"],
                                       kind=collection_definition2["partitionKey"]["kind"])
        )

        document_definition = {'id': 'document2',
                               'first level\" 1*()': {'first le/vel2': 'val3'},
                               'second level\" 1*()': {'second le/vel2': 'val4'}
                               }

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._MockExecuteFunction
        # create document without partition key being specified
        created_document = await created_collection2.create_item(body=document_definition)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
        self.assertEqual(self.last_headers[1], '["val3", "val4"]')
        del self.last_headers[:]

        await created_db.delete_container(created_collection1.id)
        await created_db.delete_container(created_collection2.id)

    async def test_partitioned_collection_document_crud_and_query(self):
        created_db = self.databaseForTest
        created_collection = await created_db.create_container(
            test_config._test_config.TEST_COLLECTION_MULTI_HASH_MULTI_PARTITION,
            PartitionKey(path=["/city", "/zipcode"], kind="MultiHash"))

        document_definition = {'id': 'document',
                               'key': 'value',
                               'city': 'Redmond',
                               'zipcode': '98052'}

        created_document = await created_collection.create_item(body=document_definition)

        self.assertEqual(created_document.get('id'), document_definition.get('id'))
        self.assertEqual(created_document.get('key'), document_definition.get('key'))
        self.assertEqual(created_document.get('city'), document_definition.get('city'))
        self.assertEqual(created_document.get('zipcode'), document_definition.get('zipcode'))

        # read document
        read_document = await created_collection.read_item(
            item=created_document.get('id'),
            partition_key=[created_document.get('city'), created_document.get('zipcode')]
        )

        self.assertEqual(read_document.get('id'), created_document.get('id'))
        self.assertEqual(read_document.get('key'), created_document.get('key'))
        self.assertEqual(read_document.get('city'), created_document.get('city'))
        self.assertEqual(read_document.get('zipcode'), created_document.get('zipcode'))

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
        document_definition['city'] = 'Atlanta'
        document_definition['zipcode'] = '30363'

        upserted_document = await created_collection.upsert_item(body=document_definition)

        self.assertEqual(upserted_document.get('id'), document_definition.get('id'))
        self.assertEqual(upserted_document.get('key'), document_definition.get('key'))
        self.assertEqual(upserted_document.get('city'), document_definition.get('city'))
        self.assertEqual(upserted_document.get('zipcode'), document_definition.get('zipcode'))

        documentlist = [document async for document in created_collection.read_all_items()]
        self.assertEqual(2, len(documentlist))

        # delete document
        await created_collection.delete_item(item=upserted_document, partition_key=[upserted_document.get('city'),
                                                                                    upserted_document.get('zipcode')])

        # query document on the partition key specified in the predicate will pass even without setting
        # enableCrossPartitionQuery or passing in the partitionKey value
        documentlist = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.city=\'' + replaced_document.get('city') + '\' and r.zipcode=\'' + replaced_document.get('zipcode') + '\''  # pylint: disable=line-too-long
        )]
        self.assertEqual(1, len(documentlist))

        # query document on any property other than partitionKey will fail without setting enableCrossPartitionQuery
        # or passing in the partitionKey value
        try:
            [document async for document in created_collection.query_items(
                query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\''  # nosec
            )]
        except Exception:
            pass

        # cross partition query
        documentlist = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
        )]

        self.assertEqual(1, len(documentlist))

        # query document by providing the partitionKey value
        documentlist = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            partition_key=[replaced_document.get('city'), replaced_document.get('zipcode')]
        )]

        self.assertEqual(1, len(documentlist))

        # Using incomplete extracted partition key in item body
        incomplete_document = {'id': 'document3',
                               'key': 'value3',
                               'city': 'Vancouver'}

        try:
            await created_collection.create_item(body=incomplete_document)
            self.fail("Test did not fail as expected")
        except exceptions.CosmosHttpResponseError as error:
            self.assertEqual(error.status_code, StatusCodes.BAD_REQUEST)
            self.assertTrue("Partition key provided either doesn't correspond to definition in the collection"
                            in error.message)

        # using incomplete partition key in read item
        try:
            await created_collection.read_item(created_document, partition_key=["Redmond"])
            self.fail("Test did not fail as expected")
        except exceptions.CosmosHttpResponseError as error:
            self.assertEqual(error.status_code, StatusCodes.BAD_REQUEST)
            self.assertTrue("Partition key provided either doesn't correspond to definition in the collection"
                            in error.message)

        # using mix value types for partition key
        doc_mixed_types = {'id': "doc4",
                           'key': 'value4',
                           'city': None,
                           'zipcode': 1000}
        created_mixed_type_doc = await created_collection.create_item(body=doc_mixed_types)
        self.assertEqual(doc_mixed_types.get('city'), created_mixed_type_doc.get('city'))
        self.assertEqual(doc_mixed_types.get('zipcode'), created_mixed_type_doc.get('zipcode'))
        await created_db.delete_container(created_collection.id)

    async def test_partitioned_collection_prefix_partition_query(self):
        created_db = self.databaseForTest
        collection_id = 'test_partitioned_collection_partition_key_prefix_query_async ' + str(uuid.uuid4())
        created_collection = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path=['/state', '/city', '/zipcode'], kind=documents.PartitionKind.MultiHash)
        )
        item_values = [
            ["CA", "Newbury Park", "91319"],
            ["CA", "Oxnard", "93033"],
            ["CA", "Oxnard", "93030"],
            ["CA", "Oxnard", "93036"],
            ["CA", "Thousand Oaks", "91358"],
            ["CA", "Ventura", "93002"],
            ["CA", "Ojai", "93023"],  # cspell:disable-line
            ["CA", "Port Hueneme", "93041"],  # cspell:disable-line
            ["WA", "Seattle", "98101"],
            ["WA", "Bellevue", "98004"]
        ]

        document_definitions = [{'id': 'document1',
                                 'state': item_values[0][0],
                                 'city': item_values[0][1],
                                 'zipcode': item_values[0][2]
                                 },
                                {'id': 'document2',
                                 'state': item_values[1][0],
                                 'city': item_values[1][1],
                                 'zipcode': item_values[1][2]
                                 },
                                {'id': 'document3',
                                 'state': item_values[2][0],
                                 'city': item_values[2][1],
                                 'zipcode': item_values[2][2]
                                 },
                                {'id': 'document4',
                                 'state': item_values[3][0],
                                 'city': item_values[3][1],
                                 'zipcode': item_values[3][2]
                                 },
                                {'id': 'document5',
                                 'state': item_values[4][0],
                                 'city': item_values[4][1],
                                 'zipcode': item_values[4][2]
                                 },
                                {'id': 'document6',
                                 'state': item_values[5][0],
                                 'city': item_values[5][1],
                                 'zipcode': item_values[5][2]
                                 },
                                {'id': 'document7',
                                 'state': item_values[6][0],
                                 'city': item_values[6][1],
                                 'zipcode': item_values[6][2]
                                 },
                                {'id': 'document8',
                                 'state': item_values[7][0],
                                 'city': item_values[7][1],
                                 'zipcode': item_values[7][2]
                                 },
                                {'id': 'document9',
                                 'state': item_values[8][0],
                                 'city': item_values[8][1],
                                 'zipcode': item_values[8][2]
                                 },
                                {'id': 'document10',
                                 'state': item_values[9][0],
                                 'city': item_values[9][1],
                                 'zipcode': item_values[9][2]
                                 }
                                ]
        created_documents = []
        for document_definition in document_definitions:
            created_documents.append(await created_collection.create_item(
                body=document_definition))
        self.assertEqual(len(created_documents), len(document_definitions))

        # Query all documents should return all items
        document_list = [document async for document in created_collection.query_items(query='Select * from c'
                                                                                       , enable_cross_partition_query=True)]  # pylint: disable=line-too-long
        self.assertEqual(len(document_list), len(document_definitions))

        # Query all items with only CA for 1st level. Should return only 8 items instead of 10
        document_list = [document async for document in created_collection.query_items(query='Select * from c'
                                                                                       , partition_key=['CA'])]
        self.assertEqual(8, len(document_list))

        # Query all items with CA for 1st level and Oxnard for second level. Should only return 3 items
        document_list = [document async for document in created_collection.query_items(query='Select * from c'
                                                                                       , partition_key=['CA', 'Oxnard'])]  # pylint: disable=line-too-long
        self.assertEqual(3, len(document_list))

        # Query for specific zipcode using 1st level of partition key value only:
        document_list = [document async for document in created_collection.query_items(query='Select * from c where c.zipcode = "93033"'  # pylint: disable=line-too-long
                                                                                       , partition_key=['CA'])]
        self.assertEqual(1, len(document_list))

        # Query Should work with None values:
        document_list = [document async for document in created_collection.query_items(query='Select * from c'
                                                                                       , partition_key=[None, '93033'])]
        self.assertEqual(0, len(document_list))

        # Query Should Work with non string values
        document_list = [document async for document in created_collection.query_items(query='Select * from c'
                                                                                       , partition_key=[0xFF, 0xFF])]
        self.assertEqual(0, len(document_list))

        # Negative Test, prefix query should not work if no partition is given (empty list is given)
        try:
            document_list = [document async for document in created_collection.query_items(query='Select * from c'
                                                                                           , partition_key=[])]
            self.fail("Test did not fail as expected")
        except exceptions.CosmosHttpResponseError as error:
            self.assertEqual(error.status_code, StatusCodes.BAD_REQUEST)
            self.assertTrue("Cross partition query is required but disabled"
                            in error.message)

        await created_db.delete_container(created_collection.id)

    async def _MockExecuteFunction(self, function, *args, **kwargs):
        self.last_headers.append(args[4].headers[HttpHeaders.PartitionKey]
                                 if HttpHeaders.PartitionKey in args[4].headers else '')
        return await self.OriginalExecuteFunction(function, *args, **kwargs)
