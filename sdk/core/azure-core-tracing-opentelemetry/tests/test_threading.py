# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from concurrent.futures import ThreadPoolExecutor, wait
import threading

from opentelemetry.trace import NonRecordingSpan

from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.core.tracing import SpanKind


def test_get_span_from_thread(tracer):

    result = []

    def get_span_from_thread(output):
        current_span = OpenTelemetrySpan.get_current_span()
        output.append(current_span)

    with tracer.start_as_current_span(name="TestSpan") as span:

        thread = threading.Thread(target=OpenTelemetrySpan.with_current_context(get_span_from_thread), args=(result,))
        thread.start()
        thread.join()

        assert span is result[0]


def test_nest_span_with_thread_pool_executor(tracer, exporter):
    def nest_spans():
        with OpenTelemetrySpan(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:
            with outer_span.span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
                assert isinstance(inner_span.span_instance, NonRecordingSpan)
                assert inner_span.get_current_span() == outer_span

    futures = []
    with tracer.start_as_current_span(name="TestSpan"):
        with ThreadPoolExecutor() as executor:
            for _ in range(3):
                futures.append(executor.submit(OpenTelemetrySpan.with_current_context(nest_spans)))
        wait(futures)

    # Each thread should produce 1 span, so we should have 3 spans plus the parent span.
    assert len(exporter.get_finished_spans()) == 4
