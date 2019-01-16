import unittest
import uuid
import azure.cosmos.cosmos_client_connection as cosmos_client_connection
import azure.cosmos.documents as documents
import test.test_config as test_config

class QueryTest(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy 
    testDbName = 'testDatabase'

    @classmethod
    def cleanUpTestDatabase(cls):
        global client
        client = cosmos_client_connection.CosmosClientConnection(cls.host,
                                                {'masterKey': cls.masterKey}, cls.connectionPolicy)
        query_iterable = client.QueryDatabases('SELECT * FROM root r WHERE r.id=\'' + cls.testDbName + '\'')
        it = iter(query_iterable)

        test_db = next(it, None)
        if test_db is not None:
            client.DeleteDatabase("/dbs/" + cls.testDbName + "/")
            """ change """

    @classmethod
    def tearDownClass(cls):
        QueryTest.cleanUpTestDatabase()

    @classmethod
    def setUp(cls):
        global created_db
        QueryTest.cleanUpTestDatabase()
        created_db = client.CreateDatabase({ 'id': cls.testDbName })

    def test_first_and_last_slashes_trimmed_for_query_string (self):
        testCollectionName = 'testCollection ' + str(uuid.uuid4())
        collection_definition = { 'id': testCollectionName, 'partitionKey': {'paths': ['/pk'],'kind': 'Hash'} }
        collection_options = { 'offerThroughput': 10100 }
        created_collection = client.CreateContainer(created_db['_self'], collection_definition, collection_options)

        document_definition = {'pk': 'pk', 'id':'myId'}
        client.CreateItem(created_collection['_self'], document_definition)

        query_options = {'partitionKey': 'pk'}
        collectionLink = '/dbs/' + self.testDbName + '/colls/' + testCollectionName + '/'
        query = 'SELECT * from c'
        query_iterable = client.QueryItems(collectionLink, query, query_options)

        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], 'myId')

    def test_query_change_feed(self):
        testCollectionName = 'testCollection ' + str(uuid.uuid4())
        collection_definition = { 'id': testCollectionName, 'partitionKey': {'paths': ['/pk'],'kind': 'Hash'} }
        collection_options = { 'offerThroughput': 30000 }
        created_collection = client.CreateContainer(created_db['_self'], collection_definition, collection_options)

        collection_link = created_collection['_self']
        # The test targets partition #3
        pkRangeId = "3"

        # Read change feed with passing options
        query_iterable = client.QueryItemsChangeFeed(collection_link)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)

        # Read change feed without specifying partition key range ID
        options = {}
        query_iterable = client.QueryItemsChangeFeed(collection_link, options)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)

        # Read change feed from current should return an empty list
        options['partitionKeyRangeId'] = pkRangeId
        query_iterable = client.QueryItemsChangeFeed(collection_link, options)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in client.last_response_headers)
        self.assertNotEquals(client.last_response_headers['etag'], '')

        # Read change feed from beginning should return an empty list
        options['isStartFromBeginning'] = True
        query_iterable = client.QueryItemsChangeFeed(collection_link, options)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in client.last_response_headers)
        continuation1 = client.last_response_headers['etag']
        self.assertNotEquals(continuation1, '')

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id':'doc1'}
        client.CreateItem(collection_link, document_definition)
        query_iterable = client.QueryItemsChangeFeed(collection_link, options)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 1)
        self.assertEqual(iter_list[0]['id'], 'doc1')
        self.assertTrue('etag' in client.last_response_headers)
        continuation2 = client.last_response_headers['etag']
        self.assertNotEquals(continuation2, '')
        self.assertNotEquals(continuation2, continuation1)

        # Create two new documents. Verify that change feed contains the 2 new documents
        # with page size 1 and page size 100
        document_definition = {'pk': 'pk', 'id':'doc2'}
        client.CreateItem(collection_link, document_definition)
        document_definition = {'pk': 'pk', 'id':'doc3'}
        client.CreateItem(collection_link, document_definition)
        options['isStartFromBeginning'] = False
        
        for pageSize in [1, 100]:
            # verify iterator
            options['continuation'] = continuation2
            options['maxItemCount'] = pageSize
            query_iterable = client.QueryItemsChangeFeed(collection_link, options)
            it = query_iterable.__iter__()
            expected_ids = 'doc2.doc3.'
            actual_ids = ''
            for item in it:
                actual_ids += item['id'] + '.'    
            self.assertEqual(actual_ids, expected_ids)

            # verify fetch_next_block
            # the options is not copied, therefore it need to be restored
            options['continuation'] = continuation2
            query_iterable = client.QueryItemsChangeFeed(collection_link, options)
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
        query_iterable = client.QueryItemsChangeFeed(collection_link, options)
        expected_ids = ['doc1', 'doc2', 'doc3']
        it = query_iterable.__iter__()
        for i in range(0, len(expected_ids)):
            doc = next(it)
            self.assertEquals(doc['id'], expected_ids[i])
        self.assertTrue('etag' in client.last_response_headers)
        continuation3 = client.last_response_headers['etag']

        # verify reading empty change feed 
        options['continuation'] = continuation3
        query_iterable = client.QueryItemsChangeFeed(collection_link, options)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)

    def test_populate_query_metrics (self):
        testCollectionName = 'testCollection ' + str(uuid.uuid4())
        collection_definition = { 'id': testCollectionName, 'partitionKey': {'paths': ['/pk'],'kind': 'Hash'} }
        collection_options = { 'offerThroughput': 10100 }
        created_collection = client.CreateContainer(created_db['_self'], collection_definition, collection_options)

        document_definition = {'pk': 'pk', 'id':'myId'}
        client.CreateItem(created_collection['_self'], document_definition)

        query_options = {'partitionKey': 'pk',
                         'populateQueryMetrics': True}
        collectionLink = '/dbs/' + self.testDbName + '/colls/' + testCollectionName + '/'
        query = 'SELECT * from c'
        query_iterable = client.QueryItems(collectionLink, query, query_options)

        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], 'myId')

        METRICS_HEADER_NAME = 'x-ms-documentdb-query-metrics'
        self.assertTrue(METRICS_HEADER_NAME in client.last_response_headers)
        metrics_header = client.last_response_headers[METRICS_HEADER_NAME]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        self.assertTrue(len(metrics) > 1)
        self.assertTrue(all(['=' in x for x in metrics]))

if __name__ == "__main__":
    unittest.main()