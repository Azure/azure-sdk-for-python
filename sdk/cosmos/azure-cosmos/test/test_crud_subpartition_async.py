# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test.
"""

import time
import unittest
import uuid
from typing import Mapping

import pytest
import requests
from azure.core.pipeline.transport import RequestsTransport, RequestsTransportResponse

import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos._routing import routing_range
from azure.cosmos._routing.collection_routing_map import CollectionRoutingMap
from azure.cosmos.aio import CosmosClient, _retry_utility_async
from azure.cosmos.diagnostics import RecordDiagnostics
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.partition_key import PartitionKey


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


@pytest.mark.cosmosEmulator
class TestSubpartitionCrudAsync(unittest.IsolatedAsyncioTestCase):
    """Python CRUD Tests.
    """

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []
    client: CosmosClient = None

    async def __assert_http_failure_with_status(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            await func(*args, **kwargs)
            self.fail("function should fail")
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

    async def test_collection_crud_subpartition_async(self):
        created_db = self.database_for_test
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
        assert collection_id == created_collection.id
        assert isinstance(created_recorder.headers, Mapping)
        assert 'Content-Type' in created_recorder.headers
        assert isinstance(created_recorder.body, Mapping)
        assert 'id' in created_recorder.body

        created_properties = await created_collection.read()
        assert 'consistent' == created_properties['indexingPolicy']['indexingMode']

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

        assert collections is not None
        # delete collection
        await created_db.delete_container(created_collection.id)
        # read collection after deletion
        created_container = created_db.get_container_client(created_collection.id)
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     created_container.read)

        container_proxy = await created_db.create_container(id=created_collection.id,
                                                            partition_key=PartitionKey(path=['/id1',
                                                                                             '/id2',
                                                                                             '/id3'],
                                                                                       kind='MultiHash'))
        assert created_collection.id == container_proxy.id
        container_proxy_properties = await container_proxy._get_properties()
        assert PartitionKey(path=["/id1", "/id2", "/id3"], kind='MultiHash') == container_proxy_properties[
            'partitionKey']

        await created_db.delete_container(created_collection.id)

    async def test_partitioned_collection_subpartition_async(self):
        created_db = self.database_for_test

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

        assert collection_definition.get('id') == created_collection.id

        created_collection_properties = await created_collection.read()
        assert collection_definition.get('partitionKey').get('paths') == created_collection_properties['partitionKey'][
            'paths']
        assert collection_definition.get('partitionKey').get('kind') == created_collection_properties['partitionKey'][
            'kind']

        expected_offer = await created_collection.get_throughput()

        assert expected_offer is not None

        assert expected_offer.offer_throughput == offer_throughput

        # Negative test, check that user can't make a subpartition higher than 3 levels
        collection_definition2 = {'id': 'test_partitioned_collection2_MH ' + str(uuid.uuid4()),
                                  'partitionKey':
                                      {
                                          'paths': ['/id', '/pk', '/id2', "/pk2"],
                                          'kind': documents.PartitionKind.MultiHash,
                                          'version': 2
                                      }
                                  }
        try:
            created_collection = await created_db.create_container(id=collection_definition['id'],
                                                                   partition_key=collection_definition2['partitionKey'],
                                                                   offer_throughput=offer_throughput)
        except exceptions.CosmosHttpResponseError as error:
            assert error.status_code == StatusCodes.BAD_REQUEST
            assert "Too many partition key paths" in error.message

        # Negative Test: Check if user tries to create multihash container while defining single hash
        collection_definition3 = {'id': 'test_partitioned_collection2_MH ' + str(uuid.uuid4()),
                                  'partitionKey':
                                      {
                                          'paths': ['/id', '/pk', '/id2', "/pk2"],
                                          'kind': documents.PartitionKind.Hash,
                                          'version': 2
                                      }
                                  }
        try:
            created_collection = await created_db.create_container(id=collection_definition['id'],
                                                                   partition_key=collection_definition3['partitionKey'],
                                                                   offer_throughput=offer_throughput)
        except exceptions.CosmosHttpResponseError as error:
            assert error.status_code == StatusCodes.BAD_REQUEST
            assert "Too many partition key paths" in error.message

        await created_db.delete_container(created_collection.id)

    async def test_partitioned_collection_partition_key_extraction_subpartition_async(self):
        created_db = self.database_for_test

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
        assert self.last_headers[0] == '["WA","Redmond"]'
        del self.last_headers[:]

        assert created_document.get('id') == document_definition.get('id')
        assert created_document.get('address').get('state') == document_definition.get('address').get('state')

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
            self.fail('Operation Should Fail.')
        except exceptions.CosmosHttpResponseError as error:
            assert error.status_code == StatusCodes.BAD_REQUEST
            assert "Partition key [[]] is invalid" in error.message
            del self.last_headers[:]

        await created_db.delete_container(created_collection.id)
        await created_db.delete_container(created_collection1.id)

    async def test_partitioned_collection_partition_key_extraction_special_chars_subpartition_async(self):
        created_db = self.database_for_test

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
        assert self.last_headers[-1] == '["val1","val2"]'
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
        assert self.last_headers[-1] == '["val3","val4"]'
        del self.last_headers[:]

        await created_db.delete_container(created_collection1.id)
        await created_db.delete_container(created_collection2.id)

    async def test_partitioned_collection_document_crud_and_query_subpartition_async(self):
        created_db = self.database_for_test
        collection_id = 'test_partitioned_collection_partition_document_crud_and_query_MH ' + str(uuid.uuid4())
        created_collection = await created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path=['/city', '/zipcode'], kind=documents.PartitionKind.MultiHash)
        )

        document_definition = {'id': 'document',
                               'key': 'value',
                               'city': 'Redmond',
                               'zipcode': '98052'}

        created_document = await created_collection.create_item(body=document_definition)

        assert created_document.get('id') == document_definition.get('id')
        assert created_document.get('key') == document_definition.get('key')
        assert created_document.get('city') == document_definition.get('city')
        assert created_document.get('zipcode') == document_definition.get('zipcode')

        # read document
        read_document = await created_collection.read_item(
            item=created_document.get('id'),
            partition_key=[created_document.get('city'), created_document.get('zipcode')]
        )

        assert read_document.get('id') == created_document.get('id')
        assert read_document.get('key') == created_document.get('key')
        assert read_document.get('city') == created_document.get('city')
        assert read_document.get('zipcode') == created_document.get('zipcode')

        # Read document feed doesn't require partitionKey as it's always a cross partition query
        documentlist = [document async for document in created_collection.read_all_items()]
        assert 1 == len(documentlist)

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
        document_definition['city'] = 'Atlanta'
        document_definition['zipcode'] = '30363'

        upserted_document = await created_collection.upsert_item(body=document_definition)

        assert upserted_document.get('id') == document_definition.get('id')
        assert upserted_document.get('key') == document_definition.get('key')
        assert upserted_document.get('city') == document_definition.get('city')
        assert upserted_document.get('zipcode') == document_definition.get('zipcode')

        documentlist = [document async for document in created_collection.read_all_items()]
        assert 2 == len(documentlist)

        # delete document
        await created_collection.delete_item(item=upserted_document, partition_key=[upserted_document.get('city'),
                                                                                    upserted_document.get('zipcode')])

        # query document on the partition key specified in the predicate will pass even without setting
        # enableCrossPartitionQuery or passing in the partitionKey value
        documentlist = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.city=\'' + replaced_document.get(
                'city') + '\' and r.zipcode=\'' + replaced_document.get('zipcode') + '\''
            # pylint: disable=line-too-long
        )]
        assert 1 == len(documentlist)

        # cross partition query
        documentlist = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
        )]

        assert 1 == len(documentlist)

        # query document by providing the partitionKey value
        documentlist = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            partition_key=[replaced_document.get('city'), replaced_document.get('zipcode')]
        )]

        assert 1 == len(documentlist)

        # Using incomplete extracted partition key in item body
        incomplete_document = {'id': 'document3',
                               'key': 'value3',
                               'city': 'Vancouver'}

        try:
            await created_collection.create_item(body=incomplete_document)
            self.fail("Test did not fail as expected")
        except exceptions.CosmosHttpResponseError as error:
            assert error.status_code == StatusCodes.BAD_REQUEST
            assert "Partition key provided either doesn't correspond to definition in the collection" in error.message

        # using incomplete partition key in read item
        try:
            await created_collection.read_item(created_document, partition_key=["Redmond"])
            self.fail("Test did not fail as expected")
        except exceptions.CosmosHttpResponseError as error:
            assert error.status_code, StatusCodes.BAD_REQUEST
            assert "Partition key provided either doesn't correspond to definition in the collection" in error.message

        # using mix value types for partition key
        doc_mixed_types = {'id': "doc4",
                           'key': 'value4',
                           'city': None,
                           'zipcode': 1000}
        created_mixed_type_doc = await created_collection.create_item(body=doc_mixed_types)
        assert doc_mixed_types.get('city') == created_mixed_type_doc.get('city')
        assert doc_mixed_types.get('zipcode') == created_mixed_type_doc.get('zipcode')
        await created_db.delete_container(created_collection.id)

    async def test_partitioned_collection_prefix_partition_query_subpartition_async(self):
        created_db = self.database_for_test
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
        assert len(created_documents) == len(document_definitions)

        # Query all documents should return all items
        document_list = [document async for document in created_collection.query_items(query='Select * from c')]
        assert len(document_list) == len(document_definitions)

        # Query all items with only CA for 1st level. Should return only 8 items instead of 10
        document_list = [document async for document in created_collection.query_items(query='Select * from c'
                                                                                       , partition_key=['CA'])]
        assert 8 == len(document_list)

        # Query all items with CA for 1st level and Oxnard for second level. Should only return 3 items
        document_list = [document async for document in created_collection.query_items(query='Select * from c'
                                                                                       , partition_key=['CA',
                                                                                                        'Oxnard'])]  # pylint: disable=line-too-long
        assert 3 == len(document_list)

        # Query for specific zipcode using 1st level of partition key value only:
        document_list = [document async for document in
                         created_collection.query_items(query='Select * from c where c.zipcode = "93033"'
                                                        # pylint: disable=line-too-long
                                                        , partition_key=['CA'])]
        assert 1 == len(document_list)

        # Query Should work with None values:
        document_list = [document async for document in created_collection.query_items(query='Select * from c'
                                                                                       , partition_key=[None, '93033'])]
        assert 0 == len(document_list)

        # Query Should Work with non string values
        document_list = [document async for document in created_collection.query_items(query='Select * from c'
                                                                                       , partition_key=[0xFF, 0xFF])]
        assert 0 == len(document_list)

        # Negative Test, prefix query should not work if no partition is given (empty list is given)
        try:
            document_list = [document async for document in created_collection.query_items(query='Select * from c'
                                                                                           , partition_key=[])]
            self.fail("Test did not fail as expected")
        except exceptions.CosmosHttpResponseError as error:
            assert error.status_code == StatusCodes.BAD_REQUEST
            assert "Cross partition query is required but disabled" in error.message

        await created_db.delete_container(created_collection.id)

    async def test_partition_key_range_subpartition_overlap(self):
        Id = 'id'
        MinInclusive = 'minInclusive'
        MaxExclusive = 'maxExclusive'
        partitionKeyRanges = \
            [
                ({Id: "2",
                  MinInclusive: "0000000050",
                  MaxExclusive: "0000000070"},
                 2),
                ({Id: "0",
                  MinInclusive: "",
                  MaxExclusive: "0000000030"},
                 0),
                ({Id: "1",
                  MinInclusive: "0000000030",
                  MaxExclusive: "0000000050"},
                 1),
                ({Id: "3",
                  MinInclusive: "0000000070",
                  MaxExclusive: "FF"},
                 3)
            ]

        crm = CollectionRoutingMap.CompleteRoutingMap(partitionKeyRanges, "")

        # Case 1: EPK range matches a single entire physical partition
        EPK_range_1 = routing_range.Range(range_min="0000000030", range_max="0000000050",
                                          isMinInclusive=True, isMaxInclusive=False)
        over_lapping_ranges_1 = crm.get_overlapping_ranges([EPK_range_1])
        # Should only have 1 over lapping range
        assert len(over_lapping_ranges_1) == 1
        # EPK range 1 should be overlapping physical partition 1
        assert over_lapping_ranges_1[0][Id] == "1"
        # Partition 1 and EPK range 1 should have same range min and range max
        over_lapping_range_1 = routing_range.Range.PartitionKeyRangeToRange(over_lapping_ranges_1[0])
        assert over_lapping_range_1.min == EPK_range_1.min
        assert over_lapping_range_1.max == EPK_range_1.max

        # Case 2: EPK range is a sub range of a single physical partition

        EPK_range_2 = routing_range.Range(range_min="0000000035", range_max="0000000045",
                                          isMinInclusive=True, isMaxInclusive=False)
        over_lapping_ranges_2 = crm.get_overlapping_ranges([EPK_range_2])
        # Should only have 1 over lapping range
        assert len(over_lapping_ranges_2) == 1
        # EPK range 2 should be overlapping physical partition 1
        assert over_lapping_ranges_2[0][Id] == "1"
        # EPK range 2 min should be higher than over lapping partition and the max should be lower
        over_lapping_range_2 = routing_range.Range.PartitionKeyRangeToRange(over_lapping_ranges_2[0])
        assert over_lapping_range_2.min < EPK_range_2.min
        assert EPK_range_2.max < over_lapping_range_2.max

        # Case 3: EPK range partially spans 2 physical partitions

        EPK_range_3 = routing_range.Range(range_min="0000000035", range_max="0000000055",
                                          isMinInclusive=True, isMaxInclusive=False)
        over_lapping_ranges_3 = crm.get_overlapping_ranges([EPK_range_3])
        # Should overlap exactly two partition ranges
        assert len(over_lapping_ranges_3) == 2
        # EPK range 3 should be over lapping partition 1 and partition 2
        assert over_lapping_ranges_3[0][Id] == "1"
        assert over_lapping_ranges_3[1][Id] == "2"
        # EPK Range 3 range min should be higher than partition 1's min, but lower than partition 2's, vice versa with max
        over_lapping_range_3A = routing_range.Range.PartitionKeyRangeToRange(over_lapping_ranges_3[0])
        over_lapping_range_3B = routing_range.Range.PartitionKeyRangeToRange(over_lapping_ranges_3[1])
        assert over_lapping_range_3A.min < EPK_range_3.min
        assert EPK_range_3.min < over_lapping_range_3B.min
        assert EPK_range_3.max > over_lapping_range_3A.max
        assert over_lapping_range_3B.max > EPK_range_3.max

        # Case 4: EPK range spans multiple physical partitions, including entire physical partitions

        EPK_range_4 = routing_range.Range(range_min="0000000020", range_max="0000000060",
                                          isMinInclusive=True, isMaxInclusive=False)
        over_lapping_ranges_4 = crm.get_overlapping_ranges([EPK_range_4])
        # should overlap 3 partitions
        assert len(over_lapping_ranges_4) == 3
        # EPK range 4 should be over lapping partitions 0, 1, and 2
        assert over_lapping_ranges_4[0][Id] == "0"
        assert over_lapping_ranges_4[1][Id] == "1"
        assert over_lapping_ranges_4[2][Id] == "2"

        # individual ranges for each partition
        olr_4_a = routing_range.Range.PartitionKeyRangeToRange(over_lapping_ranges_4[0])
        olr_4_b = routing_range.Range.PartitionKeyRangeToRange(over_lapping_ranges_4[1])
        olr_4_c = routing_range.Range.PartitionKeyRangeToRange(over_lapping_ranges_4[2])
        # both EPK range 4 min and max should be greater than partitions 0 min and max
        assert EPK_range_4.min > olr_4_a.min
        assert EPK_range_4.max > olr_4_a.max
        # EPK range 4 should contain partition 1's range entirely
        assert EPK_range_4.contains(olr_4_b.min)
        assert EPK_range_4.contains(olr_4_b.max)
        # Both EPK range 4 min and max should be less than partition 2's min and max
        assert EPK_range_4.min < olr_4_c.min
        assert EPK_range_4.max < olr_4_c.max

    # Commenting out delete all items by pk until pipelines support it
    # async def test_delete_all_items_by_partition_key_subpartition_async(self):
    #     # create database
    #     created_db = self.database_for_test
    #
    #     # create container
    #     created_collection = await created_db.create_container(
    #         id='test_delete_all_items_by_partition_key ' + str(uuid.uuid4()),
    #         partition_key=PartitionKey(path=['/pk1','/pk2','/pk3'], kind='MultiHash')
    #     )
    #     # Create two partition keys
    #     partition_key1 = "{}-{}".format("Partition Key 1", str(uuid.uuid4()))
    #     partition_key2 = "{}-{}".format("Partition Key 2", str(uuid.uuid4()))
    #
    #     #Create two partition keys
    #     partition_key1 = ['pkA1 ' + str(uuid.uuid4()), 'pkA2 ' + str(uuid.uuid4()), 'pkA3 ' + str(uuid.uuid4())]
    #     partition_key2 = ['pkB1 ' + str(uuid.uuid4()), 'pkB2 ' + str(uuid.uuid4()), 'pkB3 ' + str(uuid.uuid4())]
    #
    #     # add items for partition key 1
    #     for i in range(1, 3):
    #         created_collection.upsert_item(
    #             dict(id="item{}".format(i), pk1=partition_key1[0], pk2=partition_key1[1], pk3=partition_key1[2])
    #         )
    #
    #     # add items for partition key 2
    #
    #     pk2_item = created_collection.upsert_item(dict(id="item{}".format(3), pk1=partition_key2[0]
    #                                               , pk2=partition_key2[1], pk3=partition_key2[2]))
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

    async def _MockExecuteFunction(self, function, *args, **kwargs):
        try:
            self.last_headers.append(args[4].headers[HttpHeaders.PartitionKey]
                                     if HttpHeaders.PartitionKey in args[4].headers else '')
        except IndexError:
            self.last_headers.append('')
        return await self.OriginalExecuteFunction(function, *args, **kwargs)


if __name__ == '__main__':
    unittest.main()
