import unittest
import pydocumentdb.document_client as document_client
import pydocumentdb.documents as documents
import test.test_config as test_config

class QueryTest(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    testDbName = 'testDatabase'
    testCollectionName = 'testCollection'

    @classmethod
    def cleanUpTestDatabase(cls):
        global client
        client = document_client.DocumentClient(cls.host,
                                                {'masterKey': cls.masterKey})
        query_iterable = client.QueryDatabases('SELECT * FROM root r WHERE r.id=\'' + cls.testDbName + '\'')
        it = iter(query_iterable)

        test_db = next(it, None)
        if test_db is not None:
            client.DeleteDatabase("/dbs/" + cls.testDbName + "/")
            """ change """

    @classmethod
    def tearDownClass(cls):
        QueryTest.cleanUpTestDatabase()

    def setUp(self):
        global created_collection

        QueryTest.cleanUpTestDatabase()
        created_db = client.CreateDatabase({ 'id': self.testDbName })

        collection_definition = { 'id': self.testCollectionName, 'partitionKey': {'paths': ['/pk'],'kind': 'Hash'} }
        collection_options = { 'offerThroughput': 10100 }
        created_collection = client.CreateCollection(created_db['_self'], collection_definition, collection_options)

        document_definition = {'pk': 'pk', 'id':'myId'}
        created_doc = client.CreateDocument(created_collection['_self'], document_definition)

    def test_first_and_last_slashes_trimmed_for_query_string (self):
        query_options = {'partitionKey': 'pk'}
        collectionLink = '/dbs/' + self.testDbName + '/colls/' + self.testCollectionName + '/'
        query = 'SELECT * from ' + self.testCollectionName
        query_iterable = client.QueryDocuments(collectionLink, query, query_options)

        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], 'myId')

    def test_populate_query_metrics (self):
        query_options = {'partitionKey': 'pk',
                         'populateQueryMetrics': True}
        collectionLink = '/dbs/' + self.testDbName + '/colls/' + self.testCollectionName + '/'
        query = 'SELECT * from ' + self.testCollectionName
        query_iterable = client.QueryDocuments(collectionLink, query, query_options)

        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], 'myId')

        METRICS_HEADER_NAME = 'x-ms-documentdb-query-metrics'
        self.assertTrue(METRICS_HEADER_NAME in client.last_response_headers)
        metrics_header = client.last_response_headers[METRICS_HEADER_NAME]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        self.assertTrue(len(metrics) > 1)
        self.assertTrue(all(['=' in x for x in metrics]))
