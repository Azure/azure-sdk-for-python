# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the sync session-token tests that exercise query_items.

The originals check the session-token header on each outgoing request by patching
the Python pipeline transport, and check response session tokens. The Rust backend
does not send requests through that transport, so the outgoing-request checks cannot
be observed. Every operation and every response-side assertion still runs in order;
each test then skips, naming the outgoing-request checks it could not verify.
"""

import os
import unittest
import uuid
from contextlib import contextmanager

import pytest

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import DatabaseProxy, PartitionKey
from azure.cosmos.http_constants import HttpHeaders
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range


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
        cls.TEST_DATABASE_ID = "query_items_session_" + uuid.uuid4().hex
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
        The check is recorded and reported by _skip_unverified_request_checks.
        """
        requests = []
        yield requests
        self._unverified_request_checks.append(description)

    def _skip_unverified_request_checks(self):
        # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The Rust-prepared outgoing request is not observable, so the request session-token header checks cannot run.
        pytest.skip("accepted-vnext-change: outgoing request session-token header checks cannot be observed on the Rust path "
                    "(known gap 6); all response-side assertions ran. Unverified request checks: "
                    + "; ".join(self._unverified_request_checks))

    def test_session_token_compound_not_sent_for_single_partition_query_rust(self):
        # Source: tests/test_session.py::TestSession.test_session_token_compound_not_sent_for_single_partition_query
        """
        Verify that when querying with a feed range (single physical partition),
        only that partition's session token is sent, not the entire compound token.
        """
        # control-plane container creation
        test_container_ref = self.key_db.create_container(
            "Container query test" + str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            offer_throughput=11000
        )
        # Data-plane proxy for item/query operations
        test_container = self.created_db.get_container_client(test_container_ref.id)

        try:
            # Create items across multiple partition keys
            for i in range(100):
                test_container.create_item({
                    'id': str(uuid.uuid4()),
                    'pk': f"pk_{i:04d}"
                })

            # Get feed ranges and verify multiple exist
            feed_ranges = list(test_container.read_feed_ranges())
            self.assertGreater(len(feed_ranges), 1, "Expected multiple feed ranges")

            # Capture session token sent with feed range query
            captured_session_token = {}

            def capture_session_token(request):
                captured_session_token['token'] = request.headers.get(HttpHeaders.SessionToken)

            # Query with single feed range
            # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The capture below cannot see the outgoing request headers on the Rust path.
            with self._capture_requests("feed-range query: single-partition session token sent") as requests:
                list(test_container.query_items(
                    query="SELECT * FROM c",
                    feed_range=feed_ranges[0]
                ))
            for request in requests:
                capture_session_token(request)

            # The remaining assertions read the captured request token.
            self._skip_unverified_request_checks()
            # Verify only single partition token was sent
            token = captured_session_token.get('token')
            self.assertIsNotNone(token, "Session token should be present")
            self.assertNotIn(',', token,
                             f"Expected single partition token, got compound token: {token}")

        finally:
            self.key_db.delete_container(test_container_ref)  # control-plane

    def test_session_token_compound_not_sent_for_multi_partition_feed_range_query_rust(self):
        # Source: tests/test_session.py::TestSession.test_session_token_compound_not_sent_for_multi_partition_feed_range_query
        """
        Verify that when querying with a feed range spanning multiple physical partitions,
        each individual request sends only the relevant partition's session token,
        not the entire compound token.
        """
        # control-plane container creation
        test_container_ref = self.key_db.create_container(
            "Container multi partition test" + str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            offer_throughput=11000
        )
        # Data-plane proxy for item/query operations
        test_container = self.created_db.get_container_client(test_container_ref.id)

        try:
            # Create items across multiple partition keys
            for i in range(100):
                test_container.create_item({
                    'id': str(uuid.uuid4()),
                    'pk': f"pk_{i:04d}"
                })

            # Get feed ranges and verify multiple exist
            feed_ranges = list(test_container.read_feed_ranges())
            self.assertGreater(len(feed_ranges), 1, "Expected multiple feed ranges")

            # Create a full-range feed range that spans all physical partitions
            full_range = FeedRangeInternalEpk(
                Range("", "FF", True, False)
            ).to_dict()

            # Capture all session tokens sent across multiple requests
            captured_tokens = []

            def capture_session_token(request):
                token = request.headers.get(HttpHeaders.SessionToken)
                if token:
                    captured_tokens.append(token)

            # Query with full range feed range (spans all partitions)
            # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The capture below cannot see the outgoing request headers on the Rust path.
            with self._capture_requests("full-range feed-range query: single-partition token per request") as requests:
                list(test_container.query_items(
                    query="SELECT * FROM c",
                    feed_range=full_range
                ))
            for request in requests:
                capture_session_token(request)

            # The remaining assertions read the captured request tokens.
            self._skip_unverified_request_checks()
            # Verify each request sent only a single partition token (no commas)
            self.assertGreater(len(captured_tokens), 0, "Expected at least one request with session token")
            for token in captured_tokens:
                self.assertNotIn(',', token,
                                 f"Expected single partition token per request, got compound token: {token}")

        finally:
            self.key_db.delete_container(test_container_ref)  # control-plane

    # The three tests below check that a query targeted at a single partition
    # sends only that partition's session token on every request, including
    # each page and the partition_key entry point.

    def test_feed_range_query_session_token_matches_partition_lsn_rust(self):
        # Source: tests/test_session.py::TestSession.test_feed_range_query_session_token_matches_partition_lsn
        # The token sent for a single feed-range query must be the per-partition
        # token for that partition, not a comma-joined token across partitions.
        test_container_ref = self.key_db.create_container(
            "Container fr token value " + str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            offer_throughput=11000,
        )
        test_container = self.created_db.get_container_client(test_container_ref.id)
        try:
            for i in range(60):
                test_container.create_item({"id": str(uuid.uuid4()), "pk": f"pk_{i:04d}"})

            feed_ranges = list(test_container.read_feed_ranges())
            self.assertGreater(len(feed_ranges), 1, "Expected multiple feed ranges")

            captured = {"token": None}

            def capture(request):
                captured["token"] = request.headers.get(HttpHeaders.SessionToken)

            # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The capture below cannot see the outgoing request headers on the Rust path.
            with self._capture_requests("feed-range query: per-partition 'rangeId:vector' token sent") as requests:
                list(test_container.query_items(
                    query="SELECT * FROM c",
                    feed_range=feed_ranges[0],
                ))
            for request in requests:
                capture(request)

            # The remaining assertions read the captured request token.
            self._skip_unverified_request_checks()
            wire_token = captured["token"]
            self.assertIsNotNone(wire_token, "Expected a SessionToken header to be sent.")
            self.assertNotIn(",", wire_token, f"Got compound token on the wire: {wire_token!r}")

            # Token should be a single 'partitionRangeId:vector' pair.
            self.assertIn(":", wire_token, f"Expected single-partition token shape: {wire_token!r}")
            pk_range_id, _, vector_part = wire_token.partition(":")
            self.assertNotEqual(
                pk_range_id, "", f"Partition range id prefix should not be empty: {wire_token!r}"
            )
            self.assertTrue(vector_part, f"Vector portion should not be empty: {wire_token!r}")

        finally:
            self.key_db.delete_container(test_container_ref)

    def test_feed_range_query_session_token_single_partition_across_pages_rust(self):
        # Source: tests/test_session.py::TestSession.test_feed_range_query_session_token_single_partition_across_pages
        # Every page of a paginated single-partition query must send a single
        # partition token, not a compound one.
        test_container_ref = self.key_db.create_container(
            "Container fr pagination " + str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            offer_throughput=11000,
        )
        test_container = self.created_db.get_container_client(test_container_ref.id)
        try:
            # Build multi-partition session state first so this test can catch
            # regressions that accidentally send a compound token.
            for i in range(60):
                test_container.create_item({"id": str(uuid.uuid4()), "pk": f"pk_{i:04d}"})

            # Then concentrate items on one key so the query spans several
            # pages within one target physical partition.
            for i in range(20):
                test_container.create_item({
                    "id": str(uuid.uuid4()),
                    "pk": "pinned_pk",
                    "i": i,
                })

            feed_ranges = list(test_container.read_feed_ranges())
            self.assertGreater(len(feed_ranges), 1, "Expected multiple feed ranges")

            target_fr = test_container.feed_range_from_partition_key("pinned_pk")

            captured_tokens = []

            def capture(request):
                token = request.headers.get(HttpHeaders.SessionToken)
                if token:
                    captured_tokens.append(token)

            # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The capture below cannot see the outgoing request headers on the Rust path.
            with self._capture_requests("paged feed-range query: single-partition token on every page") as requests:
                pager = test_container.query_items(
                    query="SELECT * FROM c",
                    feed_range=target_fr,
                    max_item_count=2,
                ).by_page()
                page_count = 0
                for page in pager:
                    _ = list(page)
                    page_count += 1
            for request in requests:
                capture(request)

            self.assertGreaterEqual(page_count, 1)
            # The remaining assertions read the captured request tokens.
            self._skip_unverified_request_checks()
            self.assertGreater(len(captured_tokens), 0,
                               "Expected at least one captured SessionToken header across pages.")
            # Every page must carry a single-partition token, and all tokens
            # must reference the same partition range id.
            prefixes = set()
            for token in captured_tokens:
                self.assertNotIn(
                    ",", token,
                    f"Compound token leaked on a paginated request: {token!r}",
                )
                self.assertIn(":", token, f"Bad token shape on paginated request: {token!r}")
                prefixes.add(token.split(":", 1)[0])
            self.assertEqual(
                len(prefixes), 1,
                f"Single-partition query produced tokens for multiple partition range ids: {prefixes}",
            )
        finally:
            self.key_db.delete_container(test_container_ref)

    def test_query_with_partition_key_only_sends_single_partition_token_rust(self):
        # Source: tests/test_session.py::TestSession.test_query_with_partition_key_only_sends_single_partition_token
        # A query scoped by partition_key (not feed_range) must also send only
        # the relevant partition's token.
        test_container_ref = self.key_db.create_container(
            "Container pk-only session " + str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            offer_throughput=11000,
        )
        test_container = self.created_db.get_container_client(test_container_ref.id)
        try:
            for i in range(60):
                test_container.create_item({"id": str(uuid.uuid4()), "pk": f"pk_{i:04d}"})

            captured_tokens = []

            def capture(request):
                token = request.headers.get(HttpHeaders.SessionToken)
                if token:
                    captured_tokens.append(token)

            # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The capture below cannot see the outgoing request headers on the Rust path.
            with self._capture_requests("partition_key query: single-partition token sent") as requests:
                list(test_container.query_items(
                    query="SELECT * FROM c WHERE c.pk = @pk",
                    parameters=[{"name": "@pk", "value": "pk_0001"}],
                    partition_key="pk_0001",
                ))
            for request in requests:
                capture(request)

            # The remaining assertions read the captured request tokens.
            self._skip_unverified_request_checks()
            self.assertGreater(len(captured_tokens), 0,
                               "Expected at least one request with a SessionToken header.")
            for token in captured_tokens:
                self.assertNotIn(
                    ",", token,
                    f"partitionKey-only query leaked a compound token: {token!r}",
                )
        finally:
            self.key_db.delete_container(test_container_ref)

    def test_session_token_with_space_in_container_name_rust(self):
        # Source: tests/test_session.py::TestSession.test_session_token_with_space_in_container_name

        # Session token should not be sent for control plane operations
        # control-plane container creation
        # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). Each capture below cannot see the outgoing request headers on the Rust path.
        with self._capture_requests("create_container: no session token") as requests:
            test_container_ref = self.key_db.create_container(
                "Container with space" + str(uuid.uuid4()),
                PartitionKey(path="/pk")
            )
        for request in requests:
            assert_no_session_token(request)
        # Data-plane proxy for data operations
        test_container = self.created_db.get_container_client(test_container_ref.id)
        try:
            # Session token should be sent for document read/batch requests only - verify it is not sent for write requests
            with self._capture_requests("create_item: no session token") as requests:
                created_document = test_container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
            for request in requests:
                assert_no_session_token(request)
            response_session_token = created_document.get_response_headers().get(HttpHeaders.SessionToken)
            with self._capture_requests("read_item: session token sent") as requests:
                read_item = test_container.read_item(item=created_document['id'], partition_key='mypk')
            for request in requests:
                assert_session_token(request)
            with self._capture_requests("query_items: session token sent") as requests:
                query_iterable = test_container.query_items(
                    "SELECT * FROM c WHERE c.id = '" + str(created_document['id']) + "'",
                    partition_key='mypk')
                for _ in query_iterable:
                    pass
            for request in requests:
                assert_session_token(request)

            assert (read_item.get_response_headers().get(HttpHeaders.SessionToken) ==
                    response_session_token)
        finally:
            self.key_db.delete_container(test_container_ref)  # control-plane

        self._skip_unverified_request_checks()


if __name__ == '__main__':
    unittest.main()
