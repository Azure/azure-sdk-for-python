# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for the OpenTelemetry tracer and span classes."""
from concurrent.futures import ThreadPoolExecutor, wait
import threading
from unittest.mock import patch

from azure.core.tracing._tracer import TracerProvider, default_tracer_provider
from azure.core.tracing._models import SpanKind, Link, TracingOptions
from azure.core.tracing.opentelemetry_span import OpenTelemetrySpan
from azure.core.tracing.opentelemetry_tracer import OpenTelemetryTracer
from azure.core.tracing.common import with_current_context
from azure.core.exceptions import ClientAuthenticationError
from azure.core.settings import settings

from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.trace import (
    Tracer as OtelTracer,
    Span as OtelSpan,
    SpanKind as OtelSpanKind,
    NonRecordingSpan,
    format_span_id,
    format_trace_id,
)
import requests
import pytest


def test_tracer_provider(tracing_helper):
    """Test basic usage of a TracerProvider."""
    tracer_provider = TracerProvider(
        library_name="my-library",
        library_version="1.0.0",
        schema_url="https://test.schema",
        attributes={"namespace": "Sample.Namespace"},
    )

    tracer = tracer_provider.get_tracer()
    assert isinstance(tracer, OpenTelemetryTracer)
    assert isinstance(tracer._tracer, OtelTracer)

    with tracer.start_span("test_span") as span:
        assert isinstance(span, OpenTelemetrySpan)
        span.set_attribute("foo", "bar")

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 1
    assert finished_spans[0].name == "test_span"
    assert finished_spans[0].attributes["foo"] == "bar"
    assert finished_spans[0].instrumentation_scope.schema_url == "https://test.schema"
    assert finished_spans[0].instrumentation_scope.name == "my-library"
    assert finished_spans[0].instrumentation_scope.version == "1.0.0"
    assert finished_spans[0].instrumentation_scope.attributes.get("namespace") == "Sample.Namespace"


def test_default_tracer_provider():
    """Test that the default tracer manager returns an OpenTelemetryTracer."""
    tracer = default_tracer_provider.get_tracer()

    assert isinstance(tracer, OpenTelemetryTracer)
    assert isinstance(tracer._tracer, OtelTracer)


def test_start_span_with_links(tracing_helper):
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    trace_context_headers = {}
    with tracer.start_span(name="foo-span") as span:
        trace_context_headers = tracer.get_trace_context()

    link = Link(headers=trace_context_headers, attributes={"foo": "bar"})

    with tracer.start_span(name="bar-span", links=[link]) as span:
        pass

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 2
    assert finished_spans[0].name == "foo-span"
    assert finished_spans[1].name == "bar-span"
    assert finished_spans[1].links[0].context.trace_id == finished_spans[0].context.trace_id
    assert finished_spans[1].links[0].context.span_id == finished_spans[0].context.span_id
    assert finished_spans[1].links[0].attributes["foo"] == "bar"


def test_start_span_with_attributes(tracing_helper):
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    with tracer.start_span(name="foo-span", attributes={"foo": "bar", "biz": 123}) as span:
        pass

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 1
    assert finished_spans[0].attributes["foo"] == "bar"
    assert finished_spans[0].attributes["biz"] == 123


def test_error_type_attribute_builtin_error():
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    with pytest.raises(ValueError):
        with tracer.start_span("span") as span:
            raise ValueError("This is a test error")

    assert span.span_instance.attributes.get("error.type") == "ValueError"


def test_error_type_attribute_azure_error():
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    with pytest.raises(ClientAuthenticationError):
        with tracer.start_span("span") as span:
            raise ClientAuthenticationError("This is a test error")

    assert span.span_instance.attributes.get("error.type") == "azure.core.exceptions.ClientAuthenticationError"


def test_tracer_get_current_span():
    """Test that the tracer can get the current OpenTelemetry span instance."""
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    with tracer.start_span("test_span") as span:
        with tracer.start_span("test_span2", kind=SpanKind.CLIENT) as span2:
            current_span = tracer.get_current_span()
            assert current_span.span_instance == span2.span_instance

        current_span = tracer.get_current_span()
        assert current_span.span_instance == span.span_instance

    current_span = tracer.get_current_span()
    assert isinstance(current_span.span_instance, NonRecordingSpan)


def test_tracer_get_current_span_nested():
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    with tracer.start_span(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:
        with tracer.start_span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
            assert isinstance(inner_span.span_instance, NonRecordingSpan)
            # get_current_span should return the last non-suppressed parent span.
            assert tracer.get_current_span().span_instance == outer_span.span_instance
            # Calling from class instead of instance should yield the same result.
            assert tracer.get_current_span().span_instance == outer_span.span_instance

            with tracer.start_span(name="inner-span", kind=SpanKind.CLIENT) as client_span_2:
                with tracer.start_span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span_2:
                    assert isinstance(inner_span_2.span_instance, NonRecordingSpan)
                    # get_current_span should return the last non-suppressed parent span.
                    assert tracer.get_current_span().span_instance == client_span_2.span_instance
                assert tracer.get_current_span().span_instance == client_span_2.span_instance

            # After leaving scope of inner client span, get_current_span should return the outer span now.
            assert tracer.get_current_span().span_instance == outer_span.span_instance


def test_nested_span_suppression(tracing_helper):
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    with tracer.start_span(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:
        assert isinstance(outer_span.span_instance, OtelSpan)
        assert outer_span.span_instance.kind == OtelSpanKind.INTERNAL

        with tracer.start_span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
            assert isinstance(inner_span.span_instance, NonRecordingSpan)

        assert len(tracing_helper.exporter.get_finished_spans()) == 0
    finished_spans = tracing_helper.exporter.get_finished_spans()

    assert len(finished_spans) == 1
    assert finished_spans[0].name == "outer-span"


def test_nested_span_suppression_with_multiple_outer_spans(tracing_helper):
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    with tracer.start_span(name="outer-span-1", kind=SpanKind.INTERNAL) as outer_span_1:
        assert isinstance(outer_span_1.span_instance, OtelSpan)
        assert outer_span_1.span_instance.kind == OtelSpanKind.INTERNAL

        with tracer.start_span(name="inner-span-1", kind=SpanKind.INTERNAL) as inner_span_1:
            assert isinstance(inner_span_1.span_instance, NonRecordingSpan)

    assert len(tracing_helper.exporter.get_finished_spans()) == 1

    with tracer.start_span(name="outer-span-2", kind=SpanKind.INTERNAL) as outer_span_2:
        assert isinstance(outer_span_2.span_instance, OtelSpan)
        assert outer_span_2.span_instance.kind == OtelSpanKind.INTERNAL

        with tracer.start_span(name="inner-span-2", kind=SpanKind.INTERNAL) as inner_span_2:
            assert isinstance(inner_span_2.span_instance, NonRecordingSpan)

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 2

    assert finished_spans[0].name == "outer-span-1"
    assert finished_spans[1].name == "outer-span-2"


def test_nested_span_suppression_with_nested_client(tracing_helper):
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    with tracer.start_span(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:
        assert isinstance(outer_span.span_instance, OtelSpan)
        assert outer_span.span_instance.kind == OtelSpanKind.INTERNAL

        with tracer.start_span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
            assert isinstance(inner_span.span_instance, NonRecordingSpan)

            with tracer.start_span(name="client-span", kind=SpanKind.CLIENT) as client_span:
                assert isinstance(client_span.span_instance, OtelSpan)
                assert client_span.span_instance.kind == OtelSpanKind.CLIENT
                # Parent of this should be the unsuppressed outer span.
                assert client_span.span_instance.parent is outer_span.span_instance.context
            assert len(tracing_helper.exporter.get_finished_spans()) == 1

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 2
    assert finished_spans[0].name == "client-span"
    assert finished_spans[1].name == "outer-span"


def test_nested_span_suppression_with_attributes():
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    with tracer.start_span(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:

        with tracer.start_span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
            inner_span.set_attribute("foo", "bar")

            # Attribute added on suppressed span should not be added to the parent span.
            assert "foo" not in outer_span.span_instance.attributes

            with tracer.start_span(name="client-span", kind=SpanKind.CLIENT) as client_span:
                client_span.set_attribute("foo", "biz")
                assert isinstance(client_span.span_instance, OtelSpan)
                assert client_span.span_instance.kind == OtelSpanKind.CLIENT

                # Attribute added on span.
                assert "foo" in client_span.span_instance.attributes
                assert client_span.span_instance.attributes["foo"] == "biz"


def test_nested_span_suppression_deep_nested(tracing_helper):
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    with tracer.start_span(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:

        with tracer.start_span(name="inner-span-1", kind=SpanKind.INTERNAL):
            with tracer.start_span(name="inner-span-2", kind=SpanKind.INTERNAL):
                with tracer.start_span(name="producer-span", kind=SpanKind.PRODUCER) as producer_span:
                    assert producer_span.span_instance.parent is outer_span.span_instance.context
                    with tracer.start_span(name="inner-span-3", kind=SpanKind.INTERNAL):
                        with tracer.start_span(name="client-span", kind=SpanKind.CLIENT) as client_span:
                            assert client_span.span_instance.parent is producer_span.span_instance.context

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 3
    spans_names_list = [span.name for span in finished_spans]
    assert spans_names_list == ["client-span", "producer-span", "outer-span"]


def test_span_unsuppressed_unentered_context():
    # Creating an INTERNAL span without entering the context should not suppress
    # a subsequent INTERNAL span.

    tracer = default_tracer_provider.get_tracer()
    assert tracer

    span1 = tracer.start_span(name="span1", kind=SpanKind.INTERNAL)
    with tracer.start_span(name="span2", kind=SpanKind.INTERNAL) as span2:
        # This span is not nested in span1, so should not be suppressed.
        assert not isinstance(span2.span_instance, NonRecordingSpan)
        assert isinstance(span2.span_instance, OtelSpan)
        span2.add_event
    span1.end()


def test_suppress_http_auto_instrumentationtracing_helper(tracing_helper):
    # Enable auto-instrumentation for requests.
    requests_instrumentor = RequestsInstrumentor()
    requests_instrumentor.instrument()

    tracer = default_tracer_provider.get_tracer()
    assert tracer

    with patch("requests.adapters.HTTPAdapter.send") as mock_request:
        response = requests.Response()
        response.status_code = 200
        mock_request.return_value = response
        with tracer.start_span(name="outer-span", kind=SpanKind.INTERNAL):
            with tracer.start_span(name="client-span", kind=SpanKind.CLIENT):
                # With CLIENT spans and automatic HTTP instrumentation is suppressed.
                requests.get("https://www.foo.bar/first")
            assert len(tracing_helper.exporter.get_finished_spans()) == 1
            # The following requests should still be auto-instrumented since it's not in the scope
            # of a CLIENT span.
            requests.post("https://www.foo.bar/second")
            requests.get("https://www.foo.bar/third")
            assert len(tracing_helper.exporter.get_finished_spans()) == 3
        assert len(tracing_helper.exporter.get_finished_spans()) == 4

    requests_instrumentor.uninstrument()


def test_end_span(tracing_helper):
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    span = tracer.start_span(name="foo-span", kind=SpanKind.INTERNAL)
    assert span.span_instance.is_recording()
    assert span.span_instance.start_time is not None
    assert span.span_instance.end_time is None

    span.end()
    assert not span.span_instance.is_recording()
    assert span.span_instance.end_time is not None

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 1
    assert finished_spans[0].name == "foo-span"


def test_get_trace_context():
    """Test that the tracer can get the trace context and it contains the traceparent header."""
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    assert not tracer.get_trace_context()

    with tracer.start_span(name="foo-span") as span:
        trace_context = tracer.get_trace_context()
        span_context = span.span_instance.get_span_context()
        assert "traceparent" in trace_context
        assert trace_context["traceparent"].startswith("00-")

        assert trace_context["traceparent"].split("-")[1] == format_trace_id(span_context.trace_id)
        assert trace_context["traceparent"].split("-")[2] == format_span_id(span_context.span_id)


def test_with_current_context_util_function(tracing_helper):

    settings.tracing_enabled = True
    result = []
    tracer = default_tracer_provider.get_tracer()
    assert tracer

    def get_span_from_thread(output):
        current_span = tracer.get_current_span()
        output.append(current_span)

    with tracing_helper.tracer.start_as_current_span(name="TestSpan") as span:

        thread = threading.Thread(target=with_current_context(get_span_from_thread), args=(result,))
        thread.start()
        thread.join()

        assert span is result[0].span_instance


def test_nest_span_with_thread_pool_executor(tracing_helper):
    custom_tracer_provider = TracerProvider(
        library_name="my-library",
        library_version="1.0.0",
        schema_url="https://test.schema",
        attributes={"namespace": "Sample.Namespace"},
    )
    tracer = custom_tracer_provider.get_tracer()
    assert tracer

    def nest_spans():
        with tracer.start_span(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:
            with tracer.start_span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
                assert isinstance(inner_span.span_instance, NonRecordingSpan)
                assert tracer.get_current_span() == outer_span

    futures = []
    with ThreadPoolExecutor() as executor:
        for _ in range(3):
            futures.append(executor.submit(tracer.with_current_context(nest_spans)))
    wait(futures)

    # Each thread should produce 1 span, so we should have 3 spans plus the parent span.
    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 3
    for span in finished_spans:
        assert span.name == "outer-span"
        assert span.instrumentation_scope.schema_url == "https://test.schema"
        assert span.instrumentation_scope.name == "my-library"
        assert span.instrumentation_scope.version == "1.0.0"
        assert span.instrumentation_scope.attributes.get("namespace") == "Sample.Namespace"
