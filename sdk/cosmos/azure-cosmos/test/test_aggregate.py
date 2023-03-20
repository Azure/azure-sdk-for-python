# The MIT License (MIT)
# Copyright (c) 2017 Microsoft Corporation

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

from __future__ import print_function

import unittest
import uuid
import pytest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents
import test_config
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.partition_key import PartitionKey

pytestmark = pytest.mark.cosmosEmulator

class _config:
    host = test_config._test_config.host
    master_key = test_config._test_config.masterKey
    connection_policy = test_config._test_config.connectionPolicy
    PARTITION_KEY = 'key'
    UNIQUE_PARTITION_KEY = 'uniquePartitionKey'
    FIELD = 'field'
    DOCUMENTS_COUNT = 400
    DOCS_WITH_SAME_PARTITION_KEY = 200
    docs_with_numeric_id = 0
    sum = 0


@pytest.mark.usefixtures("teardown")
class AggregationQueryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._all_tests = []
        cls._setup()
        cls._generate_test_configs()

    @classmethod
    def _setup(cls):
        if (not _config.master_key or not _config.host):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(
            _config.host, {'masterKey': _config.master_key}, "Session", connection_policy=_config.connection_policy)
        created_db = test_config._test_config.create_database_if_not_exist(cls.client)
        cls.created_collection = cls._create_collection(created_db)

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

    def test_run_all(self):
        for test_name, query, expected_result in self._all_tests:
            test_name = "test_%s" % test_name
            try:
                self._run_one(query, expected_result)
                print(test_name + ': ' + query + " PASSED")
            except Exception as e:
                print(test_name + ': ' + query + " FAILED")
                raise e

    def _run_one(self, query, expected_result):
        self._execute_query_and_validate_results(self.created_collection, query, expected_result)

    @classmethod
    def _create_collection(cls, created_db):
        # type: (Database) -> Container
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
        # type: (Container, Dict[str, Any]) -> Dict[str, Any]
        created_docs = []
        for d in document_definitions:
            created_doc = collection.create_item(body=d)
            created_docs.append(created_doc)

        return created_docs

    def _execute_query_and_validate_results(self, collection, query, expected):
        # type: (Container, str, Dict[str, Any]) -> None

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
