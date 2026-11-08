# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-path copies of the sync cross-partition query tests.

Source: ``tests/test_query_cross_partition.py``. The class name, lane markers,
query inputs and assertions match the original; method names add ``_rust``.
Instead of the shared ``test_config`` database, the class owns a unique
database (key-auth Rust client for control plane, Rust data client for data
plane) and deletes it in ``tearDownClass``. Each test still creates and
deletes its own 5-partition ``/pk`` container, as the original does.
Rust-backed clients reject ``multiple_write_locations`` (Rust owns multi-write
routing), so the original's circuit-breaker toggle is omitted.

Run with::

    pytest --noconftest tests/query_items/sync/test_query_cross_partition.py -v
"""
import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
from azure.cosmos import CosmosClient, DatabaseProxy, http_constants
from azure.cosmos._execution_context.base_execution_context import _QueryExecutionContextBase
from azure.cosmos.partition_key import PartitionKey
from common._test_helpers import ResponseHookCaller
from config.clients import create_data_client
from config.settings import TestSettings, unique_database_id


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestCrossPartitionQuery(unittest.TestCase):
    """Rust-path copy of tests/test_query_cross_partition.py::TestCrossPartitionQuery."""

    created_db: DatabaseProxy = None
    key_db: DatabaseProxy = None
    client: CosmosClient = None
    config = TestSettings
    host = config.host
    masterKey = config.masterKey
    TEST_CONTAINER_ID_PREFIX = "Multi Partition Test Collection With Custom PK "

    @classmethod
    def setUpClass(cls):
        cls.TEST_DATABASE_ID = unique_database_id("query-xp")
        cls.key_client = CosmosClient(cls.host, cls.masterKey, _backend="rust")
        cls.key_db = cls.key_client.create_database(cls.TEST_DATABASE_ID)
        cls.client = create_data_client(_backend="rust")
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.key_client.delete_database(cls.TEST_DATABASE_ID)
        finally:
            cls.client.close()
            cls.key_client.close()

    def setUp(self):
        self.container_id = self.TEST_CONTAINER_ID_PREFIX + str(uuid.uuid4())
        created_container_ref = self.key_db.create_container(
            id=self.container_id,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=TestSettings.THROUGHPUT_FOR_5_PARTITIONS)
        self.created_container = self.created_db.get_container_client(created_container_ref.id)
        # Use key auth for test writes. This avoids flaky failures where a later change feed
        # read can hit a replica that has not finished RBAC propagation for AAD yet.
        self.key_container = self.key_db.get_container_client(created_container_ref.id)

    def tearDown(self):
        try:
            self.key_db.delete_container(self.container_id)
        except exceptions.CosmosHttpResponseError:
            pass

    def test_first_and_last_slashes_trimmed_for_query_string_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_first_and_last_slashes_trimmed_for_query_string
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

    def test_populate_query_metrics_rust(self):
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_populate_query_metrics
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

        # Known gap 36: Query diagnostics and other request options are not sent over Gateway V2 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36).
        pytest.skip("driver-gap: Rust does not send populate_query_metrics over Gateway V2, so the "
                    "query metrics header is missing (known gap 36, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36). The query ran.")
        metrics_header_name = 'x-ms-documentdb-query-metrics'
        self.assertTrue(metrics_header_name in self.created_container.client_connection.last_response_headers)
        metrics_header = self.created_container.client_connection.last_response_headers[metrics_header_name]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        self.assertTrue(len(metrics) > 1)
        self.assertTrue(all(['=' in x for x in metrics]))

    def test_populate_index_metrics_rust(self):
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_populate_index_metrics
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

        # Known gap 36: Query diagnostics and other request options are not sent over Gateway V2 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36).
        pytest.skip("driver-gap: Rust does not send populate_index_metrics over Gateway V2, so the "
                    "index utilization header is missing (known gap 36, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36). The query ran.")
        INDEX_HEADER_NAME = http_constants.HttpHeaders.IndexUtilization
        self.assertTrue(INDEX_HEADER_NAME in self.created_container.client_connection.last_response_headers)
        index_metrics = self.created_container.client_connection.last_response_headers[INDEX_HEADER_NAME]
        self.assertIsNotNone(index_metrics)
        self.assertIn('UtilizedSingleIndexes', index_metrics)
        self.assertIn('PotentialSingleIndexes', index_metrics)
        self.assertIn('UtilizedCompositeIndexes', index_metrics)
        self.assertIn('PotentialCompositeIndexes', index_metrics)

        # Backend index diagnostics can vary by region/build; validate stable signal instead of exact payload.
        candidate_indexes = list(index_metrics.get('UtilizedSingleIndexes', []))
        candidate_indexes.extend(index_metrics.get('PotentialSingleIndexes', []))
        self.assertTrue(any(
            idx.get('FilterExpression') == ''
            and idx.get('IndexImpactScore') == 'High'
            and idx.get('IndexSpec') in ('/pk/?', '/_epk/?')
            for idx in candidate_indexes
        ))

    # Known gap 36: query advice is dropped by the driver's response headers on both transports (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-advice-response-header).
    @pytest.mark.skip(
        reason=(
            "driver-gap: the x-ms-cosmos-query-advice response header never reaches Python, with "
            "Gateway V2 on or off (known gap 36, "
            "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-advice-response-header). "
            "The original skip cites the emulator; the legacy test passes on a live account."
        )
    )
    def test_populate_query_advice_rust(self):
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_populate_query_advice
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {
            'pk': 'pk', 'id': doc_id, 'name': 'test document',
            'tags': [{'name': 'python'}, {'name': 'cosmos'}],
            'timestamp': '2099-01-01T00:00:00Z', 'ticks': 0, 'ts': 0
        }
        self.created_container.create_item(body=document_definition)

        QUERY_ADVICE_HEADER = http_constants.HttpHeaders.QueryAdvice

        # QA1000 - PartialArrayContains: ARRAY_CONTAINS with partial match
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE ARRAY_CONTAINS(c.tags, {"name": "python"}, true)',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1000", query_advice)

        # QA1002 - Contains: CONTAINS usage
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE CONTAINS(c.name, "test")',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1002", query_advice)

        # QA1003 - CaseInsensitiveStartsWithOrStringEquals: case-insensitive STARTSWITH
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE STARTSWITH(c.name, "test", true)',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1003", query_advice)

        # QA1004 - CaseInsensitiveEndsWith: case-insensitive ENDSWITH
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE ENDSWITH(c.name, "document", true)',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1004", query_advice)

        # QA1007 - GetCurrentDateTime: usage of GetCurrentDateTime
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE c.timestamp < GetCurrentDateTime()',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1007", query_advice)

        # QA1008 - GetCurrentTicks: usage of GetCurrentTicks
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE c.ticks < GetCurrentTicks()',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1008", query_advice)

        # QA1009 - GetCurrentTimestamp: usage of GetCurrentTimestamp
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE c.ts < GetCurrentTimestamp()',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1009", query_advice)

    def test_unsupported_queries_rust(self):
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_unsupported_queries
        # Known gap 30 item 9: docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30
        pytest.skip(
            "driver-gap: Rust returns raw per-partition rows for the cross-partition non-VALUE aggregate "
            "'SELECT COUNT(1) FROM c' instead of the legacy 400 rejection (known gap 30 item 9, "
            "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-non-value-aggregate)."
        )
        queries = ['SELECT COUNT(1) FROM c', 'SELECT COUNT(1) + 5 FROM c', 'SELECT COUNT(1) + SUM(c) FROM c']
        for query in queries:
            query_iterable = self.created_container.query_items(query=query, enable_cross_partition_query=True)
            try:
                list(query_iterable)
                self.fail()
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, 400)

    def test_query_with_non_overlapping_pk_ranges_rust(self):
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_query_with_non_overlapping_pk_ranges
        query_iterable = self.created_container.query_items("select * from c where c.pk='1' or c.pk='2'",
                                                            enable_cross_partition_query=True)
        self.assertListEqual(list(query_iterable), [])

    def test_distinct_on_different_types_and_field_orders_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_distinct_on_different_types_and_field_orders
        self.payloads = [
            {'f1': 1, 'f2': 'value', 'f3': 100000000000000000, 'f4': [1, 2, '3'], 'f5': {'f6': {'f7': 2}}},
            {'f2': '\'value', 'f4': [1.0, 2, '3'], 'f5': {'f6': {'f7': 2.0}}, 'f1': 1.0, 'f3': 100000000000000000.00},
            {'f3': 100000000000000000.0, 'f5': {'f6': {'f7': 2}}, 'f2': '\'value', 'f1': 1, 'f4': [1, 2.0, '3']}
        ]
        pytest.skip(
            "internals-only: the original replaces the legacy Python "
            "_QueryExecutionContextBase.__next__ with mocked payloads; Rust query execution never "
            "calls that Python execution context, so the mocked rows cannot reach the results."
        )
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

    def test_paging_with_continuation_token_rust(self):
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_paging_with_continuation_token
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

    def test_cross_partition_query_with_continuation_token_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_cross_partition_query_with_continuation_token
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
        # pylint: disable-next=line-too-long
        # Source helper: tests/test_query_cross_partition.py::TestCrossPartitionQuery._validate_distinct_on_different_types_and_field_orders
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

    def test_value_max_query_rust(self):
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_value_max_query
        query = "Select value max(c.version) FROM c where c.isComplete = true and c.lookupVersion = @lookupVersion"
        query_results = self.created_container.query_items(query, parameters=[
            {"name": "@lookupVersion", "value": "console_csat"}  # cspell:disable-line
        ], enable_cross_partition_query=True)

        # Known gap 30: query_items remaining query, paging, and continuation-token gaps, item 1 aggregates (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-unscoped-max).
        pytest.skip("driver-gap: Rust rejects cross-partition MAX without a partition key with 400/20113 "
                    "(ClientUnsupportedQueryFeature) (known gap 30 item 1, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-unscoped-max).")
        self.assertListEqual(list(query_results), [None])

    def test_continuation_token_size_limit_query_rust(self):
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_continuation_token_size_limit_query
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

    def test_cross_partition_query_response_hook_rust(self):
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_cross_partition_query_response_hook
        created_collection_ref = self.key_db.create_container_if_not_exists(
            id="query_response_hook_test" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=12000
        )
        created_collection = self.created_db.get_container_client(created_collection_ref.id)
        items = [
            {'id': str(uuid.uuid4()), 'pk': '0', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': '1', 'val': 10},
            {'id': str(uuid.uuid4()), 'pk': '0', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': '1', 'val': 10},
            {'id': str(uuid.uuid4()), 'pk': '0', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': '1', 'val': 10}
        ]

        for item in items:
            created_collection.create_item(body=item)

        response_hook = ResponseHookCaller()
        item_list = [item for item in created_collection.query_items("select * from c", enable_cross_partition_query=True, response_hook=response_hook)]
        assert len(item_list) == 6
        assert response_hook.count == 2
        self.key_db.delete_container(created_collection.id)

    def test_cross_partition_query_pagination_with_max_item_count_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_cross_partition_query_pagination_with_max_item_count
        """Test cross-partition pagination showing per-page limits and total results."""
        created_collection_ref = self.key_db.create_container(
            "cross_partition_pagination_test_" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=TestSettings.THROUGHPUT_FOR_5_PARTITIONS)
        created_collection = self.created_db.get_container_client(created_collection_ref.id)
        key_collection = self.key_db.get_container_client(created_collection_ref.id)

        # Create 30 items across 3 different partitions
        total_items = 30
        items_per_partition = 10
        partitions = ["pk_1", "pk_2", "pk_3"]

        for pk in partitions:
            for i in range(items_per_partition):
                document_definition = {
                    'pk': pk,
                    'id': f'{pk}_item_{i}',
                    'value': i
                }
                key_collection.create_item(body=document_definition)

        # Test cross-partition query with max_item_count
        max_items_per_page = 8
        query = "SELECT * FROM c ORDER BY c['value']"
        # Iterate through pages and verify per-page counts
        all_fetched_results = []
        page_count = 0
        query_iterable = created_collection.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=max_items_per_page,
        )
        item_pages = query_iterable.by_page()

        for page in item_pages:
            items_in_page = list(page)
            page_count += 1
            all_fetched_results.extend(items_in_page)

            # Each page should have at most max_item_count items
            # In cross-partition queries, pages may have fewer items
            self.assertLessEqual(len(items_in_page), max_items_per_page)
            self.assertGreater(len(items_in_page), 0)  # Pages should not be empty

        # Verify total results match expected count
        self.assertEqual(len(all_fetched_results), total_items)

        # Verify we got multiple pages
        self.assertGreater(page_count, 1)

        self.key_db.delete_container(created_collection.id)

    # TODO: migrate to AAD once service-side RBAC activation window (403/5302) fix ships.
    @pytest.mark.skipif(
        TestSettings.data_auth_mode == 'aad',
        reason="environment-gap: post-create RBAC activation window (403/5302)  -  migrate after service-side fix",
    )
    def test_cross_partition_query_pagination_counting_results_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition.py::TestCrossPartitionQuery.test_cross_partition_query_pagination_counting_results
        """Test counting total results while paginating across partitions."""
        created_collection_ref = self.key_db.create_container(
            "cross_partition_count_test_" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=TestSettings.THROUGHPUT_FOR_5_PARTITIONS)
        created_collection = self.created_db.get_container_client(created_collection_ref.id)
        key_collection = self.key_db.get_container_client(created_collection_ref.id)

        # Create items across multiple partitions with different counts
        partitions_config = [
            ("partition_a", 5),
            ("partition_b", 8),
            ("partition_c", 3),
            ("partition_d", 12)
        ]

        total_expected = 0
        for pk, count in partitions_config:
            for i in range(count):
                document_definition = {
                    'pk': pk,
                    'id': f'{pk}_item_{i}',
                    'name': f'Item {i} in {pk}'
                }
                key_collection.create_item(body=document_definition)
                total_expected += 1

        # Query across partitions with pagination
        max_items_per_page = 5
        query = "SELECT * FROM c"
        # Count items across all pages
        total_count = 0
        page_count = 0
        page_sizes = []

        query_iterable = created_collection.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=max_items_per_page,
        )
        item_pages = query_iterable.by_page()
        for page in item_pages:
            items = list(page)
            page_count += 1
            page_size = len(items)
            page_sizes.append(page_size)
            total_count += page_size

            # Verify page size constraints
            self.assertLessEqual(page_size, max_items_per_page)
            self.assertGreater(page_size, 0)

        # Verify total count matches what we inserted
        self.assertEqual(total_count, total_expected)

        # Verify we processed multiple pages
        self.assertGreater(page_count, 1)

        self.key_db.delete_container(created_collection.id)

    def _MockNextFunction(self):
        # Source helper: tests/test_query_cross_partition.py::TestCrossPartitionQuery._MockNextFunction
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
