# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Copied query execution context test against the ``_backend="rust"`` path.

Self-contained: ``setUpClass`` creates an owned database and ``/id`` container
with the original 20 documents and deletes the database in ``tearDownClass``.
The original's key/data client pair becomes one key-auth Rust client. The
``setUp`` partition-range sanity check uses public ``read_feed_ranges()``
instead of the legacy ``client_connection._ReadPartitionKeyRanges``. The
public ``query_items`` assertion runs; the legacy
``_DefaultQueryExecutionContext`` checks stop with an internals-only skip.
Class and method names match ``tests/test_query_execution_context.py``; no
original test module is imported.

Run with::

    pytest --noconftest tests/query_items/sync/test_query_execution_context.py -v
"""
import os
import unittest
import uuid

import pytest

import azure.cosmos._base as base
from azure.cosmos import CosmosClient
from azure.cosmos._execution_context import base_execution_context as base_execution_context
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.partition_key import PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


def get_database_link(database):
    # Source helper: tests/test_query_execution_context.py::get_database_link
    return 'dbs/' + database.id


def get_document_collection_link(database, document_collection):
    # Source helper: tests/test_query_execution_context.py::get_document_collection_link
    return get_database_link(database) + '/colls/' + document_collection.id


@pytest.mark.cosmosEmulator
class TestQueryExecutionContextEndToEnd(unittest.TestCase):
    """Routing Map Functionalities end-to-end Tests.
    """

    created_collection = None
    document_definitions = None
    created_db = None
    client: CosmosClient = None

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(HOST, KEY, _backend="rust")
        cls.database_id = "legacy_query_exec_context_" + uuid.uuid4().hex[:8]
        cls.created_db = cls.client.create_database(cls.database_id)
        print(f"\nOwned query execution context database: {cls.database_id}")
        try:
            container_id = 'query_execution_context_tests_' + str(uuid.uuid4())
            cls.created_collection = cls.created_db.create_container(
                id=container_id,
                partition_key=PartitionKey(path='/id', kind='Hash')
            )
            cls.document_definitions = []

            # create a document using the document definition
            for i in range(20):
                d = {'id': str(i),
                     'name': 'sample document',
                     'spam': 'eggs' + str(i),
                     'key': 'value'}
                cls.document_definitions.append(d)
            cls.insert_doc(cls.document_definitions)
        except Exception:
            cls.client.delete_database(cls.database_id)
            cls.client.close()
            raise

    @classmethod
    def tearDownClass(cls):
        try:
            cls.client.delete_database(cls.database_id)
            print(f"\nDeleted owned query execution context database: {cls.database_id}")
        except CosmosHttpResponseError:
            pass
        finally:
            cls.client.close()

    def setUp(self):
        # sanity check:
        feed_ranges = list(self.created_collection.read_feed_ranges())
        self.assertGreaterEqual(len(feed_ranges), 1)

        # sanity check: read documents after creation
        queried_docs = list(self.created_collection.read_all_items())
        self.assertEqual(
            len(queried_docs),
            len(self.document_definitions),
            'create should increase the number of documents')

    def test_simple_query_default_execution_context_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_execution_context.py::TestQueryExecutionContextEndToEnd.test_simple_query_default_execution_context

        query = {
            'query': 'SELECT * FROM root r WHERE r.id != @id',
            'parameters': [
                {'name': '@id', 'value': '5'}
            ]
        }

        options = {'enableCrossPartitionQuery': True, 'maxItemCount': 2}

        res = self.created_collection.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=2
        )
        self.assertEqual(len(list(res)), 19)

        pytest.skip("internals-only: the rest drives legacy _DefaultQueryExecutionContext with "
                    "client_connection.QueryFeed, which the Rust-backed client does not use. "
                    "The public query_items result count was verified.")
        self._test_default_execution_context(options, query, 19)

    def _test_default_execution_context(self, options, query, expected_number_of_results):
        # pylint: disable-next=line-too-long
        # Source helper: tests/test_query_execution_context.py::TestQueryExecutionContextEndToEnd._test_default_execution_context
        page_size = options['maxItemCount']
        collection_link = get_document_collection_link(self.created_db, self.created_collection)
        path = base.GetPathFromLink(collection_link, 'docs')
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)

        def fetch_fn(options):
            return self.client.client_connection.QueryFeed(path,
                                                           collection_id,
                                                           query,
                                                           options)

        ######################################
        # test next() behavior
        ######################################
        ex = base_execution_context._DefaultQueryExecutionContext(self.client.client_connection, options, fetch_fn)

        it = ex.__iter__()

        def invokeNext():
            return next(it)

        results = {}
        # validate that invocations of next() produces the same results as expected
        for _ in range(expected_number_of_results):
            item = invokeNext()
            results[item['id']] = item

        self.assertEqual(len(results), expected_number_of_results)

        # after the result set is exhausted, invoking next must raise a StopIteration exception
        self.assertRaises(StopIteration, invokeNext)

        ######################################
        # test fetch_next_block() behavior
        ######################################
        ex = base_execution_context._DefaultQueryExecutionContext(self.client.client_connection, options, fetch_fn)

        results = {}
        cnt = 0
        fetched_res = ex.fetch_next_block()
        fetched_size = 0
        while fetched_res is not None and len(fetched_res) > 0:
            fetched_size = len(fetched_res)

            for item in fetched_res:
                results[item['id']] = item
            cnt += fetched_size
            fetched_res = ex.fetch_next_block()

        # validate the number of collected results
        self.assertEqual(len(results), expected_number_of_results)

        self.assertTrue(fetched_size > 0, "fetched size is 0")
        self.assertTrue(fetched_size <= page_size, "fetched page size greater than page size")

        # no more results will be returned
        self.assertEqual(ex.fetch_next_block(), [])

    @classmethod
    def insert_doc(cls, document_definitions):
        # create a document using the document definition
        created_docs = []
        for d in document_definitions:
            created_doc = cls.created_collection.create_item(body=d)
            created_docs.append(created_doc)

        return created_docs


if __name__ == "__main__":
    unittest.main()
