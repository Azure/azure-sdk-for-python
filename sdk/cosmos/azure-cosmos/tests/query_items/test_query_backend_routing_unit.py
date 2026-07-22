# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit coverage for Rust query-page routing helpers (no network).

These pin the query paging behavior: ``query_items`` and ``read_all_items`` fetch one page
at a time through the backend's paged handoff (``execute_pages``), not the
single-reply path; and the Python-side eligibility gates decide when a page may go
to the rust backend versus the legacy HTTP path. The old Python SQL-regex scan is
gone -- cross-partition shapes (COUNT, ORDER BY, ...) are no longer blocked here;
the driver's own reply is authoritative. Options the rust page path cannot
represent still fall back to legacy. All fakes, no network.
"""
from __future__ import annotations

import asyncio
import base64
import json

from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import http_constants
from azure.cosmos import _base as base_helpers
from azure.cosmos._backend.base import (
    BackendResponse,
    OP_QUERY_ITEMS,
    OP_READ_ALL_ITEMS,
    PreparedQuery,
    QueryNotSupportedByBackendError,
    QueryPage,
)
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._cosmos_client_connection import CosmosClientConnection as SyncConnection
from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection as AsyncConnection
from azure.cosmos.partition_key import _Empty
from azure.cosmos._query_rust_routing import (
    run_query_page_on_rust_backend,
    run_query_page_on_rust_backend_async,
)


class _CapturingSyncBackend:
    def __init__(self, response: BackendResponse) -> None:
        self._response = response
        self.prepared = None

    def execute_pages(self, prepared):
        self.prepared = prepared
        yield QueryPage(
            status_code=self._response.status_code,
            continuation=(
                self._response.headers.get("x-ms-continuation")
                if self._response.headers
                else None
            ),
            sub_status=self._response.sub_status,
            headers=self._response.headers,
            body=self._response.body,
            diagnostics=self._response.diagnostics,
        )


class _CapturingAsyncBackend:
    def __init__(self, response: BackendResponse) -> None:
        self._response = response
        self.prepared = None

    async def execute_pages(self, prepared):
        self.prepared = prepared
        yield QueryPage(
            status_code=self._response.status_code,
            continuation=(
                self._response.headers.get("x-ms-continuation")
                if self._response.headers
                else None
            ),
            sub_status=self._response.sub_status,
            headers=self._response.headers,
            body=self._response.body,
            diagnostics=self._response.diagnostics,
        )


def _new_sync_connection() -> SyncConnection:
    conn = SyncConnection.__new__(SyncConnection)
    conn._backend = None
    conn._query_compatibility_mode = SyncConnection._QueryCompatibilityMode.Query
    conn.default_headers = {}
    conn.last_response_headers = CaseInsensitiveDict()
    conn.session = None
    conn.availability_strategy = None
    conn.availability_strategy_executor = None
    return conn


def _new_async_connection() -> AsyncConnection:
    conn = AsyncConnection.__new__(AsyncConnection)
    conn._backend = None
    conn._query_compatibility_mode = AsyncConnection._QueryCompatibilityMode.Query
    conn.default_headers = {}
    conn.last_response_headers = CaseInsensitiveDict()
    conn.session = None
    conn.availability_strategy = None
    conn.availability_strategy_max_concurrency = None
    return conn


def test_sync_query_backend_eligibility_allows_cross_partition_but_blocks_unrepresentable_options():
    """Sync query eligibility gate. Cross-partition queries (including COUNT and
    ORDER BY) are now eligible because the old Python SQL-regex scan was removed --
    the driver's reply decides whether it can run them. But options the rust page
    path cannot represent (``enableCrossPartitionQuery=False``, a ``feed_range``, a
    MultiHash partition key, ``read_timeout``, ``availability_strategy``, full-text
    score scope, query advice) still block it and keep the query on the legacy path.
    """
    conn = _new_sync_connection()
    conn._backend = object()
    eligibility = conn._CosmosClientConnection__CanUseRustBackendForQueryPage

    assert eligibility(
        query={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"]},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert eligibility(
        query={"query": "SELECT * FROM c"},
        options={},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert eligibility(
        query={"query": "SELECT * FROM c"},
        options={"partitionKey": _Empty()},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    # These cross-partition shapes were once blocked by a Python-side SQL regex
    # scan for clauses the Rust driver couldn't run across partitions. That scan
    # was removed (see can_use_rust_backend_for_query_page's docstring): the query
    # text is no longer inspected here, so these are now eligible and the driver's
    # own reply is authoritative for whether it can actually run them.
    assert eligibility(
        query={"query": "SELECT VALUE COUNT(1) FROM c"},
        options={},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert eligibility(
        query={"query": "SELECT * FROM c ORDER BY c.ts DESC"},
        options={},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert not eligibility(
        query={"query": "SELECT * FROM c"},
        options={"enableCrossPartitionQuery": False},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert eligibility(
        query={"query": "SELECT * FROM c ORDER BY c.ts DESC"},
        options={"partitionKey": ["tenant-a"]},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert not eligibility(
        query={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"]},
        kwargs={"feed_range": {"min": "AA", "max": "FF"}},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert not eligibility(
        query={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"]},
        kwargs={},
        container_properties={
            "partitionKey": {"paths": ["/pk1", "/pk2"], "kind": "MultiHash", "version": 2}
        },
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )
    assert not eligibility(
        query={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"], "read_timeout": 0.2},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )
    assert not eligibility(
        query={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"], Constants.Kwargs.AVAILABILITY_STRATEGY: False},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )
    assert not eligibility(
        query={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"], "fullTextScoreScope": "Local"},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )
    assert not eligibility(
        query={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"], "populateQueryAdvice": True},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )


def test_sync_query_backend_page_builds_prepared_request_and_updates_headers():
    """Sync query page. A rust-served page builds the right ``PreparedQuery`` (op,
    container link, partition-key header, continuation, max item count, forwarded
    excluded-locations and timeout), returns the parsed Documents, decodes the
    index-utilization header, and updates both ``response_headers`` and the response
    hook -- so a rust page is indistinguishable from a legacy one to the caller.
    """
    index_metrics_wire = base64.b64encode(json.dumps({"indexUsed": True}).encode("utf-8")).decode("ascii")
    conn = _new_sync_connection()
    backend = _CapturingSyncBackend(
        BackendResponse(
            status_code=200,
            sub_status=0,
            headers=CaseInsensitiveDict(
                {
                    "x-ms-continuation": "ct-1",
                    http_constants.HttpHeaders.IndexUtilization: index_metrics_wire,
                }
            ),
            body=b'{"Documents":[{"id":"1"}]}',
            diagnostics="diag",
        )
    )
    conn._backend = backend

    response_headers = CaseInsensitiveDict()
    hook_calls = []
    page = conn._CosmosClientConnection__TryQueryPageWithRustBackend(
        path="/dbs/db/colls/c/docs/",
        query_payload={"query": "SELECT * FROM c"},
        options={
            "partitionKey": ["tenant-a"],
            "continuation": "ct-in",
            "maxItemCount": 25,
            Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"],
            Constants.Kwargs.TIMEOUT: 9,
        },
        req_headers={
            http_constants.HttpHeaders.PartitionKey: '["tenant-a"]',
            http_constants.HttpHeaders.IsQuery: "true",
        },
        response_hook=lambda h, b: hook_calls.append((dict(h), b)),
        response_headers=response_headers,
        internal_headers_capture=None,
    )

    assert page is not None
    result, headers = page
    assert result["Documents"][0]["id"] == "1"
    assert headers["x-ms-continuation"] == "ct-1"
    assert response_headers["x-ms-continuation"] == "ct-1"
    assert headers[http_constants.HttpHeaders.IndexUtilization] == {"indexUsed": True}
    assert "x-ms-cosmos-sdk-diagnostics" not in headers
    assert "x-ms-cosmos-sdk-diagnostics" not in response_headers
    assert len(hook_calls) == 1
    assert hook_calls[0][0][http_constants.HttpHeaders.IndexUtilization] == {"indexUsed": True}

    prepared = backend.prepared
    assert prepared is not None
    assert prepared.op == OP_QUERY_ITEMS
    assert prepared.container_link == "dbs/db/colls/c"
    assert prepared.partition_key_header == '["tenant-a"]'
    assert prepared.continuation == "ct-in"
    assert prepared.max_item_count == 25
    assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["West US"]
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 9


def test_sync_query_backend_page_defaults_partition_header_to_cross_partition_for_query_items():
    """Sync query page with no partition key. ``query_items`` defaults the
    partition-key header to the cross-partition marker (``"[]"``), so an unscoped
    query fans out across partitions instead of accidentally targeting just one.
    """
    conn = _new_sync_connection()
    backend = _CapturingSyncBackend(
        BackendResponse(
            status_code=200,
            sub_status=0,
            headers=CaseInsensitiveDict({"x-ms-continuation": "ct-cross"}),
            body=b'{"Documents":[{"id":"x"}]}',
            diagnostics="diag",
        )
    )
    conn._backend = backend

    page = conn._CosmosClientConnection__TryQueryPageWithRustBackend(
        path="/dbs/db/colls/c/docs/",
        query_payload={"query": "SELECT * FROM c"},
        options={},
        req_headers={http_constants.HttpHeaders.IsQuery: "true"},
        response_hook=None,
        response_headers=None,
        internal_headers_capture=None,
    )

    assert page is not None
    prepared = backend.prepared
    assert prepared is not None
    assert prepared.partition_key_header == "[]"


def test_async_query_backend_page_builds_prepared_request_and_updates_headers():
    """Async twin of the query-page build/headers test."""
    async def _run() -> None:
        index_metrics_wire = base64.b64encode(json.dumps({"indexUsed": True}).encode("utf-8")).decode("ascii")
        conn = _new_async_connection()
        backend = _CapturingAsyncBackend(
            BackendResponse(
                status_code=200,
                sub_status=0,
                headers=CaseInsensitiveDict(
                    {
                        "x-ms-continuation": "ct-async",
                        http_constants.HttpHeaders.IndexUtilization: index_metrics_wire,
                    }
                ),
                body=b'{"Documents":[{"id":"2"}]}',
                diagnostics="diag",
            )
        )
        conn._backend = backend

        response_headers = CaseInsensitiveDict()
        hook_calls = []
        result = await conn._CosmosClientConnection__TryQueryPageWithRustBackend(
            path="/dbs/db/colls/c/docs/",
            query_payload={"query": "SELECT * FROM c"},
            options={
                "partitionKey": ["tenant-a"],
                Constants.Kwargs.EXCLUDED_LOCATIONS: ["East US"],
                Constants.Kwargs.TIMEOUT: 11,
            },
            req_headers={
                http_constants.HttpHeaders.PartitionKey: '["tenant-a"]',
                http_constants.HttpHeaders.IsQuery: "true",
            },
            response_hook=lambda h, b: hook_calls.append((dict(h), b)),
            response_headers=response_headers,
            internal_headers_capture=None,
        )

        assert result is not None
        assert result["Documents"][0]["id"] == "2"
        assert conn.last_response_headers["x-ms-continuation"] == "ct-async"
        assert response_headers["x-ms-continuation"] == "ct-async"
        assert conn.last_response_headers[http_constants.HttpHeaders.IndexUtilization] == {"indexUsed": True}
        assert "x-ms-cosmos-sdk-diagnostics" not in conn.last_response_headers
        assert "x-ms-cosmos-sdk-diagnostics" not in response_headers
        assert len(hook_calls) == 1
        assert hook_calls[0][0][http_constants.HttpHeaders.IndexUtilization] == {"indexUsed": True}

        prepared = backend.prepared
        assert prepared is not None
        assert prepared.op == OP_QUERY_ITEMS
        assert prepared.container_link == "dbs/db/colls/c"
        assert prepared.partition_key_header == '["tenant-a"]'
        assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["East US"]
        assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 11

    asyncio.run(_run())


def test_async_query_backend_eligibility_honors_unsupported_request_options():
    """Async query eligibility gate: an unrepresentable option (``populateQueryAdvice``)
    blocks the rust page path on the async connection too.
    """
    conn = _new_async_connection()
    conn._backend = object()
    eligibility = conn._CosmosClientConnection__CanUseRustBackendForQueryPage

    assert not eligibility(
        query={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"], "populateQueryAdvice": True},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )


def test_sync_read_all_backend_eligibility_falls_back_for_unsupported_knobs():
    """Sync read_all_items eligibility gate. A plain document read-feed is eligible,
    but unsupported knobs each fall back to legacy: query metrics,
    ``availability_strategy``, ``read_timeout``, change-feed state, a ``feed_range``,
    a specific partition-key-range id, query-plan calls, and non-document resources.
    """
    conn = _new_sync_connection()
    conn._backend = object()
    eligibility = conn._CosmosClientConnection__CanUseRustBackendForReadAllItemsPage

    assert eligibility(
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={"populateQueryMetrics": True},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={Constants.Kwargs.AVAILABILITY_STRATEGY: False},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={"read_timeout": 10},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={"changeFeedState": {"ct": "value"}},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={},
        kwargs={"feed_range": {"Range": {"min": "AA", "max": "BB"}}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id="0",
    )
    assert not eligibility(
        options={},
        kwargs={},
        is_query_plan=True,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Collection,
        partition_key_range_id=None,
    )


def test_async_read_all_backend_eligibility_falls_back_for_unsupported_knobs():
    """Async twin of the read_all_items eligibility gate."""
    conn = _new_async_connection()
    conn._backend = object()
    eligibility = conn._CosmosClientConnection__CanUseRustBackendForReadAllItemsPage

    assert eligibility(
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={"populateQueryMetrics": False},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={Constants.Kwargs.AVAILABILITY_STRATEGY: True},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={"read_timeout": 1},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={"changeFeedState": {"ct": "value"}},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={},
        kwargs={"feed_range": {"Range": {"min": "AA", "max": "BB"}}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id="1",
    )
    assert not eligibility(
        options={},
        kwargs={},
        is_query_plan=True,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Collection,
        partition_key_range_id=None,
    )


def test_sync_read_all_backend_delegates_cross_partition_scope(monkeypatch):
    """Sync read_all_items, whole container. Builds a ``read_all_items`` prepared
    query with the cross-partition header (``"[]"``), no ``PartitionKey`` header, and
    no query text (a native read-feed, not a synthesized SELECT), and still
    propagates headers/session and fires the response hook exactly once.
    """
    conn = _new_sync_connection()
    backend = _CapturingSyncBackend(
        BackendResponse(
            status_code=200,
            sub_status=0,
            headers=CaseInsensitiveDict({"x-ms-continuation": "ct-read-all"}),
            body=b'{"Documents":[{"id":"doc-1"}]}',
            diagnostics="diag",
        )
    )
    conn._backend = backend
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})
    monkeypatch.setattr(base_helpers, "set_session_token_header", lambda *args, **kwargs: None)

    response_headers = CaseInsensitiveDict()
    hook_calls = []
    page = conn._CosmosClientConnection__TryReadAllItemsPageWithRustBackend(
        path="/dbs/db/colls/c/docs/",
        resource_type=http_constants.ResourceType.Document,
        resource_id="coll-rid",
        options={Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"]},
        partition_key_range_id=None,
        response_hook=lambda h, b: hook_calls.append((dict(h), b)),
        response_headers=response_headers,
        internal_headers_capture=None,
        kwargs={},
    )

    assert page is not None
    result, headers = page
    assert result["Documents"][0]["id"] == "doc-1"
    assert headers["x-ms-continuation"] == "ct-read-all"
    assert response_headers["x-ms-continuation"] == "ct-read-all"
    assert len(hook_calls) == 1

    prepared = backend.prepared
    assert prepared is not None
    assert prepared.op == OP_READ_ALL_ITEMS
    assert prepared.container_link == "dbs/db/colls/c"
    assert prepared.partition_key_header == "[]"
    assert http_constants.HttpHeaders.PartitionKey not in prepared.headers
    assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["West US"]
    assert prepared.query is None


def test_async_read_all_backend_delegates_cross_partition_scope(monkeypatch):
    """Async twin of the whole-container read_all_items delegation test."""
    async def _run() -> None:
        conn = _new_async_connection()
        backend = _CapturingAsyncBackend(
            BackendResponse(
                status_code=200,
                sub_status=0,
                headers=CaseInsensitiveDict({"x-ms-continuation": "ct-read-all-async"}),
                body=b'{"Documents":[{"id":"doc-2"}]}',
                diagnostics="diag",
            )
        )
        conn._backend = backend
        monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})

        async def _noop_set_session(*_args, **_kwargs):
            return None

        monkeypatch.setattr(base_helpers, "set_session_token_header_async", _noop_set_session)

        response_headers = CaseInsensitiveDict()
        hook_calls = []
        result = await conn._CosmosClientConnection__TryReadAllItemsPageWithRustBackend(
            path="/dbs/db/colls/c/docs/",
            resource_type=http_constants.ResourceType.Document,
            resource_id="coll-rid",
            options={Constants.Kwargs.EXCLUDED_LOCATIONS: ["East US"]},
            partition_key_range_id=None,
            response_hook=lambda h, b: hook_calls.append((dict(h), b)),
            response_headers=response_headers,
            internal_headers_capture=None,
            kwargs={},
        )

        assert result is not None
        assert result["Documents"][0]["id"] == "doc-2"
        assert conn.last_response_headers["x-ms-continuation"] == "ct-read-all-async"
        assert response_headers["x-ms-continuation"] == "ct-read-all-async"
        assert len(hook_calls) == 1

        prepared = backend.prepared
        assert prepared is not None
        assert prepared.op == OP_READ_ALL_ITEMS
        assert prepared.container_link == "dbs/db/colls/c"
        assert prepared.partition_key_header == "[]"
        assert http_constants.HttpHeaders.PartitionKey not in prepared.headers
        assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["East US"]
        assert prepared.query is None

    asyncio.run(_run())


def test_sync_read_all_backend_page_with_partition_key_uses_native_read_feed(monkeypatch):
    """Sync read_all_items scoped to one partition key. Builds a ``read_all_items``
    prepared query carrying that partition-key header and no query text -- served as
    a native single-partition read-feed, not a synthesized query.
    """
    conn = _new_sync_connection()
    backend = _CapturingSyncBackend(
        BackendResponse(
            status_code=200,
            sub_status=0,
            headers=CaseInsensitiveDict({"x-ms-continuation": "ct-read-all-pk"}),
            body=b'{"Documents":[{"id":"doc-pk"}]}',
            diagnostics="diag",
        )
    )
    conn._backend = backend
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})
    monkeypatch.setattr(base_helpers, "set_session_token_header", lambda *args, **kwargs: None)

    page = conn._CosmosClientConnection__TryReadAllItemsPageWithRustBackend(
        path="/dbs/db/colls/c/docs/",
        resource_type=http_constants.ResourceType.Document,
        resource_id="coll-rid",
        options={"partitionKey": ["tenant-a"]},
        partition_key_range_id=None,
        response_hook=None,
        response_headers=None,
        internal_headers_capture=None,
        kwargs={},
    )

    assert page is not None
    prepared = backend.prepared
    assert prepared is not None
    assert prepared.op == OP_READ_ALL_ITEMS
    assert prepared.partition_key_header == '["tenant-a"]'
    assert prepared.query is None


def test_async_read_all_backend_page_with_partition_key_uses_native_read_feed(monkeypatch):
    """Async twin of the single-partition read_all_items native-read-feed test."""
    async def _run() -> None:
        conn = _new_async_connection()
        backend = _CapturingAsyncBackend(
            BackendResponse(
                status_code=200,
                sub_status=0,
                headers=CaseInsensitiveDict({"x-ms-continuation": "ct-read-all-pk-async"}),
                body=b'{"Documents":[{"id":"doc-pk-async"}]}',
                diagnostics="diag",
            )
        )
        conn._backend = backend
        monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})

        async def _noop_set_session(*_args, **_kwargs):
            return None

        monkeypatch.setattr(base_helpers, "set_session_token_header_async", _noop_set_session)

        result = await conn._CosmosClientConnection__TryReadAllItemsPageWithRustBackend(
            path="/dbs/db/colls/c/docs/",
            resource_type=http_constants.ResourceType.Document,
            resource_id="coll-rid",
            options={"partitionKey": ["tenant-a"]},
            partition_key_range_id=None,
            response_hook=None,
            response_headers=None,
            internal_headers_capture=None,
            kwargs={},
        )

        assert result is not None
        prepared = backend.prepared
        assert prepared is not None
        assert prepared.op == OP_READ_ALL_ITEMS
        assert prepared.partition_key_header == '["tenant-a"]'
        assert prepared.query is None

    asyncio.run(_run())


def test_sync_read_all_backend_page_empty_container(monkeypatch):
    """Sync read_all_items on an empty (or fully-drained) container. Cross-partition
    read_all is routed through the rust query-page path (``SELECT * FROM root r``) and
    still finalizes normally: empty ``Documents`` array, header and session
    propagation, and the response hook fired exactly once.
    """
    conn = _new_sync_connection()
    backend = _CapturingSyncBackend(
        BackendResponse(
            status_code=200,
            sub_status=0,
            headers=CaseInsensitiveDict({"x-ms-session-token": "st-empty"}),
            body=b'{"Documents":[]}',
            diagnostics="diag",
        )
    )
    conn._backend = backend
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})
    monkeypatch.setattr(base_helpers, "set_session_token_header", lambda *args, **kwargs: None)

    response_headers = CaseInsensitiveDict()
    hook_calls = []
    page = conn._CosmosClientConnection__TryReadAllItemsPageWithRustBackend(
        path="/dbs/db/colls/c/docs/",
        resource_type=http_constants.ResourceType.Document,
        resource_id="coll-rid",
        options={},
        partition_key_range_id=None,
        response_hook=lambda h, b: hook_calls.append((dict(h), b)),
        response_headers=response_headers,
        internal_headers_capture=None,
        kwargs={},
    )

    assert page is not None
    result, headers = page
    assert result["Documents"] == []
    assert headers["x-ms-session-token"] == "st-empty"
    assert response_headers["x-ms-session-token"] == "st-empty"
    assert len(hook_calls) == 1
    assert backend.prepared.op == OP_READ_ALL_ITEMS
    assert backend.prepared.query is None


def test_async_read_all_backend_page_empty_container(monkeypatch):
    """Async twin of the empty-container read_all_items test."""
    async def _run() -> None:
        conn = _new_async_connection()
        backend = _CapturingAsyncBackend(
            BackendResponse(
                status_code=200,
                sub_status=0,
                headers=CaseInsensitiveDict({"x-ms-session-token": "st-empty-async"}),
                body=b'{"Documents":[]}',
                diagnostics="diag",
            )
        )
        conn._backend = backend
        monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})

        async def _noop_set_session(*_args, **_kwargs):
            return None

        monkeypatch.setattr(base_helpers, "set_session_token_header_async", _noop_set_session)

        response_headers = CaseInsensitiveDict()
        hook_calls = []
        result = await conn._CosmosClientConnection__TryReadAllItemsPageWithRustBackend(
            path="/dbs/db/colls/c/docs/",
            resource_type=http_constants.ResourceType.Document,
            resource_id="coll-rid",
            options={},
            partition_key_range_id=None,
            response_hook=lambda h, b: hook_calls.append((dict(h), b)),
            response_headers=response_headers,
            internal_headers_capture=None,
            kwargs={},
        )

        assert result is not None
        assert result["Documents"] == []
        assert conn.last_response_headers["x-ms-session-token"] == "st-empty-async"
        assert response_headers["x-ms-session-token"] == "st-empty-async"
        assert len(hook_calls) == 1
        assert backend.prepared.op == OP_READ_ALL_ITEMS
        assert backend.prepared.query is None

    asyncio.run(_run())


def test_sync_driver_unsupported_query_falls_back():
    """Sync: when the backend raises ``QueryNotSupportedByBackendError`` (the driver
    rejects a query plan it cannot run), ``run_query_page_on_rust_backend`` returns
    ``None`` so the caller falls back to the legacy path instead of failing.
    """
    class _UnsupportedBackend:
        def execute_pages(self, prepared):
            del prepared
            raise QueryNotSupportedByBackendError("unsupported query plan")
            yield  # pragma: no cover

    prepared = PreparedQuery(
        op=OP_QUERY_ITEMS,
        container_link="dbs/db/colls/c",
        query="SELECT VALUE COUNT(1) FROM c",
    )

    assert run_query_page_on_rust_backend(_UnsupportedBackend(), prepared) is None


def test_async_driver_unsupported_query_falls_back():
    """Async twin: ``run_query_page_on_rust_backend_async`` returns ``None`` when the
    backend rejects the query, so the caller falls back to legacy.
    """
    class _UnsupportedBackend:
        async def execute_pages(self, prepared):
            del prepared
            raise QueryNotSupportedByBackendError("unsupported query plan")
            yield  # pragma: no cover

    async def _run():
        prepared = PreparedQuery(
            op=OP_QUERY_ITEMS,
            container_link="dbs/db/colls/c",
            query="SELECT * FROM c ORDER BY c.ts",
        )
        assert await run_query_page_on_rust_backend_async(
            _UnsupportedBackend(), prepared
        ) is None

    asyncio.run(_run())


def test_sync_read_all_legacy_fallback_updates_session(monkeypatch):
    """Sync legacy fallback (no backend). The read-feed still calls
    ``_UpdateSessionIfRequired`` and propagates the session token, so a fallback read
    advances the session bookmark exactly like before the migration.
    """
    conn = _new_sync_connection()
    conn._backend = None
    update_calls = []
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})
    monkeypatch.setattr(base_helpers, "set_session_token_header", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        conn,
        "_CosmosClientConnection__Get",
        lambda *_args, **_kwargs: (
            {"Documents": [{"id": "legacy-doc"}]},
            CaseInsensitiveDict({"x-ms-session-token": "st-1"}),
        ),
    )
    monkeypatch.setattr(
        conn,
        "_UpdateSessionIfRequired",
        lambda req_headers, response_result, response_headers: update_calls.append(
            (req_headers, response_result, response_headers)
        ),
    )

    response_headers = CaseInsensitiveDict()
    result, headers = conn._CosmosClientConnection__QueryFeed(
        path="/dbs/db/colls/c/docs/",
        resource_type=http_constants.ResourceType.Document,
        resource_id="coll-rid",
        result_fn=lambda payload: payload["Documents"],
        create_fn=lambda _, item: item,
        query=None,
        options={},
        partition_key_range_id=None,
        response_headers=response_headers,
    )

    assert result[0]["id"] == "legacy-doc"
    assert headers["x-ms-session-token"] == "st-1"
    assert response_headers["x-ms-session-token"] == "st-1"
    assert len(update_calls) == 1


def test_async_read_all_legacy_fallback_updates_session(monkeypatch):
    """Async twin of the legacy-fallback session-update test. The async legacy
    read-feed branch already called ``_UpdateSessionIfRequired`` before this
    migration; this pins it so a future refactor cannot silently drop the session
    update on the async fall-back path, keeping sync, async, and both rust paths
    consistent about advancing the session token.
    """
    async def _run() -> None:
        conn = _new_async_connection()
        conn._backend = None
        update_calls = []
        monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})

        async def _noop_set_session(*_args, **_kwargs):
            return None

        monkeypatch.setattr(base_helpers, "set_session_token_header_async", _noop_set_session)

        async def _fake_get(*_args, **_kwargs):
            return (
                {"Documents": [{"id": "legacy-doc-async"}]},
                CaseInsensitiveDict({"x-ms-session-token": "st-async-1"}),
            )

        monkeypatch.setattr(conn, "_CosmosClientConnection__Get", _fake_get)
        monkeypatch.setattr(
            conn,
            "_UpdateSessionIfRequired",
            lambda req_headers, response_result, response_headers: update_calls.append(
                (req_headers, response_result, response_headers)
            ),
        )

        response_headers = CaseInsensitiveDict()
        result = await conn._CosmosClientConnection__QueryFeed(
            path="/dbs/db/colls/c/docs/",
            resource_type=http_constants.ResourceType.Document,
            id_="coll-rid",
            result_fn=lambda payload: payload["Documents"],
            create_fn=lambda _, item: item,
            query=None,
            options={},
            partition_key_range_id=None,
            response_headers=response_headers,
        )

        assert result[0]["id"] == "legacy-doc-async"
        assert conn.last_response_headers["x-ms-session-token"] == "st-async-1"
        assert response_headers["x-ms-session-token"] == "st-async-1"
        assert len(update_calls) == 1

    asyncio.run(_run())
