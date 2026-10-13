# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Exercise public telemetry with real tracing and controlled binding results."""

import asyncio
import builtins
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
import json
import logging
import sys
import time
from types import SimpleNamespace
from threading import Barrier
from unittest.mock import AsyncMock, Mock

import pytest
from common.typed_requests import wire_headers

pytest.importorskip("opentelemetry.sdk.trace")
# Optional dependency checks must run before the tracing imports.
# pylint: disable=wrong-import-position
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.sampling import ALWAYS_OFF
from azure.core import instrumentation
from azure.core.exceptions import ServiceResponseError
from azure.core.settings import settings
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace
from azure.cosmos._backend.binding_adapter import BindingAdapter
from azure.cosmos._backend import binding_adapter as sync_binding_adapter
from azure.cosmos._backend.errors import BindingProtocolError
from azure.cosmos._helpers._item_context import ItemClientContext
from azure.cosmos.aio._container import ContainerProxy
from azure.cosmos.container import ContainerProxy as SyncContainerProxy
from azure.cosmos.database import DatabaseProxy as SyncDatabaseProxy
from azure.cosmos.aio._database import DatabaseProxy
from azure.cosmos.aio._backend import binding_adapter
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos import _telemetry as telemetry
from azure.cosmos import PartitionKey
from azure.cosmos import _operation_deadline
from azure.cosmos._helpers import _item_prep
from azure.cosmos.exceptions import (
    CosmosAccessConditionFailedError,
    CosmosClientTimeoutError,
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)

# pylint: enable=wrong-import-position

ORDER = {"id": "order-17", "customerId": "customer-17", "total": 125.5}
CONTAINER_PROPERTIES = {
    "id": "orders",
    "_rid": "container-rid",
    "partitionKey": {"paths": ["/customerId"], "kind": "Hash"},
    "indexingPolicy": {"indexingMode": "consistent", "includedPaths": [{"path": "/*"}]},
}


class DriverTransportError(RuntimeError):
    pass


@pytest.fixture(name="recording", params=["native", "plugin"])
def recording_setup(request, monkeypatch):
    implementation = None
    if request.param == "plugin":
        implementation = pytest.importorskip("azure.core.tracing.ext.opentelemetry_span").OpenTelemetrySpan
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


@pytest.fixture(name="create")
def item_harness(recording, monkeypatch):  # pylint: disable=unused-argument
    backend = binding_adapter.AsyncBindingAdapter("https://example.documents.azure.com", master_key="unused")
    container = ContainerProxy(None, "dbs/sales", "orders", _item_context=ItemClientContext(backend))
    harness = SimpleNamespace(
        backend=backend,
        container=container,
        calls=[],
        payloads=[],
        prepared_requests=[],
        operations=[],
        targets=[],
        transform=lambda result: result,
        error=None,
        gate=None,
        response_status=201,
        omit_body=False,
        driver_error=None,
        driver_error_type=DriverTransportError,
    )
    monkeypatch.setattr(backend, "_ensure_driver_handle", AsyncMock(return_value="test-driver"))
    monkeypatch.setattr(binding_adapter, "_DRIVER_TRANSPORT_ERROR", DriverTransportError)

    async def binding(driver_handle, prepared, *, timeout_seconds=None, include_attempts=False):
        assert driver_handle == "test-driver"
        assert prepared.container_link == ("" if prepared.op == "create_container" else "dbs/sales/colls/orders")
        harness.calls.append((include_attempts, timeout_seconds, dict(prepared.headers)))
        harness.prepared_requests.append(prepared)
        harness.operations.append(prepared.op)
        harness.targets.append((prepared.item_id, prepared.item_self_link))
        start = time.time_ns()
        if harness.gate is not None:
            harness.gate.set()
            await asyncio.Future()
        await asyncio.sleep(0)
        if harness.error is not None:
            raise harness.error
        end = time.time_ns()
        payload = {
            "schema_version": 1,
            "request_count": 5,
            "retained_request_count": 2,
            "error": None,
            "attempts": [
                {"start_ns": start, "end_ns": end, "driver_status_code": 503, "execution_context": "initial"},
                {
                    "start_ns": start,
                    "end_ns": end,
                    "driver_status_code": harness.response_status,
                    "execution_context": "retry",
                },
            ],
        }
        harness.payloads.append(payload)
        if harness.response_status == 408:
            # This is a driver error without a service response, not an HTTP 408 response.
            harness.driver_error = harness.driver_error_type("driver failure")
            if include_attempts:
                _, payload = harness.transform((None, payload))
                if payload is not None:
                    harness.driver_error._cosmos_attempt_payload = payload
            raise harness.driver_error
        if harness.response_status == 201:
            body = (
                json.dumps({**CONTAINER_PROPERTIES, **json.loads(prepared.body_bytes)}).encode()
                if prepared.op == "create_container"
                else prepared.body_bytes
            )
        elif harness.response_status == 200:
            body = (
                prepared.body_bytes
                if prepared.op in ("upsert_item", "replace_item")
                else json.dumps(CONTAINER_PROPERTIES if prepared.op == "read_container" else ORDER).encode()
            )
        elif harness.response_status in (204, 304):
            body = b""
        elif harness.response_status == 404:
            body = b'{"message":"not found"}'
        else:
            body = b'{"message":"conflict"}'
        if harness.omit_body and harness.response_status in (200, 201):
            body = b""
        response = (harness.response_status, 0, {"x-ms-request-charge": "5.0"}, body, "diagnostic-text")
        return harness.transform((response, payload)) if include_attempts else response

    monkeypatch.setattr(
        binding_adapter,
        "_rust_module",
        SimpleNamespace(
            create_item_async=binding,
            read_item_async=binding,
            delete_item_async=binding,
            upsert_item_async=binding,
            replace_item_async=binding,
            patch_item_async=binding,
            read_container_async=binding,
            delete_container_async=binding,
            create_container_async=binding,
        ),
    )
    yield harness
    asyncio.run(backend.close())


def operation_spans(recording):
    return [span for span in recording.exporter.get_finished_spans() if span.name == "ContainerProxy.create_item"]


def attempt_spans(recording):
    return [span for span in recording.exporter.get_finished_spans() if span.name == "cosmosdb.request"]


@pytest.mark.parametrize(
    "backend",
    [None, SimpleNamespace(name="core-python"), ASYNC_LEGACY_BACKEND],
    ids=["missing", "legacy-name", "async-legacy"],
)
@pytest.mark.parametrize(
    "operation", ["create_item", "read_item", "delete_item", "upsert_item", "replace_item", "patch_item"]
)
@pytest.mark.usefixtures("recording")
def test_non_rust_calls_do_not_create_rust_telemetry_state(backend, operation):
    container = SimpleNamespace(_item_context=SimpleNamespace(adapter=backend))
    assert telemetry._new_operation(container, operation, {}) is None
    assert telemetry._OPERATION.get() is None


def test_create_preserves_result_and_records_exact_sibling_attempts(create, recording):
    hooks = []
    body = deepcopy(ORDER)

    async def run():
        with trace.get_tracer("customer").start_as_current_span("checkout") as checkout:
            result = await create.container.create_item(
                body,
                timeout=10,
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
    (operation,) = operation_spans(recording)
    assert operation.parent.span_id == checkout.get_span_context().span_id
    assert operation.attributes["cosmos.poc.request_count"] == 5
    assert operation.attributes["cosmos.poc.retained_request_count"] == 2
    assert operation.status.status_code is trace.StatusCode.UNSET
    children = sorted(
        attempt_spans(recording), key=lambda span: span.attributes["cosmos.poc.driver_status_code"], reverse=True
    )
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
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("mode", ["disabled", "global-disabled", "merged", "nested", "sampled-out"])
@pytest.mark.parametrize("response_status", [201, 409, 408])
def test_no_attempts_without_a_new_recording_operation(create, recording, mode, response_status):
    create.response_status = response_status

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

            async def call():
                if mode == "nested":

                    @distributed_trace_async
                    async def outer():
                        return await create.container.create_item(ORDER)

                    return await outer()
                return await create.container.create_item(ORDER, **kwargs)

            if response_status == 409:
                with pytest.raises(CosmosResourceExistsError, match="conflict") as error:
                    await call()
                assert error.value.headers["x-ms-request-charge"] == "5.0"
            elif response_status == 408:
                with pytest.raises(ServiceResponseError, match="driver failure") as error:
                    await call()
                assert error.value.__cause__ is create.driver_error
                assert not hasattr(create.driver_error, "_cosmos_attempt_payload")
            else:
                assert await call() == ORDER
            assert not any(key.startswith("cosmos.poc.") for key in checkout.attributes)

    asyncio.run(run())
    assert len(create.calls) == 1
    assert create.calls[0][0] is False
    assert not attempt_spans(recording)


@pytest.mark.parametrize(
    "defect",
    [
        "schema",
        "count",
        "rows",
        "start",
        "end",
        "backwards",
        "status",
        "reason",
        "binding-error",
        "conversion-error",
    ],
)
@pytest.mark.parametrize("response_status", [201, 409, 408])
def test_invalid_detail_reports_without_changing_the_write(create, recording, caplog, defect, response_status):
    create.response_status = response_status

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
        if response_status == 409:
            with pytest.raises(CosmosResourceExistsError, match="conflict") as error:
                asyncio.run(create.container.create_item(ORDER))
            assert error.value.status_code == 409
            assert error.value.headers["x-ms-request-charge"] == "5.0"
            assert error.value.headers["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
        elif response_status == 408:
            with pytest.raises(ServiceResponseError, match="driver failure") as error:
                asyncio.run(create.container.create_item(ORDER))
            assert error.value.__cause__ is create.driver_error
            assert create.driver_error.args == ("driver failure",)
        else:
            assert asyncio.run(create.container.create_item(ORDER)) == ORDER
    assert len(create.calls) == 1
    assert not attempt_spans(recording)
    assert "rejected an invalid diagnostics payload" in caplog.text
    assert "PRIVATE" not in caplog.text


@pytest.mark.parametrize("shape", ["four", "five", "one", "three"])
def test_recoverable_envelope_preserves_the_response(create, recording, caplog, shape):
    def reshape(result):
        response, payload = result
        return {"four": response[:4], "five": response, "one": (response,), "three": (response, payload, "PRIVATE")}[
            shape
        ]

    create.transform = reshape
    with caplog.at_level(logging.WARNING):
        result = asyncio.run(create.container.create_item(ORDER))
    assert result == ORDER
    assert len(create.calls) == 1
    assert not attempt_spans(recording)
    assert "response is preserved" in caplog.text
    assert "PRIVATE" not in caplog.text


def test_missing_database_response_is_not_reported_as_success(create):
    create.transform = lambda _: ("invalid", None)
    with pytest.raises(BindingProtocolError):
        asyncio.run(create.container.create_item(ORDER))
    assert len(create.calls) == 1


@pytest.mark.parametrize("response_status", [201, 408])
def test_incomplete_attempt_keeps_counts_without_inventing_end_time(create, recording, caplog, response_status):
    create.response_status = response_status

    def incomplete(result):
        result[1]["attempts"][0]["end_ns"] = None
        return result

    create.transform = incomplete
    with caplog.at_level(logging.WARNING):
        if response_status == 408:
            with pytest.raises(ServiceResponseError, match="driver failure") as error:
                asyncio.run(create.container.create_item(ORDER))
            assert error.value.__cause__ is create.driver_error
        else:
            assert asyncio.run(create.container.create_item(ORDER)) == ORDER
    assert len(attempt_spans(recording)) == 1
    (operation,) = operation_spans(recording)
    assert operation.attributes["cosmos.poc.request_count"] == 5
    assert operation.attributes["cosmos.poc.retained_request_count"] == 2
    assert "without a completion time" in caplog.text


@pytest.mark.parametrize("failure", ["tracer", "start", "end", "attribute"])
@pytest.mark.parametrize("response_status", [201, 409, 408])
def test_instrumentation_exception_does_not_replace_write_result(
    create, recording, monkeypatch, caplog, failure, response_status
):
    create.response_status = response_status
    original_get_tracer = trace.get_tracer

    def fail(*_args, **_kwargs):
        raise RuntimeError("PRIVATE")

    def get_tracer(instrumenting_module_name, *args, **kwargs):
        tracer = original_get_tracer(instrumenting_module_name, *args, **kwargs)
        if instrumenting_module_name != "azure.cosmos.rust":
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

        monkeypatch.setattr(telemetry, "emit_attempts", emit)
    with caplog.at_level(logging.WARNING):
        if response_status == 409:
            with pytest.raises(CosmosResourceExistsError, match="conflict") as error:
                asyncio.run(create.container.create_item(ORDER))
            assert error.value.status_code == 409
            assert error.value.headers["x-ms-request-charge"] == "5.0"
            assert error.value.headers["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
        elif response_status == 408:
            with pytest.raises(ServiceResponseError, match="driver failure") as error:
                asyncio.run(create.container.create_item(ORDER))
            assert error.value.__cause__ is create.driver_error
            assert create.driver_error.args == ("driver failure",)
        else:
            assert asyncio.run(create.container.create_item(ORDER)) == ORDER
    assert len(create.calls) == 1
    assert "could not emit all attempt spans" in caplog.text
    assert "PRIVATE" not in caplog.text
    expected_status = trace.StatusCode.UNSET if response_status == 201 else trace.StatusCode.ERROR
    assert operation_spans(recording)[0].status.status_code is expected_status


def test_response_hook_error_remains_the_public_failure(create, recording):
    def hook(_headers, _item):
        raise ValueError("hook failed")

    with pytest.raises(ValueError, match="hook failed"):
        asyncio.run(create.container.create_item(ORDER, response_hook=hook))
    assert len(create.calls) == 1
    assert len(attempt_spans(recording)) == 2
    assert operation_spans(recording)[0].status.status_code is trace.StatusCode.ERROR


@pytest.mark.parametrize("has_diagnostics", [True, False])
@pytest.mark.parametrize("response_status", [409, 408])
def test_failed_create_preserves_exception_and_diagnostics(create, recording, has_diagnostics, response_status):
    create.response_status = response_status
    exception_type = CosmosResourceExistsError if response_status == 409 else ServiceResponseError
    message = "conflict" if response_status == 409 else "driver failure"
    if not has_diagnostics:
        create.transform = lambda result: (result[0], None)

    async def run():
        with trace.get_tracer("customer").start_as_current_span("checkout") as checkout:
            with pytest.raises(exception_type, match=message) as error:
                await create.container.create_item(ORDER)
            assert trace.get_current_span() is checkout
        return error.value, checkout

    error, checkout = asyncio.run(run())
    if response_status == 409:
        assert error.status_code == 409
        assert error.headers["x-ms-request-charge"] == "5.0"
        assert error.headers["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
    else:
        assert error.__cause__ is create.driver_error
        assert create.driver_error.args == ("driver failure",)
        assert str(error) == str(create.driver_error)
    assert len(create.calls) == 1
    assert create.calls[0][0] is True
    (operation,) = operation_spans(recording)
    assert operation.parent.span_id == checkout.get_span_context().span_id
    assert operation.status.status_code is trace.StatusCode.ERROR
    children = attempt_spans(recording)
    if has_diagnostics:
        assert operation.attributes["cosmos.poc.request_count"] == 5
        assert operation.attributes["cosmos.poc.retained_request_count"] == 2
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
    else:
        assert not children
    assert telemetry._OPERATION.get() is None


def test_unreadable_error_diagnostics_preserve_exception(create, recording, caplog):
    class UnreadableDiagnostics(DriverTransportError):
        @property
        def _cosmos_attempt_payload(self):
            raise RuntimeError("PRIVATE")

    create.error = UnreadableDiagnostics("driver failure")
    with caplog.at_level(logging.WARNING), pytest.raises(ServiceResponseError, match="driver failure") as error:
        asyncio.run(create.container.create_item(ORDER))
    assert error.value.__cause__ is create.error
    assert len(create.calls) == 1
    assert not attempt_spans(recording)
    assert "could not read error diagnostics" in caplog.text
    assert "PRIVATE" not in caplog.text
    assert operation_spans(recording)[0].status.status_code is trace.StatusCode.ERROR
    assert telemetry._OPERATION.get() is None


def test_disabled_error_never_reads_private_diagnostics(create, recording):
    class UnreadableDiagnostics(DriverTransportError):
        @property
        def _cosmos_attempt_payload(self):
            raise AssertionError("Ordinary create must not inspect tracing diagnostics")

    create.error = UnreadableDiagnostics("driver failure")
    with pytest.raises(ServiceResponseError, match="driver failure") as error:
        asyncio.run(create.container.create_item(ORDER, tracing_options={"enabled": False}))
    assert error.value.__cause__ is create.error
    assert create.calls[0][0] is False
    assert not attempt_spans(recording)


def test_timeout_preserves_exception_without_replaying(create, recording):
    create.error = TimeoutError("driver timeout")
    with pytest.raises(CosmosClientTimeoutError):
        asyncio.run(create.container.create_item(ORDER, timeout=10))
    assert len(create.calls) == 1
    assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


def test_cancellation_is_not_swallowed(create, recording):
    async def run():
        create.gate = asyncio.Event()
        task = asyncio.create_task(create.container.create_item(ORDER))
        await create.gate.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert telemetry._OPERATION.get() is None

    asyncio.run(run())
    assert len(create.calls) == 1
    assert not attempt_spans(recording)


def test_concurrent_calls_keep_their_own_parents(create, recording):
    async def write(index):
        with trace.get_tracer("customer").start_as_current_span(f"checkout-{index}"):
            await create.container.create_item(dict(ORDER, id=f"order-{index}"))

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


def test_child_task_has_its_own_public_operation(create, recording):
    async def run():
        with telemetry._operation_scope(create.container, "create_item", {}):
            state = telemetry._OPERATION.get()
            await asyncio.create_task(create.container.create_item(ORDER))
            assert telemetry._OPERATION.get() is state
            assert state.collector.diagnostics is None
            assert not state.closed

    asyncio.run(run())
    assert create.calls[0][0] is True
    assert len(attempt_spans(recording)) == 2


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
    original_record = telemetry._record_operation
    original_current = trace.get_current_span

    @contextmanager
    def broken_record():
        def broken_current():
            raise RuntimeError("PRIVATE")

        with monkeypatch.context() as scoped:
            scoped.setattr(trace, "get_current_span", broken_current)
            with original_record():
                yield

    monkeypatch.setattr(telemetry, "_record_operation", broken_record)
    with caplog.at_level(logging.WARNING):
        assert asyncio.run(create.container.create_item(ORDER)) == ORDER
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
    result = asyncio.run(create.container.create_item(ORDER, no_response=True))
    assert result == {}
    assert result.get_response_headers()["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
    assert len(attempt_spans(recording)) == 2


def test_instrumentation_does_not_swallow_cancellation(create, monkeypatch):
    original_get = trace.get_tracer

    def get_tracer(instrumenting_module_name, *args, **kwargs):
        if instrumenting_module_name == "azure.cosmos.rust":
            raise asyncio.CancelledError()
        return original_get(instrumenting_module_name, *args, **kwargs)

    monkeypatch.setattr(trace, "get_tracer", get_tracer)
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(create.container.create_item(ORDER))
    assert len(create.calls) == 1
    assert telemetry._OPERATION.get() is None


def traced_read(harness, **kwargs):
    return harness.container.read_item(ORDER["id"], partition_key=ORDER["customerId"], **kwargs)


@pytest.mark.parametrize("status", [200, 304, 404, 408])
def test_read_preserves_outcome_and_exact_attempts(create, recording, status):
    create.response_status = status
    hooks = []

    async def run():
        with trace.get_tracer("customer").start_as_current_span("checkout") as checkout:
            call = traced_read(create, timeout=10, response_hook=lambda headers, item: hooks.append((headers, item)))
            if status in (200, 304):
                result = await call
                assert result == (ORDER if status == 200 else {})
                assert result.get_response_headers()["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
            else:
                exception = CosmosResourceNotFoundError if status == 404 else ServiceResponseError
                with pytest.raises(exception) as error:
                    await call
                if status == 404:
                    assert error.value.status_code == 404
                    assert error.value.headers["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
                else:
                    assert error.value.__cause__ is create.driver_error
            assert trace.get_current_span() is checkout
        return checkout

    checkout = asyncio.run(run())
    assert len(hooks) == (1 if status in (200, 304) else 0)
    if hooks:
        assert hooks[0][1] == (ORDER if status == 200 else {})
    assert create.operations == ["read_item"]
    assert create.calls[0][0] is True
    assert 0 < create.calls[0][1] <= 10
    assert not any("attempt" in key or "telemetry" in key for key in create.calls[0][2])
    (operation,) = [s for s in recording.exporter.get_finished_spans() if s.name == "ContainerProxy.read_item"]
    assert operation.parent.span_id == checkout.get_span_context().span_id
    assert operation.status.status_code is (trace.StatusCode.UNSET if status in (200, 304) else trace.StatusCode.ERROR)
    assert operation.attributes["cosmos.poc.request_count"] == 5
    assert operation.attributes["cosmos.poc.retained_request_count"] == 2
    children = attempt_spans(recording)
    assert len(children) == 2
    for span, row in zip(children, create.payloads[0]["attempts"]):
        assert span.parent.span_id == operation.context.span_id
        assert span.context.trace_id == operation.context.trace_id
        assert span.start_time == row["start_ns"]
        assert span.end_time == row["end_ns"]
        assert operation.start_time <= span.start_time <= span.end_time <= operation.end_time
        assert span.kind is trace.SpanKind.CLIENT
        assert dict(span.attributes) == {
            "cosmos.poc.driver_status_code": row["driver_status_code"],
            "cosmos.poc.execution_context": row["execution_context"],
        }
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("mode", ["disabled", "global-disabled", "sampled-out", "merged", "nested"])
def test_read_does_not_opt_in_without_recording(create, recording, mode):
    create.response_status = 200
    if mode == "global-disabled":
        settings.tracing_enabled = False
    elif mode == "sampled-out":
        recording.provider.sampler = ALWAYS_OFF
    if mode == "merged":
        call = traced_read(create, merge_span=True)
    elif mode == "nested":

        @distributed_trace_async
        async def outer():
            return await traced_read(create)

        call = outer()
    else:
        call = traced_read(create, **({"tracing_options": {"enabled": False}} if mode == "disabled" else {}))
    assert asyncio.run(call) == ORDER
    assert create.calls[0][0] is False
    assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("status", [200, 404, 408])
def test_bad_read_diagnostics_preserve_outcome(create, recording, caplog, status):
    create.response_status = status
    create.transform = lambda result: (result[0], "PRIVATE")
    with caplog.at_level(logging.WARNING):
        if status == 200:
            assert asyncio.run(traced_read(create)) == ORDER
        else:
            with pytest.raises(CosmosResourceNotFoundError if status == 404 else ServiceResponseError):
                asyncio.run(traced_read(create))
    assert len(create.calls) == 1
    assert not attempt_spans(recording)
    assert "rejected an invalid diagnostics payload" in caplog.text
    assert "PRIVATE" not in caplog.text
    assert telemetry._OPERATION.get() is None


def test_read_hook_failure_preserves_attempts_and_exception(create, recording):
    create.response_status = 200

    def hook(_headers, _item):
        raise ValueError("read hook failed")

    with pytest.raises(ValueError, match="read hook failed"):
        asyncio.run(traced_read(create, response_hook=hook))
    assert len(create.calls) == 1
    assert len(attempt_spans(recording)) == 2
    assert telemetry._OPERATION.get() is None


def test_read_timeout_and_cancellation_reset_opt_in(create, recording):
    create.error = TimeoutError("binding deadline")
    with pytest.raises(CosmosClientTimeoutError):
        asyncio.run(traced_read(create, timeout=10))
    assert telemetry._OPERATION.get() is None
    create.error = None

    async def run():
        create.gate = asyncio.Event()
        task = asyncio.create_task(traced_read(create))
        await create.gate.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    assert len(create.calls) == 2
    assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("selected", ["create_item", "read_item"])
def test_other_public_operation_does_not_use_inherited_state(create, recording, selected):
    async def run():
        with telemetry._operation_scope(create.container, selected, {}):
            state = telemetry._OPERATION.get()
            if selected == "create_item":
                create.response_status = 200
                await create.container.read_item(ORDER["id"], partition_key=ORDER["customerId"])
            else:
                await create.container.create_item(ORDER)
            assert telemetry._OPERATION.get() is state
            assert state.collector.diagnostics is None
            assert not state.closed

    asyncio.run(run())
    assert create.calls[0][0] is True
    assert len(attempt_spans(recording)) == 2


def test_concurrent_read_and_create_keep_separate_parents(create, recording):
    # The fake binding can return the same successful body for either operation.
    create.response_status = 200

    async def run_read():
        with trace.get_tracer("customer").start_as_current_span("read-checkout"):
            return await traced_read(create)

    async def run_create():
        with trace.get_tracer("customer").start_as_current_span("create-checkout"):
            return await create.container.create_item(ORDER)

    async def run():
        assert await asyncio.gather(run_read(), run_create()) == [ORDER, ORDER]

    asyncio.run(run())
    operations = [s for s in recording.exporter.get_finished_spans() if s.name.startswith("ContainerProxy.")]
    assert {s.name for s in operations} == {"ContainerProxy.create_item", "ContainerProxy.read_item"}
    assert len({s.context.trace_id for s in operations}) == 2
    assert len(create.calls) == 2
    for operation in operations:
        children = [s for s in attempt_spans(recording) if s.parent.span_id == operation.context.span_id]
        assert len(children) == 2
        assert all(s.context.trace_id == operation.context.trace_id for s in children)


def test_ordinary_read_does_not_import_optional_telemetry(create, monkeypatch):
    create.response_status = 200
    settings.tracing_enabled = False
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.startswith("opentelemetry"):
            raise AssertionError("Ordinary read imported optional telemetry")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    assert asyncio.run(create.container.read_item(ORDER["id"], partition_key=ORDER["customerId"])) == ORDER
    assert create.calls[0][0] is False


def test_read_mapping_target_is_preserved(create, recording):
    create.response_status = 200
    target = {"_self": "dbs/sales/colls/orders/docs/order-17/"}
    original = dict(target)
    result = asyncio.run(create.container.read_item(target, partition_key=ORDER["customerId"]))
    assert result == ORDER
    assert target == original
    assert create.targets == [(None, target["_self"])]
    assert create.calls[0][0] is True
    assert len(attempt_spans(recording)) == 2


def test_child_task_read_has_its_own_public_operation(create, recording):
    create.response_status = 200

    async def run():
        with telemetry._operation_scope(create.container, "read_item", {}):
            state = telemetry._OPERATION.get()
            await asyncio.create_task(create.container.read_item(ORDER["id"], partition_key=ORDER["customerId"]))
            assert telemetry._OPERATION.get() is state
            assert state.collector.diagnostics is None
            assert not state.closed

    asyncio.run(run())
    assert create.calls[0][0] is True
    assert len(attempt_spans(recording)) == 2


@pytest.fixture(name="sync_create")
def sync_item_harness(recording, monkeypatch):  # pylint: disable=unused-argument
    backend = BindingAdapter("https://example.documents.azure.com", master_key="unused")
    container = SyncContainerProxy(None, "dbs/sales", "orders", _item_context=ItemClientContext(backend))
    harness = SimpleNamespace(
        backend=backend,
        container=container,
        calls=[],
        payloads=[],
        prepared_requests=[],
        states=[],
        response_status=201,
        omit_body=False,
        error=None,
        barrier=None,
        driver_error=None,
        driver_error_type=DriverTransportError,
        transform=lambda result: result,
    )
    monkeypatch.setattr(backend, "_ensure_driver_handle", Mock(return_value="test-driver"))
    monkeypatch.setattr(sync_binding_adapter, "_DRIVER_TRANSPORT_ERROR", DriverTransportError)

    def binding(driver_handle, prepared, *, timeout_seconds=None, include_attempts=False):
        assert driver_handle == "test-driver"
        harness.calls.append((include_attempts, timeout_seconds, prepared))
        harness.prepared_requests.append(prepared)
        harness.states.append(telemetry._OPERATION.get())
        start = time.time_ns()
        if harness.barrier is not None:
            harness.barrier.wait(timeout=5)
        if harness.error is not None:
            raise harness.error
        payload = {
            "schema_version": 1,
            "request_count": 1,
            "retained_request_count": 1,
            "error": None,
            "attempts": [
                {
                    "start_ns": start,
                    "end_ns": time.time_ns(),
                    "driver_status_code": harness.response_status,
                    "execution_context": "initial",
                }
            ],
        }
        harness.payloads.append(payload)
        if harness.response_status == 408:
            harness.driver_error = harness.driver_error_type("driver failure")
            if include_attempts:
                _, diagnostics = harness.transform((None, payload))
                harness.driver_error._cosmos_attempt_payload = diagnostics
            raise harness.driver_error
        if harness.response_status in (200, 201):
            body = (
                prepared.body_bytes
                if prepared.op in ("create_item", "upsert_item", "replace_item")
                else json.dumps(CONTAINER_PROPERTIES if prepared.op == "read_container" else ORDER).encode()
            )
            if prepared.op == "create_container":
                body = json.dumps({**CONTAINER_PROPERTIES, **json.loads(prepared.body_bytes)}).encode()
        elif harness.response_status in (204, 304):
            body = b""
        else:
            body = b'{"message":"service failure"}'
        if harness.omit_body and harness.response_status in (200, 201):
            body = b""
        response = (harness.response_status, 0, {"x-ms-request-charge": "5.0"}, body, "diagnostic-text")
        return harness.transform((response, payload)) if include_attempts else response

    monkeypatch.setattr(
        sync_binding_adapter,
        "_rust_module",
        SimpleNamespace(
            create_item=binding,
            read_item=binding,
            delete_item=binding,
            upsert_item=binding,
            replace_item=binding,
            patch_item=binding,
            read_container=binding,
            delete_container=binding,
            create_container=binding,
        ),
    )
    yield harness
    backend.close()


def sync_call(harness, operation, **kwargs):
    if operation == "create_item":
        return harness.container.create_item(deepcopy(ORDER), **kwargs)
    return harness.container.read_item(ORDER["id"], partition_key=ORDER["customerId"], **kwargs)


@pytest.mark.parametrize("operation,status", [("create_item", 201), ("read_item", 200), ("read_item", 304)])
def test_sync_public_success_preserves_hook_snapshots_and_span_lifetime(sync_create, recording, operation, status):
    sync_create.response_status = status
    seen = []

    def response_hook(headers, item):
        state = telemetry._OPERATION.get()
        assert state is not None and not state.closed
        assert state.collector.received == 1
        assert not attempt_spans(recording)
        seen.append((dict(headers), dict(item)))
        headers["x-ms-request-charge"] = "999"
        item["id"] = "hook-only"

    with trace.get_tracer("customer").start_as_current_span("read-or-save") as parent:
        result = sync_call(sync_create, operation, timeout=10, response_hook=response_hook)
        assert trace.get_current_span() is parent
    assert result == ({} if status == 304 else ORDER)
    assert len(seen) == 1
    assert seen[0][1] == ({} if status == 304 else ORDER)
    assert result.get_response_headers()["x-ms-request-charge"] == "5.0"
    assert result.get_response_headers()["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
    enabled, budget, prepared = sync_create.calls[0]
    assert enabled and 0 < budget <= 10
    assert not any("telemetry" in key or "attempt" in key for key in prepared.headers)
    (span,) = [s for s in recording.exporter.get_finished_spans() if s.name == f"ContainerProxy.{operation}"]
    (attempt,) = attempt_spans(recording)
    row = sync_create.payloads[0]["attempts"][0]
    assert span.parent.span_id == parent.get_span_context().span_id
    assert attempt.parent.span_id == span.context.span_id
    assert span.start_time <= attempt.start_time == row["start_ns"]
    assert attempt.end_time == row["end_ns"] <= span.end_time
    assert span.status.status_code is trace.StatusCode.UNSET
    assert sync_create.states[0].closed and sync_create.states[0].collector.diagnostics is None
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize(
    "operation,status,exception",
    [
        ("create_item", 409, CosmosResourceExistsError),
        ("read_item", 404, CosmosResourceNotFoundError),
        ("create_item", 408, ServiceResponseError),
        ("read_item", 408, ServiceResponseError),
    ],
)
def test_sync_public_failures_preserve_errors_and_do_not_invoke_hook(
    sync_create, recording, operation, status, exception
):
    sync_create.response_status = status
    hook = Mock()
    with pytest.raises(exception) as error:
        sync_call(sync_create, operation, response_hook=hook)
    hook.assert_not_called()
    assert len(sync_create.calls) == 1
    if status == 408:
        assert error.value.__cause__ is sync_create.driver_error
    else:
        assert error.value.status_code == status
        assert error.value.headers["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
    (span,) = [s for s in recording.exporter.get_finished_spans() if s.name == f"ContainerProxy.{operation}"]
    assert span.status.status_code is trace.StatusCode.ERROR
    assert len(attempt_spans(recording)) == 1
    assert sync_create.states[0].closed
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("operation", ["create_item", "read_item"])
def test_sync_response_hook_exception_is_not_replayed_or_replaced(sync_create, recording, operation):
    sync_create.response_status = 201 if operation == "create_item" else 200
    failure = ValueError("response hook failure")
    hook = Mock(side_effect=failure)
    with pytest.raises(ValueError) as error:
        sync_call(sync_create, operation, response_hook=hook)
    assert error.value is failure
    hook.assert_called_once()
    assert len(sync_create.calls) == len(attempt_spans(recording)) == 1
    (span,) = [s for s in recording.exporter.get_finished_spans() if s.name == f"ContainerProxy.{operation}"]
    assert span.status.status_code is trace.StatusCode.ERROR
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("operation", ["create_item", "read_item"])
@pytest.mark.parametrize("mode", ["disabled", "global-disabled", "sampled-out", "merged", "nested"])
def test_sync_calls_without_owned_recording_span_do_not_collect_attempts(sync_create, recording, operation, mode):
    sync_create.response_status = 201 if operation == "create_item" else 200
    if mode == "global-disabled":
        settings.tracing_enabled = False
    elif mode == "sampled-out":
        recording.provider.sampler = ALWAYS_OFF
    kwargs = {"tracing_options": {"enabled": False}} if mode == "disabled" else {}
    if mode == "merged":
        kwargs["merge_span"] = True
    if mode == "nested":

        @distributed_trace
        def outer():
            return sync_call(sync_create, operation)

        result = outer()
    else:
        result = sync_call(sync_create, operation, **kwargs)
    assert result == ORDER
    assert sync_create.calls[0][0] is False
    assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("operation", ["create_item", "read_item"])
def test_sync_timeout_preserves_exception_and_cleans_state(sync_create, recording, operation):
    sync_create.error = TimeoutError("binding timeout")
    with pytest.raises(CosmosClientTimeoutError) as error:
        sync_call(sync_create, operation, timeout=10)
    assert error.value.__cause__ is sync_create.error
    assert len(sync_create.calls) == 1
    assert not attempt_spans(recording)
    assert sync_create.states[0].closed
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("operation", ["create_item", "read_item"])
def test_sync_disabled_calls_do_not_import_opentelemetry(sync_create, monkeypatch, operation):
    settings.tracing_enabled = False
    sync_create.response_status = 201 if operation == "create_item" else 200
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.startswith("opentelemetry"):
            raise AssertionError("Disabled call imported optional telemetry")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    assert sync_call(sync_create, operation) == ORDER
    assert sync_create.calls[0][0] is False


def test_sync_threads_have_independent_operation_state(sync_create, recording):
    sync_create.barrier = Barrier(4)

    def save(index):
        with trace.get_tracer("customer").start_as_current_span(f"save-{index}"):
            return sync_call(sync_create, "create_item")

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(save, range(8))) == [ORDER] * 8
    operations = operation_spans(recording)
    assert len(operations) == len(attempt_spans(recording)) == 8
    assert len({s.context.trace_id for s in operations}) == 8
    assert len({id(state) for state in sync_create.states}) == 8
    assert len({state.thread for state in sync_create.states}) == 4
    for operation in operations:
        assert len([s for s in attempt_spans(recording) if s.parent.span_id == operation.context.span_id]) == 1
    assert all(state.closed and state.collector.diagnostics is None for state in sync_create.states)


def test_operation_state_rejects_wrong_backend_task_thread_and_completed_work(sync_create):
    from contextvars import copy_context

    with trace.get_tracer("customer").start_as_current_span("owner") as span:
        state = telemetry._Operation(
            "create_item",
            sync_create.backend,
            span.get_span_context(),
            telemetry._current_task(),
            telemetry.get_ident(),
            "create_item",
            parent=span,
        )
        token = telemetry._OPERATION.set(state)
        try:
            assert telemetry.get_operation(sync_create.backend, "create_item") is state
            assert telemetry.get_operation(object(), "create_item") is None
            assert telemetry.get_operation(sync_create.backend, "read_item") is None
            context = copy_context()
            with ThreadPoolExecutor(max_workers=1) as pool:
                assert (
                    pool.submit(context.run, telemetry.get_operation, sync_create.backend, "create_item").result()
                    is None
                )

            async def child():
                assert telemetry.get_operation(sync_create.backend, "create_item") is None

            asyncio.run(child())
            state.finish()
            assert telemetry.get_operation(sync_create.backend, "create_item") is None
        finally:
            telemetry._OPERATION.reset(token)


@pytest.mark.parametrize("runtime", ["sync", "async"])
@pytest.mark.parametrize("operation", ["create_item", "read_item"])
def test_per_call_enablement_overrides_global_disable(create, sync_create, recording, runtime, operation):
    settings.tracing_enabled = False
    harness = sync_create if runtime == "sync" else create
    harness.response_status = 201 if operation == "create_item" else 200
    options = {"tracing_options": {"enabled": True}}
    if runtime == "sync":
        result = sync_call(harness, operation, **options)
    elif operation == "create_item":
        result = asyncio.run(harness.container.create_item(ORDER, **options))
    else:
        result = asyncio.run(harness.container.read_item(ORDER["id"], partition_key=ORDER["customerId"], **options))
    assert result == ORDER
    assert harness.calls[0][0] is True
    assert attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


def test_nested_response_hook_call_does_not_consume_outer_state(sync_create, recording):
    states = []

    def response_hook(_headers, _item):
        state = telemetry._OPERATION.get()
        states.append(state)
        assert sync_call(sync_create, "create_item") == ORDER
        assert telemetry._OPERATION.get() is state
        assert state.collector.received == 1 and not state.closed

    assert sync_call(sync_create, "create_item", response_hook=response_hook) == ORDER
    assert [call[0] for call in sync_create.calls] == [True, False]
    assert len(operation_spans(recording)) == len(attempt_spans(recording)) == 1
    assert states[0].closed
    assert telemetry._OPERATION.get() is None


class FailingTelemetryLogHandler(logging.Handler):
    def emit(self, record):
        raise RuntimeError("PRIVATE logging failure")


@pytest.mark.parametrize("runtime", ["sync", "async"])
@pytest.mark.parametrize("status", [201, 409])
def test_telemetry_reporting_failure_preserves_public_outcome(create, sync_create, runtime, status, monkeypatch, capfd):
    harness = sync_create if runtime == "sync" else create
    harness.response_status = status
    harness.transform = lambda result: (result[0], {"schema_version": 999})
    logger = telemetry._LOGGER
    handler = FailingTelemetryLogHandler()
    monkeypatch.setattr(logger, "level", logging.WARNING)
    before = telemetry._REPORTING_FAILURES
    logger.addHandler(handler)
    try:

        def call():
            if runtime == "sync":
                return sync_call(harness, "create_item")
            return asyncio.run(harness.container.create_item(ORDER))

        if status == 409:
            with pytest.raises(CosmosResourceExistsError) as error:
                call()
            assert error.value.status_code == 409
        else:
            assert call() == ORDER
        assert len(harness.calls) == 1
        assert telemetry._REPORTING_FAILURES > before
        assert telemetry._OPERATION.get() is None
        stderr = capfd.readouterr().err
        assert "Rust telemetry reporting failed" in stderr
        assert "PRIVATE" not in stderr
    finally:
        logger.removeHandler(handler)


def test_failed_logging_and_stderr_leave_a_reporting_failure_count(monkeypatch):
    logger = telemetry._LOGGER
    handler = FailingTelemetryLogHandler()
    monkeypatch.setattr(logger, "level", logging.WARNING)
    monkeypatch.setattr(sys, "__stderr__", SimpleNamespace(write=Mock(side_effect=OSError("PRIVATE"))))
    before = telemetry._REPORTING_FAILURES
    logger.addHandler(handler)
    try:
        telemetry._report("Sanitized diagnostics failure")
    finally:
        logger.removeHandler(handler)
    assert telemetry._REPORTING_FAILURES == before + 1


def contribution_response(total, start, count=2):
    payload = {
        "schema_version": 1,
        "request_count": total,
        "retained_request_count": count,
        "error": None,
        "attempts": [
            {
                "start_ns": start + index,
                "end_ns": start + index + 1,
                "driver_status_code": 200,
                "execution_context": "initial",
            }
            for index in range(count)
        ],
    }
    return (200, 0, {}, b"{}", None), payload


def test_aggregation_counts_once_bounds_detail_and_rejects_late_delivery(recording, caplog):
    received = []
    with trace.get_tracer("test").start_as_current_span("combined") as parent:
        state = telemetry._Operation(
            "read_items",
            object(),
            parent.get_span_context(),
            None,
            telemetry.get_ident(),
            "read_item",
            parent=parent,
            handlers=(telemetry.CompletionHandler(received.append),),
            collector=telemetry._DiagnosticCollector(retained_limit=3),
        )
        first, second = state.begin_contribution(), state.begin_contribution()
        stamp = time.time_ns()
        left, right = contribution_response(5, stamp), contribution_response(7, stamp + 10)
        second.response(right)
        first.response(left)
        first.response(left)
        state.finish()
        state.finish()
        second.response(right)
    assert len(received) == 1
    completion = received[0]
    assert completion.operation == "read_items"
    assert completion.diagnostics.complete
    assert completion.diagnostics.request_count == 12
    assert [attempt.start_ns for attempt in completion.diagnostics.attempts] == [stamp, stamp + 1, stamp + 11]
    spans = recording.exporter.get_finished_spans()
    operation = next(span for span in spans if span.name == "combined")
    assert operation.attributes["cosmos.poc.request_count"] == 12
    assert operation.attributes["cosmos.poc.retained_request_count"] == 3
    assert len(attempt_spans(recording)) == 3
    assert "duplicate or late" in caplog.text
    assert state.closed and state.collector.diagnostics is None
    assert state.parent is None and not state.handlers
    with pytest.raises(FrozenInstanceError):
        completion.outcome = "error"


@pytest.mark.parametrize("defect", ["missing", "invalid", "unfinished", "unbounded"])
def test_incomplete_contributions_do_not_publish_partial_counts_as_totals(recording, defect, caplog):
    received = []
    with trace.get_tracer("test").start_as_current_span("combined") as parent:
        state = telemetry._Operation(
            "read_items",
            object(),
            parent.get_span_context(),
            None,
            telemetry.get_ident(),
            "read_item",
            parent=parent,
            handlers=(telemetry.CompletionHandler(received.append),),
            collector=telemetry._DiagnosticCollector(retained_limit=None if defect == "unbounded" else 4),
        )
        state.begin_contribution().response(contribution_response(5, time.time_ns()))
        second = state.begin_contribution()
        if defect == "missing":
            second.response(((200, 0, {}, b"{}", None), None))
        elif defect == "invalid":
            second.response(((200, 0, {}, b"{}", None), {"schema_version": True}))
        elif defect == "unbounded":
            assert second is None
        state.finish("error")
    assert len(received) == 1
    completion = received[0]
    assert not completion.diagnostics.complete
    assert completion.diagnostics.request_count == 5
    operation = next(span for span in recording.exporter.get_finished_spans() if span.name == "combined")
    assert "cosmos.poc.request_count" not in operation.attributes
    assert "cosmos.poc.retained_request_count" not in operation.attributes
    assert "operation totals are unavailable" in caplog.text


def test_explicit_contributions_can_complete_on_other_threads_without_sharing_span_state():
    collector = telemetry._DiagnosticCollector(retained_limit=3)
    contributions = [collector.reserve() for _ in range(8)]
    gate = Barrier(4)
    stamp = time.time_ns()

    def complete(index):
        gate.wait(timeout=5)
        contributions[index].response(contribution_response(5, stamp + index * 10))

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(complete, range(8)))
    first, diagnostics = collector.close()
    assert first and diagnostics.complete
    assert diagnostics.request_count == 40
    assert len(diagnostics.attempts) == 3
    assert [attempt.start_ns for attempt in diagnostics.attempts] == [stamp, stamp + 1, stamp + 71]
    assert collector.close() == (False, None)


@pytest.mark.parametrize("limit", [-1, True, "3"])
def test_invalid_aggregate_limits_fail_at_internal_configuration(limit):
    with pytest.raises(ValueError):
        telemetry._DiagnosticCollector(retained_limit=limit)


@pytest.mark.parametrize("runtime", ["sync", "async"])
@pytest.mark.parametrize("mode", ["disabled", "sampled-out"])
@pytest.mark.parametrize("collect", [False, True])
@pytest.mark.parametrize("status", [201, 409])
def test_completion_handlers_are_independent_of_trace_recording(
    create, sync_create, recording, runtime, mode, collect, status
):
    harness = sync_create if runtime == "sync" else create
    harness.response_status = status
    seen = []
    registration = telemetry.CompletionHandler(seen.append, collect_attempts=collect)
    harness.container._item_context = replace(harness.container._item_context, telemetry_handlers=(registration,))
    if mode == "disabled":
        settings.tracing_enabled = False
    else:
        recording.provider.sampler = ALWAYS_OFF

    def call():
        if runtime == "sync":
            return sync_call(harness, "create_item")
        return asyncio.run(harness.container.create_item(ORDER))

    if status == 409:
        with pytest.raises(CosmosResourceExistsError):
            call()
    else:
        assert call() == ORDER
    assert len(seen) == 1
    completion = seen[0]
    assert completion.operation == "create_item"
    assert completion.outcome == ("success" if status == 201 else "error")
    assert completion.execution_duration_ns >= 0
    assert (completion.diagnostics is not None) is collect
    assert harness.calls[0][0] is collect
    assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("options", [{}, {"tracing_options": {"enabled": False}}])
def test_disabled_recording_does_not_inspect_backend(sync_create, monkeypatch, options):
    settings.tracing_enabled = bool(options)

    def unexpected_selection(_backend):
        raise AssertionError("Disabled recording inspected the backend")

    monkeypatch.setattr(telemetry, "is_rust_backend", unexpected_selection)
    assert telemetry._new_operation(sync_create.container, "create_item", options) is None


def test_handler_only_completion_does_not_import_opentelemetry(sync_create, monkeypatch):
    settings.tracing_enabled = False
    seen = []
    sync_create.container._item_context = replace(
        sync_create.container._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(seen.append, collect_attempts=True),),
    )
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.startswith("opentelemetry"):
            raise AssertionError("Handler-only completion imported tracing")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    assert sync_call(sync_create, "create_item") == ORDER
    assert seen[0].diagnostics.request_count == 1


def test_handler_failure_does_not_replace_hook_failure_or_stop_other_handlers(sync_create, monkeypatch, caplog):
    seen = []
    hook_failure = ValueError("response hook failure")
    clock = [100]
    monkeypatch.setattr(telemetry, "perf_counter_ns", lambda: clock[0])

    def bad_handler(_completion):
        clock[0] = 1000
        raise RuntimeError("PRIVATE handler failure")

    sync_create.container._item_context = replace(
        sync_create.container._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(bad_handler), telemetry.CompletionHandler(seen.append)),
    )

    def response_hook(_headers, _item):
        clock[0] = 200
        raise hook_failure

    with pytest.raises(ValueError) as error:
        sync_call(sync_create, "create_item", response_hook=response_hook)
    assert error.value is hook_failure
    assert len(seen) == 1
    completion = seen[0]
    assert completion.outcome == "error"
    assert completion.execution_duration_ns == 100
    assert completion.diagnostics.request_count == 1
    assert "completion handler failed" in caplog.text
    assert "PRIVATE" not in caplog.text


def test_cancelled_public_call_notifies_independent_handlers(create):
    seen = []
    create.container._item_context = replace(
        create.container._item_context, telemetry_handlers=(telemetry.CompletionHandler(seen.append),)
    )

    async def run():
        create.gate = asyncio.Event()
        task = asyncio.create_task(create.container.create_item(ORDER))
        await create.gate.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert telemetry._OPERATION.get() is None

    asyncio.run(run())
    assert len(seen) == 1
    completion = seen[0]
    assert completion.outcome == "cancelled"
    assert completion.diagnostics is None


def test_public_identity_can_differ_from_binding_operation(sync_create, recording):
    sync_call(sync_create, "create_item", tracing_options={"enabled": False})
    prepared = sync_create.calls[0][2]
    seen = []
    context = replace(
        sync_create.container._item_context, telemetry_handlers=(telemetry.CompletionHandler(seen.append),)
    )

    class PublicOperation:
        _item_context = context

        @telemetry.trace_operation(binding_operation="create_item")
        def save_order(self):
            return sync_create.backend.execute(prepared)

    assert PublicOperation().save_order().status_code == 201
    assert sync_create.calls[-1][0] is True
    assert seen[0].operation == "save_order"
    assert len(attempt_spans(recording)) == 1


@pytest.mark.parametrize("limit", [0, 1, 3])
def test_collector_snapshots_input_and_honors_zero_or_small_limits(limit):
    collector = telemetry._DiagnosticCollector(retained_limit=limit)
    payload = contribution_response(5, time.time_ns(), count=4)
    contribution = collector.reserve()
    contribution.response(payload)
    payload[1]["attempts"].clear()
    first, diagnostics = collector.close()
    assert first and diagnostics.complete
    assert diagnostics.request_count == 5
    assert len(diagnostics.attempts) == limit


def test_contribution_cannot_be_completed_by_an_unrelated_collector(caplog):
    owner = telemetry._DiagnosticCollector()
    other = telemetry._DiagnosticCollector()
    contribution = owner.reserve()
    other.accept(contribution, telemetry._Diagnostics(1, ()))
    assert not contribution.consumed
    assert other.diagnostics is None
    contribution.response(contribution_response(5, time.time_ns()))
    assert owner.close()[1].request_count == 5
    assert "different owner" in caplog.text


def test_completion_reporting_failure_preserves_original_response_hook_error(sync_create, monkeypatch, capfd):
    failure = ValueError("customer response hook failure")
    logger = telemetry._LOGGER
    monkeypatch.setattr(logger, "level", logging.WARNING)
    handler = FailingTelemetryLogHandler()
    monkeypatch.setattr(telemetry, "emit_attempts", Mock(side_effect=RuntimeError("PRIVATE emitter failure")))
    logger.addHandler(handler)
    try:
        with pytest.raises(ValueError) as caught:
            sync_call(sync_create, "create_item", response_hook=Mock(side_effect=failure))
        assert caught.value is failure
        assert len(sync_create.calls) == 1
        assert telemetry._OPERATION.get() is None
        assert "PRIVATE" not in capfd.readouterr().err
    finally:
        logger.removeHandler(handler)


@pytest.fixture(name="item_runtime", params=["sync", "async"])
def item_runtime_harness(request, recording):  # pylint: disable=unused-argument
    harness = request.getfixturevalue("sync_create" if request.param == "sync" else "create")

    def invoke(method, *args, **kwargs):
        result = method(*args, **kwargs)
        return result if request.param == "sync" else asyncio.run(result)

    harness.invoke = invoke
    return harness


@pytest.fixture(name="delete")
def delete_harness(item_runtime):
    item_runtime.response_status = 204
    item_runtime.delete = lambda **kwargs: item_runtime.invoke(
        item_runtime.container.delete_item, ORDER["id"], partition_key=ORDER["customerId"], **kwargs
    )
    return item_runtime


@pytest.fixture(name="container_read")
def container_read_harness(item_runtime):
    item_runtime.response_status = 200
    item_runtime.connection = SimpleNamespace(
        _backend=item_runtime.backend,
        ReadContainer=Mock(side_effect=AssertionError("Unexpected legacy container read")),
        _set_container_properties_cache=Mock(),
        last_response_headers={},
    )
    item_runtime.container.client_connection = item_runtime.connection
    item_runtime.read_properties = lambda **kwargs: item_runtime.invoke(item_runtime.container.read, **kwargs)
    return item_runtime


@pytest.fixture(name="container_delete")
def container_delete_harness(item_runtime):
    item_runtime.response_status = 204
    item_runtime.connection = SimpleNamespace(
        _backend=item_runtime.backend,
        DeleteContainer=Mock(side_effect=AssertionError("Unexpected legacy container delete")),
        ReadContainer=Mock(side_effect=AssertionError("Unexpected Python metadata read")),
        last_response_headers={},
    )
    proxy = (
        DatabaseProxy if isinstance(item_runtime.backend, binding_adapter.AsyncBindingAdapter) else SyncDatabaseProxy
    )
    item_runtime.database = proxy(item_runtime.connection, "sales", _item_context=item_runtime.container._item_context)
    item_runtime.delete_container = lambda **kwargs: item_runtime.invoke(
        item_runtime.database.delete_container, "orders", **kwargs
    )
    return item_runtime


@pytest.fixture(name="upsert")
def upsert_harness(item_runtime):
    item_runtime.response_status = 201
    item_runtime.upsert = lambda **kwargs: item_runtime.invoke(
        item_runtime.container.upsert_item, deepcopy(ORDER), **kwargs
    )
    return item_runtime


@pytest.fixture(name="container_create")
def container_create_harness(item_runtime):
    item_runtime.response_status = 201
    item_runtime.connection = SimpleNamespace(
        _backend=item_runtime.backend,
        CreateContainer=Mock(side_effect=AssertionError("Unexpected legacy container create")),
        ReadContainer=Mock(side_effect=AssertionError("Unexpected Python metadata read")),
        _set_container_properties_cache=Mock(),
        last_response_headers={},
    )
    proxy = (
        DatabaseProxy if isinstance(item_runtime.backend, binding_adapter.AsyncBindingAdapter) else SyncDatabaseProxy
    )
    item_runtime.database = proxy(item_runtime.connection, "sales", _item_context=item_runtime.container._item_context)
    item_runtime.create_container = lambda **kwargs: item_runtime.invoke(
        item_runtime.database.create_container, "orders", PartitionKey(path="/customerId"), **kwargs
    )
    return item_runtime


@pytest.fixture(name="replacement")
def replacement_harness(item_runtime):
    item_runtime.response_status = 200

    def call(*, item=ORDER["id"], body=None, **kwargs):
        return item_runtime.invoke(
            item_runtime.container.replace_item, item, deepcopy(ORDER) if body is None else body, **kwargs
        )

    item_runtime.replacement = call
    return item_runtime


@pytest.fixture(name="patch")
def patch_harness(item_runtime):
    item_runtime.response_status = 200
    item_runtime.patch_timeout = 10

    def call(*, item=ORDER["id"], operations=None, **kwargs):
        if item_runtime.patch_timeout is not None:
            kwargs.setdefault("timeout", item_runtime.patch_timeout)
        return item_runtime.invoke(
            item_runtime.container.patch_item,
            item,
            ORDER["customerId"],
            [{"op": "set", "path": "/total", "value": 200}] if operations is None else operations,
            **kwargs,
        )

    item_runtime.patch = call
    return item_runtime


@pytest.fixture(name="point_write", params=["delete", "upsert", "replacement", "patch"])
def point_write_harness(request, item_runtime):  # pylint: disable=unused-argument
    harness = request.getfixturevalue(request.param)
    harness.write = getattr(harness, request.param)
    harness.operation = "replace_item" if request.param == "replacement" else f"{request.param}_item"
    harness.expected_result = None if request.param == "delete" else ORDER
    harness.service_error_status = 404 if request.param == "delete" else 412
    harness.service_error_type = (
        CosmosResourceNotFoundError if request.param == "delete" else CosmosAccessConditionFailedError
    )
    return harness


def assert_item_attempts(harness, recording, parent, status, name, owner="ContainerProxy"):
    attempts = attempt_spans(recording)
    operations = [span for span in recording.exporter.get_finished_spans() if span.name == f"{owner}.{name}"]
    assert len(operations) == 1
    operation = operations[0]
    assert operation.parent.span_id == parent.get_span_context().span_id
    assert operation.status.status_code is (trace.StatusCode.UNSET if status < 400 else trace.StatusCode.ERROR)
    payload = harness.payloads[0]
    assert operation.attributes["cosmos.poc.request_count"] == payload["request_count"]
    assert operation.attributes["cosmos.poc.retained_request_count"] == len(attempts)
    assert len(attempts) == payload["retained_request_count"]
    for span, row in zip(attempts, payload["attempts"]):
        assert span.parent.span_id == operation.context.span_id
        assert span.context.trace_id == operation.context.trace_id
        assert operation.start_time <= span.start_time == row["start_ns"]
        assert span.end_time == row["end_ns"] <= operation.end_time


@pytest.mark.parametrize("status", [201, 409, 408])
@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize(
    "mode",
    ["enabled", "disabled", "global-disabled", "sampled-out", "merged", "handler-only", "attributes", "enable-call"],
)
def test_container_create_owns_returned_proxy_and_properties(  # pylint: disable=too-many-statements
    container_create, recording, status, return_properties, mode
):
    harness = container_create
    harness.response_status = status
    seen, hooks = [], []
    harness.database._item_context = replace(
        harness.database._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(seen.append, collect_attempts=mode == "handler-only"),),
    )
    kwargs = {"timeout": 10, "return_properties": return_properties}
    if mode in ("global-disabled", "handler-only", "enable-call"):
        settings.tracing_enabled = False
    elif mode == "disabled":
        kwargs["tracing_options"] = {"enabled": False}
    elif mode == "sampled-out":
        recording.provider.sampler = ALWAYS_OFF
    elif mode == "merged":
        kwargs["merge_span"] = True
    if mode == "enable-call":
        kwargs["tracing_options"] = {"enabled": True}
    elif mode == "attributes":
        kwargs["tracing_attributes"] = {"test.context": "create-config"}
    collect = mode in ("enabled", "handler-only", "attributes", "enable-call")

    def hook(headers, body):
        state = telemetry._OPERATION.get()
        assert state is not None and not state.closed
        assert state.backend is harness.database._item_context.adapter is harness.connection._backend
        assert state.binding_operation == "create_container" and state.collector.received == int(collect)
        assert not seen and not attempt_spans(recording)
        assert body["partitionKey"]["paths"] == ["/customerId"]
        hooks.append(body)
        headers.clear()
        # Create hooks already receive the returned body, unlike read's body snapshot.
        body["defaultTtl"] = 42

    def cache(link, properties):
        assert link == "dbs/sales/colls/orders"
        assert properties["partitionKey"]["paths"] == ["/customerId"]
        assert not telemetry._OPERATION.get().closed and not seen
        assert len(hooks) == 1

    harness.connection._set_container_properties_cache.side_effect = cache
    with trace.get_tracer("customer").start_as_current_span("create_disposable") as parent:
        if status == 201:
            result = harness.create_container(response_hook=hook, **kwargs)
            container = result[0] if return_properties else result
            assert isinstance(container, (ContainerProxy, SyncContainerProxy))
            assert container.id == "orders" and container._item_context is harness.database._item_context
            if return_properties:
                assert result[1] is hooks[0] and result[1]["defaultTtl"] == 42
            harness.connection._set_container_properties_cache.assert_called_once()
        else:
            with pytest.raises(CosmosResourceExistsError if status == 409 else ServiceResponseError) as caught:
                harness.create_container(response_hook=hook, **kwargs)
            if status == 408:
                assert caught.value.__cause__ is harness.driver_error
            assert not hooks
            harness.connection._set_container_properties_cache.assert_not_called()
        assert trace.get_current_span() is parent
    assert len(harness.calls) == 1 and harness.calls[0][0] is collect
    prepared = harness.prepared_requests[0]
    assert prepared.op == "create_container" and prepared.item_id == "sales"
    assert prepared.container_link == "" and prepared.settings.timeout_seconds == 10
    assert json.loads(prepared.body_bytes)["partitionKey"]["paths"] == ["/customerId"]
    assert not any("tracing" in key or "test." in key for key in prepared.headers)
    harness.connection.CreateContainer.assert_not_called()
    harness.connection.ReadContainer.assert_not_called()
    assert len(seen) == 1 and seen[0].operation == "create_container"
    assert seen[0].outcome == ("success" if status == 201 else "error")
    assert (seen[0].diagnostics is not None) is collect
    if status != 408:
        assert harness.connection.last_response_headers["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
    if mode in ("enabled", "attributes", "enable-call"):
        assert_item_attempts(harness, recording, parent, status, "create_container", owner="DatabaseProxy")
        if mode == "attributes":
            operation = next(
                span
                for span in recording.exporter.get_finished_spans()
                if span.name == "DatabaseProxy.create_container"
            )
            assert operation.attributes["test.context"] == "create-config"
    else:
        assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("mode", ["enabled", "disabled", "global-disabled"])
@pytest.mark.parametrize("failure", ["none", "diagnostics", "emitter", "handler"])
@pytest.mark.parametrize("outcome", ["success", "hook-error", "cache-error", "timeout"])
def test_container_create_preserves_errors_when_reporting_fails(
    container_create, recording, monkeypatch, mode, failure, outcome
):
    harness = container_create
    original = ValueError("public completion failure")
    hook = Mock(side_effect=original if outcome == "hook-error" else None)
    if outcome == "cache-error":
        harness.connection._set_container_properties_cache.side_effect = original
    kwargs = {"tracing_options": {"enabled": False}} if mode == "disabled" else {}
    if mode == "global-disabled":
        settings.tracing_enabled = False
    if outcome == "timeout":
        harness.response_status = 408
        harness.driver_error_type = TimeoutError
    seen = []
    handlers = (telemetry.CompletionHandler(seen.append),)
    if failure == "diagnostics":
        harness.transform = lambda result: (result[0], {"schema_version": 999})
    elif failure == "emitter":
        monkeypatch.setattr(telemetry, "emit_attempts", Mock(side_effect=RuntimeError("emitter failure")))
    elif failure == "handler":
        handlers = (telemetry.CompletionHandler(Mock(side_effect=RuntimeError("handler failure"))),) + handlers
    harness.database._item_context = replace(harness.database._item_context, telemetry_handlers=handlers)
    if outcome == "success":
        assert harness.create_container(response_hook=hook, **kwargs).id == "orders"
    else:
        with pytest.raises(TimeoutError if outcome == "timeout" else ValueError) as caught:
            harness.create_container(response_hook=hook, **kwargs)
        assert caught.value is (harness.driver_error if outcome == "timeout" else original)
    assert hook.call_count == (0 if outcome == "timeout" else 1)
    assert len(harness.calls) == len(seen) == 1
    assert seen[0].outcome == ("success" if outcome == "success" else "error")
    harness.connection.CreateContainer.assert_not_called()
    if mode != "enabled":
        assert not attempt_spans(recording)
    elif failure in ("none", "handler"):
        assert len(attempt_spans(recording)) == harness.payloads[0]["retained_request_count"]
        operation = next(
            span for span in recording.exporter.get_finished_spans() if span.name == "DatabaseProxy.create_container"
        )
        assert operation.status.status_code is (
            trace.StatusCode.UNSET if outcome == "success" else trace.StatusCode.ERROR
        )
    assert telemetry._OPERATION.get() is None


def test_async_container_create_cancellation_closes_database_operation(create, recording):
    harness = create
    connection = SimpleNamespace(
        _backend=harness.backend,
        CreateContainer=Mock(side_effect=AssertionError("Unexpected legacy create")),
        _set_container_properties_cache=Mock(),
    )
    database = DatabaseProxy(connection, "sales", _item_context=harness.container._item_context)
    seen = []
    database._item_context = replace(
        database._item_context, telemetry_handlers=(telemetry.CompletionHandler(seen.append),)
    )
    hook = Mock()

    async def run():
        harness.gate = asyncio.Event()
        with trace.get_tracer("customer").start_as_current_span("create_disposable"):
            pending = asyncio.create_task(
                database.create_container("orders", PartitionKey(path="/customerId"), response_hook=hook, timeout=10)
            )
            await harness.gate.wait()
            pending.cancel()
            with pytest.raises(asyncio.CancelledError):
                await pending

    asyncio.run(run())
    assert len(harness.calls) == len(seen) == 1
    assert seen[0].operation == "create_container" and seen[0].outcome == "cancelled"
    assert seen[0].diagnostics is None
    hook.assert_not_called()
    connection.CreateContainer.assert_not_called()
    connection._set_container_properties_cache.assert_not_called()
    assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("status", [204, 404, 412, 408])
@pytest.mark.parametrize(
    "mode",
    ["enabled", "disabled", "global-disabled", "sampled-out", "merged", "handler-only", "attributes", "enable-call"],
)
def test_container_delete_owns_database_context_until_completion(  # pylint: disable=too-many-statements
    container_delete, recording, status, mode
):
    harness = container_delete
    harness.response_status = status
    seen, hooks = [], []
    harness.database._item_context = replace(
        harness.database._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(seen.append, collect_attempts=mode == "handler-only"),),
    )
    kwargs = {"timeout": 10}
    if mode in ("global-disabled", "handler-only", "enable-call"):
        settings.tracing_enabled = False
    elif mode == "disabled":
        kwargs["tracing_options"] = {"enabled": False}
    elif mode == "sampled-out":
        recording.provider.sampler = ALWAYS_OFF
    elif mode == "merged":
        kwargs["merge_span"] = True
    if mode == "enable-call":
        kwargs["tracing_options"] = {"enabled": True}
    elif mode == "attributes":
        kwargs["tracing_options"] = {"attributes": {"test.context": "delete-config"}}
        kwargs["tracing_attributes"] = {"test.legacy": "delete-config"}
    collect = mode in ("enabled", "handler-only", "attributes", "enable-call")

    def hook(headers, body):
        state = telemetry._OPERATION.get()
        assert state is not None and not state.closed
        assert state.backend is harness.database._item_context.adapter is harness.connection._backend
        assert state.binding_operation == "delete_container"
        assert state.collector.received == int(collect)
        assert not seen and not attempt_spans(recording)
        assert body is None
        hooks.append(dict(headers))
        headers.clear()

    with trace.get_tracer("customer").start_as_current_span("delete_disposable") as parent:
        if status == 204:
            assert harness.delete_container(response_hook=hook, **kwargs) is None
            assert len(hooks) == 1
        else:
            error_type = {
                404: CosmosResourceNotFoundError,
                412: CosmosAccessConditionFailedError,
                408: ServiceResponseError,
            }[status]
            with pytest.raises(error_type) as caught:
                harness.delete_container(response_hook=hook, **kwargs)
            if status == 408:
                assert caught.value.__cause__ is harness.driver_error
            else:
                assert caught.value.status_code == status
            assert not hooks
        assert trace.get_current_span() is parent
    assert len(harness.calls) == 1 and harness.calls[0][0] is collect
    prepared = harness.prepared_requests[0]
    assert prepared.op == "delete_container" and prepared.settings.timeout_seconds == 10
    assert not any("test." in key or "tracing" in key for key in prepared.headers)
    harness.connection.DeleteContainer.assert_not_called()
    harness.connection.ReadContainer.assert_not_called()
    assert len(seen) == 1 and seen[0].operation == "delete_container"
    assert seen[0].outcome == ("success" if status == 204 else "error")
    assert (seen[0].diagnostics is not None) is collect
    if status != 408:
        assert harness.connection.last_response_headers["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
    if mode in ("enabled", "attributes", "enable-call"):
        assert_item_attempts(harness, recording, parent, status, "delete_container", owner="DatabaseProxy")
        if mode == "attributes":
            operation = next(
                span
                for span in recording.exporter.get_finished_spans()
                if span.name == "DatabaseProxy.delete_container"
            )
            assert operation.attributes["test.context"] == operation.attributes["test.legacy"] == "delete-config"
    else:
        assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("mode", ["enabled", "disabled", "global-disabled"])
@pytest.mark.parametrize("failure", ["none", "diagnostics", "emitter", "handler"])
@pytest.mark.parametrize("outcome", ["success", "hook-error", "timeout"])
def test_container_delete_preserves_errors_when_reporting_fails(
    container_delete, recording, monkeypatch, mode, failure, outcome
):
    harness = container_delete
    hook_error = ValueError("customer hook failure")
    hook = Mock(side_effect=hook_error if outcome == "hook-error" else None)
    kwargs = {"tracing_options": {"enabled": False}} if mode == "disabled" else {}
    if mode == "global-disabled":
        settings.tracing_enabled = False
    if outcome == "timeout":
        harness.response_status = 408
        harness.driver_error_type = TimeoutError
    seen = []
    handlers = (telemetry.CompletionHandler(seen.append),)
    if failure == "diagnostics":
        harness.transform = lambda result: (result[0], {"schema_version": 999})
    elif failure == "emitter":
        monkeypatch.setattr(telemetry, "emit_attempts", Mock(side_effect=RuntimeError("emitter failure")))
    elif failure == "handler":
        handlers = (telemetry.CompletionHandler(Mock(side_effect=RuntimeError("handler failure"))),) + handlers
    harness.database._item_context = replace(harness.database._item_context, telemetry_handlers=handlers)
    if outcome == "success":
        assert harness.delete_container(response_hook=hook, **kwargs) is None
    else:
        with pytest.raises(TimeoutError if outcome == "timeout" else ValueError) as caught:
            harness.delete_container(response_hook=hook, **kwargs)
        assert caught.value is (harness.driver_error if outcome == "timeout" else hook_error)
    assert hook.call_count == (0 if outcome == "timeout" else 1)
    if hook.called:
        assert hook.call_args.args[1] is None
    assert len(harness.calls) == len(seen) == 1
    assert seen[0].outcome == ("success" if outcome == "success" else "error")
    harness.connection.DeleteContainer.assert_not_called()
    if mode != "enabled":
        assert not attempt_spans(recording)
    elif failure in ("none", "handler"):
        assert len(attempt_spans(recording)) == harness.payloads[0]["retained_request_count"]
        operation = next(
            span for span in recording.exporter.get_finished_spans() if span.name == "DatabaseProxy.delete_container"
        )
        assert operation.status.status_code is (
            trace.StatusCode.UNSET if outcome == "success" else trace.StatusCode.ERROR
        )
    assert telemetry._OPERATION.get() is None


def test_container_delete_internal_metadata_is_not_a_second_contribution(container_delete, recording, monkeypatch):
    harness = container_delete
    is_async = isinstance(harness.backend, binding_adapter.AsyncBindingAdapter)
    module = binding_adapter if is_async else sync_binding_adapter
    binding_name = "delete_container_async" if is_async else "delete_container"
    metadata_name = "get_container_metadata_async" if is_async else "get_container_metadata"
    original = getattr(module._rust_module, binding_name)
    metadata = (AsyncMock if is_async else Mock)(return_value=("container-rid", ("/customerId",), "Hash", False))
    monkeypatch.setattr(module._rust_module, metadata_name, metadata, raising=False)

    async def delete_async(*args, **kwargs):
        await harness.backend.get_container_metadata(harness.container.container_link)
        return await original(*args, **kwargs)

    def delete_sync(*args, **kwargs):
        harness.backend.get_container_metadata(harness.container.container_link)
        return original(*args, **kwargs)

    monkeypatch.setattr(module._rust_module, binding_name, delete_async if is_async else delete_sync)
    with trace.get_tracer("customer").start_as_current_span("delete_disposable") as parent:
        assert harness.delete_container() is None
    metadata.assert_called_once_with("test-driver", harness.container.container_link)
    assert len(harness.calls) == 1
    assert_item_attempts(harness, recording, parent, 204, "delete_container", owner="DatabaseProxy")


def test_async_container_delete_cancellation_closes_database_operation(create, recording):
    harness = create
    harness.connection = SimpleNamespace(
        _backend=harness.backend, DeleteContainer=Mock(side_effect=AssertionError("Unexpected legacy delete"))
    )
    harness.database = DatabaseProxy(harness.connection, "sales", _item_context=harness.container._item_context)
    seen = []
    harness.database._item_context = replace(
        harness.database._item_context, telemetry_handlers=(telemetry.CompletionHandler(seen.append),)
    )
    hook = Mock()

    async def run():
        harness.gate = asyncio.Event()
        with trace.get_tracer("customer").start_as_current_span("delete_disposable"):
            pending = asyncio.create_task(harness.database.delete_container("orders", response_hook=hook, timeout=10))
            await harness.gate.wait()
            pending.cancel()
            with pytest.raises(asyncio.CancelledError):
                await pending

    asyncio.run(run())
    assert len(harness.calls) == len(seen) == 1
    assert seen[0].operation == "delete_container" and seen[0].outcome == "cancelled"
    assert seen[0].diagnostics is None
    hook.assert_not_called()
    harness.connection.DeleteContainer.assert_not_called()
    assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("status", [200, 304, 404, 412, 408])
@pytest.mark.parametrize(
    "mode",
    ["enabled", "disabled", "global-disabled", "sampled-out", "merged", "handler-only", "attributes", "enable-call"],
)
def test_container_read_owns_diagnostics_through_hook_and_cache(  # pylint: disable=too-many-statements
    container_read, recording, status, mode
):
    harness = container_read
    harness.response_status = status
    seen, hooks = [], []
    harness.container._item_context = replace(
        harness.container._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(seen.append, collect_attempts=mode == "handler-only"),),
    )
    kwargs = {}
    if mode in ("global-disabled", "handler-only", "enable-call"):
        settings.tracing_enabled = False
    elif mode == "disabled":
        kwargs["tracing_options"] = {"enabled": False}
    elif mode == "sampled-out":
        recording.provider.sampler = ALWAYS_OFF
    elif mode == "merged":
        kwargs["merge_span"] = True
    if mode == "enable-call":
        kwargs["tracing_options"] = {"enabled": True}
    elif mode == "attributes":
        kwargs["tracing_options"] = {"attributes": {"test.context": "read-config"}}
        kwargs["tracing_attributes"] = {"test.legacy": "read-config"}
    collect = mode in ("enabled", "handler-only", "attributes", "enable-call")

    def check_open_state():
        state = telemetry._OPERATION.get()
        assert state is not None and not state.closed
        assert state.binding_operation == "read_container"
        assert state.collector.received == int(collect)
        assert not seen and not attempt_spans(recording)

    def hook(headers, body):
        check_open_state()
        hooks.append(deepcopy(body))
        headers.clear()
        if body:
            body["partitionKey"]["paths"][0] = "/hook-only"
            body["indexingPolicy"].clear()

    harness.connection._set_container_properties_cache.side_effect = lambda *_: check_open_state()
    with trace.get_tracer("customer").start_as_current_span("inspect_orders") as parent:
        if status < 400:
            result = harness.read_properties(response_hook=hook, **kwargs)
            assert result == (CONTAINER_PROPERTIES if status == 200 else {})
            assert hooks == [result]
            assert result.get_response_headers()["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
            cached = harness.connection._set_container_properties_cache.call_args.args[1]
            assert cached["partitionKey"] == (CONTAINER_PROPERTIES["partitionKey"] if status == 200 else None)
        else:
            error_type = {
                404: CosmosResourceNotFoundError,
                412: CosmosAccessConditionFailedError,
                408: ServiceResponseError,
            }[status]
            with pytest.raises(error_type) as caught:
                harness.read_properties(response_hook=hook, **kwargs)
            if status == 408:
                assert caught.value.__cause__ is harness.driver_error
            else:
                assert caught.value.status_code == status
            assert not hooks
            harness.connection._set_container_properties_cache.assert_not_called()
        assert trace.get_current_span() is parent

    assert len(harness.calls) == 1
    assert harness.calls[0][0] is collect
    assert harness.prepared_requests[0].op == "read_container"
    harness.connection.ReadContainer.assert_not_called()
    assert len(seen) == 1 and seen[0].operation == "read"
    assert seen[0].outcome == ("success" if status < 400 else "error")
    assert (seen[0].diagnostics is not None) is collect
    if mode in ("enabled", "attributes", "enable-call"):
        assert_item_attempts(harness, recording, parent, status, "read")
        if mode == "attributes":
            operation = next(
                span for span in recording.exporter.get_finished_spans() if span.name == "ContainerProxy.read"
            )
            assert operation.attributes["test.context"] == operation.attributes["test.legacy"] == "read-config"
            assert not any("test." in key or "tracing" in key for key in harness.prepared_requests[0].headers)
    else:
        assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("failure", ["diagnostics", "emitter", "handler"])
@pytest.mark.parametrize("outcome", ["success", "hook-error", "timeout"])
def test_container_read_reporting_failures_preserve_execution(container_read, monkeypatch, failure, outcome):
    harness = container_read
    hook_error = ValueError("customer hook failure")
    hook = Mock(side_effect=hook_error if outcome == "hook-error" else None)
    if outcome == "timeout":
        harness.response_status = 408
        harness.driver_error_type = TimeoutError
    seen = []
    handlers = (telemetry.CompletionHandler(seen.append),)
    if failure == "diagnostics":
        harness.transform = lambda result: (result[0], {"schema_version": 999})
    elif failure == "emitter":
        monkeypatch.setattr(telemetry, "emit_attempts", Mock(side_effect=RuntimeError("emitter failure")))
    else:
        handlers = (telemetry.CompletionHandler(Mock(side_effect=RuntimeError("handler failure"))),) + handlers
    harness.container._item_context = replace(harness.container._item_context, telemetry_handlers=handlers)
    if outcome == "success":
        assert harness.read_properties(response_hook=hook) == CONTAINER_PROPERTIES
    else:
        with pytest.raises(TimeoutError if outcome == "timeout" else ValueError) as caught:
            harness.read_properties(response_hook=hook)
        assert caught.value is (harness.driver_error if outcome == "timeout" else hook_error)
        harness.connection._set_container_properties_cache.assert_not_called()
    assert hook.call_count == (0 if outcome == "timeout" else 1)
    assert len(harness.calls) == len(seen) == 1
    assert seen[0].outcome == ("success" if outcome == "success" else "error")
    assert telemetry._OPERATION.get() is None


def test_internal_metadata_does_not_contribute_to_public_container_read(container_read, recording, monkeypatch):
    harness = container_read
    is_async = isinstance(harness.backend, binding_adapter.AsyncBindingAdapter)
    module = binding_adapter if is_async else sync_binding_adapter
    binding_name = "read_container_async" if is_async else "read_container"
    metadata_name = "get_container_metadata_async" if is_async else "get_container_metadata"
    original = getattr(module._rust_module, binding_name)
    metadata = (AsyncMock if is_async else Mock)(return_value=("container-rid", ("/customerId",), "Hash", False))
    monkeypatch.setattr(module._rust_module, metadata_name, metadata, raising=False)

    async def read_async(*args, **kwargs):
        await harness.backend.get_container_metadata(harness.container.container_link)
        return await original(*args, **kwargs)

    def read_sync(*args, **kwargs):
        harness.backend.get_container_metadata(harness.container.container_link)
        return original(*args, **kwargs)

    monkeypatch.setattr(module._rust_module, binding_name, read_async if is_async else read_sync)
    with trace.get_tracer("customer").start_as_current_span("inspect_orders") as parent:
        assert harness.read_properties() == CONTAINER_PROPERTIES
    metadata.assert_called_once_with("test-driver", harness.container.container_link)
    assert len(harness.calls) == 1
    assert_item_attempts(harness, recording, parent, 200, "read")
    assert (
        len([span for span in recording.exporter.get_finished_spans() if span.name.startswith("ContainerProxy.")]) == 1
    )


def test_async_container_read_cancellation_completes_without_diagnostics(create, recording):
    create.response_status = 200
    create.container.client_connection = SimpleNamespace(
        _backend=create.backend,
        _set_container_properties_cache=Mock(),
        ReadContainer=Mock(side_effect=AssertionError("Unexpected legacy read")),
    )
    seen = []
    create.container._item_context = replace(
        create.container._item_context, telemetry_handlers=(telemetry.CompletionHandler(seen.append),)
    )
    hook = Mock()

    async def run():
        create.gate = asyncio.Event()
        with trace.get_tracer("customer").start_as_current_span("inspect_orders"):
            pending = asyncio.create_task(create.container.read(response_hook=hook))
            await create.gate.wait()
            pending.cancel()
            with pytest.raises(asyncio.CancelledError):
                await pending

    asyncio.run(run())
    assert len(create.calls) == len(seen) == 1
    assert seen[0].operation == "read" and seen[0].outcome == "cancelled"
    assert seen[0].diagnostics is None
    hook.assert_not_called()
    create.container.client_connection._set_container_properties_cache.assert_not_called()
    assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("status", [204, 404, 408])
@pytest.mark.parametrize("mode", ["enabled", "disabled", "global-disabled", "sampled-out", "merged"])
def test_delete_preserves_outcome_and_records_only_its_owned_attempts(delete, recording, status, mode):
    delete.response_status = status
    hooks = []
    kwargs = {}
    if mode == "global-disabled":
        settings.tracing_enabled = False
    elif mode == "disabled":
        kwargs["tracing_options"] = {"enabled": False}
    elif mode == "sampled-out":
        recording.provider.sampler = ALWAYS_OFF
    elif mode == "merged":
        kwargs["merge_span"] = True

    def response_hook(headers, item):
        hooks.append((dict(headers), item))
        if mode == "enabled":
            state = telemetry._OPERATION.get()
            assert state is not None and not state.closed
            assert state.collector.received == 1
            assert not attempt_spans(recording)
        headers["x-ms-request-charge"] = "changed"

    with trace.get_tracer("customer").start_as_current_span("delete_order") as parent:
        if status == 204:
            assert delete.delete(response_hook=response_hook, **kwargs) is None
            assert len(hooks) == 1
            assert hooks[0][1] is None
        else:
            with pytest.raises(CosmosResourceNotFoundError if status == 404 else ServiceResponseError) as caught:
                delete.delete(response_hook=response_hook, **kwargs)
            assert not hooks
            if status == 404:
                assert caught.value.status_code == 404
                assert caught.value.headers["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
            else:
                assert caught.value.__cause__ is delete.driver_error
        assert trace.get_current_span() is parent
        if parent.is_recording():
            assert not any(key.startswith("cosmos.poc.") for key in parent.attributes)

    assert len(delete.calls) == 1
    assert delete.calls[0][0] is (mode == "enabled")
    assert delete.calls[0][1] is None
    if status != 408:
        headers = delete.container._item_context.response_state.last_response_headers
        assert headers["x-ms-request-charge"] == "5.0"
        assert headers["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
    if mode == "enabled":
        assert_item_attempts(delete, recording, parent, status, "delete_item")
    else:
        assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("outcome", ["success", "service-error", "response-hook", "driver-timeout"])
@pytest.mark.parametrize("failure", ["diagnostics", "emitter", "handler"])
def test_point_write_telemetry_failures_cannot_replace_public_execution(
    point_write, monkeypatch, capfd, outcome, failure
):
    seen = []
    hook_error = ValueError("customer response hook failure")
    hook = Mock(side_effect=hook_error if outcome == "response-hook" else None)
    if outcome == "service-error":
        point_write.response_status = point_write.service_error_status
    elif outcome == "driver-timeout":
        point_write.response_status = 408
        point_write.driver_error_type = TimeoutError
    handlers = (telemetry.CompletionHandler(seen.append),)
    if failure == "diagnostics":
        point_write.transform = lambda result: (result[0], {"schema_version": 999})
    elif failure == "emitter":
        monkeypatch.setattr(telemetry, "emit_attempts", Mock(side_effect=RuntimeError("PRIVATE emitter failure")))
    else:
        handlers = (telemetry.CompletionHandler(Mock(side_effect=RuntimeError("PRIVATE handler failure"))),) + handlers
    point_write.container._item_context = replace(point_write.container._item_context, telemetry_handlers=handlers)
    logger = telemetry._LOGGER
    monkeypatch.setattr(logger, "level", logging.WARNING)
    handler = FailingTelemetryLogHandler()
    before = telemetry._REPORTING_FAILURES
    logger.addHandler(handler)
    try:
        if outcome == "success":
            assert point_write.write(response_hook=hook) == point_write.expected_result
        else:
            error_type = {
                "service-error": point_write.service_error_type,
                "response-hook": ValueError,
                "driver-timeout": CosmosClientTimeoutError if point_write.operation == "patch_item" else TimeoutError,
            }[outcome]
            with pytest.raises(error_type) as caught:
                point_write.write(response_hook=hook)
            if outcome == "response-hook":
                assert caught.value is hook_error
            elif outcome == "driver-timeout":
                original = caught.value.__cause__ if point_write.operation == "patch_item" else caught.value
                assert original is point_write.driver_error
        assert hook.call_count == (0 if outcome in ("service-error", "driver-timeout") else 1)
        if point_write.operation == "delete_item" and hook.call_count:
            assert hook.call_args.args[1] is None
        assert len(point_write.calls) == len(seen) == 1
        assert seen[0].operation == point_write.operation
        assert seen[0].outcome == ("success" if outcome == "success" else "error")
        assert telemetry._REPORTING_FAILURES > before
        assert telemetry._OPERATION.get() is None
        assert "PRIVATE" not in capfd.readouterr().err
    finally:
        logger.removeHandler(handler)


@pytest.mark.parametrize("collect", [False, True])
def test_point_write_completion_handler_does_not_require_tracing(point_write, collect):
    settings.tracing_enabled = False
    seen = []
    point_write.container._item_context = replace(
        point_write.container._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(seen.append, collect_attempts=collect),),
    )
    assert point_write.write() == point_write.expected_result
    assert point_write.calls[0][0] is collect
    assert len(seen) == 1
    assert seen[0].operation == point_write.operation
    assert seen[0].outcome == "success"
    assert (seen[0].diagnostics is not None) is collect


def test_point_write_without_tracing_does_not_import_opentelemetry(point_write, monkeypatch):
    settings.tracing_enabled = False
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.startswith("opentelemetry"):
            raise AssertionError("Disabled operation imported optional telemetry")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    assert point_write.write() == point_write.expected_result
    assert point_write.calls[0][0] is False


@pytest.mark.parametrize(
    "operation,timeout",
    [("delete_item", None), ("upsert_item", None), ("replace_item", None), ("patch_item", None), ("patch_item", 10)],
)
def test_point_write_cancellation_completes_once_without_inventing_attempts(create, recording, operation, timeout):
    seen = []
    hook = Mock()
    create.container._item_context = replace(
        create.container._item_context, telemetry_handlers=(telemetry.CompletionHandler(seen.append),)
    )

    async def run():
        create.gate = asyncio.Event()
        if operation == "delete_item":
            pending = create.container.delete_item(ORDER["id"], partition_key=ORDER["customerId"], response_hook=hook)
        elif operation == "replace_item":
            pending = create.container.replace_item(ORDER["id"], ORDER, response_hook=hook)
        elif operation == "patch_item":
            kwargs = {} if timeout is None else {"timeout": timeout}
            pending = create.container.patch_item(
                ORDER["id"],
                ORDER["customerId"],
                [{"op": "incr", "path": "/total", "value": 1}],
                response_hook=hook,
                **kwargs,
            )
        else:
            pending = create.container.upsert_item(ORDER, response_hook=hook)
        task = asyncio.create_task(pending)
        await create.gate.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    hook.assert_not_called()
    assert len(create.calls) == len(seen) == 1
    assert seen[0].operation == operation
    assert seen[0].outcome == "cancelled"
    assert seen[0].diagnostics is None
    assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("operation", ["delete_item", "upsert_item", "replace_item", "patch_item"])
def test_overlapping_point_writes_keep_their_own_attempts(create, recording, operation):
    create.response_status = {"delete_item": 204, "upsert_item": 201, "replace_item": 200, "patch_item": 200}[operation]

    async def write(item_id):
        with trace.get_tracer("customer").start_as_current_span(item_id):
            if operation == "delete_item":
                assert await create.container.delete_item(item_id, partition_key=ORDER["customerId"]) is None
            else:
                order = dict(ORDER, id=item_id)
                if operation == "replace_item":
                    assert await create.container.replace_item(item_id, order) == order
                elif operation == "patch_item":
                    assert (
                        await create.container.patch_item(
                            item_id, ORDER["customerId"], [{"op": "incr", "path": "/total", "value": 1}], timeout=10
                        )
                        == ORDER
                    )
                else:
                    assert await create.container.upsert_item(order) == order

    async def run():
        await asyncio.gather(write("order-A"), write("order-B"))

    asyncio.run(run())
    operations = [
        span for span in recording.exporter.get_finished_spans() if span.name == f"ContainerProxy.{operation}"
    ]
    assert len(operations) == len(create.calls) == 2
    assert len({span.context.trace_id for span in operations}) == 2
    for operation_span in operations:
        children = [span for span in attempt_spans(recording) if span.parent.span_id == operation_span.context.span_id]
        assert len(children) == 2
        assert all(span.context.trace_id == operation_span.context.trace_id for span in children)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize(
    "method,status",
    [
        ("upsert", 201),
        ("upsert", 200),
        ("upsert", 412),
        ("upsert", 408),
        ("replacement", 200),
        ("replacement", 404),
        ("replacement", 412),
        ("replacement", 408),
        ("patch", 200),
        ("patch", 404),
        ("patch", 412),
        ("patch", 408),
    ],
)
@pytest.mark.parametrize("mode", ["enabled", "disabled", "global-disabled", "sampled-out", "merged"])
def test_body_write_preserves_result_and_error_outcomes(
    item_runtime, request, recording, method, status, mode
):  # pylint: disable=unused-argument
    harness = request.getfixturevalue(method)
    harness.response_status = status
    operation = "replace_item" if method == "replacement" else f"{method}_item"
    call = getattr(harness, method)
    hooks = []
    if mode == "global-disabled":
        settings.tracing_enabled = False
    elif mode == "sampled-out":
        recording.provider.sampler = ALWAYS_OFF
    kwargs = {"tracing_options": {"enabled": False}} if mode == "disabled" else {}
    if mode == "merged":
        kwargs["merge_span"] = True

    def response_hook(headers, item):
        hooks.append((dict(headers), dict(item)))
        if mode == "enabled":
            assert telemetry._OPERATION.get().collector.received == 1
            assert not attempt_spans(recording)
        headers["x-ms-request-charge"] = "changed"
        item["id"] = "hook-only"

    with trace.get_tracer("customer").start_as_current_span("save_order") as parent:
        if status < 400:
            result = call(response_hook=response_hook, **kwargs)
            assert result == ORDER
            assert len(hooks) == 1 and hooks[0][1] == ORDER
            assert result.get_response_headers()["x-ms-request-charge"] == "5.0"
        else:
            exception = {
                404: CosmosResourceNotFoundError,
                412: CosmosAccessConditionFailedError,
                408: ServiceResponseError,
            }
            with pytest.raises(exception[status]) as caught:
                call(response_hook=response_hook, **kwargs)
            assert not hooks
            if status in (404, 412):
                assert caught.value.status_code == status
                assert caught.value.headers["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
            else:
                assert caught.value.__cause__ is harness.driver_error
        assert trace.get_current_span() is parent
        if parent.is_recording():
            assert not any(key.startswith("cosmos.poc.") for key in parent.attributes)
    assert len(harness.calls) == 1
    assert harness.calls[0][0] is (mode == "enabled")
    if method == "patch" and harness.patch_timeout is not None:
        assert 0 < harness.calls[0][1] <= harness.patch_timeout
    else:
        assert harness.calls[0][1] is None
    if mode == "enabled":
        assert_item_attempts(harness, recording, parent, status, operation)
    else:
        assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("method,status", [("upsert", 201), ("upsert", 200), ("replacement", 200), ("patch", 200)])
@pytest.mark.parametrize("enabled", [False, True])
def test_body_write_empty_response_keeps_headers_and_completion(
    item_runtime, request, recording, method, status, enabled
):  # pylint: disable=unused-argument
    harness = request.getfixturevalue(method)
    harness.response_status = status
    harness.omit_body = True
    hook = Mock()
    result = getattr(harness, method)(no_response=True, response_hook=hook, tracing_options={"enabled": enabled})
    assert result == {}
    hook.assert_called_once()
    assert hook.call_args.args[1] == {}
    assert result.get_response_headers()["x-ms-cosmos-sdk-diagnostics"] == "diagnostic-text"
    assert harness.calls[0][0] is enabled
    assert bool(attempt_spans(recording)) is enabled
    assert telemetry._OPERATION.get() is None


def test_upsert_invalid_body_finishes_without_binding_execution(upsert, recording):
    seen = []
    upsert.container._item_context = replace(
        upsert.container._item_context, telemetry_handlers=(telemetry.CompletionHandler(seen.append),)
    )
    with pytest.raises(ValueError):
        upsert.invoke(upsert.container.upsert_item, {"id": "bad/id", "customerId": "customer-17"})
    assert not upsert.calls
    assert len(seen) == 1 and seen[0].outcome == "error"
    assert seen[0].diagnostics is None
    assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("mapping", [False, True])
def test_replace_telemetry_preserves_target_and_body(replacement, mapping):
    target = {"id": "order-17", "_self": "dbs/sales/colls/orders/docs/order-17/"} if mapping else "order-17"
    body = dict(ORDER, id="different-body-id")
    original_target, original_body = deepcopy(target), deepcopy(body)
    assert replacement.replacement(item=target, body=body) == body
    prepared = replacement.prepared_requests[0]
    assert prepared.op == "replace_item"
    assert prepared.item_id == "order-17"
    assert prepared.item_self_link == (target["_self"] if mapping else None)
    assert json.loads(prepared.body_bytes)["id"] == "different-body-id"
    assert target == original_target and body == original_body
    assert replacement.calls[0][0] is True


@pytest.mark.parametrize("defect", ["body-id", "target-link", "target-id"])
def test_replace_invalid_input_completes_before_binding(replacement, defect):
    seen = []
    replacement.container._item_context = replace(
        replacement.container._item_context, telemetry_handlers=(telemetry.CompletionHandler(seen.append),)
    )
    kwargs = {
        "body-id": {"body": dict(ORDER, id="bad/id")},
        "target-link": {"item": {"id": ORDER["id"], "_self": None}},
        "target-id": {"item": {"_self": "dbs/sales/colls/orders/docs/order-17/"}},
    }[defect]
    with pytest.raises((ValueError, TypeError, KeyError)):
        replacement.replacement(**kwargs)
    assert not replacement.calls
    assert len(seen) == 1 and seen[0].outcome == "error"
    assert seen[0].diagnostics is None
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("stage", ["within-budget", "acquisition-expired", "binding-timeout", "response-expired"])
@pytest.mark.parametrize("method", ["replacement", "patch"])
def test_point_write_telemetry_preserves_deadline_and_hook_boundary(
    item_runtime, request, recording, monkeypatch, stage, method
):  # pylint: disable=unused-argument
    harness = request.getfixturevalue(method)
    clock = SimpleNamespace(now=100.0)
    clock.monotonic = lambda: clock.now
    monkeypatch.setattr(_item_prep, "time", clock)
    monkeypatch.setattr(_operation_deadline, "time", clock)

    def initialize():
        clock.now += 6 if stage == "acquisition-expired" else 2
        return "test-driver"

    initializer = AsyncMock if isinstance(harness.backend, binding_adapter.AsyncBindingAdapter) else Mock
    monkeypatch.setattr(harness.backend, "_ensure_driver_handle", initializer(side_effect=initialize))
    if stage == "binding-timeout":
        harness.error = TimeoutError("binding deadline")
    elif stage == "response-expired":

        def expire(result):
            clock.now = 106
            return result

        harness.transform = expire
    hook = Mock()
    seen = []
    harness.container._item_context = replace(
        harness.container._item_context, telemetry_handlers=(telemetry.CompletionHandler(seen.append),)
    )
    if stage == "within-budget":
        assert getattr(harness, method)(timeout=5, response_hook=hook) == ORDER
        hook.assert_called_once()
    else:
        with pytest.raises(CosmosClientTimeoutError):
            getattr(harness, method)(timeout=5, response_hook=hook)
        hook.assert_not_called()
    assert len(seen) == 1 and seen[0].outcome == ("success" if stage == "within-budget" else "error")
    if stage == "acquisition-expired":
        assert not harness.calls
    else:
        assert len(harness.calls) == 1 and harness.calls[0][1] == 3
    assert bool(attempt_spans(recording)) is (stage in ("within-budget", "response-expired"))
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("mapping", [False, True])
def test_patch_telemetry_preserves_target_guard_filter_and_snapshot(patch, monkeypatch, mapping):
    target = {"_self": "dbs/sales/colls/orders/docs/order-17/"} if mapping else ORDER["id"]
    operations = [{"op": "increment", "path": "/total", "value": 1}]
    options = {"filterPredicate": "FROM c WHERE c.total = 200"}
    original_target = deepcopy(target)

    def initialize():
        operations[0]["value"] = 999
        options["filterPredicate"] = "FROM c WHERE c.total = 999"
        return "test-driver"

    initializer = AsyncMock if isinstance(patch.backend, binding_adapter.AsyncBindingAdapter) else Mock
    monkeypatch.setattr(patch.backend, "_ensure_driver_handle", initializer(side_effect=initialize))
    assert patch.patch(item=target, operations=operations, request_options=options, if_match='"v1"') == ORDER
    prepared = patch.prepared_requests[0]
    assert prepared.item_id == (None if mapping else ORDER["id"])
    assert prepared.item_self_link == (target["_self"] if mapping else None)
    assert json.loads(prepared.body_bytes) == {
        "operations": [{"op": "incr", "path": "/total", "value": 1}],
        "condition": "FROM c WHERE c.total = 200",
    }
    assert wire_headers(prepared)["if-match"] == '"v1"'
    assert target == original_target
    assert patch.calls[0][0] is True


@pytest.mark.parametrize(
    "kwargs,error",
    [
        ({"operations": []}, ValueError),
        ({"operations": [1]}, TypeError),
        ({"item": {"id": "order-17"}}, KeyError),
        ({"item": {"_self": None}}, TypeError),
        ({"if_none_match": "*"}, NotImplementedError),
        ({"filter_predicate": 7}, TypeError),
    ],
)
def test_patch_invalid_input_completes_without_binding(patch, kwargs, error):
    seen = []
    patch.container._item_context = replace(
        patch.container._item_context, telemetry_handlers=(telemetry.CompletionHandler(seen.append),)
    )
    with pytest.raises(error):
        patch.patch(**kwargs)
    assert not patch.calls
    assert len(seen) == 1 and seen[0].outcome == "error"
    assert seen[0].diagnostics is None
    assert telemetry._OPERATION.get() is None


def test_patch_without_deadline_records_the_same_operation(patch, recording):
    patch.patch_timeout = None
    with trace.get_tracer("customer").start_as_current_span("change_order") as parent:
        assert patch.patch() == ORDER
    assert patch.calls[0][0] is True and patch.calls[0][1] is None
    assert_item_attempts(patch, recording, parent, 200, "patch_item")


@pytest.mark.parametrize("eager", [False, True])
def test_patch_deadline_authorizes_only_its_worker(create, monkeypatch, eager):
    states = []

    async def unowned():
        assert telemetry.get_operation(create.backend, "patch_item") is None
        return await _operation_deadline.run_with_deadline(lookup, time.monotonic() + 10)

    async def lookup():
        return telemetry.get_operation(create.backend, "patch_item")

    async def initialize():
        state = telemetry.get_operation(create.backend, "patch_item")
        assert state is not None
        assert state.task is not asyncio.current_task()
        assert telemetry.get_operation(object(), "patch_item") is None
        assert telemetry.get_operation(create.backend, "read_item") is None
        assert await asyncio.create_task(unowned()) is None
        assert await _operation_deadline.run_with_deadline(lookup, time.monotonic() + 10) is state
        assert telemetry.get_operation(create.backend, "patch_item") is state
        states.append(state)
        return "test-driver"

    monkeypatch.setattr(create.backend, "_ensure_driver_handle", initialize)
    create.response_status = 200

    async def run():
        loop = asyncio.get_running_loop()
        previous = loop.get_task_factory()
        if eager:
            factory = getattr(asyncio, "eager_task_factory", None)
            if factory is None:
                pytest.skip("Eager task factories require Python 3.12.")
            loop.set_task_factory(factory)
        try:
            assert (
                await create.container.patch_item(
                    ORDER["id"], ORDER["customerId"], [{"op": "set", "path": "/total", "value": 200}], timeout=10
                )
                == ORDER
            )
        finally:
            loop.set_task_factory(previous)

    asyncio.run(run())
    assert len(states) == 1 and states[0].closed
    assert not states[0].delegated_tasks
    assert create.calls[0][0] is True


@pytest.mark.parametrize("outcome", ["success", "error", "timeout", "cancelled"])
def test_deadline_worker_releases_authorization_before_public_completion(create, monkeypatch, outcome):
    # Exercise the actual wait/drain path without spending a full operation timeout.
    monkeypatch.setattr(_operation_deadline, "remaining_timeout", lambda _: 0.02 if outcome == "timeout" else 10)
    failure = TimeoutError("customer response hook")

    @telemetry.trace_operation_async(binding_operation="patch_item")
    async def public(owner):  # pylint: disable=unused-argument
        state = telemetry.get_operation(create.backend, "patch_item")
        stopped = []

        async def worker():
            assert telemetry.get_operation(create.backend, "patch_item") is state
            try:
                if outcome == "error":
                    raise failure
                if outcome == "cancelled":
                    asyncio.current_task().cancel()
                if outcome in ("timeout", "cancelled"):
                    await asyncio.Future()
                return ORDER
            finally:
                stopped.append(True)

        try:
            result = await _operation_deadline.run_with_deadline(worker, 1)
            assert outcome == "success" and result == ORDER
        except TimeoutError as error:
            assert outcome == "error" and error is failure
        except CosmosClientTimeoutError:
            assert outcome == "timeout"
        except asyncio.CancelledError:
            assert outcome == "cancelled"
        assert stopped == [True]
        assert not state.closed and not state.delegated_tasks
        assert telemetry.get_operation(create.backend, "patch_item") is state

    asyncio.run(public(create.container))
    assert telemetry._OPERATION.get() is None


def test_worker_authorization_is_single_use_and_does_not_restore_masked_state(create):
    @telemetry.trace_operation_async(binding_operation="patch_item")
    async def public(owner):  # pylint: disable=unused-argument
        state = telemetry.get_operation(create.backend, "patch_item")

        async def lookup():
            return telemetry.get_operation(create.backend, "patch_item")

        bound = telemetry.bind_operation_task(lookup)
        assert await asyncio.create_task(bound()) is state
        assert not state.delegated_tasks
        assert await asyncio.create_task(bound()) is None
        masked = telemetry.bind_operation_task(lookup)
        token = telemetry._OPERATION.set(None)
        try:
            assert await asyncio.create_task(masked()) is None
        finally:
            telemetry._OPERATION.reset(token)
        assert not state.delegated_tasks
        assert telemetry.get_operation(create.backend, "patch_item") is state

    asyncio.run(public(create.container))


@pytest.fixture(
    name="timeout_item", params=["create_item", "read_item", "upsert_item", "replace_item", "delete_item", "patch_item"]
)
def timeout_item_harness(request, item_runtime):
    item_runtime.operation = request.param
    item_runtime.response_status = 408
    item_runtime.driver_error_type = TimeoutError
    arguments = {
        "create_item": (deepcopy(ORDER),),
        "read_item": (ORDER["id"], ORDER["customerId"]),
        "upsert_item": (deepcopy(ORDER),),
        "replace_item": (ORDER["id"], deepcopy(ORDER)),
        "delete_item": (ORDER["id"], ORDER["customerId"]),
        "patch_item": (ORDER["id"], ORDER["customerId"], [{"op": "set", "path": "/total", "value": 200}]),
    }[request.param]
    item_runtime.call = lambda **kwargs: item_runtime.invoke(
        getattr(item_runtime.container, request.param), *arguments, **kwargs
    )
    return item_runtime


@pytest.mark.parametrize("budget", [False, True])
@pytest.mark.parametrize("mode", ["enabled", "disabled", "global-disabled", "sampled-out", "handler-only"])
def test_driver_returned_timeout_keeps_diagnostics_and_original_exception(timeout_item, recording, budget, mode):
    seen = []
    hook = Mock()
    timeout_item.container._item_context = replace(
        timeout_item.container._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(seen.append, collect_attempts=mode == "handler-only"),),
    )
    if mode in ("global-disabled", "handler-only"):
        settings.tracing_enabled = False
    elif mode == "sampled-out":
        recording.provider.sampler = ALWAYS_OFF
    kwargs = {"timeout": 10} if budget else {}
    if mode == "disabled":
        kwargs["tracing_options"] = {"enabled": False}
    has_deadline = budget and timeout_item.operation in ("create_item", "read_item", "replace_item", "patch_item")
    error_type = CosmosClientTimeoutError if has_deadline else TimeoutError
    with trace.get_tracer("customer").start_as_current_span("change_order") as parent:
        with pytest.raises(error_type) as caught:
            timeout_item.call(response_hook=hook, **kwargs)
        original = caught.value.__cause__ if has_deadline else caught.value
        assert original is timeout_item.driver_error
        if parent.is_recording():
            assert not any(key.startswith("cosmos.poc.") for key in parent.attributes)
    hook.assert_not_called()
    assert len(timeout_item.calls) == len(seen) == 1
    assert seen[0].operation == timeout_item.operation and seen[0].outcome == "error"
    collect = mode in ("enabled", "handler-only")
    assert timeout_item.calls[0][0] is collect
    assert (timeout_item.calls[0][1] is not None) is has_deadline
    assert (seen[0].diagnostics is not None) is collect
    if collect:
        assert seen[0].diagnostics.complete
        assert seen[0].diagnostics.request_count == timeout_item.payloads[0]["request_count"]
    if mode == "enabled":
        assert_item_attempts(timeout_item, recording, parent, 408, timeout_item.operation)
    else:
        assert not attempt_spans(recording)
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("enabled", [False, True])
def test_timeout_diagnostic_lookup_failure_never_replaces_timeout(timeout_item, recording, caplog, enabled):
    accesses = []

    class UnreadableTimeout(TimeoutError):
        @property
        def _cosmos_attempt_payload(self):
            accesses.append(True)
            raise RuntimeError("PRIVATE diagnostic lookup failed")

    original = UnreadableTimeout("driver deadline")
    timeout_item.error = original
    with caplog.at_level(logging.WARNING), pytest.raises(TimeoutError) as caught:
        timeout_item.call(tracing_options={"enabled": enabled})
    assert caught.value is original
    assert accesses == ([True] if enabled else [])
    assert len(timeout_item.calls) == 1
    assert not attempt_spans(recording)
    assert ("could not read error diagnostics" in caplog.text) is enabled
    assert "PRIVATE" not in caplog.text
