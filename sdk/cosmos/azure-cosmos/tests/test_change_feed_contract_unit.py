# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Public change-feed paging contracts without account access."""

import asyncio
import base64
import json
from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from common.typed_requests import legacy_partition_key_from_request
from common.change_feed_samples import load_change_feed_sample

from azure.cosmos import _retry_utility
from azure.cosmos.aio import _retry_utility_async
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy
from azure.cosmos._helpers._change_feed import ChangeFeedPageState
from azure.cosmos._helpers._item_context import ItemClientContext
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from azure.cosmos.partition_key import NonePartitionKeyValue
from read_all_items.test_read_all_items_contract_unit import feed as base_feed
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range


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
    def page(handle, prepared, cursor, *, timeout_seconds=None):
        base_feed.calls.append((prepared, cursor, timeout_seconds))
        if base_feed.setup_status:
            return base_feed.setup_status, 0, {}, b'{"message":"setup failed"}', None
        cursor.can_retry_setup = False
        if timeout_seconds is not None and base_feed.delay > timeout_seconds:
            raise TimeoutError("native page budget exhausted")
        base_feed.clock.now += base_feed.delay
        token = prepared.settings.query.continuation
        index = 0 if token is None else next(
            i + 1 for i, (_, value) in enumerate(base_feed.pages) if value == token
        )
        rows, following = base_feed.pages[index]
        headers = {"x-ms-request-charge": "2", "x-ms-session-token": "session"}
        if following is not None:
            headers["x-ms-continuation"] = following
        base_feed.prepared = prepared
        return base_feed.status, 0, headers, json.dumps({"Documents": rows}).encode(), None

    base_feed.binding.fetch_page_with_cursor.side_effect = page
    base_feed.binding.fetch_page_with_cursor_async.side_effect = page
    return base_feed


@pytest.mark.parametrize("mode", ["LatestVersion", "AllVersionsAndDeletes"])
@pytest.mark.parametrize("epk", ["11622DAA78F835834610ABE56EFF5CB5", "00FF", "01" * 48, "00" * 16])
@pytest.mark.parametrize("resume_with_range", [False, True])
def test_change_feed_accepts_sdk_point_range_and_preserves_resume_scope_rust(feed, mode, epk, resume_with_range):
    expected_range = FeedRangeInternalEpk(Range(epk, epk, True, True)).get_normalized_range()
    payload = {"Range": {"min": epk, "max": epk, "isMinInclusive": True, "isMaxInclusive": True}}
    result = (200, 0, {}, json.dumps(payload).encode(), None)
    name = "feed_range_from_partition_key" + ("_async" if feed.async_mode else "")
    producer = AsyncMock(return_value=result) if feed.async_mode else MagicMock(return_value=result)
    setattr(feed.binding, name, producer)
    point = feed.proxy.feed_range_from_partition_key("customer-501")
    if feed.async_mode:
        point = asyncio.run(point)
    original = deepcopy(point)
    pages = feed.proxy.query_items_change_feed(feed_range=point, mode=mode).by_page()
    feed.next_page(pages)
    token = pages.continuation_token
    resumed = feed.proxy.query_items_change_feed(
        continuation=token, **({"feed_range": point} if resume_with_range else {})
    ).by_page()
    feed.next_page(resumed)
    assert len(feed.calls) == 2
    for prepared, _, _ in feed.calls:
        assert json.loads(prepared.body_bytes)["feed_range"] == [expected_range.min, expected_range.max]
    assert point == original == payload
    producer.assert_called_once()


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


@pytest.mark.parametrize("prefix", ["c1.", "c2."])
def test_caught_up_page_publishes_bookmark_and_new_pager_polls_again(feed, prefix):
    feed.pages = [(rows, token.replace("c1.", prefix)) for rows, token in feed.pages]
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
    assert feed.calls[-1][0].settings.query.continuation == prefix + "b"
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
    pager = feed.proxy.query_items_change_feed(mode=mode, partition_key=False)
    feed.backend._ensure_driver_handle.assert_not_called()
    feed.binding._ItemFeedCursor.assert_not_called()
    assert not feed.calls
    assert not feed.connection.mock_calls
    pages = pager.by_page()
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
        ({"is_start_from_beginning": "yes"}, TypeError),
        ({"is_start_from_beginning": True, "start_time": "Now"}, ValueError),
        ({"mode": "AllVersionsAndDeletes", "start_time": "Beginning"}, ValueError),
        ({"partition_key": {}, "feed_range": {}}, ValueError),
        ({"partition_key": []}, ValueError),
        ({"partition_key": float("nan")}, ValueError),
        ({"feed_range": {"Range": {"min": "FF", "max": ""}}}, ValueError),
        ({"availability_strategy": False}, TypeError),
        ({"availability_strategy": None}, TypeError),
        ({"request_options": {"availabilityStrategy": None}}, TypeError),
        ({"feed_options": {"availabilityStrategy": None}}, TypeError),
        ({"initial_headers": {"if-none-match": "42"}}, NotImplementedError),
        ({"continuation": "c1.query"}, ValueError),
        ({"continuation": "42"}, NotImplementedError),
        ({"continuation": "cf1.invalid"}, ValueError),
    ],
)
def test_invalid_inputs_never_dispatch(feed, kwargs, error):
    with pytest.raises(error):
        feed.proxy.query_items_change_feed(**kwargs)
    feed.backend._ensure_driver_handle.assert_not_called()
    feed.binding._ItemFeedCursor.assert_not_called()
    assert feed.calls == []
    assert not feed.connection.mock_calls


@pytest.mark.parametrize("source", ["keyword", "request_options", "feed_options"])
@pytest.mark.parametrize("value", [None, 0, 1000, -1, True])
def test_cache_staleness_is_rejected_at_pager_construction_rust(feed, source, value):
    kwargs = (
        {"max_integrated_cache_staleness_in_ms": value}
        if source == "keyword"
        else {source: {"maxIntegratedCacheStaleness": value}}
    )
    original = deepcopy(kwargs)
    with pytest.raises(TypeError, match="does not accept max_integrated_cache_staleness_in_ms"):
        feed.proxy.query_items_change_feed(**kwargs)
    assert kwargs == original
    feed.backend._ensure_driver_handle.assert_not_called()
    feed.binding._ItemFeedCursor.assert_not_called()
    assert feed.calls == []
    assert not feed.connection.mock_calls


@pytest.mark.parametrize("source", ["keyword", "request_options", "feed_options"])
@pytest.mark.parametrize("value", [None, 2])
def test_per_call_connection_timeout_is_rejected_before_io_rust(feed, source, value):
    kwargs = (
        {"connection_timeout": value}
        if source == "keyword"
        else {source: {"connection_timeout": value}}
    )
    original = deepcopy(kwargs)
    with pytest.raises(TypeError, match=r"per-call connection_timeout.*ConnectionPoolOptions\.connection_timeout"):
        feed.proxy.query_items_change_feed(**kwargs)
    assert kwargs == original
    feed.backend._ensure_driver_handle.assert_not_called()
    feed.binding._ItemFeedCursor.assert_not_called()
    assert feed.calls == []
    assert not feed.connection.mock_calls


@pytest.mark.parametrize("value", [None, 2])
def test_legacy_per_call_connection_timeout_is_preserved(legacy, value):
    pages = legacy.proxy.query_items_change_feed(connection_timeout=value).by_page()
    assert legacy.next_page(pages) == [{"id": "a"}]
    assert legacy.connection.QueryFeed.call_args.kwargs["connection_timeout"] == value


def test_keyword_only_and_deprecated_keywords(feed):
    with pytest.raises(TypeError):
        feed.proxy.query_items_change_feed("0")
    with pytest.warns(DeprecationWarning):
        pages = feed.proxy.query_items_change_feed(
            is_start_from_beginning=True
        ).by_page()
    feed.next_page(pages)
    assert json.loads(feed.calls[-1][0].body_bytes)["start"] == "Beginning"
    with pytest.warns(DeprecationWarning):
        pages = feed.proxy.query_items_change_feed(partition_key_range_id="0").by_page()
    feed.next_page(pages)
    assert json.loads(feed.calls[-1][0].body_bytes)["range_id"] == "0"
    resumed = feed.proxy.query_items_change_feed(
        continuation=pages.continuation_token, partition_key="ignored"
    ).by_page()
    feed.next_page(resumed)
    assert json.loads(feed.calls[-1][0].body_bytes)["range_id"] == "0"
    assert feed.calls[-1][0].partition_key.kind == "cross_partition"


@pytest.mark.parametrize("kwargs", [
    {"partition_key_range_id": ""},
    {"partition_key_range_id": 0},
    {"partition_key_range_id": "0", "partition_key": "customer"},
    {"partition_key_range_id": "0", "feed_range": {"Range": {"min": "", "max": "FF"}}},
    {"partition_key_range_id": "0", "mode": "AllVersionsAndDeletes"},
])
def test_invalid_partition_range_id_never_dispatches(feed, kwargs):
    with pytest.warns(DeprecationWarning), pytest.raises(ValueError):
        feed.proxy.query_items_change_feed(**kwargs)
    assert not feed.calls
    feed.backend._ensure_driver_handle.assert_not_called()


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
    context = SimpleNamespace(calls=[], pages=[[{"id": "a"}], [], [{"id": "b"}], []], etag_name="etag")
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
            context.etag_name: '"' + str(len(context.calls)) + '"',
            "x-ms-request-charge": "1",
        }
        response_hook(headers, {"Documents": rows})
        connection.last_response_headers = {"etag": "unrelated"}
        return rows, headers

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


@pytest.mark.parametrize("kwargs,error", [
    ({"mode": "invalid"}, ValueError),
    ({"start_time": 42}, ValueError),
    ({"is_start_from_beginning": "yes"}, TypeError),
    ({"is_start_from_beginning": True, "start_time": "Now"}, ValueError),
    ({"partition_key": "customer", "feed_range": {"Range": {"min": "", "max": "FF"}}}, ValueError),
    ({"mode": "AllVersionsAndDeletes", "start_time": "Beginning"}, ValueError),
    ({"continuation": "cf1.invalid"}, ValueError),
])
def test_legacy_invalid_inputs_fail_at_call_without_io(legacy, kwargs, error):
    with pytest.raises(error):
        legacy.proxy.query_items_change_feed(**kwargs)
    legacy.metadata.assert_not_called()
    assert not legacy.connection.mock_calls
    assert not legacy.calls


@pytest.mark.parametrize("source", ["keyword", "request_options", "feed_options"])
def test_continuation_settings_are_validated_at_call_rust(feed, source):
    token = "cf1." + base64.urlsafe_b64encode(json.dumps({
        "backend": "rust",
        "container": feed.proxy.container_link,
        "settings": {"mode": "invalid", "start": "Now", "partition_key": None, "feed_range": None},
        "token": "c1.a",
    }).encode()).decode().rstrip("=")
    kwargs = {"continuation": token} if source == "keyword" else {source: {"continuation": token}}
    with pytest.raises(ValueError, match="Invalid change-feed continuation settings"):
        feed.proxy.query_items_change_feed(**kwargs)
    feed.backend._ensure_driver_handle.assert_not_called()
    assert not feed.calls


@pytest.mark.parametrize("mode", ["LatestVersion", "AllVersionsAndDeletes"])
@pytest.mark.parametrize("key", [None, False, 0, ""])
def test_core_python_modes_empty_checkpoint_and_authoritative_resume(legacy, mode, key):
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


def test_rust_tokens_cannot_resume_on_legacy_and_broad_legacy_import_is_explicit(feed, legacy):
    pages = feed.proxy.query_items_change_feed().by_page()
    feed.next_page(pages)
    with pytest.raises(ValueError, match="incompatible backend"):
        legacy.proxy.query_items_change_feed(
            continuation=pages.continuation_token
        ).by_page()
    core_pages = legacy.proxy.query_items_change_feed().by_page()
    legacy.next_page(core_pages)
    with pytest.raises(NotImplementedError, match="complete partition key"):
        feed.proxy.query_items_change_feed(
            continuation=core_pages.continuation_token
        ).by_page()


@pytest.mark.parametrize("channel", ["keyword", "by_page"])
@pytest.mark.parametrize("mode", ["LatestVersion", "AllVersionsAndDeletes"])
@pytest.mark.parametrize("key", [None, False, 0, ""])
def test_legacy_key_checkpoint_restores_scope_and_reaches_rust(feed, legacy, channel, mode, key):
    core_pages = legacy.proxy.query_items_change_feed(mode=mode, partition_key=key).by_page()
    legacy.next_page(core_pages)
    token = core_pages.continuation_token
    feed.pages.insert(0, ([], token))
    kwargs = (
        {"mode": "invalid", "partition_key": "ignored", "start_time": "invalid"}
        if channel == "keyword"
        else {"mode": "LatestVersion", "partition_key": "ignored", "start_time": "Beginning"}
    )
    pages = (
        feed.proxy.query_items_change_feed(continuation=token, **kwargs).by_page()
        if channel == "keyword"
        else feed.proxy.query_items_change_feed(**kwargs).by_page(continuation_token=token)
    )
    feed.next_page(pages)
    request = feed.calls[-1][0]
    assert request.partition_key.values == (key,)
    assert json.loads(request.body_bytes) == {"mode": mode, "start": "Now", "feed_range": None}
    assert json.loads(base64.b64decode(request.settings.query.continuation)) == json.loads(base64.b64decode(token))
    assert pages.continuation_token.startswith("cf1.")
    resumed = feed.proxy.query_items_change_feed(continuation=pages.continuation_token).by_page()
    feed.next_page(resumed)
    assert feed.calls[-1][0].settings.query.continuation == "c1.a"
    assert len(legacy.calls) == 1


@pytest.mark.parametrize("wrapped", [False, True])
def test_legacy_v1_etag_requires_and_preserves_explicit_key(feed, wrapped):
    token = '"42"'
    kwargs = {"partition_key": None}
    if wrapped:
        token = "cf1." + base64.urlsafe_b64encode(json.dumps({
            "backend": "core-python", "container": feed.proxy.container_link, "token": token,
            "settings": {
                "mode": "LatestVersion", "start": "Now",
                "partition_key": "[null]", "feed_range": None,
            },
        }).encode()).decode().rstrip("=")
        kwargs = {}
    feed.pages.insert(0, ([], '"42"'))
    pages = feed.proxy.query_items_change_feed(continuation=token, **kwargs).by_page()
    feed.next_page(pages)
    assert feed.calls[-1][0].partition_key.values == (None,)
    assert feed.calls[-1][0].settings.query.continuation == '"42"'
    with pytest.raises(NotImplementedError, match="complete partition_key"):
        feed.proxy.query_items_change_feed(continuation='"42"').by_page()


@pytest.mark.parametrize("start", ["Beginning", "Now", datetime(2025, 1, 2, 3, 4, 5, 123000, tzinfo=timezone.utc)])
def test_legacy_v2_start_is_restored_without_changing_checkpoint(feed, legacy, start):
    pages = legacy.proxy.query_items_change_feed(partition_key="customer", start_time=start).by_page()
    legacy.next_page(pages)
    token = pages.continuation_token
    feed.pages.insert(0, ([], token))
    feed.next_page(feed.proxy.query_items_change_feed(continuation=token).by_page())
    expected = start.isoformat() if isinstance(start, datetime) else start
    assert json.loads(feed.calls[-1][0].body_bytes)["start"] == expected


@pytest.mark.parametrize("mutation", [
    "rid", "empty_position", "no_positions", "missing_positions", "non_list_positions",
    "missing_start", "bad_time", "bad_key",
])
def test_malformed_legacy_import_never_dispatches(feed, legacy, mutation):
    pages = legacy.proxy.query_items_change_feed(partition_key="customer").by_page()
    legacy.next_page(pages)
    saved = json.loads(base64.b64decode(pages.continuation_token))
    if mutation == "rid":
        saved["continuation"]["rid"] = "different"
    elif mutation == "empty_position":
        saved["continuation"]["continuation"][0]["token"] = ""
    elif mutation == "no_positions":
        saved["continuation"]["continuation"] = []
    elif mutation == "missing_positions":
        del saved["continuation"]["continuation"]
    elif mutation == "non_list_positions":
        saved["continuation"]["continuation"] = {"token": "42"}
    elif mutation == "missing_start":
        del saved["startFrom"]
    elif mutation == "bad_time":
        saved["startFrom"] = {"Type": "PointInTime", "PointInTimeMs": True}
    else:
        saved["continuation"]["PK"] = {"unsupported": True}
    token = base64.b64encode(json.dumps(saved).encode()).decode()
    with pytest.raises(ValueError):
        feed.proxy.query_items_change_feed(continuation=token).by_page()
    assert feed.calls == []


def test_multiple_legacy_positions_remain_unsupported_rust(feed, legacy):
    pages = legacy.proxy.query_items_change_feed(partition_key="customer").by_page()
    legacy.next_page(pages)
    saved = json.loads(base64.b64decode(pages.continuation_token))
    saved["continuation"]["continuation"] *= 2
    token = base64.b64encode(json.dumps(saved).encode()).decode()
    with pytest.raises(NotImplementedError, match="multiple range positions"):
        feed.proxy.query_items_change_feed(continuation=token)
    assert feed.calls == []


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


def test_core_python_polls_past_empty_partition_and_aggregates_page_headers(
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


def test_core_python_split_retries_are_bounded(legacy, monkeypatch):
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


@pytest.mark.parametrize("etag_name", ["etag", "Etag", "ETag"])
def test_core_python_v1_keyword_checkpoint_resume(legacy, etag_name):
    legacy.etag_name = etag_name
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


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("scenario", [
    "read_change_feed_with_continuation",
    "read_change_feed_with_all_versions_and_delete_mode",
    "read_change_feed_with_all_versions_and_delete_mode_with_partition_key",
])
def test_change_feed_samples_resume_from_pager(feed, legacy, backend, scenario, monkeypatch):
    context = feed if backend == "rust" else legacy
    sample = load_change_feed_sample(context.async_mode, monkeypatch)
    full_fidelity = scenario != "read_change_feed_with_continuation"
    created = {"current": {"id": "created"}, "metadata": {"operationType": "create"}}
    deleted = {"current": {"id": "deleted"}, "metadata": {"operationType": "delete"}}
    rows = [[], [created], [], [deleted], []] if full_fidelity else [
        [{"current": {"id": "old"}}], [], [created], [],
    ]
    if backend == "rust":
        context.pages = [(page, f"c1.{index}") for index, page in enumerate(rows)]
    else:
        context.pages = rows if full_fidelity else [
            [row["current"] for row in page] for page in rows
        ]
    context.connection.last_response_headers = {"etag": '"stale-connection-token"'}
    mock = AsyncMock if context.async_mode else MagicMock
    monkeypatch.setattr(sample, "create_items", mock())
    monkeypatch.setattr(sample, "clean_up", mock())
    printed = []
    monkeypatch.setattr(sample, "print", lambda value: printed.append(value), raising=False)
    query = context.proxy.query_items_change_feed
    requests, pagers = [], []

    def observe(**kwargs):
        requests.append(kwargs)
        pager = query(**kwargs)
        pagers.append(pager)
        return pager

    monkeypatch.setattr(context.proxy, "query_items_change_feed", observe)
    result = getattr(sample, scenario)(context.proxy)
    if context.async_mode:
        asyncio.run(result)
    for index in range(1, len(requests)):
        assert requests[index]["continuation"] == pagers[index - 1].get_response_headers()["etag"]
    documents = [value for value in printed if isinstance(value, dict)]
    assert documents == ([created, deleted] if full_fidelity else [{"id": "old"}, {"id": "created"}])
    assert len(context.calls) == len(rows)
    if full_fidelity:
        assert requests[1]["continuation"] != requests[2]["continuation"]
        sample.clean_up.assert_called_once_with(context.proxy)


def test_legacy_range_id_checkpoint_is_not_restarted_on_rust(feed, legacy):
    with pytest.warns(DeprecationWarning):
        pages = legacy.proxy.query_items_change_feed(partition_key_range_id="0").by_page()
    legacy.next_page(pages)
    with pytest.raises(NotImplementedError, match="complete partition_key"):
        feed.proxy.query_items_change_feed(continuation=pages.continuation_token)
    with pytest.warns(DeprecationWarning), pytest.raises(NotImplementedError, match="complete partition_key"):
        feed.proxy.query_items_change_feed(partition_key_range_id="0", continuation='"42"')
    assert not feed.calls


def test_legacy_range_id_does_not_follow_partition_splits(legacy):
    error = CosmosHttpResponseError(status_code=410, message="split")
    error.sub_status = 1002
    legacy.connection.QueryFeed.side_effect = error
    with pytest.warns(DeprecationWarning):
        pages = legacy.proxy.query_items_change_feed(partition_key_range_id="0").by_page()
    with pytest.raises(CosmosHttpResponseError) as caught:
        legacy.next_page(pages)
    assert caught.value is error
    assert legacy.connection.QueryFeed.call_count == 1
    assert pages.continuation_token is None


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
