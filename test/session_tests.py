# -*- coding: utf-8 -*-

import unittest
from azure.cosmos.http_constants import HttpHeaders
import azure.cosmos.cosmos_client_connection as cosmos_client_connection
import azure.cosmos.documents as documents
import test.test_config as test_config
import azure.cosmos.errors as errors
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes, HttpHeaders
import azure.cosmos.synchronized_request as synchronized_request
import azure.cosmos.retry_utility as retry_utility

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
        client = cosmos_client_connection.CosmosClientConnection(cls.host,
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
        created_collection = client.CreateContainer(created_db['_self'], collection_definition, collection_options)

    def _MockRequest(self, global_endpoint_manager, request, connection_policy, requests_session, path, request_options, request_body):
        if HttpHeaders.SessionToken in request_options['headers']:
            self.last_session_token_sent = request_options['headers'][HttpHeaders.SessionToken]
        else:
            self.last_session_token_sent = None
        return self._OriginalRequest(global_endpoint_manager, request, connection_policy, requests_session, path, request_options, request_body)

    def test_session_token_not_sent_for_master_resource_ops (self):
        self._OriginalRequest = synchronized_request._Request
        synchronized_request._Request = self._MockRequest
        created_document = client.CreateItem(created_collection['_self'], {'id': '1', 'pk': 'mypk'})
        client.ReadItem(created_document['_self'], {'partitionKey': 'mypk'})
        self.assertNotEqual(self.last_session_token_sent, None)
        client.ReadContainer(created_collection['_self'])
        self.assertEqual(self.last_session_token_sent, None)
        client.ReadItem(created_document['_self'], {'partitionKey': 'mypk'})
        self.assertNotEqual(self.last_session_token_sent, None)
        synchronized_request._Request = self._OriginalRequest

    def _MockExecuteFunctionSessionReadFailureOnce(self, function, *args, **kwargs):
        raise errors.HTTPFailure(StatusCodes.NOT_FOUND, "Read Session not available", {HttpHeaders.SubStatus: SubStatusCodes.READ_SESSION_NOTAVAILABLE})

    def test_clear_session_token(self):
        created_document = client.CreateItem(created_collection['_self'], {'id': '1', 'pk': 'mypk'})

        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunctionSessionReadFailureOnce
        try:
            client.ReadItem(created_document['_self'])
        except errors.HTTPFailure as e:
            self.assertEqual(client.session.get_session_token(created_collection['_self']), "")
            self.assertEqual(e.status_code, StatusCodes.NOT_FOUND)
            self.assertEqual(e.sub_status, SubStatusCodes.READ_SESSION_NOTAVAILABLE)
        retry_utility._ExecuteFunction = self.OriginalExecuteFunction

    def _MockExecuteFunctionInvalidSessionToken(self, function, *args, **kwargs):
        response = {'_self':'dbs/90U1AA==/colls/90U1AJ4o6iA=/docs/90U1AJ4o6iABCT0AAAAABA==/', 'id':'1'}
        headers = {HttpHeaders.SessionToken: '0:2', HttpHeaders.AlternateContentPath: 'dbs/testDatabase/colls/testCollection'}
        return (response, headers)

    def test_internal_server_error_raised_for_invalid_session_token_received_from_server(self):
        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunctionInvalidSessionToken
        try:
            client.CreateItem(created_collection['_self'], {'id': '1', 'pk': 'mypk'})
            self.fail()
        except errors.HTTPFailure as e:
            self.assertEqual(e._http_error_message, "Could not parse the received session token: 2")
            self.assertEqual(e.status_code, StatusCodes.INTERNAL_SERVER_ERROR)
        retry_utility._ExecuteFunction = self.OriginalExecuteFunction
