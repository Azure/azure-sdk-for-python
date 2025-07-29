# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import time
import unittest
import uuid

import pytest

import test_config
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, DatabaseProxy


@pytest.mark.cosmosSplit
class TestPartitionSplitChangeFeedAsync(unittest.IsolatedAsyncioTestCase):
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy

    client: CosmosClient = None
    created_database: DatabaseProxy = None

    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.created_database = self.client.get_database_client(self.TEST_DATABASE_ID)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_query_change_feed_with_split_async(self):
        created_collection = await self.created_database.create_container("change_feed_test_" + str(uuid.uuid4()),
                                                                        PartitionKey(path="/pk"),
                                                                        offer_throughput=400)

        # initial change feed query returns empty result
        query_iterable = created_collection.query_items_change_feed(start_time="Beginning")
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0
        continuation = created_collection.client_connection.last_response_headers['etag']
        assert continuation != ''

        # create one doc and make sure change feed query can return the document
        document_definition = {'pk': 'pk', 'id': 'doc1'}
        await created_collection.create_item(body=document_definition)
        query_iterable = created_collection.query_items_change_feed(continuation=continuation)
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 1
        continuation = created_collection.client_connection.last_response_headers['etag']

        await test_config.TestConfig.trigger_split_async(created_collection, 11000)

        print("creating few more documents")
        new_documents = [{'pk': 'pk2', 'id': 'doc2'}, {'pk': 'pk3', 'id': 'doc3'}, {'pk': 'pk4', 'id': 'doc4'}]
        expected_ids = ['doc2', 'doc3', 'doc4']
        for document in new_documents:
            await created_collection.create_item(body=document)

        query_iterable = created_collection.query_items_change_feed(continuation=continuation)
        it = query_iterable.__aiter__()
        actual_ids = []
        async for item in it:
            actual_ids.append(item['id'])

        assert actual_ids == expected_ids
        await self.created_database.delete_container(created_collection.id)

if __name__ == '__main__':
    unittest.main()