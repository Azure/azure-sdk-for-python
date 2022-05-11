#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import unittest
import uuid
import pytest
from six.moves import xrange
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos._execution_context import base_execution_context as base_execution_context
import azure.cosmos._base as base
import test_config
from azure.cosmos.partition_key import PartitionKey

pytestmark = pytest.mark.cosmosEmulator

# IMPORTANT NOTES:

#      Most test cases in this file create collections in your Azure Cosmos account.
#      Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.
  
#      To Run the test, replace the two member fields (masterKey and host) with values 
#   associated with your Azure Cosmos account.

@pytest.mark.usefixtures("teardown")
class QueryExecutionContextEndToEndTests(unittest.TestCase):
    """Routing Map Functionalities end to end Tests.
    """

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(QueryExecutionContextEndToEndTests.host,
                                                QueryExecutionContextEndToEndTests.masterKey,
                                                consistency_level="Session",
                                                connection_policy=QueryExecutionContextEndToEndTests.connectionPolicy)
        cls.created_db = cls.client.create_database_if_not_exists(test_config._test_config.TEST_DATABASE_ID)
        cls.created_collection = cls.created_db.create_container(
            id='query_execution_context_tests_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        cls.document_definitions = []

        # create a document using the document definition
        for i in xrange(20):
            d = {'id': str(i),
                 'name': 'sample document',
                 'spam': 'eggs' + str(i),
                 'key': 'value'}
            cls.document_definitions.append(d)
        cls.insert_doc(cls.document_definitions)

    @classmethod
    def tearDownClass(cls):
        cls.created_db.delete_container(container=cls.created_collection)

    def setUp(self):
        # sanity check:
        partition_key_ranges = list(self.client.client_connection._ReadPartitionKeyRanges(
            self.GetDocumentCollectionLink(self.created_db, self.created_collection)))
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
                    { 'name': '@id', 'value': '5'}
                ]
        } 
        
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 3
    
        self._test_default_execution_context(options, query, 19)

    def _test_default_execution_context(self, options, query, expected_number_of_results):
        
        page_size = options['maxItemCount']
        collection_link = self.GetDocumentCollectionLink(self.created_db, self.created_collection)
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
        for _ in xrange(expected_number_of_results):
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
        while True:
            fetched_res = ex.fetch_next_block()
            fetched_size = len(fetched_res)
            
            for item in fetched_res:
                results[item['id']] = item
            cnt += fetched_size
            
            if (cnt < expected_number_of_results):
                # backend may not necessarily return exactly page_size of results
                self.assertEqual(fetched_size, page_size, "page size")
            else:
                if cnt == expected_number_of_results:
                    self.assertTrue(fetched_size <= page_size, "last page size")
                    break
                else:
                    #cnt > expected_number_of_results
                    self.fail("more results than expected")
        
        # validate the number of collected results
        self.assertEqual(len(results), expected_number_of_results)
        
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

    def GetDatabaseLink(self, database):
            return 'dbs/' + database.id

    def GetDocumentCollectionLink(self, database, document_collection):
            return self.GetDatabaseLink(database) + '/colls/' + document_collection.id


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
