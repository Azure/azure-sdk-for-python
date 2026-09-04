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
from unittest.mock import MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import http_constants
from azure.cosmos import _base as base_helpers
from azure.cosmos._backend.base import CosmosBackend
from azure.cosmos._backend.errors import (
    BackendProtocolError,
    PageNotSupportedByBackendError,
    QueryNotSupportedByBackendError,
)
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._backend.contracts import BackendResponse, LegacyOperation, PreparedQuery, QueryPage
from azure.cosmos._backend.operations import OP_LIST_DATABASES, OP_QUERY_DATABASES, OP_QUERY_ITEMS, OP_READ_ALL_ITEMS
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count
from azure.cosmos._backend.rust import _binding_request_from_page as _sync_binding_request_from_page
from azure.cosmos.aio._backend.rust import (
    _binding_request_from_page as _async_binding_request_from_page,
)
from azure.cosmos.aio._backend.base import AsyncCosmosBackend
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._cosmos_client_connection import CosmosClientConnection as SyncConnection
from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection as AsyncConnection
from azure.cosmos.documents import ConnectionPolicy
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.partition_key import _Empty
from azure.cosmos._query_rust_routing import (
    _build_prepared_headers_for_rust_feed_dispatch,
    can_use_rust_backend_for_list_databases_page,
    can_use_rust_backend_for_query_databases_page,
    can_use_rust_backend_for_query_page,
    can_use_rust_backend_for_read_all_items_page,
)


class _CapturingSyncBackend(CosmosBackend):
    """A stand-in for the Rust backend that records the request and replies once.

    These tests never talk to a real Cosmos account. This class keeps whatever
    ``PreparedQuery`` the routing code built, so a test can check exactly what
    would have gone on the wire, and hands back one canned page. ``execute``
    raises because a paged operation must never be dispatched through the
    single-reply path.
    """

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

    def execute(self, prepared):
        raise AssertionError("single-response execution is not expected")


class _CapturingAsyncBackend(AsyncCosmosBackend):
    """Async twin of ``_CapturingSyncBackend``, so both surfaces get the same checks."""

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

    async def execute(self, prepared):
        raise AssertionError("single-response execution is not expected")


class _SequencedSyncBackend(CosmosBackend):
    """A stand-in backend that serves two pages instead of one.

    An account with more databases than fit in one page returns a continuation
    token, and the caller is expected to send it back to get the rest. This fake
    reproduces that: the first call (no continuation) returns ``db-1`` plus a
    token, and any call carrying a token returns ``db-2`` and no token. It also
    records every request, so a test can prove the token really made the round
    trip rather than the second page being fetched from scratch.
    """

    def __init__(self) -> None:
        self.prepared = []

    def execute_pages(self, prepared):
        self.prepared.append(prepared)
        if prepared.continuation is None:
            yield QueryPage(
                status_code=200,
                continuation="next-db-page",
                headers=CaseInsensitiveDict({"x-ms-continuation": "next-db-page"}),
                body=b'{"Databases":[{"id":"db-1"}]}',
            )

        else:
            yield QueryPage(
                status_code=200,
                headers=CaseInsensitiveDict(),
                body=b'{"Databases":[{"id":"db-2"}]}',
            )

    def execute(self, prepared):
        raise AssertionError("single-response execution is not expected")


class _SequencedAsyncBackend(AsyncCosmosBackend):
    """Async twin of ``_SequencedSyncBackend``."""

    def __init__(self) -> None:
        self.prepared = []

    async def execute_pages(self, prepared):
        self.prepared.append(prepared)
        if prepared.continuation is None:
            yield QueryPage(
                status_code=200,
                continuation="next-db-page",
                headers=CaseInsensitiveDict({"x-ms-continuation": "next-db-page"}),
                body=b'{"Databases":[{"id":"db-1"}]}',
            )

        else:
            yield QueryPage(
                status_code=200,
                headers=CaseInsensitiveDict(),
                body=b'{"Databases":[{"id":"db-2"}]}',
            )

    async def execute(self, prepared):
        raise AssertionError("single-response execution is not expected")


def _new_sync_connection() -> SyncConnection:
    """Create a synchronous connection for routing tests."""
    conn = SyncConnection.__new__(SyncConnection)
    conn._backend = LEGACY_BACKEND
    conn._query_compatibility_mode = SyncConnection._QueryCompatibilityMode.Query
    conn.default_headers = {}
    conn.connection_policy = ConnectionPolicy()
    conn._global_endpoint_manager = MagicMock()
    conn._routing_map_provider = MagicMock()
    conn.pipeline_client = MagicMock()
    conn._CosmosClientConnection__container_properties_cache = {}
    conn.last_response_headers = CaseInsensitiveDict()
    conn.session = None
    conn.UseMultipleWriteLocations = False
    conn.master_key = None
    conn.resource_tokens = None
    conn.aad_credentials = None
    conn.client_id = None
    conn.availability_strategy = None
    conn.availability_strategy_executor = None
    return conn


def _new_async_connection() -> AsyncConnection:
    """Create an asynchronous connection for routing tests."""
    conn = AsyncConnection.__new__(AsyncConnection)
    conn._backend = ASYNC_LEGACY_BACKEND
    conn._query_compatibility_mode = AsyncConnection._QueryCompatibilityMode.Query
    conn.default_headers = {}
    conn.connection_policy = ConnectionPolicy()
    conn._global_endpoint_manager = MagicMock()
    conn._routing_map_provider = MagicMock()
    conn.pipeline_client = MagicMock()
    conn._CosmosClientConnection__container_properties_cache = {}
    conn.last_response_headers = CaseInsensitiveDict()
    conn.session = None
    conn.UseMultipleWriteLocations = False
    conn.master_key = None
    conn.resource_tokens = None
    conn.aad_credentials = None
    conn.client_id = None
    conn.availability_strategy = None
    conn.availability_strategy_max_concurrency = None
    return conn


def _run_sync_query_feed(
    conn,
    *,
    query,
    options,
    response_hook=None,
    response_headers=None,
    **kwargs,
):
    """Run one synchronous item-query page through the shared connection."""
    return conn._CosmosClientConnection__QueryFeed(
        "/dbs/db/colls/c/docs/",
        http_constants.ResourceType.Document,
        "collection-rid",
        lambda result: result["Documents"],
        None,
        query,
        options,
        response_hook=response_hook,
        response_headers=response_headers,
        **kwargs,
    )


async def _run_async_query_feed(
    conn,
    *,
    query,
    options,
    response_hook=None,
    response_headers=None,
    **kwargs,
):
    """Run one asynchronous item-query page through the shared connection."""
    return await conn._CosmosClientConnection__QueryFeed(
        "/dbs/db/colls/c/docs/",
        http_constants.ResourceType.Document,
        "collection-rid",
        lambda result: result["Documents"],
        None,
        query,
        options,
        response_hook=response_hook,
        response_headers=response_headers,
        **kwargs,
    )


def _run_sync_read_feed(
    conn,
    *,
    resource_type,
    options,
    response_hook=None,
    response_headers=None,
    **kwargs,
):
    """Call the shared read-feed with either resource type.

    ``list_databases`` and ``read_all_items`` run through the same code inside
    the client connection and are told apart only by resource type. This helper
    fills in the three things that differ -- the URL path, the resource id, and
    the name of the JSON list in the reply -- so a test can switch between the
    two by changing one argument.
    """
    path = "/dbs/" if resource_type == http_constants.ResourceType.Database else "/dbs/db/colls/c/docs/"
    resource_id = None if resource_type == http_constants.ResourceType.Database else "collection-rid"
    envelope = "Databases" if resource_type == http_constants.ResourceType.Database else "Documents"
    return conn._CosmosClientConnection__QueryFeed(
        path,
        resource_type,
        resource_id,
        lambda result: result[envelope],
        lambda _connection, body: body,
        None,
        options,
        response_hook=response_hook,
        response_headers=response_headers,
        **kwargs,
    )


async def _run_async_read_feed(
    conn,
    *,
    resource_type,
    options,
    response_hook=None,
    response_headers=None,
    **kwargs,
):
    """Async twin of ``_run_sync_read_feed``."""
    path = "/dbs/" if resource_type == http_constants.ResourceType.Database else "/dbs/db/colls/c/docs/"
    resource_id = None if resource_type == http_constants.ResourceType.Database else "collection-rid"
    envelope = "Databases" if resource_type == http_constants.ResourceType.Database else "Documents"
    return await conn._CosmosClientConnection__QueryFeed(
        path,
        resource_type,
        resource_id,
        lambda result: result[envelope],
        lambda _connection, body: body,
        None,
        options,
        response_hook=response_hook,
        response_headers=response_headers,
        **kwargs,
    )


@pytest.mark.parametrize(
    "adapter",
    [_sync_binding_request_from_page, _async_binding_request_from_page],
)
def test_rust_page_adapter_preserves_zero_max_item_count(adapter):
    """Typed paging fields are authoritative, including an explicit zero."""
    prepared = PreparedQuery(
        op=OP_READ_ALL_ITEMS,
        container_link="dbs/db/colls/c",
        continuation="typed-continuation",
        max_item_count=0,
        headers={
            "x-ms-continuation": "stale-header",
            "x-ms-max-item-count": "99",
        },
    )

    request = adapter(prepared)

    assert request.headers["x-ms-continuation"] == "typed-continuation"
    assert request.headers["x-ms-max-item-count"] == "0"


def test_rust_feed_prep_strips_only_driver_owned_generated_headers():
    """Only headers the driver writes itself are removed; everything else is kept.

    Shared by all three paged operations. The first case drops the six headers
    the driver generates, plus page size and continuation because those are
    already carried as typed fields -- keeping a customer header and an
    operation header. The second case shows the paging headers are only dropped
    when the typed fields actually hold those values; with no options set, the
    headers are the only copy and must survive.
    """
    prepared_headers = _build_prepared_headers_for_rust_feed_dispatch(
        options={
            "continuation": "typed-continuation",
            "maxItemCount": 0,
        },
        req_headers={
            "Accept": "application/json",
            "AUTHORIZATION": "legacy-signature",
            "Cache-Control": "no-cache",
            "User-Agent": "legacy-agent",
            "X-MS-DATE": "legacy-date",
            "x-ms-version": "legacy-version",
            "X-MS-CONTINUATION": "generated-continuation",
            "x-ms-max-item-count": "0",
            "x-ms-documentdb-isquery": "true",
            "x-customer-header": "preserved",
        },
    )

    assert prepared_headers == {
        "x-ms-documentdb-isquery": "true",
        "x-customer-header": "preserved",
    }
    assert _build_prepared_headers_for_rust_feed_dispatch(
        options={},
        req_headers={
            "x-ms-continuation": "customer-continuation",
            "x-ms-max-item-count": "7",
        },
    ) == {
        "x-ms-continuation": "customer-continuation",
        "x-ms-max-item-count": "7",
    }


@pytest.mark.parametrize(
    ("options", "is_query_plan"),
    [
        ({}, True),
        ({"changeFeedState": object()}, False),
    ],
)
def test_list_databases_gate_rejects_non_read_feed_shapes(options, is_query_plan):
    """The gate refuses shapes the Rust database page does not serve yet.

    A query-plan request and a change-feed read both reach this code but are not
    plain "list the databases" calls, so they stay on the old path.
    """
    assert not can_use_rust_backend_for_list_databases_page(
        options=options,
        kwargs={},
        is_query_plan=is_query_plan,
        resource_type=http_constants.ResourceType.Database,
    )


def test_sync_query_backend_eligibility_allows_cross_partition_but_blocks_unrepresentable_options():
    """Sync query eligibility gate. Cross-partition queries (including COUNT and
    ORDER BY) are now eligible because the old Python SQL-regex scan was removed --
    the driver's reply decides whether it can run them. But options the rust page
    path cannot represent (``enableCrossPartitionQuery=False``, a ``feed_range``, a
    MultiHash partition key, ``read_timeout``, ``availability_strategy``, full-text
    score scope, query advice) still block it and keep the query on the legacy path.
    """
    eligibility = can_use_rust_backend_for_query_page

    assert eligibility(
        query_payload={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"]},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert eligibility(
        query_payload={"query": "SELECT * FROM c"},
        options={},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert not eligibility(
        query_payload={"query": "SELECT * FROM c"},
        options={"initialHeaders": {"Accept": "application/custom"}},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert eligibility(
        query_payload={"query": "SELECT * FROM c"},
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
        query_payload={"query": "SELECT VALUE COUNT(1) FROM c"},
        options={},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert eligibility(
        query_payload={"query": "SELECT * FROM c ORDER BY c.ts DESC"},
        options={},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert not eligibility(
        query_payload={"query": "SELECT * FROM c"},
        options={"enableCrossPartitionQuery": False},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert eligibility(
        query_payload={"query": "SELECT * FROM c ORDER BY c.ts DESC"},
        options={"partitionKey": ["tenant-a"]},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert not eligibility(
        query_payload={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"]},
        kwargs={"feed_range": {"min": "AA", "max": "FF"}},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )

    assert not eligibility(
        query_payload={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"]},
        kwargs={},
        container_properties={
            "partitionKey": {"paths": ["/pk1", "/pk2"], "kind": "MultiHash", "version": 2}
        },
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )
    assert not eligibility(
        query_payload={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"], "read_timeout": 0.2},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )
    assert not eligibility(
        query_payload={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"], Constants.Kwargs.AVAILABILITY_STRATEGY: False},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )
    assert not eligibility(
        query_payload={"query": "SELECT * FROM c"},
        options={"partitionKey": ["tenant-a"], "fullTextScoreScope": "Local"},
        kwargs={},
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )
    assert not eligibility(
        query_payload={"query": "SELECT * FROM c"},
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
    result, headers = _run_sync_query_feed(
        conn,
        query={"query": "SELECT * FROM c"},
        options={
            "partitionKey": ["tenant-a"],
            "continuation": "ct-in",
            "maxItemCount": 25,
            Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"],
            Constants.Kwargs.TIMEOUT: 9,
        },
        response_hook=lambda h, b: hook_calls.append((dict(h), b)),
        response_headers=response_headers,
        container_properties={"partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
    )

    assert result[0]["id"] == "1"
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

    result, _ = _run_sync_query_feed(
        conn,
        query={"query": "SELECT * FROM c"},
        options={},
    )

    assert result[0]["id"] == "x"
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

        async def _container_properties(_options):
            return {"partitionKey": {"paths": ["/pk"], "kind": "Hash"}}

        result = await _run_async_query_feed(
            conn,
            query={"query": "SELECT * FROM c"},
            options={
                "partitionKey": ["tenant-a"],
                Constants.Kwargs.EXCLUDED_LOCATIONS: ["East US"],
                Constants.Kwargs.TIMEOUT: 11,
            },
            response_hook=lambda h, b: hook_calls.append((dict(h), b)),
            response_headers=response_headers,
            containerProperties=_container_properties,
        )

        assert result[0]["id"] == "2"
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
    eligibility = can_use_rust_backend_for_query_page

    assert not eligibility(
        query_payload={"query": "SELECT * FROM c"},
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
    eligibility = can_use_rust_backend_for_read_all_items_page

    assert eligibility(
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
        partition_key_range_id=None,
    )
    assert not eligibility(
        options={"initialHeaders": {"User-Agent": "customer-agent"}},
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
    eligibility = can_use_rust_backend_for_read_all_items_page

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
    result, headers = _run_sync_read_feed(
        conn,
        resource_type=http_constants.ResourceType.Document,
        options={Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"]},
        response_hook=lambda h, b: hook_calls.append((dict(h), b)),
        response_headers=response_headers,
    )

    assert result[0]["id"] == "doc-1"
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
        result = await _run_async_read_feed(
            conn,
            resource_type=http_constants.ResourceType.Document,
            options={Constants.Kwargs.EXCLUDED_LOCATIONS: ["East US"]},
            response_hook=lambda h, b: hook_calls.append((dict(h), b)),
            response_headers=response_headers,
        )

        assert result[0]["id"] == "doc-2"
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


# ---------------------------------------------------------------------------
# list_databases
#
# The customer call is ``client.list_databases()`` -- "tell me every database in
# this account". It is worth its own group of tests because it is the first
# operation that pages *and* is scoped to the whole account rather than to one
# container, so parts of the request that every other paged call fills in are
# empty here.
#
# The call crosses three layers. Python decides whether the request shape can go
# to Rust and builds the request; the binding (our .rs files) carries it across;
# the Rust driver, which we do not own, sends it and returns the reply. Any of
# the three could change what the customer sees, so the tests below pin down the
# handoffs rather than the internals of any one layer.
#
# What this group checks, in order:
#   * the gate says no to shapes Rust does not serve yet
#   * the request is built correctly -- empty container link, no partition key,
#     page size and continuation as typed fields, customer headers kept
#   * headers Python generated are not sent again as custom driver headers
#   * an unsupported option quietly runs on the old path instead, unchanged
#   * an error from the service is raised once, not retried on the old path
#   * paging works across two pages, with the token making the round trip
#
# Every check is written twice, once for the sync client and once for async,
# because a customer can use either and they must behave the same.
# ---------------------------------------------------------------------------


def test_sync_list_databases_backend_delegates_account_feed(monkeypatch):
    """A normal ``client.list_databases()`` reaches Rust with the right request.

    Checks the parts that are specific to account scope: the container link is
    empty and there is no partition key, because there is no container to name.
    Page size and continuation travel as typed fields rather than as headers.
    A Cosmos header the customer set (throughput bucket) is passed through, and
    a non-Cosmos one is forwarded separately for the driver to send as-is.
    """
    conn = _new_sync_connection()
    backend = _CapturingSyncBackend(
        BackendResponse(
            status_code=200,
            headers=CaseInsensitiveDict({"x-ms-continuation": "db-ct"}),
            body=b'{"Databases":[{"id":"db-1"}]}',
        )
    )
    conn._backend = backend
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: dict(args[1]))

    result, headers = _run_sync_read_feed(
        conn,
        resource_type=http_constants.ResourceType.Database,
        options={
            "maxItemCount": 1,
            "continuation": "start",
            "initialHeaders": {
                "x-test-header": "yes",
                "x-ms-cosmos-throughput-bucket": "7",
            },
        },
    )

    assert result == [{"id": "db-1"}]
    assert headers["x-ms-continuation"] == "db-ct"
    assert backend.prepared.op == OP_LIST_DATABASES
    assert backend.prepared.container_link == ""
    assert backend.prepared.partition_key_header is None
    assert backend.prepared.max_item_count == 1
    assert backend.prepared.continuation == "start"
    assert backend.prepared.headers["x-ms-cosmos-throughput-bucket"] == "7"
    assert "x-test-header" not in backend.prepared.headers
    assert backend.prepared.headers["initialHeaders"] == {"x-test-header": "yes"}


def test_list_databases_prepared_request_drops_driver_owned_headers(monkeypatch):
    """Headers Python already built are not handed to the driver a second time.

    The driver writes its own authorization, date, version, user-agent, accept,
    and cache-control headers. If we passed ours along too, the request would
    carry the same information twice and the two copies could disagree. Only the
    throughput-bucket header, which the driver does not generate, survives.
    """
    conn = _new_sync_connection()
    backend = _CapturingSyncBackend(
        BackendResponse(status_code=200, body=b'{"Databases":[]}')
    )
    conn._backend = backend
    monkeypatch.setattr(
        base_helpers,
        "GetHeaders",
        lambda *args, **kwargs: {
            "authorization": "python-signature",
            "x-ms-date": "python-date",
            "Accept": "application/json",
            "Cache-Control": "no-cache",
            "User-Agent": "python-agent",
            "x-ms-version": "2020-07-15",
            "x-ms-cosmos-throughput-bucket": "7",
        },
    )

    result, _ = _run_sync_read_feed(
        conn,
        resource_type=http_constants.ResourceType.Database,
        options={},
    )

    assert result == []
    assert backend.prepared.headers == {"x-ms-cosmos-throughput-bucket": "7"}


def test_async_list_databases_backend_delegates_account_feed(monkeypatch):
    """Same as the sync test above, for ``async for db in client.list_databases()``."""
    async def _run() -> None:
        conn = _new_async_connection()
        backend = _CapturingAsyncBackend(
            BackendResponse(
                status_code=200,
                headers=CaseInsensitiveDict({"x-ms-continuation": "db-ct-async"}),
                body=b'{"Databases":[{"id":"db-2"}]}',
            )
        )
        conn._backend = backend
        monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: dict(args[1]))

        result = await _run_async_read_feed(
            conn,
            resource_type=http_constants.ResourceType.Database,
            options={"maxItemCount": 2},
        )

        assert result == [{"id": "db-2"}]
        assert conn.last_response_headers["x-ms-continuation"] == "db-ct-async"
        assert backend.prepared.op == OP_LIST_DATABASES
        assert backend.prepared.max_item_count == 2

    asyncio.run(_run())


def test_list_databases_backend_uses_default_headers_without_initial_headers(monkeypatch):
    """A plain ``client.list_databases()`` with no options still carries the client's headers.

    Headers set once when the client was built (for example a user agent suffix)
    have to reach Rust even when the call itself passes nothing.
    """
    conn = _new_sync_connection()
    conn.default_headers = {"x-default-header": "yes"}
    backend = _CapturingSyncBackend(
        BackendResponse(
            status_code=200,
            body=b'{"Databases":[]}',
        )
    )
    conn._backend = backend
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: dict(args[1]))

    result, _ = _run_sync_read_feed(
        conn,
        resource_type=http_constants.ResourceType.Database,
        options={},
    )

    assert result == []
    assert backend.prepared.headers["x-default-header"] == "yes"


def test_async_list_databases_backend_uses_default_headers_without_initial_headers(monkeypatch):
    """Same as the sync test above, on the async client."""
    async def _run() -> None:
        conn = _new_async_connection()
        conn.default_headers = {"x-default-header": "yes"}
        backend = _CapturingAsyncBackend(
            BackendResponse(status_code=200, body=b'{"Databases":[]}')
        )
        conn._backend = backend
        monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: dict(args[1]))

        result = await _run_async_read_feed(
            conn,
            resource_type=http_constants.ResourceType.Database,
            options={},
        )

        assert result == []
        assert backend.prepared.headers["x-default-header"] == "yes"

    asyncio.run(_run())


def test_list_databases_legacy_path_sends_initial_headers(monkeypatch):
    """When the call runs on the old path, ``initial_headers`` still works.

    A customer passing ``initial_headers`` can override one of the client's own
    headers for that one call. This checks the override is applied to the
    request and that the client's stored headers are left alone afterwards, so
    the next call is unaffected.
    """
    conn = _new_sync_connection()
    conn.default_headers = {"x-default-header": "default", "x-override": "default"}
    captured_headers = []

    monkeypatch.setattr(
        base_helpers,
        "GetHeaders",
        lambda _conn, initial_headers, *args, **kwargs: dict(initial_headers),
    )
    monkeypatch.setattr(base_helpers, "set_session_token_header", lambda *args, **kwargs: None)

    def _get(_path, _request_params, headers, **kwargs):
        captured_headers.append(dict(headers))
        return {"Databases": []}, CaseInsensitiveDict()

    monkeypatch.setattr(conn, "_CosmosClientConnection__Get", _get)
    monkeypatch.setattr(conn, "_UpdateSessionIfRequired", lambda *args, **kwargs: None)

    conn._CosmosClientConnection__QueryFeed(
        "/dbs",
        http_constants.ResourceType.Database,
        "",
        lambda result: result["Databases"],
        lambda _, body: body,
        None,
        {
            "initialHeaders": {
                "x-customer-header": "sent",
                "x-override": "customer",
            }
        },
    )

    assert captured_headers == [
        {
            "x-default-header": "default",
            "x-customer-header": "sent",
            "x-override": "customer",
        }
    ]
    assert conn.default_headers == {"x-default-header": "default", "x-override": "default"}


def test_async_list_databases_legacy_path_sends_initial_headers(monkeypatch):
    """The async legacy database feed honors the same initial_headers contract."""
    async def _run() -> None:
        conn = _new_async_connection()
        conn.default_headers = {"x-default-header": "default", "x-override": "default"}
        captured_headers = []

        async def _set_session_token_header(*args, **kwargs):
            return None

        monkeypatch.setattr(
            base_helpers,
            "GetHeaders",
            lambda _conn, initial_headers, *args, **kwargs: dict(initial_headers),
        )
        monkeypatch.setattr(
            base_helpers,
            "set_session_token_header_async",
            _set_session_token_header,
        )

        async def _capturing_get(_path, _request_params, headers, **kwargs):
            captured_headers.append(dict(headers))
            return {"Databases": []}, CaseInsensitiveDict()

        monkeypatch.setattr(conn, "_CosmosClientConnection__Get", _capturing_get)
        monkeypatch.setattr(conn, "_UpdateSessionIfRequired", lambda *args, **kwargs: None)

        await conn._CosmosClientConnection__QueryFeed(
            "/dbs",
            http_constants.ResourceType.Database,
            "",
            lambda result: result["Databases"],
            lambda _, body: body,
            None,
            {
                "initialHeaders": {
                    "x-customer-header": "sent",
                    "x-override": "customer",
                }
            },
        )

        assert captured_headers == [
            {
                "x-default-header": "default",
                "x-customer-header": "sent",
                "x-override": "customer",
            }
        ]
        assert conn.default_headers == {"x-default-header": "default", "x-override": "default"}

    asyncio.run(_run())


@pytest.mark.parametrize(
    "options, kwargs",
    [
        ({"initialHeaders": {"user-agent": "custom"}}, {}),
        ({Constants.Kwargs.READ_TIMEOUT: 0.5}, {}),
        ({}, {Constants.Kwargs.READ_TIMEOUT: 0.5}),
        ({Constants.Kwargs.TIMEOUT: 0.5}, {Constants.Kwargs.TIMEOUT: 0.5}),
        ({Constants.Kwargs.TIMEOUT: 0}, {Constants.Kwargs.TIMEOUT: 0}),
        ({Constants.Kwargs.TIMEOUT: "invalid"}, {Constants.Kwargs.TIMEOUT: "invalid"}),
        ({Constants.Kwargs.AVAILABILITY_STRATEGY: False}, {}),
        ({}, {"raw_request_hook": lambda _request: None}),
    ],
)
def test_async_list_databases_backend_falls_back_for_unrepresentable_options(monkeypatch, options, kwargs):
    """Same as the sync fallback test below, on the async client."""
    async def _run() -> None:
        conn = _new_async_connection()
        backend = _CapturingAsyncBackend(BackendResponse(status_code=200))
        conn._backend = backend
        monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})

        async def _set_session(*_args, **_kwargs):
            return None

        async def _get(*_args, **_kwargs):
            return {"Databases": []}, CaseInsensitiveDict()

        monkeypatch.setattr(base_helpers, "set_session_token_header_async", _set_session)
        monkeypatch.setattr(conn, "_CosmosClientConnection__Get", _get)
        monkeypatch.setattr(conn, "_UpdateSessionIfRequired", lambda *args, **kwargs: None)

        result = await _run_async_read_feed(
            conn,
            resource_type=http_constants.ResourceType.Database,
            options=options,
            **kwargs,
        )

        assert result == []
        assert backend.prepared is None

    asyncio.run(_run())


@pytest.mark.parametrize(
    "options, kwargs",
    [
        ({"initialHeaders": {"user-agent": "custom"}}, {}),
        ({}, {Constants.Kwargs.READ_TIMEOUT: 0.5}),
        ({Constants.Kwargs.TIMEOUT: 0.5}, {Constants.Kwargs.TIMEOUT: 0.5}),
        ({Constants.Kwargs.TIMEOUT: 0}, {Constants.Kwargs.TIMEOUT: 0}),
        ({Constants.Kwargs.TIMEOUT: "invalid"}, {Constants.Kwargs.TIMEOUT: "invalid"}),
        ({Constants.Kwargs.AVAILABILITY_STRATEGY: False}, {}),
        ({}, {"raw_request_hook": lambda _request: None}),
    ],
)
def test_list_databases_backend_falls_back_for_unrepresentable_options(monkeypatch, options, kwargs):
    """An option Rust cannot honor yet sends the call down the old path instead.

    Each row is an option the Rust page does not support today: a custom user
    agent, a read or overall timeout, an availability strategy, or an internal
    hook. The result the customer gets is the same either way; what must not
    happen is Rust running the call and quietly ignoring the option. Asserting
    the fake backend was never handed a request is how we know it did not.
    """
    conn = _new_sync_connection()
    backend = _CapturingSyncBackend(BackendResponse(status_code=200))
    conn._backend = backend
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})
    monkeypatch.setattr(base_helpers, "set_session_token_header", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        conn,
        "_CosmosClientConnection__Get",
        lambda *args, **kwargs: ({"Databases": []}, CaseInsensitiveDict()),
    )
    monkeypatch.setattr(conn, "_UpdateSessionIfRequired", lambda *args, **kwargs: None)

    result, _ = _run_sync_read_feed(
        conn,
        resource_type=http_constants.ResourceType.Database,
        options=options,
        **kwargs,
    )

    assert result == []
    assert backend.prepared is None


@pytest.mark.parametrize("status_code", [403, 404, 429])
def test_sync_list_databases_rust_service_errors_do_not_replay_legacy(monkeypatch, status_code):
    """An error from the service is raised once and the call is not retried on the old path.

    Rust returning a 403, 404, or 429 means the service answered. That is a real
    answer, not a sign that Rust cannot do the job, so running the whole request
    again on the old path would bill the customer twice and slow down the error.
    The old path is wired to fail the test if it is reached. The status,
    substatus, headers, and message all have to survive so error handling the
    customer already wrote keeps working.
    """
    conn = _new_sync_connection()
    backend = _CapturingSyncBackend(
        BackendResponse(
            status_code=status_code,
            sub_status=1002,
            headers=CaseInsensitiveDict({"x-ms-substatus": "1002"}),
            body=b'{"code":"SyntheticError","message":"database feed failed"}',
        )
    )
    conn._backend = backend
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})
    monkeypatch.setattr(base_helpers, "set_session_token_header", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        conn,
        "_CosmosClientConnection__Get",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("legacy replay")),
    )

    with pytest.raises(CosmosHttpResponseError) as excinfo:
        _run_sync_read_feed(
            conn,
            resource_type=http_constants.ResourceType.Database,
            options={},
        )

    assert excinfo.value.status_code == status_code
    assert excinfo.value.sub_status == 1002
    assert excinfo.value.headers["x-ms-substatus"] == "1002"
    assert "database feed failed" in str(excinfo.value)
    assert backend.prepared.op == OP_LIST_DATABASES


@pytest.mark.parametrize("status_code", [403, 404, 429])
def test_async_list_databases_rust_service_errors_do_not_replay_legacy(monkeypatch, status_code):
    """Same as the sync error test above, on the async client."""
    async def _run() -> None:
        conn = _new_async_connection()
        backend = _CapturingAsyncBackend(
            BackendResponse(
                status_code=status_code,
                sub_status=1002,
                headers=CaseInsensitiveDict({"x-ms-substatus": "1002"}),
                body=b'{"code":"SyntheticError","message":"database feed failed"}',
            )
        )
        conn._backend = backend
        monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})

        async def _set_session(*_args, **_kwargs):
            return None

        async def _legacy_replay(*_args, **_kwargs):
            raise AssertionError("legacy replay")

        monkeypatch.setattr(base_helpers, "set_session_token_header_async", _set_session)
        monkeypatch.setattr(conn, "_CosmosClientConnection__Get", _legacy_replay)

        with pytest.raises(CosmosHttpResponseError) as excinfo:
            await _run_async_read_feed(
                conn,
                resource_type=http_constants.ResourceType.Database,
                options={},
            )

        assert excinfo.value.status_code == status_code
        assert excinfo.value.sub_status == 1002
        assert excinfo.value.headers["x-ms-substatus"] == "1002"
        assert "database feed failed" in str(excinfo.value)
        assert backend.prepared.op == OP_LIST_DATABASES

    asyncio.run(_run())


def test_sync_read_databases_keeps_python_paging_and_rust_fetches_each_page(monkeypatch):
    """Looping over two pages of databases works, and the page token is carried over.

    An account with more databases than one page holds is returned in pieces.
    Python still owns the loop the customer writes; Rust just fetches one page
    each time it is asked. This checks the customer sees both databases in
    order, that the second request carried the token the first page returned,
    and that the requested page size was applied to both. The old path is wired
    to fail the test if it is reached.
    """
    conn = _new_sync_connection()
    backend = _SequencedSyncBackend()
    conn._backend = backend
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})
    monkeypatch.setattr(
        conn,
        "_CosmosClientConnection__Get",
        lambda *args, **kwargs: pytest.fail("legacy HTTP database feed was called"),
    )

    assert list(conn.ReadDatabases(options={"maxItemCount": 1})) == [
        {"id": "db-1"},
        {"id": "db-2"},
    ]
    assert [request.continuation for request in backend.prepared] == [
        None,
        "next-db-page",
    ]
    assert all(request.max_item_count == 1 for request in backend.prepared)


def test_async_read_databases_keeps_python_paging_and_rust_fetches_each_page(monkeypatch):
    """Same as the sync paging test above, on the async client."""
    async def _run() -> None:
        conn = _new_async_connection()
        backend = _SequencedAsyncBackend()
        conn._backend = backend
        monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})

        async def _legacy_get(*_args, **_kwargs):
            pytest.fail("legacy async HTTP database feed was called")

        monkeypatch.setattr(conn, "_CosmosClientConnection__Get", _legacy_get)
        results = [item async for item in conn.ReadDatabases(options={"maxItemCount": 1})]

        assert results == [{"id": "db-1"}, {"id": "db-2"}]
        assert [request.continuation for request in backend.prepared] == [
            None,
            "next-db-page",
        ]
        assert all(request.max_item_count == 1 for request in backend.prepared)

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

    result, _ = _run_sync_read_feed(
        conn,
        resource_type=http_constants.ResourceType.Document,
        options={"partitionKey": ["tenant-a"]},
    )

    assert result[0]["id"] == "doc-pk"
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

        result = await _run_async_read_feed(
            conn,
            resource_type=http_constants.ResourceType.Document,
            options={"partitionKey": ["tenant-a"]},
        )

        assert result[0]["id"] == "doc-pk-async"
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
    result, headers = _run_sync_read_feed(
        conn,
        resource_type=http_constants.ResourceType.Document,
        options={},
        response_hook=lambda h, b: hook_calls.append((dict(h), b)),
        response_headers=response_headers,
    )

    assert result == []
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
        result = await _run_async_read_feed(
            conn,
            resource_type=http_constants.ResourceType.Document,
            options={},
            response_hook=lambda h, b: hook_calls.append((dict(h), b)),
            response_headers=response_headers,
        )

        assert result == []
        assert conn.last_response_headers["x-ms-session-token"] == "st-empty-async"
        assert response_headers["x-ms-session-token"] == "st-empty-async"
        assert len(hook_calls) == 1
        assert backend.prepared.op == OP_READ_ALL_ITEMS
        assert backend.prepared.query is None

    asyncio.run(_run())


def test_sync_driver_unsupported_query_falls_back():
    """Typed page capability failures are handled by the backend boundary."""
    class _UnsupportedBackend(CosmosBackend):
        def execute(self, prepared):
            raise AssertionError("single-response execution is not expected")

        def execute_pages(self, prepared):
            del prepared
            raise QueryNotSupportedByBackendError("unsupported query plan")
            yield  # pragma: no cover

    prepared = PreparedQuery(
        op=OP_QUERY_ITEMS,
        container_link="dbs/db/colls/c",
        query="SELECT VALUE COUNT(1) FROM c",
    )

    fallback_count_before = rust_compatibility_fallback_count()
    result = _UnsupportedBackend().run_page_operation(
        build_prepared=lambda: prepared,
        legacy_operation=LegacyOperation(op=OP_QUERY_ITEMS, invoke=lambda: "legacy"),
        parse_response=lambda _page: "rust",
        fallback_exceptions=(PageNotSupportedByBackendError,),
    )
    assert result == "legacy"
    assert rust_compatibility_fallback_count() == fallback_count_before + 1


def test_async_driver_unsupported_query_falls_back():
    """Async typed page capability failures are handled by the backend boundary."""
    class _UnsupportedBackend(AsyncCosmosBackend):
        async def execute(self, prepared):
            raise AssertionError("single-response execution is not expected")

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
        async def _build_prepared():
            return prepared

        async def _run_legacy():
            return "legacy"

        fallback_count_before = rust_compatibility_fallback_count()
        result = await _UnsupportedBackend().run_page_operation(
            build_prepared=_build_prepared,
            legacy_operation=LegacyOperation(op=OP_QUERY_ITEMS, invoke=_run_legacy),
            parse_response=lambda _page: "rust",
            fallback_exceptions=(PageNotSupportedByBackendError,),
        )
        assert result == "legacy"
        assert rust_compatibility_fallback_count() == fallback_count_before + 1

    asyncio.run(_run())


def test_sync_unrelated_not_implemented_error_is_not_replayed():
    """Unexpected backend errors propagate instead of triggering a second request."""
    class _BrokenBackend(CosmosBackend):
        def execute(self, prepared):
            raise AssertionError("single-response execution is not expected")

        def execute_pages(self, prepared):
            del prepared
            raise NotImplementedError("unexpected parser failure")
            yield  # pragma: no cover

    prepared = PreparedQuery(
        op=OP_QUERY_ITEMS,
        container_link="dbs/db/colls/c",
        query="SELECT * FROM c",
    )
    fallback_count_before = rust_compatibility_fallback_count()

    with pytest.raises(NotImplementedError, match="unexpected parser failure"):
        _BrokenBackend().run_page_operation(
            build_prepared=lambda: prepared,
            legacy_operation=LegacyOperation(op=OP_QUERY_ITEMS, invoke=lambda: "legacy"),
            parse_response=lambda _page: "rust",
            fallback_exceptions=(PageNotSupportedByBackendError,),
        )

    assert rust_compatibility_fallback_count() == fallback_count_before


def test_async_unrelated_not_implemented_error_is_not_replayed():
    """Async unexpected backend errors also propagate without fallback."""
    class _BrokenBackend(AsyncCosmosBackend):
        async def execute(self, prepared):
            raise AssertionError("single-response execution is not expected")

        async def execute_pages(self, prepared):
            del prepared
            raise NotImplementedError("unexpected async parser failure")
            yield  # pragma: no cover

    async def _run():
        prepared = PreparedQuery(
            op=OP_QUERY_ITEMS,
            container_link="dbs/db/colls/c",
            query="SELECT * FROM c",
        )
        async def _build_prepared():
            return prepared

        async def _run_legacy():
            return "legacy"

        fallback_count_before = rust_compatibility_fallback_count()

        with pytest.raises(NotImplementedError, match="unexpected async parser failure"):
            await _BrokenBackend().run_page_operation(
                build_prepared=_build_prepared,
                legacy_operation=LegacyOperation(op=OP_QUERY_ITEMS, invoke=_run_legacy),
                parse_response=lambda _page: "rust",
                fallback_exceptions=(PageNotSupportedByBackendError,),
            )

        assert rust_compatibility_fallback_count() == fallback_count_before

    asyncio.run(_run())


def test_sync_empty_page_iterator_is_not_replayed():
    """A missing Rust page raises one public error and does not repeat the call."""
    class _EmptyBackend(CosmosBackend):
        def execute(self, prepared):
            raise AssertionError("single-response execution is not expected")

        def execute_pages(self, prepared):
            del prepared
            return iter(())

    legacy_calls = []
    with pytest.raises(BackendProtocolError, match="returned no page"):
        _EmptyBackend().run_page_operation(
            build_prepared=lambda: PreparedQuery(op=OP_QUERY_ITEMS, container_link="dbs/db/colls/c"),
            legacy_operation=LegacyOperation(
                op=OP_QUERY_ITEMS,
                invoke=lambda: legacy_calls.append(1),
            ),
            parse_response=lambda _page: "rust",
            fallback_exceptions=(RuntimeError,),
        )
    assert legacy_calls == []


def test_async_empty_page_iterator_is_not_replayed():
    """A missing async Rust page raises one public error and is not repeated."""
    class _EmptyBackend(AsyncCosmosBackend):
        async def execute(self, prepared):
            raise AssertionError("single-response execution is not expected")

        async def execute_pages(self, prepared):
            del prepared
            if False:
                yield QueryPage(status_code=200)

    async def _run():
        legacy_calls = []

        async def _build_prepared():
            return PreparedQuery(op=OP_QUERY_ITEMS, container_link="dbs/db/colls/c")

        async def _run_legacy():
            legacy_calls.append(1)

        with pytest.raises(BackendProtocolError, match="returned no page"):
            await _EmptyBackend().run_page_operation(
                build_prepared=_build_prepared,
                legacy_operation=LegacyOperation(op=OP_QUERY_ITEMS, invoke=_run_legacy),
                parse_response=lambda _page: "rust",
                fallback_exceptions=(RuntimeError,),
            )
        assert legacy_calls == []

    asyncio.run(_run())


def test_sync_missing_backend_attribute_is_not_silently_treated_as_legacy():
    """A broken connection state raises its public error instead of using Python."""
    conn = _new_sync_connection()
    del conn._backend

    with pytest.raises(AttributeError, match="_backend"):
        _run_sync_read_feed(
            conn,
            resource_type=http_constants.ResourceType.Database,
            options={},
        )


def test_async_missing_backend_attribute_is_not_silently_treated_as_legacy():
    """A broken async connection state raises instead of using Python."""
    async def _run():
        conn = _new_async_connection()
        del conn._backend

        with pytest.raises(AttributeError, match="_backend"):
            await _run_async_read_feed(
                conn,
                resource_type=http_constants.ResourceType.Database,
                options={},
            )

    asyncio.run(_run())


def test_sync_read_all_legacy_fallback_updates_session(monkeypatch):
    """Sync legacy fallback (no backend). The read-feed still calls
    ``_UpdateSessionIfRequired`` and propagates the session token, so a fallback read
    advances the session bookmark exactly like before the migration.
    """
    conn = _new_sync_connection()
    conn._backend = LEGACY_BACKEND
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
        conn._backend = ASYNC_LEGACY_BACKEND
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


# Database-query routing preserves query text, options, pages, and continuations.


def _run_sync_database_query_feed(conn, *, query, options, **kwargs):
    """Run one synchronous database-query page."""
    return conn._CosmosClientConnection__QueryFeed(
        "/dbs",
        http_constants.ResourceType.Database,
        "",
        lambda result: result["Databases"],
        lambda _connection, body: body,
        query,
        options,
        **kwargs,
    )


async def _run_async_database_query_feed(conn, *, query, options, **kwargs):
    """Run one asynchronous database-query page."""
    return await conn._CosmosClientConnection__QueryFeed(
        "/dbs",
        http_constants.ResourceType.Database,
        "",
        lambda result: result["Databases"],
        lambda _connection, body: body,
        query,
        options,
        **kwargs,
    )


@pytest.mark.parametrize(
    ("query_payload", "options", "is_query_plan", "resource_type"),
    [
        (None, {}, False, http_constants.ResourceType.Database),
        ({"query": "SELECT * FROM root r"}, {}, True, http_constants.ResourceType.Database),
        ({"query": "SELECT * FROM root r"}, {}, False, http_constants.ResourceType.Document),
        (
            {"query": "SELECT * FROM root r"},
            {"changeFeedState": object()},
            False,
            http_constants.ResourceType.Database,
        ),
        (
            {"query": "SELECT * FROM root r"},
            {Constants.Kwargs.AVAILABILITY_STRATEGY: False},
            False,
            http_constants.ResourceType.Database,
        ),
        (
            "SELECT * FROM root r",
            {},
            False,
            http_constants.ResourceType.Database,
        ),
    ],
)
def test_query_databases_gate_rejects_shapes_rust_cannot_serve(
    query_payload, options, is_query_plan, resource_type
):
    """Unsupported database-query shapes use Python."""
    assert not can_use_rust_backend_for_query_databases_page(
        query_payload=query_payload,
        options=options,
        kwargs={},
        is_query_plan=is_query_plan,
        resource_type=resource_type,
    )


def test_query_databases_gate_accepts_a_plain_account_query():
    """A supported parameterized database query uses Rust."""
    assert can_use_rust_backend_for_query_databases_page(
        query_payload={
            "query": "SELECT * FROM root r WHERE r.id = @id",
            "parameters": [{"name": "@id", "value": "db-1"}],
        },
        options={"maxItemCount": 10},
        kwargs={},
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Database,
    )


def test_sync_query_databases_backend_delegates_account_query(monkeypatch):
    """Rust receives the database query, parameters, page options, and headers."""
    conn = _new_sync_connection()
    backend = _CapturingSyncBackend(
        BackendResponse(
            status_code=200,
            headers=CaseInsensitiveDict({"x-ms-continuation": "db-ct"}),
            body=b'{"Databases":[{"id":"db-1"}]}',
        )
    )
    conn._backend = backend
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: dict(args[1]))
    monkeypatch.setattr(base_helpers, "set_session_token_header", lambda *args, **kwargs: None)

    result, headers = _run_sync_database_query_feed(
        conn,
        query={
            "query": "SELECT * FROM root r WHERE r.id = @id",
            "parameters": [{"name": "@id", "value": "db-1"}],
        },
        options={
            "maxItemCount": 1,
            "continuation": "start",
            "initialHeaders": {
                "x-test-header": "yes",
                "x-ms-cosmos-throughput-bucket": "7",
            },
        },
    )

    assert result == [{"id": "db-1"}]
    assert headers["x-ms-continuation"] == "db-ct"
    assert backend.prepared.op == OP_QUERY_DATABASES
    assert backend.prepared.container_link == ""
    assert backend.prepared.partition_key_header is None
    assert backend.prepared.query == "SELECT * FROM root r WHERE r.id = @id"
    assert backend.prepared.parameters == ({"name": "@id", "value": "db-1"},)
    assert backend.prepared.max_item_count == 1
    assert backend.prepared.continuation == "start"
    assert backend.prepared.headers["x-ms-cosmos-throughput-bucket"] == "7"
    assert backend.prepared.headers["initialHeaders"] == {"x-test-header": "yes"}


def test_query_databases_binding_request_carries_the_query_body():
    """The Rust request contains the complete database query body."""
    binding_request = _sync_binding_request_from_page(
        PreparedQuery(
            op=OP_QUERY_DATABASES,
            container_link="",
            query="SELECT * FROM root r WHERE r.id = @id",
            parameters=({"name": "@id", "value": "db-1"},),
            max_item_count=2,
            continuation="token",
            headers={},
        )
    )

    assert binding_request.op == OP_QUERY_DATABASES
    assert binding_request.container_link == ""
    assert json.loads(binding_request.body_bytes) == {
        "query": "SELECT * FROM root r WHERE r.id = @id",
        "parameters": [{"name": "@id", "value": "db-1"}],
    }
    assert binding_request.headers["x-ms-max-item-count"] == "2"
    assert binding_request.headers["x-ms-continuation"] == "token"


@pytest.mark.parametrize(
    "options, kwargs",
    [
        ({"initialHeaders": {"user-agent": "custom"}}, {}),
        ({Constants.Kwargs.READ_TIMEOUT: 0.5}, {}),
        ({Constants.Kwargs.TIMEOUT: 0.5}, {Constants.Kwargs.TIMEOUT: 0.5}),
        ({Constants.Kwargs.AVAILABILITY_STRATEGY: False}, {}),
        ({}, {"raw_request_hook": lambda _request: None}),
    ],
)
def test_query_databases_backend_falls_back_for_unrepresentable_options(monkeypatch, options, kwargs):
    """Unsupported database-query options use Python."""
    conn = _new_sync_connection()
    backend = _CapturingSyncBackend(BackendResponse(status_code=200))
    conn._backend = backend
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})
    monkeypatch.setattr(base_helpers, "set_session_token_header", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        conn,
        "_CosmosClientConnection__Post",
        lambda *args, **kwargs: ({"Databases": []}, CaseInsensitiveDict()),
    )
    monkeypatch.setattr(conn, "_UpdateSessionIfRequired", lambda *args, **kwargs: None)

    result, _ = _run_sync_database_query_feed(
        conn,
        query={"query": "SELECT * FROM root r"},
        options=options,
        **kwargs,
    )

    assert result == []
    assert backend.prepared is None


def test_sync_query_databases_pages_carry_the_continuation_token(monkeypatch):
    """Database-query pages stay ordered and carry the continuation forward."""
    conn = _new_sync_connection()
    backend = _SequencedSyncBackend()
    conn._backend = backend
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})
    monkeypatch.setattr(base_helpers, "set_session_token_header", lambda *args, **kwargs: None)

    query = {"query": "SELECT * FROM root r"}
    first_page, first_headers = _run_sync_database_query_feed(
        conn, query=query, options={"maxItemCount": 1}
    )
    second_page, _ = _run_sync_database_query_feed(
        conn,
        query=query,
        options={"maxItemCount": 1, "continuation": first_headers["x-ms-continuation"]},
    )

    assert first_page == [{"id": "db-1"}]
    assert second_page == [{"id": "db-2"}]
    assert [request.op for request in backend.prepared] == [OP_QUERY_DATABASES] * 2
    assert [request.continuation for request in backend.prepared] == [None, "next-db-page"]
    assert [request.max_item_count for request in backend.prepared] == [1, 1]


def test_async_query_databases_backend_delegates_account_query(monkeypatch):
    """Async Rust receives the complete database query and page options."""
    async def _run() -> None:
        """Wire a capturing backend and assert the full query request is forwarded."""
        conn = _new_async_connection()
        backend = _CapturingAsyncBackend(
            BackendResponse(
                status_code=200,
                headers=CaseInsensitiveDict({"x-ms-continuation": "db-ct"}),
                body=b'{"Databases":[{"id":"db-1"}]}',
            )
        )
        conn._backend = backend
        monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: dict(args[1]))

        async def _set_session(*_args, **_kwargs):
            """No-op stub: suppresses session-token header writes during the test."""
            return None

        monkeypatch.setattr(base_helpers, "set_session_token_header_async", _set_session)

        result = await _run_async_database_query_feed(
            conn,
            query={
                "query": "SELECT * FROM root r WHERE r.id = @id",
                "parameters": [{"name": "@id", "value": "db-1"}],
            },
            options={"maxItemCount": 1},
        )

        assert result == [{"id": "db-1"}]
        assert backend.prepared.op == OP_QUERY_DATABASES
        assert backend.prepared.container_link == ""
        assert backend.prepared.partition_key_header is None
        assert backend.prepared.query == "SELECT * FROM root r WHERE r.id = @id"
        assert backend.prepared.parameters == ({"name": "@id", "value": "db-1"},)
        assert backend.prepared.max_item_count == 1

    asyncio.run(_run())


def test_async_query_databases_pages_carry_the_continuation_token(monkeypatch):
    """Async database-query pages preserve contents and continuation behavior."""
    async def _run() -> None:
        """Page through two sequenced responses and confirm continuation tokens thread through."""
        conn = _new_async_connection()
        backend = _SequencedAsyncBackend()
        conn._backend = backend
        monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})

        async def _set_session(*_args, **_kwargs):
            """No-op stub: suppresses session-token header writes during the test."""
            return None

        monkeypatch.setattr(base_helpers, "set_session_token_header_async", _set_session)

        query = {"query": "SELECT * FROM root r"}
        response_headers = CaseInsensitiveDict()
        first_page = await _run_async_database_query_feed(
            conn, query=query, options={"maxItemCount": 1}, response_headers=response_headers
        )
        second_page = await _run_async_database_query_feed(
            conn,
            query=query,
            options={"maxItemCount": 1, "continuation": response_headers["x-ms-continuation"]},
        )

        assert first_page == [{"id": "db-1"}]
        assert second_page == [{"id": "db-2"}]
        assert [request.op for request in backend.prepared] == [OP_QUERY_DATABASES] * 2
        assert [request.continuation for request in backend.prepared] == [None, "next-db-page"]

    asyncio.run(_run())
