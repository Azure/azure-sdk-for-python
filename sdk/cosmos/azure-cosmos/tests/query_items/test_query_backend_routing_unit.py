# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit coverage for Rust query-page routing helpers (no network).

These pin the query paging behavior: ``query_items`` and ``read_all_items`` fetch one page
at a time through the backend's paged handoff (``execute_pages``), not the
single-reply path; and the Python-side eligibility gates decide when a page may go
to the Rust backend versus the legacy HTTP path. The old Python SQL-regex scan is
gone -- cross-partition shapes (COUNT, ORDER BY, ...) are no longer blocked here;
the driver's own reply is authoritative. Options the Rust page path cannot
represent still fall back to legacy except for database listing and querying,
which reject unsupported calls without replay. All fakes, no network.
"""
from __future__ import annotations
from azure.cosmos._backend.capabilities import OperationRouting
from common.typed_requests import legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings

import asyncio
import base64
import json
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import http_constants
from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos import _base as base_helpers
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos._availability_strategy_config import CrossRegionHedgingStrategy
from azure.cosmos._backend.errors import (
    BindingProtocolError,
    PagePreflightError,
    UnsupportedQueryError,
)
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._backend.contracts import BackendResponse, PreparedPageRequest, BackendPage
from azure.cosmos._backend.operations import (
    OP_LIST_CONTAINERS, OP_LIST_DATABASES, OP_QUERY_CONTAINERS,
    OP_QUERY_DATABASES, OP_QUERY_ITEMS, OP_READ_ALL_ITEMS,
)
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count
from azure.cosmos._backend.rust_backend import build_binding_request_from_page as _sync_binding_request_from_page
from azure.cosmos.aio._backend.rust_backend import (
    build_binding_request_from_page as _async_binding_request_from_page,
)
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos._constants import _Constants as Constants, TimeoutScope
from azure.cosmos._cosmos_client_connection import CosmosClientConnection as SyncConnection
from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection as AsyncConnection
from azure.cosmos.documents import ConnectionPolicy
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from azure.cosmos._helpers._item_context import ClientLastResponseHeaders, ItemClientContext
from azure.cosmos.partition_key import _Empty
from azure.cosmos._query_rust_routing import (
    build_list_databases_prepared_query,
    can_use_rust_backend_for_list_databases_page,
    can_use_rust_backend_for_query_databases_page,
    can_use_rust_backend_for_list_containers_page,
    can_use_rust_backend_for_query_containers_page,
    can_use_rust_backend_for_query_page,
    can_use_rust_backend_for_read_all_items_page,
)


class _CapturingSyncBackend(CosmosBackend):
    """A stand-in for the Rust backend that records the request and replies once.

    These tests never talk to a real Cosmos account. This class keeps whatever
    ``PreparedPageRequest`` the routing code built, so a test can check exactly what
    would have gone on the wire, and hands back one canned page. ``execute``
    raises because a paged operation must never be dispatched through the
    single-reply path.
    """

    def __init__(self, response: BackendResponse) -> None:
        self._response = response
        self.prepared = None

    def execute_pages(self, prepared, *, deadline=None):
        self.prepared = prepared
        yield BackendPage(
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

    def execute(self, prepared, *, deadline=None):
        raise AssertionError("single-response execution is not expected")


class _CapturingAsyncBackend(AsyncCosmosBackend):
    """Async twin of ``_CapturingSyncBackend``, so both surfaces get the same checks."""

    def __init__(self, response: BackendResponse) -> None:
        self._response = response
        self.prepared = None

    async def execute_pages(self, prepared, *, deadline=None):
        self.prepared = prepared
        yield BackendPage(
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

    async def execute(self, prepared, *, deadline=None):
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

    def execute_pages(self, prepared, *, deadline=None):
        self.prepared.append(prepared)
        if prepared.continuation is None:
            yield BackendPage(
                status_code=200,
                continuation="next-db-page",
                headers=CaseInsensitiveDict({"x-ms-continuation": "next-db-page"}),
                body=b'{"Databases":[{"id":"db-1"}]}',
            )

        else:
            yield BackendPage(
                status_code=200,
                headers=CaseInsensitiveDict(),
                body=b'{"Databases":[{"id":"db-2"}]}',
            )

    def execute(self, prepared, *, deadline=None):
        raise AssertionError("single-response execution is not expected")


class _SequencedAsyncBackend(AsyncCosmosBackend):
    """Async twin of ``_SequencedSyncBackend``."""

    def __init__(self) -> None:
        self.prepared = []

    async def execute_pages(self, prepared, *, deadline=None):
        self.prepared.append(prepared)
        if prepared.continuation is None:
            yield BackendPage(
                status_code=200,
                continuation="next-db-page",
                headers=CaseInsensitiveDict({"x-ms-continuation": "next-db-page"}),
                body=b'{"Databases":[{"id":"db-1"}]}',
            )

        else:
            yield BackendPage(
                status_code=200,
                headers=CaseInsensitiveDict(),
                body=b'{"Databases":[{"id":"db-2"}]}',
            )

    async def execute(self, prepared, *, deadline=None):
        raise AssertionError("single-response execution is not expected")


@pytest.fixture(params=["sync", "async"])
def listing_client(request):
    """Exercise the public lazy pager through the real Rust page parser."""
    is_async = request.param == "async"
    conn = _new_async_connection() if is_async else _new_sync_connection()
    client_type = AsyncCosmosClient if is_async else CosmosClient
    client = client_type.__new__(client_type)
    client.client_connection = conn
    response = BackendResponse(
        status_code=200,
        headers=CaseInsensitiveDict({
            "x-ms-continuation": "next-db-page",
            "x-ms-activity-id": "page-one",
            "x-ms-request-charge": "2",
        }),
        body=b'{"Databases":[{"id":"db-1"},{"id":"db-2"}]}',
        diagnostics="activity=page-one requests=1",
    )
    backend_type = _CapturingAsyncBackend if is_async else _CapturingSyncBackend
    backend = backend_type(response)
    backend.execute_pages = MagicMock(wraps=backend.execute_pages)
    conn._backend = backend
    client._backend = backend
    client._item_context = ItemClientContext(backend, response_state=conn._response_state)
    conn.last_response_headers = CaseInsensitiveDict({"x-ms-activity-id": "stale"})
    legacy_get = AsyncMock if is_async else MagicMock
    conn._CosmosClientConnection__Get = legacy_get(side_effect=AssertionError("legacy replay"))
    conn._CosmosClientConnection__Post = legacy_get(side_effect=AssertionError("legacy replay"))
    return client, conn, backend, is_async


@pytest.fixture(params=["list", "query", "query-none", "query-dict"])
def database_feed(request, listing_client):
    client, _, _, _ = listing_client
    if request.param == "list":
        return client.list_databases
    query = {
        "query": "SELECT * FROM root r WHERE r.id != @excluded",
        "parameters": [{"name": "@excluded", "value": "excluded"}],
    }
    if request.param == "query-none":
        return lambda **kwargs: client.query_databases(query=None, **kwargs)
    if request.param == "query-dict":
        return lambda **kwargs: client.query_databases(query=query, **kwargs)
    return lambda **kwargs: client.query_databases(**query, **kwargs)


async def _next_listing_page(pager, is_async):
    if is_async:
        return [row async for row in await pager.__anext__()]
    return list(next(pager))


async def _listing_rows(iterable, is_async):
    if is_async:
        return [row async for row in iterable]
    return list(iterable)


@pytest.mark.asyncio
@pytest.mark.parametrize("timeout", [None, 1, 3.5, 10])
async def test_database_feed_public_hook_is_lazy_per_page_and_replayable(listing_client, database_feed, timeout):
    """Listing databases is lazy, calls the hook once per page, and resumes from a token.

    Runs for all four ways of asking -- ``list_databases`` and
    ``query_databases`` given its query positionally, as ``None``, or as a
    dict -- and for several timeouts.

    Building the iterable sends nothing. Taking a page then returns both
    databases and calls the hook **once for the page**, not once per database,
    with that page's activity id, charge and diagnostics.

    The second page carries the continuation token back to the backend. The
    first hook's headers are compared against a copy taken earlier to prove
    page two did not overwrite page one's record.

    Resuming a fresh iterator from the saved token returns the same page two,
    which is what makes a stored token useful.

    When a timeout is given, every page is sent a positive remaining budget no
    greater than it; when it is not, no timeout header is sent at all rather
    than some invented default. The legacy transport is never touched.
    """
    _, conn, backend, is_async = listing_client
    hooks = []
    iterable = database_feed(
        max_item_count=2,
        initial_headers={"x-custom-listing": "value"},
        throughput_bucket=1,
        response_hook=hooks.append,
        timeout=timeout,
    )
    assert hooks == []
    backend.execute_pages.assert_not_called()
    pager = iterable.by_page()
    assert await _next_listing_page(pager, is_async) == [{"id": "db-1"}, {"id": "db-2"}]
    continuation = pager.continuation_token
    assert continuation == "next-db-page"
    assert len(hooks) == 1  # One page, not one callback per database.
    assert hooks[0]["x-ms-activity-id"] == "page-one"
    assert hooks[0]["x-ms-request-charge"] == "2"
    assert hooks[0]["x-ms-cosmos-sdk-diagnostics"] == "activity=page-one requests=1"
    assert backend.prepared.max_item_count == 2
    assert wire_headers(backend.prepared)["x-custom-listing"] == "value"
    assert wire_headers(backend.prepared)["x-ms-cosmos-throughput-bucket"] == '1'
    to_binding_request = _async_binding_request_from_page if is_async else _sync_binding_request_from_page
    binding_request = to_binding_request(backend.prepared)
    if timeout is None:
        assert Constants.OVERALL_TIMEOUT_SECONDS not in wire_headers(binding_request)
    else:
        assert 0 < settings_options(binding_request)["timeout_seconds"] <= timeout
    first_headers = dict(hooks[0])

    backend._response = BackendResponse(
        status_code=200,
        headers=CaseInsensitiveDict({"x-ms-activity-id": "page-two", "x-ms-request-charge": "3"}),
        body=b'{"Databases":[{"id":"db-3"}]}',
        diagnostics="activity=page-two requests=1",
    )
    assert await _next_listing_page(pager, is_async) == [{"id": "db-3"}]
    assert backend.prepared.continuation == continuation
    remaining = settings_options(backend.prepared).get("timeout_seconds")
    assert remaining is None if timeout is None else 0 < remaining <= timeout
    assert len(hooks) == 2
    assert hooks[1]["x-ms-activity-id"] == "page-two"
    assert hooks[1]["x-ms-request-charge"] == "3"
    assert hooks[1]["x-ms-cosmos-sdk-diagnostics"] == "activity=page-two requests=1"
    assert hooks[0] == first_headers
    assert await _next_listing_page(iterable.by_page(continuation), is_async) == [{"id": "db-3"}]
    assert len(hooks) == 3
    remaining = settings_options(backend.prepared).get("timeout_seconds")
    assert remaining is None if timeout is None else 0 < remaining <= timeout
    assert backend.execute_pages.call_count == 3
    conn._CosmosClientConnection__Get.assert_not_called()
    conn._CosmosClientConnection__Post.assert_not_called()


@pytest.mark.asyncio
async def test_database_feed_hook_cannot_mutate_paging_headers(listing_client, database_feed):
    """A hook that wipes its headers cannot break paging or the recorded response.

    The hook clears the dict it is handed. The continuation token still works
    and the client's last response headers still hold the real activity id, so
    the hook was given its own copy rather than the live paging state.

    Without that, a customer writing a hook that edits headers for logging
    could stop their own enumeration partway through.
    """
    _, conn, backend, is_async = listing_client

    def hook(headers):
        headers.clear()

    pager = database_feed(response_hook=hook).by_page()
    await _next_listing_page(pager, is_async)
    assert pager.continuation_token == "next-db-page"
    assert conn.last_response_headers["x-ms-activity-id"] == "page-one"
    assert backend.execute_pages.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("has_continuation", [False, True])
async def test_database_feed_hook_includes_empty_successful_pages(listing_client, database_feed, has_continuation):
    """An empty page still reaches the hook, and only a token means there is more to come.

    The first page comes back successful but empty, in two variants: with and
    without a continuation token.

    Either way the hook sees that page. A page that cost a request and
    returned nothing is still worth reporting, since it carries a charge and
    an activity id.

    What differs is what happens next. With a token, paging continues and
    picks up the later database; without one, enumeration stops and returns
    nothing. Emptiness alone must not be read as the end of the feed -- a real
    account can return an empty page in the middle of a listing.
    """
    _, _, backend, is_async = listing_client
    hooks = []
    backend._response = BackendResponse(
        status_code=200,
        headers=CaseInsensitiveDict({
            "x-ms-activity-id": "empty-page",
            **({"x-ms-continuation": "next-db-page"} if has_continuation else {}),
        }),
        body=b'{"Databases":[]}',
    )

    def hook(headers):
        hooks.append(headers)
        backend._response = BackendResponse(
            status_code=200,
            headers=CaseInsensitiveDict({"x-ms-activity-id": "last-page"}),
            body=b'{"Databases":[{"id":"db-last"}]}',
        )

    rows = await _listing_rows(database_feed(response_hook=hook), is_async)
    assert rows == ([{"id": "db-last"}] if has_continuation else [])
    assert [headers["x-ms-activity-id"] for headers in hooks] == (
        ["empty-page", "last-page"] if has_continuation else ["empty-page"]
    )
    assert backend.execute_pages.call_count == len(hooks)


@pytest.mark.asyncio
@pytest.mark.parametrize("later_page", [False, True])
async def test_database_feed_hook_not_called_on_failed_page(listing_client, database_feed, later_page):
    """A page that fails does not reach the hook, whether it is the first page or a later one.

    The backend returns 403. The error surfaces with its status, and the hook
    has been called only for whatever pages genuinely succeeded before it --
    none in the first case, one in the second.

    The hook reports delivered pages, so calling it for a failure would
    corrupt a customer's own charge accounting with a page they never got.
    The failure is also not retried through the legacy transport.
    """
    _, conn, backend, is_async = listing_client
    hooks = []
    pager = database_feed(response_hook=hooks.append).by_page()
    if later_page:
        await _next_listing_page(pager, is_async)
    backend._response = BackendResponse(
        status_code=403,
        headers=CaseInsensitiveDict({"x-ms-activity-id": "failed"}),
        body=b'{"code":"Forbidden","message":"denied"}',
    )
    with pytest.raises(CosmosHttpResponseError) as error:
        await _next_listing_page(pager, is_async)
    assert error.value.status_code == 403
    assert len(hooks) == int(later_page)
    assert backend.execute_pages.call_count == 1 + int(later_page)
    conn._CosmosClientConnection__Get.assert_not_called()
    conn._CosmosClientConnection__Post.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("error_type", [ValueError, PagePreflightError, asyncio.CancelledError])
async def test_database_feed_hook_errors_propagate_without_replay(listing_client, database_feed, error_type):
    """A failing hook is never treated as a reason to retry on the legacy path.

    Three kinds of failure: an ordinary ``ValueError``, a backend capability
    error, and a cancellation. Each reaches the caller as the exact object
    raised.

    The page ran once, the legacy transport was not used, and the
    compatibility fallback counter did not move. Even a capability-shaped
    exception raised by customer code is propagated, not used to replay a page.
    """
    _, conn, backend, is_async = listing_client
    error = error_type("hook failure")
    hook = MagicMock(side_effect=error)
    fallback_before = rust_compatibility_fallback_count()
    with pytest.raises(error_type) as raised:
        await _listing_rows(database_feed(response_hook=hook), is_async)
    assert raised.value is error
    hook.assert_called_once()
    assert backend.execute_pages.call_count == 1
    conn._CosmosClientConnection__Get.assert_not_called()
    conn._CosmosClientConnection__Post.assert_not_called()
    assert rust_compatibility_fallback_count() == fallback_before


@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics", "availability_strategy"])
@pytest.mark.parametrize("value", [None, False, True, "unused", CrossRegionHedgingStrategy()])
@pytest.mark.parametrize("use_legacy_backend", [False, True], ids=["rust", "core-python"])
def test_database_feed_rejects_irrelevant_arguments_before_iteration(
    listing_client, database_feed, option, value, use_legacy_backend
):
    """Options that mean nothing for a database feed are rejected at the call, on both backends.

    ``session_token``, ``populate_query_metrics`` and
    ``availability_strategy`` do not apply to listing or querying databases.
    Each is refused with a ``TypeError`` naming the option, for every value
    tried -- including ``None``, since even passing it explicitly is a sign
    the caller expects it to do something.

    The rejection happens while building the iterable, before any pager
    exists, and behaves the same whether the client is on Rust or core-python.
    Accepting and ignoring them would leave a customer believing they had set
    a session token on a call that never sends one.
    """
    _, conn, backend, is_async = listing_client
    if use_legacy_backend:
        conn._backend = ASYNC_LEGACY_BACKEND if is_async else LEGACY_BACKEND
    conn.ReadDatabases = MagicMock(side_effect=AssertionError("must reject before constructing the pager"))
    conn.QueryDatabases = MagicMock(side_effect=AssertionError("must reject before constructing the pager"))
    hook = MagicMock()
    with pytest.raises(TypeError, match=option):
        database_feed(response_hook=hook, **{option: value})
    hook.assert_not_called()
    conn.ReadDatabases.assert_not_called()
    conn.QueryDatabases.assert_not_called()
    backend.execute_pages.assert_not_called()
    conn._CosmosClientConnection__Get.assert_not_called()
    conn._CosmosClientConnection__Post.assert_not_called()


@pytest.mark.parametrize("args", [(2,), (2, False)])
def test_list_databases_settings_are_keyword_only(listing_client, args):
    """``list_databases`` takes no positional arguments.

    A positional page size, alone or with a second value, is a ``TypeError``
    rather than being bound to whichever parameter happens to come first. That
    keeps the signature free to change without silently changing what existing
    callers mean.
    """
    client, _, backend, _ = listing_client
    with pytest.raises(TypeError):
        client.list_databases(*args)
    backend.execute_pages.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("later_page", [False, True])
@pytest.mark.parametrize("error_type", [PagePreflightError, UnsupportedQueryError])
async def test_database_feed_capability_errors_never_replay(
    listing_client, database_feed, later_page, error_type
):
    """A backend that cannot serve a database page reports it; it does not fall back to legacy.

    The injected capability error reaches the caller unchanged, on the first
    page or a later one. This test does not establish item-query routing rules.

    The fallback counter does not move and the legacy transport is untouched.
    Replaying a partly consumed feed on another backend would re-send pages
    the caller already has, with tokens the other backend cannot read.
    """
    _, conn, backend, is_async = listing_client
    hooks = []
    pager = database_feed(response_hook=hooks.append).by_page()
    if later_page:
        await _next_listing_page(pager, is_async)
    error = error_type("unsupported database page")
    backend.execute_pages.side_effect = error
    fallback_before = rust_compatibility_fallback_count()
    with pytest.raises(error_type) as raised:
        await _next_listing_page(pager, is_async)
    assert raised.value is error
    assert len(hooks) == int(later_page)
    assert backend.execute_pages.call_count == 1 + int(later_page)
    conn._CosmosClientConnection__Get.assert_not_called()
    conn._CosmosClientConnection__Post.assert_not_called()
    assert rust_compatibility_fallback_count() == fallback_before


@pytest.mark.parametrize("read_timeout", [0, 0.5, 30, False, "invalid"])
def test_database_feed_rejects_per_call_read_timeout(listing_client, database_feed, read_timeout):
    """``read_timeout`` cannot be set per call on a database feed.

    Every value is refused with a ``TypeError`` naming the option, including
    ``0`` and ``False``, which a looser check based on truthiness would let
    through. The read timeout is a client-level transport setting, so
    accepting it here would imply a per-call control that does not exist.

    Nothing is constructed or sent.
    """
    _, conn, backend, _ = listing_client
    conn.QueryDatabases = MagicMock(side_effect=AssertionError("pager must not be constructed"))
    conn.ReadDatabases = MagicMock(side_effect=AssertionError("pager must not be constructed"))
    hook = MagicMock()
    with pytest.raises(TypeError, match="'read_timeout'"):
        database_feed(read_timeout=read_timeout, response_hook=hook)
    hook.assert_not_called()
    backend.execute_pages.assert_not_called()
    conn.QueryDatabases.assert_not_called()
    conn.ReadDatabases.assert_not_called()


@pytest.mark.asyncio
async def test_database_feed_accepts_unset_read_timeout(listing_client, database_feed):
    """Passing ``read_timeout=None`` is allowed, because it asks for nothing.

    The counterpart to the rejection test. ``None`` means "not supplied", so
    it is accepted and paging works normally with the other settings intact.

    This matters for callers that pass every option through from their own
    config, most of them unset; they should not have to strip the Nones out.
    """
    _, _, backend, is_async = listing_client
    pager = database_feed(read_timeout=None, max_item_count=1).by_page()
    await _next_listing_page(pager, is_async)
    assert backend.prepared.max_item_count == 1


@pytest.mark.parametrize("is_query", [False, True], ids=["list", "query"])
@pytest.mark.parametrize(
    "timeout, supported",
    [
        (None, True), (1, True), (3.5, True), (10, True),
        (0.5, False), (0, False), (-1, False), (True, False), (False, False),
        ("10", False), (float("nan"), False), (float("inf"), False),
        (float("-inf"), False), (2**64, False), (2**64 - 1, False),
        pytest.param(10**1000, False, id="overflowing-integer"),
    ],
)
def test_database_feed_gate_only_accepts_representable_timeouts(is_query, timeout, supported):
    """The routing gate only sends a page to Rust when the timeout can be represented.

    Accepted: no timeout at all, and ordinary positive numbers.

    Rejected: sub-second values, zero and negatives, ``True``/``False`` (bools
    are integers in Python and would otherwise pass as 1 and 0), a numeric
    string, ``nan`` and both infinities, and integers at or beyond the 64-bit
    range -- including one far too large for any native integer.

    A timeout the driver cannot express is not a small problem: it could be
    truncated or wrapped into a completely different deadline. Declining to
    route keeps those calls on the legacy path instead. Checked for both
    listing and querying databases.
    """
    arguments = {
        "options": {"timeout": timeout},
        "kwargs": {"timeout": timeout},
        "is_query_plan": False,
        "resource_type": http_constants.ResourceType.Database,
    }
    if is_query:
        result = can_use_rust_backend_for_query_databases_page(
            query_payload={"query": "SELECT * FROM root r"}, **arguments
        )
    else:
        result = can_use_rust_backend_for_list_databases_page(**arguments)
    assert result is supported


@pytest.mark.parametrize(
    "options, kwargs, supported",
    [
        ({"timeout": 10}, {}, True),
        ({}, {"timeout": 10}, False),
        ({"timeout": 10}, {"timeout": 20}, False),
        ({"timeout": 10}, {"timeout": None}, False),
    ],
)
def test_database_feed_timeout_must_match_the_forwarded_option(options, kwargs, supported):
    """A page only routes to Rust when the timeout in the options is the one being forwarded.

    Routing is allowed when the options carry the timeout and the keyword
    arguments do not contradict it. It is refused when the timeout appears
    only in the keyword arguments, when the two disagree, and when the keyword
    arguments explicitly unset it.

    The gate inspects the options, but the driver is handed the keyword
    arguments. If they can differ, the value checked is not the value used --
    so the honest response is to decline rather than send a request under a
    deadline nobody verified.
    """
    assert can_use_rust_backend_for_list_databases_page(
        options=options, kwargs=kwargs, is_query_plan=False,
        resource_type=http_constants.ResourceType.Database,
    ) is supported


@pytest.mark.parametrize("is_query", [False, True], ids=["list", "query"])
def test_container_feeds_support_page_timeouts(is_query):
    """Container listing and querying accept a page timeout too.

    The same check as for databases, one resource level down, for both listing
    and querying containers. Container feeds are a separate routing gate, so
    without this a timeout could be supported for databases and quietly
    unsupported for containers.
    """
    arguments = {
        "path": "/dbs/db1/colls/",
        "options": {"timeout": 10},
        "kwargs": {"timeout": 10},
        "is_query_plan": False,
        "resource_type": http_constants.ResourceType.Collection,
    }
    if is_query:
        supported = can_use_rust_backend_for_query_containers_page(
            query_payload={"query": "SELECT * FROM root r"}, **arguments
        )
    else:
        supported = can_use_rust_backend_for_list_containers_page(**arguments)
    assert supported is True


def _configure_legacy_database_feed(conn, is_async):
    conn._backend = ASYNC_LEGACY_BACKEND if is_async else LEGACY_BACKEND

    def response(*_args, **_kwargs):
        headers = CaseInsensitiveDict({
            "x-ms-continuation": "next-db-page",
            "x-ms-activity-id": "legacy-page",
        })
        conn.last_response_headers = headers
        return {"Databases": [{"id": "db-1"}]}, headers

    conn._CosmosClientConnection__Get.side_effect = response
    conn._CosmosClientConnection__Post.side_effect = response
    conn._UpdateSessionIfRequired = MagicMock()


@pytest.mark.asyncio
@pytest.mark.parametrize("use_legacy", [False, True], ids=["rust", "core-python"])
async def test_database_feed_timeout_resets_per_page_and_replay(
    listing_client, database_feed, monkeypatch, use_legacy
):
    """``timeout`` bounds each page, so time spent in the caller's own code never counts.

    The clock jumps 100 seconds three times: after building the iterable,
    between two pages, and before resuming from a token. With a 3.5 second
    timeout, none of that causes a failure.

    This is the difference between a per-page budget and a whole-enumeration
    one. A customer looping over databases and doing real work for each must
    not have iteration die because their processing took longer than the
    timeout. Building the iterable does not start any clock either.

    Every page is sent the full 3.5 seconds, and the behaviour is the same on
    Rust and core-python -- each staying on its own transport.
    """
    _, conn, backend, is_async = listing_client
    if use_legacy:
        _configure_legacy_database_feed(conn, is_async)
        listing_client[0]._backend = conn._backend
    clock = [100.0]
    monkeypatch.setattr(time, "time", lambda: clock[0])
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    iterable = database_feed(timeout=3.5)
    clock[0] += 100  # Constructing the lazy pager does not start its default page budget.
    pager = iterable.by_page()
    assert await _next_listing_page(pager, is_async)
    continuation = pager.continuation_token
    clock[0] += 100  # Application time between pages is not charged to the next page.
    assert await _next_listing_page(pager, is_async)
    clock[0] += 100
    assert await _next_listing_page(iterable.by_page(continuation), is_async)
    if use_legacy:
        backend.execute_pages.assert_not_called()
        assert conn._CosmosClientConnection__Get.call_count + conn._CosmosClientConnection__Post.call_count == 3
    else:
        assert backend.execute_pages.call_count == 3
        assert settings_options(backend.prepared)["timeout_seconds"] == 3.5
        conn._CosmosClientConnection__Get.assert_not_called()
        conn._CosmosClientConnection__Post.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("use_legacy", [False, True], ids=["rust", "core-python"])
@pytest.mark.parametrize("fetch_first", [False, True])
async def test_database_feed_retains_existing_operation_scope_checks(
    listing_client, database_feed, monkeypatch, use_legacy, fetch_first
):
    """Asking for an operation-wide timeout brings back the stricter, older behaviour.

    Per-page budgets are the default, but a caller can request that the
    timeout cover the whole operation. With that set, the clock passing the
    deadline ends the enumeration with a timeout error -- whether or not a
    page was fetched first.

    Both backends behave the same and neither crosses to the other's
    transport. The fallback counter does not move: a timeout is the caller's
    deadline expiring, not a sign the backend was incapable.
    """
    _, conn, backend, is_async = listing_client
    if use_legacy:
        _configure_legacy_database_feed(conn, is_async)
        listing_client[0]._backend = conn._backend
    clock = [100.0]
    monkeypatch.setattr(time, "time", lambda: clock[0])
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    pager = database_feed(
        timeout=3.5, request_options={Constants.TimeoutScope: TimeoutScope.OPERATION}
    ).by_page()
    if fetch_first:
        await _next_listing_page(pager, is_async)
    clock[0] += 4
    before = rust_compatibility_fallback_count()
    with pytest.raises(CosmosClientTimeoutError):
        await _next_listing_page(pager, is_async)
    if use_legacy:
        backend.execute_pages.assert_not_called()
        assert conn._CosmosClientConnection__Get.call_count + conn._CosmosClientConnection__Post.call_count == int(fetch_first)
    else:
        assert backend.execute_pages.call_count == int(fetch_first)
        conn._CosmosClientConnection__Get.assert_not_called()
        conn._CosmosClientConnection__Post.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.asyncio
async def test_database_feed_empty_pages_do_not_restart_expired_budget(listing_client, database_feed, monkeypatch):
    """An empty page that overruns the budget ends the call instead of quietly paging on.

    The backend returns an empty page with a continuation token, taking 4
    seconds against a 3.5 second budget.

    Empty pages are consumed internally, so the loop would naturally fetch the
    next one. It must check the budget first: a run of slow empty pages would
    otherwise keep a timed-out enumeration going indefinitely, invisible to
    the caller because no rows are being produced.

    Exactly one page is fetched, and the fallback counter does not move.
    """
    _, conn, backend, is_async = listing_client
    clock = [100.0]
    monkeypatch.setattr(time, "time", lambda: clock[0])
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    backend._response = BackendResponse(
        status_code=200,
        headers=CaseInsensitiveDict({"x-ms-continuation": "next-db-page"}),
        body=b'{"Databases":[]}',
    )
    execute = type(backend).execute_pages

    def slow_page(prepared, *, deadline=None):
        clock[0] += 4
        return execute(backend, prepared, deadline=deadline)

    backend.execute_pages.side_effect = slow_page
    before = rust_compatibility_fallback_count()
    with pytest.raises(CosmosClientTimeoutError):
        await _listing_rows(database_feed(timeout=3.5), is_async)
    backend.execute_pages.assert_called_once()
    conn._CosmosClientConnection__Get.assert_not_called()
    conn._CosmosClientConnection__Post.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.asyncio
async def test_database_feed_driver_timeout_propagates_without_replay(listing_client, database_feed, monkeypatch):
    """A timeout raised by the driver reaches the caller and is not retried on legacy.

    The driver itself raises ``CosmosClientTimeoutError``. It surfaces as-is,
    the hook is never called since no page was delivered, the page ran once,
    and the fallback counter does not move.

    A timeout means the deadline passed, not that the backend was incapable.
    Retrying on the legacy path would ignore the deadline the caller set and
    double the work.
    """
    _, conn, backend, is_async = listing_client
    clock = [100.0]
    monkeypatch.setattr(time, "time", lambda: clock[0])
    error = CosmosClientTimeoutError()

    def timed_out(_prepared, *, deadline=None):
        clock[0] += 4
        raise error

    backend.execute_pages.side_effect = timed_out
    hooks = []
    before = rust_compatibility_fallback_count()
    with pytest.raises(CosmosClientTimeoutError):
        await _listing_rows(database_feed(timeout=3.5, response_hook=hooks.append), is_async)
    assert hooks == []
    backend.execute_pages.assert_called_once()
    conn._CosmosClientConnection__Get.assert_not_called()
    conn._CosmosClientConnection__Post.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kwargs",
    [
        {"timeout": 0.5},
        {"connection_timeout": 1},
        {"initial_headers": {"USER-AGENT": "custom"}},
        {"initial_headers": {"x-ms-version": "2020-07-15"}},
        {"raw_request_hook": lambda request: None},
        {"raw_response_hook": lambda response: None},
        {"unknown_option": True},
    ],
)
async def test_database_feed_unsupported_public_options_never_fall_back(
    listing_client, database_feed, kwargs
):
    """Options the Rust database feed cannot honour fail loudly instead of falling back.

    Covers a sub-second timeout, a connection timeout, overriding the user
    agent or API version header, the raw request and response hooks, and an
    unrecognised keyword.

    These database feeds reject unsupported transport options with a
    ``NotImplementedError`` naming the legacy Python path. The hook is never
    called, neither transport is used, and the fallback counter does not move.

    Both listing and query reject an invalid timeout while constructing the
    iterator, before any page can be requested.
    """
    _, conn, backend, is_async = listing_client
    hook = MagicMock()
    fallback_before = rust_compatibility_fallback_count()
    if "timeout" in kwargs:
        with pytest.raises(ValueError, match="timeout"):
            database_feed(response_hook=hook, **kwargs)
        backend.execute_pages.assert_not_called()
        return
    iterable = database_feed(response_hook=hook, **kwargs)
    hook.assert_not_called()
    with pytest.raises(NotImplementedError, match="legacy Python"):
        await _next_listing_page(iterable.by_page(), is_async)
    hook.assert_not_called()
    backend.execute_pages.assert_not_called()
    conn._CosmosClientConnection__Get.assert_not_called()
    conn._CosmosClientConnection__Post.assert_not_called()
    assert rust_compatibility_fallback_count() == fallback_before


@pytest.mark.asyncio
async def test_query_databases_old_sql_mode_does_not_fall_back(listing_client):
    """An unsupported internal query mode fails validation rather than rerouting.

    With the connection switched to the old SQL query compatibility mode, the
    existing format validator rejects the call before anything is dispatched.

    Nothing is sent on either transport and the fallback counter does not
    move: a rejected format is a programming error, not a sign the Rust
    backend was incapable of the work.
    """
    client, conn, backend, is_async = listing_client
    conn._query_compatibility_mode = conn._QueryCompatibilityMode.SqlQuery
    fallback_before = rust_compatibility_fallback_count()
    # The existing format validator rejects this private mode before dispatch.
    with pytest.raises(SystemError, match="Unexpected query compatibility mode"):
        await _listing_rows(client.query_databases("SELECT * FROM root r"), is_async)
    backend.execute_pages.assert_not_called()
    conn._CosmosClientConnection__Post.assert_not_called()
    assert rust_compatibility_fallback_count() == fallback_before


@pytest.mark.parametrize("value", [None, False, True])
def test_query_databases_rejects_old_positional_query_metrics(value):
    """The old positional call shape is no longer accepted.

    ``query_databases`` once took several positional arguments ending in a
    query-metrics flag. Passing them now raises ``TypeError`` instead of being
    silently reinterpreted under the current signature, which would bind those
    values to entirely different parameters.
    """
    client = object.__new__(CosmosClient)
    client.client_connection = MagicMock()
    with pytest.raises(TypeError):
        client.query_databases("SELECT * FROM root r", None, False, 20, value)
    client.client_connection.QueryDatabases.assert_not_called()


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
@pytest.mark.parametrize(
    "args",
    [
        (),
        ("SELECT * FROM root r", []),
        ("SELECT * FROM root r", [], True),
        ("SELECT * FROM root r", [], True, 20),
    ],
)
def test_query_databases_requires_query_and_keyword_only_settings(client_type, args):
    """The query is required, and everything after it must be passed by name.

    No arguments at all fails, and so does any call that passes parameters,
    the cross-partition flag, or a page size positionally after the query.

    Checked on both the sync and async clients so the two signatures cannot
    drift apart. Nothing is dispatched and the hook is never called.
    """
    client = object.__new__(client_type)
    client.client_connection = MagicMock()
    hook = MagicMock()
    with pytest.raises(TypeError):
        client.query_databases(*args, response_hook=hook)
    hook.assert_not_called()
    client.client_connection.QueryDatabases.assert_not_called()
    client.client_connection.ReadDatabases.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("query_by_keyword", [False, True])
async def test_query_databases_accepts_positional_or_named_query_with_keyword_settings(listing_client, query_by_keyword):
    """The query may be given positionally or by name, and both build the same request.

    The positive counterpart to the signature tests. Either way the query and
    its parameters are packed into one payload and the page size is translated
    to its wire name.

    The cross-partition flag is absent from the options. Database queries are
    never partitioned, so sending it would be meaningless -- and it is
    rejected outright if a caller passes it.
    """
    client, connection, backend, is_async = listing_client
    query = "SELECT * FROM root r WHERE r.id = @id"
    parameters = [{"name": "@id", "value": "db-1"}]
    options = {"parameters": parameters, "max_item_count": 20}
    if query_by_keyword:
        result = client.query_databases(query=query, **options)
    else:
        result = client.query_databases(query, **options)
    backend.execute_pages.assert_not_called()
    assert await _next_listing_page(result.by_page(), is_async)
    assert backend.prepared.query == query
    assert dict(backend.prepared.parameters[0]) == parameters[0]
    assert backend.prepared.max_item_count == 20
    assert "x-ms-documentdb-query-enablecrosspartition" not in backend.prepared.headers
    connection._CosmosClientConnection__Post.assert_not_called()


@pytest.mark.parametrize("value", [None, False, True])
@pytest.mark.parametrize("query", [None, "SELECT * FROM root r"])
@pytest.mark.parametrize("use_legacy_backend", [False, True], ids=["rust", "core-python"])
def test_query_databases_rejects_cross_partition_option_before_iteration(
    listing_client, value, query, use_legacy_backend
):
    """``enable_cross_partition_query`` is refused for database queries on both backends.

    Databases are not partitioned, so the option has no meaning here. It is
    rejected with a ``TypeError`` naming it, for every value including
    ``None`` and ``False``, with or without a query, on Rust and core-python
    alike.

    Rejecting even ``False`` is deliberate: passing it at all means the caller
    thinks the setting applies. Nothing is constructed or sent.
    """
    client, conn, backend, is_async = listing_client
    if use_legacy_backend:
        conn._backend = ASYNC_LEGACY_BACKEND if is_async else LEGACY_BACKEND
    conn.QueryDatabases = MagicMock(side_effect=AssertionError("pager must not be constructed"))
    conn.ReadDatabases = MagicMock(side_effect=AssertionError("pager must not be constructed"))
    hook = MagicMock()
    with pytest.raises(TypeError, match="'enable_cross_partition_query'"):
        client.query_databases(query, enable_cross_partition_query=value, response_hook=hook)
    hook.assert_not_called()
    conn.QueryDatabases.assert_not_called()
    conn.ReadDatabases.assert_not_called()
    backend.execute_pages.assert_not_called()
    conn._CosmosClientConnection__Get.assert_not_called()
    conn._CosmosClientConnection__Post.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "resource_type, path, body_key, query, op",
    [
        (http_constants.ResourceType.Database, "/dbs/", "Databases", None, OP_LIST_DATABASES),
        (http_constants.ResourceType.Database, "/dbs/", "Databases", {"query": "SELECT * FROM c"}, OP_QUERY_DATABASES),
        (http_constants.ResourceType.Collection, "/dbs/db/colls/", "DocumentCollections", None, OP_LIST_CONTAINERS),
        (http_constants.ResourceType.Collection, "/dbs/db/colls/", "DocumentCollections",
         {"query": "SELECT * FROM c"}, OP_QUERY_CONTAINERS),
        (http_constants.ResourceType.Document, "/dbs/db/colls/c/docs/", "Documents", None, OP_READ_ALL_ITEMS),
        (http_constants.ResourceType.Document, "/dbs/db/colls/c/docs/", "Documents",
         {"query": "SELECT * FROM c"}, OP_QUERY_ITEMS),
    ],
)
async def test_all_rust_feed_operations_expose_diagnostics(
    monkeypatch, is_async, resource_type, path, body_key, query, op
):
    """Every Rust feed operation reports diagnostics everywhere, and prepares no legacy headers.

    Runs all six paged operations -- listing and querying databases,
    containers and items -- sync and async, and checks each is tagged with its
    own operation identity.

    The diagnostics string has to reach all four places a customer might look:
    the connection's last response headers, the caller's headers dict, the
    internal capture, and the response hook. Reaching only some would make
    diagnostics appear or vanish depending on how the call was made.

    The legacy header machinery -- header building, session tokens,
    authorization, request id generation -- is replaced with something that
    fails if touched. The Rust path builds its own requests, and quietly
    running the legacy preparation as well would mean signing and tagging
    every request twice.
    """
    conn = _new_async_connection() if is_async else _new_sync_connection()
    backend_type = _CapturingAsyncBackend if is_async else _CapturingSyncBackend
    diagnostics = f"activity={op} requests=1"
    backend = backend_type(BackendResponse(
        status_code=200,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "2"}),
        body=json.dumps({body_key: [{"id": "result"}]}).encode("utf-8"),
        diagnostics=diagnostics,
    ))
    conn._backend = backend
    forbidden = MagicMock(side_effect=AssertionError("Rust feed must not prepare legacy headers"))
    for name in ("GetHeaders", "set_session_token_header", "set_session_token_header_async",
                 "_get_authorization_header", "GenerateGuidId"):
        monkeypatch.setattr(base_helpers, name, forbidden)
    public_headers = CaseInsensitiveDict()
    internal_headers = {}
    hook = MagicMock()
    result = conn._CosmosClientConnection__QueryFeed(
        path, resource_type, "", lambda body: body[body_key], lambda _, body: body,
        query, {}, response_hook=hook, response_headers=public_headers,
        _internal_response_headers_capture=internal_headers,
    )
    if is_async:
        await result
    assert backend.prepared.op == op
    forbidden.assert_not_called()
    assert "x-ms-activity-id" not in wire_headers(backend.prepared)
    for headers in (conn.last_response_headers, public_headers, internal_headers):
        assert headers["x-ms-cosmos-sdk-diagnostics"] == diagnostics
    hook.assert_called_once()
    assert hook.call_args.args[0]["x-ms-cosmos-sdk-diagnostics"] == diagnostics


def _new_sync_connection() -> SyncConnection:
    """Create a synchronous connection for routing tests."""
    conn = SyncConnection.__new__(SyncConnection)
    conn._response_state = ClientLastResponseHeaders()
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
    conn._response_state = ClientLastResponseHeaders()
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
    prepared = PreparedPageRequest(
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

    assert wire_headers(request)["x-ms-continuation"] == "typed-continuation"
    assert wire_headers(request)["x-ms-max-item-count"] == "0"


def test_rust_feed_prep_has_one_paging_authority():
    """Typed options win; raw-header-only paging is promoted rather than lost."""
    prepared = build_list_databases_prepared_query(
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

    assert wire_headers(prepared) == {
        "x-ms-documentdb-isquery": "true",
        "x-customer-header": "preserved",
    }
    assert prepared.continuation == "typed-continuation"
    assert prepared.max_item_count == 0
    prepared = build_list_databases_prepared_query(
        options={},
        req_headers={
            "x-ms-continuation": "customer-continuation",
            "x-ms-max-item-count": "7",
        },
    )
    assert prepared.continuation == "customer-continuation"
    assert prepared.max_item_count == 7
    assert wire_headers(prepared) == {}


@pytest.mark.parametrize("count", ["", "not-an-integer", "2.5"])
def test_rust_feed_rejects_invalid_raw_page_size(count):
    """A page size supplied as a raw header must be a whole number.

    Callers can set paging headers directly. An empty string, a word, and
    ``"2.5"`` are each rejected with a message naming the header.

    The value becomes a native integer, so a non-integer would otherwise fail
    somewhere deep in the driver with no hint of which header caused it.
    """
    with pytest.raises(ValueError, match="x-ms-max-item-count must be an integer"):
        build_list_databases_prepared_query(
            options={"initialHeaders": {"X-MS-MAX-ITEM-COUNT": count}}, req_headers={},
        )


@pytest.mark.parametrize("typed", [False, True])
def test_rust_feed_header_and_paging_precedence_is_case_insensitive(typed):
    """Header names match regardless of case, and typed settings outrank raw headers.

    The caller supplies upper-case headers over lower-case defaults. Matching
    is case-insensitive, so the caller's value wins each time rather than both
    surviving as two spellings of one header.

    Paging headers are consumed rather than forwarded: continuation and page
    size become typed fields and disappear from the wire headers. When typed
    values are also given they take precedence -- including ``maxItemCount=0``,
    which a truthiness check would wrongly discard in favour of the header.

    The typed throughput bucket likewise beats the raw header. Options that
    belong to other resource kinds, such as a container id or an item session
    token, are ignored here, while a genuine raw session token and activity id
    pass through.

    Neither the caller's options nor the defaults dict is modified, so a
    caller reusing either across calls is safe.
    """
    options = {
        "initialHeaders": {
            "X-MS-CONTINUATION": "caller-token", "X-MS-MAX-ITEM-COUNT": "7",
            "X-APP": "caller", "X-MS-COSMOS-THROUGHPUT-BUCKET": "2",
            "X-MS-ACTIVITY-ID": "caller-activity", "X-MS-SESSION-TOKEN": "raw-session",
        },
        "throughputBucket": 3,
        "containerRID": "not-a-database-header",
        "sessionToken": "not-a-master-resource-token",
    }
    if typed:
        options.update(maxItemCount=0, continuation="typed-token")
    defaults = {
        "x-ms-continuation": "default-token", "x-ms-max-item-count": "3",
        "x-app": "default", "x-ms-consistency-level": "Session",
    }
    prepared = build_list_databases_prepared_query(options=options, req_headers=defaults)
    assert prepared.max_item_count == (0 if typed else 7)
    assert prepared.continuation == ("typed-token" if typed else "caller-token")
    assert wire_headers(prepared) == {
        "x-app": "caller", "x-ms-cosmos-throughput-bucket": "3",
        "x-ms-activity-id": "caller-activity", "x-ms-session-token": "raw-session",
        "x-ms-consistency-level": "Session",
    }
    assert defaults["x-app"] == "default"
    assert options["initialHeaders"]["X-MS-MAX-ITEM-COUNT"] == "7"


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("route", ["legacy", "capability-fallback", "ineligible", "query-plan"])
async def test_query_legacy_preparation_is_lazy_but_preserved(monkeypatch, is_async, route):
    """Whenever a query does end up on the legacy path, it is prepared exactly as before.

    Four ways to get there: a legacy backend, a backend that rejects the page
    shape, an option the Rust path cannot represent, and a query plan call.

    In every case the legacy request is built once -- not zero times, which
    would send an unsigned request, and not twice, which would mean the work
    was done eagerly and then repeated. The caller's own header survives and
    an activity id is attached.

    Session token handling runs for real queries but is skipped for query plan
    calls, which do not carry one. Preparing legacy headers is only skipped
    when the Rust path actually serves the request, so falling back must not
    leave a request half-prepared.
    """
    conn = _new_async_connection() if is_async else _new_sync_connection()
    backend_type = _CapturingAsyncBackend if is_async else _CapturingSyncBackend
    backend = backend_type(BackendResponse(status_code=200, body=b'{"Documents":[]}'))
    if route != "legacy":
        conn._backend = backend
    if route == "capability-fallback":
        backend.validate_page_request = MagicMock(side_effect=PagePreflightError("unsupported test shape"))
    headers_spy = MagicMock(wraps=base_helpers.GetHeaders)
    monkeypatch.setattr(base_helpers, "GetHeaders", headers_spy)
    session_spy = AsyncMock() if is_async else MagicMock()
    monkeypatch.setattr(
        base_helpers, "set_session_token_header_async" if is_async else "set_session_token_header", session_spy,
    )
    post = (AsyncMock if is_async else MagicMock)(
        return_value=({"Documents": [{"id": "legacy-result"}]}, CaseInsensitiveDict()),
    )
    conn._CosmosClientConnection__Post = post
    options = {"initialHeaders": {"x-application": "caller"}}
    if route == "ineligible":
        options["read_timeout"] = 2
    call = _run_async_query_feed if is_async else _run_sync_query_feed
    result = call(
        conn, query={"query": "SELECT * FROM c"}, options=options, is_query_plan=route == "query-plan",
    )
    rows = await result if is_async else result[0]
    assert rows == [{"id": "legacy-result"}]
    headers_spy.assert_called_once()
    assert session_spy.call_count == (0 if route == "query-plan" else 1)
    assert post.call_args.args[3]["x-application"] == "caller"
    assert "x-ms-activity-id" in post.call_args.args[3]


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
    the driver's reply decides whether it can run them. But options the Rust page
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
    """Sync query page. A Rust-served page builds the right ``PreparedPageRequest`` (op,
    container link, partition-key header, continuation, max item count, forwarded
    excluded-locations and timeout), returns the parsed Documents, decodes the
    index-utilization header, and updates both ``response_headers`` and the response
    hook, retaining the SDK's additional diagnostics header.
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
    assert headers["x-ms-cosmos-sdk-diagnostics"] == "diag"
    assert response_headers["x-ms-cosmos-sdk-diagnostics"] == "diag"
    assert len(hook_calls) == 1
    assert hook_calls[0][0][http_constants.HttpHeaders.IndexUtilization] == {"indexUsed": True}
    assert hook_calls[0][0]["x-ms-cosmos-sdk-diagnostics"] == "diag"

    prepared = backend.prepared
    assert prepared is not None
    assert prepared.op == OP_QUERY_ITEMS
    assert prepared.container_link == "dbs/db/colls/c"
    assert legacy_partition_key_from_request(prepared) == '["tenant-a"]'
    assert prepared.continuation == "ct-in"
    assert prepared.max_item_count == 25
    assert settings_options(prepared)["excludedLocations"] == ["West US"]
    assert settings_options(prepared)["timeout_seconds"] == 9


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
    assert legacy_partition_key_from_request(prepared) == "[]"


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
        assert conn.last_response_headers["x-ms-cosmos-sdk-diagnostics"] == "diag"
        assert response_headers["x-ms-cosmos-sdk-diagnostics"] == "diag"
        assert len(hook_calls) == 1
        assert hook_calls[0][0][http_constants.HttpHeaders.IndexUtilization] == {"indexUsed": True}
        assert hook_calls[0][0]["x-ms-cosmos-sdk-diagnostics"] == "diag"

        prepared = backend.prepared
        assert prepared is not None
        assert prepared.op == OP_QUERY_ITEMS
        assert prepared.container_link == "dbs/db/colls/c"
        assert legacy_partition_key_from_request(prepared) == '["tenant-a"]'
        assert settings_options(prepared)["excludedLocations"] == ["East US"]
        assert settings_options(prepared)["timeout_seconds"] == 11

    asyncio.run(_run())


def test_async_query_backend_eligibility_honors_unsupported_request_options():
    """Async query eligibility gate: an unrepresentable option (``populateQueryAdvice``)
    blocks the Rust page path on the async connection too.
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


def test_sync_read_all_marks_unsupported_options_as_rust_ineligible():
    """Check which sync read-all inputs the Rust eligibility function accepts.

    A plain document read-feed is eligible; the listed unsupported options and
    resource kinds are not. This tests selection, not execution of a fallback.
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


def test_async_read_all_marks_unsupported_options_as_rust_ineligible():
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
    assert legacy_partition_key_from_request(prepared) == "[]"
    assert http_constants.HttpHeaders.PartitionKey not in wire_headers(prepared)
    assert settings_options(prepared)["excludedLocations"] == ["West US"]
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
        assert legacy_partition_key_from_request(prepared) == "[]"
        assert http_constants.HttpHeaders.PartitionKey not in wire_headers(prepared)
        assert settings_options(prepared)["excludedLocations"] == ["East US"]
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
#   * an unsupported option raises instead of switching to the old path
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
    assert backend.prepared.partition_key.kind == "cross_partition"
    assert backend.prepared.max_item_count == 1
    assert backend.prepared.continuation == "start"
    assert wire_headers(backend.prepared)["x-ms-cosmos-throughput-bucket"] == "7"
    assert wire_headers(backend.prepared)["x-test-header"] == "yes"
    assert all(wire_headers(backend.prepared).get(key.lower()) == str(value) for key, value in ({"x-test-header": "yes"}).items())


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
    conn.default_headers = {
        "authorization": "SDK default",
        "x-ms-date": "SDK default",
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "User-Agent": "python-agent",
        "x-ms-version": "2020-07-15",
        "x-ms-cosmos-throughput-bucket": "7",
    }
    monkeypatch.setattr(
        base_helpers, "GetHeaders",
        MagicMock(side_effect=AssertionError("legacy preparation must not run")),
    )

    result, _ = _run_sync_read_feed(
        conn,
        resource_type=http_constants.ResourceType.Database,
        options={},
    )

    assert result == []
    assert wire_headers(backend.prepared) == {"x-ms-cosmos-throughput-bucket": "7"}


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
    assert wire_headers(backend.prepared)["x-default-header"] == "yes"


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
        assert wire_headers(backend.prepared)["x-default-header"] == "yes"

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
def test_async_list_databases_backend_rejects_unrepresentable_options(monkeypatch, options, kwargs):
    """Unsupported listing options must not cross into legacy transport."""
    async def _run() -> None:
        conn = _new_async_connection()
        backend = _CapturingAsyncBackend(BackendResponse(status_code=200))
        conn._backend = backend
        monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})

        async def _set_session(*_args, **_kwargs):
            return None

        legacy_get = AsyncMock(side_effect=AssertionError("legacy replay"))

        monkeypatch.setattr(base_helpers, "set_session_token_header_async", _set_session)
        monkeypatch.setattr(conn, "_CosmosClientConnection__Get", legacy_get)
        monkeypatch.setattr(conn, "_UpdateSessionIfRequired", lambda *args, **kwargs: None)

        fallback_count = rust_compatibility_fallback_count()
        with pytest.raises(NotImplementedError, match="list_databases"):
            await _run_async_read_feed(
                conn,
                resource_type=http_constants.ResourceType.Database,
                options=options,
                **kwargs,
            )

        assert backend.prepared is None
        legacy_get.assert_not_called()
        assert rust_compatibility_fallback_count() == fallback_count

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
def test_list_databases_backend_rejects_unrepresentable_options(monkeypatch, options, kwargs):
    """Unsupported listing options raise before either transport sends a page."""
    conn = _new_sync_connection()
    backend = _CapturingSyncBackend(BackendResponse(status_code=200))
    conn._backend = backend
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})
    monkeypatch.setattr(base_helpers, "set_session_token_header", lambda *args, **kwargs: None)
    legacy_get = MagicMock(side_effect=AssertionError("legacy replay"))
    monkeypatch.setattr(conn, "_CosmosClientConnection__Get", legacy_get)
    monkeypatch.setattr(conn, "_UpdateSessionIfRequired", lambda *args, **kwargs: None)

    fallback_count = rust_compatibility_fallback_count()
    with pytest.raises(NotImplementedError, match="list_databases"):
        _run_sync_read_feed(
            conn,
            resource_type=http_constants.ResourceType.Database,
            options=options,
            **kwargs,
        )

    assert backend.prepared is None
    legacy_get.assert_not_called()
    assert rust_compatibility_fallback_count() == fallback_count


@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "aio"])
@pytest.mark.parametrize(
    "options, kwargs",
    [
        ({Constants.Kwargs.TIMEOUT: 0.5}, {}),
        ({}, {"connection_timeout": 1}),
        ({}, {"unknown_option": None}),
        ({"changeFeedState": {}}, {}),
        ({"initialHeaders": {"x-ms-version": "custom"}}, {}),
    ],
)
def test_list_databases_rejection_categories_are_explicit(monkeypatch, is_async, options, kwargs):
    """Each kind of unsupported listing call gets one clear, actionable error.

    Five categories: a sub-second timeout, a connection timeout, an unknown
    keyword, change feed state, and an API version override.

    All raise ``NotImplementedError`` naming ``list_databases``, and the
    message tells the customer what to do -- configure it when constructing
    the client -- and states plainly that the call will not be sent through
    the legacy Python path.

    That second half matters because database listing is the one feed that
    never falls back. Nothing is prepared and the legacy transport is unused.
    """
    conn = _new_async_connection() if is_async else _new_sync_connection()
    backend_type = _CapturingAsyncBackend if is_async else _CapturingSyncBackend
    conn._backend = backend_type(BackendResponse(status_code=200))
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})
    legacy_get = AsyncMock() if is_async else MagicMock()
    monkeypatch.setattr(conn, "_CosmosClientConnection__Get", legacy_get)

    with pytest.raises(NotImplementedError, match="list_databases") as error:
        if is_async:
            asyncio.run(_run_async_read_feed(
                conn, resource_type=http_constants.ResourceType.Database, options=options, **kwargs
            ))
        else:
            _run_sync_read_feed(
                conn, resource_type=http_constants.ResourceType.Database, options=options, **kwargs
            )

    assert "constructing CosmosClient" in str(error.value)
    assert "not be sent through legacy Python" in str(error.value)
    assert conn._backend.prepared is None
    legacy_get.assert_not_called()


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
@pytest.mark.parametrize("read_timeout", [0, 0.5, 30, False, "invalid"])
def test_public_list_databases_rejects_per_call_read_timeout(client_type, read_timeout):
    """``read_timeout`` cannot be set per call on the public ``list_databases``.

    The same rule as the internal feed, checked on the public surface of both
    the sync and async clients so they cannot drift apart. Every value is
    refused by name, including ``0`` and ``False``, which a truthiness check
    would let slip through. Nothing is dispatched.
    """
    client = object.__new__(client_type)
    client.client_connection = MagicMock()
    hook = MagicMock()
    with pytest.raises(TypeError, match="'read_timeout'"):
        client.list_databases(read_timeout=read_timeout, response_hook=hook)
    client.client_connection.ReadDatabases.assert_not_called()
    hook.assert_not_called()


def test_public_list_databases_accepts_unset_read_timeout(listing_client):
    """``read_timeout=None`` is accepted and leaves the other settings intact.

    ``None`` means "not supplied", so it is allowed. The page size still
    reaches the pager's options, and building the iterable sends nothing --
    the call is lazy either way.
    """
    client, _, backend, _ = listing_client
    result = client.list_databases(max_item_count=1, read_timeout=None)
    assert result.by_page().state.config.options["maxItemCount"] == 1
    backend.execute_pages.assert_not_called()


@pytest.mark.parametrize("fail_on_page", [1, 2])
def test_sync_list_databases_capability_error_never_replays_legacy(monkeypatch, fail_on_page):
    """A capability error part way through a listing is reported, never replayed on legacy.

    The backend fails either on the first page or on the second, after one
    database has already been handed to the caller.

    Either way the error surfaces and the legacy transport is never used. The
    mid-enumeration case is the dangerous one: replaying there would re-fetch
    databases the caller already has, and the continuation token confirms the
    second attempt really was a continuation rather than a fresh start.

    The fallback counter does not move, since nothing was rerouted.
    """
    class FailingBackend(_SequencedSyncBackend):

        def execute_pages(self, prepared, *, deadline=None):
            if len(self.prepared) + 1 == fail_on_page:
                self.prepared.append(prepared)
                raise PagePreflightError("unsupported database page")
            yield from super().execute_pages(prepared)

    conn = _new_sync_connection()
    conn._backend = FailingBackend()
    client = object.__new__(CosmosClient)
    client.client_connection = conn
    client._backend = conn._backend
    client._item_context = ItemClientContext(conn._backend, response_state=conn._response_state)
    monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})
    legacy_get = MagicMock(side_effect=AssertionError("legacy replay"))
    monkeypatch.setattr(conn, "_CosmosClientConnection__Get", legacy_get)
    fallback_count = rust_compatibility_fallback_count()
    items = iter(client.list_databases(max_item_count=1))
    if fail_on_page == 2:
        assert next(items) == {"id": "db-1"}
    with pytest.raises(PagePreflightError, match="unsupported database page"):
        next(items)
    assert len(conn._backend.prepared) == fail_on_page
    if fail_on_page == 2:
        assert conn._backend.prepared[-1].continuation == "next-db-page"
    legacy_get.assert_not_called()
    assert rust_compatibility_fallback_count() == fallback_count


@pytest.mark.parametrize("fail_on_page", [1, 2])
def test_async_list_databases_capability_error_never_replays_legacy(monkeypatch, fail_on_page):
    """The async listing behaves exactly like the sync one when a page is unsupported.

    Same scenario through the async client: fail on the first page or after
    one database has been delivered. The error surfaces, the legacy transport
    stays unused, the retry carries the continuation token, and the fallback
    counter does not move.

    Kept as a separate test because async paging is driven by different
    machinery, and a fallback could easily be reintroduced on one side only.
    """
    class FailingBackend(_SequencedAsyncBackend):

        async def execute_pages(self, prepared, *, deadline=None):
            if len(self.prepared) + 1 == fail_on_page:
                self.prepared.append(prepared)
                raise PagePreflightError("unsupported database page")
            async for page in super().execute_pages(prepared):
                yield page

    async def run():
        conn = _new_async_connection()
        conn._backend = FailingBackend()
        client = object.__new__(AsyncCosmosClient)
        client.client_connection = conn
        client._backend = conn._backend
        client._item_context = ItemClientContext(conn._backend, response_state=conn._response_state)
        monkeypatch.setattr(base_helpers, "GetHeaders", lambda *args, **kwargs: {})
        legacy_get = AsyncMock(side_effect=AssertionError("legacy replay"))
        monkeypatch.setattr(conn, "_CosmosClientConnection__Get", legacy_get)
        fallback_count = rust_compatibility_fallback_count()
        items = client.list_databases(max_item_count=1).__aiter__()
        if fail_on_page == 2:
            assert await items.__anext__() == {"id": "db-1"}
        with pytest.raises(PagePreflightError, match="unsupported database page"):
            await items.__anext__()
        assert len(conn._backend.prepared) == fail_on_page
        if fail_on_page == 2:
            assert conn._backend.prepared[-1].continuation == "next-db-page"
        legacy_get.assert_not_called()
        assert rust_compatibility_fallback_count() == fallback_count

    asyncio.run(run())


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
    assert legacy_partition_key_from_request(prepared) == '["tenant-a"]'
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
        assert legacy_partition_key_from_request(prepared) == '["tenant-a"]'
        assert prepared.query is None

    asyncio.run(_run())


def test_sync_read_all_backend_page_empty_container(monkeypatch):
    """Sync read_all_items on an empty (or fully-drained) container. Cross-partition
    read_all is routed through the Rust query-page path (``SELECT * FROM root r``) and
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


def test_sync_driver_unsupported_query_never_replays():
    """Query planning is execution, not a static preflight capability check."""

    class _UnsupportedBackend(CosmosBackend):
        def execute(self, prepared, *, deadline=None):
            raise AssertionError("single-response execution is not expected")

        def execute_pages(self, prepared, *, deadline=None):
            del prepared
            raise UnsupportedQueryError("unsupported query plan")
            yield  # pragma: no cover

    prepared = PreparedPageRequest(
        op=OP_QUERY_ITEMS,
        container_link="dbs/db/colls/c",
        query="SELECT VALUE COUNT(1) FROM c",
    )

    fallback_count_before = rust_compatibility_fallback_count()
    legacy = MagicMock(side_effect=AssertionError("legacy replay"))
    with pytest.raises(UnsupportedQueryError, match="unsupported query plan"):
        _UnsupportedBackend().run_page_operation(
            build_request=lambda: prepared,
            routing=OperationRouting(OP_QUERY_ITEMS),
            legacy_call=legacy,
            process_response=lambda _page: "rust",
        )
    legacy.assert_not_called()
    assert rust_compatibility_fallback_count() == fallback_count_before


def test_async_driver_unsupported_query_never_replays():
    """Async execution failures cannot switch transports."""

    class _UnsupportedBackend(AsyncCosmosBackend):
        async def execute(self, prepared, *, deadline=None):
            raise AssertionError("single-response execution is not expected")

        async def execute_pages(self, prepared, *, deadline=None):
            del prepared
            raise UnsupportedQueryError("unsupported query plan")
            yield  # pragma: no cover

    async def _run():
        prepared = PreparedPageRequest(
            op=OP_QUERY_ITEMS,
            container_link="dbs/db/colls/c",
            query="SELECT * FROM c ORDER BY c.ts",
        )

        def _prepare_request():
            return prepared

        legacy = AsyncMock(side_effect=AssertionError("legacy replay"))

        fallback_count_before = rust_compatibility_fallback_count()
        with pytest.raises(
            UnsupportedQueryError, match="unsupported query plan"
        ):
            await _UnsupportedBackend().run_page_operation(
                build_request=_prepare_request,
                routing=OperationRouting(OP_QUERY_ITEMS),
                legacy_call=legacy,
                process_response=lambda _page: "rust",
            )
        legacy.assert_not_called()
        assert rust_compatibility_fallback_count() == fallback_count_before

    asyncio.run(_run())


def test_sync_unrelated_not_implemented_error_is_not_replayed():
    """Unexpected backend errors propagate instead of triggering a second request."""
    class _BrokenBackend(CosmosBackend):
        def execute(self, prepared, *, deadline=None):
            raise AssertionError("single-response execution is not expected")

        def execute_pages(self, prepared, *, deadline=None):
            del prepared
            raise NotImplementedError("unexpected parser failure")
            yield  # pragma: no cover

    prepared = PreparedPageRequest(
        op=OP_QUERY_ITEMS,
        container_link="dbs/db/colls/c",
        query="SELECT * FROM c",
    )
    fallback_count_before = rust_compatibility_fallback_count()

    with pytest.raises(NotImplementedError, match="unexpected parser failure"):
        _BrokenBackend().run_page_operation(
            build_request=lambda: prepared,
            routing=OperationRouting(OP_QUERY_ITEMS, True),
            legacy_call=lambda: "legacy",
            process_response=lambda _page: "rust",
        )

    assert rust_compatibility_fallback_count() == fallback_count_before


def test_async_unrelated_not_implemented_error_is_not_replayed():
    """Async unexpected backend errors also propagate without fallback."""
    class _BrokenBackend(AsyncCosmosBackend):
        async def execute(self, prepared, *, deadline=None):
            raise AssertionError("single-response execution is not expected")

        async def execute_pages(self, prepared, *, deadline=None):
            del prepared
            raise NotImplementedError("unexpected async parser failure")
            yield  # pragma: no cover

    async def _run():
        prepared = PreparedPageRequest(
            op=OP_QUERY_ITEMS,
            container_link="dbs/db/colls/c",
            query="SELECT * FROM c",
        )
        def _prepare_request():
            return prepared

        async def _run_legacy():
            return "legacy"

        fallback_count_before = rust_compatibility_fallback_count()

        with pytest.raises(NotImplementedError, match="unexpected async parser failure"):
            await _BrokenBackend().run_page_operation(
                build_request=_prepare_request,
                routing=OperationRouting(OP_QUERY_ITEMS, True),
                legacy_call=_run_legacy,
                process_response=lambda _page: "rust",
            )

        assert rust_compatibility_fallback_count() == fallback_count_before

    asyncio.run(_run())


def test_sync_empty_page_iterator_is_not_replayed():
    """A missing Rust page raises one public error and does not repeat the call."""
    class _EmptyBackend(CosmosBackend):
        def execute(self, prepared, *, deadline=None):
            raise AssertionError("single-response execution is not expected")

        def execute_pages(self, prepared, *, deadline=None):
            del prepared
            return iter(())

    legacy_calls = []
    with pytest.raises(BindingProtocolError, match="returned no page"):
        _EmptyBackend().run_page_operation(
            build_request=lambda: PreparedPageRequest(
                op=OP_QUERY_ITEMS, container_link="dbs/db/colls/c"
            ),
            routing=OperationRouting(OP_QUERY_ITEMS, True),
            legacy_call=lambda: legacy_calls.append(1),
            process_response=lambda _page: "rust",
        )
    assert legacy_calls == []


def test_async_empty_page_iterator_is_not_replayed():
    """A missing async Rust page raises one public error and is not repeated."""
    class _EmptyBackend(AsyncCosmosBackend):
        async def execute(self, prepared, *, deadline=None):
            raise AssertionError("single-response execution is not expected")

        async def execute_pages(self, prepared, *, deadline=None):
            del prepared
            if False:
                yield BackendPage(status_code=200)

    async def _run():
        legacy_calls = []

        def _prepare_request():
            return PreparedPageRequest(op=OP_QUERY_ITEMS, container_link="dbs/db/colls/c")

        async def _run_legacy():
            legacy_calls.append(1)

        with pytest.raises(BindingProtocolError, match="returned no page"):
            await _EmptyBackend().run_page_operation(
                build_request=_prepare_request,
                routing=OperationRouting(OP_QUERY_ITEMS, True),
                legacy_call=_run_legacy,
                process_response=lambda _page: "rust",
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
    update on the async fall-back path, keeping sync, async, and both Rust paths
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
    assert backend.prepared.partition_key.kind == "cross_partition"
    assert backend.prepared.query == "SELECT * FROM root r WHERE r.id = @id"
    assert backend.prepared.parameters == ({"name": "@id", "value": "db-1"},)
    assert backend.prepared.max_item_count == 1
    assert backend.prepared.continuation == "start"
    assert wire_headers(backend.prepared)["x-ms-cosmos-throughput-bucket"] == "7"
    assert all(wire_headers(backend.prepared).get(key.lower()) == str(value) for key, value in ({"x-test-header": "yes"}).items())


def test_query_databases_binding_request_carries_the_query_body():
    """The Rust request contains the complete database query body."""
    binding_request = _sync_binding_request_from_page(
        PreparedPageRequest(
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
    assert wire_headers(binding_request)["x-ms-max-item-count"] == "2"
    assert wire_headers(binding_request)["x-ms-continuation"] == "token"


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
@pytest.mark.asyncio
async def test_query_databases_backend_rejects_unrepresentable_options(listing_client, options, kwargs):
    """Neither client may send an unsupported database query through legacy."""
    _, conn, backend, is_async = listing_client
    fallback_before = rust_compatibility_fallback_count()
    with pytest.raises(NotImplementedError, match="query_databases.*legacy Python"):
        if is_async:
            await _run_async_database_query_feed(
                conn, query={"query": "SELECT * FROM root r"}, options=options, **kwargs
            )
        else:
            _run_sync_database_query_feed(
                conn, query={"query": "SELECT * FROM root r"}, options=options, **kwargs
            )
    assert backend.prepared is None
    backend.execute_pages.assert_not_called()
    conn._CosmosClientConnection__Post.assert_not_called()
    assert rust_compatibility_fallback_count() == fallback_before


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
        assert backend.prepared.partition_key.kind == "cross_partition"
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
