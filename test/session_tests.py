# -*- coding: utf-8 -*-

import unittest
import uuid
import pytest
from azure.cosmos.http_constants import HttpHeaders
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents
import test.test_config as test_config
import azure.cosmos.errors as errors
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes, HttpHeaders
import azure.cosmos.synchronized_request as synchronized_request
import azure.cosmos.retry_utility as retry_utility

@pytest.mark.usefixtures("teardown")
class SessionTests(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy
    client = cosmos_client.CosmosClient(host, {'masterKey': masterKey}, "Session", connectionPolicy)
    created_db = test_config._test_config.create_database_if_not_exist(client)
    created_collection = test_config._test_config.create_multi_partition_collection_with_custom_pk_if_not_exist(client)

    def _MockRequest(self, global_endpoint_manager, request, connection_policy, requests_session, path, request_options, request_body):
        if HttpHeaders.SessionToken in request_options['headers']:
            self.last_session_token_sent = request_options['headers'][HttpHeaders.SessionToken]
        else:
            self.last_session_token_sent = None
        return self._OriginalRequest(global_endpoint_manager, request, connection_policy, requests_session, path, request_options, request_body)

    def test_session_token_not_sent_for_master_resource_ops (self):
        self._OriginalRequest = synchronized_request._Request
        synchronized_request._Request = self._MockRequest
        created_document = self.created_collection.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        self.created_collection.get_item(id=created_document['id'], partition_key='mypk')
        self.assertNotEqual(self.last_session_token_sent, None)
        self.created_db.get_container(container=self.created_collection)
        self.assertEqual(self.last_session_token_sent, None)
        self.created_collection.get_item(id=created_document['id'], partition_key='mypk')
        self.assertNotEqual(self.last_session_token_sent, None)
        synchronized_request._Request = self._OriginalRequest

    def _MockExecuteFunctionSessionReadFailureOnce(self, function, *args, **kwargs):
        raise errors.HTTPFailure(StatusCodes.NOT_FOUND, "Read Session not available", {HttpHeaders.SubStatus: SubStatusCodes.READ_SESSION_NOTAVAILABLE})

    def test_clear_session_token(self):
        created_document = self.created_collection.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})

        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunctionSessionReadFailureOnce
        try:
            self.created_collection.get_item(id=created_document['id'], partition_key='mypk')
        except errors.HTTPFailure as e:
            self.assertEqual(self.client.client_connection.session.get_session_token(
                'dbs/' + self.created_db.id + '/colls/' + self.created_collection.id), "")
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
            self.created_collection.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
            self.fail()
        except errors.HTTPFailure as e:
            self.assertEqual(e._http_error_message, "Could not parse the received session token: 2")
            self.assertEqual(e.status_code, StatusCodes.INTERNAL_SERVER_ERROR)
        retry_utility._ExecuteFunction = self.OriginalExecuteFunction
