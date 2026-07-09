# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit coverage for Rust query-page routing helpers (no network)."""
from __future__ import annotations

import asyncio
import base64
import json

from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import http_constants
from azure.cosmos import _base as base_helpers
from azure.cosmos._backend.base import BackendResponse, OP_QUERY_ITEMS
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._cosmos_client_connection import CosmosClientConnection as SyncConnection
from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection as AsyncConnection
from azure.cosmos.partition_key import _Empty


class _CapturingSyncBackend:
    def __init__(self, response: BackendResponse) -> None:
        self._response = response
        self.prepared = None

    def execute(self, prepared):
        self.prepared = prepared
        return self._response


class _CapturingAsyncBackend:
    def __init__(self, response: BackendResponse) -> None:
        self._response = response
        self.prepared = None

    async def execute(self, prepared):
        self.prepared = prepared
        return self._response


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


def test_sync_query_backend_eligibility_allows_plain_cross_partition_but_blocks_unsupported_shapes():
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

    assert not eligibility(
        query={"query": "SELECT VALUE COUNT(1) FROM c"},
        options={},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert not eligibility(
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
    assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["West US"]
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 9


def test_sync_query_backend_page_defaults_partition_header_to_cross_partition_for_query_items():
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


def test_async_read_all_backend_eligibility_falls_back_for_unsupported_knobs():
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


def test_sync_read_all_backend_page_builds_cross_partition_query(monkeypatch):
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
    assert prepared.op == OP_QUERY_ITEMS
    assert prepared.container_link == "dbs/db/colls/c"
    assert prepared.partition_key_header == "[]"
    assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["West US"]
    assert b"Select * from root r" in prepared.body_bytes


def test_async_read_all_backend_page_builds_cross_partition_query(monkeypatch):
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
        assert prepared.op == OP_QUERY_ITEMS
        assert prepared.container_link == "dbs/db/colls/c"
        assert prepared.partition_key_header == "[]"
        assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["East US"]
        assert b"Select * from root r" in prepared.body_bytes

    asyncio.run(_run())
