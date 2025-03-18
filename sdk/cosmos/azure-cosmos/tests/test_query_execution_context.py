# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos._base as base
import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos._execution_context import base_execution_context as base_execution_context
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.partition_key import PartitionKey


def get_database_link(database):
    return 'dbs/' + database.id


def get_document_collection_link(database, document_collection):
    return get_database_link(database) + '/colls/' + document_collection.id


@pytest.mark.cosmosEmulator
class TestQueryExecutionContextEndToEnd(unittest.TestCase):
    """Routing Map Functionalities end-to-end Tests.
    """

    created_collection = None
    document_definitions = None
    created_db = None
    client: cosmos_client.CosmosClient = None
    config = test_config.TestConfig
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = config.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.created_collection = cls.created_db.create_container(
            id='query_execution_context_tests_' + str(uuid.uuid4()),
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

    @classmethod
    def tearDownClass(cls):
        try:
            cls.created_db.delete_container(cls.created_collection.id)
        except CosmosHttpResponseError:
            pass

    def setUp(self):
        # sanity check:
        partition_key_ranges = list(self.client.client_connection._ReadPartitionKeyRanges(
            get_document_collection_link(self.created_db, self.created_collection)))
        self.assertGreaterEqual(len(partition_key_ranges), 1)

        # sanity check: read documents after creation
        queried_docs = list(self.created_collection.read_all_items())
        self.assertEqual(
            len(queried_docs),
            len(self.document_definitions),
            'create should increase the number of documents')

    def test_no_query_default_execution_context(self):

        options = {'maxItemCount': 2}

        self._test_default_execution_context(options, None, 20)

    def test_no_query_default_execution_context_with_small_last_page(self):

        options = {'maxItemCount': 3}

        self._test_default_execution_context(options, None, 20)

    def test_simple_query_default_execution_context(self):

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

        self._test_default_execution_context(options, query, 19)

    def test_simple_query_default_execution_context_with_small_last_page(self):

        query = {
            'query': 'SELECT * FROM root r WHERE r.id != @id',
            'parameters': [
                {'name': '@id', 'value': '5'}
            ]
        }

        options = {}
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 3

        self._test_default_execution_context(options, query, 19)

    def _test_default_execution_context(self, options, query, expected_number_of_results):

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
