# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Read-all contracts through public sync/async wrappers and real adapters."""
from common.typed_requests import key_from_legacy_header

import asyncio
import inspect
import json
from types import MethodType, SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import _operation_deadline
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos._backend import rust as sync_rust
from azure.cosmos.aio._backend import rust as async_rust
from azure.cosmos._helpers import _read_all_items
from azure.cosmos._helpers._item_context import ItemClientContext, ItemClientDefaults
from azure.cosmos.exceptions import CosmosClientTimeoutError


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def feed(request, monkeypatch):
    async_mode = request.param
    clock = SimpleNamespace(now=100.0)
    clock.monotonic = lambda: clock.now
    monkeypatch.setattr(_read_all_items, "time", clock)
    monkeypatch.setattr(_operation_deadline, "time", clock)
    context = SimpleNamespace(
        clock=clock,
        calls=[],
        pages=[
            ([{"id": "a", "nested": [1]}], "c1.a"),
            ([], "c1.b"),
            ([{"id": "b"}], "c1.c"),
            ([], None),
        ],
        delay=0,
        init_delay=0,
        async_mode=async_mode,
        status=200,
    )

    def page(handle, prepared, cursor, *, timeout_seconds=None):
        context.calls.append((prepared, cursor, timeout_seconds))
        if timeout_seconds is not None and context.delay > timeout_seconds:
            raise TimeoutError("native page budget exhausted")
        clock.now += context.delay
        token = prepared.settings.query.continuation
        index = (
            0
            if token is None
            else next(i + 1 for i, (_, t) in enumerate(context.pages) if t == token)
        )
        rows, following = context.pages[index]
        headers = {"x-ms-request-charge": "2", "x-ms-session-token": "session"}
        if following is not None:
            headers["x-ms-continuation"] = following
        context.prepared = prepared
        return (
            context.status,
            0,
            headers,
            json.dumps({"Documents": rows}).encode(),
            None,
        )

    def ensure():
        clock.now += context.init_delay
        return "handle"

    module = async_rust if async_mode else sync_rust
    binding = SimpleNamespace(
        ItemFeedCursor=MagicMock(side_effect=object),
        read_all_items=MagicMock(),
        read_all_items_async=AsyncMock(),
        fetch_page_with_cursor=MagicMock(side_effect=page),
        fetch_page_with_cursor_async=AsyncMock(side_effect=page),
    )
    monkeypatch.setattr(module, "_rust_module", binding)
    backend_type = async_rust.AsyncRustBackend if async_mode else sync_rust.RustBackend
    backend = backend_type("https://read-all.invalid", master_key="ZmFrZQ==")
    monkeypatch.setattr(
        backend,
        "_ensure_driver_handle",
        AsyncMock(side_effect=ensure) if async_mode else MagicMock(side_effect=ensure),
    )
    connection = MagicMock()
    connection._backend = backend
    context.item_context = ItemClientContext(backend)
    context.proxy = (AsyncContainerProxy if async_mode else ContainerProxy)(
        connection,
        "dbs/db",
        "c",
        _item_context=context.item_context,
    )
    context.binding, context.connection, context.backend = binding, connection, backend

    def collect(pager):
        async def collect_async():
            return [row async for row in pager]

        return asyncio.run(collect_async()) if async_mode else list(pager)

    def next_page(pages):
        async def fetch():
            page = await pages.__anext__()
            return [row async for row in page]

        return asyncio.run(fetch()) if async_mode else list(next(pages))

    context.collect, context.next_page = collect, next_page
    yield context
    closed = backend.close()
    if inspect.isawaitable(closed):
        asyncio.run(closed)


@pytest.mark.parametrize("kwargs,priority,bucket", [
    ({}, "Low", 3),
    ({"priority": "High", "throughput_bucket": 5}, "High", 5),
])
def test_read_all_inherits_client_priority_defaults(feed, kwargs, priority, bucket):
    feed.proxy._item_context = ItemClientContext(
        feed.backend, ItemClientDefaults(priority="Low", throughput_bucket=3)
    )
    feed.collect(feed.proxy.read_all_items(**kwargs))
    assert all(p.settings.priority == priority for p, _, _ in feed.calls)
    assert all(p.settings.throughput_bucket == bucket for p, _, _ in feed.calls)


def test_complete_enumeration_retains_cursor_and_skips_empty_pages(feed):
    pager = feed.proxy.read_all_items(max_item_count=1)
    assert feed.calls == []
    assert feed.collect(pager) == [{"id": "a", "nested": [1]}, {"id": "b"}]
    assert len(feed.calls) == 4
    assert len({id(cursor) for _, cursor, _ in feed.calls}) == 1
    assert all(p.settings.query.max_item_count == 1 for p, _, _ in feed.calls)
    feed.connection.ReadItems.assert_not_called()


def test_resume_and_independent_pagers_ignore_global_headers(feed):
    first = feed.proxy.read_all_items().by_page()
    assert feed.next_page(first)[0]["id"] == "a"
    token = first.continuation_token
    feed.connection.last_response_headers = {"x-ms-continuation": "unrelated"}
    resumed = feed.proxy.read_all_items().by_page(continuation_token=token)
    assert feed.next_page(resumed) == [{"id": "b"}]
    assert feed.next_page(first) == [{"id": "b"}]
    assert feed.calls[0][1] is not feed.calls[1][1]
    assert feed.calls[0][1] is feed.calls[-1][1]


@pytest.mark.parametrize(
    "kwargs,error",
    [
        ({"populate_query_metrics": None}, TypeError),
        ({"populate_query_metrics": False}, TypeError),
        ({"populate_query_metrics": True}, TypeError),
        ({"max_item_count": 0}, ValueError),
        ({"max_item_count": -2}, ValueError),
        ({"max_item_count": True}, ValueError),
        ({"max_item_count": 1.5}, ValueError),
        ({"max_integrated_cache_staleness_in_ms": False}, ValueError),
        ({"max_integrated_cache_staleness_in_ms": -1}, ValueError),
        ({"timeout": float("nan")}, ValueError),
        ({"timeout": 0}, ValueError),
        ({"timeout": True}, ValueError),
        ({"response_hook": 4}, TypeError),
        ({"read_timeout": 2}, NotImplementedError),
        ({"availability_strategy": False}, NotImplementedError),
        ({"feed_range": {}}, NotImplementedError),
        ({"request_options": {"partitionKeyRangeId": "0"}}, NotImplementedError),
        ({"initial_headers": {"authorization": "override"}}, NotImplementedError),
        ({"continuation": "legacy"}, ValueError),
    ],
)
def test_invalid_or_unsupported_settings_fail_without_dispatch(feed, kwargs, error):
    with pytest.raises(error):
        feed.proxy.read_all_items(**kwargs)
    assert feed.calls == []


def test_positional_settings_rejected(feed):
    with pytest.raises(TypeError):
        feed.proxy.read_all_items(1)


@pytest.mark.parametrize("count", [None, -1, 1, 100])
def test_page_size_is_a_hint_not_total_limit(feed, count):
    assert len(feed.collect(feed.proxy.read_all_items(max_item_count=count))) == 2


def test_options_snapshotted_and_false_callback_isolated(feed):
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
    assert all(headers.get("x-ms-continuation") != "corrupt" for headers in calls)
    assert options == {"maxItemCount": 1, "initialHeaders": {"x-test": "after"}}


def test_hook_error_not_replayed_and_bookmark_not_advanced(feed):
    error = TimeoutError("customer callback")
    hook = MagicMock(side_effect=error)
    pages = feed.proxy.read_all_items(response_hook=hook).by_page()
    with pytest.raises(TimeoutError) as caught:
        feed.next_page(pages)
    assert caught.value is error
    assert pages.continuation_token is None
    with pytest.raises(RuntimeError, match="pager failed"):
        feed.next_page(pages)
    assert len(feed.calls) == 1
    hook.assert_called_once()


def test_new_budget_each_public_page_including_internal_empty_pages(feed):
    feed.delay = 0.3
    pages = feed.proxy.read_all_items(timeout=1).by_page()
    feed.clock.now += 500
    feed.next_page(pages)
    feed.clock.now += 500
    feed.next_page(pages)
    assert [timeout for _, _, timeout in feed.calls] == pytest.approx([1, 1, 0.7])


def test_handle_initialization_is_in_page_budget(feed):
    feed.init_delay = 1.1
    with pytest.raises(CosmosClientTimeoutError):
        feed.collect(feed.proxy.read_all_items(timeout=1))
    assert feed.calls == []


def test_internal_empty_pages_do_not_restart_budget(feed):
    feed.pages = [([], "c1.a"), ([{"id": "late"}], None)]
    feed.delay = 0.6
    with pytest.raises(CosmosClientTimeoutError):
        feed.collect(feed.proxy.read_all_items(timeout=1))


def test_backend_pinned_at_iterator_creation(feed):
    pager = feed.proxy.read_all_items()
    feed.proxy._item_context = ItemClientContext(MagicMock())
    feed.connection._backend = MagicMock()
    assert len(feed.collect(pager)) == 2


def test_wrong_backend_by_page_bookmark_rejected(feed):
    with pytest.raises(ValueError, match="incompatible backend"):
        feed.proxy.read_all_items().by_page(continuation_token="legacy")
    assert feed.calls == []


def test_internal_page_charges_accumulate_and_hook_failure_keeps_headers(feed):
    calls = []
    pager = feed.proxy.read_all_items(response_hook=lambda h, _: calls.append(h))
    pages = pager.by_page()
    feed.next_page(pages)
    feed.next_page(pages)
    assert float(calls[1]["x-ms-request-charge"]) == 4
    assert calls[1]["x-ms-continuation"] == "c1.c"
    assert pager.get_response_headers()["x-ms-continuation"] == "c1.c"


def test_hook_iteration_stop_is_a_failure_not_silent_exhaustion(feed):
    pages = feed.proxy.read_all_items(
        response_hook=MagicMock(side_effect=StopIteration("hook"))
    ).by_page()
    with pytest.raises(RuntimeError, match="response_hook"):
        feed.next_page(pages)
    with pytest.raises(RuntimeError, match="pager failed"):
        feed.next_page(pages)


def test_empty_container_hook_once_and_state_released(feed):
    feed.pages = [([], "c1.empty"), ([], None)]
    hook = MagicMock()
    pager = feed.proxy.read_all_items(response_hook=hook)
    pages = pager.by_page()
    feed.collect_pages = pages
    with pytest.raises((StopIteration, StopAsyncIteration)):
        feed.next_page(pages)
    hook.assert_called_once()
    assert pages.state.cursor is None
    assert "x-ms-continuation" not in pager.get_response_headers()


def test_async_cancellation_drains_work_and_prevents_replay(feed):
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
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert dropped.is_set()
        assert pages.state.cursor is None
        with pytest.raises(RuntimeError, match="pager failed"):
            await pages.__anext__()

    asyncio.run(scenario())


@pytest.fixture(params=[False, True], ids=["sync-legacy", "async-legacy"])
def legacy_feed(request, monkeypatch):
    from azure.cosmos._cosmos_client_connection import CosmosClientConnection
    from azure.cosmos.aio._cosmos_client_connection_async import (
        CosmosClientConnection as AsyncConnection,
    )
    from azure.cosmos._backend.legacy import LEGACY_BACKEND
    from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
    from azure.cosmos import _retry_utility
    from azure.cosmos.aio import _retry_utility_async

    async_mode = request.param
    cls = AsyncConnection if async_mode else CosmosClientConnection
    backend = ASYNC_LEGACY_BACKEND if async_mode else LEGACY_BACKEND
    connection = MagicMock()
    connection._backend = backend
    connection.ReadItems = MethodType(cls.ReadItems, connection)
    connection.QueryItems = MethodType(cls.QueryItems, connection)
    connection._CosmosClientConnection__container_properties_cache = {
        "dbs/db/colls/c": {"_rid": "rid"}
    }
    context = SimpleNamespace(calls=[], metadata=[], async_mode=async_mode)

    def metadata(options):
        context.metadata.append(dict(options))
        return {"_rid": "rid"}

    def fetch(*args, **kwargs):
        options = args[6]
        context.calls.append((dict(options), kwargs.get("_read_all_backend")))
        assert kwargs["_read_all_backend"] is backend
        token = options.get("continuation")
        rows, following = {
            None: ([{"id": "a"}], "legacy-a"),
            "legacy-a": ([], "legacy-empty"),
            "legacy-empty": ([{"id": "b"}], None),
        }[token]
        headers = CaseInsensitiveDict(
            {"x-ms-request-charge": "2", "etag": "not-a-bookmark"}
        )
        if following is not None:
            headers["x-ms-continuation"] = following
        kwargs["response_headers"].clear()
        kwargs["response_headers"].update(headers)
        kwargs["response_hook"](headers, {"Documents": rows})
        connection.last_response_headers = {"x-ms-continuation": "unrelated"}
        return rows if async_mode else (rows, headers)

    async def execute_async(_client, _manager, callback, **kwargs):
        return await callback()

    monkeypatch.setattr(
        _retry_utility, "Execute", lambda _c, _m, callback, **kw: callback()
    )
    monkeypatch.setattr(_retry_utility_async, "ExecuteAsync", execute_async)
    connection._CosmosClientConnection__QueryFeed = (
        AsyncMock(side_effect=fetch) if async_mode else fetch
    )
    context.proxy = (AsyncContainerProxy if async_mode else ContainerProxy)(
        connection,
        "dbs/db",
        "c",
        _item_context=ItemClientContext(backend),
    )
    context.proxy._get_properties_with_options = (
        AsyncMock(side_effect=metadata) if async_mode else metadata
    )

    def next_page(pages):
        async def fetch_page():
            page = await pages.__anext__()
            return [row async for row in page]

        return asyncio.run(fetch_page()) if async_mode else list(next(pages))

    context.next_page, context.connection = next_page, connection
    return context


def test_legacy_remains_lazy_pinned_and_uses_per_pager_bookmarks(legacy_feed):
    hook = MagicMock()
    options = {"maxItemCount": 1}
    pager = legacy_feed.proxy.read_all_items(
        request_options=options,
        read_timeout=2,
        availability_strategy=False,
        response_hook=hook,
    )
    pages = pager.by_page()
    assert legacy_feed.calls == legacy_feed.metadata == []
    assert legacy_feed.next_page(pages) == [{"id": "a"}]
    assert pages.continuation_token == "legacy-a"
    assert legacy_feed.next_page(pages) == [{"id": "b"}]
    assert pages.continuation_token is None
    assert len(legacy_feed.calls) == 3
    assert float(pager.get_response_headers()["x-ms-request-charge"]) == 4
    assert hook.call_count == 2
    assert options == {"maxItemCount": 1}


def test_legacy_rejects_driver_bookmarks_before_metadata(legacy_feed):
    with pytest.raises(ValueError, match="incompatible backend"):
        legacy_feed.proxy.read_all_items().by_page(continuation_token="c1.driver")
    assert legacy_feed.metadata == []


def test_legacy_resume_does_not_use_connection_headers(legacy_feed):
    pages = legacy_feed.proxy.read_all_items().by_page(continuation_token="legacy-a")
    assert legacy_feed.next_page(pages) == [{"id": "b"}]
    assert len(legacy_feed.calls) == 2


@pytest.mark.parametrize("method", ["fetch_page_with_cursor", "fetch_page_with_cursor_async"])
def test_compiled_page_entrypoint_rejects_legacy_token_without_io(method):
    from azure.cosmos._backend.request_settings import RequestSettings, QuerySettings

    native = pytest.importorskip("azure.cosmos._rust")
    prepared = SimpleNamespace(
        container_link="dbs/db/colls/c",
        protocol_version=3, partition_key=key_from_legacy_header("[]"),
        headers={},
        settings=RequestSettings(query=QuerySettings(continuation="legacy-bookmark")),
    )
    with pytest.raises(ValueError, match="Rust driver continuation"):
        getattr(native, method)("unused-handle", prepared, native.ItemFeedCursor())


def test_hook_preserves_envelope_fields_and_does_not_alias_rows(feed):
    calls = []
    original = (
        feed.binding.fetch_page_with_cursor_async.side_effect
        if feed.async_mode
        else feed.binding.fetch_page_with_cursor.side_effect
    )

    def with_envelope(*args, **kwargs):
        status, substatus, headers, body, diagnostics = original(*args, **kwargs)
        envelope = json.loads(body)
        envelope["_rid"] = "container-rid"
        envelope["_count"] = len(envelope["Documents"])
        return status, substatus, headers, json.dumps(envelope).encode(), diagnostics

    feed.binding.fetch_page_with_cursor.side_effect = with_envelope
    feed.binding.fetch_page_with_cursor_async.side_effect = with_envelope

    def hook(headers, body):
        calls.append((body["_rid"], body["_count"]))
        if body["Documents"]:
            body["Documents"][0]["id"] = "hook-change"

    rows = feed.collect(feed.proxy.read_all_items(response_hook=hook))
    assert [row["id"] for row in rows] == ["a", "b"]
    assert calls[:2] == [("container-rid", 1), ("container-rid", 1)]
