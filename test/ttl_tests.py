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
import time

import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors
from pydocumentdb.http_constants import StatusCodes
import test.test_config as test_config


#IMPORTANT NOTES:
  
#  	Most test cases in this file create collections in your Azure Cosmos DB account.
#  	Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.
  
#  	To Run the test, replace the two member fields (masterKey and host) with values 
#   associated with your Azure Cosmos DB account.

class Test_ttl_tests(unittest.TestCase):
    """TTL Unit Tests.
    """

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    testDbName = 'sample database'

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except errors.HTTPFailure as inst:
            self.assertEqual(inst.status_code, status_code)

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos DB account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    def setUp(self):
        client = document_client.DocumentClient(Test_ttl_tests.host, 
                                                {'masterKey': Test_ttl_tests.masterKey})
        query_iterable = client.QueryDatabases('SELECT * FROM root r WHERE r.id=\'' + Test_ttl_tests.testDbName + '\'')
        it = iter(query_iterable)
        
        test_db = next(it, None)
        if test_db is not None:
            client.DeleteDatabase(test_db['_self'])

    def test_collection_and_document_ttl_values(self):
        client = document_client.DocumentClient(Test_ttl_tests.host, {'masterKey': Test_ttl_tests.masterKey})

        created_db = client.CreateDatabase({ 'id': Test_ttl_tests.testDbName })
        
        collection_definition = {'id' : 'sample collection1',
                                 'defaultTtl' : 5
                                 }

        created_collection = client.CreateCollection(created_db['_self'], collection_definition)
        self.assertEqual(created_collection['defaultTtl'], collection_definition['defaultTtl'])
        
        collection_definition['id'] = 'sample collection2'
        collection_definition['defaultTtl'] = None

        # None is an unsupported value for defaultTtl. Valid values are -1 or a non-zero positive 32-bit integer value
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            client.CreateCollection,
            created_db['_self'],
            collection_definition)

        collection_definition['id'] = 'sample collection3'
        collection_definition['defaultTtl'] = 0

        # 0 is an unsupported value for defaultTtl. Valid values are -1 or a non-zero positive 32-bit integer value
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            client.CreateCollection,
            created_db['_self'],
            collection_definition)

        collection_definition['id'] = 'sample collection4'
        collection_definition['defaultTtl'] = -10

        # -10 is an unsupported value for defaultTtl. Valid values are -1 or a non-zero positive 32-bit integer value
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            client.CreateCollection,
            created_db['_self'],
            collection_definition)

        document_definition = { 'id': 'doc1',
                                'name': 'sample document',
                                'key': 'value',
                                'ttl' : 0}

        # 0 is an unsupported value for ttl. Valid values are -1 or a non-zero positive 32-bit integer value
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            client.CreateDocument,
            created_collection['_self'],
            document_definition)

        document_definition['id'] = 'doc2'
        document_definition['ttl'] = None

        # None is an unsupported value for ttl. Valid values are -1 or a non-zero positive 32-bit integer value
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            client.CreateDocument,
            created_collection['_self'],
            document_definition)

        document_definition['id'] = 'doc3'
        document_definition['ttl'] = -10
        
        # -10 is an unsupported value for ttl. Valid values are -1 or a non-zero positive 32-bit integer value
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            client.CreateDocument,
            created_collection['_self'],
            document_definition)

    def test_document_ttl_with_positive_defaultTtl(self):
        client = document_client.DocumentClient(Test_ttl_tests.host, {'masterKey': Test_ttl_tests.masterKey})

        created_db = client.CreateDatabase({ 'id': Test_ttl_tests.testDbName })
        
        collection_definition = {'id' : 'sample collection',
                                 'defaultTtl' : 5
                                 }
        
        created_collection = client.CreateCollection(created_db['_self'], collection_definition)

        document_definition = { 'id': 'doc1',
                                'name': 'sample document',
                                'key': 'value'}

        created_document = client.CreateDocument(created_collection['_self'], document_definition)

        time.sleep(7)
        
        # the created document should be gone now as it's ttl value would be same as defaultTtl value of the collection
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.NOT_FOUND,
            client.ReadDocument,
            created_document['_self'])

        document_definition['id'] = 'doc2'
        document_definition['ttl'] = -1
        created_document = client.CreateDocument(created_collection['_self'], document_definition)

        time.sleep(5)

        # the created document should NOT be gone as it's ttl value is set to -1(never expire) which overrides the collections's defaultTtl value
        read_document = client.ReadDocument(created_document['_self'])
        self.assertEqual(created_document['id'], read_document['id'])

        document_definition['id'] = 'doc3'
        document_definition['ttl'] = 2
        created_document = client.CreateDocument(created_collection['_self'], document_definition)

        time.sleep(4)

        # the created document should be gone now as it's ttl value is set to 2 which overrides the collections's defaultTtl value(5)
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.NOT_FOUND,
            client.ReadDocument,
            created_document['_self'])

        document_definition['id'] = 'doc4'
        document_definition['ttl'] = 8
        created_document = client.CreateDocument(created_collection['_self'], document_definition)

        time.sleep(6)

        # the created document should NOT be gone as it's ttl value is set to 8 which overrides the collections's defaultTtl value(5)
        read_document = client.ReadDocument(created_document['_self'])
        self.assertEqual(created_document['id'], read_document['id'])

        time.sleep(4)

        # the created document should be gone now as we have waited for (6+4) secs which is greater than documents's ttl value of 8
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.NOT_FOUND,
            client.ReadDocument,
            created_document['_self'])

    def test_document_ttl_with_negative_one_defaultTtl(self):
        client = document_client.DocumentClient(Test_ttl_tests.host, {'masterKey': Test_ttl_tests.masterKey})

        created_db = client.CreateDatabase({ 'id': Test_ttl_tests.testDbName })
        
        collection_definition = {'id' : 'sample collection',
                                 'defaultTtl' : -1
                                 }
        
        created_collection = client.CreateCollection(created_db['_self'], collection_definition)

        document_definition = { 'id': 'doc1',
                                'name': 'sample document',
                                'key': 'value'}

        # the created document's ttl value would be -1 inherited from the collection's defaultTtl and this document will never expire
        created_document1 = client.CreateDocument(created_collection['_self'], document_definition)

        # This document is also set to never expire explicitly
        document_definition['id'] = 'doc2'
        document_definition['ttl'] = -1
        created_document2 = client.CreateDocument(created_collection['_self'], document_definition)

        document_definition['id'] = 'doc3'
        document_definition['ttl'] = 2
        created_document3 = client.CreateDocument(created_collection['_self'], document_definition)

        time.sleep(4)

        # the created document should be gone now as it's ttl value is set to 2 which overrides the collections's defaultTtl value(-1)
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.NOT_FOUND,
            client.ReadDocument,
            created_document3['_self'])

        # The documents with id doc1 and doc2 will never expire
        read_document = client.ReadDocument(created_document1['_self'])
        self.assertEqual(created_document1['id'], read_document['id'])

        read_document = client.ReadDocument(created_document2['_self'])
        self.assertEqual(created_document2['id'], read_document['id'])

    def test_document_ttl_with_no_defaultTtl(self):
        client = document_client.DocumentClient(Test_ttl_tests.host, {'masterKey': Test_ttl_tests.masterKey})

        created_db = client.CreateDatabase({ 'id': Test_ttl_tests.testDbName })
        
        collection_definition = {'id' : 'sample collection' }
        
        created_collection = client.CreateCollection(created_db['_self'], collection_definition)

        document_definition = { 'id': 'doc1',
                                'name': 'sample document',
                                'key': 'value',
                                'ttl' : 5}

        created_document = client.CreateDocument(created_collection['_self'], document_definition)

        time.sleep(7)

        # Created document still exists even after ttl time has passed since the TTL is disabled at collection level(no defaultTtl property defined)
        read_document = client.ReadDocument(created_document['_self'])
        self.assertEqual(created_document['id'], read_document['id'])

    def test_document_ttl_misc(self):
        client = document_client.DocumentClient(Test_ttl_tests.host, {'masterKey': Test_ttl_tests.masterKey})

        created_db = client.CreateDatabase({ 'id': Test_ttl_tests.testDbName })
        
        collection_definition = {'id' : 'sample collection',
                                 'defaultTtl' : 8
                                 }
        
        created_collection = client.CreateCollection(created_db['_self'], collection_definition)

        document_definition = { 'id': 'doc1',
                                'name': 'sample document',
                                'key': 'value'}

        created_document = client.CreateDocument(created_collection['_self'], document_definition)

        time.sleep(10)

        # the created document cannot be deleted since it should already be gone now
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.NOT_FOUND,
            client.DeleteDocument,
            created_document['_self'])

        # We can create a document with the same id after the ttl time has expired
        created_document = client.CreateDocument(created_collection['_self'], document_definition)
        self.assertEqual(created_document['id'], document_definition['id'])

        time.sleep(3)

        # Upsert the document after 3 secs to reset the document's ttl
        document_definition['key'] = 'value2'
        upserted_docment = client.UpsertDocument(created_collection['_self'], document_definition)

        time.sleep(7)

        # Upserted document still exists after 10 secs from document creation time(with collection's defaultTtl set to 8) since it's ttl was reset after 3 secs by upserting it
        read_document = client.ReadDocument(upserted_docment['_self'])
        self.assertEqual(upserted_docment['id'], read_document['id'])

        time.sleep(3)

        # the upserted document should be gone now after 10 secs from the last write(upsert) of the document
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.NOT_FOUND,
            client.ReadDocument,
            upserted_docment['_self'])

        documents = list(client.QueryDocuments(
        created_collection['_self'],
        {
            'query': 'SELECT * FROM root r'
        }))

        self.assertEqual(0, len(documents))

        # Removes defaultTtl property from collection to disable ttl at collection level
        collection_definition.pop('defaultTtl')
        replaced_collection = client.ReplaceCollection(created_collection['_self'], collection_definition)

        document_definition['id'] = 'doc2'
        created_document = client.CreateDocument(replaced_collection['_self'], document_definition)

        time.sleep(5)

        # Created document still exists even after ttl time has passed since the TTL is disabled at collection level
        read_document = client.ReadDocument(created_document['_self'])
        self.assertEqual(created_document['id'], read_document['id'])
    
if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True:  # raised by sys.exit(True) when tests failed
            raise
