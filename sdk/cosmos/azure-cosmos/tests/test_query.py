# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import os
import unittest
import uuid
from unittest.mock import patch

import pytest

import azure.cosmos._retry_utility as retry_utility
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import http_constants, DatabaseProxy, _endpoint_discovery_retry_policy, _synchronized_request
from azure.cosmos._routing.feed_range_continuation import _decode_token
from azure.cosmos._execution_context.base_execution_context import _QueryExecutionContextBase
from azure.cosmos._execution_context.query_execution_info import _PartitionedQueryExecutionInfo
from azure.cosmos.documents import _DistinctType
from azure.cosmos.partition_key import PartitionKey

@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQuery(unittest.TestCase):
    """Live query tests: exercise Container.query_items across the query features customers rely
    on -- partition-scoped and cross-partition queries, paging with continuation tokens, DISTINCT /
    OFFSET-LIMIT / VALUE aggregates, query and index metrics, positional args, None parameters, and
    retry behavior. Without these, a change to the query path could silently return wrong results,
    skip or duplicate pages, or break a customer's error/retry handling."""

    created_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    key_client: cosmos_client.CosmosClient = None
    key_db: DatabaseProxy = None
    config = test_config.TestConfig
    host = config.host
    connectionPolicy = config.connectionPolicy
    TEST_DATABASE_ID = config.TEST_DATABASE_ID
    is_emulator = config.is_emulator
    credential = config.masterKey

    @classmethod
    def setUpClass(cls):
        use_multiple_write_locations = False
        if os.environ.get("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER", "False") == "True":
            use_multiple_write_locations = True
        # Keep multi-write-region routing enabled during circuit-breaker runs.
        cls.key_client = cosmos_client.CosmosClient(
            cls.host,
            cls.credential,
            multiple_write_locations=use_multiple_write_locations,
        )
        cls.key_db = cls.key_client.get_database_client(cls.TEST_DATABASE_ID)
        cls.client = test_config.TestConfig.create_data_client()
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)

    def _create_container_for_test(self, *args, **kwargs):
        container_ref = self.key_db.create_container(*args, **kwargs)
        return self.created_db.get_container_client(container_ref.id)

    def _delete_container_for_test(self, *args, **kwargs):
        return self.key_db.delete_container(*args, **kwargs)


    def test_first_and_last_slashes_trimmed_for_query_string(self):
        created_collection = self._create_container_for_test(
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
        self._delete_container_for_test(created_collection.id)

    # TODO: Need to validate the query request count logic
    @pytest.mark.skip
    def test_max_item_count_honored_in_order_by_query(self):
        created_collection = self._create_container_for_test("test-max-item-count" + str(uuid.uuid4()),
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
        self._delete_container_for_test(created_collection.id)

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

    # TODO: migrate to AAD once service-side RBAC activation window (403/5302) fix ships.
    @pytest.mark.skipif(
        test_config.TestConfig.data_auth_mode == 'aad',
        reason="post-create RBAC activation window (403/5302)  -  migrate after service-side fix",
    )
    def test_distinct_on_different_types_and_field_orders(self):
        created_collection = self._create_container_for_test(
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

        self._delete_container_for_test(created_collection.id)

    def test_full_pk_continuation_emits_legacy_by_default(self):
        # A full-partition-key query must still hand back the legacy (opaque) continuation
        # token, not the new feed-range token: _decode_token returns None only for the legacy
        # form. Without this, changing the default token format could break customers who
        # stored an old token and replay it later.
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})
        created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})

        query_iterable = created_collection.query_items(
            query='SELECT * from c',
            partition_key='pk',
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        pager.next()
        token = pager.continuation_token

        self.assertIsNotNone(token)
        self.assertIsNone(_decode_token(token))


    def test_full_pk_legacy_replay_resumes_same_page(self):
        # Replaying that legacy continuation token must resume on the same next page. Without
        # this, a regression in legacy-token replay would drop or repeat results for customers
        # who page through query results.
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})
        created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})

        query_iterable = created_collection.query_items(
            query='SELECT * from c',
            partition_key='pk',
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        pager.next()
        token = pager.continuation_token
        second_page = list(pager.next())[0]

        self.assertIsNotNone(token)
        self.assertIsNone(_decode_token(token))

        replay_pager = query_iterable.by_page(token)
        replay_second_page = list(replay_pager.next())[0]
        self.assertEqual(second_page['id'], replay_second_page['id'])



    def test_cross_partition_query_with_none_partition_key(self):
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        document_definition = {'pk': 'pk1', 'id': str(uuid.uuid4())}
        created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk2', 'id': str(uuid.uuid4())}
        created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key=None,
            enable_cross_partition_query=True
        )

        assert len(list(query_iterable)) >= 2

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

    def test_query_request_params_none_retry_policy(self):
        created_collection = self._create_container_for_test(
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
        self._delete_container_for_test(created_collection.id)

    def test_query_pagination_without_max_item_count(self):
        """Test pagination behavior without specifying max_item_count."""
        created_collection = self._create_container_for_test(
            "pagination_no_max_test_" + str(uuid.uuid4()),
            PartitionKey(path="/pk"))
        
        # Create 15 items in a single partition
        total_items = 15
        partition_key_value = "test_pk_2"
        for i in range(total_items):
            document_definition = {
                'pk': partition_key_value,
                'id': f'item_{i}',
                'value': i
            }
            created_collection.create_item(body=document_definition)
        
        # Query without specifying max_item_count
        query = "SELECT * FROM c WHERE c.pk = @pk"
        query_iterable = created_collection.query_items(
            query=query,
            parameters=[{"name": "@pk", "value": partition_key_value}],
            partition_key=partition_key_value
        )
        
        # Count total results
        all_results = list(query_iterable)
        self.assertEqual(len(all_results), total_items)
        
        self._delete_container_for_test(created_collection.id)

    def test_query_positional_args(self):
        container = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        partition_key_value1 = "pk1"
        partition_key_value2 = "pk2"

        num_items = 10
        new_items = []
        for pk_value in [partition_key_value1, partition_key_value2]:
            for i in range(num_items):
                item = {
                    self.config.TEST_CONTAINER_PARTITION_KEY: pk_value,
                    'id': f"{pk_value}_{i}",
                    'name': 'sample name'
                }
                new_items.append(item)

        for item in new_items:
            container.upsert_item(body=item)

        query = "SELECT * FROM root r WHERE r.name=@name"
        parameters = [{'name': '@name', 'value': 'sample name'}]
        partition_key_value = partition_key_value2
        enable_cross_partition_query = True
        max_item_count = 3
        enable_scan_in_query = True
        populate_query_metrics = True
        pager = container.query_items(
            query,
            parameters,
            partition_key_value,
            enable_cross_partition_query,
            max_item_count,
            enable_scan_in_query,
            populate_query_metrics,
        ).by_page()

        ids = []
        for page in pager:
            items = list(page)
            num_items = len(items)
            for item in items:
                assert item['pk'] == partition_key_value
                ids.append(item['id'])
            assert num_items <= max_item_count
        assert ids == [item['id'] for item in new_items if item['pk'] == partition_key_value]

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

    def test_query_items_parameters_none_with_options(self):
        """Test parameters=None works with various query options."""
        created_collection = self._create_container_for_test(
            "test_params_none_opts_" + str(uuid.uuid4()), PartitionKey(path="/pk"))
        
        # Create multiple test documents
        for i in range(5):
            doc_id = f'doc_{i}_' + str(uuid.uuid4())
            created_collection.create_item(body={'pk': 'test', 'id': doc_id, 'index': i})

        # Test with parameters=None and max_item_count
        query = 'SELECT * FROM c ORDER BY c.index'
        query_iterable = created_collection.query_items(
            query=query,
            parameters=None,
            partition_key='test',
            max_item_count=2
        )
        
        # Verify pagination works
        page_count = 0
        total_items = 0
        for page in query_iterable.by_page():
            page_count += 1
            items = list(page)
            total_items += len(items)
            self.assertLessEqual(len(items), 2)
        
        self.assertEqual(total_items, 5)
        self.assertGreaterEqual(page_count, 2)  # Should have multiple pages

        # Test with parameters=None and populate_query_metrics
        query_iterable = created_collection.query_items(
            query=query,
            parameters=None,
            partition_key='test',
            populate_query_metrics=True
        )
        results = list(query_iterable)
        self.assertEqual(len(results), 5)
        
        # Verify query metrics were populated
        metrics_header_name = 'x-ms-documentdb-query-metrics'
        self.assertTrue(metrics_header_name in created_collection.client_connection.last_response_headers)

        self._delete_container_for_test(created_collection.id)


    # by_page() coverage for the outer timeout, connection_timeout,
    # resume from a continuation token, and the cross-partition AVG
    # error.

    def _capture_pipeline_kwarg(self, kwarg_name):
        # Wraps the outgoing HTTP call so each request records its URL
        # and the value of the named kwarg the SDK passed along.
        captured = []
        original = _synchronized_request._PipelineRunFunction

        def _wrapper(pipeline_client, request, **kwargs):
            captured.append((str(request.url), kwargs.get(kwarg_name)))
            return original(pipeline_client, request, **kwargs)

        return captured, patch.object(
            _synchronized_request, "_PipelineRunFunction", side_effect=_wrapper,
        )

    def test_outer_timeout_propagates_through_by_page_paging(self):
        # The outer wall-clock timeout must reach every page fetch when
        # a cross-partition query is walked one page at a time. The
        # remaining budget may decrement across attempts, but it must
        # never be dropped and must never exceed the requested value.
        container = self._create_container_for_test(
            "by_page_outer_timeout_" + str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            offer_throughput=11000,
        )
        try:
            for i in range(6):
                container.create_item(
                    {"id": f"item_{i}_{uuid.uuid4()}", "pk": i % 2, "data": i}
                )

            outer_timeout = 15
            captured, ctx = self._capture_pipeline_kwarg("timeout")
            with ctx:
                pages = container.query_items(
                    query="SELECT * FROM c",
                    enable_cross_partition_query=True,
                    max_item_count=1,
                    timeout=outer_timeout,
                ).by_page()
                for page in pages:
                    list(page)
            doc_values = [t for (url, t) in captured if "/docs" in url]
            self.assertGreater(len(doc_values), 0)
            non_none = [t for t in doc_values if t is not None]
            self.assertGreater(len(non_none), 0)
            for t in non_none:
                self.assertLessEqual(t, outer_timeout)
        finally:
            self._delete_container_for_test(container.id)

    def test_connection_timeout_propagates_through_by_page_paging(self):
        # connection_timeout is per-attempt, so it must reach every
        # page fetch as the same exact value the caller passed in.
        container = self._create_container_for_test(
            "by_page_conn_timeout_" + str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            offer_throughput=11000,
        )
        try:
            for i in range(6):
                container.create_item(
                    {"id": f"item_{i}_{uuid.uuid4()}", "pk": i % 2, "data": i}
                )

            connection_timeout = 27
            captured, ctx = self._capture_pipeline_kwarg("connection_timeout")
            with ctx:
                pages = container.query_items(
                    query="SELECT * FROM c",
                    enable_cross_partition_query=True,
                    max_item_count=1,
                    connection_timeout=connection_timeout,
                ).by_page()
                for page in pages:
                    list(page)
            doc_values = [t for (url, t) in captured if "/docs" in url]
            self.assertGreater(len(doc_values), 0)
            self.assertTrue(all(t == connection_timeout for t in doc_values))
        finally:
            self._delete_container_for_test(container.id)

    def test_avg_aggregate_by_page_raises_value_error_cross_partition(self):
        # A VALUE AVG query across multiple partitions cannot be merged
        # to a correct result on the client, so the SDK must raise
        # ValueError. A single-partition AVG is the supported workaround
        # and is verified as a control at the end.
        container = self._create_container_for_test(
            "by_page_avg_cross_" + str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            offer_throughput=11000,
        )
        try:
            # Seed across many distinct partition key values so the
            # query has data on multiple physical partitions to merge.
            for i in range(20):
                container.create_item(
                    {"id": f"item_{i}_{uuid.uuid4()}", "pk": f"pk_{i}", "amount": i + 10}
                )

            # A feed range that covers the full hash space forces the
            # query to fan out across every physical partition.
            full_range = test_config.create_range(
                range_min="",
                range_max="FF",
                is_min_inclusive=True,
                is_max_inclusive=False,
            )
            feed_range = test_config.create_feed_range_in_dict(full_range)

            with self.assertRaises(ValueError) as cm:
                pages = container.query_items(
                    query="SELECT VALUE AVG(c.amount) FROM c",
                    feed_range=feed_range,
                    max_item_count=1,
                ).by_page()
                for page in pages:
                    list(page)
            self.assertIn("AVG", str(cm.exception).upper())

            # Control: a single-partition AVG must still succeed.
            single_pages = container.query_items(
                query="SELECT VALUE AVG(c.amount) FROM c WHERE c.pk = @pk",
                parameters=[{"name": "@pk", "value": "pk_0"}],
                partition_key="pk_0",
                max_item_count=1,
            ).by_page()
            single_result = []
            for page in single_pages:
                single_result.extend(list(page))
            self.assertEqual(len(single_result), 1)
        finally:
            self._delete_container_for_test(container.id)



if __name__ == "__main__":
    unittest.main()
