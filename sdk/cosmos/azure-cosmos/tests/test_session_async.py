# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

from _fault_injection_transport_async import FaultInjectionTransportAsync
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos.aio import CosmosClient, _retry_utility_async
from azure.cosmos import DatabaseProxy, PartitionKey
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes, HttpHeaders
from azure.core.pipeline.transport._aiohttp import AioHttpTransportResponse
from azure.core.rest import HttpRequest, AsyncHttpResponse
from typing import Awaitable, Callable



@pytest.mark.cosmosEmulator
class TestSessionAsync(unittest.IsolatedAsyncioTestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    created_db: DatabaseProxy = None
    client: CosmosClient = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    configs = test_config.TestConfig
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    TEST_COLLECTION_ID = configs.TEST_MULTI_PARTITION_CONTAINER_ID

    @classmethod
    def setUpClass(cls):
        if cls.masterKey == '[YOUR_KEY_HERE]' or cls.host == '[YOUR_ENDPOINT_HERE]':
            raise Exception("You must specify your Azure Cosmos account values for "
                            "'masterKey' and 'host' at the top of this class to run the "
                            "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        await self.client.__aenter__()
        self.created_db = self.client.get_database_client(self.TEST_DATABASE_ID)
        self.created_container = self.created_db.get_container_client(self.TEST_COLLECTION_ID)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_session_token_swr_for_ops_async(self):
        # Session token should not be sent for control plane operations
        test_container = await self.created_db.create_container(str(uuid.uuid4()), PartitionKey(path="/id"), raw_response_hook=test_config.no_token_response_hook)
        await self.created_db.get_container_client(container=self.created_container).read(raw_response_hook=test_config.no_token_response_hook)
        await self.created_db.delete_container(test_container, raw_response_hook=test_config.no_token_response_hook)

        # Session token should be sent for document read/batch requests only - verify it is not sent for write requests
        up_item = await self.created_container.upsert_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                                                          raw_response_hook=test_config.no_token_response_hook)
        replaced_item = await self.created_container.replace_item(item=up_item['id'], body={'id': up_item['id'], 'song': 'song', 'pk': 'mypk'},
                                                             raw_response_hook=test_config.no_token_response_hook)
        created_document = await self.created_container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                                                               raw_response_hook=test_config.no_token_response_hook)
        response_session_token = created_document.get_response_headers().get(HttpHeaders.SessionToken)
        read_item = await self.created_container.read_item(item=created_document['id'], partition_key='mypk',
                                                      raw_response_hook=test_config.token_response_hook)
        read_item2 = await self.created_container.read_item(item=created_document['id'], partition_key='mypk',
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
        batch_result = await self.created_container.execute_item_batch(batch_operations, 'mypk', raw_response_hook=test_config.token_response_hook)
        batch_response_token = batch_result.get_response_headers().get(HttpHeaders.SessionToken)
        assert batch_response_token != response_session_token

        # Verify no session tokens are sent for delete requests either - but verify session token is updated
        await self.created_container.delete_item(replaced_item['id'], replaced_item['pk'], raw_response_hook=test_config.no_token_response_hook)
        assert self.created_db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) is not None
        assert self.created_db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) != batch_response_token

    async def test_session_token_mwr_for_ops_async(self):
        # For multiple write regions, all document requests should send out session tokens
        # We will use fault injection to simulate the regions the emulator needs
        first_region_uri: str = test_config.TestConfig.local_host.replace("localhost", "127.0.0.1")
        custom_transport = FaultInjectionTransportAsync()

        # Inject topology transformation that would make Emulator look like a multiple write region account
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation: Callable[[HttpRequest, Callable[[HttpRequest], Awaitable[AsyncHttpResponse]]], AioHttpTransportResponse] = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_mwr(
                first_region_name="First Region",
                second_region_name="Second Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)
        client = CosmosClient(self.host, self.masterKey, consistency_level="Session",
                              transport=custom_transport, multiple_write_locations=True)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_COLLECTION_ID)
        await client.__aenter__()

        # Session token should not be sent for control plane operations
        test_container = await db.create_container(str(uuid.uuid4()), PartitionKey(path="/id"),
                                                                raw_response_hook=test_config.no_token_response_hook)
        await db.get_container_client(container=self.created_container).read(
            raw_response_hook=test_config.no_token_response_hook)
        await db.delete_container(test_container, raw_response_hook=test_config.no_token_response_hook)

        # Session token should be sent for all document requests since we have mwr configuration
        # First write request won't have since tokens need to be populated on the client first
        await container.upsert_item(body={'id': '0' + str(uuid.uuid4()), 'pk': 'mypk'},
                                    raw_response_hook=test_config.no_token_response_hook)
        up_item = await container.upsert_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                                              raw_response_hook=test_config.token_response_hook)
        replaced_item = await container.replace_item(item=up_item['id'],
                                                                  body={'id': up_item['id'], 'song': 'song',
                                                                        'pk': 'mypk'},
                                                                  raw_response_hook=test_config.token_response_hook)
        created_document = await container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                                                                    raw_response_hook=test_config.token_response_hook)
        response_session_token = created_document.get_response_headers().get(HttpHeaders.SessionToken)
        read_item = await container.read_item(item=created_document['id'], partition_key='mypk',
                                                           raw_response_hook=test_config.token_response_hook)
        read_item2 = await container.read_item(item=created_document['id'], partition_key='mypk',
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
        batch_result = await container.execute_item_batch(batch_operations, 'mypk',
                                                                       raw_response_hook=test_config.token_response_hook)
        batch_response_token = batch_result.get_response_headers().get(HttpHeaders.SessionToken)
        assert batch_response_token != response_session_token

        # Should get sent now that we have mwr configuration
        await container.delete_item(replaced_item['id'], replaced_item['pk'],
                                                 raw_response_hook=test_config.token_response_hook)
        assert db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) is not None
        assert db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) != batch_response_token


    def _MockExecuteFunctionSessionReadFailureOnce(self, function, *args, **kwargs):
        response = test_config.FakeResponse({HttpHeaders.SubStatus: SubStatusCodes.READ_SESSION_NOTAVAILABLE})
        raise exceptions.CosmosHttpResponseError(
            status_code=StatusCodes.NOT_FOUND,
            message="Read Session not available",
            response=response)

    async def test_clear_session_token_async(self):
        created_document = await self.created_container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})

        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._MockExecuteFunctionSessionReadFailureOnce
        try:
            await self.created_container.read_item(item=created_document['id'], partition_key='mypk')
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(self.client.client_connection.session.get_session_token(
                'dbs/' + self.created_db.id + '/colls/' + self.created_container.id,
                None,
                None,
                None,
                None), "")
            self.assertEqual(e.status_code, StatusCodes.NOT_FOUND)
            self.assertEqual(e.sub_status, SubStatusCodes.READ_SESSION_NOTAVAILABLE)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction

    async def _MockExecuteFunctionInvalidSessionTokenAsync(self, function, *args, **kwargs):
        response = {'_self': 'dbs/90U1AA==/colls/90U1AJ4o6iA=/docs/90U1AJ4o6iABCT0AAAAABA==/', 'id': '1'}
        headers = {HttpHeaders.SessionToken: '0:2',
                   HttpHeaders.AlternateContentPath: 'dbs/testDatabase/colls/testCollection'}
        return (response, headers)

    async def test_internal_server_error_raised_for_invalid_session_token_received_from_server_async(self):
        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        _retry_utility_async.ExecuteFunctionAsync = self._MockExecuteFunctionInvalidSessionTokenAsync
        try:
            await self.created_container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
            self.fail('Test did not fail as expected')
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.http_error_message, "Could not parse the received session token: 2")
            self.assertEqual(e.status_code, StatusCodes.INTERNAL_SERVER_ERROR)
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
