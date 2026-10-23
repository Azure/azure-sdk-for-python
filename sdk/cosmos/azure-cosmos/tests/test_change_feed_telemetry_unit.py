# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Record internal change-feed polls without changing checkpoints or empty results."""

import asyncio
import builtins
from dataclasses import replace
from datetime import datetime, timezone
import json
import time
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

pytest.importorskip("opentelemetry.sdk.trace")
# pylint: disable=wrong-import-position
from opentelemetry import trace
from opentelemetry.sdk.trace.sampling import ALWAYS_OFF
from common.test_rust_telemetry_unit import (  # pylint: disable=unused-import
    DriverTransportError,
    attempt_spans,
    contribution_response,
    recording_setup,
)
from test_change_feed_contract_unit import base_feed, feed  # pylint: disable=unused-import
from azure.core.exceptions import ServiceResponseError
from azure.core.settings import settings
from azure.cosmos import _telemetry as telemetry
from azure.cosmos._backend import binding_adapter as sync_binding
from azure.cosmos.aio._backend import binding_adapter as async_binding
from azure.cosmos._backend.errors import BindingProtocolError
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError

# pylint: enable=wrong-import-position


@pytest.fixture(name="polling")
def polling_setup(recording, feed, monkeypatch):  # pylint: disable=unused-argument,redefined-outer-name
    h = SimpleNamespace(
        feed=feed,
        calls=[],
        states=[],
        seen=[],
        error=None,
        gate=None,
        drained=False,
        transform=lambda value: value,
    )
    feed.proxy._item_context = replace(
        feed.proxy._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(h.seen.append),),
    )
    module = async_binding if feed.async_mode else sync_binding
    monkeypatch.setattr(module, "_DRIVER_TRANSPORT_ERROR", DriverTransportError)
    original = feed.binding.fetch_page_with_cursor.side_effect

    def start(prepared, cursor, include_attempts, timeout_seconds):
        h.calls.append((prepared, cursor, include_attempts, timeout_seconds))
        h.states.append(telemetry._OPERATION.get())

    def finish(handle, prepared, cursor, include_attempts, timeout_seconds):
        _, payload = contribution_response(5, time.time_ns())
        payload["complete"] = False
        if h.error:
            if include_attempts:
                h.error._cosmos_attempt_payload = payload
            raise h.error
        response = original(handle, prepared, cursor, timeout_seconds=timeout_seconds)
        result = h.transform((response, payload))
        return result if include_attempts else result[0]

    def native(handle, prepared, cursor, *, include_attempts=False, timeout_seconds=None):
        start(prepared, cursor, include_attempts, timeout_seconds)
        return finish(handle, prepared, cursor, include_attempts, timeout_seconds)

    async def native_async(handle, prepared, cursor, *, include_attempts=False, timeout_seconds=None):
        start(prepared, cursor, include_attempts, timeout_seconds)
        if h.gate:
            h.gate.set()
            try:
                await asyncio.Future()
            finally:
                h.drained = True
        return finish(handle, prepared, cursor, include_attempts, timeout_seconds)

    feed.binding.fetch_page_with_cursor.side_effect = native
    feed.binding.fetch_page_with_cursor_async.side_effect = native_async
    return h


def fetch_spans(recording):
    return [
        s for s in recording.exporter.get_finished_spans() if s.name == "ContainerProxy.query_items_change_feed.fetch"
    ]


@pytest.mark.parametrize("recording_mode", ["enabled", "disabled", "handler-only", "sampled-out", "no-handlers"])
@pytest.mark.parametrize("mode", ["LatestVersion", "AllVersionsAndDeletes"])
@pytest.mark.parametrize("timeout", [None, 10])
def test_caught_up_poll_and_resume_keep_per_fetch_ownership(
    polling, recording, recording_mode, mode, timeout
):  # pylint: disable=too-many-statements
    h, f = polling, polling.feed
    if recording_mode in ("disabled", "handler-only"):
        settings.tracing_enabled = False
    if recording_mode == "sampled-out":
        recording.provider.sampler = ALWAYS_OFF
    f.proxy._item_context = replace(
        f.proxy._item_context,
        telemetry_handlers=(
            ()
            if recording_mode == "no-handlers"
            else (telemetry.CompletionHandler(h.seen.append, collect_attempts=recording_mode == "handler-only"),)
        ),
    )
    hooks = []

    def hook(headers, body):
        state = telemetry._OPERATION.get()
        assert state is h.states[-1] and (state is None or not state.closed)
        hooks.append(dict(headers))
        headers.clear()
        body["Documents"].clear()

    with trace.get_tracer("customer").start_as_current_span("prepare"):
        pager = f.proxy.query_items_change_feed(mode=mode, timeout=timeout, response_hook=hook)
    assert not h.calls and not h.seen and not fetch_spans(recording)
    pages = pager.by_page()
    parents = []
    with trace.get_tracer("customer").start_as_current_span("consume") as consumer:
        rows = f.next_page(pages)
        assert rows == ([{"id": "a", "nested": [1]}] if mode == "LatestVersion" else f.pages[0][0])
        parents.append(consumer.get_span_context().span_id)
    first = pages.continuation_token
    f.status = 304
    with trace.get_tracer("customer").start_as_current_span("caught-up") as consumer:
        assert f.next_page(pages) == []
        parents.append(consumer.get_span_context().span_id)
    token = pages.continuation_token
    assert token != first and token.startswith("cf1.")
    assert hooks[-1]["etag"] == pager.get_response_headers()["x-ms-continuation"] == token
    with pytest.raises(StopAsyncIteration if f.async_mode else StopIteration):
        f.next_page(pages)
    assert len(h.calls) == 2 and pages.state.done and pages.state.cursor is None
    f.status = 200
    with trace.get_tracer("customer").start_as_current_span("resume") as consumer:
        resumed = f.proxy.query_items_change_feed(continuation=token, timeout=timeout).by_page()
        assert f.next_page(resumed) == ([{"id": "b"}] if mode == "LatestVersion" else f.pages[2][0])
        parents.append(consumer.get_span_context().span_id)
    assert h.calls[0][1] is h.calls[1][1] and h.calls[2][1] is not h.calls[0][1]
    collect = recording_mode in ("enabled", "handler-only", "no-handlers")
    assert all(call[2] == collect for call in h.calls)
    assert len(h.seen) == (0 if recording_mode == "no-handlers" else 3)
    assert all(c.operation == "query_items_change_feed" and c.outcome == "success" for c in h.seen)
    if h.seen and collect:
        assert all(not c.diagnostics.complete for c in h.seen)
    spans = fetch_spans(recording)
    assert len(spans) == (3 if recording_mode in ("enabled", "no-handlers") else 0)
    if spans:
        assert [s.parent.span_id for s in spans] == parents
        assert all(s.status.status_code is trace.StatusCode.UNSET for s in spans)
        assert not any(k.startswith("cosmos.poc.") for s in spans for k in s.attributes)
        assert [sum(a.parent.span_id == s.context.span_id for a in attempt_spans(recording)) for s in spans] == [
            2,
            2,
            2,
        ]
    assert telemetry._OPERATION.get() is None and not f.connection.mock_calls


def test_time_start_shares_deadline_and_only_final_fetch_owns_hook(polling, recording, monkeypatch):
    h, f = polling, polling.feed
    f.pages[0] = ([], "c1.a")
    f.pages[1] = ([{"current": {"id": "b"}}], "c1.b")
    f.delay = 1
    deadlines, hooks = [], []
    execute = f.backend.execute_pages

    def execute_pages(*args, **kwargs):
        deadlines.append(kwargs["deadline"])
        return execute(*args, **kwargs)

    def hook(_headers, _body):
        assert telemetry._OPERATION.get() is h.states[1] and h.states[0].closed
        hooks.append(len(h.calls))

    monkeypatch.setattr(f.backend, "execute_pages", execute_pages)
    pages = f.proxy.query_items_change_feed(
        start_time=datetime(2025, 1, 1, tzinfo=timezone.utc), timeout=10, response_hook=hook
    ).by_page()
    assert f.next_page(pages) == [{"id": "b"}]
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 2
    assert deadlines[0] == deadlines[1] and h.calls[1][3] < h.calls[0][3]
    assert hooks == [2]


@pytest.mark.parametrize("failure", ["service", "transport", "timeout", "parse", "hook", "hook-stop"])
@pytest.mark.parametrize("timeout", [None, 10])
def test_failed_poll_preserves_last_delivered_checkpoint(polling, recording, failure, timeout):
    h, f = polling, polling.feed
    hook = Mock()
    pages = f.proxy.query_items_change_feed(timeout=timeout, response_hook=hook).by_page()
    f.next_page(pages)
    token = pages.continuation_token
    error = None
    if failure == "service":
        f.status, expected = 503, CosmosHttpResponseError
    elif failure == "transport":
        h.error, expected = DriverTransportError("failed"), ServiceResponseError
    elif failure == "timeout":
        h.error, expected = TimeoutError("timed out"), CosmosClientTimeoutError if timeout else TimeoutError
    elif failure == "parse":
        h.transform = lambda value: ((200, 0, {}, b"invalid-json", None), value[1])
        expected = json.JSONDecodeError
    else:
        error = StopAsyncIteration("hook stopped") if failure == "hook-stop" else ValueError("hook failed")
        hook.side_effect = error
        expected = RuntimeError if failure == "hook-stop" else ValueError
    with pytest.raises(expected) as caught:
        f.next_page(pages)
    if failure == "hook":
        assert caught.value is error
    if failure == "hook-stop":
        assert caught.value.__cause__ is error
    if failure in ("service", "transport") or (failure == "timeout" and timeout):
        assert caught.value.continuation_token == token
    assert pages.continuation_token == token and pages.state.failed
    assert h.seen[-1].outcome == "error" and not h.seen[-1].diagnostics.complete
    assert fetch_spans(recording)[-1].status.status_code is trace.StatusCode.ERROR
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 2
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("detail", ["missing", "malformed", "reporting", "invalid-response"])
def test_diagnostic_failure_does_not_change_poll_result(polling, recording, monkeypatch, detail):
    h, f = polling, polling.feed
    if detail == "missing":
        h.transform = lambda value: (value[0], None)
    elif detail == "malformed":
        h.transform = lambda value: (value[0], {"schema_version": 99})
    elif detail == "invalid-response":
        h.transform = lambda _: ("invalid",)
    else:
        monkeypatch.setattr(telemetry, "emit_attempts", Mock(side_effect=RuntimeError("reporting failed")))
        f.proxy._item_context = replace(
            f.proxy._item_context,
            telemetry_handlers=(
                telemetry.CompletionHandler(Mock(side_effect=ValueError("handler failed"))),
                telemetry.CompletionHandler(h.seen.append),
            ),
        )
    pages = f.proxy.query_items_change_feed().by_page()
    if detail == "invalid-response":
        with pytest.raises(BindingProtocolError):
            f.next_page(pages)
    else:
        assert f.next_page(pages) == [{"id": "a", "nested": [1]}]
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1
    assert h.seen[0].outcome == ("error" if detail == "invalid-response" else "success")
    assert not any(k.startswith("cosmos.poc.") for k in fetch_spans(recording)[0].attributes)


def test_setup_retry_keeps_cursor_and_separate_completions(polling, recording):
    h, f = polling, polling.feed
    f.setup_status = 503
    pages = f.proxy.query_items_change_feed().by_page()
    with pytest.raises(CosmosHttpResponseError):
        f.next_page(pages)
    cursor = pages.state.cursor
    assert cursor is not None and not pages.state.failed
    f.setup_status = 0
    assert f.next_page(pages) == [{"id": "a", "nested": [1]}]
    assert all(call[1] is cursor for call in h.calls)
    assert [c.outcome for c in h.seen] == ["error", "success"]
    assert len(fetch_spans(recording)) == 2


def test_delete_record_keeps_all_versions_shape(polling, recording):
    h, f = polling, polling.feed
    record = {"current": {}, "previous": {"id": "a"}, "metadata": {"operationType": "delete"}}
    f.pages[0] = ([record], "c1.a")
    rows = f.next_page(f.proxy.query_items_change_feed(mode="AllVersionsAndDeletes").by_page())
    assert rows == [record]
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1
    assert h.seen[0].outcome == "success" and not h.seen[0].diagnostics.complete


def test_pinned_backend_and_consumption_settings(polling, recording):
    h, f = polling, polling.feed
    f.pages[0] = ([{"current": {"id": "a"}}, {"current": {"id": "b"}}], "c1.a")
    settings.tracing_enabled = False
    pager = f.proxy.query_items_change_feed(partition_key="private-customer")
    f.proxy._item_context = replace(f.proxy._item_context, adapter=Mock(), telemetry_handlers=())
    settings.tracing_enabled = True
    assert (asyncio.run(pager.__anext__()) if f.async_mode else next(pager)) == {"id": "a"}
    assert (asyncio.run(pager.__anext__()) if f.async_mode else next(pager)) == {"id": "b"}
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1
    assert h.states[0].backend is f.backend and h.states[0].closed
    for span in (*fetch_spans(recording), *attempt_spans(recording)):
        assert "private-customer" not in repr(span.attributes) + repr(span.events)


def test_disabled_poll_does_not_import_opentelemetry(polling, monkeypatch):
    h, f = polling, polling.feed
    settings.tracing_enabled = False
    f.proxy._item_context = replace(f.proxy._item_context, telemetry_handlers=())
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        assert not name.startswith("opentelemetry")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    assert f.next_page(f.proxy.query_items_change_feed().by_page()) == [{"id": "a", "nested": [1]}]
    assert not h.calls[0][2] and not h.seen


@pytest.mark.parametrize("timeout", [None, 10])
def test_cancellation_drains_poll_before_completion(polling, recording, timeout):
    h, f = polling, polling.feed
    if not f.async_mode:
        pytest.skip("Async cancellation")

    async def run():
        pages = f.proxy.query_items_change_feed(timeout=timeout).by_page()
        await pages.__anext__()
        token = pages.continuation_token
        h.gate = asyncio.Event()
        task = asyncio.create_task(pages.__anext__())
        await h.gate.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert h.drained and pages.state.failed and pages.state.cursor is None
        assert pages.continuation_token == token and h.seen[-1].outcome == "cancelled"
        assert h.states[-1].closed and not h.states[-1].delegated_tasks
        assert len(h.calls) == len(fetch_spans(recording)) == 2
        assert telemetry._OPERATION.get() is None

    asyncio.run(run())


@pytest.mark.parametrize("enabled", [False, True])
def test_poll_masks_outer_completion_state(polling, recording, enabled):
    h, f = polling, polling.feed
    with telemetry._operation_scope(f.proxy, "outer", {}, "query_items_change_feed"):
        outer = telemetry._OPERATION.get()
        f.proxy._item_context = replace(f.proxy._item_context, telemetry_handlers=())
        settings.tracing_enabled = enabled
        f.next_page(f.proxy.query_items_change_feed().by_page())
        assert telemetry._OPERATION.get() is outer and outer.collector.contributions == 0
        assert h.states[0] is not outer
    assert not h.seen and len(fetch_spans(recording)) == int(enabled)


def test_nested_poll_hook_keeps_completion_state_separate(polling, recording):
    h, f = polling, polling.feed
    if f.async_mode:
        pytest.skip("Synchronous nested poll inside a synchronous hook")
    f.proxy._item_context = replace(
        f.proxy._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(h.seen.append, collect_attempts=True),),
    )

    def hook(_headers, _body):
        outer = telemetry._OPERATION.get()
        assert f.next_page(f.proxy.query_items_change_feed().by_page()) == [{"id": "a", "nested": [1]}]
        assert telemetry._OPERATION.get() is outer and not outer.closed

    f.next_page(f.proxy.query_items_change_feed(response_hook=hook).by_page())
    assert len(h.calls) == len(h.seen) == 2
    assert h.states[0] is not h.states[1] and all(s.closed for s in h.states)
    assert all(c.diagnostics.request_count == 5 for c in h.seen)
    assert len(fetch_spans(recording)) == 1
