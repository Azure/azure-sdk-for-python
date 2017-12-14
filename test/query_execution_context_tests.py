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
from six.moves import xrange
import pydocumentdb.documents as documents
import pydocumentdb.document_client as document_client
from pydocumentdb.execution_context import base_execution_context as base_execution_context
import pydocumentdb.base as base
import test.test_config as test_config

#IMPORTANT NOTES:
  
#      Most test cases in this file create collections in your Azure Cosmos DB account.
#      Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.
  
#      To Run the test, replace the two member fields (masterKey and host) with values 
#   associated with your Azure Cosmos DB account.

class QueryExecutionContextEndToEndTests(unittest.TestCase):
    """Routing Map Functionalities end to end Tests.
    """

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    testDbName = 'sample database'

    @classmethod
    def cleanUpTestDatabase(cls):
        client = document_client.DocumentClient(cls.host, {'masterKey': cls.masterKey})
        query_iterable = client.QueryDatabases('SELECT * FROM root r WHERE r.id=\'' + cls.testDbName + '\'')
        it = iter(query_iterable)
        
        test_db = next(it, None)
        if test_db is not None:
            client.DeleteDatabase(test_db['_self'])

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos DB account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    @classmethod
    def tearDownClass(cls):
        QueryExecutionContextEndToEndTests.cleanUpTestDatabase();

    def setUp(self):
        QueryExecutionContextEndToEndTests.cleanUpTestDatabase();
        
        self.client = document_client.DocumentClient(QueryExecutionContextEndToEndTests.host, {'masterKey': QueryExecutionContextEndToEndTests.masterKey})
        self.created_db = self.client.CreateDatabase({ 'id': 'sample database' })        
        self.created_collection = self.create_collection(self.client, self.created_db)
        self.collection_link = self.GetDocumentCollectionLink(self.created_db, self.created_collection)
        
        # sanity check:
        partition_key_ranges = list(self.client._ReadPartitionKeyRanges(self.collection_link))
        self.assertGreaterEqual(len(partition_key_ranges), 1)

        # create a document using the document definition
        self.document_definitions = []
        for i in xrange(20):
            d = {'id' : str(i),
                 'name': 'sample document',
                 'spam': 'eggs' + str(i),
                 'key': 'value'}
            self.document_definitions.append(d)
        self.insert_doc(self.client, self.created_db, self.collection_link, self.document_definitions)

        # sanity check: read documents after creation
        queried_docs = list(self.client.ReadDocuments(self.collection_link))
        self.assertEqual(
            len(queried_docs),
            len(self.document_definitions),
            'create should increase the number of documents')    

    def test_no_query_default_execution_context(self):        
                    
        options = {}    
        options['maxItemCount'] = 2

        self._test_default_execution_context(options, None, 20)

    def test_no_query_default_execution_context_with_small_last_page(self):        
                    
        options = {}    
        options['maxItemCount'] = 3

        self._test_default_execution_context(options, None, 20)

    def test_simple_query_default_execution_context(self):        
            
        query = {
                'query': 'SELECT * FROM root r WHERE r.id != @id',
                'parameters': [
                    { 'name': '@id', 'value': '5'}
                ]
        }
        
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        res = self.client.QueryDocuments(self.collection_link, query, options)
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
                return self.client.QueryFeed(path,
                                        collection_id,
                                        query,
                                        options)
        
        ######################################
        # test next() behavior
        ######################################
        ex = base_execution_context._DefaultQueryExecutionContext(self.client, options, fetch_fn)
        
        it = ex.__iter__()
        def invokeNext():
            return next(it)
                    
        results = {}            
        # validate that invocations of next() produces the same results as expected
        for i in xrange(expected_number_of_results):
            item = invokeNext()
            results[item['id']] = item
       
        self.assertEqual(len(results), expected_number_of_results)
       
        # after the result set is exhausted, invoking next must raise a StopIteration exception
        self.assertRaises(StopIteration, invokeNext)

        ######################################
        # test fetch_next_block() behavior
        ######################################
        ex = base_execution_context._DefaultQueryExecutionContext(self.client, options, fetch_fn)
        
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
        
    def create_collection(self, client, created_db):

        collection_definition = {   'id': 'sample collection', 
                                    'partitionKey': 
                                    {   
                                        'paths': ['/id'],
                                        'kind': documents.PartitionKind.Hash
                                    }
                                }
        
        collection_options = {  }

        created_collection = client.CreateCollection(self.GetDatabaseLink(created_db),
                                collection_definition, 
                                collection_options)

        return created_collection

    def insert_doc(self, client, created_db, collection_link, document_definitions):
        # create a document using the document definition
        created_docs = []
        for d in document_definitions:

            created_doc = client.CreateDocument(collection_link, d)
            created_docs.append(created_doc)
                        
        return created_docs

    def GetDatabaseLink(self, database, is_name_based=True):
        if is_name_based:
            return 'dbs/' + database['id']
        else:
            return database['_self']

    def GetDocumentCollectionLink(self, database, document_collection, is_name_based=True):
        if is_name_based:
            return self.GetDatabaseLink(database) + '/colls/' + document_collection['id']
        else:
            return document_collection['_self']
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()