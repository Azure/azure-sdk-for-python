# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Ensure the compiled proof rejects missing or mismatched evidence."""

import copy
import importlib.util
from pathlib import Path

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_PATH = Path(__file__).parents[2] / "samples" / "tracing_rust_failures_async.py"
_SPEC = importlib.util.spec_from_file_location("rust_failure_proof", _PATH)
proof = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(proof)


@pytest.fixture
def recorded():
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("proof-test")
    checkout = tracer.start_span("checkout", start_time=10)
    operation = tracer.start_span(
        "ContainerProxy.create_item",
        context=trace.set_span_in_context(checkout),
        start_time=20,
        attributes={"cosmos.poc.request_count": 1, "cosmos.poc.retained_request_count": 1},
    )
    attempt = tracer.start_span(
        "cosmosdb.request",
        context=trace.set_span_in_context(operation),
        start_time=30,
        kind=trace.SpanKind.CLIENT,
        attributes={"cosmos.poc.driver_status_code": 503, "cosmos.poc.execution_context": "initial"},
    )
    attempt.end(end_time=40)
    operation.set_status(trace.StatusCode.ERROR)
    operation.end(end_time=50)
    checkout.end(end_time=60)
    payload = {
        "schema_version": 1,
        "error": None,
        "request_count": 1,
        "retained_request_count": 1,
        "attempts": [
            {"start_ns": 30, "end_ns": 40, "driver_status_code": 503, "execution_context": "initial"},
        ],
    }
    yield exporter, checkout.get_span_context().trace_id, payload
    provider.shutdown()


def test_exact_compiled_fields_match_recorded_spans(recorded):
    exporter, trace_id, payload = recorded
    spans = proof.inspect_spans(exporter, trace_id, "enabled", "connection", payload)
    assert len(spans) == 3
    assert spans[0]["start_ns"] == 30
    assert spans[0]["end_ns"] == 40


@pytest.mark.parametrize(
    "field,value",
    [
        ("start_ns", 31),
        ("end_ns", 41),
        ("end_ns", None),
        ("driver_status_code", 408),
        ("execution_context", "transport_retry"),
    ],
)
def test_changed_or_incomplete_compiled_record_fails_proof(recorded, field, value):
    exporter, trace_id, payload = recorded
    payload = copy.deepcopy(payload)
    payload["attempts"][0][field] = value
    with pytest.raises(AssertionError):
        proof.inspect_spans(exporter, trace_id, "enabled", "connection", payload)


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema_version", 2),
        ("error", "conversion failed"),
        ("request_count", 0),
        ("request_count", 2),
        ("retained_request_count", 2),
    ],
)
def test_bad_schema_or_counts_fail_proof(recorded, field, value):
    exporter, trace_id, payload = recorded
    payload = {**payload, field: value}
    with pytest.raises(AssertionError):
        proof.inspect_spans(exporter, trace_id, "enabled", "connection", payload)


@pytest.mark.parametrize(
    "mode,failure",
    [
        ("per-call-disabled", "connection"),
        ("global-disabled", "connection"),
        ("enabled", "binding-timeout"),
        ("enabled", "cancellation"),
    ],
)
def test_unexpected_attempts_fail_proof(recorded, mode, failure):
    exporter, trace_id, _ = recorded
    with pytest.raises(AssertionError):
        proof.inspect_spans(exporter, trace_id, mode, failure, None)


@pytest.mark.parametrize("host", ["example.com", "localhost.example.com", "127.0.0.1.example.com", ""])
def test_nonloopback_target_is_rejected(monkeypatch, host):
    monkeypatch.setenv("COSMOSDBCONNECTIONSTRING", f"AccountEndpoint=https://{host}:8081/;")
    with pytest.raises(ValueError, match="loopback"):
        proof.emulator_connection_string()
