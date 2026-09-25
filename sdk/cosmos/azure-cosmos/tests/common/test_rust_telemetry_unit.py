# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Exercise the private async create proof with real tracing and a fake binding."""

import asyncio
import builtins
from copy import deepcopy
import logging
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

pytest.importorskip("opentelemetry.sdk.trace")
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.sampling import ALWAYS_OFF
from azure.core import instrumentation
from azure.core.settings import settings
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.cosmos._backend.errors import BindingProtocolError
from azure.cosmos._helpers._item_context import ItemClientContext
from azure.cosmos.aio._container import ContainerProxy
from azure.cosmos.aio._backend import rust_backend
from azure.cosmos.aio import _telemetry_poc as telemetry
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosResourceExistsError


ORDER = {"id": "order-42", "customerId": "customer-17", "total": 125.5}


@pytest.fixture(params=["native", "plugin"])
def recording(request, monkeypatch):
    implementation = None
    if request.param == "plugin":
        implementation = pytest.importorskip(
            "azure.core.tracing.ext.opentelemetry_span"
        ).OpenTelemetrySpan
    enabled, previous_implementation = settings.tracing_enabled(), settings.tracing_implementation()
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    # Inject a provider without replacing OpenTelemetry's process-global provider.
    monkeypatch.setattr(trace, "get_tracer_provider", lambda: provider)
    instrumentation._get_tracer_cached.cache_clear()
    settings.tracing_enabled = True
    settings.tracing_implementation = implementation
    try:
        yield SimpleNamespace(provider=provider, exporter=exporter)
    finally:
        settings.tracing_enabled = enabled
        settings.tracing_implementation = previous_implementation
        instrumentation._get_tracer_cached.cache_clear()
        provider.shutdown()


@pytest.fixture
def create(recording, monkeypatch):
    backend = rust_backend.AsyncRustBackend("https://example.documents.azure.com", master_key="unused")
    container = ContainerProxy(None, "dbs/sales", "orders", _item_context=ItemClientContext(backend))
    harness = SimpleNamespace(
        backend=backend, container=container, calls=[], payloads=[],
        transform=lambda result: result, error=None, gate=None,
    )
    monkeypatch.setattr(backend, "_ensure_driver_handle", AsyncMock(return_value="test-driver"))

    async def binding(driver_handle, prepared, *, timeout_seconds=None, include_attempts=False):
        assert driver_handle == "test-driver"
        assert prepared.container_link == "dbs/sales/colls/orders"
        harness.calls.append((include_attempts, timeout_seconds, dict(prepared.headers)))
        start = time.time_ns()
        if harness.gate is not None:
            harness.gate.set()
            await asyncio.Future()
        await asyncio.sleep(0)
        if harness.error is not None:
            raise harness.error
        end = time.time_ns()
        payload = {
            "schema_version": 1, "request_count": 5, "retained_request_count": 2, "error": None,
            "attempts": [
                {"start_ns": start, "end_ns": end, "driver_status_code": 503, "execution_context": "initial"},
                {"start_ns": start, "end_ns": end, "driver_status_code": 201, "execution_context": "retry"},
            ],
        }
        harness.payloads.append(payload)
        response = (201, 0, {"x-ms-request-charge": "5.0"}, prepared.body_bytes, "diagnostic-text")
        return harness.transform((response, payload)) if include_attempts else response

    monkeypatch.setattr(rust_backend, "_rust_module", SimpleNamespace(create_item_async=binding))
    yield harness
    asyncio.run(backend.close())


def operation_spans(recording):
    return [
        span for span in recording.exporter.get_finished_spans()
        if span.name == "ContainerProxy.create_item"
    ]


def attempt_spans(recording):
    return [span for span in recording.exporter.get_finished_spans() if span.name == "cosmosdb.request"]


def test_create_preserves_result_and_records_exact_sibling_attempts(create, recording):
    hooks = []
    body = deepcopy(ORDER)

    async def run():
        with trace.get_tracer("customer").start_as_current_span("checkout") as checkout:
            result = await telemetry.create_item_with_attempt_tracing(
                create.container, body, timeout=10,
                response_hook=lambda headers, item: hooks.append((headers, item)),
            )
            assert trace.get_current_span() is checkout
        return result, checkout

    result, checkout = asyncio.run(run())
    assert result == body == ORDER
    assert len(hooks) == 1
    assert hooks[0][1] == ORDER
    assert result.get_response_headers()["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
    assert create.calls[0][0] is True
    assert 0 < create.calls[0][1] <= 10
    assert not any("attempt" in key or "telemetry" in key for key in create.calls[0][2])
    operation, = operation_spans(recording)
    assert operation.parent.span_id == checkout.get_span_context().span_id
    assert operation.attributes["cosmos.poc.request_count"] == 5
    assert operation.attributes["cosmos.poc.retained_request_count"] == 2
    assert operation.status.status_code is trace.StatusCode.UNSET
    children = sorted(attempt_spans(recording), key=lambda span: span.attributes["cosmos.poc.driver_status_code"],
                      reverse=True)
    assert len(children) == 2
    for child, row in zip(children, create.payloads[0]["attempts"]):
        assert child.parent.span_id == operation.context.span_id
        assert child.context.trace_id == operation.context.trace_id
        assert child.start_time == row["start_ns"]
        assert child.end_time == row["end_ns"]
        assert operation.start_time <= child.start_time <= child.end_time <= operation.end_time
        assert child.kind is trace.SpanKind.CLIENT
        assert dict(child.attributes) == {
            "cosmos.poc.driver_status_code": row["driver_status_code"],
            "cosmos.poc.execution_context": row["execution_context"],
        }
    assert telemetry._CAPTURE.get() is None


@pytest.mark.parametrize("mode", ["ordinary", "disabled", "global-disabled", "merged", "nested", "sampled-out"])
def test_no_attempts_without_a_new_recording_operation(create, recording, mode):
    async def run():
        with trace.get_tracer("customer").start_as_current_span("checkout") as checkout:
            kwargs = {}
            if mode == "disabled":
                kwargs["tracing_options"] = {"enabled": False}
            elif mode == "global-disabled":
                settings.tracing_enabled = False
            elif mode == "merged":
                kwargs["merge_span"] = True
            elif mode == "sampled-out":
                recording.provider.sampler = ALWAYS_OFF
            if mode == "ordinary":
                await create.container.create_item(ORDER)
            elif mode == "nested":
                @distributed_trace_async
                async def outer():
                    return await telemetry.create_item_with_attempt_tracing(create.container, ORDER)
                await outer()
            else:
                await telemetry.create_item_with_attempt_tracing(create.container, ORDER, **kwargs)
            assert not any(key.startswith("cosmos.poc.") for key in checkout.attributes)

    asyncio.run(run())
    assert len(create.calls) == 1
    assert create.calls[0][0] is False
    assert not attempt_spans(recording)


@pytest.mark.parametrize("defect", [
    "schema", "count", "rows", "start", "end", "backwards", "status", "reason", "binding-error", "conversion-error",
])
def test_invalid_detail_reports_without_changing_the_write(create, recording, caplog, defect):
    def corrupt(result):
        response, payload = result
        if defect == "schema":
            payload["schema_version"] = True
        elif defect == "count":
            payload["request_count"] = 1
        elif defect == "rows":
            payload["attempts"] = "PRIVATE"
        elif defect == "start":
            payload["attempts"][0]["start_ns"] = -1
        elif defect == "end":
            payload["attempts"][0]["end_ns"] = 1 << 64
        elif defect == "backwards":
            payload["attempts"][0]["end_ns"] = payload["attempts"][0]["start_ns"] - 1
        elif defect == "status":
            payload["attempts"][0]["driver_status_code"] = 65536
        elif defect == "reason":
            payload["attempts"][0]["execution_context"] = ""
        elif defect == "binding-error":
            payload["error"] = "PRIVATE"
        else:
            payload = "PRIVATE"
        return response, payload

    create.transform = corrupt
    with caplog.at_level(logging.WARNING):
        result = asyncio.run(telemetry.create_item_with_attempt_tracing(create.container, ORDER))
    assert result == ORDER
    assert len(create.calls) == 1
    assert not attempt_spans(recording)
    assert "rejected an invalid diagnostics payload" in caplog.text
    assert "PRIVATE" not in caplog.text


@pytest.mark.parametrize("shape", ["four", "five", "one", "three"])
def test_recoverable_envelope_preserves_the_response(create, recording, caplog, shape):
    def reshape(result):
        response, payload = result
        return {"four": response[:4], "five": response, "one": (response,),
                "three": (response, payload, "PRIVATE")}[shape]

    create.transform = reshape
    with caplog.at_level(logging.WARNING):
        result = asyncio.run(telemetry.create_item_with_attempt_tracing(create.container, ORDER))
    assert result == ORDER
    assert len(create.calls) == 1
    assert not attempt_spans(recording)
    assert "response is preserved" in caplog.text
    assert "PRIVATE" not in caplog.text


def test_missing_database_response_is_not_reported_as_success(create):
    create.transform = lambda _: ("invalid", None)
    with pytest.raises(BindingProtocolError):
        asyncio.run(telemetry.create_item_with_attempt_tracing(create.container, ORDER))
    assert len(create.calls) == 1


def test_incomplete_attempt_keeps_counts_without_inventing_end_time(create, recording, caplog):
    def incomplete(result):
        result[1]["attempts"][0]["end_ns"] = None
        return result

    create.transform = incomplete
    with caplog.at_level(logging.WARNING):
        assert asyncio.run(telemetry.create_item_with_attempt_tracing(create.container, ORDER)) == ORDER
    assert len(attempt_spans(recording)) == 1
    operation, = operation_spans(recording)
    assert operation.attributes["cosmos.poc.request_count"] == 5
    assert operation.attributes["cosmos.poc.retained_request_count"] == 2
    assert "without a completion time" in caplog.text


@pytest.mark.parametrize("failure", ["tracer", "start", "end", "attribute"])
def test_instrumentation_exception_does_not_replace_write_result(
    create, recording, monkeypatch, caplog, failure
):
    original_get_tracer = trace.get_tracer

    def fail(*_args, **_kwargs):
        raise RuntimeError("PRIVATE")

    def get_tracer(instrumenting_module_name, *args, **kwargs):
        tracer = original_get_tracer(instrumenting_module_name, *args, **kwargs)
        if instrumenting_module_name != "azure.cosmos.rust_attempt_poc":
            return tracer
        if failure == "tracer":
            fail()
        if failure == "start":
            monkeypatch.setattr(tracer, "start_span", fail)
        elif failure == "end":
            original_start = tracer.start_span

            def start(*args, **kwargs):
                span = original_start(*args, **kwargs)
                monkeypatch.setattr(span, "end", fail)
                return span

            monkeypatch.setattr(tracer, "start_span", start)
        return tracer

    monkeypatch.setattr(trace, "get_tracer", get_tracer)
    if failure == "attribute":
        original_emit = telemetry.emit_attempts

        def emit(parent, payload):
            original_set = parent.set_attribute

            def set_attribute(name, value):
                if name.startswith("cosmos.poc."):
                    fail()
                return original_set(name, value)

            monkeypatch.setattr(parent, "set_attribute", set_attribute)
            original_emit(parent, payload)

        monkeypatch.setattr(rust_backend, "emit_attempts", emit)
    with caplog.at_level(logging.WARNING):
        result = asyncio.run(telemetry.create_item_with_attempt_tracing(create.container, ORDER))
    assert result == ORDER
    assert len(create.calls) == 1
    assert "could not emit all attempt spans" in caplog.text
    assert "PRIVATE" not in caplog.text
    assert operation_spans(recording)[0].status.status_code is trace.StatusCode.UNSET


def test_response_hook_error_remains_the_public_failure(create, recording):
    def hook(_headers, _item):
        raise ValueError("hook failed")

    with pytest.raises(ValueError, match="hook failed"):
        asyncio.run(telemetry.create_item_with_attempt_tracing(create.container, ORDER, response_hook=hook))
    assert len(create.calls) == 1
    assert len(attempt_spans(recording)) == 2
    assert operation_spans(recording)[0].status.status_code is trace.StatusCode.ERROR


def test_service_error_preserves_exception_and_diagnostics(create, recording):
    create.transform = lambda _: ((409, 0, {}, b'{"message":"conflict"}', "error-diagnostics"), None)
    with pytest.raises(CosmosResourceExistsError) as error:
        asyncio.run(telemetry.create_item_with_attempt_tracing(create.container, ORDER))
    assert error.value.headers["x-ms-cosmos-sdk-diagnostics"] == "error-diagnostics"
    assert len(create.calls) == 1
    assert not attempt_spans(recording)


def test_timeout_preserves_exception_without_replaying(create, recording):
    create.error = TimeoutError("driver timeout")
    with pytest.raises(CosmosClientTimeoutError):
        asyncio.run(telemetry.create_item_with_attempt_tracing(create.container, ORDER, timeout=10))
    assert len(create.calls) == 1
    assert not attempt_spans(recording)
    assert telemetry._CAPTURE.get() is None


def test_cancellation_is_not_swallowed(create, recording):
    async def run():
        create.gate = asyncio.Event()
        task = asyncio.create_task(telemetry.create_item_with_attempt_tracing(create.container, ORDER))
        await create.gate.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert telemetry._CAPTURE.get() is None

    asyncio.run(run())
    assert len(create.calls) == 1
    assert not attempt_spans(recording)


def test_concurrent_calls_keep_their_own_parents(create, recording):
    async def write(index):
        with trace.get_tracer("customer").start_as_current_span(f"checkout-{index}"):
            await telemetry.create_item_with_attempt_tracing(create.container, dict(ORDER, id=f"order-{index}"))

    async def run():
        await asyncio.gather(*(write(index) for index in range(4)))

    asyncio.run(run())
    operations = operation_spans(recording)
    assert len(operations) == len(create.calls) == 4
    assert len(attempt_spans(recording)) == 8
    assert len({span.context.trace_id for span in operations}) == 4
    for operation in operations:
        children = [span for span in attempt_spans(recording) if span.parent.span_id == operation.context.span_id]
        assert len(children) == 2
        assert all(child.context.trace_id == operation.context.trace_id for child in children)


def test_child_task_cannot_consume_another_tasks_opt_in(create, recording):
    async def run():
        caller = trace.get_current_span().get_span_context()
        capture = telemetry._Capture(caller, create.backend, asyncio.current_task())
        token = telemetry._CAPTURE.set(capture)
        try:
            await asyncio.create_task(create.container.create_item(ORDER))
            assert capture.consumed is False
        finally:
            telemetry._CAPTURE.reset(token)

    asyncio.run(run())
    assert create.calls[0][0] is False
    assert not attempt_spans(recording)


def test_ordinary_create_needs_no_opentelemetry_import(create, monkeypatch):
    original_import = builtins.__import__

    def import_without_opentelemetry(name, *args, **kwargs):
        if name.startswith("opentelemetry"):
            raise AssertionError("Ordinary create imported optional telemetry")
        return original_import(name, *args, **kwargs)

    settings.tracing_enabled = False
    monkeypatch.setattr(builtins, "__import__", import_without_opentelemetry)
    assert asyncio.run(create.container.create_item(ORDER)) == ORDER
    assert create.calls[0][0] is False


def test_span_capture_failure_skips_only_attempt_detail(create, recording, monkeypatch, caplog):
    original_take = telemetry.take_operation_parent
    original_current = trace.get_current_span

    def take(backend):
        def broken_current():
            raise RuntimeError("PRIVATE")

        with monkeypatch.context() as scoped:
            scoped.setattr(trace, "get_current_span", broken_current)
            return original_take(backend)

    monkeypatch.setattr(rust_backend, "take_operation_parent", take)
    with caplog.at_level(logging.WARNING):
        assert asyncio.run(telemetry.create_item_with_attempt_tracing(create.container, ORDER)) == ORDER
    assert trace.get_current_span is original_current
    assert create.calls[0][0] is False
    assert not attempt_spans(recording)
    assert "could not capture the operation span" in caplog.text
    assert "PRIVATE" not in caplog.text


def test_empty_success_body_keeps_diagnostics_and_attempts(create, recording):
    def empty_body(result):
        response, payload = result
        return (*response[:3], b"", response[4]), payload

    create.transform = empty_body
    result = asyncio.run(telemetry.create_item_with_attempt_tracing(create.container, ORDER, no_response=True))
    assert result == {}
    assert result.get_response_headers()["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
    assert len(attempt_spans(recording)) == 2


def test_instrumentation_does_not_swallow_cancellation(create, monkeypatch):
    original_get = trace.get_tracer

    def get_tracer(instrumenting_module_name, *args, **kwargs):
        if instrumenting_module_name == "azure.cosmos.rust_attempt_poc":
            raise asyncio.CancelledError()
        return original_get(instrumenting_module_name, *args, **kwargs)

    monkeypatch.setattr(trace, "get_tracer", get_tracer)
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(telemetry.create_item_with_attempt_tracing(create.container, ORDER))
    assert len(create.calls) == 1
    assert telemetry._CAPTURE.get() is None
