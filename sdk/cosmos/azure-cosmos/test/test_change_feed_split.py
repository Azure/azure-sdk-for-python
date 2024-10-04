# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import time
import unittest
import uuid

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy, PartitionKey


class TestPartitionSplitChangeFeed(unittest.TestCase):
    database: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.database = cls.client.get_database_client(cls.TEST_DATABASE_ID)

    def test_query_change_feed_with_split(self):
        created_collection = self.database.create_container("change_feed_split_test_" + str(uuid.uuid4()),
                                                              PartitionKey(path="/pk"),
                                                              offer_throughput=400)

        # initial change feed query returns empty result
        query_iterable = created_collection.query_items_change_feed(start_time="Beginning")
        iter_list = list(query_iterable)
        assert len(iter_list) == 0
        continuation = created_collection.client_connection.last_response_headers['etag']
        assert continuation != ''

        # create one doc and make sure change feed query can return the document
        document_definition = {'pk': 'pk', 'id': 'doc1'}
        created_collection.create_item(body=document_definition)
        query_iterable = created_collection.query_items_change_feed(continuation=continuation)
        iter_list = list(query_iterable)
        assert len(iter_list) == 1
        continuation = created_collection.client_connection.last_response_headers['etag']

        print("Triggering a split in test_query_change_feed_with_split")
        created_collection.replace_throughput(11000)
        print("changed offer to 11k")
        print("--------------------------------")
        print("Waiting for split to complete")
        start_time = time.time()

        while True:
            offer = created_collection.get_throughput()
            if offer.properties['content'].get('isOfferReplacePending', False):
                if time.time() - start_time > 60 * 25:  # timeout test at 25 minutes
                    unittest.skip("Partition split didn't complete in time.")
                else:
                    print("Waiting for split to complete")
                    time.sleep(60)
            else:
                break

        print("Split in test_query_change_feed_with_split has completed")
        print("creating few more documents")
        new_documents = [{'pk': 'pk2', 'id': 'doc2'}, {'pk': 'pk3', 'id': 'doc3'}, {'pk': 'pk4', 'id': 'doc4'}]
        expected_ids = ['doc2', 'doc3', 'doc4']
        for document in new_documents:
            created_collection.create_item(body=document)

        query_iterable = created_collection.query_items_change_feed(continuation=continuation)
        it = query_iterable.__iter__()
        actual_ids = []
        for item in it:
            actual_ids.append(item['id'])

        assert actual_ids == expected_ids
        self.database.delete_container(created_collection.id)

if __name__ == "__main__":
    unittest.main()
