# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import threading

from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan


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
