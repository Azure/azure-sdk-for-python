# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import test_config
from _fault_injection_transport import FaultInjectionTransport
from azure.core.rest import HttpRequest
from azure.cosmos import DatabaseProxy, PartitionKey
from azure.cosmos import _retry_utility
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes, HttpHeaders
from typing import Callable


@pytest.mark.cosmosEmulator
class TestSession(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    created_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    configs = test_config.TestConfig
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    TEST_COLLECTION_ID = configs.TEST_MULTI_PARTITION_CONTAINER_ID

    @classmethod
    def setUpClass(cls):
        # creates the database, collection, and insert all the documents
        # we will gain some speed up in running the tests by creating the
        # database, collection and inserting all the docs only once

        if cls.masterKey == '[YOUR_KEY_HERE]' or cls.host == '[YOUR_ENDPOINT_HERE]':
            raise Exception("You must specify your Azure Cosmos account values for "
                            "'masterKey' and 'host' at the top of this class to run the "
                            "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.created_collection = cls.created_db.get_container_client(cls.TEST_COLLECTION_ID)

    def test_session_token_sm_for_ops(self):

        # Session token should not be sent for control plane operations
        test_container = self.created_db.create_container(str(uuid.uuid4()), PartitionKey(path="/id"), raw_response_hook=test_config.no_token_response_hook)
        self.created_db.get_container_client(container=self.created_collection).read(raw_response_hook=test_config.no_token_response_hook)
        self.created_db.delete_container(test_container, raw_response_hook=test_config.no_token_response_hook)

        # Session token should be sent for document read/batch requests only - verify it is not sent for write requests
        up_item = self.created_collection.upsert_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                                                          raw_response_hook=test_config.no_token_response_hook)
        replaced_item = self.created_collection.replace_item(item=up_item['id'], body={'id': up_item['id'], 'song': 'song', 'pk': 'mypk'},
                                                             raw_response_hook=test_config.no_token_response_hook)
        created_document = self.created_collection.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                                                               raw_response_hook=test_config.no_token_response_hook)
        response_session_token = created_document.get_response_headers().get(HttpHeaders.SessionToken)
        read_item = self.created_collection.read_item(item=created_document['id'], partition_key='mypk',
                                                      raw_response_hook=test_config.token_response_hook)
        read_item2 = self.created_collection.read_item(item=created_document['id'], partition_key='mypk',
                                                       raw_response_hook=test_config.token_response_hook)

        # Since the session hasn't been updated (no write requests have happened) verify session is still the same
        assert (read_item.get_response_headers().get(HttpHeaders.SessionToken) ==
                read_item2.get_response_headers().get(HttpHeaders.SessionToken) ==
                response_session_token)
        # Verify session tokens are sent for batch requests too
        batch_operations = [
            ("create", ({"id": str(uuid.uuid4()), "pk": 'mypk'},)),
            ("replace", (read_item2['id'], {"id": str(uuid.uuid4()), "pk": 'mypk'})),
            ("read", (replaced_item['id'],)),
            ("upsert", ({"id": str(uuid.uuid4()), "pk": 'mypk'},)),
        ]
        batch_result = self.created_collection.execute_item_batch(batch_operations, 'mypk', raw_response_hook=test_config.token_response_hook)
        batch_response_token = batch_result.get_response_headers().get(HttpHeaders.SessionToken)
        assert batch_response_token != response_session_token

        # Verify no session tokens are sent for delete requests either - but verify session token is updated
        self.created_collection.delete_item(replaced_item['id'], replaced_item['pk'], raw_response_hook=test_config.no_token_response_hook)
        assert self.created_db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) is not None
        assert self.created_db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) != batch_response_token

    def test_session_token_mwr_for_ops(self):
        # For multiple write regions, all document requests should send out session tokens
        # We will use fault injection to simulate the regions the emulator needs
        first_region_uri: str = test_config.TestConfig.local_host.replace("localhost", "127.0.0.1")
        custom_transport = FaultInjectionTransport()

        # Inject topology transformation that would make Emulator look like a multiple write region account
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransport.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransport.transform_topology_mwr(
                first_region_name="First Region",
                second_region_name="Second Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)
        client = cosmos_client.CosmosClient(self.host, self.masterKey, consistency_level="Session",
                                            transport=custom_transport, multiple_write_locations=True)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_COLLECTION_ID)

        # Session token should not be sent for control plane operations
        test_container = db.create_container(str(uuid.uuid4()), PartitionKey(path="/id"),
                                                                raw_response_hook=test_config.no_token_response_hook)
        db.get_container_client(container=self.created_collection).read(
            raw_response_hook=test_config.no_token_response_hook)
        db.delete_container(test_container, raw_response_hook=test_config.no_token_response_hook)

        # Session token should be sent for all document requests since we have mwr configuration
        # First write request won't have since tokens need to be populated on the client first
        container.upsert_item(body={'id': '0' + str(uuid.uuid4()), 'pk': 'mypk'},
                                    raw_response_hook=test_config.no_token_response_hook)
        up_item = container.upsert_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                                              raw_response_hook=test_config.token_response_hook)
        replaced_item = container.replace_item(item=up_item['id'], body={'id': up_item['id'], 'song': 'song',
                                                                         'pk': 'mypk'},
                                               raw_response_hook=test_config.token_response_hook)
        created_document = container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                                                 raw_response_hook=test_config.token_response_hook)
        response_session_token = created_document.get_response_headers().get(HttpHeaders.SessionToken)
        read_item = container.read_item(item=created_document['id'], partition_key='mypk',
                                        raw_response_hook=test_config.token_response_hook)
        read_item2 = container.read_item(item=created_document['id'], partition_key='mypk',
                                         raw_response_hook=test_config.token_response_hook)

        # Since the session hasn't been updated (no write requests have happened) verify session is still the same
        assert (read_item.get_response_headers().get(HttpHeaders.SessionToken) ==
                read_item2.get_response_headers().get(HttpHeaders.SessionToken) ==
                response_session_token)
        # Verify session tokens are sent for batch requests too
        batch_operations = [
            ("create", ({"id": str(uuid.uuid4()), "pk": 'mypk'},)),
            ("replace", (read_item2['id'], {"id": str(uuid.uuid4()), "pk": 'mypk'})),
            ("read", (replaced_item['id'],)),
            ("upsert", ({"id": str(uuid.uuid4()), "pk": 'mypk'},)),
        ]
        batch_result = container.execute_item_batch(batch_operations, 'mypk',
                                                    raw_response_hook=test_config.token_response_hook)
        batch_response_token = batch_result.get_response_headers().get(HttpHeaders.SessionToken)
        assert batch_response_token != response_session_token

        # Should get sent now that we have mwr configuration
        container.delete_item(replaced_item['id'], replaced_item['pk'],
                                                 raw_response_hook=test_config.token_response_hook)
        assert db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) is not None
        assert db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) != batch_response_token


    def _MockExecuteFunctionSessionReadFailureOnce(self, function, *args, **kwargs):
        response = test_config.FakeResponse({HttpHeaders.SubStatus: SubStatusCodes.READ_SESSION_NOTAVAILABLE})
        raise exceptions.CosmosHttpResponseError(
            status_code=StatusCodes.NOT_FOUND,
            message="Read Session not available",
            response=response)

    def test_clear_session_token(self):
        created_document = self.created_collection.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})

        self.OriginalExecuteFunction = _retry_utility.ExecuteFunction
        _retry_utility.ExecuteFunction = self._MockExecuteFunctionSessionReadFailureOnce
        try:
            self.created_collection.read_item(item=created_document['id'], partition_key='mypk')
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(self.client.client_connection.session.get_session_token(
                'dbs/' + self.created_db.id + '/colls/' + self.created_collection.id,
                None,
                None,
                None,
                None), "")
            self.assertEqual(e.status_code, StatusCodes.NOT_FOUND)
            self.assertEqual(e.sub_status, SubStatusCodes.READ_SESSION_NOTAVAILABLE)
        _retry_utility.ExecuteFunction = self.OriginalExecuteFunction

    def _MockExecuteFunctionInvalidSessionToken(self, function, *args, **kwargs):
        response = {'_self': 'dbs/90U1AA==/colls/90U1AJ4o6iA=/docs/90U1AJ4o6iABCT0AAAAABA==/', 'id': '1'}
        headers = {HttpHeaders.SessionToken: '0:2',
                   HttpHeaders.AlternateContentPath: 'dbs/testDatabase/colls/testCollection'}
        return (response, headers)

    def test_internal_server_error_raised_for_invalid_session_token_received_from_server(self):
        self.OriginalExecuteFunction = _retry_utility.ExecuteFunction
        _retry_utility.ExecuteFunction = self._MockExecuteFunctionInvalidSessionToken
        try:
            self.created_collection.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
            self.fail()
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.http_error_message, "Could not parse the received session token: 2")
            self.assertEqual(e.status_code, StatusCodes.INTERNAL_SERVER_ERROR)
        _retry_utility.ExecuteFunction = self.OriginalExecuteFunction


if __name__ == '__main__':
    unittest.main()
