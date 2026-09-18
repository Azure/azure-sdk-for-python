# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Database listing ownership, callbacks and elapsed page budgets; no service calls."""
import asyncio
import json
import time
from unittest.mock import MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import _rust
from azure.cosmos._backend import rust as sync_rust
from azure.cosmos.aio._backend import rust as async_rust
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.errors import BackendProtocolError
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from query_items.test_query_backend_routing_unit import (
    listing_client,
    _configure_legacy_database_feed,
    _next_listing_page,
)


@pytest.fixture(params=[False, True], ids=["rust", "legacy"])
def listing(listing_client, request):
    client, connection, backend, is_async = listing_client
    legacy = request.param
    if legacy:
        _configure_legacy_database_feed(connection, is_async)
        client._backend = connection._backend

        def respond(*args, **kwargs):
            reply = backend._response
            headers = CaseInsensitiveDict(reply.headers)
            connection.last_response_headers = headers
            return json.loads(reply.body), headers

        connection._CosmosClientConnection__Get.side_effect = respond
    return client, connection, backend, is_async, legacy


def requests(listing):
    _, connection, backend, _, legacy = listing
    return connection._CosmosClientConnection__Get if legacy else backend.execute_pages


@pytest.mark.asyncio
async def test_bookmark_is_owned_by_pager_even_when_hook_runs_other_work(listing):
    client, connection, _, is_async, _ = listing
    def hook(headers):
        assert headers["x-ms-continuation"] == "next-db-page"
        headers.clear()
        connection.last_response_headers = CaseInsensitiveDict({"x-ms-continuation": "other-operation"})
    pager = client.list_databases(response_hook=hook).by_page()
    assert await _next_listing_page(pager, is_async)
    assert pager.continuation_token == "next-db-page"


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [429, 410, 503])
async def test_callback_service_error_is_not_retried_or_swallowed(listing, status):
    client, _, _, is_async, _ = listing
    error = CosmosHttpResponseError(status_code=status, message="customer hook error")
    hook = MagicMock(side_effect=error)
    pager = client.list_databases(response_hook=hook).by_page()
    with pytest.raises(CosmosHttpResponseError) as raised:
        await _next_listing_page(pager, is_async)
    assert raised.value is error
    requests(listing).assert_called_once()
    hook.assert_called_once()
    with pytest.raises(RuntimeError, match="pager failed"):
        await _next_listing_page(pager, is_async)
    requests(listing).assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", [StopIteration, StopAsyncIteration])
async def test_iteration_stop_callback_cannot_hide_results(listing, kind):
    client, _, _, is_async, _ = listing
    error = kind("customer hook error")
    pager = client.list_databases(response_hook=MagicMock(side_effect=error)).by_page()
    with pytest.raises(RuntimeError, match="iteration-stop") as raised:
        await _next_listing_page(pager, is_async)
    assert raised.value.__cause__ is error
    requests(listing).assert_called_once()


@pytest.mark.parametrize("hook", [False, 0, "not callable", {}])
def test_invalid_hook_rejected_without_request(listing, hook):
    with pytest.raises(TypeError, match="callable"):
        listing[0].list_databases(response_hook=hook)
    requests(listing).assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("option_name", ["request_options", "feed_options"])
async def test_nested_input_is_copied_before_iteration(listing, option_name):
    client, _, backend, is_async, legacy = listing
    headers = {"x-my-app": "original"}
    options = {"initialHeaders": headers, "maxItemCount": 2}
    pages = client.list_databases(**{option_name: options})
    assert options == {"initialHeaders": {"x-my-app": "original"}, "maxItemCount": 2}
    headers["x-my-app"] = "changed"
    options["maxItemCount"] = 99
    assert await _next_listing_page(pages.by_page(), is_async)
    if legacy:
        sent = requests(listing).call_args.args[2]
        assert sent["x-my-app"] == "original"
        assert str(sent["x-ms-max-item-count"]) == "2"
    else:
        assert backend.prepared.headers["x-my-app"] == "original"
        assert backend.prepared.max_item_count == 2
    assert "operationStartTime" not in options
    assert "continuation" not in options


@pytest.mark.asyncio
async def test_replay_does_not_change_an_existing_pagers_bookmark(listing):
    client, _, backend, is_async, _ = listing
    items = client.list_databases()
    first = items.by_page()
    await _next_listing_page(first, is_async)
    backend._response = BackendResponse(
        status_code=200, headers=CaseInsensitiveDict(), body=b'{"Databases":[{"id":"last"}]}',
    )
    second = items.by_page("different-start")
    await _next_listing_page(second, is_async)
    assert second.continuation_token is None
    assert first.continuation_token == "next-db-page"


@pytest.mark.asyncio
@pytest.mark.parametrize("spent", [3.0, 4.75])
async def test_empty_service_page_uses_remaining_budget(listing, monkeypatch, spent):
    client, connection, backend, is_async, legacy = listing
    clock = [100.0]
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(time, "time", lambda: clock[0])
    budgets = []
    pages = [
        BackendResponse(status_code=200, headers={"x-ms-continuation": "next"}, body=b'{"Databases":[]}'),
        BackendResponse(status_code=200, headers={}, body=b'{"Databases":[{"id":"last"}]}'),
    ]
    original = type(backend).execute_pages
    def response():
        page = pages[len(budgets) - 1]
        if len(budgets) == 1:
            clock[0] += spent
        return page
    if legacy:
        def legacy_request(*args, **kwargs):
            budgets.append(kwargs["timeout"])
            page = response()
            headers = CaseInsensitiveDict(page.headers)
            connection.last_response_headers = headers
            return json.loads(page.body), headers
        requests(listing).side_effect = legacy_request
    else:
        def execute(prepared, *, deadline=None):
            budgets.append(prepared.settings.timeout_seconds)
            assert deadline == 105
            backend._response = response()
            return original(backend, prepared, deadline=deadline)
        requests(listing).side_effect = execute
    hooks = []
    assert await _next_listing_page(client.list_databases(timeout=5, response_hook=hooks.append).by_page(), is_async)
    assert budgets == [5, 5 - spent]
    assert len(hooks) == 2


@pytest.mark.parametrize("timeout", [False, 0, 0.25, "5", float("nan"), float("inf"), 2**64])
def test_invalid_timeout_rejected_before_iteration(listing, timeout):
    with pytest.raises(ValueError, match="timeout"):
        listing[0].list_databases(timeout=timeout)
    requests(listing).assert_not_called()


@pytest.mark.parametrize("count", [False, 0, -2, 2.5, "2", 2**63])
def test_invalid_page_size_rejected_before_iteration(listing, count):
    with pytest.raises(ValueError, match="max_item_count"):
        listing[0].list_databases(max_item_count=count)
    requests(listing).assert_not_called()


@pytest.mark.asyncio
async def test_explicit_none_clears_nested_timeout(listing):
    client, _, _, is_async, _ = listing
    options = {"timeout": 2}
    pager = client.list_databases(request_options=options, timeout=None).by_page()
    assert pager.state.config.timeout is None
    await _next_listing_page(pager, is_async)
    assert options == {"timeout": 2}


@pytest.mark.asyncio
@pytest.mark.parametrize("setup_seconds", [2, 4.75, 6])
async def test_real_rust_backend_deducts_setup_before_binding(listing_client, monkeypatch, setup_seconds):
    client, _, backend, is_async = listing_client
    clock = [100.0]
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    module = async_rust if is_async else sync_rust
    captured = []
    def acquire():
        clock[0] += setup_seconds
        return "offline"
    async def acquire_async():
        return acquire()
    def dispatch(handle, prepared, *, timeout_seconds):
        captured.append(timeout_seconds)
        return 200, 0, {}, b'{"Databases":[{"id":"sales"}]}'
    async def dispatch_async(handle, prepared, *, timeout_seconds):
        return dispatch(handle, prepared, timeout_seconds=timeout_seconds)
    backend._ensure_driver_handle = acquire_async if is_async else acquire
    execute = module.AsyncRustBackend.execute_pages if is_async else module.RustBackend.execute_pages
    backend.execute_pages = lambda prepared, deadline=None: execute(backend, prepared, deadline=deadline)
    monkeypatch.setattr(module, "_get_page_dispatch", lambda method: dispatch_async if is_async else dispatch)
    pager = client.list_databases(timeout=5).by_page()
    if setup_seconds >= 5:
        with pytest.raises(CosmosClientTimeoutError):
            await _next_listing_page(pager, is_async)
        assert captured == []
    else:
        await _next_listing_page(pager, is_async)
        assert captured == [5 - setup_seconds]


@pytest.mark.asyncio
async def test_async_cancellation_drains_page_work(listing_client):
    client, _, backend, is_async = listing_client
    if not is_async:
        return
    started = asyncio.Event()
    stopped = asyncio.Event()
    async def execute(prepared, *, deadline=None):
        try:
            started.set()
            await asyncio.Event().wait()
            yield None
        finally:
            stopped.set()
    backend.execute_pages = execute
    hooks = []
    pager = client.list_databases(timeout=5, response_hook=hooks.append).by_page()
    task = asyncio.create_task(_next_listing_page(pager, True))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert stopped.is_set()
    assert hooks == []
    with pytest.raises(RuntimeError, match="pager failed"):
        await _next_listing_page(pager, True)


@pytest.mark.asyncio
@pytest.mark.parametrize("seconds", [None, 0.25, 2])
async def test_native_listing_accepts_remaining_duration(listing_client, seconds):
    client, _, _, is_async = listing_client
    config = client.list_databases().by_page().state.config
    prepared = sync_rust.build_binding_request_from_page(config.prepared(None, None))
    function = _rust.list_databases_async if is_async else _rust.list_databases
    with pytest.raises(RuntimeError, match="(?i)driver"):
        result = function("unregistered-listing-review", prepared, timeout_seconds=seconds)
        if is_async:
            await result


@pytest.mark.asyncio
async def test_async_timeout_drains_page_and_prevents_hook(listing_client):
    client, _, backend, is_async = listing_client
    if not is_async:
        return
    stopped = asyncio.Event()
    async def execute(prepared, *, deadline=None):
        try:
            await asyncio.Event().wait()
            yield None
        finally:
            stopped.set()
    backend.execute_pages = execute
    hook = MagicMock()
    pager = client.list_databases(timeout=1, response_hook=hook).by_page()
    # A valid initial budget can have only a fraction remaining.
    pager.state.config.deadline = lambda: time.monotonic() + 0.02
    with pytest.raises(CosmosClientTimeoutError):
        await _next_listing_page(pager, True)
    assert stopped.is_set()
    hook.assert_not_called()


@pytest.mark.asyncio
async def test_failed_fetch_does_not_advance_delivered_bookmark(listing):
    client, _, _, is_async, _ = listing
    pager = client.list_databases().by_page()
    await _next_listing_page(pager, is_async)
    requests(listing).side_effect = CosmosHttpResponseError(status_code=403, message="denied")
    with pytest.raises(CosmosHttpResponseError):
        await _next_listing_page(pager, is_async)
    assert pager.continuation_token == "next-db-page"
    with pytest.raises(RuntimeError, match="pager failed"):
        await _next_listing_page(pager, is_async)
    assert requests(listing).call_count == 2


@pytest.mark.asyncio
async def test_concurrent_fetch_rejected_without_poisoning_first_fetch(listing_client):
    client, _, backend, is_async = listing_client
    if not is_async:
        return
    started, release = asyncio.Event(), asyncio.Event()
    original = type(backend).execute_pages
    async def execute(prepared, *, deadline=None):
        started.set()
        await release.wait()
        async for page in original(backend, prepared, deadline=deadline):
            yield page
    backend.execute_pages = execute
    pager = client.list_databases().by_page()
    first = asyncio.create_task(_next_listing_page(pager, True))
    await started.wait()
    with pytest.raises(RuntimeError, match="Concurrent"):
        await _next_listing_page(pager, True)
    release.set()
    assert await first
    assert not pager.state.failed


@pytest.mark.asyncio
@pytest.mark.parametrize("body", [b"{}", b'{"Databases":{}}', b'{"Databases":[3]}'])
async def test_malformed_rust_page_is_an_explicit_error(listing_client, body):
    client, _, backend, is_async = listing_client
    backend._response = BackendResponse(status_code=200, headers={}, body=body)
    hook = MagicMock()
    with pytest.raises(BackendProtocolError, match="invalid Databases"):
        await _next_listing_page(client.list_databases(response_hook=hook).by_page(), is_async)
    hook.assert_not_called()


@pytest.mark.asyncio
async def test_terminal_empty_page_clears_public_bookmark(listing):
    client, _, backend, is_async, _ = listing
    hook = MagicMock()
    pager = client.list_databases(response_hook=hook).by_page()
    await _next_listing_page(pager, is_async)
    assert pager.continuation_token == "next-db-page"
    backend._response = BackendResponse(status_code=200, headers={}, body=b'{"Databases":[]}')
    if is_async:
        with pytest.raises(StopAsyncIteration):
            await pager.__anext__()
    else:
        with pytest.raises(StopIteration):
            next(pager)
    assert pager.continuation_token is None
    assert hook.call_count == 2


@pytest.mark.asyncio
async def test_repeated_empty_page_bookmark_is_an_explicit_error(listing):
    client, _, backend, is_async, _ = listing
    backend._response = BackendResponse(
        status_code=200, headers={"x-ms-continuation": "same"}, body=b'{"Databases":[]}',
    )
    pager = client.list_databases().by_page("same")
    with pytest.raises(BackendProtocolError, match="without continuation progress"):
        await _next_listing_page(pager, is_async)
    requests(listing).assert_called_once()


def test_nested_public_sync_listing_preserves_outer_bookmark(listing):
    client, _, backend, is_async, _ = listing
    if is_async:
        return
    def hook(headers):
        backend._response = BackendResponse(
            status_code=200, headers={}, body=b'{"Databases":[{"id":"nested"}]}',
        )
        assert list(client.list_databases()) == [{"id": "nested"}]
    pager = client.list_databases(response_hook=hook).by_page()
    assert list(next(pager))
    assert pager.continuation_token == "next-db-page"


def test_sync_guard_covers_public_bookmark_publication(listing):
    client, _, _, is_async, _ = listing
    if is_async:
        return
    pager = client.list_databases().by_page()
    original = pager._extract_data
    def extract(value):
        with pytest.raises(RuntimeError, match="Concurrent"):
            pager.next()
        return original(value)
    pager._extract_data = extract
    assert list(next(pager))
    assert pager.continuation_token == "next-db-page"
    assert not pager.state.failed
    requests(listing).assert_called_once()
