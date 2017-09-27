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

from six import with_metaclass
from six.moves import xrange

import pydocumentdb.document_client as document_client
import pydocumentdb.documents as documents
import test.test_config as test_config
from pydocumentdb.errors import HTTPFailure


class _config:
    host = test_config._test_config.host
    master_key = test_config._test_config.masterKey
    PARTITION_KEY = 'key'
    UNIQUE_PARTITION_KEY = 'uniquePartitionKey'
    FIELD = 'field'
    TEST_DATABASE_NAME = 'testDb'
    DOCUMENTS_COUNT = 400
    DOCS_WITH_SAME_PARTITION_KEY = 200
    docs_with_numeric_id = 0
    sum = 0


class _helper:
    @classmethod
    def clean_up_database(cls):
        client = document_client.DocumentClient(_config.host,
                                                {'masterKey': _config.master_key})
        query_iterable = client.QueryDatabases(
            'SELECT * FROM root r WHERE r.id=\'{}\''.format(_config.TEST_DATABASE_NAME))
        it = iter(query_iterable)

        test_db = next(it, None)
        if test_db is not None:
            client.DeleteDatabase(test_db['_self'])


class AggregateQueryTestSequenceMeta(type):
    def __new__(mcs, name, bases, dict):
        def _run_one(query, expected_result):
            def test(self):
                self._execute_query_and_validate_results(mcs.client, mcs.collection_link, query, expected_result)

            return test

        def _setup():
            if (not _config.master_key or not _config.host):
                raise Exception(
                    "You must specify your Azure DocumentDB account values for "
                    "'masterKey' and 'host' at the top of this class to run the "
                    "tests.")

            _helper.clean_up_database()

            mcs.client = document_client.DocumentClient(_config.host,
                                                        {'masterKey': _config.master_key})
            created_db = mcs.client.CreateDatabase({'id': _config.TEST_DATABASE_NAME})
            created_collection = _create_collection(mcs.client, created_db)
            mcs.collection_link = _get_collection_link(created_db, created_collection)

            # test documents
            document_definitions = []

            values = [None, False, True, "abc", "cdfg", "opqrs", "ttttttt", "xyz", "oo", "ppp"]
            for value in values:
                d = {_config.PARTITION_KEY: value}
                document_definitions.append(d)

            for i in xrange(_config.DOCS_WITH_SAME_PARTITION_KEY):
                d = {_config.PARTITION_KEY: _config.UNIQUE_PARTITION_KEY,
                     'resourceId': i,
                     _config.FIELD: i + 1}
                document_definitions.append(d)

            _config.docs_with_numeric_id = \
                _config.DOCUMENTS_COUNT - len(values) - _config.DOCS_WITH_SAME_PARTITION_KEY
            for i in xrange(_config.docs_with_numeric_id):
                d = {_config.PARTITION_KEY: i + 1}
                document_definitions.append(d)

            _config.sum = _config.docs_with_numeric_id \
                          * (_config.docs_with_numeric_id + 1) / 2.0

            _insert_doc(mcs.collection_link, document_definitions, mcs.client)

        def _generate_test_configs():
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
                _all_tests.append([
                    '{} {}'.format(operator, condition),
                    aggregate_query_format.format(operator, _config.PARTITION_KEY, condition),
                    expected])
                _all_tests.append([
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
                _all_tests.append([
                    '{} SinglePartition {}'.format(operator, 'SELECT VALUE'),
                    aggregate_single_partition_format.format(
                        operator, _config.FIELD, _config.PARTITION_KEY, _config.UNIQUE_PARTITION_KEY), expected])
                _all_tests.append([
                    '{} SinglePartition {}'.format(operator, 'SELECT'),
                    aggregate_orderby_single_partition_format.format(
                        operator, _config.FIELD, _config.PARTITION_KEY, _config.UNIQUE_PARTITION_KEY),
                    Exception()])

        def _run_all():
            for test_name, query, expected_result in _all_tests:
                test_name = "test_%s" % test_name
                dict[test_name] = _run_one(query, expected_result)

        def _create_collection(client, created_db):
            collection_definition = {
                'id': 'sample collection',
                'indexingPolicy': {
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
                'partitionKey': {
                    'paths': [
                        '/{}'.format(_config.PARTITION_KEY)
                    ],
                    'kind': documents.PartitionKind.Hash
                }
            }

            collection_options = {'offerThroughput': 10100}
            created_collection = client.CreateCollection(_get_database_link(created_db),
                                                         collection_definition,
                                                         collection_options)

            return created_collection

        def _insert_doc(collection_link, document_definitions, client):
            created_docs = []
            for d in document_definitions:
                created_doc = client.CreateDocument(collection_link, d)
                created_docs.append(created_doc)

            return created_docs

        def _get_database_link(database, is_name_based=True):
            if is_name_based:
                return 'dbs/' + database['id']
            else:
                return database['_self']

        def _get_collection_link(database, document_collection, is_name_based=True):
            if is_name_based:
                return _get_database_link(database) + '/colls/' + document_collection['id']
            else:
                return document_collection['_self']

        _all_tests = []

        _setup()
        _generate_test_configs()
        _run_all()
        return type.__new__(mcs, name, bases, dict)

class AggregationQueryTest(with_metaclass(AggregateQueryTestSequenceMeta, unittest.TestCase)):
    @classmethod
    def tearDownClass(cls):
        _helper.clean_up_database()

    def _execute_query_and_validate_results(self, client, collection_link, query, expected):
        print('Running test with query: ' + query)

        # executes the query and validates the results against the expected results
        options = {'enableCrossPartitionQuery': 'true'}

        result_iterable = client.QueryDocuments(collection_link, query, options)

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
            # test fetch_next_block() behavior
            ######################################
            fetched_res = result_iterable.fetch_next_block()
            fetched_size = len(fetched_res)

            self.assertEqual(fetched_size, 1)
            self.assertEqual(fetched_res[0], expected)

            # no more results will be returned
            self.assertEqual(result_iterable.fetch_next_block(), [])

        if isinstance(expected, Exception):
            self.assertRaises(HTTPFailure, _verify_result)
        else:
            _verify_result()

if __name__ == "__main__":
    unittest.main()
