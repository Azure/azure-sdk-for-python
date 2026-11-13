# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Copied aggregate query tests against the ``_backend="rust"`` path.

Self-contained: ``setUpClass`` creates an owned database and the original's
10,100 RU/s ``/key`` container with Range indexes, inserts the original
documents and deletes the database in ``tearDownClass``. The original's shared
test database and key/data client pair become one key-auth Rust client. Class
and method names match ``tests/test_aggregate.py``; no original test module is
imported.

Run with::

    pytest --noconftest tests/query_items/sync/test_aggregate.py -v
"""
import os
import unittest
import uuid

import pytest

import azure.cosmos.documents as documents
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.partition_key import PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)
# Source helper: tests/test_config.py::TestConfig.data_auth_mode
DATA_AUTH_MODE = os.environ.get("COSMOS_TEST_DATA_AUTH_MODE", "key").lower()


class _config:
    # Source helper: tests/test_aggregate.py::_config
    is_aad_mode = DATA_AUTH_MODE == "aad"
    PARTITION_KEY = 'key'
    UNIQUE_PARTITION_KEY = 'uniquePartitionKey'
    FIELD = 'field'
    # Keep key-auth query coverage unchanged; trim only AAD runs to stay under CI timeout.
    DOCUMENTS_COUNT = 120 if is_aad_mode else 400
    DOCS_WITH_SAME_PARTITION_KEY = 60 if is_aad_mode else 200
    docs_with_numeric_id = 0
    sum = 0


@pytest.mark.cosmosQuery
class TestAggregateQuery(unittest.TestCase):
    client: CosmosClient = None

    @classmethod
    def setUpClass(cls):
        cls._all_tests = []
        cls._setup()
        cls._generate_test_configs()

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            cls.client.delete_database(cls.database_id)
            print(f"\nDeleted owned aggregate database: {cls.database_id}")
        except CosmosHttpResponseError:
            pass
        finally:
            cls.client.close()

    @classmethod
    def _setup(cls):
        cls.client = CosmosClient(HOST, KEY, _backend="rust")
        cls.database_id = "legacy_query_aggregate_" + uuid.uuid4().hex[:8]
        cls.created_db = cls.client.create_database(cls.database_id)
        print(f"\nOwned aggregate database: {cls.database_id}")
        try:
            cls.created_collection = cls._create_collection(cls.created_db)

            # test documents
            document_definitions = []

            values = [None, False, True, "abc", "cdfg", "opqrs", "ttttttt", "xyz", "oo", "ppp"]
            for value in values:
                d = {_config.PARTITION_KEY: value, 'id': str(uuid.uuid4())}
                document_definitions.append(d)

            for i in range(_config.DOCS_WITH_SAME_PARTITION_KEY):
                d = {_config.PARTITION_KEY: _config.UNIQUE_PARTITION_KEY,
                     'resourceId': i,
                     _config.FIELD: i + 1,
                     'id': str(uuid.uuid4())}
                document_definitions.append(d)

            _config.docs_with_numeric_id = \
                _config.DOCUMENTS_COUNT - len(values) - _config.DOCS_WITH_SAME_PARTITION_KEY
            for i in range(_config.docs_with_numeric_id):
                d = {_config.PARTITION_KEY: i + 1, 'id': str(uuid.uuid4())}
                document_definitions.append(d)

            _config.sum = _config.docs_with_numeric_id \
                          * (_config.docs_with_numeric_id + 1) / 2.0

            cls._insert_doc(cls.created_collection, document_definitions)
        except Exception:
            cls.client.delete_database(cls.database_id)
            cls.client.close()
            raise

    @classmethod
    def _generate_test_configs(cls):
        aggregate_query_format = 'SELECT VALUE {}(r.{}) FROM r WHERE {}'
        aggregate_orderby_query_format = 'SELECT VALUE {}(r.{}) FROM r WHERE {} ORDER BY r.{}'
        aggregate_configs = [
            ['AVG', _config.sum / _config.docs_with_numeric_id,
             'IS_NUMBER(r.{})'.format(_config.PARTITION_KEY)],
            ['AVG', None, 'true'],
            ['COUNT', _config.DOCUMENTS_COUNT, 'true'],
            ['MAX', 'xyz', 'true'],
            ['MIN', None, 'true'],
            ['SUM', _config.sum, 'IS_NUMBER(r.{})'.format(_config.PARTITION_KEY)],
            ['SUM', None, 'true']
        ]
        for operator, expected, condition in aggregate_configs:
            cls._all_tests.append([
                '{} {}'.format(operator, condition),
                aggregate_query_format.format(operator, _config.PARTITION_KEY, condition),
                expected])
            cls._all_tests.append([
                '{} {} OrderBy'.format(operator, condition),
                aggregate_orderby_query_format.format(operator, _config.PARTITION_KEY, condition,
                                                      _config.PARTITION_KEY),
                expected])

        aggregate_single_partition_format = 'SELECT VALUE {}(r.{}) FROM r WHERE r.{} = \'{}\''
        aggregate_orderby_single_partition_format = 'SELECT {}(r.{}) FROM r WHERE r.{} = \'{}\''
        same_partiton_sum = _config.DOCS_WITH_SAME_PARTITION_KEY * (_config.DOCS_WITH_SAME_PARTITION_KEY + 1) / 2.0
        aggregate_single_partition_configs = [
            ['AVG', same_partiton_sum / _config.DOCS_WITH_SAME_PARTITION_KEY],
            ['COUNT', _config.DOCS_WITH_SAME_PARTITION_KEY],
            ['MAX', _config.DOCS_WITH_SAME_PARTITION_KEY],
            ['MIN', 1],
            ['SUM', same_partiton_sum]
        ]
        for operator, expected in aggregate_single_partition_configs:
            cls._all_tests.append([
                '{} SinglePartition {}'.format(operator, 'SELECT VALUE'),
                aggregate_single_partition_format.format(
                    operator, _config.FIELD, _config.PARTITION_KEY, _config.UNIQUE_PARTITION_KEY), expected])
            cls._all_tests.append([
                '{} SinglePartition {}'.format(operator, 'SELECT'),
                aggregate_orderby_single_partition_format.format(
                    operator, _config.FIELD, _config.PARTITION_KEY, _config.UNIQUE_PARTITION_KEY),
                Exception()])

    def test_run_all_rust(self):
        # Source: tests/test_aggregate.py::TestAggregateQuery.test_run_all
        for test_name, query, expected_result in self._all_tests:
            test_name = "test_%s" % test_name
            try:
                self._run_one(query, expected_result)
                print(test_name + ': ' + query + " PASSED")
            except Exception as e:
                print(test_name + ': ' + query + " FAILED")
                if "20113" in str(e):
                    # pylint: disable-next=line-too-long
                    # Known gap 30: query_items remaining query, paging, and continuation-token gaps, item 1 aggregates (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-full-range-sum).
                    pytest.skip("driver-gap: Rust rejects cross-partition aggregates with 400/20113 "
                                "(ClientUnsupportedQueryFeature) (known gap 30 item 1, "
                                "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-full-range-sum). "
                                "Failed at " + test_name + ".")
                raise e

    @pytest.mark.cosmosAADLong
    @pytest.mark.skipif(
        DATA_AUTH_MODE != "aad",
        reason="environment-gap: AAD-only smoke subset; full coverage runs under cosmosQuery (key auth).",
    )
    def test_aad_aggregate_subset_rust(self):
        # Source: tests/test_aggregate.py::TestAggregateQuery.test_aad_aggregate_subset
        same_partition_avg = (
            _config.DOCS_WITH_SAME_PARTITION_KEY * (_config.DOCS_WITH_SAME_PARTITION_KEY + 1) / 2.0
        ) / _config.DOCS_WITH_SAME_PARTITION_KEY
        subset = [
            (
                "test_aad_xp_count",
                "SELECT VALUE COUNT(r.{}) FROM r WHERE true".format(_config.PARTITION_KEY),
                _config.DOCUMENTS_COUNT,
            ),
            (
                "test_aad_xp_sum_orderby",
                "SELECT VALUE SUM(r.{f}) FROM r WHERE IS_NUMBER(r.{pk}) ORDER BY r.{pk}".format(
                    f=_config.PARTITION_KEY, pk=_config.PARTITION_KEY
                ),
                _config.sum,
            ),
            (
                "test_aad_sp_avg",
                "SELECT VALUE AVG(r.{f}) FROM r WHERE r.{pk} = '{val}'".format(
                    f=_config.FIELD,
                    pk=_config.PARTITION_KEY,
                    val=_config.UNIQUE_PARTITION_KEY,
                ),
                same_partition_avg,
            ),
        ]
        for test_name, query, expected in subset:
            try:
                self._run_one(query, expected)
                print(test_name + ': ' + query + " PASSED", flush=True)
            except Exception as e:
                print(test_name + ': ' + query + " FAILED", flush=True)
                raise e

    def _run_one(self, query, expected_result):
        self._execute_query_and_validate_results(self.created_collection, query, expected_result)

    @classmethod
    def _create_collection(cls, created_db):
        created_collection = created_db.create_container(
            id='aggregate tests collection ' + str(uuid.uuid4()),
            indexing_policy={
                'includedPaths': [
                    {
                        'path': '/',
                        'indexes': [
                            {
                                'kind': 'Range',
                                'dataType': 'Number'
                            },
                            {
                                'kind': 'Range',
                                'dataType': 'String'
                            }
                        ]
                    }
                ]
            },
            partition_key=PartitionKey(
                path='/{}'.format(_config.PARTITION_KEY),
                kind=documents.PartitionKind.Hash,
            ),
            offer_throughput=10100
        )
        return created_collection

    @classmethod
    def _insert_doc(cls, collection, document_definitions):
        created_docs = []
        for d in document_definitions:
            created_doc = collection.create_item(body=d)
            created_docs.append(created_doc)

        return created_docs

    def _execute_query_and_validate_results(self, collection, query, expected):
        # executes the query and validates the results against the expected results
        result_iterable = collection.query_items(
            query=query,
            enable_cross_partition_query=True
        )

        def _verify_result():
            ######################################
            # test next() behavior
            ######################################
            it = result_iterable.__iter__()

            def invokeNext():
                return next(it)

            # validate that invocations of next() produces the same results as expected
            item = invokeNext()
            self.assertEqual(item, expected)

            # after the result set is exhausted, invoking next must raise a StopIteration exception
            self.assertRaises(StopIteration, invokeNext)

            ######################################
            # test by_page() behavior
            ######################################
            page_iter = result_iterable.by_page()
            fetched_res = list(next(page_iter))
            fetched_size = len(fetched_res)

            self.assertEqual(fetched_size, 1)
            self.assertEqual(fetched_res[0], expected)

            # no more results will be returned
            with self.assertRaises(StopIteration):
                next(page_iter)

        if isinstance(expected, Exception):
            self.assertRaises(CosmosHttpResponseError, _verify_result)
        else:
            _verify_result()


if __name__ == "__main__":
    unittest.main()
