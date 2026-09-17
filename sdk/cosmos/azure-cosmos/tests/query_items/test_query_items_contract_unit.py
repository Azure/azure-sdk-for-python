# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Public query contracts through the real sync/async backend adapters."""
from common.typed_requests import wire_headers, settings_options, legacy_settings

import asyncio
import inspect
import hashlib
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from common.typed_requests import legacy_partition_key_from_request

from azure.cosmos import _operation_deadline
from azure.cosmos._backend import rust as sync_rust
from azure.cosmos.aio._backend import rust as async_rust
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos._helpers import _read_all_items
from azure.cosmos._helpers._item_context import ItemClientContext, ItemClientDefaults
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from azure.cosmos.partition_key import NonePartitionKeyValue, NullPartitionKeyValue


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def query(request, monkeypatch):
    async_mode = request.param
    clock = SimpleNamespace(now=100.0)
    clock.monotonic = lambda: clock.now
    monkeypatch.setattr(_read_all_items, "time", clock)
    monkeypatch.setattr(_operation_deadline, "time", clock)
    context = SimpleNamespace(
        calls=[],
        async_mode=async_mode,
        clock=clock,
        status=200,
        delay=0,
        resumable=True,
        failure=None,
        pages=[[{"id": "a", "nested": [1]}], [], [7, None, ["value"], "text"], None],
    )

    def cursor():
        return SimpleNamespace(index=0, has_more=False, continuation_supported=True)

    def page(handle, prepared, state, *, timeout_seconds=None):
        context.calls.append((prepared, state, timeout_seconds))
        if context.failure:
            raise context.failure
        if timeout_seconds is not None and context.delay > timeout_seconds:
            raise TimeoutError("query page timed out")
        clock.now += context.delay
        token = wire_headers(prepared).get("x-ms-continuation")
        if token is not None:
            state.index = int(token.removeprefix("c1."))
        rows = context.pages[state.index]
        state.index += 1
        state.has_more = rows is not None
        state.continuation_supported = context.resumable
        headers = {}
        if rows is not None:
            headers = {
                "x-ms-request-charge": "2",
                "x-ms-session-token": "session",
                "x-custom": "preserved",
            }
            if context.resumable:
                headers["x-ms-continuation"] = "c1." + str(state.index)
        return (
            context.status,
            0,
            headers,
            json.dumps({"Documents": rows or []}).encode(),
            None,
        )

    module = async_rust if async_mode else sync_rust
    binding = SimpleNamespace(
        ItemFeedCursor=MagicMock(side_effect=cursor),
        query_items=MagicMock(),
        query_items_async=AsyncMock(),
        fetch_page_with_cursor=MagicMock(side_effect=page),
        fetch_page_with_cursor_async=AsyncMock(side_effect=page),
    )
    monkeypatch.setattr(module, "_rust_module", binding)
    cls = async_rust.AsyncRustBackend if async_mode else sync_rust.RustBackend
    backend = cls("https://queries.invalid", master_key="ZmFrZQ==")
    monkeypatch.setattr(
        backend,
        "_ensure_driver_handle",
        (
            AsyncMock(return_value="handle")
            if async_mode
            else MagicMock(return_value="handle")
        ),
    )
    connection = MagicMock()
    connection._backend = backend
    context.proxy = (AsyncContainerProxy if async_mode else ContainerProxy)(
        connection,
        "dbs/db",
        "c",
        _item_context=ItemClientContext(
            backend, ItemClientDefaults(priority="Low", throughput_bucket=3)
        ),
    )
    context.connection, context.binding, context.backend = connection, binding, backend

    def collect(pager):
        async def run():
            return [row async for row in pager]

        return asyncio.run(run()) if async_mode else list(pager)

    def next_page(pages):
        async def run():
            return [row async for row in await pages.__anext__()]

        return asyncio.run(run()) if async_mode else list(next(pages))

    context.collect, context.next_page = collect, next_page
    yield context
    closed = backend.close()
    if inspect.isawaitable(closed):
        asyncio.run(closed)


def test_cursor_is_lazy_per_iterator_and_released_at_completion(query):
    pager = query.proxy.query_items("SELECT * FROM c")
    first, second = pager.by_page(), pager.by_page()
    assert first.state.cursor is second.state.cursor is None
    query.binding.ItemFeedCursor.assert_not_called()
    query.backend._ensure_driver_handle.assert_not_called()

    query.next_page(first)
    cursor = first.state.cursor
    query.next_page(second)
    assert second.state.cursor is not cursor
    assert cursor is not None
    assert query.binding.ItemFeedCursor.call_count == 2
    query.next_page(first)
    assert first.state.cursor is cursor
    assert query.calls[-1][1] is cursor
    with pytest.raises((StopIteration, StopAsyncIteration)):
        query.next_page(first)
    assert first.state.cursor is None
    assert second.state.cursor is not None
    assert query.binding.ItemFeedCursor.call_count == 2


@pytest.mark.parametrize("interval", [None, ("00", "FF")])
def test_typed_scope_keeps_the_previous_bookmark_identity(query, interval):
    kwargs = (
        {}
        if interval is None
        else {"feed_range": {"Range": {"min": interval[0], "max": interval[1]}}}
    )
    pager = query.proxy.query_items("SELECT * FROM c", **kwargs)
    config = pager.by_page().state.config
    previous_identity_input = [
        query.backend._endpoint,
        query.proxy.container_link,
        "SELECT * FROM c",
        [],
        {
            "feed_range": list(interval) if interval is not None else None,
            "allow_cross_partition": True,
            "partition_key": None,
        },
    ]
    expected = hashlib.sha256(
        json.dumps(
            previous_identity_input,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
    assert config.identity == expected
    assert config.scope.feed_range == interval
    query.binding.ItemFeedCursor.assert_not_called()


def test_complete_iteration_scalar_results_and_no_legacy_metadata(query):
    pager = query.proxy.query_items("SELECT VALUE c.value FROM c", max_item_count=1)
    assert query.calls == []
    query.binding.ItemFeedCursor.assert_not_called()
    assert query.collect(pager) == [
        {"id": "a", "nested": [1]},
        7,
        None,
        ["value"],
        "text",
    ]
    assert len(query.calls) == 4
    assert len({id(cursor) for _, cursor, _ in query.calls}) == 1
    query.connection.QueryItems.assert_not_called()
    query.connection.ReadContainer.assert_not_called()
    query.binding.query_items.assert_not_called()
    query.binding.query_items_async.assert_not_called()


def test_bookmarks_resume_independently_and_bind_query_and_scope(query):
    pages = query.proxy.query_items("SELECT * FROM c").by_page()
    assert query.next_page(pages)[0]["id"] == "a"
    bookmark = pages.continuation_token
    assert bookmark.startswith("q1.")
    query.connection.last_response_headers = {"x-ms-continuation": "unrelated"}
    resumed = query.proxy.query_items("SELECT * FROM c", max_item_count=50).by_page(
        continuation_token=bookmark
    )
    assert query.next_page(resumed) == [7, None, ["value"], "text"]
    assert query.next_page(pages) == [7, None, ["value"], "text"]
    assert query.calls[0][1] is not query.calls[1][1]
    assert query.calls[0][1] is query.calls[-1][1]
    for kwargs in [
        {"query": "SELECT c.id FROM c"},
        {"query": "SELECT * FROM c", "partition_key": "other"},
        {"query": "SELECT * FROM c", "parameters": [{"name": "@p", "value": 2}]},
    ]:
        with pytest.raises(ValueError, match="bookmark"):
            query.proxy.query_items(**kwargs).by_page(continuation_token=bookmark)


def test_nonresumable_queries_enumerate_but_bookmark_access_raises(query):
    query.resumable = False
    pages = query.proxy.query_items("SELECT DISTINCT VALUE c.value FROM c").by_page()
    assert query.next_page(pages)[0]["id"] == "a"
    with pytest.raises(NotImplementedError, match="bookmark"):
        _ = pages.continuation_token
    assert query.next_page(pages) == [7, None, ["value"], "text"]
    with pytest.raises((StopIteration, StopAsyncIteration)):
        query.next_page(pages)
    assert len(query.calls) == 4


@pytest.mark.parametrize(
    "key,expected",
    [
        (None, None),
        ("tenant", '["tenant"]'),
        (False, "[false]"),
        (0, "[0]"),
        (NullPartitionKeyValue, "[null]"),
        (NonePartitionKeyValue, "[{}]"),
        (["tenant"], '["tenant"]'),
        (["tenant", None], '["tenant",null]'),
        (["tenant", NonePartitionKeyValue], '["tenant",{}]'),
    ],
)
def test_partition_scope_normalization(query, key, expected):
    query.collect(query.proxy.query_items("SELECT * FROM c", partition_key=key))
    prepared = query.calls[0][0]
    actual = legacy_partition_key_from_request(prepared) if prepared.partition_key.kind == "components" else None
    assert actual == expected
    assert "partition_key" not in json.loads(prepared.body_bytes)


@pytest.mark.parametrize("key,wire", [
    (None, None), (False, "[false]"), (NonePartitionKeyValue, "[{}]"),
    (NullPartitionKeyValue, "[null]"), (["tenant", None], '["tenant",null]'),
])
def test_existing_query_bookmark_identity_is_unchanged(query, key, wire):
    import hashlib
    from azure.cosmos._helpers._query_items import QueryConfig

    config = QueryConfig(query.proxy, {"query": "SELECT * FROM c", "partition_key": key})
    original_scope = {
        "partition_key": wire, "feed_range": None, "allow_cross_partition": True,
    }
    original = json.dumps(
        [config.backend._endpoint, query.proxy.container_link, config.query, config.parameters, original_scope],
        sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()
    assert config.identity == hashlib.sha256(original).hexdigest()


def test_query_body_scope_options_and_client_defaults_are_preserved(query):
    params = [{"name": "@v", "value": [1, 2]}]
    feed = {"Range": {"min": "", "max": "AA"}}
    headers = {"x-custom-request": "before"}
    pager = query.proxy.query_items(
        "SELECT TOP 2 * FROM c ORDER BY VectorDistance(c.v, @v)",
        parameters=params,
        feed_range=feed,
        initial_headers=headers,
        populate_query_metrics=True,
        populate_index_metrics=False,
        populate_query_advice=True,
        enable_scan_in_query=True,
        availability_strategy=False,
        excluded_locations=["East US"],
        max_item_count=2,
        session_token="session",
        max_integrated_cache_staleness_in_ms=0,
    )
    params[0]["value"].append(3)
    feed["Range"]["max"] = "BB"
    headers["x-custom-request"] = "after"
    query.collect(pager)
    prepared = query.calls[0][0]
    body = json.loads(prepared.body_bytes)
    assert body["query"]["parameters"] == [{"name": "@v", "value": [1, 2]}]
    assert body["feed_range"] == ["", "AA"]
    assert wire_headers(prepared)["x-custom-request"] == "before"
    assert wire_headers(prepared)["x-ms-documentdb-populatequerymetrics"] == "True"
    assert "x-ms-cosmos-populateindexmetrics" not in wire_headers(prepared)
    assert wire_headers(prepared)["x-ms-cosmos-populatequeryadvice"] == "True"
    assert wire_headers(prepared)["x-ms-cosmos-priority-level"] == "Low"
    assert wire_headers(prepared)["x-ms-cosmos-throughput-bucket"] == "3"
    assert settings_options(prepared)["availabilityStrategy"] == "disabled"
    assert settings_options(prepared)["excludedLocations"] == ["East US"]


@pytest.mark.parametrize(
    "kwargs,error",
    [
        ({"query": None}, ValueError),
        ({"query": ""}, ValueError),
        ({"parameters": [{"name": "bad", "value": 1}]}, ValueError),
        ({"parameters": [{"name": "@p", "value": float("nan")}]}, ValueError),
        ({"partition_key": []}, ValueError),
        ({"partition_key": float("inf")}, ValueError),
        (
            {"partition_key": "a", "feed_range": {"Range": {"min": "", "max": "FF"}}},
            ValueError,
        ),
        ({"feed_range": {}}, ValueError),
        ({"enable_cross_partition_query": "false"}, TypeError),
        ({"timeout": 0.5}, ValueError),
        ({"max_item_count": 0}, ValueError),
        ({"max_item_count": True}, ValueError),
        ({"populate_query_metrics": 1}, TypeError),
        ({"full_text_score_scope": "Invalid"}, ValueError),
        ({"full_text_score_scope": "Local"}, NotImplementedError),
        ({"full_text_score_scope": "Global"}, NotImplementedError),
        ({"continuation_token_limit": -1}, ValueError),
        ({"continuation_token_limit": 1}, NotImplementedError),
        ({"read_timeout": 1}, NotImplementedError),
        ({"availability_strategy": "True"}, TypeError),
        ({"initial_headers": {"X-MS-Start-EPK": "00"}}, NotImplementedError),
        ({"initial_headers": {"Authorization": "override"}}, NotImplementedError),
        ({"request_options": {"partitionKeyRangeId": "0"}}, NotImplementedError),
        ({"unknown_option": 1}, NotImplementedError),
        ({"continuation": "legacy"}, ValueError),
        ({"continuation": "c1.raw"}, ValueError),
        ({"continuation": "q1.invalid"}, ValueError),
        ({"continuation": "cf1.feed"}, ValueError),
    ],
)
def test_invalid_or_unsupported_arguments_fail_without_dispatch(query, kwargs, error):
    values = {"query": "SELECT * FROM c", **kwargs}
    with pytest.raises(error):
        query.proxy.query_items(**values)
    assert not query.calls
    query.connection.QueryItems.assert_not_called()


def test_empty_pages_share_deadline_and_preserve_hook_accounting(query):
    query.pages = [[], [{"id": "a"}], None]
    query.delay = 0.3
    calls = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            calls.append((dict(headers), dict(body)))
            headers["x-ms-continuation"] = "corrupt"
            body["Documents"].clear()

    pager = query.proxy.query_items("SELECT * FROM c", timeout=1, response_hook=Hook())
    assert query.collect(pager) == [{"id": "a"}]
    assert len(calls) == 1
    assert calls[0][0]["x-ms-request-charge"] == "4.0"
    assert calls[0][0]["x-custom"] == "preserved"
    assert calls[0][0]["x-ms-continuation"].startswith("q1.")
    assert query.calls[1][2] == pytest.approx(0.7)


def test_errors_do_not_replay_and_keep_last_delivered_bookmark(query):
    pages = query.proxy.query_items("SELECT * FROM c").by_page()
    query.next_page(pages)
    previous = pages.continuation_token
    query.failure = NotImplementedError("unsupported query feature")
    with pytest.raises(NotImplementedError):
        query.next_page(pages)
    assert pages.continuation_token == previous
    with pytest.raises(RuntimeError, match="failed"):
        query.next_page(pages)
    assert len(query.calls) == 2
    query.connection.QueryItems.assert_not_called()


def test_timeout_and_service_error_surface(query):
    query.delay = 2
    with pytest.raises(CosmosClientTimeoutError):
        query.collect(query.proxy.query_items("SELECT * FROM c", timeout=1))
    query.delay, query.status = 0, 429
    with pytest.raises(CosmosHttpResponseError) as error:
        query.collect(query.proxy.query_items("SELECT * FROM c"))
    assert error.value.status_code == 429


def test_hook_failure_does_not_advance_public_bookmark(query):
    def hook(headers, body):
        raise ValueError("hook failed")

    pages = query.proxy.query_items("SELECT * FROM c", response_hook=hook).by_page()
    with pytest.raises(ValueError, match="hook failed"):
        query.next_page(pages)
    assert pages.continuation_token is None
    with pytest.raises(RuntimeError, match="failed"):
        query.next_page(pages)


def test_core_python_public_query_stays_on_legacy_and_rejects_rust_tokens(query):
    query.proxy._item_context = None
    query.connection._backend = SimpleNamespace(name="core-python")
    query.proxy._get_properties_with_options = MagicMock(
        return_value={
            "_rid": "rid",
            "partitionKey": {"paths": ["/pk"], "kind": "Hash", "version": 2},
        }
    )
    result = query.proxy.query_items("SELECT * FROM c", read_timeout=5)
    assert result is query.connection.QueryItems.return_value
    assert not query.calls
    with pytest.raises(ValueError, match="incompatible"):
        query.proxy.query_items("SELECT * FROM c", continuation="q1.saved")
    iterable = (
        __import__(
            "azure.cosmos.aio._query_iterable_async", fromlist=["QueryIterable"]
        ).QueryIterable
        if query.async_mode
        else __import__(
            "azure.cosmos._query_iterable", fromlist=["QueryIterable"]
        ).QueryIterable
    )
    with pytest.raises(ValueError, match="incompatible"):
        iterable(query.connection, "SELECT * FROM c", {}, continuation_token="q1.saved")


def test_query_advice_and_index_headers_are_decoded_before_hooks(query, monkeypatch):
    from azure.cosmos._helpers import _query_items

    monkeypatch.setattr(
        _query_items._utils, "get_index_metrics_info", lambda value: "index:" + value
    )
    monkeypatch.setattr(
        _query_items, "get_query_advice_info", lambda value: "advice:" + value
    )
    method = (
        query.binding.fetch_page_with_cursor_async
        if query.async_mode
        else query.binding.fetch_page_with_cursor
    )
    original = method.side_effect

    def page(*args, **kwargs):
        result = original(*args, **kwargs)
        if result[2]:
            result[2]["x-ms-cosmos-index-utilization"] = "raw"
            result[2]["x-ms-cosmos-query-advice"] = "raw"
        return result

    method.side_effect = page
    calls = []
    pager = query.proxy.query_items(
        "SELECT * FROM c",
        response_hook=lambda headers, body: calls.append(dict(headers)),
    )
    query.collect(pager)
    assert calls[0]["x-ms-cosmos-index-utilization"] == "index:raw"
    assert calls[0]["x-ms-cosmos-query-advice"] == "advice:raw"
    assert (
        query.proxy._item_context.response_state.last_response_headers[
            "x-ms-cosmos-query-advice"
        ]
        == "advice:raw"
    )


def test_driver_initialization_consumes_public_page_budget(query, monkeypatch):
    def ensure():
        query.clock.now += 2
        return "handle"

    monkeypatch.setattr(
        query.backend,
        "_ensure_driver_handle",
        (
            AsyncMock(side_effect=ensure)
            if query.async_mode
            else MagicMock(side_effect=ensure)
        ),
    )
    with pytest.raises(CosmosClientTimeoutError):
        query.collect(query.proxy.query_items("SELECT * FROM c", timeout=1))
    assert not query.calls


def test_async_query_cancellation_invalidates_cursor_without_replay(query):
    if not query.async_mode:
        return

    async def run():
        entered = asyncio.Event()
        blocker = asyncio.Event()

        async def blocked(*args, **kwargs):
            entered.set()
            await blocker.wait()

        query.binding.fetch_page_with_cursor_async.side_effect = blocked
        pages = query.proxy.query_items("SELECT * FROM c").by_page()
        task = asyncio.create_task(pages.__anext__())
        await entered.wait()
        with pytest.raises(RuntimeError, match="Concurrent"):
            await pages.__anext__()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        with pytest.raises(RuntimeError, match="failed"):
            await pages.__anext__()
        assert pages.continuation_token is None
        assert pages.state.cursor is None

    asyncio.run(run())
    query.connection.QueryItems.assert_not_called()


def test_service_error_carries_last_delivered_public_bookmark(query):
    pages = query.proxy.query_items("SELECT * FROM c").by_page()
    query.next_page(pages)
    bookmark = pages.continuation_token
    query.status = 429
    with pytest.raises(CosmosHttpResponseError) as error:
        query.next_page(pages)
    assert error.value.continuation_token == bookmark
    assert pages.continuation_token == bookmark


def test_enabled_request_hedging_uses_client_threshold(query, monkeypatch):
    from azure.cosmos._backend.contracts import PreparedClientConfig

    with monkeypatch.context() as patch:
        patch.setattr(
            query.backend,
            "_client_config",
            PreparedClientConfig(hedging_threshold_ms=250),
        )
        query.collect(
            query.proxy.query_items("SELECT * FROM c", availability_strategy=True)
        )
    assert settings_options(query.calls[0][0])["availabilityStrategy"] == "enabled:250"


def test_invalid_header_name_and_non_document_envelope_fail_explicitly(query):
    with pytest.raises(TypeError, match="names must be strings"):
        query.proxy.query_items("SELECT * FROM c", initial_headers={1: "value"})
    method = (
        query.binding.fetch_page_with_cursor_async
        if query.async_mode
        else query.binding.fetch_page_with_cursor
    )
    method.side_effect = lambda *args, **kwargs: (200, 0, {}, b'{"Documents":{}}', None)
    with pytest.raises(ValueError, match="query_items.*invalid Documents"):
        query.collect(query.proxy.query_items("SELECT * FROM c", read_timeout=None))
