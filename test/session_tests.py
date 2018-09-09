# -*- coding: utf-8 -*-

import unittest
from pydocumentdb.http_constants import HttpHeaders
import pydocumentdb.document_client as document_client
import pydocumentdb.documents as documents
import test.test_config as test_config
import pydocumentdb.synchronized_request as synchronized_request

class SessionTests(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy
    testDbName = 'testDatabase'
    testCollectionName = 'testCollection'

    @classmethod
    def cleanUpTestDatabase(cls):
        global client
        client = document_client.DocumentClient(cls.host,
                                                {'masterKey': cls.masterKey}, cls.connectionPolicy)
        query_iterable = client.QueryDatabases('SELECT * FROM root r WHERE r.id=\'' + cls.testDbName + '\'')
        it = iter(query_iterable)

        test_db = next(it, None)
        if test_db is not None:
            client.DeleteDatabase(test_db['_self'])

    @classmethod
    def tearDownClass(cls):
        cls.cleanUpTestDatabase()

    def setUp(self):
        global created_collection

        self.cleanUpTestDatabase()
        created_db = client.CreateDatabase({ 'id': self.testDbName })

        collection_definition = { 'id': self.testCollectionName, 'partitionKey': {'paths': ['/pk'],'kind': 'Hash'} }
        collection_options = { 'offerThroughput': 10100 }
        created_collection = client.CreateCollection(created_db['_self'], collection_definition, collection_options)

    def _MockRequest(self, connection_policy, requests_session, resource_url, request_options, request_body):
        if HttpHeaders.SessionToken in request_options['headers']:
            self.last_session_token_sent = request_options['headers'][HttpHeaders.SessionToken]
        else:
            self.last_session_token_sent = None
        return self._OriginalRequest(connection_policy, requests_session, resource_url, request_options, request_body)

    def test_session_token_not_sent_for_master_resource_ops (self):
        self._OriginalRequest = synchronized_request._Request
        synchronized_request._Request = self._MockRequest
        created_document = client.CreateDocument(created_collection['_self'], {'id': '1', 'pk': 'mypk'})
        read_document = client.ReadDocument(created_document['_self'], {'partitionKey': 'mypk'})
        self.assertNotEqual(self.last_session_token_sent, None)
        read_collection = client.ReadCollection(created_collection['_self'])
        self.assertEqual(self.last_session_token_sent, None)
        read_document = client.ReadDocument(created_document['_self'], {'partitionKey': 'mypk'})
        self.assertNotEqual(self.last_session_token_sent, None)
        synchronized_request._Request = self._OriginalRequest
