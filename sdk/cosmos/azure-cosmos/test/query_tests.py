import unittest
import uuid
import pytest
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents
import test_config

pytestmark = pytest.mark.cosmosEmulator

@pytest.mark.usefixtures("teardown")
class QueryTest(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    config = test_config._test_config
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        
        cls.client = cosmos_client.CosmosClient(cls.host, {'masterKey': cls.masterKey}, cls.connectionPolicy)
        cls.created_db = cls.config.create_database_if_not_exist(cls.client)

    def test_first_and_last_slashes_trimmed_for_query_string (self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        document_definition = {'pk': 'pk', 'id':'myId'}
        self.client.CreateItem(created_collection['_self'], document_definition)

        query_options = {'partitionKey': 'pk'}
        collectionLink = '/dbs/' + self.created_db['id'] + '/colls/' + created_collection['id'] + '/'
        query = 'SELECT * from c'
        query_iterable = self.client.QueryItems(collectionLink, query, query_options)

        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], 'myId')

    def test_query_change_feed(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        collection_link = created_collection['_self']
        # The test targets partition #3
        pkRangeId = "3"

        # Read change feed with passing options
        query_iterable = self.client.QueryItemsChangeFeed(collection_link)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)

        # Read change feed without specifying partition key range ID
        options = {}
        query_iterable = self.client.QueryItemsChangeFeed(collection_link, options)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)

        # Read change feed from current should return an empty list
        options['partitionKeyRangeId'] = pkRangeId
        query_iterable = self.client.QueryItemsChangeFeed(collection_link, options)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in self.client.last_response_headers)
        self.assertNotEquals(self.client.last_response_headers['etag'], '')

        # Read change feed from beginning should return an empty list
        options['isStartFromBeginning'] = True
        query_iterable = self.client.QueryItemsChangeFeed(collection_link, options)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in self.client.last_response_headers)
        continuation1 = self.client.last_response_headers['etag']
        self.assertNotEquals(continuation1, '')

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id':'doc1'}
        self.client.CreateItem(collection_link, document_definition)
        query_iterable = self.client.QueryItemsChangeFeed(collection_link, options)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 1)
        self.assertEqual(iter_list[0]['id'], 'doc1')
        self.assertTrue('etag' in self.client.last_response_headers)
        continuation2 = self.client.last_response_headers['etag']
        self.assertNotEquals(continuation2, '')
        self.assertNotEquals(continuation2, continuation1)

        # Create two new documents. Verify that change feed contains the 2 new documents
        # with page size 1 and page size 100
        document_definition = {'pk': 'pk', 'id':'doc2'}
        self.client.CreateItem(collection_link, document_definition)
        document_definition = {'pk': 'pk', 'id':'doc3'}
        self.client.CreateItem(collection_link, document_definition)
        options['isStartFromBeginning'] = False
        
        for pageSize in [1, 100]:
            # verify iterator
            options['continuation'] = continuation2
            options['maxItemCount'] = pageSize
            query_iterable = self.client.QueryItemsChangeFeed(collection_link, options)
            it = query_iterable.__iter__()
            expected_ids = 'doc2.doc3.'
            actual_ids = ''
            for item in it:
                actual_ids += item['id'] + '.'    
            self.assertEqual(actual_ids, expected_ids)

            # verify fetch_next_block
            # the options is not copied, therefore it need to be restored
            options['continuation'] = continuation2
            query_iterable = self.client.QueryItemsChangeFeed(collection_link, options)
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
        options['isStartFromBeginning'] = True
        options['continuation'] = None
        query_iterable = self.client.QueryItemsChangeFeed(collection_link, options)
        expected_ids = ['doc1', 'doc2', 'doc3']
        it = query_iterable.__iter__()
        for i in range(0, len(expected_ids)):
            doc = next(it)
            self.assertEquals(doc['id'], expected_ids[i])
        self.assertTrue('etag' in self.client.last_response_headers)
        continuation3 = self.client.last_response_headers['etag']

        # verify reading empty change feed 
        options['continuation'] = continuation3
        query_iterable = self.client.QueryItemsChangeFeed(collection_link, options)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)

    def test_populate_query_metrics (self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        document_definition = {'pk': 'pk', 'id':'myId'}
        self.client.CreateItem(created_collection['_self'], document_definition)

        query_options = {'partitionKey': 'pk',
                         'populateQueryMetrics': True}
        query = 'SELECT * from c'
        query_iterable = self.client.QueryItems(created_collection['_self'], query, query_options)

        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], 'myId')

        METRICS_HEADER_NAME = 'x-ms-documentdb-query-metrics'
        self.assertTrue(METRICS_HEADER_NAME in self.client.last_response_headers)
        metrics_header = self.client.last_response_headers[METRICS_HEADER_NAME]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        self.assertTrue(len(metrics) > 1)
        self.assertTrue(all(['=' in x for x in metrics]))

if __name__ == "__main__":
    unittest.main()