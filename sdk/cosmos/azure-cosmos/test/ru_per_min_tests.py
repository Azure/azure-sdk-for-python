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
import uuid
import pytest
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import query_iterable
import azure.cosmos.base as base
import test_config

pytestmark = pytest.mark.cosmosEmulator

# IMPORTANT NOTES:
  
#      Most test cases in this file create collections in your Azure Cosmos
#      account.
#      Collections are billing entities.  By running these test cases, you may
#      incur monetary costs on your account.
  
#      To Run the test, replace the two member fields (masterKey and host) with
#      values
#   associated with your Azure Cosmos account.

@pytest.mark.usefixtures("teardown")
class RuPerMinTests(unittest.TestCase):
    """RuPerMinTests Tests.
    """
    
    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy

    @classmethod
    def setUpClass(cls):
        # creates the database, collection, and insert all the documents
        # we will gain some speed up in running the tests by creating the
        # database, collection and inserting all the docs only once

        if (cls.masterKey == '[YOUR_KEY_HERE]' or cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception("You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, {'masterKey': cls.masterKey}, cls.connectionPolicy)
        cls.created_db = test_config._test_config.create_database_if_not_exist(cls.client)

    def _query_offers(self, collection_self_link):
        offers = list(self.client.ReadOffers())
        for o in offers:
            if o['resource'] == collection_self_link:
                return o
        return None

    def test_create_collection_with_ru_pm(self):
        # create an ru pm collection
        collection_definition = {
            'id' : "test_create_collection_with_ru_pm collection" + str(uuid.uuid4())
        }

        options = {
            'offerEnableRUPerMinuteThroughput': True,
            'offerVersion': "V2",
            'offerThroughput': 400
        }

        created_collection = self.client.CreateContainer(self.created_db['_self'], collection_definition, options)

        offer = self._query_offers(created_collection['_self'])
        self.assertIsNotNone(offer)
        self.assertEqual(offer['offerType'], "Invalid")
        self.assertIsNotNone(offer['content'])
        self.client.DeleteContainer(created_collection['_self'])

    def test_create_collection_without_ru_pm(self):        
        # create a non ru pm collection
        collection_definition = {
            'id' : "test_create_collection_without_ru_pm collection" + str(uuid.uuid4())
        }

        options = {
            'offerEnableRUPerMinuteThroughput': False,
            'offerVersion': "V2",
            'offerThroughput': 400
        }

        created_collection = self.client.CreateContainer(self.created_db['_self'], collection_definition, options)

        offer = self._query_offers(created_collection['_self'])
        self.assertIsNotNone(offer)
        self.assertEqual(offer['offerType'], "Invalid")
        self.assertIsNotNone(offer['content'])
        self.client.DeleteContainer(created_collection['_self'])

    def test_create_collection_disable_ru_pm_on_request(self):        
        # create a non ru pm collection
        collection_definition = {
            'id' : "test_create_collection_disable_ru_pm_on_request collection" + str(uuid.uuid4())
        }

        options = {
            'offerVersion': "V2",
            'offerThroughput': 400
        }

        created_collection = self.client.CreateContainer(self.created_db['_self'], collection_definition, options)

        offer = self._query_offers(created_collection['_self'])
        self.assertIsNotNone(offer)
        self.assertEqual(offer['offerType'], "Invalid")
        self.assertIsNotNone(offer['content'])
        self.assertEqual(offer['content']['offerIsRUPerMinuteThroughputEnabled'], False)

        request_options = {
            'disableRUPerMinuteUsage': True
        }

        doc = {
            'id' : 'test_doc' + str(uuid.uuid4())
        }
        self.client.CreateItem(created_collection['_self'], doc, request_options)
        self.client.DeleteContainer(created_collection['_self'])

if __name__ == "__main__":

    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
