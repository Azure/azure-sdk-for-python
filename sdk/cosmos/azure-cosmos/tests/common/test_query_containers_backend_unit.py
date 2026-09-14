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
from azure.cosmos._backend.errors import PageNotSupportedByBackendError
from azure.cosmos._backend.operations import OP_LIST_CONTAINERS, OP_QUERY_CONTAINERS
from .test_list_containers_backend_unit import listing_case, _page, _drain, _run


SQL = "SELECT * FROM c WHERE c.id != @excluded"
PARAMETERS = [{"name": "@excluded", "value": "missing"}]


@pytest.fixture
def query_case(listing_case):
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
    sync = inspect.signature(DatabaseProxy.query_containers)
    asynchronous = inspect.signature(AsyncDatabaseProxy.query_containers)
    assert sync.parameters == asynchronous.parameters


@pytest.mark.parametrize("form", ["string", "dictionary", "parameters"])
def test_query_payload_and_lazy_resumable_pages(query_case, form):
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
    with pytest.raises(TypeError, match=option):
        query_case.database.query_containers(SQL, **{option: value})
    assert query_case.requests == []


@pytest.mark.parametrize("args", [(), (SQL, []), (SQL, [], 1), (SQL, [], 1, False)])
def test_query_required_and_only_positional_argument(query_case, args):
    with pytest.raises(TypeError):
        query_case.database.query_containers(*args)
    assert query_case.requests == []


@pytest.mark.parametrize("value", [False, 0, 1])
def test_read_timeout_rejected(query_case, value):
    with pytest.raises(TypeError, match="read_timeout"):
        query_case.database.query_containers(SQL, read_timeout=value)
    assert query_case.requests == []


@pytest.mark.parametrize("query", [SQL, None])
@pytest.mark.parametrize("timeout", [None, 1, 1.5, 10])
def test_supported_timeout_headers_and_explicit_none_query(query_case, query, timeout):
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
            assert prepared.headers["initialHeaders"]["x-company-trace"] == "query-containers"
            budget = prepared.headers.get("__overall_timeout_seconds")
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
    with pytest.raises(error):
        _drain(query_case, query_case.database.query_containers(query, **kwargs))
    assert query_case.requests == []


@pytest.mark.parametrize("error", [
    ValueError("hook failed"), PageNotSupportedByBackendError("hook failed"),
    exceptions.CosmosResourceNotFoundError(status_code=404),
    exceptions.CosmosHttpResponseError(status_code=429),
    exceptions.CosmosHttpResponseError(status_code=500),
])
def test_hook_error_propagates_without_repeating_page(query_case, error):
    hook = MagicMock(side_effect=error)
    with pytest.raises(type(error)) as raised:
        _drain(query_case, query_case.database.query_containers(SQL, response_hook=hook))
    assert raised.value is error
    assert len(query_case.requests) == 1
    hook.assert_called_once()


@pytest.mark.parametrize("status", [403, 404, 429, 500])
def test_service_error_does_not_call_success_hook(query_case, status):
    query_case.responses[""] = _page([], status=status)
    hook = MagicMock()
    with pytest.raises(exceptions.CosmosHttpResponseError) as raised:
        _drain(query_case, query_case.database.query_containers(SQL, response_hook=hook))
    assert raised.value.status_code == status
    hook.assert_not_called()
    assert len(query_case.requests) == 1 if status != 429 else len(query_case.requests) >= 1


@pytest.mark.parametrize("error", [
    PageNotSupportedByBackendError("unsupported"), ValueError("binding failure"), asyncio.CancelledError(),
])
def test_binding_failure_never_replays_on_legacy(query_case, error):
    if not query_case.rust:
        pytest.skip("Rust-specific binding failures")
    query_case.failure = error
    with pytest.raises(type(error)) as raised:
        _drain(query_case, query_case.database.query_containers(SQL))
    assert raised.value is error
    assert len(query_case.requests) == 1


def test_timeout_restarts_between_public_pages(query_case, monkeypatch):
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
