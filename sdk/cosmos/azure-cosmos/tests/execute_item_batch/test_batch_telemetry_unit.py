# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep batch request diagnostics separate from the public transaction outcome."""

import asyncio
import builtins
from copy import deepcopy
from dataclasses import replace
import json
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

pytest.importorskip("opentelemetry.sdk.trace")
# pylint: disable=wrong-import-position
from opentelemetry import trace
from opentelemetry.sdk.trace.sampling import ALWAYS_OFF
from telemetry.test_rust_telemetry_unit import (  # pylint: disable=unused-import
    DriverTransportError,
    attempt_spans,
    contribution_response,
    recording_setup,
)
from azure.core.exceptions import ServiceResponseError
from azure.core.settings import settings
from azure.cosmos import _telemetry as telemetry
from azure.cosmos._backend import binding_adapter as sync_binding
from azure.cosmos.aio._backend import binding_adapter as async_binding
from azure.cosmos._backend.errors import BindingProtocolError
from azure.cosmos._helpers._item_context import ItemClientContext
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy
from azure.cosmos.exceptions import (
    CosmosBatchOperationError,
    CosmosClientTimeoutError,
    CosmosHttpResponseError,
    CosmosResourceNotFoundError,
)

# pylint: enable=wrong-import-position


class DriverResponseError(RuntimeError):
    """Stand in for the binding's typed metadata error."""


@pytest.fixture(name="batch", params=["sync", "async"])
def batch_setup(request, recording, monkeypatch):  # pylint: disable=unused-argument
    asynchronous = request.param == "async"
    module = async_binding if asynchronous else sync_binding
    cls = module.AsyncBindingAdapter if asynchronous else module.BindingAdapter
    backend = cls("https://batch.invalid", master_key="unused")
    h = SimpleNamespace(
        asynchronous=asynchronous,
        backend=backend,
        calls=[],
        states=[],
        seen=[],
        error=None,
        gate=None,
        drained=False,
        transform=lambda value: value,
        response=(
            200,
            0,
            {"x-ms-request-charge": "2", "x-ms-session-token": "session"},
            b'[{"statusCode":201,"resourceBody":{"id":"order-17"}}]',
            None,
        ),
    )
    context = ItemClientContext(backend, telemetry_handlers=(telemetry.CompletionHandler(h.seen.append),))
    h.connection = Mock()
    h.proxy = (AsyncContainerProxy if asynchronous else ContainerProxy)(
        h.connection, "dbs/sales", "orders", _item_context=context
    )
    monkeypatch.setattr(
        backend,
        "_ensure_driver_handle",
        (AsyncMock(return_value="handle") if asynchronous else Mock(return_value="handle")),
    )
    monkeypatch.setattr(module, "_DRIVER_TRANSPORT_ERROR", DriverTransportError)
    monkeypatch.setattr(module, "_DRIVER_RESPONSE_ERROR", DriverResponseError)

    def start(prepared, include_attempts, timeout_seconds):
        h.calls.append((prepared, include_attempts, timeout_seconds))
        h.states.append(telemetry._OPERATION.get())

    def finish(include_attempts):
        _, payload = contribution_response(5, time.time_ns())
        payload["complete"] = False
        payload["incomplete_reasons"] = ["metadata_diagnostics_unavailable"]
        if h.error is not None:
            if include_attempts:
                h.error._cosmos_attempt_payload = payload
            raise h.error
        result = h.transform((h.response, payload))
        return result if include_attempts else result[0]

    def native(_handle, prepared, *, include_attempts=False, timeout_seconds=None):
        start(prepared, include_attempts, timeout_seconds)
        return finish(include_attempts)

    async def native_async(_handle, prepared, *, include_attempts=False, timeout_seconds=None):
        start(prepared, include_attempts, timeout_seconds)
        if h.gate:
            h.gate.set()
            try:
                await asyncio.Future()
            finally:
                h.drained = True
        return finish(include_attempts)

    monkeypatch.setattr(
        module,
        "_rust_module",
        SimpleNamespace(
            execute_item_batch=native,
            execute_item_batch_async=native_async,
        ),
    )
    h.operations = [("create", ({"id": "order-17", "customerId": "customer-17"},))]

    def call(operations=None, **kwargs):
        result = h.proxy.execute_item_batch(h.operations if operations is None else operations, "customer-17", **kwargs)
        return asyncio.run(result) if asynchronous else result

    h.call = call
    yield h
    assert not h.connection.mock_calls
    if asynchronous:
        asyncio.run(backend.close())
    else:
        backend.close()


def operation_spans(recording):
    return [s for s in recording.exporter.get_finished_spans() if s.name == "ContainerProxy.execute_item_batch"]


@pytest.mark.parametrize("mode", ["enabled", "disabled", "handler-only", "sampled-out", "no-handlers"])
@pytest.mark.parametrize("timeout", [None, 10])
def test_batch_span_owns_preparation_result_and_hook_rust(batch, recording, mode, timeout):
    h = batch
    if mode in ("disabled", "handler-only"):
        settings.tracing_enabled = False
    if mode == "sampled-out":
        recording.provider.sampler = ALWAYS_OFF
    h.proxy._item_context = replace(
        h.proxy._item_context,
        telemetry_handlers=(
            ()
            if mode == "no-handlers"
            else (telemetry.CompletionHandler(h.seen.append, collect_attempts=mode == "handler-only"),)
        ),
    )
    original, hooks = deepcopy(h.operations), []

    def hook(headers, results):
        state = telemetry._OPERATION.get()
        assert state is h.states[0] and (state is None or not state.closed)
        assert not h.seen
        hooks.append((dict(headers), deepcopy(results)))

    with trace.get_tracer("customer").start_as_current_span("checkout") as parent:
        result = h.call(timeout=timeout, response_hook=hook)
        assert trace.get_current_span() is parent
    assert h.operations == original
    assert result == [{"statusCode": 201, "resourceBody": {"id": "order-17"}}]
    assert result.get_response_headers()["x-ms-request-charge"] == "2"
    assert len(hooks) == len(h.calls) == 1
    assert h.calls[0][1] == (mode in ("enabled", "handler-only", "no-handlers"))
    assert (h.calls[0][2] is None) == (timeout is None)
    assert json.loads(h.calls[0][0].body_bytes)[0]["operationType"] == "Create"
    assert len(h.seen) == (0 if mode == "no-handlers" else 1)
    if h.seen:
        assert h.seen[0].operation == "execute_item_batch" and h.seen[0].outcome == "success"
        if mode in ("enabled", "handler-only"):
            assert not h.seen[0].diagnostics.complete
        else:
            assert h.seen[0].diagnostics is None
    spans = operation_spans(recording)
    assert len(spans) == (1 if mode in ("enabled", "no-handlers") else 0)
    if spans:
        assert spans[0].parent.span_id == parent.get_span_context().span_id
        assert spans[0].status.status_code is trace.StatusCode.UNSET
        assert "azure.cosmosdb.operation.request_count" not in spans[0].attributes
        assert "azure.cosmosdb.operation.retained_request_count" not in spans[0].attributes
        assert spans[0].attributes["azure.cosmosdb.operation.diagnostics_complete"] is False
        assert len(attempt_spans(recording)) == 2
        assert all(s.parent.span_id == spans[0].context.span_id for s in attempt_spans(recording))
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("status", [400, 404, 409, 412])
def test_failed_operation_marks_public_span_not_successful_request_rust(batch, recording, status):
    results = [{"statusCode": 424}, {"statusCode": status}, {"statusCode": 424}]
    batch.response = (
        207,
        0,
        {"x-ms-request-charge": "3"},
        json.dumps(results).encode(),
        None,
    )
    hook = Mock()
    with pytest.raises(CosmosBatchOperationError) as caught:
        batch.call(response_hook=hook)
    assert caught.value.error_index == 1 and caught.value.status_code == status
    assert caught.value.operation_responses == results
    hook.assert_not_called()
    assert len(batch.calls) == len(batch.seen) == len(operation_spans(recording)) == 1
    assert batch.seen[0].outcome == "error"
    assert operation_spans(recording)[0].status.status_code is trace.StatusCode.ERROR
    assert len(attempt_spans(recording)) == 2
    assert not batch.seen[0].diagnostics.complete


@pytest.mark.parametrize(
    "failure",
    ["request", "metadata", "transport", "timeout", "parse", "hook", "no-cause"],
)
@pytest.mark.parametrize("timeout", [None, 10])
def test_errors_keep_type_cause_headers_and_no_replay_rust(batch, recording, failure, timeout):
    h, hook = batch, Mock()
    if failure == "request":
        h.response, expected = (
            503,
            0,
            {},
            b'{"message":"unavailable"}',
            None,
        ), CosmosHttpResponseError
    elif failure == "metadata":
        h.error = DriverResponseError((404, 0, {"x-ms-activity-id": "metadata"}, b'{"message":"missing"}', None))
        expected = CosmosResourceNotFoundError
        h.proxy._item_context.response_state.last_response_headers = {"old": "preserved"}
    elif failure == "transport":
        h.error, expected = DriverTransportError("failed"), ServiceResponseError
    elif failure == "timeout":
        h.error, expected = TimeoutError("expired"), (CosmosClientTimeoutError if timeout else TimeoutError)
    elif failure == "parse":
        h.response, expected = (200, 0, {}, b"invalid-json", None), json.JSONDecodeError
    elif failure == "no-cause":
        h.response, expected = (
            207,
            0,
            {},
            b'[{"statusCode":424}]',
            None,
        ), BindingProtocolError
    else:
        hook.side_effect, expected = ValueError("hook failed"), ValueError
    with pytest.raises(expected) as caught:
        h.call(timeout=timeout, response_hook=hook)
    if failure in ("metadata", "transport") or (failure == "timeout" and timeout):
        assert caught.value.__cause__ is h.error
    if failure == "metadata":
        assert caught.value.headers["x-ms-activity-id"] == "metadata"
        assert h.proxy._item_context.response_state.last_response_headers == {"old": "preserved"}
    if failure == "hook":
        assert caught.value is hook.side_effect
    else:
        hook.assert_not_called()
    assert len(h.calls) == len(h.seen) == len(operation_spans(recording)) == 1
    assert h.seen[0].outcome == "error" and h.seen[0].diagnostics.request_count == 5
    assert not h.seen[0].diagnostics.complete
    assert len(attempt_spans(recording)) == 2 and telemetry._OPERATION.get() is None


@pytest.mark.parametrize("detail", ["missing", "malformed", "reporting", "invalid-response"])
def test_reporting_failure_does_not_replace_batch_result_rust(batch, recording, monkeypatch, detail):
    h = batch
    if detail == "missing":
        h.transform = lambda value: (value[0], None)
    elif detail == "malformed":
        h.transform = lambda value: (value[0], {"schema_version": 99})
    elif detail == "invalid-response":
        h.transform = lambda _: ("invalid",)
    else:
        monkeypatch.setattr(telemetry, "emit_attempts", Mock(side_effect=RuntimeError("emit failed")))
        h.proxy._item_context = replace(
            h.proxy._item_context,
            telemetry_handlers=(
                telemetry.CompletionHandler(Mock(side_effect=RuntimeError("handler failed"))),
                telemetry.CompletionHandler(h.seen.append),
            ),
        )
    if detail == "invalid-response":
        with pytest.raises(BindingProtocolError):
            h.call()
    else:
        assert h.call()[0]["statusCode"] == 201
    assert len(h.calls) == len(h.seen) == len(operation_spans(recording)) == 1
    assert "azure.cosmosdb.operation.request_count" not in operation_spans(recording)[0].attributes
    assert "azure.cosmosdb.operation.retained_request_count" not in operation_spans(recording)[0].attributes


def test_invalid_input_creates_no_attempts_rust(batch, recording):
    with pytest.raises(TypeError, match="response_hook must be callable"):
        batch.call(response_hook=object())
    assert not batch.calls
    assert batch.seen[0].outcome == "error"
    assert not attempt_spans(recording)


def test_disabled_batch_does_not_import_opentelemetry_rust(batch, monkeypatch):
    settings.tracing_enabled = False
    batch.proxy._item_context = replace(batch.proxy._item_context, telemetry_handlers=())
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        assert not name.startswith("opentelemetry")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    assert batch.call()[0]["statusCode"] == 201
    assert not batch.calls[0][1] and not batch.seen


def test_batch_does_not_export_item_body_or_partition_key_rust(batch, recording):
    batch.call()
    for span in (*operation_spans(recording), *attempt_spans(recording)):
        text = repr(span.attributes) + repr(span.events)
        assert "order-17" not in text and "customer-17" not in text


def test_nested_hook_keeps_separate_completion_rust(batch, recording):
    if batch.asynchronous:
        pytest.skip("Synchronous nested batch inside a synchronous hook")
    batch.proxy._item_context = replace(
        batch.proxy._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(batch.seen.append, collect_attempts=True),),
    )

    def hook(_headers, _results):
        outer = telemetry._OPERATION.get()
        batch.call()
        assert telemetry._OPERATION.get() is outer and not outer.closed

    batch.call(response_hook=hook)
    assert len(batch.calls) == len(batch.seen) == 2
    assert batch.states[0] is not batch.states[1]
    assert all(s.closed for s in batch.states) and len(operation_spans(recording)) == 1


@pytest.mark.parametrize("timeout", [None, 10])
def test_cancellation_drains_authorized_batch_rust(batch, recording, timeout):
    if not batch.asynchronous:
        pytest.skip("Async cancellation")

    async def run():
        batch.gate = asyncio.Event()
        hook = Mock()
        task = asyncio.create_task(
            batch.proxy.execute_item_batch(batch.operations, "customer-17", timeout=timeout, response_hook=hook)
        )
        await batch.gate.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert batch.drained and batch.seen[0].outcome == "cancelled"
        assert batch.states[0].closed and not batch.states[0].delegated_tasks
        hook.assert_not_called()
        assert len(batch.calls) == len(operation_spans(recording)) == 1
        assert telemetry._OPERATION.get() is None

    asyncio.run(run())
