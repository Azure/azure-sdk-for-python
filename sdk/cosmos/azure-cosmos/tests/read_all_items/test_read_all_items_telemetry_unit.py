# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retained read-all telemetry owns each internal fetch and its final hook."""

import asyncio
import builtins
from dataclasses import replace
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
from read_all_items.test_read_all_items_contract_unit import feed  # pylint: disable=unused-import
from azure.core.exceptions import ServiceResponseError
from azure.core.settings import settings
from azure.cosmos import _telemetry as telemetry
from azure.cosmos._backend import binding_adapter as sync_binding
from azure.cosmos.aio._backend import binding_adapter as async_binding
from azure.cosmos._backend.errors import BindingProtocolError
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError

# pylint: enable=wrong-import-position


@pytest.fixture(name="reading")
def read_all_setup(recording, feed, monkeypatch):  # pylint: disable=unused-argument,redefined-outer-name
    h = SimpleNamespace(
        feed=feed,
        calls=[],
        states=[],
        seen=[],
        error=None,
        gate=None,
        drained=False,
        local_exhaustion=False,
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
        payload["complete"] = not cursor.can_retry_setup
        if h.error:
            if include_attempts:
                h.error._cosmos_attempt_payload = payload
            raise h.error
        response = original(handle, prepared, cursor, timeout_seconds=timeout_seconds)
        if h.local_exhaustion and prepared.settings.query.continuation == "c1.c":
            response, payload = (200, 0, {}, b'{"Documents":[]}', None), None
        value = h.transform((response, payload))
        return value if include_attempts else value[0]

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
    return [s for s in recording.exporter.get_finished_spans() if s.name == "ContainerProxy.read_all_items.fetch"]


@pytest.mark.parametrize("mode", ["enabled", "disabled", "handler-only", "sampled-out", "no-handlers"])
@pytest.mark.parametrize("timeout", [None, 10])
def test_internal_fetch_owns_diagnostics_and_final_hook(
    reading, recording, mode, timeout
):  # pylint: disable=too-many-statements
    h, f = reading, reading.feed
    if mode in ("disabled", "handler-only"):
        settings.tracing_enabled = False
    if mode == "sampled-out":
        recording.provider.sampler = ALWAYS_OFF
    f.proxy._item_context = replace(
        f.proxy._item_context,
        telemetry_handlers=(
            ()
            if mode == "no-handlers"
            else (telemetry.CompletionHandler(h.seen.append, collect_attempts=mode == "handler-only"),)
        ),
    )
    hooks = []

    def hook(headers, body):
        state = telemetry._OPERATION.get()
        assert state is h.states[-1]
        assert state is None or not state.closed
        hooks.append((dict(headers), len(h.calls)))
        headers.clear()
        body["Documents"].clear()

    with trace.get_tracer("customer").start_as_current_span("prepare"):
        iterable = f.proxy.read_all_items(max_item_count=1, timeout=timeout, response_hook=hook)
    assert not h.calls and not h.seen and not fetch_spans(recording)
    pages = iterable.by_page()
    parents = []
    for expected, fetch_count in (([{"id": "a", "nested": [1]}], 1), ([{"id": "b"}], 2)):
        with trace.get_tracer("customer").start_as_current_span("consume") as consumer:
            assert f.next_page(pages) == expected
            parents.extend([consumer.get_span_context().span_id] * fetch_count)
            assert trace.get_current_span() is consumer
        assert telemetry._OPERATION.get() is None
    assert [count for _, count in hooks] == [1, 3]
    assert [float(headers["x-ms-request-charge"]) for headers, _ in hooks] == [2, 4]
    with trace.get_tracer("customer").start_as_current_span("exhaust") as consumer:
        with pytest.raises(StopAsyncIteration if f.async_mode else StopIteration):
            f.next_page(pages)
        parents.append(consumer.get_span_context().span_id)
    assert len(h.calls) == 4 and len(hooks) == 3
    assert pages.state.token is None
    assert pages.continuation_token == "c1.c"
    with pytest.raises(StopAsyncIteration if f.async_mode else StopIteration):
        f.next_page(pages)
    assert len(h.calls) == 4
    assert len({id(call[1]) for call in h.calls}) == 1
    collect = mode in ("enabled", "handler-only", "no-handlers")
    assert all(call[2] == collect for call in h.calls)
    assert len(h.seen) == (0 if mode == "no-handlers" else 4)
    assert all(c.operation == "read_all_items" and c.outcome == "success" for c in h.seen)
    assert all((c.diagnostics is not None) == collect for c in h.seen)
    if h.seen and collect:
        assert [c.diagnostics.complete for c in h.seen] == [False, True, True, True]
    spans = fetch_spans(recording)
    assert len(spans) == (4 if mode in ("enabled", "no-handlers") else 0)
    if spans:
        assert [s.parent.span_id for s in spans] == parents
        assert not any(key.startswith("cosmos.poc.") for key in spans[0].attributes)
        assert all(s.attributes["cosmos.poc.request_count"] == 5 for s in spans[1:])
        assert all(s.status.status_code is trace.StatusCode.UNSET for s in spans)
        assert all(
            len([a for a in attempt_spans(recording) if a.parent.span_id == s.context.span_id]) == 2 for s in spans
        )
    f.connection.ReadItems.assert_not_called()
    f.binding.read_all_items.assert_not_called()
    f.binding.read_all_items_async.assert_not_called()


def test_empty_fetches_share_deadline_and_local_exhaustion_is_not_a_response(reading, recording, monkeypatch):
    h, f = reading, reading.feed
    h.local_exhaustion = True
    f.delay = 1
    deadlines = []
    original = f.backend.execute_pages

    def execute_pages(*args, **kwargs):
        deadlines.append(kwargs["deadline"])
        return original(*args, **kwargs)

    monkeypatch.setattr(f.backend, "execute_pages", execute_pages)
    hook = Mock()
    assert f.collect(f.proxy.read_all_items(timeout=10, response_hook=hook)) == [
        {"id": "a", "nested": [1]},
        {"id": "b"},
    ]
    assert hook.call_count == 2
    assert deadlines[1] == deadlines[2]
    assert h.calls[2][3] < h.calls[1][3]
    assert len(fetch_spans(recording)) == 4
    assert h.seen[-1].outcome == "success"
    assert not any(key.startswith("cosmos.poc.") for key in fetch_spans(recording)[-1].attributes)
    assert not [a for a in attempt_spans(recording) if a.parent.span_id == fetch_spans(recording)[-1].context.span_id]


@pytest.mark.parametrize("failure", ["service", "transport", "timeout", "parse", "hook", "hook-stop"])
@pytest.mark.parametrize("timeout", [None, 10])
def test_fetch_errors_preserve_customer_outcome(reading, recording, failure, timeout):
    h, f = reading, reading.feed
    kwargs = {"timeout": timeout}
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
        error = StopIteration("hook stopped") if failure == "hook-stop" else ValueError("hook failed")
        expected = RuntimeError if failure == "hook-stop" else ValueError
        kwargs["response_hook"] = Mock(side_effect=error)
    pages = f.proxy.read_all_items(**kwargs).by_page()
    with pytest.raises(expected) as caught:
        f.next_page(pages)
    if failure == "hook":
        assert caught.value is error
    if failure == "hook-stop":
        assert caught.value.__cause__ is error
    if failure == "transport" or (failure == "timeout" and timeout):
        assert caught.value.__cause__ is h.error
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1
    assert h.seen[0].outcome == "error" and not h.seen[0].diagnostics.complete
    assert fetch_spans(recording)[0].status.status_code is trace.StatusCode.ERROR
    assert telemetry._OPERATION.get() is None


def test_retryable_setup_error_has_separate_completion(reading, recording):
    h, f = reading, reading.feed
    f.setup_status = 503
    pages = f.proxy.read_all_items().by_page()
    with pytest.raises(CosmosHttpResponseError):
        f.next_page(pages)
    cursor = pages.state.cursor
    assert cursor is not None and not pages.state.failed
    f.setup_status = 0
    assert f.next_page(pages) == [{"id": "a", "nested": [1]}]
    assert [c.outcome for c in h.seen] == ["error", "success"]
    assert all(not c.diagnostics.complete for c in h.seen)
    assert all(call[1] is cursor for call in h.calls)
    assert len(fetch_spans(recording)) == 2


@pytest.mark.parametrize("detail", ["missing", "malformed", "partial", "reporting", "invalid-response"])
def test_diagnostics_failure_does_not_change_paging(reading, recording, monkeypatch, detail):
    h, f = reading, reading.feed
    if detail == "missing":
        h.transform = lambda value: (value[0], None)
    elif detail == "malformed":
        h.transform = lambda value: (value[0], {"schema_version": 99})
    elif detail == "partial":
        h.transform = lambda value: (value[0], {**value[1], "complete": False})
    elif detail == "invalid-response":
        h.transform = lambda _: ("invalid",)
    else:
        monkeypatch.setattr(telemetry, "emit_attempts", Mock(side_effect=RuntimeError("recording failed")))
        f.proxy._item_context = replace(
            f.proxy._item_context,
            telemetry_handlers=(
                telemetry.CompletionHandler(Mock(side_effect=ValueError("handler failed"))),
                telemetry.CompletionHandler(h.seen.append),
            ),
        )
    pages = f.proxy.read_all_items().by_page("c1.b")
    if detail == "invalid-response":
        with pytest.raises(BindingProtocolError):
            f.next_page(pages)
    else:
        assert f.next_page(pages) == [{"id": "b"}]
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1
    assert h.seen[0].outcome == ("error" if detail == "invalid-response" else "success")
    assert not any(key.startswith("cosmos.poc.") for key in fetch_spans(recording)[0].attributes)
    assert len(attempt_spans(recording)) == (2 if detail == "partial" else 0)


def test_replay_pins_backend_and_handlers_but_uses_consumption_settings(reading, recording):
    h, f = reading, reading.feed
    settings.tracing_enabled = False
    iterable = f.proxy.read_all_items()
    original = f.proxy._item_context
    f.proxy._item_context = replace(original, adapter=Mock(name="replacement"), telemetry_handlers=())
    settings.tracing_enabled = True
    pages = iterable.by_page()
    assert f.next_page(pages) == [{"id": "a", "nested": [1]}]
    token = pages.continuation_token
    assert f.next_page(pages) == [{"id": "b"}]
    assert f.next_page(iterable.by_page(token)) == [{"id": "b"}]
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 5
    assert h.calls[0][1] is not h.calls[3][1]
    assert [c.diagnostics.complete for c in h.seen] == [False, True, True, False, True]
    assert all(state.backend is f.backend and state.closed for state in h.states)
    settings.tracing_enabled = False
    assert f.next_page(iterable.by_page()) == [{"id": "a", "nested": [1]}]
    assert not h.calls[-1][2] and len(fetch_spans(recording)) == 5


def test_disabled_recording_does_not_import_opentelemetry(reading, monkeypatch):
    h, f = reading, reading.feed
    settings.tracing_enabled = False
    f.proxy._item_context = replace(f.proxy._item_context, telemetry_handlers=())
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        assert not name.startswith("opentelemetry")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    assert f.next_page(f.proxy.read_all_items().by_page()) == [{"id": "a", "nested": [1]}]
    assert not h.calls[0][2] and not h.seen


def test_partial_iteration_does_not_record_each_returned_item(reading, recording):
    h, f = reading, reading.feed
    f.pages[0] = ([{"id": "a"}, {"id": "b"}], "c1.a")
    iterable = f.proxy.read_all_items()
    first = asyncio.run(iterable.__anext__()) if f.async_mode else next(iterable)
    assert first == {"id": "a"}
    assert len(h.calls) == len(fetch_spans(recording)) == 1
    assert h.states[0].closed and telemetry._OPERATION.get() is None
    second = asyncio.run(iterable.__anext__()) if f.async_mode else next(iterable)
    assert second == {"id": "b"}
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1


def test_stateless_binding_does_not_receive_attempt_flag(reading):
    f = reading.feed
    pages = f.proxy.read_all_items().by_page()
    assert f.next_page(pages) == [{"id": "a", "nested": [1]}]
    prepared = replace(pages.state.config.prepared(None, pages.state.cursor, None), cursor=None)
    response = (200, 0, {}, b'{"Documents":[]}', None)
    binding = f.binding.read_all_items_async if f.async_mode else f.binding.read_all_items
    binding.return_value = response

    async def fetch():
        return [page async for page in f.backend.execute_pages(prepared)]

    with telemetry._operation_scope(f.proxy, "outer", {}, "read_all_items"):
        outer = telemetry._OPERATION.get()
        if f.async_mode:
            asyncio.run(fetch())
        else:
            list(f.backend.execute_pages(prepared))
        assert outer.collector.contributions == 0
    assert "include_attempts" not in binding.call_args.kwargs


def test_nested_hook_does_not_contribute_to_outer_fetch(reading, recording):
    h, f = reading, reading.feed
    if f.async_mode:
        pytest.skip("Synchronous nested fetch in a synchronous hook")
    f.proxy._item_context = replace(
        f.proxy._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(h.seen.append, collect_attempts=True),),
    )

    def hook(_headers, _body):
        outer = telemetry._OPERATION.get()
        assert f.next_page(f.proxy.read_all_items().by_page("c1.b")) == [{"id": "b"}]
        assert telemetry._OPERATION.get() is outer and not outer.closed

    assert f.next_page(f.proxy.read_all_items(response_hook=hook).by_page()) == [{"id": "a", "nested": [1]}]
    assert len(h.calls) == len(h.seen) == 2
    assert h.states[0] is not h.states[1] and all(s.closed for s in h.states)
    assert all(c.diagnostics.request_count == 5 for c in h.seen)
    assert len(fetch_spans(recording)) == 1


@pytest.mark.parametrize("option", ["tracing_options", "tracing_attributes"])
def test_unsupported_tracing_arguments_remain_unsupported(reading, recording, option):
    with pytest.raises(NotImplementedError):
        reading.feed.proxy.read_all_items(**{option: {}})
    assert not reading.calls and not reading.seen and not fetch_spans(recording)


@pytest.mark.parametrize("enabled", [False, True])
def test_fetch_masks_unrelated_outer_operation(reading, recording, enabled):
    h, f = reading, reading.feed
    with telemetry._operation_scope(f.proxy, "outer", {}, "read_all_items"):
        outer = telemetry._OPERATION.get()
        f.proxy._item_context = replace(f.proxy._item_context, telemetry_handlers=())
        settings.tracing_enabled = enabled
        assert f.next_page(f.proxy.read_all_items().by_page()) == [{"id": "a", "nested": [1]}]
        assert telemetry._OPERATION.get() is outer
        assert h.states[0] is not outer and outer.collector.contributions == 0
    assert not h.seen and h.calls[0][2] == enabled
    assert len(fetch_spans(recording)) == int(enabled)


@pytest.mark.parametrize("timeout", [None, 10])
def test_cancellation_drains_authorized_fetch_and_invalidates_cursor(reading, recording, timeout):
    h, f = reading, reading.feed
    if not f.async_mode:
        pytest.skip("Async cancellation")

    async def run():
        h.gate = asyncio.Event()
        pages = f.proxy.read_all_items(timeout=timeout).by_page()
        task = asyncio.create_task(pages.__anext__())
        await h.gate.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert h.drained and pages.state.failed and pages.state.cursor is None
        assert h.seen[0].outcome == "cancelled"
        assert h.states[0].closed and not h.states[0].delegated_tasks
        assert len(h.calls) == len(fetch_spans(recording)) == 1
        with pytest.raises(RuntimeError, match="pager failed"):
            await pages.__anext__()
        assert len(h.calls) == 1 and telemetry._OPERATION.get() is None

    asyncio.run(run())
