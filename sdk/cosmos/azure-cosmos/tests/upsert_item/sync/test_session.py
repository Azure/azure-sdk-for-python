# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the sync session-token tests that exercise upsert_item.

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
from typing import Callable

import pytest

import azure.cosmos.cosmos_client as cosmos_client
from azure.core.rest import HttpRequest
from azure.cosmos import DatabaseProxy, PartitionKey
from azure.cosmos.http_constants import HttpHeaders
from _fault_injection_transport import FaultInjectionTransport


def assert_no_session_token(request):
    request_headers = request.headers
    assert request_headers.get(HttpHeaders.SessionToken) is None


def assert_session_token(request):
    request_headers = request.headers
    assert request_headers.get(HttpHeaders.SessionToken) is not None


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestSession(unittest.TestCase):
    """Rust-path copies of tests/test_session.py::TestSession."""

    created_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    host = os.environ.get("ACCOUNT_HOST")
    masterKey = os.environ.get("ACCOUNT_KEY")

    @classmethod
    def setUpClass(cls):
        cls.TEST_DATABASE_ID = "upsert_item_session_" + uuid.uuid4().hex
        cls.TEST_COLLECTION_ID = "multi_partition_" + uuid.uuid4().hex[:8]
        # key-auth client for control-plane operations, and a separate data-plane client,
        # like the original create_test_clients pair.
        cls.key_client = cosmos_client.CosmosClient(cls.host, cls.masterKey, _backend="rust")
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, _backend="rust")
        cls.key_db = cls.key_client.create_database(cls.TEST_DATABASE_ID)
        cls.key_db.create_container(cls.TEST_COLLECTION_ID, PartitionKey(path="/pk"))
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.created_collection = cls.created_db.get_container_client(cls.TEST_COLLECTION_ID)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.key_client.delete_database(cls.TEST_DATABASE_ID)
        finally:
            cls.client.close()
            cls.key_client.close()

    def setUp(self):
        self._unverified_request_checks = []

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

    def test_session_token_sm_for_ops_rust(self):
        # Source: tests/test_session.py::TestSession.test_session_token_sm_for_ops

        # Session token should not be sent for control plane operations
        # control-plane container create/read/delete via key_db
        # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). Each capture below cannot see the outgoing request headers on the Rust path.
        with self._capture_requests("create_container: no session token") as requests:
            test_container = self.key_db.create_container(str(uuid.uuid4()), PartitionKey(path="/id"))
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("container read: no session token") as requests:
            self.key_db.get_container_client(container=self.created_collection).read()
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("delete_container: no session token") as requests:
            self.key_db.delete_container(test_container)
        for request in requests:
            assert_no_session_token(request)

        # Session token should be sent for document read/batch requests only - verify it is not sent for write requests
        with self._capture_requests("upsert_item: no session token") as requests:
            up_item = self.created_collection.upsert_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("replace_item: no session token") as requests:
            replaced_item = self.created_collection.replace_item(item=up_item['id'], body={'id': up_item['id'], 'song': 'song', 'pk': 'mypk'})
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("create_item: no session token") as requests:
            created_document = self.created_collection.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        for request in requests:
            assert_no_session_token(request)
        response_session_token = created_document.get_response_headers().get(HttpHeaders.SessionToken)
        with self._capture_requests("read_item: session token sent") as requests:
            read_item = self.created_collection.read_item(item=created_document['id'], partition_key='mypk')
        for request in requests:
            assert_session_token(request)
        with self._capture_requests("second read_item: session token sent") as requests:
            read_item2 = self.created_collection.read_item(item=created_document['id'], partition_key='mypk')
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
            batch_result = self.created_collection.execute_item_batch(batch_operations, 'mypk')
        for request in requests:
            assert_session_token(request)
        batch_response_token = batch_result.get_response_headers().get(HttpHeaders.SessionToken)
        assert batch_response_token != response_session_token

        # Verify no session tokens are sent for delete requests either - but verify session token is updated
        with self._capture_requests("delete_item: no session token") as requests:
            self.created_collection.delete_item(replaced_item['id'], replaced_item['pk'])
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
    def test_session_token_mwr_for_ops_rust(self):
        # Source: tests/test_session.py::TestSession.test_session_token_mwr_for_ops
        # For multiple write regions, all document requests should send out session tokens
        # We will use fault injection to simulate the regions the emulator needs
        # NOTE: This test stays entirely on key-auth since it uses a custom FaultInjection transport
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
        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The Rust client cannot take the custom transport that fakes the multi-write topology, so the client cannot be built.
        pytest.skip("accepted-vnext-change: custom transport (multi-write topology injection) is not accepted by the Rust client "
                    "(known gap 10); multiple_write_locations is also rejected and the live account is single-write.")
        client = cosmos_client.CosmosClient(self.host, self.masterKey, consistency_level="Session",
                                            transport=custom_transport, multiple_write_locations=True,
                                            _backend="rust")
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_COLLECTION_ID)

        # Session token should not be sent for control plane operations
        # control-plane container create/read/delete
        with self._capture_requests("create_container: no session token") as requests:
            test_container = db.create_container(str(uuid.uuid4()), PartitionKey(path="/id"))
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("container read: no session token") as requests:
            db.get_container_client(container=self.created_collection).read(
                )
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("delete_container: no session token") as requests:
            db.delete_container(test_container)
        for request in requests:
            assert_no_session_token(request)

        # Session token should be sent for all document requests since we have mwr configuration
        # First write request won't have since tokens need to be populated on the client first
        with self._capture_requests("first upsert_item: no session token") as requests:
            container.upsert_item(body={'id': '0' + str(uuid.uuid4()), 'pk': 'mypk'})
        for request in requests:
            assert_no_session_token(request)
        with self._capture_requests("upsert_item: session token sent") as requests:
            up_item = container.upsert_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        for request in requests:
            assert_session_token(request)
        with self._capture_requests("replace_item: session token sent") as requests:
            replaced_item = container.replace_item(item=up_item['id'], body={'id': up_item['id'], 'song': 'song',
                                                                             'pk': 'mypk'})
        for request in requests:
            assert_session_token(request)
        with self._capture_requests("create_item: session token sent") as requests:
            created_document = container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        for request in requests:
            assert_session_token(request)
        response_session_token = created_document.get_response_headers().get(HttpHeaders.SessionToken)
        with self._capture_requests("read_item: session token sent") as requests:
            read_item = container.read_item(item=created_document['id'], partition_key='mypk')
        for request in requests:
            assert_session_token(request)
        with self._capture_requests("second read_item: session token sent") as requests:
            read_item2 = container.read_item(item=created_document['id'], partition_key='mypk')
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
            batch_result = container.execute_item_batch(batch_operations, 'mypk')
        for request in requests:
            assert_session_token(request)
        batch_response_token = batch_result.get_response_headers().get(HttpHeaders.SessionToken)
        assert batch_response_token != response_session_token

        # Should get sent now that we have mwr configuration
        with self._capture_requests("delete_item: session token sent") as requests:
            container.delete_item(replaced_item['id'], replaced_item['pk'])
        for request in requests:
            assert_session_token(request)
        assert db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) is not None
        assert db.client_connection.last_response_headers.get(HttpHeaders.SessionToken) != batch_response_token

        self._skip_unverified_request_checks()


if __name__ == '__main__':
    unittest.main()
