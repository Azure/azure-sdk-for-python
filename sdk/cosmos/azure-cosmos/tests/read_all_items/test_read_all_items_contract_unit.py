# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Rust-only live paging, explicit non-resumability, and per-page budgets."""

import asyncio
import inspect
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.exceptions import ServiceResponseError

from azure.cosmos import _operation_deadline
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos._backend import binding_adapter as sync_rust
from azure.cosmos.aio._backend import binding_adapter as async_rust
from azure.cosmos._helpers import _read_all_items
from azure.cosmos._helpers._item_context import ItemClientContext, ItemClientDefaults
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def feed(request, monkeypatch):
    """Keep the real proxy, adapter and pager; replace only native I/O and time."""
    async_mode = request.param
    clock = SimpleNamespace(now=100.0)
    clock.monotonic = lambda: clock.now
    monkeypatch.setattr(_read_all_items, "time", clock)
    monkeypatch.setattr(_operation_deadline, "time", clock)
    context = SimpleNamespace(
        clock=clock, calls=[], delay=0, init_delay=0, async_mode=async_mode,
        status=200, setup_status=0,
        pages=[[{"id": "a", "nested": [1]}], [], [{"id": "b"}], []],
    )

    def page(handle, prepared, cursor, *, timeout_seconds=None):
        context.calls.append((prepared, cursor, timeout_seconds))
        assert prepared.op == "read_all_items"
        assert prepared.body_bytes == b""
        assert prepared.settings.query.continuation is None
        if context.setup_status:
            return context.setup_status, 0, {}, b'{"message":"setup failed"}', None
        cursor.can_retry_setup = False
        if timeout_seconds is not None and context.delay > timeout_seconds:
            raise TimeoutError("native page budget exhausted")
        clock.now += context.delay
        rows = context.pages[cursor.index]
        cursor.index += 1
        cursor.has_more = cursor.index < len(context.pages)
        context.prepared = prepared
        return (
            context.status, 0,
            {"x-ms-request-charge": "2", "x-ms-session-token": "session"},
            json.dumps({"Documents": rows}).encode(), None,
        )

    def ensure(**_kwargs):
        clock.now += context.init_delay
        return "handle"

    module = async_rust if async_mode else sync_rust
    binding = SimpleNamespace(
        _ItemFeedCursor=MagicMock(side_effect=lambda: SimpleNamespace(
            can_retry_setup=True, index=0, has_more=True, continuation_supported=False,
        )),
        read_all_items=MagicMock(),
        read_all_items_async=AsyncMock(),
        fetch_page_with_cursor=MagicMock(side_effect=page),
        fetch_page_with_cursor_async=AsyncMock(side_effect=page),
    )
    monkeypatch.setattr(module, "_rust_module", binding)
    backend_type = async_rust.AsyncBindingAdapter if async_mode else sync_rust.BindingAdapter
    backend = backend_type("https://read-all.invalid", master_key="ZmFrZQ==")
    monkeypatch.setattr(
        backend, "_ensure_driver_handle",
        AsyncMock(side_effect=ensure) if async_mode else MagicMock(side_effect=ensure),
    )
    connection = MagicMock()
    connection._backend = backend
    context.item_context = ItemClientContext(backend)
    context.proxy = (AsyncContainerProxy if async_mode else ContainerProxy)(
        connection, "dbs/db", "c", _item_context=context.item_context,
    )
    context.binding, context.connection, context.backend = binding, connection, backend

    def collect(pager):
        async def collect_async():
            return [row async for row in pager]
        return asyncio.run(collect_async()) if async_mode else list(pager)

    def next_page(pages):
        async def fetch():
            return [row async for row in await pages.__anext__()]
        return asyncio.run(fetch()) if async_mode else list(next(pages))

    context.collect, context.next_page = collect, next_page
    yield context
    closed = backend.close()
    if inspect.isawaitable(closed):
        asyncio.run(closed)


class ForbiddenConnection:
    def __getattr__(self, name):
        raise AssertionError(f"Legacy connection accessed: {name}")


@pytest.mark.parametrize("kwargs,priority,bucket", [
    ({}, "Low", 3), ({"priority": "High", "throughput_bucket": 5}, "High", 5),
])
def test_read_all_inherits_client_defaults_rust(feed, kwargs, priority, bucket):
    feed.proxy._item_context = ItemClientContext(
        feed.backend, ItemClientDefaults(priority="Low", throughput_bucket=3, operation_timeout_seconds=10)
    )
    feed.collect(feed.proxy.read_all_items(**kwargs))
    assert all(p.settings.priority == priority for p, _, _ in feed.calls)
    assert all(p.settings.throughput_bucket == bucket for p, _, _ in feed.calls)
    assert all(timeout == 10 for _, _, timeout in feed.calls)


def test_complete_enumeration_is_lazy_and_connection_free_rust(feed):
    feed.proxy.client_connection = ForbiddenConnection()
    pager = feed.proxy.read_all_items(max_item_count=1)
    assert feed.calls == []
    assert feed.collect(pager) == [{"id": "a", "nested": [1]}, {"id": "b"}]
    assert len(feed.calls) == 4
    assert len({id(cursor) for _, cursor, _ in feed.calls}) == 1
    assert all(p.settings.query.max_item_count == 1 for p, _, _ in feed.calls)
    assert "x-ms-continuation" not in pager.get_response_headers()
    feed.binding.read_all_items.assert_not_called()
    feed.binding.read_all_items_async.assert_not_called()


@pytest.mark.parametrize("context", [None, ItemClientContext(SimpleNamespace(name="core-python"))])
def test_missing_rust_context_never_consults_connection_rust(feed, context):
    feed.proxy.client_connection = ForbiddenConnection()
    feed.proxy._item_context = context
    with pytest.raises(NotImplementedError, match="client-owned Rust"):
        feed.proxy.read_all_items()
    assert not feed.calls


@pytest.mark.parametrize("status", [429, 503])
def test_initial_setup_service_error_can_retry_same_iterator_rust(feed, status):
    hook = MagicMock()
    pages = feed.proxy.read_all_items(response_hook=hook).by_page()
    feed.setup_status = status
    with pytest.raises(CosmosHttpResponseError) as caught:
        feed.next_page(pages)
    assert caught.value.status_code == status
    cursor = pages.state.cursor
    assert cursor is not None and not pages.state.failed
    hook.assert_not_called()
    feed.setup_status = 0
    assert feed.next_page(pages) == [{"id": "a", "nested": [1]}]
    assert all(call[1] is cursor for call in feed.calls)
    hook.assert_called_once()


def test_first_execution_service_error_invalidates_rust(feed):
    feed.status = 503
    pages = feed.proxy.read_all_items().by_page()
    with pytest.raises(CosmosHttpResponseError):
        feed.next_page(pages)
    assert pages.state.cursor is None
    with pytest.raises(RuntimeError, match="pager failed"):
        feed.next_page(pages)
    assert len(feed.calls) == 1


@pytest.mark.parametrize("error", [
    ServiceResponseError("setup transport failure"),
    CosmosClientTimeoutError(), TimeoutError("setup timeout"),
])
def test_setup_transport_retry_and_terminal_timeouts_rust(feed, error):
    pages = feed.proxy.read_all_items().by_page()
    fetch = feed.binding.fetch_page_with_cursor_async if feed.async_mode else feed.binding.fetch_page_with_cursor
    original = fetch.side_effect
    fetch.side_effect = error
    with pytest.raises(type(error)) as caught:
        feed.next_page(pages)
    assert caught.value is error
    fetch.side_effect = original
    if isinstance(error, ServiceResponseError):
        cursor = pages.state.cursor
        assert feed.next_page(pages) == [{"id": "a", "nested": [1]}]
        assert feed.calls[0][1] is cursor
    else:
        assert pages.state.cursor is None
        with pytest.raises(RuntimeError, match="pager failed"):
            feed.next_page(pages)
        assert feed.calls == []


def test_stale_cursor_contract_fails_before_fetch_rust(feed):
    feed.binding._ItemFeedCursor.side_effect = object
    pages = feed.proxy.read_all_items().by_page()
    with pytest.raises(RuntimeError, match="can_retry_setup.*rebuild"):
        feed.next_page(pages)
    assert not feed.calls and pages.state.cursor is None


def test_independent_live_pagers_ignore_connection_headers_rust(feed):
    first = feed.proxy.read_all_items().by_page()
    assert feed.next_page(first)[0]["id"] == "a"
    feed.connection.last_response_headers = {"x-ms-continuation": "unrelated"}
    second = feed.proxy.read_all_items().by_page()
    assert feed.next_page(second)[0]["id"] == "a"
    assert feed.next_page(first) == [{"id": "b"}]
    assert feed.next_page(second) == [{"id": "b"}]
    assert first.state.cursor is not second.state.cursor


@pytest.mark.parametrize("token", ["", "legacy", "c1.driver", "c2.driver"])
@pytest.mark.parametrize("location", ["by_page", "continuation", "request_options"])
def test_all_continuations_are_rejected_without_fetch_rust(feed, token, location):
    with pytest.raises(ValueError, match="does not support continuation"):
        if location == "by_page":
            feed.proxy.read_all_items().by_page(continuation_token=token)
        elif location == "request_options":
            feed.proxy.read_all_items(request_options={"continuation": token})
        else:
            feed.proxy.read_all_items(continuation=token)
    assert not feed.calls


def test_bookmark_property_is_explicitly_unsupported_rust(feed):
    pages = feed.proxy.read_all_items().by_page()
    with pytest.raises(NotImplementedError, match="cannot be bookmarked"):
        _ = pages.continuation_token
    feed.next_page(pages)
    with pytest.raises(NotImplementedError, match="cannot be bookmarked"):
        _ = pages.continuation_token
    assert feed.next_page(pages) == [{"id": "b"}]


@pytest.mark.parametrize("kwargs,error", [
    ({"populate_query_metrics": None}, TypeError),
    ({"populate_query_metrics": False}, TypeError),
    ({"populate_query_metrics": True}, TypeError),
    ({"max_item_count": 0}, ValueError), ({"max_item_count": -2}, ValueError),
    ({"max_item_count": True}, ValueError), ({"max_item_count": 1.5}, ValueError),
    ({"max_integrated_cache_staleness_in_ms": False}, ValueError),
    ({"max_integrated_cache_staleness_in_ms": -1}, ValueError),
    ({"timeout": float("nan")}, ValueError), ({"timeout": 0}, ValueError),
    ({"timeout": True}, ValueError), ({"response_hook": 4}, TypeError),
    ({"availability_strategy": False}, NotImplementedError),
    ({"feed_range": {}}, NotImplementedError),
    ({"request_options": {"partitionKeyRangeId": "0"}}, NotImplementedError),
    ({"initial_headers": {"authorization": "override"}}, NotImplementedError),
    ({"read_timeout": 25}, TypeError),
    ({"read_timeout": None}, TypeError),
    ({"raw_response_hook": None}, TypeError),
    ({"request_options": {"read_timeout": 25}}, TypeError),
])
def test_invalid_or_unsupported_options_do_not_dispatch_rust(feed, kwargs, error):
    with pytest.raises(error):
        feed.proxy.read_all_items(**kwargs)
    assert not feed.calls


def test_positional_settings_rejected_rust(feed):
    with pytest.raises(TypeError):
        feed.proxy.read_all_items(1)


@pytest.mark.parametrize("count", [None, -1, 1, 100])
def test_page_size_is_not_total_limit_rust(feed, count):
    assert len(feed.collect(feed.proxy.read_all_items(max_item_count=count))) == 2


def test_snapshot_options_and_isolate_falsey_hook_rust(feed):
    options = {"maxItemCount": 1, "initialHeaders": {"x-test": "before"}}
    calls = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            calls.append(dict(headers))
            headers["x-ms-continuation"] = "corrupt"
            body["Documents"].clear()

    pager = feed.proxy.read_all_items(request_options=options, response_hook=Hook())
    options["initialHeaders"]["x-test"] = "after"
    assert len(feed.collect(pager)) == 2
    assert feed.calls[0][0].headers["x-test"] == "before"
    assert calls and all("x-ms-continuation" not in headers for headers in calls)
    assert options == {"maxItemCount": 1, "initialHeaders": {"x-test": "after"}}


@pytest.mark.parametrize("error", [TimeoutError("customer hook"), StopIteration("hook")])
def test_hook_failure_is_not_replayed_or_silent_exhaustion_rust(feed, error):
    hook = MagicMock(side_effect=error)
    pages = feed.proxy.read_all_items(response_hook=hook).by_page()
    with pytest.raises(RuntimeError if isinstance(error, StopIteration) else TimeoutError):
        feed.next_page(pages)
    with pytest.raises(RuntimeError, match="pager failed"):
        feed.next_page(pages)
    assert len(feed.calls) == 1
    hook.assert_called_once()


def test_per_public_page_budget_includes_internal_empty_pages_rust(feed):
    feed.delay = 0.3
    pages = feed.proxy.read_all_items(timeout=1).by_page()
    feed.clock.now += 500
    feed.next_page(pages)
    feed.clock.now += 500
    feed.next_page(pages)
    assert [timeout for _, _, timeout in feed.calls] == pytest.approx([1, 1, 0.7])


def test_handle_initialization_is_in_page_budget_rust(feed):
    feed.init_delay = 1.1
    with pytest.raises(CosmosClientTimeoutError):
        feed.collect(feed.proxy.read_all_items(timeout=1))
    assert not feed.calls


def test_empty_pages_cannot_restart_budget_rust(feed):
    feed.pages = [[], [{"id": "late"}]]
    feed.delay = 0.6
    with pytest.raises(CosmosClientTimeoutError):
        feed.collect(feed.proxy.read_all_items(timeout=1))


def test_backend_is_pinned_at_iterator_creation_rust(feed):
    pager = feed.proxy.read_all_items()
    feed.proxy._item_context = ItemClientContext(MagicMock())
    feed.connection._backend = MagicMock()
    assert len(feed.collect(pager)) == 2


def test_internal_page_charges_accumulate_without_continuation_rust(feed):
    calls = []
    pager = feed.proxy.read_all_items(response_hook=lambda h, _: calls.append(h))
    pages = pager.by_page()
    feed.next_page(pages)
    feed.next_page(pages)
    assert float(calls[1]["x-ms-request-charge"]) == 4
    assert "x-ms-continuation" not in calls[1]
    assert "x-ms-continuation" not in pager.get_response_headers()


def test_empty_container_notifies_once_and_releases_cursor_rust(feed):
    feed.pages = [[], []]
    hook = MagicMock()
    pager = feed.proxy.read_all_items(response_hook=hook)
    pages = pager.by_page()
    with pytest.raises((StopIteration, StopAsyncIteration)):
        feed.next_page(pages)
    hook.assert_called_once()
    assert pages.state.cursor is None
    assert "x-ms-continuation" not in pager.get_response_headers()


def test_async_cancellation_drains_work_and_prevents_replay_rust(feed):
    if not feed.async_mode:
        pytest.skip("async cancellation")

    async def scenario():
        started, dropped = asyncio.Event(), asyncio.Event()

        async def slow(*args, **kwargs):
            started.set()
            try:
                await asyncio.Future()
            finally:
                dropped.set()

        feed.binding.fetch_page_with_cursor_async.side_effect = slow
        pages = feed.proxy.read_all_items(timeout=1).by_page()
        task = asyncio.create_task(pages.__anext__())
        await asyncio.wait_for(started.wait(), 1)
        with pytest.raises(RuntimeError, match="Concurrent use"):
            await pages.__anext__()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert dropped.is_set() and pages.state.cursor is None
        with pytest.raises(RuntimeError, match="pager failed"):
            await pages.__anext__()

    asyncio.run(scenario())


def test_hook_preserves_envelope_and_cannot_mutate_rows_rust(feed):
    calls = []
    original = feed.binding.fetch_page_with_cursor.side_effect

    def with_envelope(*args, **kwargs):
        status, substatus, headers, body, diagnostics = original(*args, **kwargs)
        envelope = json.loads(body)
        envelope.update(_rid="container-rid", _count=len(envelope["Documents"]))
        return status, substatus, headers, json.dumps(envelope).encode(), diagnostics

    feed.binding.fetch_page_with_cursor.side_effect = with_envelope
    feed.binding.fetch_page_with_cursor_async.side_effect = with_envelope

    def hook(headers, body):
        calls.append((body["_rid"], body["_count"]))
        if body["Documents"]:
            body["Documents"][0]["id"] = "hook-change"

    assert [row["id"] for row in feed.collect(feed.proxy.read_all_items(response_hook=hook))] == ["a", "b"]
    assert calls[:2] == [("container-rid", 1), ("container-rid", 1)]
