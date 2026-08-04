# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Fault-injection tests for per-call timeout propagation to the metadata
"setup" calls a query makes before its first page: the container read, the
``/pkranges`` partition-key-ranges fetch, and the query-plan fetch.

They run end to end against a live account (or the emulator), using a recording
transport that captures the ``connection_timeout`` / ``read_timeout`` the SDK
hands to the wire for each request, plus an injected delay to exercise the
operation deadline:

* **Cold start** -- a per-call ``read_timeout`` / ``connection_timeout`` set on
  ``query_items`` reaches the container read, the query plan, and ``/pkranges``,
  while the forced-short account probe does not inherit them.
* **Post-split** -- after the routing map is force-refreshed (the ``410 Gone``
  path a partition split triggers), the re-issued ``/pkranges`` fetch still
  carries the caller's per-call timeouts.
* **Operation deadline** -- with the query-plan fetch delayed past a tight
  ``timeout``, the query raises ``CosmosClientTimeoutError`` during the setup
  phase, before the ``/pkranges`` fan-out is issued.

The recording transport observes ``connection_timeout`` / ``read_timeout`` as
they reach the transport ``send`` call, so a regression that drops a per-call
timeout on a setup call surfaces here as the client default instead of the
value the test set.
"""

import re
import unittest
from time import sleep
from urllib.parse import urlparse

import pytest

import test_config
from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.http_constants import HttpHeaders

from _fault_injection_transport import FaultInjectionTransport


def _classify_request(request):
    """Bucket an outgoing request by URL/header so the test can assert on the
    metadata setup calls independently of the page fetch."""
    url = request.url or ""
    headers = request.headers or {}
    if "/pkranges" in url:
        return "pkranges"
    if "/docs" in url:
        flag = headers.get(HttpHeaders.IsQueryPlanRequest)
        if flag is not None and str(flag).lower() == "true":
            return "query_plan"
        return "page_fetch"
    if re.search(r"/colls/[^/]+/?$", urlparse(url).path):
        return "container_read"
    if "/dbs/" not in url:
        return "account_probe"
    return "other"


def _is_query_plan(request):
    return _classify_request(request) == "query_plan"


class _RecordingFaultTransport(FaultInjectionTransport):
    """Records the per-request ``connection_timeout`` / ``read_timeout`` handed
    to the transport, and optionally sleeps before a matching request so the
    operation deadline can be exercised without depending on real latency."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.records = []
        self._delays = []

    def add_delay(self, predicate, seconds):
        self._delays.append((predicate, seconds))

    def send(self, request, *, proxies=None, **kwargs):
        self.records.append({
            "kind": _classify_request(request),
            "url": request.url,
            "connection_timeout": kwargs.get("connection_timeout"),
            "read_timeout": kwargs.get("read_timeout"),
        })
        for predicate, seconds in self._delays:
            if predicate(request):
                sleep(seconds)
                break
        return super().send(request, proxies=proxies, **kwargs)

    def records_for(self, kind):
        return [r for r in self.records if r["kind"] == kind]


@pytest.mark.cosmosEmulator
class TestMetadataTimeoutPropagation(unittest.TestCase):
    """End-to-end propagation of per-call timeouts to the metadata setup calls."""

    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    # A cross-partition aggregate forces the cross-partition pipeline: an
    # optimistic attempt, then a query-plan fetch, then a /pkranges fan-out.
    QUERY = "SELECT VALUE COUNT(1) FROM c"

    # Per-call values that are deliberately not the client/policy defaults, so a
    # match proves the caller's value -- not the default -- reached the wire.
    READ_TIMEOUT = 33
    CONNECTION_TIMEOUT = 7

    def _cold_client(self, transport):
        # A fresh client => cold container-properties and routing caches, so the
        # setup calls actually go on the wire.
        return CosmosClient(self.host, self.master_key, transport=transport)

    def test_cold_start_per_call_timeouts_reach_setup_calls(self):
        transport = _RecordingFaultTransport()
        client = self._cold_client(transport)
        try:
            container = client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)
            list(container.query_items(
                query=self.QUERY,
                enable_cross_partition_query=True,
                read_timeout=self.READ_TIMEOUT,
                connection_timeout=self.CONNECTION_TIMEOUT,
            ))
        finally:
            client.close()

        for kind in ("container_read", "query_plan", "pkranges"):
            recs = transport.records_for(kind)
            self.assertTrue(recs, "expected at least one {} request on a cold client".format(kind))
            for r in recs:
                self.assertEqual(
                    r["read_timeout"], self.READ_TIMEOUT,
                    "{} dropped the per-call read_timeout (got {})".format(kind, r["read_timeout"]))
                self.assertEqual(
                    r["connection_timeout"], self.CONNECTION_TIMEOUT,
                    "{} dropped the per-call connection_timeout (got {})".format(kind, r["connection_timeout"]))

        # The forced-short failover probe must never inherit a caller's per-call
        # values -- that is what keeps a generous read_timeout from slowing
        # regional failover.
        for r in transport.records_for("account_probe"):
            self.assertNotEqual(r["read_timeout"], self.READ_TIMEOUT)
            self.assertNotEqual(r["connection_timeout"], self.CONNECTION_TIMEOUT)

    def test_change_feed_cold_start_carries_per_call_timeouts(self):
        # Change feed resolves its feed range to a physical partition through its
        # own /pkranges fetch -- a separate code path from the query pipeline (it
        # never fetches a query plan). A per-call timeout must reach that fetch
        # and the container read the same way it does for a query.
        transport = _RecordingFaultTransport()
        client = self._cold_client(transport)
        try:
            container = client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)
            list(container.query_items_change_feed(
                is_start_from_beginning=True,
                read_timeout=self.READ_TIMEOUT,
                connection_timeout=self.CONNECTION_TIMEOUT,
            ))
        finally:
            client.close()

        for kind in ("container_read", "pkranges"):
            recs = transport.records_for(kind)
            self.assertTrue(recs, "expected at least one {} request on a cold change feed".format(kind))
            for r in recs:
                self.assertEqual(
                    r["read_timeout"], self.READ_TIMEOUT,
                    "change-feed {} dropped the per-call read_timeout (got {})".format(kind, r["read_timeout"]))
                self.assertEqual(
                    r["connection_timeout"], self.CONNECTION_TIMEOUT,
                    "change-feed {} dropped the per-call connection_timeout (got {})".format(
                        kind, r["connection_timeout"]))

        # The forced-short failover probe must not inherit the caller's values here either.
        for r in transport.records_for("account_probe"):
            self.assertNotEqual(r["read_timeout"], self.READ_TIMEOUT)
            self.assertNotEqual(r["connection_timeout"], self.CONNECTION_TIMEOUT)

    def test_post_split_pkranges_refresh_carries_per_call_timeouts(self):
        transport = _RecordingFaultTransport()
        client = self._cold_client(transport)
        try:
            container = client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)
            # Warm the caches with default timeouts.
            list(container.query_items(query=self.QUERY, enable_cross_partition_query=True))

            # Simulate the post-split refresh: clearing the routing map forces the
            # next query to re-issue /pkranges, exactly as the 410-Gone path does.
            client.client_connection._routing_map_provider.clear_cache()  # pylint: disable=protected-access
            transport.records.clear()

            list(container.query_items(
                query=self.QUERY,
                enable_cross_partition_query=True,
                read_timeout=44,
                connection_timeout=9,
            ))
        finally:
            client.close()

        pkranges = transport.records_for("pkranges")
        self.assertTrue(pkranges, "a /pkranges refresh should occur after the routing cache is cleared")
        for r in pkranges:
            self.assertEqual(r["read_timeout"], 44,
                             "the post-split /pkranges refresh dropped the per-call read_timeout")
            self.assertEqual(r["connection_timeout"], 9,
                             "the post-split /pkranges refresh dropped the per-call connection_timeout")

    def test_operation_deadline_halts_setup_phase(self):
        transport = _RecordingFaultTransport()
        # Delay the query-plan fetch past the operation deadline. With timeout=1
        # and a 2s query plan, the setup phase exceeds the budget, so the query
        # raises CosmosClientTimeoutError before it issues the /pkranges fan-out.
        transport.add_delay(_is_query_plan, 2.0)
        client = self._cold_client(transport)
        try:
            container = client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)
            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                list(container.query_items(query=self.QUERY, enable_cross_partition_query=True, timeout=1))
        finally:
            client.close()

        # The deadline tripped during the setup phase: the /pkranges fan-out
        # (which follows the query plan) never went out.
        self.assertEqual(transport.records_for("pkranges"), [],
                         "the operation deadline should halt the query during the setup phase, "
                         "before the /pkranges fan-out is issued")


if __name__ == "__main__":
    unittest.main()

