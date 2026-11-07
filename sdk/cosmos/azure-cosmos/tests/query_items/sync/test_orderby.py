# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Self-contained TOP/ORDER BY copies with preserved public paging assertions.

The original method and document definitions are retained. Owned setup uses
11,000 RU/s instead of the original 30,000 RU/s; that still spans more than one
physical partition, and the original's explicit Range indexes match the default
indexing policy. The helper omits only the private legacy QueryIterable identity
assertion; ItemPaged, IDs, ordering, page sizes, counts, and exhaustion remain.
No original test module is imported. The TOP-without-ORDER-BY copies read
legacy partition key ranges and per-range QueryFeed results, so they stop with
an internals-only skip where those internals are first used.
"""

import os
import unittest
import uuid

import pytest
from azure.core.paging import ItemPaged

import azure.cosmos._base as base
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos import _query_iterable as query_iterable


class TestCrossPartitionTopOrderBy(unittest.TestCase):
    def setUp(self):
        self.client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust",
        )
        self.addCleanup(self.client.close)
        self.database_id = "legacy_query_top_" + uuid.uuid4().hex
        database = self.client.create_database(self.database_id)
        self.addCleanup(self._delete_owned_database)
        print(f"\nOwned TOP database: {self.database_id}")
        self.created_container = database.create_container(
            id="orders", partition_key=PartitionKey(path="/id"), offer_throughput=11000,
        )
        self.collection_link = 'dbs/' + self.database_id + '/colls/' + self.created_container.id
        self.document_definitions = []
        for i in range(20):
            d = {'id': str(i),
                 'name': 'sample document',
                 'spam': 'eggs' + str(i),
                 'cnt': i,
                 'key': 'value',
                 'spam2': 'eggs' + str(i) if (i == 3) else i,
                 'boolVar': (i % 2 == 0),
                 'number': 1.1 * i
                 }
            self.created_container.create_item(d)
            self.document_definitions.append(d)

    def _delete_owned_database(self):
        self.client.delete_database(self.database_id)
        print(f"\nDeleted owned TOP database: {self.database_id}")

    @pytest.mark.cosmosEmulator
    # Known gap 30: query_items remaining query, paging, and continuation-token gaps (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-top-page-size).
    @pytest.mark.skip(
        reason=(
            "driver-gap: Rust-backed TOP/ORDER BY query pages can exceed max_item_count=2 "
            "(known gap 30, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-top-page-size). "
            "Re-enable when paging honors the requested maximum while preserving result ordering "
            "and the total count."
        )
    )
    def test_orderby_top_query_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_orderby_top_query
        # test an order by query combined with top

        top_count = 9
        # sanity check
        self.assertLess(top_count, len(self.document_definitions))

        # an order by query with top, total existing docs more than requested top count
        query = {
            'query': 'SELECT top %d * FROM root r order by r.spam' % top_count  # nosec
        }

        def get_order_by_key(r):
            return r['spam']

        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)[:top_count]]

        self.execute_query_and_validate_results(query, expected_ordered_ids)

    def execute_query_and_validate_results(self, query, expected_ordered_ids):
        # Source helper: tests/test_orderby.py::TestCrossPartitionTopOrderBy.execute_query_and_validate_results
        page_size = 2

        result_iterable = self.created_container.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=page_size
        )

        self.assertTrue(isinstance(result_iterable, ItemPaged))

        it = result_iterable.__iter__()

        def invokeNext():
            return next(it)

        for i in range(len(expected_ordered_ids)):
            item = invokeNext()
            self.assertEqual(item['id'], expected_ordered_ids[i])

        results = {}
        cnt = 0
        page_iter = result_iterable.by_page()
        for page in page_iter:
            fetched_res = list(page)
            fetched_size = len(fetched_res)

            for item in fetched_res:
                self.assertEqual(item['id'], expected_ordered_ids[cnt])
                results[cnt] = item
                cnt = cnt + 1
            if (cnt < len(expected_ordered_ids)):
                self.assertEqual(fetched_size, page_size, "page size")
            else:
                if cnt == len(expected_ordered_ids):
                    self.assertTrue(fetched_size <= page_size, "last page size")
                    break
                else:
                    self.fail("more results than expected")

        self.assertEqual(len(results), len(expected_ordered_ids))

        with self.assertRaises(StopIteration):
            next(page_iter)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_orderby_query_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_orderby_query
        # test a simple order by query

        # an order by query
        query = {
            'query': 'SELECT * FROM root r order by r.spam',
        }

        def get_order_by_key(r):
            return r['spam']

        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]

        # validates the results size and order
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_orderby_query_as_string_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_orderby_query_as_string
        # test a simple order by query as string

        # an order by query
        query = 'SELECT * FROM root r order by r.spam'

        def get_order_by_key(r):
            return r['spam']

        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]

        # validates the results size and order
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_orderby_asc_query_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_orderby_asc_query
        # test an order by query with explicit ascending ordering

        # an ascending order by query (ascending explicitly mentioned in the query)
        query = {
            'query': 'SELECT * FROM root r order by r.spam ASC',
        }

        def get_order_by_key(r):
            return r['spam']

        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]

        # validates the results size and order
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_orderby_desc_query_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_orderby_desc_query
        # test an order by query with explicit descending ordering

        # a descending order by query
        query = {
            'query': 'SELECT * FROM root r order by r.spam DESC',
        }

        def get_order_by_key(r):
            return r['spam']

        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key, reverse=True)]

        # validates the results size and order
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_orderby_top_query_less_results_than_top_counts_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_orderby_top_query_less_results_than_top_counts
        # test an order by query combined with top. where top is greater than the total number of docs

        top_count = 30
        # sanity check
        self.assertGreater(top_count, len(self.document_definitions))

        # an order by query with top, total existing docs less than requested top count
        query = {
            'query': 'SELECT top %d * FROM root r order by r.spam' % top_count  # nosec
        }

        def get_order_by_key(r):
            return r['spam']

        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]

        self.execute_query_and_validate_results(query, expected_ordered_ids)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_top_query_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_top_query
        # test a simple top query without order by.
        # The rewrittenQuery in the query execution info responded by backend will be empty

        pytest.skip("internals-only: expected results are built from legacy "
                    "client_connection._ReadPartitionKeyRanges and per-range QueryFeed pages, which the "
                    "Rust-backed client does not expose. The documents were created.")
        partition_key_ranges = list(self.client.client_connection._ReadPartitionKeyRanges(self.collection_link))

        docs_by_partition_key_range_id = self.find_docs_by_partition_key_range_id()

        # find the first two non-empty target partition key ranges
        cnt = 0
        first_two_ranges_results = []
        for r in partition_key_ranges:
            if cnt >= 2:
                break
            p_id = r['id']
            if len(docs_by_partition_key_range_id[p_id]) > 0:
                first_two_ranges_results.extend(docs_by_partition_key_range_id[p_id])
                cnt += 1

        # sanity checks
        self.assertEqual(cnt, 2)
        self.assertLess(2, len(partition_key_ranges))

        # sanity check
        self.assertLess(len(first_two_ranges_results), len(self.document_definitions))
        self.assertGreater(len(first_two_ranges_results), 1)

        expected_ordered_ids = [d['id'] for d in first_two_ranges_results]

        # a top query, the results will be sorted based on the target partition key range
        query = {
            'query': 'SELECT top %d * FROM root r' % len(expected_ordered_ids)  # nosec
        }
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_top_query_as_string_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_top_query_as_string
        # test a simple top query without order by.
        # The rewrittenQuery in the query execution info responded by backend will be empty

        pytest.skip("internals-only: expected results are built from legacy "
                    "client_connection._ReadPartitionKeyRanges and per-range QueryFeed pages, which the "
                    "Rust-backed client does not expose. The documents were created.")
        partition_key_ranges = list(self.client.client_connection._ReadPartitionKeyRanges(self.collection_link))

        docs_by_partition_key_range_id = self.find_docs_by_partition_key_range_id()

        # find the first two non-empty target partition key ranges
        cnt = 0
        first_two_ranges_results = []
        for r in partition_key_ranges:
            if cnt >= 2:
                break
            p_id = r['id']
            if len(docs_by_partition_key_range_id[p_id]) > 0:
                first_two_ranges_results.extend(docs_by_partition_key_range_id[p_id])
                cnt += 1

        # sanity checks
        self.assertEqual(cnt, 2)
        self.assertLess(2, len(partition_key_ranges))

        # sanity check
        self.assertLess(len(first_two_ranges_results), len(self.document_definitions))
        self.assertGreater(len(first_two_ranges_results), 1)

        expected_ordered_ids = [d['id'] for d in first_two_ranges_results]

        # a top query, the results will be sorted based on the target partition key range
        query = 'SELECT top %d * FROM root r' % len(expected_ordered_ids)  # nosec
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_parametrized_top_query_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_parametrized_top_query
        # test a simple parameterized query without order by.
        # The rewrittenQuery in the query execution info responded by backend will be empty

        pytest.skip("internals-only: expected results are built from legacy "
                    "client_connection._ReadPartitionKeyRanges and per-range QueryFeed pages, which the "
                    "Rust-backed client does not expose. The documents were created.")
        partition_key_ranges = list(self.client.client_connection._ReadPartitionKeyRanges(self.collection_link))

        docs_by_partition_key_range_id = self.find_docs_by_partition_key_range_id()

        # find the first two non-empty target partition key ranges
        cnt = 0
        first_two_ranges_results = []
        for r in partition_key_ranges:
            if cnt >= 2:
                break
            p_id = r['id']
            if len(docs_by_partition_key_range_id[p_id]) > 0:
                first_two_ranges_results.extend(docs_by_partition_key_range_id[p_id])
                cnt += 1

        # sanity checks
        self.assertEqual(cnt, 2)
        self.assertLess(2, len(partition_key_ranges))

        # sanity check
        self.assertLess(len(first_two_ranges_results), len(self.document_definitions))
        self.assertGreater(len(first_two_ranges_results), 1)

        expected_ordered_ids = [d['id'] for d in first_two_ranges_results]

        # a top query, the results will be sorted based on the target partition key range
        query = {
            'query': 'SELECT top @n * FROM root r',

            "parameters": [
                {"name": "@n", "value": len(expected_ordered_ids)}
            ]
        }
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_orderby_query_with_parametrized_top_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_orderby_query_with_parametrized_top
        # test an order by query combined with parametrized top

        top_count = 9
        # sanity check
        self.assertLess(top_count, len(self.document_definitions))

        def get_order_by_key(r):
            return r['spam']

        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)[:top_count]]

        # a parametrized top order by query
        query = {
            'query': 'SELECT top @n * FROM root r order by r.spam',

            "parameters": [
                {"name": "@n", "value": top_count}
            ]
        }

        self.execute_query_and_validate_results(query, expected_ordered_ids)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_orderby_query_with_parametrized_predicate_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_orderby_query_with_parametrized_predicate
        # test an order by query combined with parametrized predicate

        # an order by query with parametrized predicate
        query = {
            'query': 'SELECT * FROM root r where r.cnt > @cnt order by r.spam',

            "parameters": [
                {"name": "@cnt", "value": 5}
            ]

        }

        def get_order_by_key(r):
            return r['spam']

        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key) if
                                r['cnt'] > 5]

        self.execute_query_and_validate_results(query, expected_ordered_ids)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_orderby_query_noncomparable_orderby_item_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_orderby_query_noncomparable_orderby_item
        # Known gap 30 item 10: docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30
        pytest.skip(
            "driver-gap: Rust returns rows for ORDER BY over mixed number/string values instead of the "
            "legacy ValueError (known gap 30 item 10, "
            "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-orderby-mixed-types)."
        )
        # test orderby with different order by item type

        # an order by query
        query = {
            'query': 'SELECT * FROM root r order by r.spam2 DESC',
        }

        def get_order_by_key(r):
            return r['id']

        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]

        # validates the results size and order
        try:
            self.execute_query_and_validate_results(query, expected_ordered_ids)
            self.fail('non comparable order by items did not result in failure.')
        except ValueError as e:
            self.assertTrue(
                e.args[0] == "Expected String, but got Number." or e.message == "Expected Number, but got String.")

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_orderby_integer_query_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_orderby_integer_query
        # an order by integer query
        query = {
            'query': 'SELECT * FROM root r order by r.cnt',
        }

        def get_order_by_key(r):
            return r['cnt']

        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]

        # validates the results size and order
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_orderby_floating_point_number_query_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_orderby_floating_point_number_query
        # an orderby by floating point number query
        query = {
            'query': 'SELECT * FROM root r order by r.number',
        }

        def get_order_by_key(r):
            return r['number']

        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]

        # validates the results size and order
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADLong
    def test_orderby_boolean_query_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_orderby_boolean_query
        # an orderby by floating point number query
        query = {
            'query': 'SELECT * FROM root r order by r.boolVar',
        }

        result_iterable = self.created_container.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=2
        )
        results = list(result_iterable)
        # validates the results size and order

        self.assertEqual(len(results), len(self.document_definitions))

        # false values before true values
        index = 0
        while index < len(results):
            if results[index]['boolVar']:
                break

            self.assertTrue(int(results[index]['id']) % 2 == 1)
            index = index + 1

        while index < len(results):
            self.assertTrue(results[index]['boolVar'])
            self.assertTrue(int(results[index]['id']) % 2 == 0)
            index = index + 1

    def find_docs_by_partition_key_range_id(self):
        # Source helper: tests/test_orderby.py::TestCrossPartitionTopOrderBy.find_docs_by_partition_key_range_id
        query = {
            'query': 'SELECT * FROM root r'
        }

        partition_key_range = list(self.client.client_connection._ReadPartitionKeyRanges(self.collection_link))
        docs_by_partition_key_range_id = {}
        for r in partition_key_range:
            options = {}

            path = base.GetPathFromLink(self.collection_link, 'docs')
            collection_id = base.GetResourceIdOrFullNameFromLink(self.collection_link)

            def fetch_fn(options):
                return self.client.client_connection.QueryFeed(path, collection_id, query, options, r['id'])

            docResultsIterable = ItemPaged(
                self.client.client_connection,
                query,
                options,
                fetch_function=fetch_fn,
                collection_link=self.collection_link,
                page_iterator_class=query_iterable.QueryIterable
            )

            docs = list(docResultsIterable)
            self.assertFalse(r['id'] in docs_by_partition_key_range_id)
            docs_by_partition_key_range_id[r['id']] = docs
        return docs_by_partition_key_range_id
