# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Public change-feed paging contracts without account access."""

import asyncio
import base64
import json
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from common.typed_requests import legacy_partition_key_from_request

from azure.cosmos import _retry_utility
from azure.cosmos.aio import _retry_utility_async
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy
from azure.cosmos._helpers._change_feed import ChangeFeedPageState
from azure.cosmos._helpers._item_context import ItemClientContext
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from azure.cosmos.partition_key import NonePartitionKeyValue
from read_all_items.test_read_all_items_contract_unit import feed as base_feed


@pytest.fixture
def feed(base_feed):
    base_feed.pages = [
        (
            [
                {
                    "current": {"id": "a", "nested": [1]},
                    "metadata": {"operationType": "create"},
                }
            ],
            "c1.a",
        ),
        ([], "c1.b"),
        ([{"current": {"id": "b"}}], "c1.c"),
        ([], "c1.d"),
    ]
    return base_feed


@pytest.mark.parametrize("status", [429, 503])
def test_initial_setup_service_error_can_retry_same_page_iterator(feed, status):
    hooks = []
    pages = feed.proxy.query_items_change_feed(
        response_hook=lambda headers, body: hooks.append(body)
    ).by_page()
    feed.setup_status = status
    with pytest.raises(CosmosHttpResponseError) as caught:
        feed.next_page(pages)
    assert caught.value.status_code == status
    cursor = pages.state.cursor
    assert cursor is not None and not pages.state.failed
    assert pages.continuation_token is None
    assert hooks == []
    feed.setup_status = 0
    assert feed.next_page(pages) == [{"id": "a", "nested": [1]}]
    assert feed.calls[0][1] is feed.calls[1][1] is cursor
    assert len(hooks) == 1


def test_first_execution_service_error_still_invalidates(feed):
    feed.status = 503
    pages = feed.proxy.query_items_change_feed().by_page()
    with pytest.raises(CosmosHttpResponseError):
        feed.next_page(pages)
    assert pages.state.cursor is None
    with pytest.raises(RuntimeError, match="pager failed"):
        feed.next_page(pages)
    assert len(feed.calls) == 1


def test_caught_up_page_publishes_bookmark_and_new_pager_polls_again(feed):
    calls = []
    pager = feed.proxy.query_items_change_feed(
        response_hook=lambda h, b: calls.append((h, b))
    )
    pages = pager.by_page()
    assert feed.calls == []
    assert feed.next_page(pages) == [{"id": "a", "nested": [1]}]
    first_token = pages.continuation_token
    feed.status = 304
    assert feed.next_page(pages) == []
    caught_up = pages.continuation_token
    assert caught_up != first_token and caught_up.startswith("cf1.")
    with pytest.raises((StopIteration, StopAsyncIteration)):
        feed.next_page(pages)
    assert len(feed.calls) == len(calls) == 2
    assert calls[-1][0]["etag"] == caught_up
    assert pager.get_response_headers()["x-ms-continuation"] == caught_up
    feed.status = 200
    resumed = feed.proxy.query_items_change_feed(continuation=caught_up).by_page()
    assert feed.next_page(resumed) == [{"id": "b"}]
    assert feed.calls[-1][0].settings.query.continuation == "c1.b"
    assert feed.calls[0][1] is feed.calls[1][1]
    assert feed.calls[0][1] is not feed.calls[2][1]


def test_existing_change_feed_bookmark_restores_a_typed_key(feed):
    payload = {
        "backend": "rust", "container": feed.proxy.container_link, "token": "c1.a",
        "settings": {
            "mode": "LatestVersion", "start": "Now",
            "partition_key": "[false]", "feed_range": None,
        },
    }
    old_token = "cf1." + base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode().rstrip("=")
    pages = feed.proxy.query_items_change_feed(continuation=old_token).by_page()
    feed.next_page(pages)
    assert feed.calls[-1][0].partition_key.values == (False,)
    assert "partition_key" not in json.loads(feed.calls[-1][0].body_bytes)


@pytest.mark.parametrize("mode", ["LatestVersion", "AllVersionsAndDeletes"])
def test_both_modes_and_authoritative_resume(feed, mode):
    pages = feed.proxy.query_items_change_feed(mode=mode, partition_key=False).by_page()
    rows = feed.next_page(pages)
    assert rows == (
        [{"id": "a", "nested": [1]}] if mode == "LatestVersion" else feed.pages[0][0]
    )
    resumed = feed.proxy.query_items_change_feed(
        continuation=pages.continuation_token,
        mode="invalid",
        start_time=42,
        partition_key={"invalid": True},
        feed_range={"invalid": True},
    ).by_page()
    assert feed.next_page(resumed) == []
    request = json.loads(feed.calls[-1][0].body_bytes)
    assert request == {
        "mode": mode,
        "start": "Now",
        "feed_range": None,
    }


@pytest.mark.parametrize(
    "key,wire",
    [
        (None, "[null]"),
        (False, "[false]"),
        (0, "[0]"),
        ("", '[""]'),
        (["a", 0, None], '["a",0,null]'),
        (NonePartitionKeyValue, "[{}]"),
    ],
)
def test_partition_scope_roundtrips(feed, key, wire):
    pages = feed.proxy.query_items_change_feed(partition_key=key).by_page()
    feed.next_page(pages)
    assert legacy_partition_key_from_request(feed.calls[-1][0]) == wire
    assert "partition_key" not in json.loads(feed.calls[-1][0].body_bytes)
    resumed = feed.proxy.query_items_change_feed(
        continuation=pages.continuation_token
    ).by_page()
    feed.next_page(resumed)
    assert legacy_partition_key_from_request(feed.calls[-1][0]) == wire


@pytest.mark.parametrize(
    "start", ["Now", "now", "Beginning", datetime(2025, 1, 2, tzinfo=timezone.utc)]
)
def test_start_and_feed_range_roundtrip(feed, start):
    scope = {
        "Range": {
            "min": "",
            "max": "FF",
            "isMinInclusive": True,
            "isMaxInclusive": False,
        }
    }
    pages = feed.proxy.query_items_change_feed(
        start_time=start, feed_range=scope
    ).by_page()
    feed.next_page(pages)
    prepared = json.loads(feed.calls[-1][0].body_bytes)
    assert prepared["feed_range"] == ["", "FF"]
    resumed = feed.proxy.query_items_change_feed(
        continuation=pages.continuation_token
    ).by_page()
    feed.next_page(resumed)
    assert json.loads(feed.calls[-1][0].body_bytes) == prepared


@pytest.mark.parametrize(
    "kwargs,error",
    [
        ({"max_item_count": 0}, ValueError),
        ({"max_item_count": True}, ValueError),
        ({"max_item_count": -2}, ValueError),
        ({"timeout": False}, ValueError),
        ({"start_time": 42}, ValueError),
        ({"mode": ""}, ValueError),
        ({"mode": "AllVersionsAndDeletes", "start_time": "Beginning"}, ValueError),
        ({"partition_key": {}, "feed_range": {}}, ValueError),
        ({"partition_key": []}, ValueError),
        ({"partition_key": float("nan")}, ValueError),
        ({"feed_range": {"Range": {"min": "FF", "max": ""}}}, ValueError),
        ({"availability_strategy": False}, NotImplementedError),
        ({"initial_headers": {"if-none-match": "42"}}, NotImplementedError),
        ({"continuation": "c1.query"}, ValueError),
        ({"continuation": "42"}, ValueError),
        ({"continuation": "cf1.invalid"}, ValueError),
    ],
)
def test_invalid_inputs_never_dispatch(feed, kwargs, error):
    with pytest.raises(error):
        feed.proxy.query_items_change_feed(**kwargs).by_page()
    assert feed.calls == []


def test_keyword_only_and_deprecated_keywords(feed):
    with pytest.raises(TypeError):
        feed.proxy.query_items_change_feed("0")
    with pytest.warns(DeprecationWarning):
        pages = feed.proxy.query_items_change_feed(
            is_start_from_beginning=True
        ).by_page()
    feed.next_page(pages)
    assert json.loads(feed.calls[-1][0].body_bytes)["start"] == "Beginning"
    with pytest.warns(DeprecationWarning), pytest.raises(NotImplementedError):
        feed.proxy.query_items_change_feed(partition_key_range_id="0").by_page()


def test_hook_and_options_are_isolated_and_false_hook_is_called(feed):
    options = {"maxItemCount": 1, "initialHeaders": {"x-test": "before"}}
    calls = []

    class Hook:
        def __bool__(self):
            return False

        def clear(self):
            raise AssertionError("must not clear customer state")

        def __call__(self, headers, body):
            calls.append(dict(headers))
            headers.clear()
            body["Documents"][0]["nested"].append(99)

    pager = feed.proxy.query_items_change_feed(
        request_options=options, response_hook=Hook()
    )
    assert options == {"maxItemCount": 1, "initialHeaders": {"x-test": "before"}}
    options["initialHeaders"]["x-test"] = "after"
    assert feed.next_page(pager.by_page()) == [{"id": "a", "nested": [1]}]
    assert len(calls) == 1
    assert feed.calls[0][0].headers["x-test"] == "before"


def test_hook_failure_does_not_advance_public_bookmark_or_replay(feed):
    def hook(_headers, body):
        if not body["Documents"]:
            raise ValueError("customer callback")

    pages = feed.proxy.query_items_change_feed(response_hook=hook).by_page()
    feed.next_page(pages)
    token = pages.continuation_token
    with pytest.raises(ValueError, match="customer callback"):
        feed.next_page(pages)
    assert pages.continuation_token == token
    with pytest.raises(RuntimeError, match="pager failed"):
        feed.next_page(pages)
    assert len(feed.calls) == 2


def test_deadline_is_page_local_and_failure_safe(feed):
    pages = feed.proxy.query_items_change_feed(timeout=2).by_page()
    feed.init_delay = 0.25
    feed.next_page(pages)
    assert feed.calls[-1][2] == 1.75
    token = pages.continuation_token
    feed.clock.now += 100
    feed.delay = 3
    with pytest.raises(CosmosClientTimeoutError):
        feed.next_page(pages)
    assert pages.continuation_token == token
    with pytest.raises(RuntimeError, match="pager failed"):
        feed.next_page(pages)


@pytest.fixture(params=[False, True], ids=["legacy-sync", "legacy-async"])
def legacy(request, monkeypatch):
    async_mode = request.param
    context = SimpleNamespace(calls=[], pages=[[{"id": "a"}], [], [{"id": "b"}], []])
    connection = MagicMock()
    backend = SimpleNamespace(name="core-python")
    connection._backend = backend
    proxy = (AsyncContainerProxy if async_mode else ContainerProxy)(
        connection, "dbs/db", "c", _item_context=ItemClientContext(backend)
    )
    properties = {
        "_rid": "rid",
        "partitionKey": {"paths": ["/pk"], "kind": "Hash", "version": 2},
    }
    metadata = (
        AsyncMock(return_value=properties)
        if async_mode
        else MagicMock(return_value=properties)
    )
    monkeypatch.setattr(proxy, "_get_properties_with_options", metadata)

    def fetch(path, container, query, options, response_hook, **kwargs):
        context.calls.append(dict(options))
        rows = context.pages[len(context.calls) - 1]
        headers = {
            "etag": '"' + str(len(context.calls)) + '"',
            "x-ms-request-charge": "1",
        }
        response_hook(headers, {"Documents": rows})
        connection.last_response_headers = {"etag": "unrelated"}
        return rows if async_mode else (rows, headers)

    connection.QueryFeed = (
        AsyncMock(side_effect=fetch) if async_mode else MagicMock(side_effect=fetch)
    )
    monkeypatch.setattr(
        _retry_utility, "Execute", lambda _c, _m, callback, **kw: callback(**kw)
    )

    async def execute(_c, _m, callback, **kw):
        return await callback(**kw)

    monkeypatch.setattr(_retry_utility_async, "ExecuteAsync", execute)

    def next_page(pages):
        async def read():
            page = await pages.__anext__()
            return [row async for row in page]

        return asyncio.run(read()) if async_mode else list(next(pages))

    context.proxy, context.next_page, context.metadata = proxy, next_page, metadata
    context.connection, context.async_mode = connection, async_mode
    return context


@pytest.mark.parametrize("mode", ["LatestVersion", "AllVersionsAndDeletes"])
@pytest.mark.parametrize("key", [None, False, 0, ""])
def test_legacy_modes_empty_checkpoint_and_authoritative_resume(legacy, mode, key):
    options = {"maxItemCount": 1}
    pager = legacy.proxy.query_items_change_feed(
        mode=mode, partition_key=key, request_options=options
    )
    legacy.metadata.assert_not_called()
    assert options == {"maxItemCount": 1}
    pages = pager.by_page()
    assert legacy.next_page(pages) == [{"id": "a"}]
    assert legacy.next_page(pages) == []
    token = pages.continuation_token
    decoded = json.loads(base64.b64decode(token))
    assert decoded["mode"] == mode
    with pytest.raises((StopIteration, StopAsyncIteration)):
        legacy.next_page(pages)
    resumed = legacy.proxy.query_items_change_feed(
        continuation=token, mode="invalid", start_time=42, feed_range={"invalid": True}
    ).by_page()
    assert legacy.next_page(resumed) == [{"id": "b"}]
    state = legacy.calls[-1]["changeFeedState"]
    assert state._mode == mode
    assert state._feed_range._pk_value == key


def test_cross_backend_tokens_rejected(feed, legacy):
    pages = feed.proxy.query_items_change_feed().by_page()
    feed.next_page(pages)
    with pytest.raises(ValueError, match="incompatible backend"):
        legacy.proxy.query_items_change_feed(
            continuation=pages.continuation_token
        ).by_page()
    core_pages = legacy.proxy.query_items_change_feed().by_page()
    legacy.next_page(core_pages)
    with pytest.raises(ValueError, match="incompatible backend"):
        feed.proxy.query_items_change_feed(
            continuation=core_pages.continuation_token
        ).by_page()


def test_avad_delete_record_is_not_unwrapped(feed):
    record = {"previous": {"id": "deleted"}, "metadata": {"operationType": "delete"}}
    feed.pages[0] = ([record], "c1.a")
    pages = feed.proxy.query_items_change_feed(mode="AllVersionsAndDeletes").by_page()
    assert feed.next_page(pages) == [record]


def test_invalid_latest_envelope_poisoned_without_checkpoint(feed):
    feed.pages[0] = ([{"id": "unstructured"}], "c1.a")
    pages = feed.proxy.query_items_change_feed().by_page()
    with pytest.raises(ValueError, match="without current"):
        feed.next_page(pages)
    assert pages.continuation_token is None
    with pytest.raises(RuntimeError, match="pager failed"):
        feed.next_page(pages)


def test_iteration_stop_hook_is_not_silent_exhaustion(feed):
    def hook(_headers, _body):
        raise StopIteration("callback")

    pages = feed.proxy.query_items_change_feed(response_hook=hook).by_page()
    with pytest.raises(RuntimeError, match="iteration-stop"):
        feed.next_page(pages)
    assert pages.continuation_token is None


def test_async_cancellation_and_concurrent_fetch_are_failure_safe(feed):
    if not feed.async_mode:
        pytest.skip("async cancellation")

    async def run():
        pages = feed.proxy.query_items_change_feed().by_page()
        await pages.__anext__()
        token = pages.continuation_token
        started, cancelled = asyncio.Event(), asyncio.Event()

        async def blocked(*args, **kwargs):
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        feed.binding.fetch_page_with_cursor_async = AsyncMock(side_effect=blocked)
        pending = asyncio.create_task(pages.__anext__())
        await asyncio.wait_for(started.wait(), timeout=5)
        with pytest.raises(RuntimeError, match="Concurrent"):
            await pages.__anext__()
        pending.cancel()
        with pytest.raises(asyncio.CancelledError):
            await pending
        assert cancelled.is_set()
        assert pages.continuation_token == token
        with pytest.raises(RuntimeError, match="pager failed"):
            await pages.__anext__()

    asyncio.run(run())


def test_legacy_polls_past_empty_partition_and_aggregates_page_headers(
    legacy, monkeypatch
):
    from collections import deque
    from azure.cosmos._change_feed.composite_continuation_token import (
        CompositeContinuationToken,
    )
    from azure.cosmos._change_feed.feed_range_composite_continuation_token import (
        FeedRangeCompositeContinuation,
    )
    from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
    from azure.cosmos._routing.routing_range import Range

    original = ChangeFeedPageState.legacy_state

    def two_ranges(self, properties):
        state = original(self, properties)
        state._continuation = FeedRangeCompositeContinuation(
            "rid",
            FeedRangeInternalEpk(Range("", "FF", True, False)),
            deque(
                [
                    CompositeContinuationToken(Range("", "80", True, False), None),
                    CompositeContinuationToken(Range("80", "FF", True, False), None),
                ]
            ),
        )
        return state

    monkeypatch.setattr(ChangeFeedPageState, "legacy_state", two_ranges)
    legacy.pages = [[], [{"id": "second-partition"}], [], []]
    hooks = []
    pages = legacy.proxy.query_items_change_feed(
        start_time="Beginning", response_hook=lambda h, b: hooks.append((h, b))
    ).by_page()
    assert legacy.next_page(pages) == [{"id": "second-partition"}]
    assert len(legacy.calls) == 2 and len(hooks) == 1
    assert float(hooks[0][0]["x-ms-request-charge"]) == 2
    assert legacy.next_page(pages) == []
    assert len(legacy.calls) == 4 and len(hooks) == 2
    decoded = json.loads(base64.b64decode(pages.continuation_token))
    assert all(part["token"] for part in decoded["continuation"]["continuation"])


def test_legacy_split_retries_are_bounded(legacy, monkeypatch):
    from azure.cosmos._change_feed.change_feed_state import ChangeFeedStateV2
    from azure.cosmos.exceptions import CosmosHttpResponseError

    error = CosmosHttpResponseError(status_code=410, message="split")
    error.sub_status = 1002
    query = (
        AsyncMock(side_effect=error)
        if legacy.async_mode
        else MagicMock(side_effect=error)
    )
    legacy.connection.QueryFeed = query
    refresh = AsyncMock() if legacy.async_mode else MagicMock()
    monkeypatch.setattr(
        ChangeFeedStateV2,
        (
            "handle_feed_range_gone_async"
            if legacy.async_mode
            else "handle_feed_range_gone"
        ),
        refresh,
    )
    pages = legacy.proxy.query_items_change_feed().by_page()
    with pytest.raises(CosmosHttpResponseError):
        legacy.next_page(pages)
    assert query.call_count == 11 and refresh.call_count == 10
    assert pages.continuation_token is None


def test_legacy_v1_keyword_checkpoint_resume(legacy):
    with pytest.warns(DeprecationWarning):
        pages = legacy.proxy.query_items_change_feed(
            partition_key_range_id="0"
        ).by_page()
    assert legacy.next_page(pages) == [{"id": "a"}]
    token = pages.continuation_token
    assert token.startswith("cf1.")
    resumed = legacy.proxy.query_items_change_feed(
        continuation=token, mode="AllVersionsAndDeletes", start_time="Beginning"
    ).by_page()
    assert legacy.next_page(resumed) == []
    state = legacy.calls[-1]["changeFeedState"]
    assert state._partition_key_range_id == "0"


def test_split_intersection_preserves_scope_and_resets_empty_cycle():
    from collections import deque
    from azure.cosmos._change_feed.composite_continuation_token import (
        CompositeContinuationToken,
    )
    from azure.cosmos._change_feed.feed_range_composite_continuation_token import (
        FeedRangeCompositeContinuation,
    )
    from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
    from azure.cosmos._routing.routing_range import Range

    scope = Range("20", "D0", True, False)
    state = FeedRangeCompositeContinuation(
        "rid",
        FeedRangeInternalEpk(scope),
        deque([CompositeContinuationToken(scope, '"42"')]),
    )
    state.apply_not_modified_response()
    state._replace_split_range(
        [
            {"minInclusive": "", "maxExclusive": "80"},
            {"minInclusive": "80", "maxExclusive": "FF"},
        ]
    )
    assert [
        (part.feed_range.min, part.feed_range.max, part.token)
        for part in state._continuation
    ] == [("20", "80", '"42"'), ("80", "D0", '"42"')]
    assert state._initial_no_result_range is None


def test_time_start_initial_empty_is_polled_within_same_public_page(feed):
    feed.pages = [
        ([], "c1.a"),
        ([{"current": {"id": "after-start"}}], "c1.b"),
        ([], "c1.c"),
    ]
    hooks = []
    pages = feed.proxy.query_items_change_feed(
        start_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
        response_hook=lambda h, b: hooks.append((h, b)),
        timeout=3,
    ).by_page()
    assert feed.next_page(pages) == [{"id": "after-start"}]
    assert len(feed.calls) == 2 and len(hooks) == 1
    assert float(hooks[0][0]["x-ms-request-charge"]) == 4
    assert feed.calls[0][1] is feed.calls[1][1]
    assert feed.next_page(pages) == []
