# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Standalone sync/async read_items contracts over Rust's typed page boundary."""

import asyncio
import inspect
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import CosmosList, _operation_deadline
from azure.cosmos._helpers import _read_items
from azure.cosmos._helpers._read_items import partition_key_identity
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from azure.cosmos.partition_key import NonePartitionKeyValue, NullPartitionKeyValue, _Undefined

from ._helpers import make_proxy, page


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def mode(request):
    asynchronous = request.param
    return SimpleNamespace(
        asynchronous=asynchronous,
        make=lambda *args, **kwargs: make_proxy(asynchronous, *args, **kwargs),
        run=lambda result: asyncio.run(result) if inspect.isawaitable(result) else result,
        mock=AsyncMock if asynchronous else MagicMock,
    )


def test_order_duplicates_missing_and_empty_pages_rust(mode):
    pairs = [("same", "a"), ("other", "a"), ("same", "b"), ("same", "a"), ("missing", "b")]
    proxy, backend = mode.make([
        page([{"id": "same", "pk": "b", "nested": [1]}], 2, more=True, diagnostics="first"),
        page([], 0.5, more=True, diagnostics="empty"),
        page([{"id": "other", "pk": "a"}, {"id": "same", "pk": "a", "nested": [2]}],
             3, diagnostics="last"),
    ])
    hook = MagicMock()
    result = mode.run(proxy.read_items(pairs, response_hook=hook))
    assert [(row["id"], row["pk"]) for row in result] == pairs[:-1]
    assert result[0] is not result[3] and result[0]["nested"] is not result[3]["nested"]
    assert result.get_response_headers()["x-ms-request-charge"] == "5.5"
    assert result.get_response_headers()["x-ms-cosmos-sdk-diagnostics"] == "first; empty; last"
    assert "x-ms-continuation" not in result.get_response_headers()
    hook.assert_called_once()
    assert len(backend.calls) == backend.closed == 3
    assert all(call.cursor is backend.calls[0].cursor for call in backend.calls)
    assert all(call.continuation is None for call in backend.calls)


@pytest.mark.parametrize("kind", ["none", "mutating", "false-valued", "raising", "timeout"])
def test_hook_isolated_once_and_never_replayed_rust(mode, kind):
    calls = []
    error = TimeoutError("customer callback") if kind == "timeout" else RuntimeError("customer callback")

    class Hook:
        def __bool__(self):
            return kind != "false-valued"

        def __call__(self, headers, body):
            calls.append(1)
            assert body.get_response_headers() is not headers
            headers["x-ms-request-charge"] = "changed"
            body.get_response_headers()["test"] = "changed"
            body[0]["nested"].append(99)
            body.clear()
            if kind in ("raising", "timeout"):
                raise error

    proxy, backend = mode.make([page([{"id": "a", "pk": "p", "nested": [1]}], 2)])
    hook = None if kind == "none" else Hook()
    if kind in ("raising", "timeout"):
        with pytest.raises(type(error)) as caught:
            mode.run(proxy.read_items([("a", "p")], response_hook=hook, timeout=5))
        assert caught.value is error
    else:
        result = mode.run(proxy.read_items([("a", "p")], response_hook=hook))
        assert result == [{"id": "a", "pk": "p", "nested": [1]}]
        assert result.get_response_headers() == {"x-ms-request-charge": "2.0"}
    assert len(calls) == (0 if kind == "none" else 1)
    assert len(backend.calls) == backend.closed == 1


def test_empty_input_no_metadata_or_cursor_and_one_hook_rust(mode):
    proxy, backend = mode.make()
    hook = MagicMock()
    result = mode.run(proxy.read_items([], response_hook=hook))
    assert isinstance(result, CosmosList) and result == []
    assert result.get_response_headers() == {}
    hook.assert_called_once_with({}, [])
    assert hook.call_args.args[1] is not result
    backend.get_container_metadata.assert_not_called()
    backend.create_item_feed_cursor.assert_not_called()
    assert not backend.calls


@pytest.mark.parametrize("items,kwargs,error", [
    (None, {}, TypeError), ("ab", {}, TypeError), ([("a",)], {}, TypeError),
    ([("a", "p", "extra")], {}, TypeError), ([(3, "p")], {}, TypeError),
    ([("", "p")], {}, ValueError), ([("a/b", "p")], {}, ValueError),
    ([("a", [])], {}, ValueError), ([("a", {"bad": 1})], {}, TypeError),
    ([("a", float("nan"))], {}, ValueError), ([("a", float("inf"))], {}, ValueError),
    ([("a", [object()])], {}, TypeError),
    ([], {"max_concurrency": 0}, TypeError), ([], {"max_concurrency": 1}, TypeError),
    ([], {"max_concurrency": None}, TypeError), ([], {"executor": None}, TypeError),
    ([], {"response_hook": False}, TypeError), ([], {"timeout": 0.5}, ValueError),
    ([], {"timeout": float("nan")}, ValueError), ([], {"timeout": True}, ValueError),
    ([], {"continuation": "token"}, TypeError), ([], {"max_item_count": 0}, ValueError),
    ([], {"max_integrated_cache_staleness_in_ms": False}, ValueError),
    ([], {"max_integrated_cache_staleness_in_ms": -1}, ValueError),
    ([], {"request_options": {"maxIntegratedCacheStaleness": -1}}, ValueError),
    ([], {"initial_headers": {"x-ms-continuation": "token"}}, TypeError),
    ([], {"request_options": {"maxConcurrency": 1}}, TypeError),
])
def test_validation_precedes_metadata_even_for_empty_input_rust(mode, items, kwargs, error):
    proxy, backend = mode.make()
    with pytest.raises(error):
        mode.run(proxy.read_items(items, **kwargs))
    backend.get_container_metadata.assert_not_called()
    assert not backend.calls


def test_input_keys_snapshot_before_metadata_rust(mode):
    pairs = [("a", ["tenant", None])]
    proxy, backend = mode.make(paths=("/tenant", "/user"), kind="MultiHash")
    metadata = backend.get_container_metadata.return_value

    def mutate(*args, **kwargs):
        pairs[0][1][0] = "changed"
        return metadata

    backend.get_container_metadata.side_effect = mutate
    mode.run(proxy.read_items(pairs))
    assert backend.calls[0].read_many_items[0].partition_key.values == ("tenant", None)


@pytest.mark.parametrize("path,row", [
    ("/tenant/id", {"tenant": {"id": "p"}}),
    ('/"tenant/id"', {"tenant/id": "p"}),
    ("/a-b", {"a-b": "p"}),
    ("/na\u00efve", {"na\u00efve": "p"}),
])
def test_partition_paths_match_returned_documents_rust(mode, path, row):
    document = {"id": "a", **row}
    proxy, backend = mode.make([page([document])], paths=(path,))
    assert mode.run(proxy.read_items([("a", "p")])) == [document]
    assert backend.calls[0].read_many_items[0].partition_key.values == ("p",)


def test_hierarchical_null_undefined_and_duplicate_identity_rust(mode):
    proxy, backend = mode.make([
        page([{"id": "same", "tenant": "t"}, {"id": "same", "tenant": "t", "user": None}])
    ], paths=("/tenant", "/user"), kind="MultiHash")
    result = mode.run(proxy.read_items([
        ("same", ["t", None]), ("same", ["t", NonePartitionKeyValue]), ("same", ["t", None]),
    ]))
    assert len(result) == 3 and result[0]["user"] is None and "user" not in result[1]
    assert result[0] is not result[2]
    assert backend.calls[0].read_many_items[1].partition_key.values == ("t", Ellipsis)


def test_typed_keys_are_distinct_and_numeric_keys_match_rust(mode):
    keys = [True, 1, False, 0, None, NonePartitionKeyValue]
    rows = [{"id": "same", "pk": key} for key in keys[:-1]] + [{"id": "same"}]
    proxy, backend = mode.make([page(list(reversed(rows)))])
    assert mode.run(proxy.read_items([("same", key) for key in keys])) == rows
    assert len(backend.calls[0].read_many_items) == 6
    assert partition_key_identity(True) != partition_key_identity(1)
    assert partition_key_identity(False) != partition_key_identity(0)
    assert partition_key_identity(1) == partition_key_identity(1.0)
    assert partition_key_identity(None) == partition_key_identity(NullPartitionKeyValue)
    assert partition_key_identity({}) == partition_key_identity(_Undefined())


def test_incomplete_full_key_fails_before_page_dispatch_rust(mode):
    proxy, backend = mode.make(paths=("/tenant", "/user"), kind="MultiHash")
    with pytest.raises(ValueError, match="every component"):
        mode.run(proxy.read_items([("a", ["tenant"])]))
    assert not backend.calls


def test_wrong_partition_response_is_not_accepted_by_id_rust(mode):
    proxy, _ = mode.make([page([{"id": "same", "pk": "wrong"}])])
    with pytest.raises(CosmosHttpResponseError, match="outside the requested"):
        mode.run(proxy.read_items([("same", "a")]))


@pytest.mark.parametrize("stage", ["metadata", "first-page", "second-page"])
def test_one_deadline_includes_metadata_and_every_page_rust(mode, monkeypatch, stage):
    clock = SimpleNamespace(monotonic=lambda: clock.now, now=100.0)
    monkeypatch.setattr(_read_items, "time", clock)
    monkeypatch.setattr(_operation_deadline, "time", clock)
    calls = []

    def response():
        calls.append(1)
        clock.now += 6 if stage == "first-page" or len(calls) == 2 else 1
        return page([{"id": "a", "pk": "p"}], 2, more=True)

    proxy, backend = mode.make([response, response])
    metadata = backend.get_container_metadata.return_value

    def resolve(_link, *, deadline):
        assert deadline == 105
        clock.now += 6 if stage == "metadata" else 1
        return metadata

    backend.get_container_metadata.side_effect = resolve
    hook = MagicMock()
    with pytest.raises(CosmosClientTimeoutError):
        mode.run(proxy.read_items([("a", "p")], timeout=5, response_hook=hook))
    assert len(backend.calls) == {"metadata": 0, "first-page": 1, "second-page": 2}[stage]
    assert all(deadline == 105 for deadline in backend.deadlines)
    if backend.calls:
        assert backend.calls[0].settings.timeout_seconds == 4
    if len(backend.calls) == 2:
        assert backend.calls[1].settings.timeout_seconds == 3
    hook.assert_not_called()


@pytest.mark.parametrize("stage", ["metadata", "first-page", "later-page"])
def test_failures_never_return_partial_success_or_replay_rust(mode, stage):
    error = CosmosHttpResponseError(status_code=503, message="routing or service failure")
    responses = [error] if stage != "later-page" else [page([{"id": "a", "pk": "p"}], 2, more=True), error]
    proxy, backend = mode.make(responses)
    if stage == "metadata":
        backend.get_container_metadata.side_effect = error
    hook = MagicMock()
    with pytest.raises(CosmosHttpResponseError) as caught:
        mode.run(proxy.read_items([("a", "p"), ("b", "p")], response_hook=hook))
    assert caught.value is error
    assert len(backend.calls) == {"metadata": 0, "first-page": 1, "later-page": 2}[stage]
    assert backend.closed == len(backend.calls)
    hook.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel", [False, True])
async def test_async_cancellation_and_timeout_drain_inflight_fetch_rust(cancel):
    proxy, backend = make_proxy(True)
    entered, cleaned = asyncio.Event(), asyncio.Event()
    calls = []

    async def execute(_prepared, **kwargs):
        calls.append(1)
        entered.set()
        try:
            await asyncio.Event().wait()
            yield page()
        finally:
            cleaned.set()

    backend.execute_pages = execute
    task = asyncio.create_task(proxy.read_items(
        [("a", "p")], _item_operation_deadline=None if cancel else time.monotonic() + 0.05
    ))
    await asyncio.wait_for(entered.wait(), 2)
    if cancel:
        task.cancel()
    with pytest.raises(asyncio.CancelledError if cancel else CosmosClientTimeoutError):
        await task
    assert cleaned.is_set() and calls == [1]
