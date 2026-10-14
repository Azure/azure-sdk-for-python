# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Copied sync query tests against the ``_backend="rust"`` path.

Self-contained: builds its own database + container in ``setUp`` and
registers cleanup immediately. The class name and method names match the
source at ``tests/test_query.py`` so test IDs differ only by path.
The None-parameters, ordered-paging, OFFSET LIMIT, and COUNT tests reuse the
owned container; their query inputs and assertions are unchanged.
DISTINCT retains its original composite indexes in a separate owned container.

Run with::

    pytest --noconftest tests/query_items/sync/legacy/test_query.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, http_constants
from query_items._legacy_distinct_helpers import DistinctConfig


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
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

    def test_query_items_with_parameters_none(self):
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

    def test_query_pagination_with_max_item_count(self):
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

    def test_offset_limit(self):
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

    def test_distinct(self):
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

    def test_partition_scoped_count_is_index_only(self):
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

    def test_paging_with_continuation_token(self):
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
        self.container.create_item({"pk": "pk", "id": "1"})
        self.container.create_item({"pk": "pk", "id": "2"})

        query_iterable = self.container.query_items(
            query="SELECT * from c",
            partition_key="pk",
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        pager.next()
        token = pager.continuation_token
        second_page = list(pager.next())[0]

        replay_pager = query_iterable.by_page(token)
        replay_second_page = list(replay_pager.next())[0]
        self.assertEqual(second_page["id"], replay_second_page["id"])

    def test_cross_partition_query_with_continuation_token(self):
        """Original cross-partition continuation replay, using this test's isolated container."""
        # Source: tests/test_query.py::TestQuery.test_cross_partition_query_with_continuation_token
        created_collection = self.container
        created_collection.create_item(body={"pk": "pk1", "id": str(uuid.uuid4())})
        created_collection.create_item(body={"pk": "pk2", "id": str(uuid.uuid4())})

        query_iterable = created_collection.query_items(
            query="SELECT * from c",
            enable_cross_partition_query=True,
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        pager.next()
        token = pager.continuation_token
        second_page = list(pager.next())[0]

        pager = query_iterable.by_page(token)
        second_page_fetched_with_continuation_token = list(pager.next())[0]
        self.assertEqual(second_page["id"], second_page_fetched_with_continuation_token["id"])
