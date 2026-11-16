# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the async session-token tests that exercise replace_item.

The originals check the session-token header on each outgoing request by patching
the Python pipeline transport, and check response session tokens. The Rust backend
does not send requests through that transport, so the outgoing-request checks cannot
be observed. Every operation and every response-side assertion still runs in order;
the test then skips, naming the outgoing-request checks it could not verify.
"""

import os
import unittest
import uuid
from contextlib import contextmanager
from typing import Awaitable, Callable

import pytest

from _fault_injection_transport_async import FaultInjectionTransportAsync
from azure.core.pipeline.transport._aiohttp import AioHttpTransportResponse
from azure.core.rest import HttpRequest, AsyncHttpResponse
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, DatabaseProxy
from azure.cosmos.http_constants import HttpHeaders


def assert_no_session_token(request):
    request_headers = request.headers
    assert request_headers.get(HttpHeaders.SessionToken) is None


def assert_session_token(request):
    request_headers = request.headers
    assert request_headers.get(HttpHeaders.SessionToken) is not None


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestSessionAsync(unittest.IsolatedAsyncioTestCase):
    """Rust-path copies of tests/test_session_async.py::TestSessionAsync."""

    created_db: DatabaseProxy = None
    client: CosmosClient = None
    host = os.environ.get("ACCOUNT_HOST")
    masterKey = os.environ.get("ACCOUNT_KEY")

    async def asyncSetUp(self):
        self._unverified_request_checks = []
        self.TEST_DATABASE_ID = "replace_item_session_async_" + uuid.uuid4().hex
        self.TEST_COLLECTION_ID = "multi_partition_" + uuid.uuid4().hex[:8]
        # key-auth client for control-plane operations, and a separate data-plane client,
        # like the original create_test_clients_async pair.
        self.key_client = CosmosClient(self.host, self.masterKey, _backend="rust")
        self.client = CosmosClient(self.host, self.masterKey, _backend="rust")
        await self.key_client.__aenter__()
        await self.client.__aenter__()
        self.key_db = None
        try:
            self.key_db = await self.key_client.create_database(self.TEST_DATABASE_ID)
            await self.key_db.create_container(self.TEST_COLLECTION_ID, PartitionKey(path="/pk"))
        except BaseException:
            await self.asyncTearDown()
            raise
        self.created_db = self.client.get_database_client(self.TEST_DATABASE_ID)
        self.created_container = self.created_db.get_container_client(self.TEST_COLLECTION_ID)

    async def asyncTearDown(self):
        try:
            if self.key_db is not None:
                await self.key_client.delete_database(self.TEST_DATABASE_ID)
        finally:
            await self.client.close()
            await self.key_client.close()

    @contextmanager
    def _capture_requests(self, description):
        """Stand-in for test_config.capture_requests, which patches the Python pipeline transport.

        The Rust backend sends requests itself, so no outgoing request can be captured here.
        The check is recorded and reported by _skip_unverified_request_checks at the end.
        """
        requests = []
        yield requests
        self._unverified_request_checks.append(description)

    def _skip_unverified_request_checks(self):
        # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The Rust-prepared outgoing request is not observable, so the request session-token header checks cannot run.
        pytest.skip("accepted-vnext-change: outgoing request session-token header checks cannot be observed on the Rust path "
                    "(known gap 6); all response-side assertions ran. Unverified request checks: "
                    + "; ".join(self._unverified_request_checks))

    async def test_session_token_swr_for_ops_async_rust(self):
        # Source: tests/test_session_async.py::TestSessionAsync.test_session_token_swr_for_ops_async
        # Session token should not be sent for control plane operations
        # control-plane container create/read/delete via key_db
        # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). Each capture below cannot see the outgoing request headers on the Rust path.
        with self._capture_requests("create_container: no session token") as requests:
            test_container = await self.key_db.create_container(str(uuid.uuid4()), PartitionKey(path="/id"))
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("container read: no session token") as requests:
            await self.key_db.get_container_client(container=self.created_container).read()
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("delete_container: no session token") as requests:
            await self.key_db.delete_container(test_container)
        for request in requests:
            assert_no_session_token(request)

        # Session token should be sent for document read/batch requests only - verify it is not sent for write requests
        with self._capture_requests("upsert_item: no session token") as requests:
            up_item = await self.created_container.upsert_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("replace_item: no session token") as requests:
            replaced_item = await self.created_container.replace_item(item=up_item['id'], body={'id': up_item['id'], 'song': 'song', 'pk': 'mypk'})
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("create_item: no session token") as requests:
            created_document = await self.created_container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        for request in requests:
            assert_no_session_token(request)
        response_session_token = created_document.get_response_headers().get(HttpHeaders.SessionToken)
        with self._capture_requests("read_item: session token sent") as requests:
            read_item = await self.created_container.read_item(item=created_document['id'], partition_key='mypk')
        for request in requests:
            assert_session_token(request)
        with self._capture_requests("second read_item: session token sent") as requests:
            read_item2 = await self.created_container.read_item(item=created_document['id'], partition_key='mypk')
        for request in requests:
            assert_session_token(request)

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
        with self._capture_requests("execute_item_batch: session token sent") as requests:
            batch_result = await self.created_container.execute_item_batch(batch_operations, 'mypk')
        for request in requests:
            assert_session_token(request)
        batch_response_token = batch_result.get_response_headers().get(HttpHeaders.SessionToken)
        assert batch_response_token != response_session_token

        # Verify no session tokens are sent for delete requests either - but verify session token is updated
        with self._capture_requests("delete_item: no session token") as requests:
            await self.created_container.delete_item(replaced_item['id'], replaced_item['pk'])
        for request in requests:
            assert_no_session_token(request)
        assert self.created_db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) is not None
        assert self.created_db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) != batch_response_token

        self._skip_unverified_request_checks()

    # This test injects emulator-style multi-write topology with a localhost endpoint.
    # In AAD live lanes that injected secondary endpoint is unreachable, so skip there.
    @pytest.mark.skipif(
        os.getenv("COSMOS_TEST_DATA_AUTH_MODE", "key").strip().lower() == 'aad',
        reason="environment-gap: MWR topology fault-injection test uses localhost secondary endpoint and is emulator-only."
    )
    async def test_session_token_mwr_for_ops_async_rust(self):
        # Source: tests/test_session_async.py::TestSessionAsync.test_session_token_mwr_for_ops_async
        # For multiple write regions, all document requests should send out session tokens
        # We will use fault injection to simulate the regions the emulator needs
        # NOTE: This test stays entirely on key-auth since it uses a custom FaultInjection transport
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
        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The Rust client cannot take the custom transport that fakes the multi-write topology, so the client cannot be built.
        pytest.skip("accepted-vnext-change: custom transport (multi-write topology injection) is not accepted by the Rust client "
                    "(known gap 10); multiple_write_locations is also rejected and the live account is single-write.")
        client = CosmosClient(self.host, self.masterKey, consistency_level="Session",
                              transport=custom_transport, multiple_write_locations=True, _backend="rust")
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_COLLECTION_ID)
        await client.__aenter__()

        # Session token should not be sent for control plane operations
        with self._capture_requests("create_container: no session token") as requests:
            test_container = await db.create_container(str(uuid.uuid4()), PartitionKey(path="/id"))
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("container read: no session token") as requests:
            await db.get_container_client(container=self.created_container).read(
                )
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("delete_container: no session token") as requests:
            await db.delete_container(test_container)
        for request in requests:
            assert_no_session_token(request)

        # Session token should be sent for all document requests since we have mwr configuration
        # First write request won't have since tokens need to be populated on the client first
        with self._capture_requests("first upsert_item: no session token") as requests:
            await container.upsert_item(body={'id': '0' + str(uuid.uuid4()), 'pk': 'mypk'})
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("upsert_item: session token sent") as requests:
            up_item = await container.upsert_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        for request in requests:
            assert_session_token(request)
        with self._capture_requests("replace_item: session token sent") as requests:
            replaced_item = await container.replace_item(item=up_item['id'],
                                                         body={'id': up_item['id'], 'song': 'song',
                                                               'pk': 'mypk'})
        for request in requests:
            assert_session_token(request)
        with self._capture_requests("create_item: session token sent") as requests:
            created_document = await container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        for request in requests:
            assert_session_token(request)
        response_session_token = created_document.get_response_headers().get(HttpHeaders.SessionToken)
        with self._capture_requests("read_item: session token sent") as requests:
            read_item = await container.read_item(item=created_document['id'], partition_key='mypk')
        for request in requests:
            assert_session_token(request)
        with self._capture_requests("second read_item: session token sent") as requests:
            read_item2 = await container.read_item(item=created_document['id'], partition_key='mypk')
        for request in requests:
            assert_session_token(request)

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
        with self._capture_requests("execute_item_batch: session token sent") as requests:
            batch_result = await container.execute_item_batch(batch_operations, 'mypk')
        for request in requests:
            assert_session_token(request)
        batch_response_token = batch_result.get_response_headers().get(HttpHeaders.SessionToken)
        assert batch_response_token != response_session_token

        # Should get sent now that we have mwr configuration
        with self._capture_requests("delete_item: session token sent") as requests:
            await container.delete_item(replaced_item['id'], replaced_item['pk'])
        for request in requests:
            assert_session_token(request)
        assert db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) is not None
        assert db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) != batch_response_token
        await client.close()

        self._skip_unverified_request_checks()


if __name__ == '__main__':
    unittest.main()
