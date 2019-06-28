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
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import query_iterable
import azure.cosmos.base as base
from six.moves import xrange
import test_config

pytestmark = pytest.mark.cosmosEmulator

#IMPORTANT NOTES:
  
#      Most test cases in this file create collections in your Azure Cosmos account.
#      Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.
  
#      To Run the test, replace the two member fields (masterKey and host) with values 
#   associated with your Azure Cosmos account.

@pytest.mark.usefixtures("teardown")
class CrossPartitionTopOrderByTest(unittest.TestCase):
    """Orderby Tests.
    """
    
    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy

    @classmethod
    def setUpClass(cls):
        # creates the database, collection, and insert all the documents
        # we will gain some speed up in running the tests by creating the database, collection and inserting all the docs only once
        
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
            
        cls.client = cosmos_client.CosmosClient(cls.host, {'masterKey': cls.masterKey}, cls.connectionPolicy)
        cls.created_db = test_config._test_config.create_database_if_not_exist(cls.client)
        cls.created_collection = CrossPartitionTopOrderByTest.create_collection(cls.client, cls.created_db)
        cls.collection_link = cls.GetDocumentCollectionLink(cls.created_db, cls.created_collection)

        # create a document using the document definition
        cls.document_definitions = []
        for i in xrange(20):
            d = {'id' : str(i),
                 'name': 'sample document',
                 'spam': 'eggs' + str(i),
                 'cnt': i,
                 'key': 'value',
                 'spam2': 'eggs' + str(i) if (i == 3) else i,
                 'boolVar': (i % 2 == 0),
                 'number': 1.1 * i
                 }
            cls.document_definitions.append(d)

        CrossPartitionTopOrderByTest.insert_doc()

    @classmethod
    def tearDownClass(cls):
        cls.client.DeleteContainer(cls.collection_link)

    def setUp(self):
        
        # sanity check:
        partition_key_ranges = list(self.client._ReadPartitionKeyRanges(self.collection_link))
        self.assertGreaterEqual(len(partition_key_ranges), 5)
        
        # sanity check: read documents after creation
        queried_docs = list(self.client.ReadItems(self.collection_link))
        self.assertEqual(
            len(queried_docs),
            len(self.document_definitions),
            'create should increase the number of documents')    

    
    def test_orderby_query(self):        
        # test a simply order by query

        # an order by query
        query = {
                'query': 'SELECT * FROM root r order by r.spam',
        }    
        
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]
    
        # validates the results size and order
        self.execute_query_and_validate_results(query, options, expected_ordered_ids)

    def test_orderby_query_as_string(self):
        # test a simply order by query as string

        # an order by query
        query = 'SELECT * FROM root r order by r.spam'
        
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]
    
        # validates the results size and order
        self.execute_query_and_validate_results(query, options, expected_ordered_ids)

    def test_orderby_asc_query(self):        
        # test an order by query with explicit ascending ordering

        # an ascending order by query (ascending explicitly mentioned in the query)
        query = {
                'query': 'SELECT * FROM root r order by r.spam ASC',
        }    
        
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]
    
        # validates the results size and order
        self.execute_query_and_validate_results(query, options, expected_ordered_ids)

    def test_orderby_desc_query(self):        
        # test an order by query with explicit descending ordering

        # a descending order by query
        query = {
                'query': 'SELECT * FROM root r order by r.spam DESC',
        }    
        
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key, reverse=True)]
    
        # validates the results size and order
        self.execute_query_and_validate_results(query, options, expected_ordered_ids)

    def test_orderby_top_query(self):        
        # test an order by query combined with top
        
        top_count = 9
        # sanity check  
        self.assertLess(top_count, len(self.document_definitions)) 
        
        # an order by query with top, total existing docs more than requested top count   
        query = {
                 'query': 'SELECT top %d * FROM root r order by r.spam' % top_count
        }    
        
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)[:top_count]]
    
        self.execute_query_and_validate_results(query, options, expected_ordered_ids)

    def test_orderby_top_query_less_results_than_top_counts(self):        
        # test an order by query combined with top. where top is greater than the total number of docs

        top_count = 30
        # sanity check  
        self.assertGreater(top_count, len(self.document_definitions)) 
        
        # an order by query with top, total existing docs less than requested top count   
        query = {
                 'query': 'SELECT top %d * FROM root r order by r.spam' % top_count
        }  
        
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]
    
        self.execute_query_and_validate_results(query, options, expected_ordered_ids)

    def test_top_query(self):
        # test a simple top query without order by. 
        # The rewrittenQuery in the query execution info responded by backend will be empty
       
        partition_key_ranges = list(self.client._ReadPartitionKeyRanges(self.collection_link))
        
        docs_by_partition_key_range_id = self.find_docs_by_partition_key_range_id()
        
        # find the first two non-empty target partition key ranges
        cnt = 0
        first_two_ranges_results = []
        for r in partition_key_ranges:
            if cnt >= 2:
                break
            p_id = r['id']
            if len(docs_by_partition_key_range_id[p_id]) > 0:
                first_two_ranges_results.extend(docs_by_partition_key_range_id[p_id])
                cnt += 1
        
        # sanity checks
        self.assertEqual(cnt, 2)
        self.assertLess(2, len(partition_key_ranges))
 
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        # sanity check  
        self.assertLess(len(first_two_ranges_results), len(self.document_definitions)) 
        self.assertGreater(len(first_two_ranges_results), 1) 

        expected_ordered_ids = [d['id'] for d in first_two_ranges_results]

        # a top query, the results will be sorted based on the target partition key range  
        query = {
                 'query': 'SELECT top %d * FROM root r' % len(expected_ordered_ids)
        }
        self.execute_query_and_validate_results(query, options, expected_ordered_ids)
        
    def test_top_query_as_string(self):
        # test a simple top query without order by. 
        # The rewrittenQuery in the query execution info responded by backend will be empty
       
        partition_key_ranges = list(self.client._ReadPartitionKeyRanges(self.collection_link))
        
        docs_by_partition_key_range_id = self.find_docs_by_partition_key_range_id()
        
        # find the first two non-empty target partition key ranges
        cnt = 0
        first_two_ranges_results = []
        for r in partition_key_ranges:
            if cnt >= 2:
                break
            p_id = r['id']
            if len(docs_by_partition_key_range_id[p_id]) > 0:
                first_two_ranges_results.extend(docs_by_partition_key_range_id[p_id])
                cnt += 1
        
        # sanity checks
        self.assertEqual(cnt, 2)
        self.assertLess(2, len(partition_key_ranges))
 
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        # sanity check  
        self.assertLess(len(first_two_ranges_results), len(self.document_definitions)) 
        self.assertGreater(len(first_two_ranges_results), 1) 

        expected_ordered_ids = [d['id'] for d in first_two_ranges_results]

        # a top query, the results will be sorted based on the target partition key range  
        query = 'SELECT top %d * FROM root r' % len(expected_ordered_ids)
        self.execute_query_and_validate_results(query, options, expected_ordered_ids)
        
    def test_parametrized_top_query(self):
        # test a simple parameterized query without order by. 
        # The rewrittenQuery in the query execution info responded by backend will be empty
       
        partition_key_ranges = list(self.client._ReadPartitionKeyRanges(self.collection_link))
        
        docs_by_partition_key_range_id = self.find_docs_by_partition_key_range_id()
        
        # find the first two non-empty target partition key ranges
        cnt = 0
        first_two_ranges_results = []
        for r in partition_key_ranges:
            if cnt >= 2:
                break
            p_id = r['id']
            if len(docs_by_partition_key_range_id[p_id]) > 0:
                first_two_ranges_results.extend(docs_by_partition_key_range_id[p_id])
                cnt += 1
        
        # sanity checks
        self.assertEqual(cnt, 2)
        self.assertLess(2, len(partition_key_ranges))
 
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        # sanity check  
        self.assertLess(len(first_two_ranges_results), len(self.document_definitions)) 
        self.assertGreater(len(first_two_ranges_results), 1) 

        expected_ordered_ids = [d['id'] for d in first_two_ranges_results]

        # a top query, the results will be sorted based on the target partition key range  
        query = {
                 'query': 'SELECT top @n * FROM root r',
                 
                    "parameters": [          
                                    {"name": "@n", "value": len(expected_ordered_ids)}
                                ] 
        }
        self.execute_query_and_validate_results(query, options, expected_ordered_ids)

    def test_orderby_query_with_parametrized_top(self):
        # test an order by query combined with parametrized top
        
        top_count = 9
        # sanity check  
        self.assertLess(top_count, len(self.document_definitions)) 

        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)[:top_count]]
    
        # a parametrized top order by query
        query = {
                 'query': 'SELECT top @n * FROM root r order by r.spam',
                 
                    "parameters": [          
                                    {"name": "@n", "value": top_count}
                                ] 
        }
    
        self.execute_query_and_validate_results(query, options, expected_ordered_ids)
        
    def test_orderby_query_with_parametrized_predicate(self):
        # test an order by query combined with parametrized predicate

        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
        # an order by query with parametrized predicate
        query = {
                 'query': 'SELECT * FROM root r where r.cnt > @cnt order by r.spam',
                  
                    "parameters": [          
                                    {"name": "@cnt", "value": 5}
                                ]
                 
        }
    
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key) if r['cnt'] > 5]
    
        self.execute_query_and_validate_results(query, options, expected_ordered_ids)
        
    def test_orderby_query_noncomparable_orderby_item(self):        
        # test orderby with different order by item type
                
        # an order by query
        query = {
                'query': 'SELECT * FROM root r order by r.spam2 DESC',
        }    
        
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        def get_order_by_key(r):
            return r['id']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]

        # validates the results size and order
        try:
            self.execute_query_and_validate_results(query, options, expected_ordered_ids)
            self.fail('non comparable order by items did not result in failure.')
        except ValueError as e:
            self.assertTrue(e.args[0] == "Expected String, but got Number." or e.message == "Expected Number, but got String.")
            
    def test_orderby_integer_query(self):        
        # an order by integer query
        query = {
                'query': 'SELECT * FROM root r order by r.cnt',
        }    
        
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        def get_order_by_key(r):
            return r['cnt']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]
    
        # validates the results size and order
        self.execute_query_and_validate_results(query, options, expected_ordered_ids)      
        
    def test_orderby_floating_point_number_query(self):        
        # an orderby by floating point number query
        query = {
                'query': 'SELECT * FROM root r order by r.number',
        }    
        
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        def get_order_by_key(r):
            return r['number']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]
    
        # validates the results size and order
        self.execute_query_and_validate_results(query, options, expected_ordered_ids)            
          
    def test_orderby_boolean_query(self):        
        # an orderby by floating point number query
        query = {
                'query': 'SELECT * FROM root r order by r.boolVar',
        }    
        
        options = {} 
        options['enableCrossPartitionQuery'] = True
        options['maxItemCount'] = 2
    
        result_iterable = self.client.QueryItems(self.collection_link, query, options)
        results = list(result_iterable)
        # validates the results size and order

        self.assertEqual(len(results), len(self.document_definitions))

        # false values before true values
        index = 0
        while index < len(results):
            if results[index]['boolVar']:
                break
            
            self.assertTrue(int(results[index]['id']) % 2 == 1)
            index = index + 1
        
        while index < len(results):
            self.assertTrue(results[index]['boolVar'])
            self.assertTrue(int(results[index]['id']) % 2 == 0)
            index = index + 1
            
    def find_docs_by_partition_key_range_id(self):
        query = {
                 'query': 'SELECT * FROM root r'
        }  
        
        partition_key_range = list(self.client._ReadPartitionKeyRanges(self.collection_link))
        docs_by_partition_key_range_id = {}
        for r in partition_key_range:
            options = {} 
            
            path = base.GetPathFromLink(self.collection_link, 'docs')
            collection_id = base.GetResourceIdOrFullNameFromLink(self.collection_link)
            def fetch_fn(options):
                return self.client.QueryFeed(path, collection_id, query, options, r['id'])
            docResultsIterable = query_iterable.QueryIterable(self.client, query, options, fetch_fn, self.collection_link)
            
            docs = list(docResultsIterable)
            self.assertFalse(r['id'] in docs_by_partition_key_range_id)
            docs_by_partition_key_range_id[r['id']] = docs
        return docs_by_partition_key_range_id

    def execute_query_and_validate_results(self, query, options, expected_ordered_ids):        
        # executes the query and validates the results against the expected results
        page_size = options['maxItemCount']

        result_iterable = self.client.QueryItems(self.collection_link, query, options)
        
        self.assertTrue(isinstance(result_iterable, query_iterable.QueryIterable))
        
        ######################################
        # test next() behavior
        ######################################
        it = result_iterable.__iter__()
        def invokeNext():
            return next(it)
                    
        # validate that invocations of next() produces the same results as expected_ordered_ids
        for i in xrange(len(expected_ordered_ids)):
            item = invokeNext()
            self.assertEqual(item['id'], expected_ordered_ids[i])
       
        # after the result set is exhausted, invoking next must raise a StopIteration exception
        self.assertRaises(StopIteration, invokeNext)

        ######################################
        # test fetch_next_block() behavior
        ######################################
        results = {}
        cnt = 0
        while True:
            fetched_res = result_iterable.fetch_next_block()
            fetched_size = len(fetched_res)
            
            for item in fetched_res:
                self.assertEqual(item['id'], expected_ordered_ids[cnt])
                results[cnt] = item
                cnt = cnt + 1
            if (cnt < len(expected_ordered_ids)):
                self.assertEqual(fetched_size, page_size, "page size")
            else:
                if cnt == len(expected_ordered_ids):
                    self.assertTrue(fetched_size <= page_size, "last page size")
                    break
                else:
                    #cnt > expected_number_of_results
                    self.fail("more results than expected")
        
        # validate the number of collected results
        self.assertEqual(len(results), len(expected_ordered_ids))
        
        # no more results will be returned
        self.assertEqual(result_iterable.fetch_next_block(), [])

    @classmethod
    def create_collection(self, client, created_db):

        collection_definition = {  
           'id': 'orderby_tests collection ' + str(uuid.uuid4()),
           'indexingPolicy':{  
              'includedPaths':[  
                 {  
                    'path':'/',
                    'indexes':[  
                       {  
                          'kind':'Range',
                          'dataType':'Number'
                       },
                       {  
                          'kind':'Range',
                          'dataType':'String'
                       }
                    ]
                 }
              ]
           },
           'partitionKey':{  
              'paths':[  
                 '/id'
              ],
              'kind':documents.PartitionKind.Hash
           }
        }
        
        collection_options = { 'offerThroughput': 30000 }

        created_collection = client.CreateContainer(self.GetDatabaseLink(created_db),
                                collection_definition, 
                                collection_options)

        return created_collection

    @classmethod
    def insert_doc(cls):
        # create a document using the document definition
        created_docs = []
        for d in cls.document_definitions:

            created_doc = cls.client.CreateItem(cls.collection_link, d)
            created_docs.append(created_doc)
            
        return created_docs
    
    @classmethod
    def GetDatabaseLink(cls, database, is_name_based=True):
        if is_name_based:
            return 'dbs/' + database['id']
        else:
            return database['_self']

    @classmethod
    def GetDocumentCollectionLink(cls, database, document_collection, is_name_based=True):
        if is_name_based:
            return cls.GetDatabaseLink(database) + '/colls/' + document_collection['id']
        else:
            return document_collection['_self']

    @classmethod
    def GetDocumentLink(cls, database, document_collection, document, is_name_based=True):
        if is_name_based:
            return cls.GetDocumentCollectionLink(database, document_collection) + '/docs/' + document['id']
        else:
            return document['_self']

if __name__ == "__main__":
    
    
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()