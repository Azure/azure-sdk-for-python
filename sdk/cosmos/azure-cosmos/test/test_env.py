#The MIT License (MIT)
#Copyright (c) 2019 Microsoft Corporation

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
import pytest
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import PartitionKey
import test_config
import os

pytestmark = pytest.mark.cosmosEmulator

#IMPORTANT NOTES:
  
#      Most test cases in this file create collections in your Azure Cosmos account.
#      Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.
  
#      To Run the test, replace the two member fields (masterKey and host) with values 
#   associated with your Azure Cosmos account.

@pytest.mark.usefixtures("teardown")
class EnvTest(unittest.TestCase):
    """Env Tests.
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

        os.environ["COSMOS_ENDPOINT"] = cls.host
        os.environ["COSMOS_KEY"] = cls.masterKey
        cls.client = cosmos_client.CosmosClient(url=cls.host, credential=cls.masterKey, consistency_level="Session",
                                                connection_policy=cls.connectionPolicy)
        cls.created_db = cls.client.create_database_if_not_exists("Test_Env_DB")
        cls.created_collection = cls.databaseForTest.create_container_if_not_exists(
            cls.configs.TEST_COLLECTION_SINGLE_PARTITION_ID, PartitionKey(path="/id"))

    @classmethod
    def tearDownClass(cls):
        del os.environ['COSMOS_ENDPOINT']
        del os.environ['COSMOS_KEY']

    def test_insert(self):
        # create a document using the document definition
        d = {'id': '1',
                 'name': 'sample document',
                 'spam': 'eggs',
                 'cnt': '1',
                 'key': 'value',
                 'spam2': 'eggs',
                 }

        self.created_collection.create_item(d)

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