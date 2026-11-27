# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import tracemalloc
from itertools import product

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.sdk.trace.sampling import ALWAYS_ON

from azure.core.pipeline.transport import HttpResponse, HttpTransport
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter


class _NoOpResponse(HttpResponse):
    def __init__(self, request):
        super().__init__(request, None)
        self.status_code = 200
        self.headers = {"Content-Type": "application/json"}
        self.content_type = "application/json"

    def body(self):
        return b'{"errors":[]}'

    def json(self):
        return {"errors": []}

    def stream_download(self, pipeline, **kwargs):
        raise NotImplementedError("The benchmark transport does not support streaming responses.")


class _NoOpTransport(HttpTransport):
    def open(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def send(self, request, **kwargs):
        return _NoOpResponse(request)


_MODES = ("disabled", "disabled-with-attributes", "enabled")
_COUNTS = (1, 3, 25)
_BATCH_SIZE = 512


@pytest.fixture(autouse=True)
def _explicit_performance_run(request: pytest.FixtureRequest) -> None:
    if not any(str(arg).startswith("--benchmark-") for arg in request.config.invocation_params.args):
        pytest.skip("Performance tests require an explicit --benchmark-* option.")


@pytest.fixture(name="routing_batch", params=list(product(_MODES, _COUNTS)), ids=lambda value: f"{value[0]}-{value[1]}")
def _routing_batch(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> tuple[str, int, list[ReadableSpan]]:
    mode, count = request.param
    for name, value in {
        "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
        "APPLICATIONINSIGHTS_SDKSTATS_DISABLED": "true",
        "APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED": "true",
        "APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED": "true",
        "APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing" if mode == "enabled" else "",
    }.items():
        monkeypatch.setenv(name, value)
    # Each parametrized case must select its own otherwise process-wide cached opt-in.
    monkeypatch.setattr(
        "azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None, raising=False
    )
    provider = TracerProvider(
        resource=Resource({"service.name": "routing-benchmark", "service.instance.id": "benchmark"}),
        sampler=ALWAYS_ON,
        shutdown_on_exit=False,
    )
    spans: list[ReadableSpan] = []
    try:
        tracer = provider.get_tracer("routing-benchmark")
        for index in range(_BATCH_SIZE):
            attributes: dict[str, int | str] = {"benchmark.index": index}
            if mode != "disabled":
                endpoint = index % count
                attributes.update(
                    {
                        "microsoft.instrumentation_key": f"key-{endpoint}",
                        "microsoft.ingestion_endpoint": f"https://endpoint-{endpoint}.example/",
                    }
                )
            with tracer.start_as_current_span("routing-benchmark", attributes=attributes) as span:
                assert isinstance(span, ReadableSpan)
                spans.append(span)
    finally:
        provider.shutdown()
    return mode, count, spans


def _create_exporter() -> AzureMonitorTraceExporter:
    return AzureMonitorTraceExporter(
        connection_string="InstrumentationKey=00000000-0000-0000-0000-000000000001;"
        "IngestionEndpoint=https://host.example/",
        credential=None,
        disable_offline_storage=True,
        max_envelopes_per_second=0,
        transport=_NoOpTransport(),
        retry_total=0,
    )


def _close_exporter(exporter: AzureMonitorTraceExporter) -> None:
    try:
        exporter.shutdown()
    finally:
        exporter.client.close()


def _export_batch(exporter: AzureMonitorTraceExporter, spans: list[ReadableSpan]) -> None:
    if exporter.export(spans) != SpanExportResult.SUCCESS:
        raise RuntimeError("Routing benchmark export failed.")


def _cold_export(spans: list[ReadableSpan]) -> None:
    exporter = _create_exporter()
    try:
        _export_batch(exporter, spans)
    finally:
        _close_exporter(exporter)


@pytest.mark.benchmark(group="multi-endpoint-routing")
@pytest.mark.parametrize("cold_start", (False, True), ids=("warm", "cold"))
def test_export(
    benchmark: BenchmarkFixture, routing_batch: tuple[str, int, list[ReadableSpan]], cold_start: bool
) -> None:
    mode, count, spans = routing_batch
    benchmark.extra_info.update(
        {"routing_mode": mode, "endpoint_count": count, "batch_size": _BATCH_SIZE, "cold_start": cold_start}
    )
    if cold_start:
        benchmark(_cold_export, spans)
    else:
        exporter = _create_exporter()
        try:
            _export_batch(exporter, spans)
            benchmark(_export_batch, exporter, spans)
        finally:
            _close_exporter(exporter)


@pytest.mark.parametrize("cold_start", (False, True), ids=("warm", "cold"))
def test_peak_memory(routing_batch: tuple[str, int, list[ReadableSpan]], cold_start: bool) -> None:
    mode, count, spans = routing_batch
    exporter = None if cold_start else _create_exporter()
    try:
        if exporter is not None:
            _export_batch(exporter, spans)
        if tracemalloc.is_tracing():
            raise RuntimeError("Run memory measurements without an existing tracemalloc session.")
        tracemalloc.start()
        try:
            if exporter is None:
                _cold_export(spans)
            else:
                _export_batch(exporter, spans)
            current, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
    finally:
        if exporter is not None:
            _close_exporter(exporter)
    assert 0 <= current <= peak and peak > 0
    print(
        json.dumps(
            {
                "benchmark": "routing-memory",
                "routing_mode": mode,
                "endpoint_count": count,
                "batch_size": _BATCH_SIZE,
                "cold_start": cold_start,
                "retained_traced_bytes": current,
                "peak_traced_bytes": peak,
            }
        )
    )
