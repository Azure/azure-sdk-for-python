# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests that ``read_timeout`` is honored by async query operations.

A caller can pass ``read_timeout`` per call (e.g. ``container.query_items(...
read_timeout=X)``) or set it on the client constructor / connection policy.
These tests use a capturing transport to confirm the value actually reaches
the wire for each query entry point and that per-call beats client-level.
"""

import unittest
from typing import Any, Optional

import pytest
from azure.core.pipeline.transport import AioHttpTransport

import test_config
from azure.cosmos import documents
from azure.cosmos.aio import CosmosClient


def _is_query_document_fetch(url: str) -> bool:
    """True for query/result fetches against ``/docs``.

    Filters out SDK-internal calls (partition-range fetches, container
    properties reads, account-info probes) as well as non-document query
    surfaces that are asserted separately in dedicated tests.
    """
    stripped = url.rstrip("/")
    return stripped.endswith("/docs")


class _AsyncCaptureTransport(AioHttpTransport):
    """Forwards every request and records the timeout values used on the wire."""

    def __init__(self):
        super().__init__()
        self.captured: list[dict[str, Any]] = []

    async def send(self, request, **kwargs):
        self.captured.append({
            "url": request.url,
            "method": request.method,
            "read_timeout": kwargs.get("read_timeout"),
            "connection_timeout": kwargs.get("connection_timeout"),
        })
        return await super().send(request, **kwargs)

    def query_document_fetch_read_timeouts(self) -> list[Optional[float]]:
        return [c["read_timeout"] for c in self.captured if _is_query_document_fetch(c["url"])]


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADQuery
class TestReadTimeoutPropagationAsync(unittest.IsolatedAsyncioTestCase):
    """``read_timeout`` propagation tests for the async query surface."""

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    SINGLE_PARTITION_ID = configs.TEST_SINGLE_PARTITION_CONTAINER_ID
    MULTI_PARTITION_ID = configs.TEST_MULTI_PARTITION_CONTAINER_ID

    @classmethod
    def setUpClass(cls):
        if cls.masterKey == "[YOUR_KEY_HERE]" or cls.host == "[YOUR_ENDPOINT_HERE]":
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' to run the tests.")

    async def asyncSetUp(self):
        """Seeds a few items once per class with the master key."""
        if getattr(self.__class__, "_seeded", False):
            return
        async with CosmosClient(self.host, self.masterKey) as seed:
            db = seed.get_database_client(self.TEST_DATABASE_ID)
            for cid in (self.SINGLE_PARTITION_ID, self.MULTI_PARTITION_ID):
                c = db.get_container_client(cid)
                seeded_count = 0
                seed_failures = []
                for i in range(3):
                    try:
                        await c.upsert_item({
                            "id": f"read_timeout_seed_{cid}_{i}_async",
                            "pk": f"pk{i}",
                        })
                        seeded_count += 1
                    except Exception as exc:
                        seed_failures.append(f"{type(exc).__name__}: {exc}")
                if seeded_count == 0:
                    raise RuntimeError(
                        f"Failed to seed any items into {cid}. "
                        f"Seed errors: {seed_failures}"
                    )
        self.__class__._seeded = True

    def _build_client(self, capture: _AsyncCaptureTransport, **kw) -> CosmosClient:
        """Builds a client routed through the capturing transport."""
        return self.configs.create_data_client_async(transport=capture, **kw)

    def _assert_all_query_document_fetch_read_timeouts_equal(
        self, capture: _AsyncCaptureTransport, expected: float
    ) -> None:
        observed = capture.query_document_fetch_read_timeouts()
        assert observed, (
            "no /docs query requests captured; the test did not run a document query. "
            "captured={}".format(capture.captured)
        )
        bad = [v for v in observed if v != expected]
        assert not bad, (
            "document query request used read_timeout={} (expected {}). "
            "all /docs query read_timeouts: {}. all captures: {}".format(
                bad, expected, observed, capture.captured
            )
        )

    async def test_per_call_read_timeout_propagates_to_single_partition_query_async(self):
        """Per-call ``read_timeout`` reaches the wire for a single-partition query."""
        capture = _AsyncCaptureTransport()
        client = self._build_client(capture)
        try:
            container = (
                client.get_database_client(self.TEST_DATABASE_ID)
                .get_container_client(self.SINGLE_PARTITION_ID)
            )
            _ = [item async for item in container.query_items(
                query="SELECT * FROM c",
                partition_key="pk0",
                read_timeout=17.0,
            )]
        finally:
            await client.close()
        self._assert_all_query_document_fetch_read_timeouts_equal(capture, 17.0)

    async def test_per_call_read_timeout_propagates_to_cross_partition_query_async(self):
        """Per-call ``read_timeout`` reaches the wire for a cross-partition query."""
        capture = _AsyncCaptureTransport()
        client = self._build_client(capture)
        try:
            container = (
                client.get_database_client(self.TEST_DATABASE_ID)
                .get_container_client(self.MULTI_PARTITION_ID)
            )
            _ = [item async for item in container.query_items(
                query="SELECT * FROM c",
                read_timeout=18.0,
            )]
        finally:
            await client.close()
        self._assert_all_query_document_fetch_read_timeouts_equal(capture, 18.0)

    async def test_per_call_read_timeout_propagates_to_change_feed_async(self):
        """Per-call ``read_timeout`` reaches the wire for change-feed reads."""
        capture = _AsyncCaptureTransport()
        client = self._build_client(capture)
        try:
            container = (
                client.get_database_client(self.TEST_DATABASE_ID)
                .get_container_client(self.SINGLE_PARTITION_ID)
            )
            _ = [item async for item in container.query_items_change_feed(
                start_time="Beginning",
                read_timeout=19.0,
            )]
        finally:
            await client.close()
        self._assert_all_query_document_fetch_read_timeouts_equal(capture, 19.0)

    async def test_per_call_read_timeout_propagates_to_database_query_containers_async(self):
        """Per-call ``read_timeout`` reaches the wire when querying containers."""
        capture = _AsyncCaptureTransport()
        client = self._build_client(capture)
        try:
            db = client.get_database_client(self.TEST_DATABASE_ID)
            _ = [c async for c in db.query_containers(
                query="SELECT * FROM c",
                read_timeout=20.0,
            )]
        finally:
            await client.close()
        # query_containers hits the /colls endpoint.
        observed = [c["read_timeout"] for c in capture.captured if "/colls" in c["url"]]
        assert observed, "no /colls request captured: {}".format(capture.captured)
        assert all(v == 20.0 for v in observed), (
            "db.query_containers dropped per-call read_timeout. captured={}".format(
                capture.captured
            )
        )

    async def test_per_call_read_timeout_propagates_to_client_query_databases_async(self):
        """Per-call ``read_timeout`` reaches the wire when querying databases."""
        capture = _AsyncCaptureTransport()
        client = self._build_client(capture)
        try:
            _ = [d async for d in client.query_databases(
                query="SELECT * FROM c",
                read_timeout=21.0,
            )]
        finally:
            await client.close()
        # query_databases hits the /dbs endpoint with no collection suffix.
        observed = [c["read_timeout"] for c in capture.captured if "/dbs" in c["url"]]
        assert observed, "no /dbs request captured: {}".format(capture.captured)
        assert all(v == 21.0 for v in observed), (
            "client.query_databases dropped per-call read_timeout. captured={}".format(
                capture.captured
            )
        )

    async def test_per_call_read_timeout_overrides_client_for_query_async(self):
        """Per-call ``read_timeout`` wins over the value set on the client."""
        capture = _AsyncCaptureTransport()
        client = self._build_client(capture, read_timeout=33.0)
        try:
            container = (
                client.get_database_client(self.TEST_DATABASE_ID)
                .get_container_client(self.SINGLE_PARTITION_ID)
            )
            _ = [item async for item in container.query_items(
                query="SELECT * FROM c",
                partition_key="pk0",
                read_timeout=5.0,
            )]
        finally:
            await client.close()
        self._assert_all_query_document_fetch_read_timeouts_equal(capture, 5.0)

    async def test_client_level_read_timeout_kwarg_propagates_to_queries_async(self):
        """``read_timeout`` set on the client constructor reaches the wire for queries."""
        capture = _AsyncCaptureTransport()
        client = self._build_client(capture, read_timeout=22.0)
        try:
            assert client.client_connection.connection_policy.ReadTimeout == 22.0
            container = (
                client.get_database_client(self.TEST_DATABASE_ID)
                .get_container_client(self.SINGLE_PARTITION_ID)
            )
            _ = [item async for item in container.query_items(
                query="SELECT * FROM c",
                partition_key="pk0",
            )]
        finally:
            await client.close()
        self._assert_all_query_document_fetch_read_timeouts_equal(capture, 22.0)

    async def test_connection_policy_read_timeout_propagates_to_queries_async(self):
        """``ReadTimeout`` set on the connection policy reaches the wire for queries."""
        cp = documents.ConnectionPolicy()
        cp.DisableSSLVerification = self.configs.is_emulator
        cp.ReadTimeout = 23.0
        capture = _AsyncCaptureTransport()
        client = self._build_client(capture, connection_policy=cp)
        try:
            container = (
                client.get_database_client(self.TEST_DATABASE_ID)
                .get_container_client(self.SINGLE_PARTITION_ID)
            )
            _ = [item async for item in container.query_items(
                query="SELECT * FROM c",
                partition_key="pk0",
            )]
        finally:
            await client.close()
        self._assert_all_query_document_fetch_read_timeouts_equal(capture, 23.0)


if __name__ == "__main__":
    unittest.main()
