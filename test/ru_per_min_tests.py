# The MIT License (MIT)
# Copyright (c) 2017 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
import pydocumentdb.documents as documents
import pydocumentdb.document_client as document_client
from pydocumentdb import query_iterable
import pydocumentdb.base as base
import test.test_config as test_config

# IMPORTANT NOTES:
  
#      Most test cases in this file create collections in your DocumentDB
#      account.
#      Collections are billing entities.  By running these test cases, you may
#      incur monetary costs on your account.
  
#      To Run the test, replace the two member fields (masterKey and host) with
#      values
#   associated with your DocumentDB account.
class RuPerMinTests(unittest.TestCase):
    """RuPerMinTests Tests.
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
        # creates the database, collection, and insert all the documents
        # we will gain some speed up in running the tests by creating the
        # database, collection and inserting all the docs only once

        if (cls.masterKey == '[YOUR_KEY_HERE]' or cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception("You must specify your Azure DocumentDB account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
            
        RuPerMinTests.cleanUpTestDatabase()
        
        cls.client = document_client.DocumentClient(cls.host, {'masterKey': cls.masterKey})
        cls.created_db = cls.client.CreateDatabase({ 'id': 'sample database' })
        
    @classmethod
    def tearDownClass(cls):
        RuPerMinTests.cleanUpTestDatabase()

    def setUp(self):
        colls = list(self.client.ReadCollections(self.created_db['_self']))
        for col in colls:
            self.client.DeleteCollection(RuPerMinTests.GetDocumentCollectionLink(self.created_db, col))

    def _query_offers(self, collection_self_link):
        offers = list(self.client.ReadOffers())
        for o in offers:
            if o['resource'] == collection_self_link:
                return o
        return None

    def test_create_collection_with_ru_pm(self):        
        # create an ru pm collection

        databae_link = self.GetDatabaseLink(self.created_db)

        collection_definition = {
            'id' : "sample col"
        }

        options = {
            'offerEnableRUPerMinuteThroughput': True,
            'offerVersion': "V2",
            'offerThroughput': 400
        }

        created_collection = self.client.CreateCollection(databae_link, collection_definition, options)

        offer = self._query_offers(created_collection['_self'])
        self.assertIsNotNone(offer)
        self.assertEqual(offer['offerType'], "Invalid")
        self.assertIsNotNone(offer['content'])

    def test_create_collection_without_ru_pm(self):        
        # create a non ru pm collection

        databae_link = self.GetDatabaseLink(self.created_db)

        collection_definition = {
            'id' : "sample col"
        }

        options = {
            'offerEnableRUPerMinuteThroughput': True,
            'offerVersion': "V2",
            'offerThroughput': 400
        }

        created_collection = self.client.CreateCollection(databae_link, collection_definition, options)

        offer = self._query_offers(created_collection['_self'])
        self.assertIsNotNone(offer)
        self.assertEqual(offer['offerType'], "Invalid")
        self.assertIsNotNone(offer['content'])

    def test_create_collection_disable_ru_pm_on_request(self):        
        # create a non ru pm collection

        databae_link = self.GetDatabaseLink(self.created_db)

        collection_definition = {
            'id' : "sample col"
        }

        options = {
            'offerVersion': "V2",
            'offerThroughput': 400
        }

        created_collection = self.client.CreateCollection(databae_link, collection_definition, options)

        offer = self._query_offers(created_collection['_self'])
        self.assertIsNotNone(offer)
        self.assertEqual(offer['offerType'], "Invalid")
        self.assertIsNotNone(offer['content'])
        self.assertEqual(offer['content']['offerIsRUPerMinuteThroughputEnabled'], False)

        request_options = {
            'disableRUPerMinuteUsage': True
        }

        doc = {
            'id' : 'test_doc'
        }
        created_document = self.client.CreateDocument(created_collection['_self'], doc, request_options)


    @classmethod
    def GetDatabaseLink(cls, database, is_name_based=True):
        if is_name_based:
            print("helloooo" + str(database))
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

    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
