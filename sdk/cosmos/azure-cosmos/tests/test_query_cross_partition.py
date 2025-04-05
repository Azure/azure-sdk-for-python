# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import os
import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import http_constants, DatabaseProxy
from azure.cosmos._execution_context.base_execution_context import _QueryExecutionContextBase
from azure.cosmos._execution_context.query_execution_info import _PartitionedQueryExecutionInfo
from azure.cosmos.documents import _DistinctType
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosQuery
class TestCrossPartitionQuery(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    created_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    config = test_config.TestConfig
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy
    TEST_DATABASE_ID = config.TEST_DATABASE_ID
    TEST_CONTAINER_ID = "Multi Partition Test Collection With Custom PK " + str(uuid.uuid4())

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        if cls.host == "https://localhost:8081/":
            os.environ["AZURE_COSMOS_DISABLE_NON_STREAMING_ORDER_BY"] = "True"

    def setUp(self):
        self.created_container = self.created_db.create_container(
            id=self.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=test_config.TestConfig.THROUGHPUT_FOR_5_PARTITIONS)

    def tearDown(self):
        try:
            self.created_db.delete_container(self.TEST_CONTAINER_ID)
        except exceptions.CosmosHttpResponseError:
            pass

    def test_first_and_last_slashes_trimmed_for_query_string(self):
        doc_id = 'myId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        self.created_container.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = self.created_container.query_items(
            query=query,
            partition_key='pk'
        )
        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], doc_id)

    def test_query_change_feed_with_pk(self):
        # The test targets partition #3
        partition_key = "pk"

        # Read change feed without passing any options
        query_iterable = self.created_container.query_items_change_feed()
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)

        # Read change feed from current should return an empty list
        query_iterable = self.created_container.query_items_change_feed(partition_key=partition_key)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in self.created_container.client_connection.last_response_headers)
        self.assertNotEqual(self.created_container.client_connection.last_response_headers['etag'], '')

        # Read change feed from beginning should return an empty list
        query_iterable = self.created_container.query_items_change_feed(
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in self.created_container.client_connection.last_response_headers)
        continuation1 = self.created_container.client_connection.last_response_headers['etag']
        self.assertNotEqual(continuation1, '')

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id': 'doc1'}
        self.created_container.create_item(body=document_definition)
        query_iterable = self.created_container.query_items_change_feed(
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 1)
        self.assertEqual(iter_list[0]['id'], 'doc1')
        self.assertTrue('etag' in self.created_container.client_connection.last_response_headers)
        continuation2 = self.created_container.client_connection.last_response_headers['etag']
        self.assertNotEqual(continuation2, '')
        self.assertNotEqual(continuation2, continuation1)

        # Create two new documents. Verify that change feed contains the 2 new documents
        # with page size 1 and page size 100
        document_definition = {'pk': 'pk', 'id': 'doc2'}
        self.created_container.create_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': 'doc3'}
        self.created_container.create_item(body=document_definition)

        for pageSize in [1, 100]:
            # verify iterator
            query_iterable = self.created_container.query_items_change_feed(
                continuation=continuation2,
                max_item_count=pageSize,
                partition_key=partition_key
            )
            it = query_iterable.__iter__()
            expected_ids = 'doc2.doc3.'
            actual_ids = ''
            for item in it:
                actual_ids += item['id'] + '.'
            self.assertEqual(actual_ids, expected_ids)

            # verify by_page
            # the options is not copied, therefore it need to be restored
            query_iterable = self.created_container.query_items_change_feed(
                continuation=continuation2,
                max_item_count=pageSize,
                partition_key=partition_key
            )
            count = 0
            expected_count = 2
            all_fetched_res = []
            for page in query_iterable.by_page():
                fetched_res = list(page)
                self.assertEqual(len(fetched_res), min(pageSize, expected_count - count))
                count += len(fetched_res)
                all_fetched_res.extend(fetched_res)

            actual_ids = ''
            for item in all_fetched_res:
                actual_ids += item['id'] + '.'
            self.assertEqual(actual_ids, expected_ids)

        # verify reading change feed from the beginning
        query_iterable = self.created_container.query_items_change_feed(
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        expected_ids = ['doc1', 'doc2', 'doc3']
        it = query_iterable.__iter__()
        for i in range(0, len(expected_ids)):
            doc = next(it)
            self.assertEqual(doc['id'], expected_ids[i])
        self.assertTrue('etag' in self.created_container.client_connection.last_response_headers)
        continuation3 = self.created_container.client_connection.last_response_headers['etag']

        # verify reading empty change feed
        query_iterable = self.created_container.query_items_change_feed(
            continuation=continuation3,
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)

    def test_populate_query_metrics(self):
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        self.created_container.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = self.created_container.query_items(
            query=query,
            partition_key='pk',
            populate_query_metrics=True
        )

        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], doc_id)

        metrics_header_name = 'x-ms-documentdb-query-metrics'
        self.assertTrue(metrics_header_name in self.created_container.client_connection.last_response_headers)
        metrics_header = self.created_container.client_connection.last_response_headers[metrics_header_name]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        self.assertTrue(len(metrics) > 1)
        self.assertTrue(all(['=' in x for x in metrics]))

    def test_populate_index_metrics(self):
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        self.created_container.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = self.created_container.query_items(
            query=query,
            partition_key='pk',
            populate_index_metrics=True
        )

        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], doc_id)

        INDEX_HEADER_NAME = http_constants.HttpHeaders.IndexUtilization
        self.assertTrue(INDEX_HEADER_NAME in self.created_container.client_connection.last_response_headers)
        index_metrics = self.created_container.client_connection.last_response_headers[INDEX_HEADER_NAME]
        self.assertIsNotNone(index_metrics)
        expected_index_metrics = {'UtilizedSingleIndexes': [{'FilterExpression': '', 'IndexSpec': '/pk/?',
                                                             'FilterPreciseSet': True, 'IndexPreciseSet': True,
                                                             'IndexImpactScore': 'High'}],
                                  'PotentialSingleIndexes': [], 'UtilizedCompositeIndexes': [],
                                  'PotentialCompositeIndexes': []}
        self.assertDictEqual(expected_index_metrics, index_metrics)

    def test_get_query_plan_through_gateway(self):
        self._validate_query_plan(query="Select top 10 value count(c.id) from c",
                                  container_link=self.created_container.container_link,
                                  top=10,
                                  order_by=[],
                                  aggregate=['Count'],
                                  select_value=True,
                                  offset=None,
                                  limit=None,
                                  distinct=_DistinctType.NoneType)

        self._validate_query_plan(query="Select * from c order by c._ts offset 5 limit 10",
                                  container_link=self.created_container.container_link,
                                  top=None,
                                  order_by=['Ascending'],
                                  aggregate=[],
                                  select_value=False,
                                  offset=5,
                                  limit=10,
                                  distinct=_DistinctType.NoneType)

        self._validate_query_plan(query="Select distinct value c.id from c order by c.id",
                                  container_link=self.created_container.container_link,
                                  top=None,
                                  order_by=['Ascending'],
                                  aggregate=[],
                                  select_value=True,
                                  offset=None,
                                  limit=None,
                                  distinct=_DistinctType.Ordered)

    def _validate_query_plan(self, query, container_link, top, order_by, aggregate, select_value, offset, limit,
                             distinct):
        query_plan_dict = self.client.client_connection._GetQueryPlanThroughGateway(query, container_link)
        query_execution_info = _PartitionedQueryExecutionInfo(query_plan_dict)
        self.assertTrue(query_execution_info.has_rewritten_query())
        self.assertEqual(query_execution_info.has_distinct_type(), distinct != "None")
        self.assertEqual(query_execution_info.get_distinct_type(), distinct)
        self.assertEqual(query_execution_info.has_top(), top is not None)
        self.assertEqual(query_execution_info.get_top(), top)
        self.assertEqual(query_execution_info.has_order_by(), len(order_by) > 0)
        self.assertListEqual(query_execution_info.get_order_by(), order_by)
        self.assertEqual(query_execution_info.has_aggregates(), len(aggregate) > 0)
        self.assertListEqual(query_execution_info.get_aggregates(), aggregate)
        self.assertEqual(query_execution_info.has_select_value(), select_value)
        self.assertEqual(query_execution_info.has_offset(), offset is not None)
        self.assertEqual(query_execution_info.get_offset(), offset)
        self.assertEqual(query_execution_info.has_limit(), limit is not None)
        self.assertEqual(query_execution_info.get_limit(), limit)

    def test_unsupported_queries(self):
        queries = ['SELECT COUNT(1) FROM c', 'SELECT COUNT(1) + 5 FROM c', 'SELECT COUNT(1) + SUM(c) FROM c']
        for query in queries:
            query_iterable = self.created_container.query_items(query=query, enable_cross_partition_query=True)
            try:
                list(query_iterable)
                self.fail()
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, 400)

    def test_query_with_non_overlapping_pk_ranges(self):
        query_iterable = self.created_container.query_items("select * from c where c.pk='1' or c.pk='2'",
                                                            enable_cross_partition_query=True)
        self.assertListEqual(list(query_iterable), [])

    def test_offset_limit(self):
        values = []
        for i in range(10):
            document_definition = {'pk': i, 'id': 'myId' + str(uuid.uuid4()), 'value': i // 3}
            values.append(self.created_container.create_item(body=document_definition)['pk'])

        self.config._validate_distinct_offset_limit(
            created_collection=self.created_container,
            query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 0 LIMIT 2',
            results=[0, 1])

        self.config._validate_distinct_offset_limit(
            created_collection=self.created_container,
            query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 2 LIMIT 2',
            results=[2, 3])

        self.config._validate_distinct_offset_limit(
            created_collection=self.created_container,
            query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 4 LIMIT 3',
            results=[])

        self.config._validate_offset_limit(created_collection=self.created_container,
                                           query='SELECT * from c ORDER BY c.pk OFFSET 0 LIMIT 5',
                                           results=values[:5])

        self.config._validate_offset_limit(created_collection=self.created_container,
                                           query='SELECT * from c ORDER BY c.pk OFFSET 5 LIMIT 10',
                                           results=values[5:])

        self.config._validate_offset_limit(created_collection=self.created_container,
                                           query='SELECT * from c ORDER BY c.pk OFFSET 10 LIMIT 5',
                                           results=[])

        self.config._validate_offset_limit(created_collection=self.created_container,
                                           query='SELECT * from c ORDER BY c.pk OFFSET 100 LIMIT 1',
                                           results=[])

    def test_distinct_on_different_types_and_field_orders(self):
        self.payloads = [
            {'f1': 1, 'f2': 'value', 'f3': 100000000000000000, 'f4': [1, 2, '3'], 'f5': {'f6': {'f7': 2}}},
            {'f2': '\'value', 'f4': [1.0, 2, '3'], 'f5': {'f6': {'f7': 2.0}}, 'f1': 1.0, 'f3': 100000000000000000.00},
            {'f3': 100000000000000000.0, 'f5': {'f6': {'f7': 2}}, 'f2': '\'value', 'f1': 1, 'f4': [1, 2.0, '3']}
        ]
        self.OriginalExecuteFunction = _QueryExecutionContextBase.__next__
        _QueryExecutionContextBase.__next__ = self._MockNextFunction

        self._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct value c.f1 from c",
            expected_results=[1],
            get_mock_result=lambda x, i: (None, x[i]["f1"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct value c.f2 from c",
            expected_results=['value', '\'value'],
            get_mock_result=lambda x, i: (None, x[i]["f2"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct value c.f2 from c order by c.f2",
            expected_results=['\'value', 'value'],
            get_mock_result=lambda x, i: (x[i]["f2"], x[i]["f2"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct value c.f3 from c",
            expected_results=[100000000000000000],
            get_mock_result=lambda x, i: (None, x[i]["f3"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct value c.f4 from c",
            expected_results=[[1, 2, '3']],
            get_mock_result=lambda x, i: (None, x[i]["f4"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct value c.f5.f6 from c",
            expected_results=[{'f7': 2}],
            get_mock_result=lambda x, i: (None, x[i]["f5"]["f6"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct c.f1, c.f2, c.f3 from c",
            expected_results=[self.payloads[0], self.payloads[1]],
            get_mock_result=lambda x, i: (None, x[i])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct c.f1, c.f2, c.f3 from c order by c.f1",
            expected_results=[self.payloads[0], self.payloads[1]],
            get_mock_result=lambda x, i: (i, x[i])
        )

        _QueryExecutionContextBase.__next__ = self.OriginalExecuteFunction
        _QueryExecutionContextBase.next = self.OriginalExecuteFunction

    def test_paging_with_continuation_token(self):
        document_definition = {'pk': 'pk', 'id': '1'}
        self.created_container.create_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': '2'}
        self.created_container.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = self.created_container.query_items(
            query=query,
            partition_key='pk',
            max_item_count=1
        )
        pager = query_iterable.by_page()
        pager.next()
        token = pager.continuation_token
        second_page = list(pager.next())[0]

        pager = query_iterable.by_page(token)
        second_page_fetched_with_continuation_token = list(pager.next())[0]

        self.assertEqual(second_page['id'], second_page_fetched_with_continuation_token['id'])

    def test_cross_partition_query_with_continuation_token(self):
        document_definition = {'pk': 'pk1', 'id': str(uuid.uuid4())}
        self.created_container.create_item(body=document_definition)
        document_definition = {'pk': 'pk2', 'id': str(uuid.uuid4())}
        self.created_container.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = self.created_container.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        pager.next()
        token = pager.continuation_token
        second_page = list(pager.next())[0]

        pager = query_iterable.by_page(token)
        second_page_fetched_with_continuation_token = list(pager.next())[0]

        self.assertEqual(second_page['id'], second_page_fetched_with_continuation_token['id'])

    def _validate_distinct_on_different_types_and_field_orders(self, collection, query, expected_results,
                                                               get_mock_result):
        self.count = 0
        self.get_mock_result = get_mock_result
        query_iterable = collection.query_items(query, enable_cross_partition_query=True)
        results = list(query_iterable)
        for i in range(len(expected_results)):
            if isinstance(results[i], dict):
                self.assertDictEqual(results[i], expected_results[i])
            elif isinstance(results[i], list):
                self.assertListEqual(results[i], expected_results[i])
            else:
                self.assertEqual(results[i], expected_results[i])
        self.count = 0

    def test_value_max_query(self):
        query = "Select value max(c.version) FROM c where c.isComplete = true and c.lookupVersion = @lookupVersion"
        query_results = self.created_container.query_items(query, parameters=[
            {"name": "@lookupVersion", "value": "console_csat"}  # cspell:disable-line
        ], enable_cross_partition_query=True)

        self.assertListEqual(list(query_results), [None])

    def test_continuation_token_size_limit_query(self):
        for i in range(1, 1000):
            self.created_container.create_item(body=dict(pk='123', id=str(i), some_value=str(i % 3)))
        query = "Select * from c where c.some_value='2'"
        response_query = self.created_container.query_items(query, partition_key='123', max_item_count=100,
                                                            continuation_token_limit=1)
        pager = response_query.by_page()
        pager.next()
        token = pager.continuation_token
        # Continuation token size should be below 1kb
        self.assertLessEqual(len(token.encode('utf-8')), 1024)
        pager.next()
        token = pager.continuation_token

        # verify a second time
        self.assertLessEqual(len(token.encode('utf-8')), 1024)

    def _MockNextFunction(self):
        if self.count < len(self.payloads):
            item, result = self.get_mock_result(self.payloads, self.count)
            self.count += 1
            if item is not None:
                return {'orderByItems': [{'item': item}], '_rid': 'fake_rid', 'payload': result}
            else:
                return result
        else:
            raise StopIteration


if __name__ == "__main__":
    unittest.main()
