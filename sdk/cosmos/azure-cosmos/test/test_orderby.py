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
from azure.core.paging import ItemPaged
from azure.cosmos.partition_key import PartitionKey
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import _query_iterable as query_iterable
import azure.cosmos._base as base
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

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, "Session",
                                                connection_policy=cls.connectionPolicy)
        cls.created_db = cls.client.create_database_if_not_exists(test_config._test_config.TEST_DATABASE_ID)
        cls.created_collection = cls.created_db.create_container(
            id='orderby_tests collection ' + str(uuid.uuid4()),
            indexing_policy={
                'includedPaths': [
                    {
                        'path': '/',
                        'indexes': [
                            {
                                'kind': 'Range',
                                'dataType': 'Number'
                            },
                            {
                                'kind': 'Range',
                                'dataType': 'String'
                            }
                        ]
                    }
                ]
            },
            partition_key=PartitionKey(path='/id'),
            offer_throughput=30000)

        cls.collection_link = cls.GetDocumentCollectionLink(cls.created_db, cls.created_collection)

        # create a document using the document definition
        cls.document_definitions = []
        for i in range(20):
            d = {'id': str(i),
                 'name': 'sample document',
                 'spam': 'eggs' + str(i),
                 'cnt': i,
                 'key': 'value',
                 'spam2': 'eggs' + str(i) if (i == 3) else i,
                 'boolVar': (i % 2 == 0),
                 'number': 1.1 * i
                 }
            cls.created_collection.create_item(d)
            cls.document_definitions.append(d)

    def test_orderby_query(self):
        # test a simply order by query

        # an order by query
        query = {
                'query': 'SELECT * FROM root r order by r.spam',
        }    
        
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]
    
        # validates the results size and order
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    def test_orderby_query_as_string(self):
        # test a simply order by query as string

        # an order by query
        query = 'SELECT * FROM root r order by r.spam'
        
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]
    
        # validates the results size and order
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    def test_orderby_asc_query(self):        
        # test an order by query with explicit ascending ordering

        # an ascending order by query (ascending explicitly mentioned in the query)
        query = {
                'query': 'SELECT * FROM root r order by r.spam ASC',
        }    
        
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]
    
        # validates the results size and order
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    def test_orderby_desc_query(self):        
        # test an order by query with explicit descending ordering

        # a descending order by query
        query = {
                'query': 'SELECT * FROM root r order by r.spam DESC',
        }    
        
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key, reverse=True)]
    
        # validates the results size and order
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    def test_orderby_top_query(self):        
        # test an order by query combined with top
        
        top_count = 9
        # sanity check  
        self.assertLess(top_count, len(self.document_definitions)) 
        
        # an order by query with top, total existing docs more than requested top count   
        query = {
                 'query': 'SELECT top %d * FROM root r order by r.spam' % top_count # nosec
        }    
        
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)[:top_count]]
    
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    def test_orderby_top_query_less_results_than_top_counts(self):        
        # test an order by query combined with top. where top is greater than the total number of docs

        top_count = 30
        # sanity check  
        self.assertGreater(top_count, len(self.document_definitions)) 
        
        # an order by query with top, total existing docs less than requested top count   
        query = {
                 'query': 'SELECT top %d * FROM root r order by r.spam' % top_count # nosec
        }  
        
        def get_order_by_key(r):
            return r['spam']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]
    
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    def test_top_query(self):
        # test a simple top query without order by. 
        # The rewrittenQuery in the query execution info responded by backend will be empty
       
        partition_key_ranges = list(self.client.client_connection._ReadPartitionKeyRanges(self.collection_link))
        
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
 
        # sanity check
        self.assertLess(len(first_two_ranges_results), len(self.document_definitions)) 
        self.assertGreater(len(first_two_ranges_results), 1) 

        expected_ordered_ids = [d['id'] for d in first_two_ranges_results]

        # a top query, the results will be sorted based on the target partition key range  
        query = {
                 'query': 'SELECT top %d * FROM root r' % len(expected_ordered_ids) # nosec
        }
        self.execute_query_and_validate_results(query, expected_ordered_ids)
        
    def test_top_query_as_string(self):
        # test a simple top query without order by. 
        # The rewrittenQuery in the query execution info responded by backend will be empty
       
        partition_key_ranges = list(self.client.client_connection._ReadPartitionKeyRanges(self.collection_link))
        
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
 
        # sanity check
        self.assertLess(len(first_two_ranges_results), len(self.document_definitions)) 
        self.assertGreater(len(first_two_ranges_results), 1) 

        expected_ordered_ids = [d['id'] for d in first_two_ranges_results]

        # a top query, the results will be sorted based on the target partition key range  
        query = 'SELECT top %d * FROM root r' % len(expected_ordered_ids)   # nosec
        self.execute_query_and_validate_results(query, expected_ordered_ids)
        
    def test_parametrized_top_query(self):
        # test a simple parameterized query without order by. 
        # The rewrittenQuery in the query execution info responded by backend will be empty
       
        partition_key_ranges = list(self.client.client_connection._ReadPartitionKeyRanges(self.collection_link))
        
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
        self.execute_query_and_validate_results(query, expected_ordered_ids)

    def test_orderby_query_with_parametrized_top(self):
        # test an order by query combined with parametrized top
        
        top_count = 9
        # sanity check  
        self.assertLess(top_count, len(self.document_definitions)) 

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
    
        self.execute_query_and_validate_results(query, expected_ordered_ids)
        
    def test_orderby_query_with_parametrized_predicate(self):
        # test an order by query combined with parametrized predicate

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
    
        self.execute_query_and_validate_results(query, expected_ordered_ids)
        
    def test_orderby_query_noncomparable_orderby_item(self):        
        # test orderby with different order by item type
                
        # an order by query
        query = {
                'query': 'SELECT * FROM root r order by r.spam2 DESC',
        }    
        
        def get_order_by_key(r):
            return r['id']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]

        # validates the results size and order
        try:
            self.execute_query_and_validate_results(query, expected_ordered_ids)
            self.fail('non comparable order by items did not result in failure.')
        except ValueError as e:
            self.assertTrue(e.args[0] == "Expected String, but got Number." or e.message == "Expected Number, but got String.")
            
    def test_orderby_integer_query(self):        
        # an order by integer query
        query = {
                'query': 'SELECT * FROM root r order by r.cnt',
        }    
        
        def get_order_by_key(r):
            return r['cnt']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]
    
        # validates the results size and order
        self.execute_query_and_validate_results(query, expected_ordered_ids)
        
    def test_orderby_floating_point_number_query(self):        
        # an orderby by floating point number query
        query = {
                'query': 'SELECT * FROM root r order by r.number',
        }    
        
        def get_order_by_key(r):
            return r['number']
        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)]
    
        # validates the results size and order
        self.execute_query_and_validate_results(query, expected_ordered_ids)
          
    def test_orderby_boolean_query(self):        
        # an orderby by floating point number query
        query = {
                'query': 'SELECT * FROM root r order by r.boolVar',
        }    
        
        result_iterable = self.created_collection.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=2
        )
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
        
        partition_key_range = list(self.client.client_connection._ReadPartitionKeyRanges(self.collection_link))
        docs_by_partition_key_range_id = {}
        for r in partition_key_range:
            options = {} 
            
            path = base.GetPathFromLink(self.collection_link, 'docs')
            collection_id = base.GetResourceIdOrFullNameFromLink(self.collection_link)
            def fetch_fn(options):
                return self.client.client_connection.QueryFeed(path, collection_id, query, options, r['id'])
            docResultsIterable = ItemPaged(
                self.client.client_connection,
                query,
                options,
                fetch_function=fetch_fn,
                collection_link=self.collection_link,
                page_iterator_class=query_iterable.QueryIterable
            )

            docs = list(docResultsIterable)
            self.assertFalse(r['id'] in docs_by_partition_key_range_id)
            docs_by_partition_key_range_id[r['id']] = docs
        return docs_by_partition_key_range_id

    def execute_query_and_validate_results(self, query, expected_ordered_ids):
        # executes the query and validates the results against the expected results
        page_size = 2

        result_iterable = self.created_collection.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=page_size
        )
        
        self.assertTrue(isinstance(result_iterable, ItemPaged))
        self.assertEqual(result_iterable._page_iterator_class, query_iterable.QueryIterable)
        
        ######################################
        # test next() behavior
        ######################################
        it = result_iterable.__iter__()
        def invokeNext():
            return next(it)
                    
        # validate that invocations of next() produces the same results as expected_ordered_ids
        for i in range(len(expected_ordered_ids)):
            item = invokeNext()
            self.assertEqual(item['id'], expected_ordered_ids[i])

        ######################################
        # test by_page() behavior
        ######################################
        results = {}
        cnt = 0
        page_iter = result_iterable.by_page()
        for page in page_iter:
            fetched_res = list(page)
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
        with self.assertRaises(StopIteration):
            next(page_iter)

    @classmethod
    def create_collection(self, client, created_db):
        # type: (CosmosClient, Database) -> Container

        created_collection = created_db.create_container(
            id='orderby_tests collection ' + str(uuid.uuid4()),
            indexing_policy={
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
            partition_key=PartitionKey(path='/id', kind='Hash'),
            offer_throughput=30000
        )

        return created_collection

    @classmethod
    def insert_doc(cls):
        # create a document using the document definition
        created_docs = []
        for d in cls.document_definitions:

            created_doc = cls.created_collection.create_item(body=d)
            created_docs.append(created_doc)
            
        return created_docs

    @classmethod
    def GetDatabaseLink(cls, database, is_name_based=True):
        if is_name_based:
            return 'dbs/' + database.id
        else:
            return database['_self']

    @classmethod
    def GetDocumentCollectionLink(cls, database, document_collection, is_name_based=True):
        if is_name_based:
            return cls.GetDatabaseLink(database) + '/colls/' + document_collection.id
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