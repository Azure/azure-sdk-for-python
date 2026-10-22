# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Record retained item-query fetches without changing query progress."""

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
from common.test_list_databases_telemetry_unit import DriverUnsupportedQueryError
from query_items.test_query_items_contract_unit import query  # pylint: disable=unused-import
from azure.core.exceptions import ServiceResponseError
from azure.core.settings import settings
from azure.cosmos import _telemetry as telemetry
from azure.cosmos._backend import binding_adapter as sync_binding
from azure.cosmos.aio._backend import binding_adapter as async_binding
from azure.cosmos._backend.errors import BindingProtocolError, UnsupportedQueryError
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError

# pylint: enable=wrong-import-position


@pytest.fixture(name="querying")
def query_setup(recording, query, monkeypatch):  # pylint: disable=unused-argument,redefined-outer-name
    h = SimpleNamespace(
        feed=query,
        calls=[],
        states=[],
        seen=[],
        error=None,
        gate=None,
        drained=False,
        transform=lambda value: value,
    )
    query.proxy._item_context = replace(
        query.proxy._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(h.seen.append),),
    )
    module = async_binding if query.async_mode else sync_binding
    monkeypatch.setattr(module, "_DRIVER_TRANSPORT_ERROR", DriverTransportError)
    monkeypatch.setattr(module, "_UNSUPPORTED_QUERY_ERROR", DriverUnsupportedQueryError)
    original = query.binding.fetch_page_with_cursor.side_effect

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
        if response[0] == 200 and not cursor.has_more and not response[2]:
            payload = None
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

    query.binding.fetch_page_with_cursor.side_effect = native
    query.binding.fetch_page_with_cursor_async.side_effect = native_async
    return h


def fetch_spans(recording):
    return [s for s in recording.exporter.get_finished_spans() if s.name == "ContainerProxy.query_items.fetch"]


@pytest.mark.parametrize("mode", ["enabled", "disabled", "handler-only", "sampled-out", "no-handlers"])
@pytest.mark.parametrize("resumable", [False, True])
@pytest.mark.parametrize("timeout", [None, 10])
def test_each_internal_fetch_owns_query_progress_and_final_hook(
    querying, recording, mode, resumable, timeout
):  # pylint: disable=too-many-statements
    h, f = querying, querying.feed
    f.resumable = resumable
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
        assert state is h.states[-1] and (state is None or not state.closed)
        assert pages.state.last_delivered_continuation_token == (None if len(h.calls) == 1 or not resumable else "c1.1")
        hooks.append((dict(headers), len(h.calls)))
        headers.clear()
        body["Documents"].clear()

    with trace.get_tracer("customer").start_as_current_span("prepare"):
        iterable = f.proxy.query_items("SELECT VALUE c.result FROM c", timeout=timeout, response_hook=hook)
    assert not h.calls and not h.seen and not fetch_spans(recording)
    pages = iterable.by_page()
    parents = []
    for expected, count in (([{"id": "a", "nested": [1]}], 1), ([7, None, ["value"], "text"], 2)):
        with trace.get_tracer("customer").start_as_current_span("consume") as consumer:
            assert f.next_page(pages) == expected
            parents.extend([consumer.get_span_context().span_id] * count)
            assert trace.get_current_span() is consumer
        assert telemetry._OPERATION.get() is None
    if resumable:
        assert pages.continuation_token == "c1.3"
    else:
        with pytest.raises(NotImplementedError, match="cannot bookmark"):
            _ = pages.continuation_token
    assert [count for _, count in hooks] == [1, 3]
    assert [float(headers["x-ms-request-charge"]) for headers, _ in hooks] == [2, 4]
    with trace.get_tracer("customer").start_as_current_span("exhaust") as consumer:
        with pytest.raises(StopAsyncIteration if f.async_mode else StopIteration):
            f.next_page(pages)
        parents.append(consumer.get_span_context().span_id)
    assert len(h.calls) == 4 and len(hooks) == 2
    assert pages.state.done and pages.state.cursor is None
    with pytest.raises(StopAsyncIteration if f.async_mode else StopIteration):
        f.next_page(pages)
    assert len(h.calls) == 4
    collect = mode in ("enabled", "handler-only", "no-handlers")
    assert all(call[2] == collect for call in h.calls)
    assert len({id(call[1]) for call in h.calls}) == 1
    assert len(h.seen) == (0 if mode == "no-handlers" else 4)
    assert all(c.operation == "query_items" and c.outcome == "success" for c in h.seen)
    if h.seen and collect:
        assert [c.diagnostics.complete for c in h.seen[:3]] == [False, True, True]
    spans = fetch_spans(recording)
    assert len(spans) == (4 if mode in ("enabled", "no-handlers") else 0)
    if spans:
        assert [s.parent.span_id for s in spans] == parents
        assert all(s.status.status_code is trace.StatusCode.UNSET for s in spans)
        assert not any(k.startswith("cosmos.poc.") for s in (spans[0], spans[-1]) for k in s.attributes)
        assert all(s.attributes["cosmos.poc.request_count"] == 5 for s in spans[1:3])
        attempts = attempt_spans(recording)
        assert [sum(a.parent.span_id == s.context.span_id for a in attempts) for s in spans] == [2, 2, 2, 0]
    f.binding.query_items.assert_not_called()
    f.binding.query_items_async.assert_not_called()
    assert not f.connection.mock_calls


@pytest.mark.parametrize("token_prefix", ["c1.", ""])
def test_replay_and_copied_query_inputs_keep_independent_diagnostics(querying, recording, token_prefix):
    h, f = querying, querying.feed
    f.token_prefix = token_prefix
    parameters = [{"name": "@id", "value": {"nested": ["private-order"]}}]
    sql = "SELECT * FROM c WHERE c.id = @id"
    specification = {"query": sql, "parameters": parameters}
    iterable = f.proxy.query_items(specification, partition_key="customer-17")
    parameters[0]["value"]["nested"].clear()
    specification["query"] = "changed"
    pages = iterable.by_page()
    assert f.next_page(pages) == [{"id": "a", "nested": [1]}]
    token = pages.continuation_token
    expected = [7, None, ["value"], "text"]
    assert f.next_page(pages) == f.next_page(iterable.by_page(token)) == expected
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 5
    assert h.calls[0][1] is not h.calls[3][1]
    assert [c.diagnostics.complete for c in h.seen] == [False, True, True, False, True]
    for prepared, _, _, _ in h.calls:
        assert json.loads(prepared.body_bytes) == {
            "query": sql,
            "parameters": [{"name": "@id", "value": {"nested": ["private-order"]}}],
        }
    for span in (*fetch_spans(recording), *attempt_spans(recording)):
        recorded = repr(span.attributes) + repr(span.events)
        assert sql not in recorded and "private-order" not in recorded and "customer-17" not in recorded


@pytest.mark.parametrize("failure", ["service", "transport", "unsupported", "timeout", "parse", "hook", "hook-stop"])
@pytest.mark.parametrize("timeout", [None, 10])
def test_query_failures_preserve_error_and_last_delivered_bookmark(querying, recording, failure, timeout):
    h, f = querying, querying.feed
    hook = Mock()
    pages = f.proxy.query_items("SELECT * FROM c", timeout=timeout, response_hook=hook).by_page()
    assert f.next_page(pages) == [{"id": "a", "nested": [1]}]
    error = None
    if failure == "service":
        f.status, expected = 503, CosmosHttpResponseError
    elif failure == "transport":
        h.error, expected = DriverTransportError("failed"), ServiceResponseError
    elif failure == "unsupported":
        h.error, expected = DriverUnsupportedQueryError("unsupported"), UnsupportedQueryError
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
        assert caught.value.continuation_token == "c1.1"
    if failure in ("transport", "unsupported") or (failure == "timeout" and timeout):
        assert caught.value.__cause__ is h.error
    assert pages.continuation_token == "c1.1" and pages.state.failed
    assert h.seen[-1].outcome == "error" and h.seen[-1].diagnostics.request_count == 5
    assert fetch_spans(recording)[-1].status.status_code is trace.StatusCode.ERROR
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording))
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("detail", ["missing", "malformed", "partial", "reporting", "invalid-response"])
def test_diagnostic_failures_do_not_change_query_outcomes(querying, recording, monkeypatch, detail):
    h, f = querying, querying.feed
    if detail == "missing":
        h.transform = lambda value: (value[0], None)
    elif detail == "malformed":
        h.transform = lambda value: (value[0], {"schema_version": 99})
    elif detail == "partial":
        h.transform = lambda value: (value[0], {**value[1], "complete": False})
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
    pages = f.proxy.query_items("SELECT * FROM c").by_page()
    if detail == "invalid-response":
        with pytest.raises(BindingProtocolError):
            f.next_page(pages)
    else:
        assert f.next_page(pages) == [{"id": "a", "nested": [1]}]
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1
    assert h.seen[0].outcome == ("error" if detail == "invalid-response" else "success")
    assert not any(k.startswith("cosmos.poc.") for k in fetch_spans(recording)[0].attributes)
    assert len(attempt_spans(recording)) == (2 if detail == "partial" else 0)


def test_setup_retry_and_one_budget_across_empty_fetches(querying, recording, monkeypatch):
    h, f = querying, querying.feed
    deadlines = []
    original = f.backend.execute_pages

    def execute_pages(*args, **kwargs):
        deadlines.append(kwargs["deadline"])
        return original(*args, **kwargs)

    monkeypatch.setattr(f.backend, "execute_pages", execute_pages)
    f.setup_status = 503
    pages = f.proxy.query_items("SELECT * FROM c", timeout=10).by_page()
    with pytest.raises(CosmosHttpResponseError):
        f.next_page(pages)
    cursor = pages.state.cursor
    assert cursor is not None and not pages.state.failed
    f.setup_status, f.delay = 0, 1
    assert f.next_page(pages) == [{"id": "a", "nested": [1]}]
    assert f.next_page(pages) == [7, None, ["value"], "text"]
    assert all(call[1] is cursor for call in h.calls)
    assert deadlines[2] == deadlines[3] and h.calls[3][3] < h.calls[2][3]
    assert [c.outcome for c in h.seen] == ["error", "success", "success", "success"]
    assert [c.diagnostics.complete for c in h.seen] == [False, False, True, True]
    assert len(fetch_spans(recording)) == 4


def test_pinned_backend_and_partial_iteration_use_consumption_settings(querying, recording):
    h, f = querying, querying.feed
    f.pages[0] = [{"id": "a"}, {"id": "b"}]
    settings.tracing_enabled = False
    iterable = f.proxy.query_items("SELECT * FROM c")
    f.proxy._item_context = replace(f.proxy._item_context, adapter=Mock(), telemetry_handlers=())
    settings.tracing_enabled = True
    first = asyncio.run(iterable.__anext__()) if f.async_mode else next(iterable)
    assert first == {"id": "a"} and h.states[0].closed
    second = asyncio.run(iterable.__anext__()) if f.async_mode else next(iterable)
    assert second == {"id": "b"} and len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1
    assert h.states[0].backend is f.backend and telemetry._OPERATION.get() is None
    settings.tracing_enabled = False
    assert f.next_page(iterable.by_page()) == [{"id": "a"}, {"id": "b"}]
    assert not h.calls[-1][2] and len(fetch_spans(recording)) == 1


def test_stateless_query_does_not_receive_attempt_flag(querying):
    h, f = querying, querying.feed
    pages = f.proxy.query_items("SELECT * FROM c").by_page()
    f.next_page(pages)
    prepared = replace(pages.state.config.prepared(None, pages.state.cursor, None), cursor=None)
    binding = f.binding.query_items_async if f.async_mode else f.binding.query_items
    binding.return_value = (200, 0, {}, b'{"Documents":[]}', None)

    async def fetch():
        return [page async for page in f.backend.execute_pages(prepared)]

    with telemetry._operation_scope(f.proxy, "outer", {}, "query_items"):
        outer = telemetry._OPERATION.get()
        if f.async_mode:
            asyncio.run(fetch())
        else:
            list(f.backend.execute_pages(prepared))
        assert outer.collector.contributions == 0
    assert "include_attempts" not in binding.call_args.kwargs
    assert len(h.calls) == 1


def test_disabled_query_recording_does_not_import_opentelemetry(querying, monkeypatch):
    h, f = querying, querying.feed
    settings.tracing_enabled = False
    f.proxy._item_context = replace(f.proxy._item_context, telemetry_handlers=())
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        assert not name.startswith("opentelemetry")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    assert f.next_page(f.proxy.query_items("SELECT * FROM c").by_page()) == [{"id": "a", "nested": [1]}]
    assert not h.calls[0][2] and not h.seen


@pytest.mark.parametrize("enabled", [False, True])
def test_query_fetch_masks_outer_state(querying, recording, enabled):
    h, f = querying, querying.feed
    with telemetry._operation_scope(f.proxy, "outer", {}, "query_items"):
        outer = telemetry._OPERATION.get()
        f.proxy._item_context = replace(f.proxy._item_context, telemetry_handlers=())
        settings.tracing_enabled = enabled
        f.next_page(f.proxy.query_items("SELECT * FROM c").by_page())
        assert telemetry._OPERATION.get() is outer and outer.collector.contributions == 0
        assert h.states[0] is not outer
    assert not h.seen and len(fetch_spans(recording)) == int(enabled)


def test_nested_query_hook_keeps_completion_state_separate(querying, recording):
    h, f = querying, querying.feed
    if f.async_mode:
        pytest.skip("Synchronous nested query inside a synchronous hook")
    f.proxy._item_context = replace(
        f.proxy._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(h.seen.append, collect_attempts=True),),
    )

    def hook(_headers, _body):
        outer = telemetry._OPERATION.get()
        assert f.next_page(f.proxy.query_items("SELECT * FROM c").by_page("c1.2")) == [7, None, ["value"], "text"]
        assert telemetry._OPERATION.get() is outer and not outer.closed

    f.next_page(f.proxy.query_items("SELECT * FROM c", response_hook=hook).by_page())
    assert len(h.calls) == len(h.seen) == 2
    assert h.states[0] is not h.states[1] and all(s.closed for s in h.states)
    assert all(c.diagnostics.request_count == 5 for c in h.seen)
    assert len(fetch_spans(recording)) == 1


@pytest.mark.parametrize("timeout", [None, 10])
def test_cancellation_drains_query_fetch_and_preserves_bookmark(querying, recording, timeout):
    h, f = querying, querying.feed
    if not f.async_mode:
        pytest.skip("Async cancellation")

    async def run():
        pages = f.proxy.query_items("SELECT * FROM c", timeout=timeout).by_page()
        await pages.__anext__()
        h.gate = asyncio.Event()
        task = asyncio.create_task(pages.__anext__())
        await h.gate.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert h.drained and pages.state.failed and pages.state.cursor is None
        assert pages.continuation_token == "c1.1"
        assert h.seen[-1].outcome == "cancelled"
        assert h.states[-1].closed and not h.states[-1].delegated_tasks
        assert len(h.calls) == len(fetch_spans(recording)) == 2
        assert telemetry._OPERATION.get() is None

    asyncio.run(run())
