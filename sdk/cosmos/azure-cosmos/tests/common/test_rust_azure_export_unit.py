# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline checks for the opt-in Azure proof and its export boundary."""

import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExportResult
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_PATH = Path(__file__).parents[2] / "samples" / "tracing_rust_attempts_async.py"
_SPEC = importlib.util.spec_from_file_location("rust_azure_proof", _PATH)
proof = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(proof)


@pytest.fixture(name="spans", params=["ContainerProxy.create_item", "ContainerProxy.read_item"])
def recorded_spans(request):
    provider = TracerProvider(resource=Resource({"host.name": "PRIVATE-HOST", "service.name": "PRIVATE-SERVICE"}))
    local = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(local))
    tracer = provider.get_tracer("PRIVATE-SCOPE")
    with tracer.start_as_current_span("setup"):
        pass
    with tracer.start_as_current_span("checkout") as checkout:
        with tracer.start_as_current_span(request.param) as operation:
            operation.set_attribute("db.statement", "PRIVATE-QUERY")
            operation.set_attribute("url.full", "https://private.invalid/secret")
            operation.set_status(trace.Status(trace.StatusCode.ERROR, "PRIVATE-ERROR"))
            operation.record_exception(ValueError("PRIVATE-BODY"))
            with tracer.start_as_current_span("cosmosdb.request") as attempt:
                attempt.set_attribute("cosmos.poc.driver_status_code", 409)
                attempt.set_attribute("cosmos.poc.execution_context", "initial")
        with tracer.start_as_current_span("PRIVATE-UNEXPECTED-SPAN"):
            pass
    with tracer.start_as_current_span("cleanup"):
        pass
    yield local.get_finished_spans(), checkout.get_span_context().trace_id
    provider.shutdown()


def test_export_boundary_preserves_identity_but_removes_sensitive_fields(spans):
    originals, trace_id = spans
    delegate = Mock()
    delegate.export.return_value = SpanExportResult.SUCCESS
    exporter = proof.MeasuredTraceExporter(delegate)
    exporter.trace_id = trace_id
    assert exporter.export(originals) == SpanExportResult.SUCCESS
    selected = delegate.export.call_args.args[0]
    assert {span.name for span in selected} == {s.name for s in originals if s.name in proof._PROOF_NAMES}
    assert len(selected) == 3
    for span in selected:
        original = next(s for s in originals if s.context.span_id == span.context.span_id)
        assert span.context == original.context
        assert span.parent == original.parent
        assert (span.start_time, span.end_time, span.kind) == (original.start_time, original.end_time, original.kind)
        assert span.status.status_code == original.status.status_code
        assert span.status.description is None
        assert not span.events and not span.links
        assert span.instrumentation_scope is None
        assert dict(span.resource.attributes) == {
            "service.name": "cosmos-rust-telemetry-proof",
            "service.instance.id": "synthetic-proof",
        }
        assert set(span.attributes) <= proof._PROOF_ATTRIBUTES
        assert "PRIVATE" not in span.to_json()
    operation = next(s for s in originals if s.name.startswith("ContainerProxy."))
    assert operation.events and operation.attributes["db.statement"] == "PRIVATE-QUERY"
    exporter.verify(3)
    exporter.shutdown()
    delegate.shutdown.assert_called_once()


def test_unselected_trace_never_reaches_azure(spans):
    delegate = Mock()
    exporter = proof.MeasuredTraceExporter(delegate)
    assert exporter.export(spans[0]) == SpanExportResult.SUCCESS
    delegate.export.assert_not_called()
    with pytest.raises(RuntimeError, match="0/3"):
        exporter.verify(3)


@pytest.mark.parametrize("raises", [False, True])
def test_export_failure_cannot_be_mistaken_for_success(spans, caplog, raises):
    delegate = Mock()
    if raises:
        delegate.export.side_effect = ValueError("PRIVATE-CONNECTION-STRING")
    else:
        delegate.export.return_value = SpanExportResult.FAILURE
    exporter = proof.MeasuredTraceExporter(delegate)
    exporter.trace_id = spans[1]
    assert exporter.export(spans[0]) == SpanExportResult.FAILURE
    with pytest.raises(RuntimeError, match="Azure export incomplete"):
        exporter.verify(3)
    assert "Azure trace export failed" in caplog.text
    assert "PRIVATE" not in caplog.text


def test_local_default_does_not_require_azure_configuration(monkeypatch):
    monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)
    provider, local, azure = proof.configure_recording()
    try:
        assert azure is None
        with provider.get_tracer("local").start_as_current_span("checkout"):
            pass
        assert provider.force_flush()
        assert len(local.get_finished_spans()) == 1
    finally:
        provider.shutdown()


@pytest.mark.parametrize("value", [None, "", "   "])
def test_missing_azure_configuration_fails_before_database_work(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)
    else:
        monkeypatch.setenv("APPLICATIONINSIGHTS_CONNECTION_STRING", value)
    with pytest.raises(ValueError, match="requires APPLICATIONINSIGHTS_CONNECTION_STRING"):
        proof.configure_recording(True)


def test_invalid_azure_configuration_does_not_expose_value(monkeypatch):
    pytest.importorskip("azure.monitor.opentelemetry.exporter")
    monkeypatch.setenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "PRIVATE-INVALID-CONNECTION-STRING")
    for name in (
        "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL",
        "APPLICATIONINSIGHTS_SDKSTATS_DISABLED",
        "APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED",
        "APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED",
    ):
        monkeypatch.setenv(name, "true")
    with pytest.raises(ValueError, match="Could not initialize Azure export") as error:
        proof.configure_recording(True)
    assert "PRIVATE" not in str(error.value)
    assert error.value.__suppress_context__


def test_real_azure_conversion_and_batch_flush_without_network(monkeypatch, spans):
    azure = pytest.importorskip("azure.monitor.opentelemetry.exporter")
    from azure.monitor.opentelemetry.exporter.export._base import ExportResult
    from azure.monitor.opentelemetry.exporter import _utils

    envelopes = []
    monkeypatch.setattr(_utils.platform, "node", lambda: "PRIVATE-HOSTNAME")

    def transmit(_self, items):
        envelopes.extend(items)
        return ExportResult.SUCCESS

    monkeypatch.setenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "InstrumentationKey=00000000-0000-0000-0000-000000000001;IngestionEndpoint=https://example.invalid/",
    )
    for name in (
        "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL",
        "APPLICATIONINSIGHTS_SDKSTATS_DISABLED",
        "APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED",
        "APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED",
    ):
        monkeypatch.setenv(name, "true")
    monkeypatch.setattr(azure.AzureMonitorTraceExporter, "_transmit", transmit)
    provider, local, exporter = proof.configure_recording(True)
    try:
        assert isinstance(provider.sampler, azure.ApplicationInsightsSampler)
        assert exporter.delegate.storage is None
        exporter.trace_id = spans[1]
        assert exporter.export(spans[0]) == SpanExportResult.SUCCESS
        exporter.verify(3)
        assert len(envelopes) == 3
        serialized = str([item.as_dict() for item in envelopes])
        assert "PRIVATE" not in serialized
        assert all(item.tags["ai.cloud.roleInstance"] == "synthetic-proof" for item in envelopes)
        assert f"{spans[1]:032x}" in serialized
        with provider.get_tracer("batch").start_as_current_span("checkout") as checkout:
            exporter.trace_id = checkout.get_span_context().trace_id
        assert provider.force_flush()
        exporter.verify(4)
        assert len(envelopes) == 4
        assert len(local.get_finished_spans()) == 1
    finally:
        provider.shutdown()
