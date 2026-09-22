"""Unit coverage for listing the containers in a database, on both engines (no network).

Listing is a feed: the service answers one page at a time and hands back a
continuation token to fetch the next. That shape drives almost everything here.

Nothing should happen until the caller actually asks for items. Building the
pager makes no request, so a customer who creates one and never iterates it
pays nothing.

The pages must join up. A token from one page has to resume exactly where it
left off, including on a brand-new pager, which is how customers page across
separate calls or processes.

Empty is not the same as finished. A page with no containers in it is still a
successful page, and the feed has to keep going rather than stop early.

The deadline applies to fetching one page, not to the whole walk. A customer
iterating slowly must not have the feed expire underneath them.

Each of the four setups -- sync and async, Rust and legacy -- is a separate code
path, so every test runs on all four.

All fakes, no Cosmos account.
"""
from common.typed_requests import wire_headers, settings_options, legacy_settings
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import inspect
import json
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import exceptions
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos._backend.contracts import BackendPage
from azure.cosmos._backend.errors import PagePreflightError
from azure.cosmos._backend.operations import OP_LIST_CONTAINERS
from azure.cosmos._query_rust_routing import can_use_rust_backend_for_query_containers_page
from azure.cosmos.http_constants import ResourceType
from .test_container_backend_unit import (
    _CapturingPagedBackend, _CapturingAsyncPagedBackend,
    _new_sync_connection, _new_async_connection,
)


def _page(ids, continuation=None, status=200):
    """Build one fake feed page holding the named containers.

    The containers sit under the ``DocumentCollections`` key, which is what the
    service really uses for a container feed. A database feed uses a different
    key, and reading the wrong one yields an empty list rather than an error --
    the worst kind of wrong, because the customer sees "no containers" instead
    of a failure.

    The activity id is set from the container names so a test can tell the pages
    apart in the headers a hook receives.
    """
    headers = CaseInsensitiveDict({"x-ms-request-charge": "2", "x-ms-activity-id": ",".join(ids) or "empty"})
    if continuation:
        headers["x-ms-continuation"] = continuation
    return BackendPage(
        status_code=status, continuation=continuation, headers=headers,
        body=json.dumps({"DocumentCollections": [{"id": value} for value in ids]}).encode(),
    )


@pytest.fixture(params=["sync-rust", "async-rust", "sync-legacy", "async-legacy"])
def listing_case(request):
    """Build a container listing across all four combinations of client and engine.

    By default the feed is two pages: one container with a token, then one more
    without. Tests can replace either page to stage an empty page or a failure.

    Every request is recorded, which is how the tests prove that building a
    pager sends nothing and that a failure is not quietly tried a second time.
    A failure can also be armed so the next fetch raises instead of answering.

    At the end of every Rust run the fixture asserts the legacy transport was
    never called. That is the guard against a silent fallback: without it, a
    test could pass while the work was actually done by the other engine.
    """
    is_async = request.param.startswith("async")
    rust = request.param.endswith("rust")
    conn = _new_async_connection() if is_async else _new_sync_connection()
    case = SimpleNamespace(
        connection=conn, is_async=is_async, rust=rust, requests=[], failure=None,
        responses={"": _page(["c1"], "next"), "next": _page(["c2"])},
    )

    def response(token, prepared):
        case.requests.append(prepared)
        if case.failure is not None:
            raise case.failure
        return case.responses[token or ""]

    class Backend(_CapturingPagedBackend):
        name = "rust"

        def execute_pages(self, prepared, *, deadline=None):
            yield response(prepared.continuation, prepared)

    class AsyncBackend(_CapturingAsyncPagedBackend):
        name = "rust"

        async def execute_pages(self, prepared, *, deadline=None):
            yield response(prepared.continuation, prepared)

    if rust:
        conn._backend = AsyncBackend(b"") if is_async else Backend(b"")

    def legacy_get(_path, _request, headers, **kwargs):
        page = response(headers.get("x-ms-continuation"), dict(headers))
        if page.status_code >= 400:
            raise exceptions.CosmosHttpResponseError(status_code=page.status_code, headers=page.headers)
        return json.loads(page.body), page.headers.copy()

    case.legacy_get = (AsyncMock if is_async else MagicMock)(side_effect=legacy_get)
    conn._CosmosClientConnection__Get = case.legacy_get
    case.database = (AsyncDatabaseProxy if is_async else DatabaseProxy)(conn, "db1")
    yield case
    if rust:
        case.legacy_get.assert_not_called()


def _run(case, sync_call, async_call):
    """Run whichever of the two versions matches the client under test."""
    return asyncio.run(async_call()) if case.is_async else sync_call()


def _drain(case, pager):
    """Walk the whole feed to the end and return every container it yielded."""
    async def collect():
        return [item async for item in pager]
    return _run(case, lambda: list(pager), collect)


def test_lazy_pages_and_continuation_resume(listing_case):
    """No request until the caller asks, one request per page, and a token resumes on
    a fresh pager.

    Creating the pager sends nothing and runs no hook, and on the async client it
    is not even something to wait on -- the work starts when iteration does. A
    customer who builds a pager and abandons it pays nothing.

    Taking the first page makes exactly one request and hands back a token.
    That token is then given to a *brand-new* pager, which picks up at the second
    container rather than starting over. This is what lets customers page across
    separate calls, or hand a token to another process.

    Two requests in total, so resuming did not silently refetch the first page.
    On the Rust path each request is a container listing scoped to this database,
    carries the caller's page size, and the second carries the token.
    """
    case = listing_case
    hooks = []
    pager = case.database.list_containers(max_item_count=1, response_hook=hooks.append)
    assert not inspect.isawaitable(pager)
    assert case.requests == [] and hooks == []

    def sync_call():
        pages = pager.by_page()
        first = list(next(pages))
        assert len(case.requests) == 1 and len(hooks) == 1
        assert pages.continuation_token == "next"
        resumed = case.database.list_containers(max_item_count=1).by_page(
            continuation_token=pages.continuation_token
        )
        return first, [item for page in resumed for item in page]

    async def async_call():
        pages = pager.by_page()
        first = [item async for item in await pages.__anext__()]
        assert len(case.requests) == 1 and len(hooks) == 1
        assert pages.continuation_token == "next"
        resumed = case.database.list_containers(max_item_count=1).by_page(
            continuation_token=pages.continuation_token
        )
        rest = [item async for page in resumed async for item in page]
        return first, rest

    first, rest = _run(case, sync_call, async_call)
    assert first == [{"id": "c1"}] and rest == [{"id": "c2"}]
    assert len(case.requests) == 2
    if case.rust:
        assert all(prepared.op == OP_LIST_CONTAINERS for prepared in case.requests)
        assert all(prepared.container_link == "dbs/db1" for prepared in case.requests)
        assert all(prepared.max_item_count == 1 for prepared in case.requests)
        assert case.requests[1].continuation == "next"


@pytest.mark.parametrize("empty_first", [False, True])
def test_falsey_hook_receives_each_page_as_an_isolated_snapshot(listing_case, empty_first):
    """The hook runs once per page with that page's own headers, and cannot disturb
    the client.

    The hook reports itself as false when tested as a boolean, and still runs,
    because being callable is what matters.

    It fires twice, once per page, and never before iteration begins. Each call
    gets the headers belonging to *that* page -- checked through the activity id
    -- rather than a single set overwritten as the walk goes on, which is what a
    customer needs to account for charges page by page.

    The headers are its own copy: it writes a marker and nothing reaches the
    client's record of the last response.

    The run with an empty first page proves an empty page still reports itself.
    """
    case = listing_case
    if empty_first:
        case.responses[""] = _page([], "next")
    snapshots = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers):
            assert headers is not case.connection.last_response_headers
            snapshots.append(headers)
            headers["x-hook-mutation"] = "local"

    pager = case.database.list_containers(response_hook=Hook())
    assert snapshots == []
    items = _drain(case, pager)
    assert [item["id"] for item in items] == (["c2"] if empty_first else ["c1", "c2"])
    assert len(snapshots) == 2
    assert snapshots[0]["x-ms-activity-id"] == ("empty" if empty_first else "c1")
    assert snapshots[1]["x-ms-activity-id"] == "c2"
    assert "x-hook-mutation" not in case.connection.last_response_headers


def test_empty_database_still_reports_its_successful_page(listing_case):
    """A database with no containers yields nothing but still reports one successful
    page.

    The hook fires once. A customer tracking request charges needs to see the
    request that was actually made and paid for, even though it returned nothing.
    """
    case = listing_case
    case.responses[""] = _page([])
    hook = MagicMock()
    assert _drain(case, case.database.list_containers(response_hook=hook)) == []
    hook.assert_called_once()


@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics", "availability_strategy"])
@pytest.mark.parametrize("value", [None, False, True])
def test_obsolete_options_fail_before_paging(listing_case, option, value):
    """Retired options are refused as the pager is built, not on the first fetch.

    Session token, query metrics, and availability strategy each raise
    ``TypeError`` naming the option, whatever the value. Failing straight away
    matters for a feed: if the error waited until iteration, a customer could
    build a pager, pass it elsewhere, and only discover the mistake far from the
    call that caused it.
    """
    case = listing_case
    with pytest.raises(TypeError, match=option):
        case.database.list_containers(**{option: value})
    assert case.requests == []


@pytest.mark.parametrize("args", [(1,), (1, False)])
def test_options_are_keyword_only(listing_case, args):
    """Listing takes no positional arguments; every option must be named.

    One and two positional values are both refused. Older code passed page size
    and a flag by position, and silently accepting them now would land a
    customer's values in whichever options happen to sit in those slots today.
    """
    with pytest.raises(TypeError):
        listing_case.database.list_containers(*args)
    assert listing_case.requests == []


@pytest.mark.parametrize("value", [False, 0, 1])
def test_socket_timeout_is_rejected(listing_case, value):
    """The socket-level ``read_timeout`` is not accepted here, including when false or
    zero, which are still the customer asking for it. The error names the option
    so it is clear what to remove, and it is raised before any request.
    """
    with pytest.raises(TypeError, match="read_timeout"):
        listing_case.database.list_containers(read_timeout=value)
    assert listing_case.requests == []


@pytest.mark.parametrize("timeout", [None, 1, 1.5, 10])
def test_supported_timeout_and_application_headers(listing_case, timeout):
    """A supported deadline and the customer's own header reach every page request.

    The header must ride on both requests, not just the first, or a customer's
    tracing breaks partway through a long walk.

    With no timeout, no deadline is invented. With one, each page gets a
    remaining allowance that is positive and no larger than what was asked for:
    a page is never given more time than the customer allowed, and is never
    started with none left.
    """
    case = listing_case
    pager = case.database.list_containers(
        timeout=timeout, read_timeout=None, initial_headers={"x-company-trace": "listing"}
    )
    assert len(_drain(case, pager)) == 2
    if case.rust:
        for prepared in case.requests:
            assert wire_headers(prepared)["x-company-trace"] == "listing"
            budget = settings_options(prepared).get("timeout_seconds")
            if timeout is None:
                assert budget is None
            else:
                assert 0 < budget <= timeout


@pytest.mark.parametrize("kwargs", [
    {"timeout": 0}, {"timeout": 0.5}, {"timeout": False}, {"timeout": True},
    {"timeout": -1}, {"timeout": float("nan")}, {"timeout": float("inf")},
    {"timeout": "10"}, {"timeout": 2**64 - 1}, {"timeout": 10**400},
    {"initial_headers": {"User-Agent": "override"}},
    {"initial_headers": {"x-ms-version": "override"}},
    {"raw_request_hook": lambda request: None}, {"raw_response_hook": lambda response: None},
    {"connection_timeout": 10}, {"unknown_option": None},
    {"request_options": {"availabilityStrategy": False}},
    {"request_options": {"read_timeout": 2}},
])
def test_unsupported_rust_options_do_not_dispatch(listing_case, kwargs):
    """Options the Rust path cannot honor never produce a request, and never move the
    feed to the legacy transport.

    Eighteen calls are covered: ten unusable deadlines, two driver-owned headers,
    both raw hooks, a connect timeout, an unknown keyword, and two raw
    request-options dictionaries.

    Building the pager still sends nothing. The failure comes when the customer
    starts iterating, and no request is made then either -- so the refusal costs
    nothing and the hook never runs. The fixture's own check confirms the legacy
    transport was not used as a silent substitute.

    Skipped on the legacy setups, where these options are genuinely supported.
    """
    case = listing_case
    if not case.rust:
        pytest.skip("Rust-specific option rejection")
    hook = MagicMock()
    pager = case.database.list_containers(response_hook=hook, **kwargs)
    assert case.requests == []
    with pytest.raises((NotImplementedError, TypeError, exceptions.CosmosClientTimeoutError)):
        _drain(case, pager)
    assert case.requests == []
    hook.assert_not_called()


@pytest.mark.parametrize("error", [
    ValueError("hook failed"), PagePreflightError("hook failed"),
    exceptions.CosmosResourceNotFoundError(status_code=404),
    exceptions.CosmosHttpResponseError(status_code=429),
    exceptions.CosmosHttpResponseError(status_code=500),
])
def test_hook_failure_does_not_fetch_again_or_fall_back(listing_case, error):
    """An error from the customer's hook stops the walk without refetching the page.

    Five errors are raised from the hook, including two that the SDK would
    normally read as service replies -- a not-found and a throttling response --
    and one that normally means "this engine cannot serve this page". Any of
    those, if caught too broadly, would be mistaken for something the SDK should
    react to: retrying the page, or restarting the feed on the other engine.

    Instead the exact exception reaches the caller after exactly one request,
    with the hook having run once. Refetching would charge the customer twice
    for a page they already received.
    """
    case = listing_case
    hook = MagicMock(side_effect=error)
    with pytest.raises(type(error)) as raised:
        _drain(case, case.database.list_containers(response_hook=hook))
    assert raised.value is error
    assert len(case.requests) == 1
    hook.assert_called_once()


@pytest.mark.parametrize("status", [403, 404, 429, 500])
def test_error_page_does_not_invoke_success_hook(listing_case, status):
    """A failed page keeps its status and does not run the success hook.

    Four statuses are covered. Each reaches the caller with its status code
    intact, and the hook stays silent, because nothing succeeded -- a hook that
    fired here would report a charge for a page the customer never got.

    Throttling is allowed more than one request, since that is the one status the
    client is expected to retry; the others must produce exactly one.
    """
    case = listing_case
    case.responses[""] = _page([], status=status)
    hook = MagicMock()
    with pytest.raises(exceptions.CosmosHttpResponseError) as raised:
        _drain(case, case.database.list_containers(response_hook=hook))
    assert raised.value.status_code == status
    hook.assert_not_called()
    assert len(case.requests) >= 1
    if status != 429:
        assert len(case.requests) == 1


@pytest.mark.parametrize("error", [
    PagePreflightError("unsupported page"), ValueError("binding failure"), asyncio.CancelledError(),
])
def test_binding_failures_are_not_replayed(listing_case, error):
    """A failure inside the Rust engine, including cancellation, ends the walk after
    one request.

    All three reach the caller unchanged: a page the engine says it cannot
    serve, an ordinary error, and cancellation. The first is the tempting one --
    it sounds like an invitation to retry on legacy -- but restarting the feed
    there would charge the customer for the same page twice and could interleave
    results from two different walks.

    Cancellation must also pass through untouched, or it stops unwinding and the
    caller's request to stop is ignored.

    Skipped on the legacy setups, which have no such engine.
    """
    case = listing_case
    if not case.rust:
        pytest.skip("Rust-specific binding failure")
    case.failure = error
    with pytest.raises(type(error)) as raised:
        _drain(case, case.database.list_containers())
    assert raised.value is error
    assert len(case.requests) == 1


def test_timeout_restarts_between_public_page_fetches(listing_case, monkeypatch):
    """The deadline covers fetching one page, not the whole walk.

    The clock is moved forward by ten seconds before the first page and ten more
    before the second, far past the one-second timeout, yet both pages arrive.

    This is deliberate. Customers iterate feeds slowly -- processing each page,
    waiting on something else, looping in a job. If the deadline covered the
    whole walk, a feed would expire mid-iteration for reasons that have nothing
    to do with how the service responded. The timeout limits how long any single
    page may take.
    """
    case = listing_case
    clock = [100.0]
    monkeypatch.setattr(time, "time", lambda: clock[0])
    pager = case.database.list_containers(timeout=1).by_page()
    clock[0] += 10

    def sync_call():
        first = list(next(pager))
        clock[0] += 10
        second = list(next(pager))
        return first + second

    async def async_call():
        first = [item async for item in await pager.__anext__()]
        clock[0] += 10
        second = [item async for item in await pager.__anext__()]
        return first + second

    assert len(_run(case, sync_call, async_call)) == 2


def test_empty_service_page_does_not_reset_current_page_budget(listing_case, monkeypatch):
    """Time spent skipping past empty pages counts against the page the customer is
    waiting for.

    The previous test showed the deadline restarts between pages the *customer*
    asks for. This is the other half: when the service answers with an empty page
    carrying a token, the SDK fetches again on its own to find something to
    return. That inner loop must not keep resetting the allowance.

    Here the hook advances the clock by two seconds against a one-second
    deadline, and the walk gives up with a timeout after a single request. If the
    allowance restarted on every empty page, a run of them could keep a customer
    waiting indefinitely on a call they had given one second.

    Skipped on legacy, where the fake transport bypasses these checks.
    """
    case = listing_case
    if not case.rust:
        pytest.skip("Legacy transport timeout checks are bypassed by the fake HTTP response")
    clock = [100.0]
    monkeypatch.setattr(time, "time", lambda: clock[0])
    case.responses[""] = _page([], "next")

    def hook(headers):
        clock[0] += 2

    with pytest.raises(exceptions.CosmosClientTimeoutError):
        _drain(case, case.database.list_containers(timeout=1, response_hook=hook))
    assert len(case.requests) == 1


def test_query_container_timeout_policy_matches_listing():
    """A container query with an ordinary deadline is allowed on the Rust path, the
    same as a listing.

    The two feeds are built by separate code, so it would be easy for one to
    start turning away a deadline the other accepts. A customer switching from
    listing to querying would then be moved to a different engine by a setting
    that has nothing to do with the difference between the two calls.
    """
    assert can_use_rust_backend_for_query_containers_page(
        path="/dbs/db1/colls/", query_payload={"query": "SELECT * FROM c"},
        options={"timeout": 10}, kwargs={"timeout": 10},
        is_query_plan=False, resource_type=ResourceType.Collection,
    )
