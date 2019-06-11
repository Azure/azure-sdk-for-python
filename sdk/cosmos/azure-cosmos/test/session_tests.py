# -*- coding: utf-8 -*-

import unittest
import uuid
import pytest
from azure.cosmos.http_constants import HttpHeaders
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents
import test_config
import azure.cosmos.errors as errors
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes, HttpHeaders
import azure.cosmos.synchronized_request as synchronized_request
import azure.cosmos.retry_utility as retry_utility

pytestmark = pytest.mark.cosmosEmulator

@pytest.mark.usefixtures("teardown")
class SessionTests(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

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
        cls.created_collection = test_config._test_config.create_multi_partition_collection_with_custom_pk_if_not_exist(cls.client)

    def _MockRequest(self, global_endpoint_manager, request, connection_policy, requests_session, path, request_options, request_body):
        if HttpHeaders.SessionToken in request_options['headers']:
            self.last_session_token_sent = request_options['headers'][HttpHeaders.SessionToken]
        else:
            self.last_session_token_sent = None
        return self._OriginalRequest(global_endpoint_manager, request, connection_policy, requests_session, path, request_options, request_body)

    def test_session_token_not_sent_for_master_resource_ops (self):
        self._OriginalRequest = synchronized_request._Request
        synchronized_request._Request = self._MockRequest
        created_document = self.client.CreateItem(self.created_collection['_self'], {'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        self.client.ReadItem(created_document['_self'], {'partitionKey': 'mypk'})
        self.assertNotEqual(self.last_session_token_sent, None)
        self.client.ReadContainer(self.created_collection['_self'])
        self.assertEqual(self.last_session_token_sent, None)
        self.client.ReadItem(created_document['_self'], {'partitionKey': 'mypk'})
        self.assertNotEqual(self.last_session_token_sent, None)
        synchronized_request._Request = self._OriginalRequest

    def _MockExecuteFunctionSessionReadFailureOnce(self, function, *args, **kwargs):
        raise errors.HTTPFailure(StatusCodes.NOT_FOUND, "Read Session not available", {HttpHeaders.SubStatus: SubStatusCodes.READ_SESSION_NOTAVAILABLE})

    def test_clear_session_token(self):
        created_document = self.client.CreateItem(self.created_collection['_self'], {'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})

        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunctionSessionReadFailureOnce
        try:
            self.client.ReadItem(created_document['_self'])
        except errors.HTTPFailure as e:
            self.assertEqual(self.client.session.get_session_token(self.created_collection['_self']), "")
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
            self.client.CreateItem(self.created_collection['_self'], {'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
            self.fail()
        except errors.HTTPFailure as e:
            self.assertEqual(e._http_error_message, "Could not parse the received session token: 2")
            self.assertEqual(e.status_code, StatusCodes.INTERNAL_SERVER_ERROR)
        retry_utility._ExecuteFunction = self.OriginalExecuteFunction
