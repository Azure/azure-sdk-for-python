# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import os
import unittest
import uuid

import pytest

import azure.cosmos._retry_utility as retry_utility
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import http_constants, DatabaseProxy, _endpoint_discovery_retry_policy
from azure.cosmos._execution_context.base_execution_context import _QueryExecutionContextBase
from azure.cosmos._execution_context.query_execution_info import _PartitionedQueryExecutionInfo
from azure.cosmos.documents import _DistinctType
from azure.cosmos.partition_key import PartitionKey


class TestQuery(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    created_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    config = test_config.TestConfig
    host = config.host
    connectionPolicy = config.connectionPolicy
    TEST_DATABASE_ID = config.TEST_DATABASE_ID
    is_emulator = config.is_emulator
    credential = config.credential

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.credential)
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        if cls.host == "https://localhost:8081/":
            os.environ["AZURE_COSMOS_DISABLE_NON_STREAMING_ORDER_BY"] = "True"

    def test_first_and_last_slashes_trimmed_for_query_string(self):
        created_collection = self.created_db.create_container(
            "test_trimmed_slashes", PartitionKey(path="/pk"))
        doc_id = 'myId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk'
        )
        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], doc_id)
        self.created_db.delete_container(created_collection.id)

    def test_populate_query_metrics(self):
        created_collection = self.created_db.create_container("query_metrics_test",
                                                              PartitionKey(path="/pk"))
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk',
            populate_query_metrics=True
        )

        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], doc_id)

        METRICS_HEADER_NAME = 'x-ms-documentdb-query-metrics'
        self.assertTrue(METRICS_HEADER_NAME in created_collection.client_connection.last_response_headers)
        metrics_header = created_collection.client_connection.last_response_headers[METRICS_HEADER_NAME]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        self.assertTrue(len(metrics) > 1)
        self.assertTrue(all(['=' in x for x in metrics]))
        self.created_db.delete_container(created_collection.id)

    def test_populate_index_metrics(self):
        created_collection = self.created_db.create_container("query_index_test",
                                                              PartitionKey(path="/pk"))

        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk',
            populate_index_metrics=True
        )

        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], doc_id)

        INDEX_HEADER_NAME = http_constants.HttpHeaders.IndexUtilization
        self.assertTrue(INDEX_HEADER_NAME in created_collection.client_connection.last_response_headers)
        index_metrics = created_collection.client_connection.last_response_headers[INDEX_HEADER_NAME]
        self.assertIsNotNone(index_metrics)
        expected_index_metrics = {'UtilizedSingleIndexes': [{'FilterExpression': '', 'IndexSpec': '/pk/?',
                                                             'FilterPreciseSet': True, 'IndexPreciseSet': True,
                                                             'IndexImpactScore': 'High'}],
                                  'PotentialSingleIndexes': [], 'UtilizedCompositeIndexes': [],
                                  'PotentialCompositeIndexes': []}
        self.assertDictEqual(expected_index_metrics, index_metrics)
        self.created_db.delete_container(created_collection.id)

    # TODO: Need to validate the query request count logic
    @pytest.mark.skip
    def test_max_item_count_honored_in_order_by_query(self):
        created_collection = self.created_db.create_container("test-max-item-count" + str(uuid.uuid4()),
                                                              PartitionKey(path="/pk"))
        docs = []
        for i in range(10):
            document_definition = {'pk': 'pk', 'id': 'myId' + str(uuid.uuid4())}
            docs.append(created_collection.create_item(body=document_definition))

        query = 'SELECT * from c ORDER BY c._ts'
        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=1,
            enable_cross_partition_query=True
        )
        self.validate_query_requests_count(query_iterable, 25)

        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=100,
            enable_cross_partition_query=True
        )

        self.validate_query_requests_count(query_iterable, 5)
        self.created_db.delete_container(created_collection.id)

    def validate_query_requests_count(self, query_iterable, expected_count):
        self.count = 0
        self.OriginalExecuteFunction = retry_utility.ExecuteFunction
        retry_utility.ExecuteFunction = self._MockExecuteFunction
        for block in query_iterable.by_page():
            assert len(list(block)) != 0
        retry_utility.ExecuteFunction = self.OriginalExecuteFunction
        self.assertEqual(self.count, expected_count)
        self.count = 0

    def _MockExecuteFunction(self, function, *args, **kwargs):
        self.count += 1
        return self.OriginalExecuteFunction(function, *args, **kwargs)

    def test_get_query_plan_through_gateway(self):
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        self._validate_query_plan(query="Select top 10 value count(c.id) from c",
                                  container_link=created_collection.container_link,
                                  top=10,
                                  order_by=[],
                                  aggregate=['Count'],
                                  select_value=True,
                                  offset=None,
                                  limit=None,
                                  distinct=_DistinctType.NoneType)

        self._validate_query_plan(query="Select * from c order by c._ts offset 5 limit 10",
                                  container_link=created_collection.container_link,
                                  top=None,
                                  order_by=['Ascending'],
                                  aggregate=[],
                                  select_value=False,
                                  offset=5,
                                  limit=10,
                                  distinct=_DistinctType.NoneType)

        self._validate_query_plan(query="Select distinct value c.id from c order by c.id",
                                  container_link=created_collection.container_link,
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
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        queries = ['SELECT COUNT(1) FROM c', 'SELECT COUNT(1) + 5 FROM c', 'SELECT COUNT(1) + SUM(c) FROM c']
        for query in queries:
            query_iterable = created_collection.query_items(query=query, enable_cross_partition_query=True)
            try:
                list(query_iterable)
                self.fail()
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, 400)

    def test_query_with_non_overlapping_pk_ranges(self):
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        query_iterable = created_collection.query_items("select * from c where c.pk='1' or c.pk='2'",
                                                        enable_cross_partition_query=True)
        self.assertListEqual(list(query_iterable), [])

    def test_offset_limit(self):
        created_collection = self.created_db.create_container("offset_limit_test_" + str(uuid.uuid4()),
                                                              PartitionKey(path="/pk"))
        values = []
        for i in range(10):
            document_definition = {'pk': i, 'id': 'myId' + str(uuid.uuid4()), 'value': i // 3}
            values.append(created_collection.create_item(body=document_definition)['pk'])

        self._validate_distinct_offset_limit(created_collection=created_collection,
                                             query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 0 LIMIT 2',
                                             results=[0, 1])

        self._validate_distinct_offset_limit(created_collection=created_collection,
                                             query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 2 LIMIT 2',
                                             results=[2, 3])

        self._validate_distinct_offset_limit(created_collection=created_collection,
                                             query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 4 LIMIT 3',
                                             results=[])

        self._validate_offset_limit(created_collection=created_collection,
                                    query='SELECT * from c ORDER BY c.pk OFFSET 0 LIMIT 5',
                                    results=values[:5])

        self._validate_offset_limit(created_collection=created_collection,
                                    query='SELECT * from c ORDER BY c.pk OFFSET 5 LIMIT 10',
                                    results=values[5:])

        self._validate_offset_limit(created_collection=created_collection,
                                    query='SELECT * from c ORDER BY c.pk OFFSET 10 LIMIT 5',
                                    results=[])

        self._validate_offset_limit(created_collection=created_collection,
                                    query='SELECT * from c ORDER BY c.pk OFFSET 100 LIMIT 1',
                                    results=[])
        self.created_db.delete_container(created_collection.id)

    def _validate_offset_limit(self, created_collection, query, results):
        query_iterable = created_collection.query_items(
            query=query,
            enable_cross_partition_query=True
        )
        self.assertListEqual(list(map(lambda doc: doc['pk'], list(query_iterable))), results)

    def _validate_distinct_offset_limit(self, created_collection, query, results):
        query_iterable = created_collection.query_items(
            query=query,
            enable_cross_partition_query=True
        )
        self.assertListEqual(list(map(lambda doc: doc["value"], list(query_iterable))), results)

    def test_distinct(self):
        distinct_field = 'distinct_field'
        pk_field = "pk"
        different_field = "different_field"

        created_collection = self.created_db.create_container(
            id='collection with composite index ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk", kind="Hash"),
            indexing_policy={
                "compositeIndexes": [
                    [{"path": "/" + pk_field, "order": "ascending"},
                     {"path": "/" + distinct_field, "order": "ascending"}],
                    [{"path": "/" + distinct_field, "order": "ascending"},
                     {"path": "/" + pk_field, "order": "ascending"}]
                ]
            }
        )
        documents = []
        for i in range(5):
            j = i
            while j > i - 5:
                document_definition = {pk_field: i, 'id': str(uuid.uuid4()), distinct_field: j}
                documents.append(created_collection.create_item(body=document_definition))
                document_definition = {pk_field: i, 'id': str(uuid.uuid4()), distinct_field: j}
                documents.append(created_collection.create_item(body=document_definition))
                document_definition = {pk_field: i, 'id': str(uuid.uuid4())}
                documents.append(created_collection.create_item(body=document_definition))
                j -= 1

        padded_docs = self.config._pad_with_none(documents, distinct_field)

        self._validate_distinct(created_collection=created_collection,  # returns {} and is right number
                                query='SELECT distinct c.%s from c' % distinct_field,  # nosec
                                results=self.config._get_distinct_docs(padded_docs, distinct_field, None, False),
                                is_select=True,
                                fields=[distinct_field])

        self._validate_distinct(created_collection=created_collection,
                                query='SELECT distinct c.%s, c.%s from c' % (distinct_field, pk_field),  # nosec
                                results=self.config._get_distinct_docs(padded_docs, distinct_field, pk_field, False),
                                is_select=True,
                                fields=[distinct_field, pk_field])

        self._validate_distinct(created_collection=created_collection,
                                query='SELECT distinct value c.%s from c' % distinct_field,  # nosec
                                results=self.config._get_distinct_docs(padded_docs, distinct_field, None, True),
                                is_select=True,
                                fields=[distinct_field])

        self._validate_distinct(created_collection=created_collection,
                                query='SELECT distinct c.%s from c' % different_field,  # nosec
                                results=['None'],
                                is_select=True,
                                fields=[different_field])

        self.created_db.delete_container(created_collection.id)

    def _validate_distinct(self, created_collection, query, results, is_select, fields):
        query_iterable = created_collection.query_items(
            query=query,
            enable_cross_partition_query=True
        )
        query_results = list(query_iterable)

        self.assertEqual(len(results), len(query_results))
        query_results_strings = []
        result_strings = []
        for i in range(len(results)):
            query_results_strings.append(self.config._get_query_result_string(query_results[i], fields))
            result_strings.append(str(results[i]))
        if is_select:
            query_results_strings = sorted(query_results_strings)
            result_strings = sorted(result_strings)
        self.assertListEqual(result_strings, query_results_strings)

    def test_distinct_on_different_types_and_field_orders(self):
        created_collection = self.created_db.create_container(
            id="test-distinct-container-" + str(uuid.uuid4()),
            partition_key=PartitionKey("/pk"),
            offer_throughput=self.config.THROUGHPUT_FOR_5_PARTITIONS)
        self.payloads = [
            {'f1': 1, 'f2': 'value', 'f3': 100000000000000000, 'f4': [1, 2, '3'], 'f5': {'f6': {'f7': 2}}},
            {'f2': '\'value', 'f4': [1.0, 2, '3'], 'f5': {'f6': {'f7': 2.0}}, 'f1': 1.0, 'f3': 100000000000000000.00},
            {'f3': 100000000000000000.0, 'f5': {'f6': {'f7': 2}}, 'f2': '\'value', 'f1': 1, 'f4': [1, 2.0, '3']}
        ]
        self.OriginalExecuteFunction = _QueryExecutionContextBase.__next__
        _QueryExecutionContextBase.__next__ = self._MockNextFunction

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f1 from c",
            expected_results=[1],
            get_mock_result=lambda x, i: (None, x[i]["f1"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f2 from c",
            expected_results=['value', '\'value'],
            get_mock_result=lambda x, i: (None, x[i]["f2"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f2 from c order by c.f2",
            expected_results=['\'value', 'value'],
            get_mock_result=lambda x, i: (x[i]["f2"], x[i]["f2"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f3 from c",
            expected_results=[100000000000000000],
            get_mock_result=lambda x, i: (None, x[i]["f3"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f4 from c",
            expected_results=[[1, 2, '3']],
            get_mock_result=lambda x, i: (None, x[i]["f4"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f5.f6 from c",
            expected_results=[{'f7': 2}],
            get_mock_result=lambda x, i: (None, x[i]["f5"]["f6"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct c.f1, c.f2, c.f3 from c",
            expected_results=[self.payloads[0], self.payloads[1]],
            get_mock_result=lambda x, i: (None, x[i])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct c.f1, c.f2, c.f3 from c order by c.f1",
            expected_results=[self.payloads[0], self.payloads[1]],
            get_mock_result=lambda x, i: (i, x[i])
        )

        _QueryExecutionContextBase.__next__ = self.OriginalExecuteFunction
        _QueryExecutionContextBase.next = self.OriginalExecuteFunction

        self.created_db.delete_container(created_collection.id)

    def test_paging_with_continuation_token(self):
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)

        document_definition = {'pk': 'pk', 'id': '1'}
        created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': '2'}
        created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
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
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        document_definition = {'pk': 'pk1', 'id': str(uuid.uuid4())}
        created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk2', 'id': str(uuid.uuid4())}
        created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
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
        container = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        query = "Select value max(c.version) FROM c where c.isComplete = true and c.lookupVersion = @lookupVersion"
        query_results = container.query_items(query, parameters=[
            {"name": "@lookupVersion", "value": "console_csat"}  # cspell:disable-line
        ], enable_cross_partition_query=True)

        self.assertListEqual(list(query_results), [None])

    def test_continuation_token_size_limit_query(self):
        container = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        for i in range(1, 1000):
            container.create_item(body=dict(pk='123', id=str(uuid.uuid4()), some_value=str(i % 3)))
        query = "Select * from c where c.some_value='2'"
        response_query = container.query_items(query, partition_key='123', max_item_count=100,
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

    def test_query_request_params_none_retry_policy(self):
        created_collection = self.created_db.create_container(
            "query_request_params_none_retry_policy_" + str(uuid.uuid4()), PartitionKey(path="/pk"))
        items = [
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5}]

        for item in items:
            created_collection.create_item(body=item)

        self.OriginalExecuteFunction = retry_utility.ExecuteFunction
        # Test session retry will properly push the exception when retries run out
        retry_utility.ExecuteFunction = self._MockExecuteFunctionSessionRetry
        try:
            query = "SELECT * FROM c"
            items = created_collection.query_items(
                query=query,
                enable_cross_partition_query=True
            )
            fetch_results = list(items)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, 404)
            self.assertEqual(e.sub_status, 1002)

        # Test endpoint discovery retry
        retry_utility.ExecuteFunction = self._MockExecuteFunctionEndPointRetry
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Max_retry_attempt_count = 3
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Retry_after_in_milliseconds = 10
        try:
            query = "SELECT * FROM c"
            items = created_collection.query_items(
                query=query,
                enable_cross_partition_query=True
            )
            fetch_results = list(items)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, http_constants.StatusCodes.FORBIDDEN)
            self.assertEqual(e.sub_status, http_constants.SubStatusCodes.WRITE_FORBIDDEN)
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Max_retry_attempt_count = 120
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Retry_after_in_milliseconds = 1000

        # Finally lets test timeout failover retry
        retry_utility.ExecuteFunction = self._MockExecuteFunctionTimeoutFailoverRetry
        try:
            query = "SELECT * FROM c"
            items = created_collection.query_items(
                query=query,
                enable_cross_partition_query=True
            )
            fetch_results = list(items)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, http_constants.StatusCodes.REQUEST_TIMEOUT)
            retry_utility.ExecuteFunction = self.OriginalExecuteFunction
        retry_utility.ExecuteFunction = self.OriginalExecuteFunction
        self.created_db.delete_container(created_collection.id)


    def _MockExecuteFunctionSessionRetry(self, function, *args, **kwargs):
        if args:
            if args[1].operation_type == 'SqlQuery':
                ex_to_raise = exceptions.CosmosHttpResponseError(status_code=http_constants.StatusCodes.NOT_FOUND,
                                                                 message="Read Session is Not Available")
                ex_to_raise.sub_status = http_constants.SubStatusCodes.READ_SESSION_NOTAVAILABLE
                raise ex_to_raise
        return self.OriginalExecuteFunction(function, *args, **kwargs)

    def _MockExecuteFunctionEndPointRetry(self, function, *args, **kwargs):
        if args:
            if args[1].operation_type == 'SqlQuery':
                ex_to_raise = exceptions.CosmosHttpResponseError(status_code=http_constants.StatusCodes.FORBIDDEN,
                                                                 message="End Point Discovery")
                ex_to_raise.sub_status = http_constants.SubStatusCodes.WRITE_FORBIDDEN
                raise ex_to_raise
        return self.OriginalExecuteFunction(function, *args, **kwargs)

    def _MockExecuteFunctionTimeoutFailoverRetry(self, function, *args, **kwargs):
        if args:
            if args[1].operation_type == 'SqlQuery':
                ex_to_raise = exceptions.CosmosHttpResponseError(status_code=http_constants.StatusCodes.REQUEST_TIMEOUT,
                                                                 message="Timeout Failover")
                raise ex_to_raise
        return self.OriginalExecuteFunction(function, *args, **kwargs)

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
