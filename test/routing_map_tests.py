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
import pydocumentdb.documents as documents
import pydocumentdb.document_client as document_client
from pydocumentdb.routing.routing_map_provider import _PartitionKeyRangeCache
from pydocumentdb.routing import routing_range as routing_range
import test.test_config as test_config

#IMPORTANT NOTES:
  
#      Most test cases in this file create collections in your Azure Cosmos DB account.
#      Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.
  
#      To Run the test, replace the two member fields (masterKey and host) with values 
#   associated with your Azure Cosmos DB account.

class RoutingMapEndToEndTests(unittest.TestCase):
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
        RoutingMapEndToEndTests.cleanUpTestDatabase();

    def setUp(self):
        RoutingMapEndToEndTests.cleanUpTestDatabase();
        
        self.client = document_client.DocumentClient(RoutingMapEndToEndTests.host, {'masterKey': RoutingMapEndToEndTests.masterKey})
        self.created_db = self.client.CreateDatabase({ 'id': 'sample database' })        
        self.created_collection = self.create_collection(self.client, self.created_db)
        self.collection_link = self.GetDocumentCollectionLink(self.created_db, self.created_collection)
        
        # sanity check:
        partition_key_ranges = list(self.client._ReadPartitionKeyRanges(self.collection_link))
        self.assertGreaterEqual(len(partition_key_ranges), 5)
        
    def test_read_partition_key_ranges(self):
        
        collection_link = self.GetDocumentCollectionLink(self.created_db, self.created_collection)
        partition_key_ranges = list(self.client._ReadPartitionKeyRanges(collection_link))
        #"the number of expected partition ranges returned from the emulator is 5."
        self.assertEqual(5, len(partition_key_ranges))
        
    def test_routing_map_provider(self):
        
        collection_link = self.GetDocumentCollectionLink(self.created_db, self.created_collection)
        partition_key_ranges = list(self.client._ReadPartitionKeyRanges(collection_link))

        routing_mp = _PartitionKeyRangeCache(self.client)
        overlapping_partition_key_ranges = routing_mp.get_overlapping_ranges(collection_link, routing_range._Range("", "FF", True, False))
        self.assertEqual(len(overlapping_partition_key_ranges), len(partition_key_ranges))
        self.assertEqual(overlapping_partition_key_ranges, partition_key_ranges)

    def create_collection(self, client, created_db):

        collection_definition = {  
           'id':'sample collection',
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
        
        collection_options = { 'offerThroughput': 10100 }

        created_collection = client.CreateCollection(self.GetDatabaseLink(created_db),
                                collection_definition, 
                                collection_options)

        return created_collection

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