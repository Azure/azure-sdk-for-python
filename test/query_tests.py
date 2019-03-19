import unittest
import azure.cosmos.cosmos_client as cosmos_client
import pytest
import test.test_config as test_config


@pytest.mark.usefixtures("teardown")
class QueryTest(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    config = test_config._test_config
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy
    client = cosmos_client.CosmosClient(host, {'masterKey': masterKey}, "Session", connectionPolicy)
    created_db = config.create_database_if_not_exist(client)

    def test_first_and_last_slashes_trimmed_for_query_string (self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        document_definition = {'pk': 'pk', 'id': 'myId'}
        created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk'
        )
        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], 'myId')

    def test_query_change_feed(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        # The test targets partition #3
        pkRangeId = "3"

        # Read change feed without passing any options
        query_iterable = created_collection.query_items_change_feed()
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)

        # Read change feed from current should return an empty list
        query_iterable = created_collection.query_items_change_feed(partition_key_range_id=pkRangeId)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        self.assertNotEquals(created_collection.client_connection.last_response_headers['etag'], '')

        # Read change feed from beginning should return an empty list
        query_iterable = created_collection.query_items_change_feed(
            partition_key_range_id=pkRangeId,
            is_start_from_beginning=True
        )
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation1 = created_collection.client_connection.last_response_headers['etag']
        self.assertNotEquals(continuation1, '')

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id':'doc1'}
        created_collection.create_item(body=document_definition)
        query_iterable = created_collection.query_items_change_feed(
            partition_key_range_id=pkRangeId,
            is_start_from_beginning=True,
        )
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 1)
        self.assertEqual(iter_list[0]['id'], 'doc1')
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation2 = created_collection.client_connection.last_response_headers['etag']
        self.assertNotEquals(continuation2, '')
        self.assertNotEquals(continuation2, continuation1)

        # Create two new documents. Verify that change feed contains the 2 new documents
        # with page size 1 and page size 100
        document_definition = {'pk': 'pk', 'id': 'doc2'}
        created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': 'doc3'}
        created_collection.create_item(body=document_definition)

        for pageSize in [1, 100]:
            # verify iterator
            query_iterable = created_collection.query_items_change_feed(
                partition_key_range_id=pkRangeId,
                continuation=continuation2,
                max_item_count=pageSize
            )
            it = query_iterable.__iter__()
            expected_ids = 'doc2.doc3.'
            actual_ids = ''
            for item in it:
                actual_ids += item['id'] + '.'    
            self.assertEqual(actual_ids, expected_ids)

            # verify fetch_next_block
            # the options is not copied, therefore it need to be restored
            query_iterable = created_collection.query_items_change_feed(
                partition_key_range_id=pkRangeId,
                continuation=continuation2,
                max_item_count=pageSize
            )
            count = 0
            expected_count = 2
            all_fetched_res = []
            while (True):
                fetched_res = query_iterable.fetch_next_block()
                self.assertEquals(len(fetched_res), min(pageSize, expected_count - count))
                count += len(fetched_res)
                all_fetched_res.extend(fetched_res)
                if len(fetched_res) == 0:
                    break
            actual_ids = ''
            for item in all_fetched_res:
                actual_ids += item['id'] + '.'
            self.assertEqual(actual_ids, expected_ids)
            # verify there's no more results
            self.assertEquals(query_iterable.fetch_next_block(), [])

        # verify reading change feed from the beginning
        query_iterable = created_collection.query_items_change_feed(
            partition_key_range_id=pkRangeId,
            is_start_from_beginning=True
        )
        expected_ids = ['doc1', 'doc2', 'doc3']
        it = query_iterable.__iter__()
        for i in range(0, len(expected_ids)):
            doc = next(it)
            self.assertEquals(doc['id'], expected_ids[i])
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation3 = created_collection.client_connection.last_response_headers['etag']

        # verify reading empty change feed 
        query_iterable = created_collection.query_items_change_feed(
            partition_key_range_id=pkRangeId,
            continuation=continuation3,
            is_start_from_beginning=True
        )
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)

    def test_populate_query_metrics(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        document_definition = {'pk': 'pk', 'id':'myId'}
        created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk',
            populate_query_metrics=True
        )

        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], 'myId')

        METRICS_HEADER_NAME = 'x-ms-documentdb-query-metrics'
        self.assertTrue(METRICS_HEADER_NAME in created_collection.client_connection.last_response_headers)
        metrics_header = created_collection.client_connection.last_response_headers[METRICS_HEADER_NAME]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        self.assertTrue(len(metrics) > 1)
        self.assertTrue(all(['=' in x for x in metrics]))


if __name__ == "__main__":
    unittest.main()