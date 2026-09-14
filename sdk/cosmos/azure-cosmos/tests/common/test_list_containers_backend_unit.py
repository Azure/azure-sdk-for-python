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
from azure.cosmos._backend.contracts import QueryPage
from azure.cosmos._backend.errors import PageNotSupportedByBackendError
from azure.cosmos._backend.operations import OP_LIST_CONTAINERS
from azure.cosmos._query_rust_routing import can_use_rust_backend_for_query_containers_page
from azure.cosmos.http_constants import ResourceType
from .test_container_backend_unit import (
    _CapturingPagedBackend, _CapturingAsyncPagedBackend,
    _new_sync_connection, _new_async_connection,
)


def _page(ids, continuation=None, status=200):
    headers = CaseInsensitiveDict({"x-ms-request-charge": "2", "x-ms-activity-id": ",".join(ids) or "empty"})
    if continuation:
        headers["x-ms-continuation"] = continuation
    return QueryPage(
        status_code=status, continuation=continuation, headers=headers,
        body=json.dumps({"DocumentCollections": [{"id": value} for value in ids]}).encode(),
    )


@pytest.fixture(params=["sync-rust", "async-rust", "sync-legacy", "async-legacy"])
def listing_case(request):
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

        def execute_pages(self, prepared):
            yield response(prepared.continuation, prepared)

    class AsyncBackend(_CapturingAsyncPagedBackend):
        name = "rust"

        async def execute_pages(self, prepared):
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
    return asyncio.run(async_call()) if case.is_async else sync_call()


def _drain(case, pager):
    async def collect():
        return [item async for item in pager]
    return _run(case, lambda: list(pager), collect)


def test_lazy_pages_and_continuation_resume(listing_case):
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
    case = listing_case
    case.responses[""] = _page([])
    hook = MagicMock()
    assert _drain(case, case.database.list_containers(response_hook=hook)) == []
    hook.assert_called_once()


@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics", "availability_strategy"])
@pytest.mark.parametrize("value", [None, False, True])
def test_obsolete_options_fail_before_paging(listing_case, option, value):
    case = listing_case
    with pytest.raises(TypeError, match=option):
        case.database.list_containers(**{option: value})
    assert case.requests == []


@pytest.mark.parametrize("args", [(1,), (1, False)])
def test_options_are_keyword_only(listing_case, args):
    with pytest.raises(TypeError):
        listing_case.database.list_containers(*args)
    assert listing_case.requests == []


@pytest.mark.parametrize("value", [False, 0, 1])
def test_socket_timeout_is_rejected(listing_case, value):
    with pytest.raises(TypeError, match="read_timeout"):
        listing_case.database.list_containers(read_timeout=value)
    assert listing_case.requests == []


@pytest.mark.parametrize("timeout", [None, 1, 1.5, 10])
def test_supported_timeout_and_application_headers(listing_case, timeout):
    case = listing_case
    pager = case.database.list_containers(
        timeout=timeout, read_timeout=None, initial_headers={"x-company-trace": "listing"}
    )
    assert len(_drain(case, pager)) == 2
    if case.rust:
        for prepared in case.requests:
            assert prepared.headers["initialHeaders"]["x-company-trace"] == "listing"
            budget = prepared.headers.get("__overall_timeout_seconds")
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
    ValueError("hook failed"), PageNotSupportedByBackendError("hook failed"),
    exceptions.CosmosResourceNotFoundError(status_code=404),
    exceptions.CosmosHttpResponseError(status_code=429),
    exceptions.CosmosHttpResponseError(status_code=500),
])
def test_hook_failure_does_not_fetch_again_or_fall_back(listing_case, error):
    case = listing_case
    hook = MagicMock(side_effect=error)
    with pytest.raises(type(error)) as raised:
        _drain(case, case.database.list_containers(response_hook=hook))
    assert raised.value is error
    assert len(case.requests) == 1
    hook.assert_called_once()


@pytest.mark.parametrize("status", [403, 404, 429, 500])
def test_error_page_does_not_invoke_success_hook(listing_case, status):
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
    PageNotSupportedByBackendError("unsupported page"), ValueError("binding failure"), asyncio.CancelledError(),
])
def test_binding_failures_are_not_replayed(listing_case, error):
    case = listing_case
    if not case.rust:
        pytest.skip("Rust-specific binding failure")
    case.failure = error
    with pytest.raises(type(error)) as raised:
        _drain(case, case.database.list_containers())
    assert raised.value is error
    assert len(case.requests) == 1


def test_timeout_restarts_between_public_page_fetches(listing_case, monkeypatch):
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
    assert can_use_rust_backend_for_query_containers_page(
        path="/dbs/db1/colls/", query_payload={"query": "SELECT * FROM c"},
        options={"timeout": 10}, kwargs={"timeout": 10},
        is_query_plan=False, resource_type=ResourceType.Collection,
    )
