# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Container metadata bookmarks belong to each page iterator, not the client."""
import asyncio
from dataclasses import replace
from unittest.mock import MagicMock

import pytest
from common.test_query_containers_backend_unit import query_case, SQL  # pylint: disable=unused-import
from common.test_list_containers_backend_unit import listing_case, _page, _run, _drain  # pylint: disable=unused-import

from azure.core.utils import CaseInsensitiveDict
from azure.cosmos._backend.errors import BindingProtocolError
from azure.cosmos.exceptions import CosmosHttpResponseError


@pytest.fixture(name="metadata_case", params=["list", "query"])
def metadata_case_setup(query_case, request):  # pylint: disable=redefined-outer-name
    case = query_case
    case.query = request.param == "query"
    case.listing = (
        (lambda **kwargs: case.database.query_containers(SQL, **kwargs))
        if case.query else case.database.list_containers
    )
    return case


def _next(case, pages):
    async def consume():
        return [item async for item in await pages.__anext__()]
    return _run(case, lambda: list(next(pages)), consume)


def test_hook_cannot_replace_the_delivered_bookmark_rust(metadata_case):
    case = metadata_case

    def hook(headers, results):
        assert results is result
        assert headers["x-ms-continuation"] == "next"
        headers.clear()
        case.connection.last_response_headers = CaseInsensitiveDict({"x-ms-continuation": "other-operation"})

    result = case.listing(response_hook=hook)
    pages = result.by_page()
    assert _next(case, pages) == [{"id": "c1"}]
    assert pages.continuation_token == "next"


def test_terminal_empty_page_clears_bookmark_rust(metadata_case):
    case = metadata_case
    case.responses["next"] = _page([])
    hook = MagicMock()
    pages = case.listing(response_hook=hook).by_page()
    assert _next(case, pages) == [{"id": "c1"}]
    assert pages.continuation_token == "next"
    with pytest.raises(StopAsyncIteration if case.is_async else StopIteration):
        _next(case, pages)
    assert pages.continuation_token is None
    assert hook.call_count == 2
    assert len(case.requests) == 2


def test_nested_public_listing_preserves_outer_bookmark_rust(metadata_case):
    case = metadata_case
    if case.is_async:
        pytest.skip("Synchronous nested operation inside a synchronous response hook")

    def hook(headers, _results):
        assert headers["x-ms-continuation"] == "next"
        assert _drain(case, case.listing()) == [{"id": "c1"}, {"id": "c2"}]

    pages = case.listing(response_hook=hook).by_page()
    assert _next(case, pages) == [{"id": "c1"}]
    assert pages.continuation_token == "next"


def test_replay_does_not_change_other_iterators_rust(metadata_case):
    case = metadata_case
    result = case.listing()
    resumed = result.by_page("next")
    original = result.by_page()
    assert _next(case, original) == [{"id": "c1"}]
    assert _next(case, resumed) == [{"id": "c2"}]
    assert resumed.continuation_token is None
    assert original.continuation_token == "next"
    assert _next(case, original) == [{"id": "c2"}]


def test_nonadvancing_empty_page_fails_without_looping_rust(metadata_case):
    case = metadata_case
    case.responses["next"] = _page([], "next")
    pages = case.listing().by_page("next")
    with pytest.raises(BindingProtocolError, match="without continuation progress"):
        _next(case, pages)
    assert len(case.requests) == 1
    with pytest.raises(RuntimeError, match="pager failed"):
        _next(case, pages)
    assert len(case.requests) == 1


@pytest.mark.parametrize("kind", [StopIteration, StopAsyncIteration, ValueError])
def test_hook_failure_does_not_publish_or_replay_page_rust(metadata_case, kind):
    case = metadata_case
    hook = MagicMock()
    pages = case.listing(response_hook=hook).by_page()
    assert _next(case, pages) == [{"id": "c1"}]
    hook.side_effect = kind("customer hook failed")
    with pytest.raises(ValueError if kind is ValueError else RuntimeError):
        _next(case, pages)
    assert pages.continuation_token == "next"
    assert len(case.requests) == 2
    with pytest.raises(RuntimeError, match="pager failed"):
        _next(case, pages)
    assert len(case.requests) == 2


@pytest.mark.parametrize("status", [429, 503])
def test_rust_final_error_is_not_retried_by_python_rust(metadata_case, monkeypatch, status):
    case = metadata_case
    if not case.rust:
        pytest.skip("The explicitly selected legacy backend retains its HTTP retry policy")
    from azure.cosmos import _retry_utility
    from azure.cosmos.aio import _retry_utility_async

    forbidden = MagicMock(side_effect=AssertionError("Metadata paging entered legacy retries"))
    monkeypatch.setattr(_retry_utility, "Execute", forbidden)
    monkeypatch.setattr(_retry_utility_async, "ExecuteAsync", forbidden)
    case.responses[""] = _page([], status=status)
    with pytest.raises(CosmosHttpResponseError) as raised:
        _drain(case, case.listing())
    assert raised.value.status_code == status
    assert len(case.requests) == 1
    forbidden.assert_not_called()


def test_query_projection_is_not_forced_to_resource_dictionaries_rust(metadata_case):
    case = metadata_case
    if not case.query:
        pytest.skip("Scalar rows are a query projection, not a resource listing")
    case.responses[""] = replace(_page([]), body=b'{"DocumentCollections":["c1",2,null]}')
    assert _drain(case, case.listing()) == ["c1", 2, None]


@pytest.mark.asyncio
async def test_async_cancellation_stops_work_and_poisoned_pager_rust(metadata_case):
    case = metadata_case
    if not case.rust or not case.is_async:
        pytest.skip("Async Rust cancellation")
    entered = asyncio.Event()
    stopped = asyncio.Event()

    async def fetch(prepared, *, deadline=None):
        assert prepared.op == ("query_containers" if case.query else "list_containers")
        assert deadline is None
        try:
            entered.set()
            await asyncio.Future()
            yield _page([])
        finally:
            stopped.set()

    case.connection._backend.execute_pages = fetch
    pages = case.listing().by_page()
    task = asyncio.create_task(pages.__anext__())
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert stopped.is_set()
    assert pages.continuation_token is None
    with pytest.raises(RuntimeError, match="pager failed"):
        await pages.__anext__()
