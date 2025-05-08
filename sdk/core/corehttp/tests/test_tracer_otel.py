# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for the OpenTelemetry tracer and span classes."""
from concurrent.futures import ThreadPoolExecutor, wait
import sys
import threading

from corehttp.instrumentation import get_tracer
from corehttp.instrumentation.tracing._models import SpanKind, Link
from corehttp.instrumentation.tracing.opentelemetry import OpenTelemetryTracer
from corehttp.instrumentation.tracing.utils import with_current_context
from corehttp.settings import settings

from opentelemetry.trace import (
    Tracer as OtelTracer,
    Span as OtelSpan,
    StatusCode as OtelStatusCode,
    NonRecordingSpan,
    format_span_id,
    format_trace_id,
)
import pytest


def test_tracer(tracing_helper):
    """Test basic usage of a Instrumentation."""
    tracer = get_tracer(
        library_name="my-library",
        library_version="1.0.0",
        schema_url="https://test.schema",
        attributes={"namespace": "Sample.Namespace"},
    )

    assert isinstance(tracer, OpenTelemetryTracer)
    assert isinstance(tracer._tracer, OtelTracer)

    with tracer.start_as_current_span("test_span") as span:
        assert isinstance(span, OtelSpan)
        span.set_attribute("foo", "bar")

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 1
    assert finished_spans[0].name == "test_span"
    assert finished_spans[0].attributes["foo"] == "bar"
    assert finished_spans[0].status.status_code == OtelStatusCode.UNSET
    assert finished_spans[0].instrumentation_scope.schema_url == "https://test.schema"
    assert finished_spans[0].instrumentation_scope.name == "my-library"
    assert finished_spans[0].instrumentation_scope.version == "1.0.0"
    assert finished_spans[0].instrumentation_scope.attributes.get("namespace") == "Sample.Namespace"


def test_default_instrumentation():
    """Test that the default tracer manager returns an OpenTelemetryTracer."""
    tracer = get_tracer()

    assert isinstance(tracer, OpenTelemetryTracer)
    assert isinstance(tracer._tracer, OtelTracer)


def test_start_span_with_links(tracing_helper):
    tracer = get_tracer()
    assert tracer

    trace_context_headers = {}
    with tracer.start_as_current_span(name="foo-span") as span:
        trace_context_headers = tracer.get_trace_context()

    link = Link(headers=trace_context_headers, attributes={"foo": "bar"})

    with tracer.start_as_current_span(name="bar-span", links=[link]) as span:
        pass

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 2
    assert finished_spans[0].name == "foo-span"
    assert finished_spans[1].name == "bar-span"
    assert finished_spans[1].links[0].context.trace_id == finished_spans[0].context.trace_id
    assert finished_spans[1].links[0].context.span_id == finished_spans[0].context.span_id
    assert finished_spans[1].links[0].attributes["foo"] == "bar"


def test_start_span_with_attributes(tracing_helper):
    tracer = get_tracer()
    assert tracer

    with tracer.start_as_current_span(name="foo-span", attributes={"foo": "bar", "biz": 123}) as span:
        pass

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 1
    assert finished_spans[0].attributes["foo"] == "bar"
    assert finished_spans[0].attributes["biz"] == 123


def test_start_as_current_span_no_exit(tracing_helper):
    tracer = get_tracer()
    assert tracer

    with tracer.start_as_current_span(name="foo-span", kind=SpanKind.INTERNAL, end_on_exit=False) as span:
        assert span.is_recording()
        assert tracer.get_current_span() == span

    assert span.is_recording()
    span.end()
    assert not span.is_recording()
    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 1


def test_tracer_get_current_span():
    """Test that the tracer can get the current OpenTelemetry span instance."""
    tracer = get_tracer()
    assert tracer

    with tracer.start_as_current_span("test_span") as span:
        with tracer.start_as_current_span("test_span2", kind=SpanKind.CLIENT) as span2:
            current_span = tracer.get_current_span()
            assert current_span == span2

        current_span = tracer.get_current_span()
        assert current_span == span

    current_span = tracer.get_current_span()
    assert isinstance(current_span, NonRecordingSpan)


def test_end_span(tracing_helper):
    tracer = get_tracer()
    assert tracer

    span = tracer.start_span(name="foo-span", kind=SpanKind.INTERNAL)
    assert span.is_recording()
    assert span.start_time is not None
    assert span.end_time is None

    span.end()
    assert not span.is_recording()
    assert span.end_time is not None

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 1
    assert finished_spans[0].name == "foo-span"


def test_use_span(tracing_helper):
    tracer = get_tracer()
    assert tracer

    assert isinstance(tracer.get_current_span(), NonRecordingSpan)
    with tracer.start_as_current_span(name="root", kind=SpanKind.INTERNAL) as root:
        span = tracer.start_span(name="foo-span", kind=SpanKind.INTERNAL)
        assert span.is_recording()
        assert tracer.get_current_span() == root

        with tracer.use_span(span):
            assert tracer.get_current_span() == span

        assert not span.is_recording()

        span2 = tracer.start_span(name="bar-span", kind=SpanKind.INTERNAL)
        assert span2.is_recording()
        assert tracer.get_current_span() == root
        with tracer.use_span(span2, end_on_exit=False):
            assert tracer.get_current_span() == span2
            assert span2.is_recording()

        assert span2.is_recording()
        span2.end()
        assert not span2.is_recording()
        assert tracer.get_current_span() == root

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 3


def test_get_trace_context():
    """Test that the tracer can get the trace context and it contains the traceparent header."""
    tracer = get_tracer()
    assert tracer

    assert not tracer.get_trace_context()

    with tracer.start_as_current_span(name="foo-span") as span:
        trace_context = tracer.get_trace_context()
        span_context = span.get_span_context()
        assert "traceparent" in trace_context
        assert trace_context["traceparent"].startswith("00-")

        assert trace_context["traceparent"].split("-")[1] == format_trace_id(span_context.trace_id)
        assert trace_context["traceparent"].split("-")[2] == format_span_id(span_context.span_id)


def test_with_current_context_util_function(tracing_helper):

    settings.tracing_enabled = True
    result = []
    tracer = get_tracer()
    assert tracer

    def get_span_from_thread(output):
        current_span = tracer.get_current_span()
        output.append(current_span)

    with tracing_helper.tracer.start_as_current_span(name="TestSpan") as span:

        thread = threading.Thread(target=with_current_context(get_span_from_thread), args=(result,))
        thread.start()
        thread.join()

        assert span is result[0]


def test_nest_span_with_thread_pool_executor(tracing_helper):
    tracer = get_tracer(
        library_name="my-library",
        library_version="1.0.0",
        schema_url="https://test.schema",
        attributes={"namespace": "Sample.Namespace"},
    )
    assert tracer

    def nest_spans():
        with tracer.start_as_current_span(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:
            with tracer.start_as_current_span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
                assert isinstance(inner_span, OtelSpan)
                assert tracer.get_current_span() == inner_span

    futures = []
    with ThreadPoolExecutor() as executor:
        for _ in range(3):
            futures.append(executor.submit(tracer.with_current_context(nest_spans)))
    wait(futures)

    # Each thread should produce 2 spans, so we should have 6 spans.
    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 6
    for span in finished_spans:
        assert "-span" in span.name
        assert span.instrumentation_scope.schema_url == "https://test.schema"
        assert span.instrumentation_scope.name == "my-library"
        assert span.instrumentation_scope.version == "1.0.0"
        assert span.instrumentation_scope.attributes.get("namespace") == "Sample.Namespace"


def test_set_span_status(tracing_helper):
    tracer = get_tracer()
    assert tracer

    with tracer.start_as_current_span(name="foo-span") as span:
        span.set_status(OtelStatusCode.OK)

    with tracer.start_as_current_span(name="bar-span") as span:
        span.set_status(OtelStatusCode.ERROR, "This is an error")

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 2
    assert finished_spans[0].status.status_code == OtelStatusCode.OK
    assert finished_spans[0].status.description is None

    assert finished_spans[1].status.status_code == OtelStatusCode.ERROR
    assert finished_spans[1].status.description == "This is an error"


def test_add_event(tracing_helper):
    tracer = get_tracer()
    assert tracer

    with tracer.start_as_current_span(name="foo-span") as span:
        span.add_event("test-event", attributes={"foo": "bar"})

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 1
    assert len(finished_spans[0].events) == 1
    assert finished_spans[0].events[0].name == "test-event"
    assert finished_spans[0].events[0].attributes["foo"] == "bar"


def test_span_exception(tracing_helper):
    tracer = get_tracer()
    assert tracer

    with pytest.raises(ValueError):
        with tracer.start_as_current_span(name="foo-span") as span:
            raise ValueError("This is an error")
    finished_spans = tracing_helper.exporter.get_finished_spans()

    assert len(finished_spans) == 1
    assert finished_spans[0].status.status_code == OtelStatusCode.ERROR


def test_span_exception_without_current_context(tracing_helper):
    tracer = get_tracer()
    assert tracer

    span = tracer.start_span(name="foo-span")
    assert span.is_recording()

    with pytest.raises(ValueError):
        with span:
            raise ValueError("This is an error")

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 1
    assert len(finished_spans[0].events) == 1
    assert finished_spans[0].events[0].name == "exception"
    assert finished_spans[0].events[0].attributes["exception.type"] == "ValueError"
    assert finished_spans[0].events[0].attributes["exception.message"] == "This is an error"
    assert finished_spans[0].status.status_code == OtelStatusCode.ERROR


def test_span_exception_exit(tracing_helper):

    tracer = get_tracer()
    assert tracer

    span = tracer.start_span(name="foo-span")
    assert span.is_recording()
    try:
        raise ValueError("This is an error")
    except ValueError as e:
        exc_info = sys.exc_info()
        span.__exit__(*exc_info)

    finished_spans = tracing_helper.exporter.get_finished_spans()

    assert len(finished_spans) == 1
    assert len(finished_spans[0].events) == 1
    assert finished_spans[0].events[0].name == "exception"
    assert finished_spans[0].events[0].attributes["exception.type"] == "ValueError"
    assert finished_spans[0].events[0].attributes["exception.message"] == "This is an error"
    assert finished_spans[0].status.status_code == OtelStatusCode.ERROR


def test_tracer_caching():
    """Test that get_tracer caches the OpenTelemetryTracer."""
    tracer1 = get_tracer()
    tracer2 = get_tracer()

    assert tracer1 is tracer2


def test_tracer_caching_different_args():
    """Test that get_tracer caches the OpenTelemetryTracer."""
    tracer1 = get_tracer(
        library_name="my-library",
        library_version="1.0.0",
        schema_url="https://test.schema",
        attributes={"namespace": "Sample.Namespace"},
    )
    tracer2 = get_tracer(
        library_name="my-library",
        library_version="1.0.0",
        schema_url="https://test.schema",
        attributes={"namespace": "Sample.Namespace"},
    )
    tracer3 = get_tracer(
        library_name="my-library-2",
        library_version="2.0.0",
        schema_url="https://test.schema",
        attributes={"namespace": "Sample.Namespace"},
    )

    assert tracer1 is tracer2
    assert tracer1 is not tracer3
