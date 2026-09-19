"""Unit coverage for querying the containers in a database, on both engines (no network).

Querying containers is the same feed machinery as listing them, with a query
attached, and it reuses that file's setup. What is specific here is the query
itself.

A query can be given three ways -- as plain text, as a dictionary, or as text
with separate parameters -- and all three have to produce the same request. A
parameter that failed to reach the service would silently change which
containers came back.

The customer's query must also come back unchanged. Customers reuse a query
dictionary across calls, so building a request from it must not edit it.

Everything the listing tests establish about paging, deadlines, hooks, and never
retrying still applies, and is checked again here because this call builds its
requests through separate code.

All fakes, no Cosmos account.
"""
from common.typed_requests import wire_headers, settings_options, legacy_settings
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import copy
import inspect
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import exceptions
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos._backend.errors import PagePreflightError
from azure.cosmos._backend.operations import OP_LIST_CONTAINERS, OP_QUERY_CONTAINERS
from .test_list_containers_backend_unit import listing_case, _page, _drain, _run


SQL = "SELECT * FROM c WHERE c.id != @excluded"
PARAMETERS = [{"name": "@excluded", "value": "missing"}]


@pytest.fixture
def query_case(listing_case):
    """Extend the listing setup so the legacy path answers queries too.

    Queries go out through a different legacy call than listings, so that call is
    added here and made to answer from the same staged pages. Each query is
    copied as it passes, letting a test inspect exactly what legacy was asked
    without the record changing afterwards.

    At the end of every Rust run the fixture asserts the legacy query call was
    never used, which is the guard against a silent fallback.
    """
    case = listing_case
    case.queries = []

    def post(path, request, query, headers, **kwargs):
        case.queries.append(copy.deepcopy(query))
        return case.legacy_get.side_effect(path, request, headers, **kwargs)

    case.legacy_post = (AsyncMock if case.is_async else MagicMock)(side_effect=post)
    case.connection._CosmosClientConnection__Post = case.legacy_post
    yield case
    if case.rust:
        case.legacy_post.assert_not_called()


def test_sync_async_parameter_contracts_match():
    """The sync and async versions take exactly the same arguments.

    They are written as separate code, so one can easily gain an option the
    other lacks. A customer moving code from the sync client to the async one
    would then hit a failure that has nothing to do with the change they made.
    """
    sync = inspect.signature(DatabaseProxy.query_containers)
    asynchronous = inspect.signature(AsyncDatabaseProxy.query_containers)
    assert sync.parameters == asynchronous.parameters


@pytest.mark.parametrize("form", ["string", "dictionary", "parameters"])
def test_query_payload_and_lazy_resumable_pages(query_case, form):
    """All three ways of writing a query produce the same request, and the feed pages
    and resumes the same way.

    The query is given as plain text, as a dictionary holding the text and its
    parameters, and as text with parameters passed separately. Every form must
    send the same query text, and the two parameterized forms must send the same
    parameters. If a parameter were dropped, the query would still run and
    return a different set of containers, with nothing to indicate why.

    The plain-text form sends no parameters at all rather than something empty
    standing in for them.

    As with listing, building the pager sends nothing, taking the first page
    makes one request, and the token resumes on a brand-new pager -- two
    requests in total, so resuming did not refetch.

    Afterwards the customer's query and parameters are unchanged, so a
    dictionary reused for a second call is still intact.
    """
    case = query_case
    query = {"query": SQL, "parameters": PARAMETERS} if form == "dictionary" else SQL
    kwargs = {"parameters": PARAMETERS} if form == "parameters" else {}
    original = copy.deepcopy((query, kwargs))
    hooks = []
    pager = case.database.query_containers(query, max_item_count=1, response_hook=hooks.append, **kwargs)
    assert not inspect.isawaitable(pager)
    assert case.requests == [] and hooks == []

    def sync_call():
        pages = pager.by_page()
        first = list(next(pages))
        assert len(first) == 1 and len(case.requests) == 1 and len(hooks) == 1
        assert pages.continuation_token == "next"
        resumed = case.database.query_containers(query, max_item_count=1, **kwargs).by_page(
            continuation_token=pages.continuation_token
        )
        return first + [item for page in resumed for item in page]

    async def async_call():
        pages = pager.by_page()
        first = [item async for item in await pages.__anext__()]
        assert len(first) == 1 and len(case.requests) == 1 and len(hooks) == 1
        assert pages.continuation_token == "next"
        resumed = case.database.query_containers(query, max_item_count=1, **kwargs).by_page(
            continuation_token=pages.continuation_token
        )
        return first + [item async for page in resumed async for item in page]

    assert _run(case, sync_call, async_call) == [{"id": "c1"}, {"id": "c2"}]
    assert (query, kwargs) == original
    assert len(case.requests) == 2
    expected_parameters = PARAMETERS if form != "string" else []
    if case.rust:
        for prepared in case.requests:
            assert prepared.op == OP_QUERY_CONTAINERS
            assert prepared.container_link == "dbs/db1"
            assert prepared.query == SQL
            assert prepared.parameters == tuple(expected_parameters)
            assert prepared.max_item_count == 1
        assert case.requests[1].continuation == "next"
    else:
        assert len(case.queries) == 2
        assert all(query["query"] == SQL for query in case.queries)
        assert all(query.get("parameters", []) == expected_parameters for query in case.queries)


@pytest.mark.parametrize("empty", ["first", "all", "neither"])
def test_page_hooks_are_lazy_independent_and_honor_false_callables(query_case, empty):
    """The hook runs once per page with that page's own headers, including for pages
    that matched nothing.

    Three shapes are covered: a first page that matched nothing but has more to
    come, a single page that matched nothing and ends the feed, and two pages
    that both matched.

    Empty pages are ordinary for a query -- a filter can exclude everything in a
    page while later pages still match -- so the walk continues and each page is
    still reported. A customer tracking charges is billed for those requests and
    needs to see them.

    The hook reports itself as false and still runs. Its headers are its own
    copy: it writes a marker and nothing reaches the client's record.
    """
    case = query_case
    if empty != "neither":
        case.responses[""] = _page([], "next" if empty == "first" else None)
    snapshots = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers):
            assert headers is not case.connection.last_response_headers
            snapshots.append(headers)
            headers["x-local"] = "mutation"

    pager = case.database.query_containers(SQL, response_hook=Hook())
    assert snapshots == [] and case.requests == []
    rows = _drain(case, pager)
    assert rows == ([] if empty == "all" else [{"id": "c2"}] if empty == "first"
                    else [{"id": "c1"}, {"id": "c2"}])
    assert len(snapshots) == (1 if empty == "all" else 2)
    assert snapshots[0]["x-ms-activity-id"] == ("c1" if empty == "neither" else "empty")
    assert "x-local" not in case.connection.last_response_headers


def test_terminal_empty_service_page_still_invokes_hook(query_case):
    """A final page that matched nothing is still reported.

    The feed is staged as three pages, the last of which is empty and ends the
    walk. All the containers from the first two arrive, and the hook fires three
    times -- once per request, the last for the empty page.

    That last request was made and paid for. Skipping the hook because there was
    nothing to yield would leave a customer's charge accounting short.
    """
    case = query_case
    case.responses["next"] = _page(["c2"], "last")
    case.responses["last"] = _page([])
    hooks = []
    rows = _drain(case, case.database.query_containers(SQL, response_hook=hooks.append))
    assert rows == [{"id": "c1"}, {"id": "c2"}]
    assert len(hooks) == len(case.requests) == 3
    assert hooks[-1]["x-ms-activity-id"] == "empty"


@pytest.mark.parametrize("option", [
    "session_token", "populate_query_metrics", "availability_strategy", "enable_cross_partition_query",
])
@pytest.mark.parametrize("value", [None, False, True])
def test_retired_options_rejected_before_requests(query_case, option, value):
    """Retired options are refused as the pager is built, whatever their value.

    Four are covered, including the cross-partition flag, which customers had to
    set explicitly in older versions and is now always implied. Each raises
    ``TypeError`` naming the option, before any request, so the mistake surfaces
    at the call that caused it rather than wherever the pager is later
    iterated.
    """
    with pytest.raises(TypeError, match=option):
        query_case.database.query_containers(SQL, **{option: value})
    assert query_case.requests == []


@pytest.mark.parametrize("args", [(), (SQL, []), (SQL, [], 1), (SQL, [], 1, False)])
def test_query_required_and_only_positional_argument(query_case, args):
    """The query is required, and it is the only argument that may be positional.

    No arguments at all is refused, and so are one, two, and three extra
    positional values. Older code passed parameters, page size, and a flag by
    position; accepting them now would land a customer's values in whichever
    options happen to sit in those slots today.
    """
    with pytest.raises(TypeError):
        query_case.database.query_containers(*args)
    assert query_case.requests == []


@pytest.mark.parametrize("value", [False, 0, 1])
def test_read_timeout_rejected(query_case, value):
    """The socket-level ``read_timeout`` is not accepted here, including when false or
    zero, which are still the customer asking for it. The error names the option,
    and no request is made.
    """
    with pytest.raises(TypeError, match="read_timeout"):
        query_case.database.query_containers(SQL, read_timeout=value)
    assert query_case.requests == []


@pytest.mark.parametrize("query", [SQL, None])
@pytest.mark.parametrize("timeout", [None, 1, 1.5, 10])
def test_supported_timeout_headers_and_explicit_none_query(query_case, query, timeout):
    """A deadline and the customer's header reach every page, and no query at all
    becomes a plain listing.

    Passing ``None`` as the query is not an error and not an empty query. It
    means "no filter", and the request that goes out is a container listing
    rather than a query -- the same thing the customer would get from the listing
    call. Sending an empty query instead would be rejected by the service.

    In both cases the customer's header rides on every page request, and the
    deadline gives each page an allowance that is positive and no larger than
    what was asked for. With no deadline, none is invented.
    """
    case = query_case
    hooks = []
    rows = _drain(case, case.database.query_containers(
        query, timeout=timeout, read_timeout=None,
        initial_headers={"x-company-trace": "query-containers"}, response_hook=hooks.append,
    ))
    assert rows == [{"id": "c1"}, {"id": "c2"}]
    assert len(hooks) == 2
    if case.rust:
        for prepared in case.requests:
            assert prepared.op == (OP_LIST_CONTAINERS if query is None else OP_QUERY_CONTAINERS)
            assert wire_headers(prepared)["x-company-trace"] == "query-containers"
            budget = settings_options(prepared).get("timeout_seconds")
            assert budget is None if timeout is None else 0 < budget <= timeout


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
def test_unsupported_rust_options_never_fall_back(query_case, kwargs):
    """Options the Rust path cannot honor never produce a request, and never move the
    query to the legacy transport.

    Eighteen calls are covered: ten unusable deadlines, two driver-owned headers,
    both raw hooks, a connect timeout, an unknown keyword, and two raw
    request-options dictionaries.

    The failure arrives when the customer starts iterating, and no request is
    made then either, so the refusal costs nothing and the hook never runs. The
    fixture's own check confirms the legacy query call was not used as a silent
    substitute.

    Skipped on the legacy setups, where these options are genuinely supported.
    """
    case = query_case
    if not case.rust:
        pytest.skip("Rust-specific option rejection")
    hook = MagicMock()
    pager = case.database.query_containers(SQL, response_hook=hook, **kwargs)
    with pytest.raises((NotImplementedError, TypeError, exceptions.CosmosClientTimeoutError)):
        _drain(case, pager)
    assert case.requests == []
    hook.assert_not_called()


@pytest.mark.parametrize("query,kwargs,error", [
    ([], {}, TypeError), (False, {}, TypeError), ({}, {}, ValueError),
    ({"query": ""}, {}, ValueError), (None, {"parameters": []}, ValueError),
])
def test_invalid_queries_preserve_errors_without_requests(query_case, query, kwargs, error):
    """A query that cannot be used is rejected without a request, with the error type
    that fits the mistake.

    A list and a boolean are the wrong kind of thing entirely, so they are
    ``TypeError``. A dictionary with no query text, a query that is an empty
    string, and parameters supplied with no query to bind them to are all the
    right kind of thing but unusable, so they are ``ValueError``.

    Keeping those apart matters to anyone catching one deliberately. Note that
    ``None`` with no parameters is a valid call -- it means "no filter" -- while
    ``None`` with parameters is not, because there is nothing for them to
    apply to.
    """
    with pytest.raises(error):
        _drain(query_case, query_case.database.query_containers(query, **kwargs))
    assert query_case.requests == []


@pytest.mark.parametrize("error", [
    ValueError("hook failed"), PagePreflightError("hook failed"),
    exceptions.CosmosResourceNotFoundError(status_code=404),
    exceptions.CosmosHttpResponseError(status_code=429),
    exceptions.CosmosHttpResponseError(status_code=500),
])
def test_hook_error_propagates_without_repeating_page(query_case, error):
    """An error from the customer's hook stops the walk without refetching the page.

    Five errors are raised from the hook, including two the SDK would normally
    read as service replies -- a not-found and a throttling response -- and one
    that normally means the engine cannot serve the page. Caught too broadly,
    any of those would be mistaken for something to react to: retrying the page,
    or restarting the feed elsewhere.

    Instead the exact exception reaches the caller after exactly one request.
    Refetching would charge the customer twice for a page they already received.
    """
    hook = MagicMock(side_effect=error)
    with pytest.raises(type(error)) as raised:
        _drain(query_case, query_case.database.query_containers(SQL, response_hook=hook))
    assert raised.value is error
    assert len(query_case.requests) == 1
    hook.assert_called_once()


@pytest.mark.parametrize("status", [403, 404, 429, 500])
def test_service_error_does_not_call_success_hook(query_case, status):
    """A failed page keeps its status and does not run the success hook.

    Four statuses are covered, each reaching the caller with its status code
    intact. The hook stays silent because nothing succeeded -- firing it here
    would report a charge for a page the customer never received.

    Throttling is allowed more than one request, being the one status the client
    is expected to retry; the others must produce exactly one.
    """
    query_case.responses[""] = _page([], status=status)
    hook = MagicMock()
    with pytest.raises(exceptions.CosmosHttpResponseError) as raised:
        _drain(query_case, query_case.database.query_containers(SQL, response_hook=hook))
    assert raised.value.status_code == status
    hook.assert_not_called()
    assert len(query_case.requests) == 1 if status != 429 else len(query_case.requests) >= 1


@pytest.mark.parametrize("error", [
    PagePreflightError("unsupported"), ValueError("binding failure"), asyncio.CancelledError(),
])
def test_binding_failure_never_replays_on_legacy(query_case, error):
    """A failure inside the Rust engine, including cancellation, ends the walk after
    one request.

    All three reach the caller unchanged: a page the engine says it cannot
    serve, an ordinary error, and cancellation. The first is the tempting one --
    it sounds like an invitation to retry on legacy -- but restarting the query
    there would charge the customer for the same page twice and could interleave
    results from two separate walks.

    Cancellation must pass through untouched, or it stops unwinding and the
    caller's request to stop is ignored.

    Skipped on the legacy setups, which have no such engine.
    """
    if not query_case.rust:
        pytest.skip("Rust-specific binding failures")
    query_case.failure = error
    with pytest.raises(type(error)) as raised:
        _drain(query_case, query_case.database.query_containers(SQL))
    assert raised.value is error
    assert len(query_case.requests) == 1


def test_timeout_restarts_between_public_pages(query_case, monkeypatch):
    """The deadline covers fetching one page, not the whole walk.

    The clock jumps ten seconds before the first page and ten more before the
    second, far past the one-second deadline, and both pages still arrive.

    Customers iterate query results slowly, processing each page as it comes. If
    the deadline covered the entire walk, a feed would expire mid-iteration for
    reasons unrelated to how the service responded.
    """
    case = query_case
    clock = [100.0]
    monkeypatch.setattr(time, "time", lambda: clock[0])
    pages = case.database.query_containers(SQL, timeout=1).by_page()
    clock[0] += 10

    def sync_call():
        first = list(next(pages))
        clock[0] += 10
        return first + list(next(pages))

    async def async_call():
        first = [item async for item in await pages.__anext__()]
        clock[0] += 10
        return first + [item async for item in await pages.__anext__()]

    assert len(_run(case, sync_call, async_call)) == 2


def test_empty_page_does_not_reset_current_budget(query_case, monkeypatch):
    """Time spent skipping past pages that matched nothing counts against the page the
    customer is waiting for.

    The deadline restarts between pages the *customer* asks for. This is the
    other half: when a page matches nothing but carries a token, the SDK fetches
    again on its own to find something to return, and that inner loop must not
    keep resetting the allowance.

    This matters more for a query than for a listing, because a selective filter
    can produce a long run of pages that match nothing. Here the hook advances
    the clock past a one-second deadline and the walk gives up after a single
    request, rather than leaving a customer waiting indefinitely on a call they
    had given one second.

    Skipped on legacy, where the fake transport does not apply these checks.
    """
    case = query_case
    if not case.rust:
        pytest.skip("Fake legacy transport does not enforce socket timeouts")
    clock = [100.0]
    monkeypatch.setattr(time, "time", lambda: clock[0])
    case.responses[""] = _page([], "next")

    def hook(headers):
        clock[0] += 2

    with pytest.raises(exceptions.CosmosClientTimeoutError):
        _drain(case, case.database.query_containers(SQL, timeout=1, response_hook=hook))
    assert len(case.requests) == 1
