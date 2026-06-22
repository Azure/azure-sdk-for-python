# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Async fault-injection tests for per-call timeout propagation to the metadata
calls a query makes before its first page (container read, ``/pkranges``, query
plan). Async counterpart of ``test_metadata_timeout_propagation.py``, reusing its
request classifier so both suites bucket requests the same way.

* Cold start -- a per-call ``read_timeout`` / ``connection_timeout`` reaches the
  three metadata calls; the forced-short account probe does not inherit them.
* Post-split -- the re-issued ``/pkranges`` fetch still carries them.
* Operation deadline -- a delayed query plan makes the query raise
  ``CosmosClientTimeoutError`` before the ``/pkranges`` fan-out goes out.
"""

import asyncio
import unittest

import pytest

import test_config
from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions

from _fault_injection_transport_async import FaultInjectionTransportAsync
# Reuse the sync suite's request classifier so both buckets requests identically.
from test_metadata_timeout_propagation import _classify_request, _is_query_plan


class _RecordingFaultTransportAsync(FaultInjectionTransportAsync):
    """Records the per-request ``connection_timeout`` / ``read_timeout`` handed
    to the transport, and optionally awaits a delay before a matching request so
    the operation deadline can be exercised without depending on real latency."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.records = []
        self._delays = []

    def add_delay(self, predicate, seconds):
        self._delays.append((predicate, seconds))

    async def send(self, request, *, stream=False, proxies=None, **config):
        self.records.append({
            "kind": _classify_request(request),
            "url": request.url,
            "connection_timeout": config.get("connection_timeout"),
            "read_timeout": config.get("read_timeout"),
        })
        for predicate, seconds in self._delays:
            if predicate(request):
                await asyncio.sleep(seconds)
                break
        return await super().send(request, stream=stream, proxies=proxies, **config)

    def records_for(self, kind):
        return [r for r in self.records if r["kind"] == kind]


@pytest.mark.cosmosEmulator
class TestMetadataTimeoutPropagationAsync(unittest.IsolatedAsyncioTestCase):
    """End-to-end propagation of per-call timeouts to the metadata setup calls
    on the asynchronous client."""

    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    # A cross-partition aggregate forces the full pipeline: a query-plan fetch
    # then a /pkranges fan-out. The async query_items enables cross-partition on
    # its own (no partition key) and does not accept enable_cross_partition_query,
    # which would leak to the transport -- so, unlike the sync sibling, we omit it.
    QUERY = "SELECT VALUE COUNT(1) FROM c"

    # Per-call values that are deliberately not the client/policy defaults, so a
    # match proves the caller's value -- not the default -- reached the wire.
    READ_TIMEOUT = 33
    CONNECTION_TIMEOUT = 7

    def _cold_client(self, transport):
        # A fresh client => cold container-properties and routing caches, so the
        # setup calls actually go on the wire.
        return CosmosClient(self.host, self.master_key, transport=transport)

    async def test_cold_start_per_call_timeouts_reach_setup_calls(self):
        transport = _RecordingFaultTransportAsync()
        async with self._cold_client(transport) as client:
            container = client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)
            _ = [item async for item in container.query_items(
                query=self.QUERY,
                read_timeout=self.READ_TIMEOUT,
                connection_timeout=self.CONNECTION_TIMEOUT,
            )]

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

    async def test_change_feed_cold_start_carries_per_call_timeouts(self):
        # Change feed resolves its feed range to a physical partition through its
        # own /pkranges fetch -- a separate code path from the query pipeline (it
        # never fetches a query plan). A per-call timeout must reach that fetch
        # and the container read the same way it does for a query.
        transport = _RecordingFaultTransportAsync()
        async with self._cold_client(transport) as client:
            container = client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)
            _ = [item async for item in container.query_items_change_feed(
                is_start_from_beginning=True,
                read_timeout=self.READ_TIMEOUT,
                connection_timeout=self.CONNECTION_TIMEOUT,
            )]

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

    async def test_post_split_pkranges_refresh_carries_per_call_timeouts(self):
        transport = _RecordingFaultTransportAsync()
        async with self._cold_client(transport) as client:
            container = client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)
            # Warm the caches with default timeouts.
            _ = [item async for item in container.query_items(query=self.QUERY)]

            # Simulate the post-split refresh: clearing the routing map forces the
            # next query to re-issue /pkranges, exactly as the 410-Gone path does.
            client.client_connection._routing_map_provider.clear_cache()  # pylint: disable=protected-access
            transport.records.clear()

            _ = [item async for item in container.query_items(
                query=self.QUERY,
                read_timeout=44,
                connection_timeout=9,
            )]

        pkranges = transport.records_for("pkranges")
        self.assertTrue(pkranges, "a /pkranges refresh should occur after the routing cache is cleared")
        for r in pkranges:
            self.assertEqual(r["read_timeout"], 44,
                             "the post-split /pkranges refresh dropped the per-call read_timeout")
            self.assertEqual(r["connection_timeout"], 9,
                             "the post-split /pkranges refresh dropped the per-call connection_timeout")

    async def test_operation_deadline_halts_setup_phase(self):
        transport = _RecordingFaultTransportAsync()
        # Delay the query-plan fetch past the operation deadline. With timeout=1
        # and a 2s query plan, the setup phase exceeds the budget, so the query
        # raises CosmosClientTimeoutError before it issues the /pkranges fan-out.
        transport.add_delay(_is_query_plan, 2.0)
        async with self._cold_client(transport) as client:
            container = client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)
            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                _ = [item async for item in container.query_items(
                    query=self.QUERY, timeout=1)]

        # The deadline tripped during the setup phase: the /pkranges fan-out
        # (which follows the query plan) never went out.
        self.assertEqual(transport.records_for("pkranges"), [],
                         "the operation deadline should halt the query during the setup phase, "
                         "before the /pkranges fan-out is issued")


if __name__ == "__main__":
    unittest.main()

