# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Copied sync query tests against the ``_backend="rust"`` path.

Self-contained: builds its own database + container in ``setUp`` and
registers cleanup immediately. The class name and method names match the
source (apart from the method's ``_rust`` suffix) at ``tests/test_query.py`` so test IDs
differ by path and method suffix.
The positional-argument, None-parameters, ordered-paging, OFFSET LIMIT, COUNT, MAX, and query/index-metrics tests reuse the
owned container; their query inputs and assertions are unchanged.
DISTINCT retains its original composite indexes in a separate owned container.
Query advice retains the original unconditional emulator-related skip.
The remaining copies create owned containers in the same database; the shared
multi-partition container becomes an owned ``/pk`` container with 11000 RU.
Tests that patch legacy Python internals (retry utility, execution context,
pipeline run function) skip with ``internals-only`` where the internal is used.

Run with::

    pytest --noconftest tests/query_items/sync/test_query.py -v
"""
import os
import unittest
import uuid
from unittest.mock import patch

import pytest

import azure.cosmos._retry_utility as retry_utility
import azure.cosmos.exceptions as exceptions
from azure.cosmos import (
    CosmosClient, PartitionKey, http_constants, _endpoint_discovery_retry_policy, _synchronized_request,
)
from azure.cosmos._execution_context.base_execution_context import _QueryExecutionContextBase
from azure.cosmos._routing.feed_range_continuation import _decode_token
from query_items._legacy_distinct_helpers import DistinctConfig, distinct_query_diagnostics
from query_items._legacy_feed_range_helpers import create_feed_range_in_dict, create_range


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


class TestQuery(unittest.TestCase):
    config = DistinctConfig

    def setUp(self) -> None:
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self.addCleanup(self.client.close)
        self._db_id = "legacy_query_paging_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = self.client.create_database(self._db_id)
        self.addCleanup(self._delete_owned_database)
        print(f"\nOwned query database: {self._db_id}")
        self.container = self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )

    def _delete_owned_database(self) -> None:
        self.client.delete_database(self._db_id)
        print(f"\nDeleted owned query database: {self._db_id}")

    @pytest.mark.cosmosEmulator
    def test_populate_query_metrics_rust(self):
        # Source: tests/test_query.py::TestQuery.test_populate_query_metrics
        created_collection = self.container
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

        # Known gap 36: Query diagnostics and other request options are not sent over Gateway V2 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36).
        pytest.skip("driver-gap: Rust does not send populate_query_metrics over Gateway V2, so the "
                    "metrics header is missing (known gap 36, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36). The query ran.")
        METRICS_HEADER_NAME = 'x-ms-documentdb-query-metrics'
        self.assertTrue(METRICS_HEADER_NAME in created_collection.client_connection.last_response_headers)
        metrics_header = created_collection.client_connection.last_response_headers[METRICS_HEADER_NAME]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        self.assertTrue(len(metrics) > 1)
        self.assertTrue(all(['=' in x for x in metrics]))
        self.database.delete_container(created_collection.id)

    @pytest.mark.cosmosEmulator
    def test_populate_index_metrics_rust(self):
        # Source: tests/test_query.py::TestQuery.test_populate_index_metrics
        created_collection = self.container

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

        # Known gap 36: Query diagnostics and other request options are not sent over Gateway V2 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36).
        pytest.skip("driver-gap: Rust does not send populate_index_metrics over Gateway V2, so the "
                    "index-utilization header is missing (known gap 36, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36). The query ran.")
        INDEX_HEADER_NAME = http_constants.HttpHeaders.IndexUtilization
        self.assertTrue(INDEX_HEADER_NAME in created_collection.client_connection.last_response_headers)
        index_metrics = created_collection.client_connection.last_response_headers[INDEX_HEADER_NAME]
        self.assertIsNotNone(index_metrics)
        self.assertIn('UtilizedSingleIndexes', index_metrics)
        self.assertIn('PotentialSingleIndexes', index_metrics)
        self.assertIn('UtilizedCompositeIndexes', index_metrics)
        self.assertIn('PotentialCompositeIndexes', index_metrics)

        # Backend index diagnostics can vary by region/build; validate a stable shape and key signal.
        candidate_indexes = list(index_metrics.get('UtilizedSingleIndexes', []))
        candidate_indexes.extend(index_metrics.get('PotentialSingleIndexes', []))
        self.assertTrue(any(
            idx.get('FilterExpression') == ''
            and idx.get('IndexImpactScore') == 'High'
            and idx.get('IndexSpec') in ('/pk/?', '/_epk/?')
            for idx in candidate_indexes
        ))
        self.database.delete_container(created_collection.id)

    @pytest.mark.cosmosEmulator
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
        # Source: tests/test_query.py::TestQuery.test_populate_query_advice
        created_collection = self.container

        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {
            'pk': 'pk', 'id': doc_id, 'name': 'test document',
            'tags': [{'name': 'python'}, {'name': 'cosmos'}],
            'timestamp': '2099-01-01T00:00:00Z', 'ticks': 0, 'ts': 0
        }
        created_collection.create_item(body=document_definition)

        QUERY_ADVICE_HEADER = http_constants.HttpHeaders.QueryAdvice

        # QA1000 - PartialArrayContains: ARRAY_CONTAINS with partial match
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE ARRAY_CONTAINS(c.tags, {"name": "python"}, true)',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1000", query_advice)

        # QA1002 - Contains: CONTAINS usage
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE CONTAINS(c.name, "test")',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1002", query_advice)

        # QA1003 - CaseInsensitiveStartsWithOrStringEquals: case-insensitive STARTSWITH
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE STARTSWITH(c.name, "test", true)',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1003", query_advice)

        # QA1004 - CaseInsensitiveEndsWith: case-insensitive ENDSWITH
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE ENDSWITH(c.name, "document", true)',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1004", query_advice)

        # QA1007 - GetCurrentDateTime: usage of GetCurrentDateTime
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE c.timestamp < GetCurrentDateTime()',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1007", query_advice)

        # QA1008 - GetCurrentTicks: usage of GetCurrentTicks
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE c.ticks < GetCurrentTicks()',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1008", query_advice)

        # QA1009 - GetCurrentTimestamp: usage of GetCurrentTimestamp
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE c.ts < GetCurrentTimestamp()',
            partition_key='pk', populate_query_advice=True
        )
        list(query_iterable)
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        self.assertIsNotNone(query_advice)
        self.assertIn("QA1009", query_advice)
        self.database.delete_container(created_collection.id)

    @pytest.mark.cosmosEmulator
    @pytest.mark.skip(
        reason="driver-gap: Gap 30 - Rust rejects MAX queries without a partition key "
        "(HTTP 400/1004). Re-enable when the driver supports this aggregate query."
    )
    def test_value_max_query_results_rust(self):
        # Source: tests/test_query.py::TestQuery.test_value_max_query_results
        container = self.container
        container.upsert_item(
            {"id": str(uuid.uuid4()), "isComplete": True, "version": 3, "lookupVersion": "console_version"})
        container.upsert_item(
            {"id": str(uuid.uuid4()), "isComplete": True, "version": 2, "lookupVersion": "console_version"})
        query = "Select value max(c.version) FROM c where c.isComplete = true and c.lookupVersion = @lookupVersion"
        query_results = container.query_items(query, parameters=[
            {"name": "@lookupVersion", "value": "console_version"}  # cspell:disable-line
        ], enable_cross_partition_query=True)
        item_list = list(query_results)
        assert len(item_list) == 1
        assert item_list[0] == 3

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_query_positional_args_rust(self):
        # Source: tests/test_query.py::TestQuery.test_query_positional_args
        container = self.container
        partition_key_value1 = "pk1"
        partition_key_value2 = "pk2"

        num_items = 10
        new_items = []
        for pk_value in [partition_key_value1, partition_key_value2]:
            for i in range(num_items):
                item = {
                    'pk': pk_value,
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

    @pytest.mark.cosmosEmulator
    def test_query_items_with_parameters_none_rust(self):
        """Test that query_items handles parameters=None correctly (issue #43662)."""
        # Source: tests/test_query.py::TestQuery.test_query_items_with_parameters_none
        created_collection = self.container

        # Create test documents
        doc1_id = 'doc1_' + str(uuid.uuid4())
        doc2_id = 'doc2_' + str(uuid.uuid4())
        created_collection.create_item(body={'pk': 'pk1', 'id': doc1_id, 'value1': 1})
        created_collection.create_item(body={'pk': 'pk2', 'id': doc2_id, 'value1': 2})

        # Test 1: Explicitly passing parameters=None should not cause TypeError
        query = 'SELECT * FROM c'
        query_iterable = created_collection.query_items(
            query=query,
            parameters=None,
            enable_cross_partition_query=True
        )
        results = list(query_iterable)
        self.assertEqual(len(results), 2)

        # Test 2: parameters=None with partition_key should work
        query_iterable = created_collection.query_items(
            query=query,
            parameters=None,
            partition_key='pk1'
        )
        results = list(query_iterable)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], doc1_id)

        # Test 3: Verify parameterized query still works with actual parameters
        query_with_params = 'SELECT * FROM c WHERE c.value1 = @value'
        query_iterable = created_collection.query_items(
            query=query_with_params,
            parameters=[{'name': '@value', 'value': 2}],
            enable_cross_partition_query=True
        )
        results = list(query_iterable)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], doc2_id)

        # Test 4: Query without parameters argument should work (default behavior)
        query_iterable = created_collection.query_items(
            query=query,
            enable_cross_partition_query=True
        )
        results = list(query_iterable)
        self.assertEqual(len(results), 2)

        self.database.delete_container(created_collection.id)

    @pytest.mark.cosmosEmulator
    def test_query_pagination_with_max_item_count_rust(self):
        """Test pagination showing per-page limits and total results counting."""
        # Source: tests/test_query.py::TestQuery.test_query_pagination_with_max_item_count
        created_collection = self.container

        # Create 20 items in a single partition
        total_items = 20
        partition_key_value = "test_pk"
        for i in range(total_items):
            document_definition = {
                'pk': partition_key_value,
                'id': f'item_{i}',
                'value': i
            }
            created_collection.create_item(body=document_definition)

        # Test pagination with max_item_count limiting items per page
        max_items_per_page = 7
        query = "SELECT * FROM c WHERE c.pk = @pk ORDER BY c['value']"
        query_iterable = created_collection.query_items(
            query=query,
            parameters=[{"name": "@pk", "value": partition_key_value}],
            partition_key=partition_key_value,
            max_item_count=max_items_per_page
        )

        # Iterate through pages and verify per-page counts
        all_fetched_results = []
        page_count = 0
        item_pages = query_iterable.by_page()

        for page in item_pages:
            page_count += 1
            items_in_page = list(page)
            all_fetched_results.extend(items_in_page)

            # Each page should have at most max_item_count items
            # (last page may have fewer)
            self.assertLessEqual(len(items_in_page), max_items_per_page)

        # Verify total results match expected count
        self.assertEqual(len(all_fetched_results), total_items)

        # Verify we got the expected number of pages
        # 20 items with max 7 per page = 3 pages (7, 7, 6)
        self.assertEqual(page_count, 3)

        # Verify ordering is maintained
        for i, item in enumerate(all_fetched_results):
            self.assertEqual(item['value'], i)

        self.database.delete_container(created_collection.id)

    @pytest.mark.cosmosEmulator
    @pytest.mark.skip(
        reason="driver-gap: Gap 30 - For SELECT DISTINCT c[\"value\"] with ORDER BY and "
        "OFFSET LIMIT, Rust returns rows with a '$1' field instead of the requested "
        "'value' field, so the unchanged test raises KeyError. Re-enable when the "
        "driver preserves the selected property name."
    )
    def test_offset_limit_rust(self):
        # Source: tests/test_query.py::TestQuery.test_offset_limit
        created_collection = self.container
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
        self.database.delete_container(created_collection.id)

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

    @pytest.mark.cosmosEmulator
    def test_distinct_rust(self):
        # Source: tests/test_query.py::TestQuery.test_distinct
        distinct_field = 'distinct_field'
        pk_field = "pk"
        different_field = "different_field"

        created_collection = self.database.create_container(
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

        # Known gap 30: query_items() remaining query, paging, and continuation-token gaps, item 2 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30).
        pytest.skip("driver-gap: Rust rejects cross-partition unordered DISTINCT without TOP or LIMIT "
                    "(400/20125 ClientBufferedQueryRequiresFiniteWindow) (known gap 30 item 2, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30). The documents were created.")
        self._validate_distinct(created_collection=created_collection,
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

        self.database.delete_container(created_collection.id)

    def _validate_distinct(self, created_collection, query, results, is_select, fields):
        with distinct_query_diagnostics(query):
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

    @pytest.mark.cosmosEmulator
    def test_partition_scoped_count_is_index_only_rust(self):
        # Source: tests/test_query.py::TestQuery.test_partition_scoped_count_is_index_only
        created_collection = self.container
        partition_key = "PowerCut-" + str(uuid.uuid4())
        other_partition_key = "Other-" + str(uuid.uuid4())
        created_items = []
        try:
            for i in range(25):
                item = created_collection.create_item({
                    "id": f"power-cut-{i}-{uuid.uuid4()}",
                    "pk": partition_key,
                    "value": i,
                })
                created_items.append((item["id"], item["pk"]))
            item = created_collection.create_item({
                "id": "other-document-type-" + str(uuid.uuid4()),
                "pk": other_partition_key,
            })
            created_items.append((item["id"], item["pk"]))

            query_iterable = created_collection.query_items(
                query="SELECT VALUE COUNT(1) FROM c",
                partition_key=partition_key,
                enable_cross_partition_query=False,
                populate_query_metrics=True,
            )
            pager = query_iterable.by_page()
            pages = [list(page) for page in pager]

            self.assertEqual([[25]], pages)
            self.assertIsNone(pager.continuation_token)

            # Known gap 36: Query diagnostics and other request options are not sent over Gateway V2 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36).
            pytest.skip("driver-gap: Rust does not send populate_query_metrics over Gateway V2, so the "
                        "metrics header is missing (known gap 36, "
                        "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36). The COUNT query ran.")
            response_headers = query_iterable.get_response_headers()
            metrics_header = response_headers[http_constants.HttpHeaders.QueryMetrics]
            metrics = dict(
                entry.split("=", 1)
                for entry in metrics_header.split(";")
                if entry
            )
            self.assertEqual(0, int(metrics["retrievedDocumentCount"]))
            self.assertEqual(0, int(metrics["retrievedDocumentSize"]))
            self.assertEqual(1.0, float(metrics["indexUtilizationRatio"]))
            self.assertLess(float(response_headers[http_constants.HttpHeaders.RequestCharge]), 20.0)
        finally:
            for item_id, item_partition_key in created_items:
                created_collection.delete_item(item_id, item_partition_key)

    @pytest.mark.cosmosEmulator
    def test_paging_with_continuation_token_rust(self):
        """A continuation token replays the page that follows it.

        Two items are queried one page at a time. After taking the first page,
        the token is saved and the second page is read normally. A fresh page
        iterator resumed from that token must then return the same second page.

        This is the promise behind every saved token: a customer who stores one
        and comes back later gets the next page, not a repeat of what they
        already have and not a gap. Run against a real account so the token is
        a genuine one from the service rather than a fake.
        """
        # Source: tests/test_query.py::TestQuery.test_paging_with_continuation_token
        created_collection = self.container

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

    @pytest.mark.cosmosEmulator
    def test_continuation_token_size_limit_query_rust(self):
        """Preserve the original one-kilobyte token assertions on owned data."""
        # Source: tests/test_query.py::TestQuery.test_continuation_token_size_limit_query
        container = self.container
        for i in range(1, 1000):
            container.create_item(body=dict(pk='123', id=str(uuid.uuid4()), some_value=str(i % 3)))
        query = "Select * from c where c.some_value='2'"
        response_query = container.query_items(query, partition_key='123', max_item_count=100,
                                               continuation_token_limit=1)
        pager = response_query.by_page()
        pager.next()
        token = pager.continuation_token
        self.assertLessEqual(len(token.encode('utf-8')), 1024)
        pager.next()
        token = pager.continuation_token
        self.assertLessEqual(len(token.encode('utf-8')), 1024)

    @pytest.mark.cosmosEmulator
    def test_continuation_token_limit_preserves_broad_scope_and_resume_rust(self):
        """Forward the service limit without imposing a size cap on the SDK token."""
        container = self._create_multi_partition_container()
        self.assertGreater(len(list(container.read_feed_ranges())), 1)
        expected = {f"token-limit-{i}" for i in range(7)}
        for i in range(7):
            container.create_item({"id": f"token-limit-{i}", "pk": f"customer-{i % 3}"})
        full_range = {
            "Range": {
                "min": "",
                "max": "FF",
                "isMinInclusive": True,
                "isMaxInclusive": False,
            }
        }
        for scope in ({}, {"feed_range": full_range}):
            with self.subTest(scope=scope):
                options = dict(
                    query="SELECT * FROM c",
                    max_item_count=1,
                    continuation_token_limit=1,
                    enable_cross_partition_query=True,
                    **scope,
                )
                pages = container.query_items(**options).by_page()
                first = list(next(pages))
                token = pages.continuation_token
                self.assertTrue(first)
                self.assertTrue(token)
                resumed = container.query_items(**options).by_page(
                    continuation_token=token
                )
                rows = first + [row for page in resumed for row in page]
                self.assertEqual(len(rows), len(expected))
                self.assertEqual({row["id"] for row in rows}, expected)

    @pytest.mark.cosmosEmulator
    def test_cross_partition_query_with_continuation_token_rust(self):
        """Original cross-partition continuation replay, using this test's isolated container."""
        # Source: tests/test_query.py::TestQuery.test_cross_partition_query_with_continuation_token
        created_collection = self.container
        document_definition = {'pk': 'pk1', 'id': str(uuid.uuid4())}
        created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk2', 'id': str(uuid.uuid4())}
        created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        pager.next()
        token = pager.continuation_token
        second_page = list(pager.next())[0]

        pager = query_iterable.by_page(token)
        second_page_fetched_with_continuation_token = list(pager.next())[0]
        self.assertEqual(second_page['id'], second_page_fetched_with_continuation_token['id'])

    # Copies below use owned containers in this test's database. The shared
    # TEST_MULTI_PARTITION_CONTAINER_ID (``/pk``) becomes an owned ``/pk``
    # container with 11000 RU so it still spans more than one physical partition.

    def _create_container_for_test(self, *args, **kwargs):
        # Source helper: tests/test_query.py::TestQuery._create_container_for_test
        return self.database.create_container(*args, **kwargs)

    def _delete_container_for_test(self, *args, **kwargs):
        # Source helper: tests/test_query.py::TestQuery._delete_container_for_test
        return self.database.delete_container(*args, **kwargs)

    def _create_multi_partition_container(self):
        return self.database.create_container(
            "multi_partition_" + uuid.uuid4().hex[:8], PartitionKey(path="/pk"), offer_throughput=11000)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_first_and_last_slashes_trimmed_for_query_string_rust(self):
        # Source: tests/test_query.py::TestQuery.test_first_and_last_slashes_trimmed_for_query_string
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

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    @pytest.mark.skip(reason="internals-only: the original is unconditionally skipped and counts requests by "
                             "patching legacy retry_utility.ExecuteFunction, which Rust never calls.")
    def test_max_item_count_honored_in_order_by_query_rust(self):
        # Source: tests/test_query.py::TestQuery.test_max_item_count_honored_in_order_by_query
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
        # Source helper: tests/test_query.py::TestQuery.validate_query_requests_count
        self.count = 0
        self.OriginalExecuteFunction = retry_utility.ExecuteFunction
        retry_utility.ExecuteFunction = self._MockExecuteFunction
        for block in query_iterable.by_page():
            assert len(list(block)) != 0
        retry_utility.ExecuteFunction = self.OriginalExecuteFunction
        self.assertEqual(self.count, expected_count)
        self.count = 0

    def _MockExecuteFunction(self, function, *args, **kwargs):
        # Source helper: tests/test_query.py::TestQuery._MockExecuteFunction
        self.count += 1
        return self.OriginalExecuteFunction(function, *args, **kwargs)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_unsupported_queries_rust(self):
        # Source: tests/test_query.py::TestQuery.test_unsupported_queries
        # Known gap 30 item 9: docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30
        pytest.skip(
            "driver-gap: Rust returns raw per-partition rows for the cross-partition non-VALUE aggregate "
            "'SELECT COUNT(1) FROM c' instead of the legacy 400 rejection (known gap 30 item 9, "
            "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-non-value-aggregate)."
        )
        created_collection = self._create_multi_partition_container()
        queries = ['SELECT COUNT(1) FROM c', 'SELECT COUNT(1) + 5 FROM c', 'SELECT COUNT(1) + SUM(c) FROM c']
        for query in queries:
            query_iterable = created_collection.query_items(query=query, enable_cross_partition_query=True)
            try:
                list(query_iterable)
                self.fail()
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, 400)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_query_with_non_overlapping_pk_ranges_rust(self):
        # Source: tests/test_query.py::TestQuery.test_query_with_non_overlapping_pk_ranges
        created_collection = self._create_multi_partition_container()
        query_iterable = created_collection.query_items("select * from c where c.pk='1' or c.pk='2'",
                                                        enable_cross_partition_query=True)
        self.assertListEqual(list(query_iterable), [])

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_distinct_on_different_types_and_field_orders_rust(self):
        # Source: tests/test_query.py::TestQuery.test_distinct_on_different_types_and_field_orders
        created_collection = self._create_container_for_test(
            id="test-distinct-container-" + str(uuid.uuid4()),
            partition_key=PartitionKey("/pk"),
            offer_throughput=11000)
        self.payloads = [
            {'f1': 1, 'f2': 'value', 'f3': 100000000000000000, 'f4': [1, 2, '3'], 'f5': {'f6': {'f7': 2}}},
            {'f2': '\'value', 'f4': [1.0, 2, '3'], 'f5': {'f6': {'f7': 2.0}}, 'f1': 1.0, 'f3': 100000000000000000.00},
            {'f3': 100000000000000000.0, 'f5': {'f6': {'f7': 2}}, 'f2': '\'value', 'f1': 1, 'f4': [1, 2.0, '3']}
        ]
        pytest.skip("internals-only: the results come from patching legacy "
                    "_QueryExecutionContextBase.__next__ with canned payloads; Rust query execution "
                    "never calls it, so no Rust behavior would be tested.")
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

    def _validate_distinct_on_different_types_and_field_orders(self, collection, query, expected_results,
                                                               get_mock_result):
        # Source helper: tests/test_query.py::TestQuery._validate_distinct_on_different_types_and_field_orders
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

    def _MockNextFunction(self):
        # Source helper: tests/test_query.py::TestQuery._MockNextFunction
        if self.count < len(self.payloads):
            item, result = self.get_mock_result(self.payloads, self.count)
            self.count += 1
            if item is not None:
                return {'orderByItems': [{'item': item}], '_rid': 'fake_rid', 'payload': result}
            else:
                return result
        else:
            raise StopIteration

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_full_pk_continuation_emits_legacy_by_default_rust(self):
        # Source: tests/test_query.py::TestQuery.test_full_pk_continuation_emits_legacy_by_default
        created_collection = self._create_multi_partition_container()
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

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_full_pk_legacy_replay_resumes_same_page_rust(self):
        # Source: tests/test_query.py::TestQuery.test_full_pk_legacy_replay_resumes_same_page
        created_collection = self._create_multi_partition_container()
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

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_cross_partition_query_with_none_partition_key_rust(self):
        # Source: tests/test_query.py::TestQuery.test_cross_partition_query_with_none_partition_key
        created_collection = self._create_multi_partition_container()
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

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_value_max_query_rust(self):
        # Source: tests/test_query.py::TestQuery.test_value_max_query
        container = self._create_multi_partition_container()
        query = "Select value max(c.version) FROM c where c.isComplete = true and c.lookupVersion = @lookupVersion"
        query_results = container.query_items(query, parameters=[
            {"name": "@lookupVersion", "value": "console_csat"}  # cspell:disable-line
        ], enable_cross_partition_query=True)

        # Known gap 30: query_items remaining query, paging, and continuation-token gaps, item 1 aggregates (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-unscoped-max).
        pytest.skip("driver-gap: Rust rejects cross-partition VALUE MAX with 400/20113 "
                    "(ClientUnsupportedQueryFeature) (known gap 30 item 1, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-unscoped-max). The query was built.")
        self.assertListEqual(list(query_results), [None])

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_query_request_params_none_retry_policy_rust(self):
        # Source: tests/test_query.py::TestQuery.test_query_request_params_none_retry_policy
        created_collection = self._create_container_for_test(
            "query_request_params_none_retry_policy_" + str(uuid.uuid4()), PartitionKey(path="/pk"))
        items = [
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5}]

        for item in items:
            created_collection.create_item(body=item)

        # Known gap 11: Closed: driver-owned throttle retry waiting (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-11). Retry policies are owned by the Rust driver.
        pytest.skip("internals-only: the errors are injected by patching legacy retry_utility.ExecuteFunction "
                    "and the legacy endpoint-discovery retry policy; Rust never calls them and owns its retries "
                    "(known gap 11). The items were created.")
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

    def _MockExecuteFunctionSessionRetry(self, function, *args, **kwargs):
        # Source helper: tests/test_query.py::TestQuery._MockExecuteFunctionSessionRetry
        if args:
            if args[1].operation_type == 'SqlQuery':
                ex_to_raise = exceptions.CosmosHttpResponseError(status_code=http_constants.StatusCodes.NOT_FOUND,
                                                                 message="Read Session is Not Available")
                ex_to_raise.sub_status = http_constants.SubStatusCodes.READ_SESSION_NOTAVAILABLE
                raise ex_to_raise
        return self.OriginalExecuteFunction(function, *args, **kwargs)

    def _MockExecuteFunctionEndPointRetry(self, function, *args, **kwargs):
        # Source helper: tests/test_query.py::TestQuery._MockExecuteFunctionEndPointRetry
        if args:
            if args[1].operation_type == 'SqlQuery':
                ex_to_raise = exceptions.CosmosHttpResponseError(status_code=http_constants.StatusCodes.FORBIDDEN,
                                                                 message="End Point Discovery")
                ex_to_raise.sub_status = http_constants.SubStatusCodes.WRITE_FORBIDDEN
                raise ex_to_raise
        return self.OriginalExecuteFunction(function, *args, **kwargs)

    def _MockExecuteFunctionTimeoutFailoverRetry(self, function, *args, **kwargs):
        # Source helper: tests/test_query.py::TestQuery._MockExecuteFunctionTimeoutFailoverRetry
        if args:
            if args[1].operation_type == 'SqlQuery':
                ex_to_raise = exceptions.CosmosHttpResponseError(status_code=http_constants.StatusCodes.REQUEST_TIMEOUT,
                                                                 message="Timeout Failover")
                raise ex_to_raise
        return self.OriginalExecuteFunction(function, *args, **kwargs)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_query_pagination_without_max_item_count_rust(self):
        """Test pagination behavior without specifying max_item_count."""
        # Source: tests/test_query.py::TestQuery.test_query_pagination_without_max_item_count
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

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_query_items_parameters_none_with_options_rust(self):
        """Test parameters=None works with various query options."""
        # Source: tests/test_query.py::TestQuery.test_query_items_parameters_none_with_options
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

        # Known gap 36: Query diagnostics and other request options are not sent over Gateway V2 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36).
        pytest.skip("driver-gap: Rust does not send populate_query_metrics over Gateway V2, so the "
                    "metrics header is missing (known gap 36, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36). Paging and the query ran.")
        # Verify query metrics were populated
        metrics_header_name = 'x-ms-documentdb-query-metrics'
        self.assertTrue(metrics_header_name in created_collection.client_connection.last_response_headers)

        self._delete_container_for_test(created_collection.id)

    def _capture_pipeline_kwarg(self, kwarg_name):
        # Source helper: tests/test_query.py::TestQuery._capture_pipeline_kwarg
        captured = []
        original = _synchronized_request._PipelineRunFunction

        def _wrapper(pipeline_client, request, **kwargs):
            captured.append((str(request.url), kwargs.get(kwarg_name)))
            return original(pipeline_client, request, **kwargs)

        return captured, patch.object(
            _synchronized_request, "_PipelineRunFunction", side_effect=_wrapper,
        )

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_outer_timeout_propagates_through_by_page_paging_rust(self):
        # Source: tests/test_query.py::TestQuery.test_outer_timeout_propagates_through_by_page_paging
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
            # Known gap 5: Closed: runtime and operation timeout scopes (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-5). The driver applies the operation budget; Rust never calls legacy _synchronized_request.
            pytest.skip("internals-only: per-request timeout values were captured by patching legacy "
                        "_synchronized_request._PipelineRunFunction, which Rust never calls; the driver owns "
                        "the operation budget (known gap 5). The paged query with timeout ran.")
            doc_values = [t for (url, t) in captured if "/docs" in url]
            self.assertGreater(len(doc_values), 0)
            non_none = [t for t in doc_values if t is not None]
            self.assertGreater(len(non_none), 0)
            for t in non_none:
                self.assertLessEqual(t, outer_timeout)
        finally:
            self._delete_container_for_test(container.id)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_connection_timeout_propagates_through_by_page_paging_rust(self):
        # Source: tests/test_query.py::TestQuery.test_connection_timeout_propagates_through_by_page_paging
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
            # Known gap 5: Closed: runtime and operation timeout scopes (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-5). Rust-served operations reject per-call connection_timeout.
            pytest.skip("accepted-vnext-change: Rust query_items rejects per-call connection_timeout with "
                        "NotImplementedError; connection limits belong to the runtime (known gap 5, "
                        "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-5). The items were created.")
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

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    def test_avg_aggregate_by_page_raises_value_error_cross_partition_rust(self):
        # Source: tests/test_query.py::TestQuery.test_avg_aggregate_by_page_raises_value_error_cross_partition
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
            full_range = create_range(
                range_min="",
                range_max="FF",
                is_min_inclusive=True,
                is_max_inclusive=False,
            )
            feed_range = create_feed_range_in_dict(full_range)

            # Known gap 30: query_items remaining query, paging, and continuation-token gaps, item 1 aggregates (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-full-range-sum).
            pytest.skip("driver-gap: Rust rejects full-range aggregates with 400/20113 "
                        "(ClientUnsupportedQueryFeature) instead of the legacy AVG ValueError (known gap 30 item 1, "
                        "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-full-range-sum). The items were created.")
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
