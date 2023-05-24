# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""The tests for opentelemetry_span.py"""
from unittest import mock

from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.trace import NonRecordingSpan, SpanKind as OpenTelemetrySpanKind
import pytest
import requests


from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.core.tracing import SpanKind


class TestOpentelemetryWrapper:
    def test_span_passed_in(self, tracer):
        with tracer.start_as_current_span(name="parent") as parent:
            wrapped_span = OpenTelemetrySpan(parent)

            assert wrapped_span.span_instance.name == "parent"
            assert parent is trace.get_current_span()
            assert wrapped_span.span_instance is trace.get_current_span()

            assert parent is trace.get_current_span()

    def test_no_span_passed_in_with_no_environ(self, tracer):
        with tracer.start_as_current_span("Root") as parent:
            with OpenTelemetrySpan() as wrapped_span:

                assert wrapped_span.span_instance.name == "span"
                assert wrapped_span.span_instance is trace.get_current_span()

            assert parent is trace.get_current_span()

    def test_span(self, tracer):
        with tracer.start_as_current_span("Root") as parent:
            with OpenTelemetrySpan() as wrapped_span:
                assert wrapped_span.span_instance is trace.get_current_span()

                with wrapped_span.span() as child:
                    assert child.span_instance.name == "span"
                    assert child.span_instance is trace.get_current_span()
                    assert child.span_instance.parent is wrapped_span.span_instance.context

    def test_nested_span_suppression(self, tracer, exporter):
        with tracer.start_as_current_span("Root"):
            with OpenTelemetrySpan(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:
                assert isinstance(outer_span.span_instance, trace.Span)
                assert outer_span.span_instance.kind == OpenTelemetrySpanKind.INTERNAL

                with outer_span.span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
                    assert isinstance(inner_span.span_instance, NonRecordingSpan)

                assert len(exporter.get_finished_spans()) == 0
            assert len(exporter.get_finished_spans()) == 1

        assert len(exporter.get_finished_spans()) == 2
        spans_names_list = [span.name for span in exporter.get_finished_spans()]
        assert spans_names_list == ["outer-span", "Root"]

    def test_nested_span_suppression_with_multiple_outer_spans(self, tracer, exporter):
        with tracer.start_as_current_span("Root"):
            with OpenTelemetrySpan(name="outer-span-1", kind=SpanKind.INTERNAL) as outer_span_1:
                assert isinstance(outer_span_1.span_instance, trace.Span)
                assert outer_span_1.span_instance.kind == OpenTelemetrySpanKind.INTERNAL

                with OpenTelemetrySpan(name="inner-span-1", kind=SpanKind.INTERNAL) as inner_span_1:
                    assert isinstance(inner_span_1.span_instance, NonRecordingSpan)

            assert len(exporter.get_finished_spans()) == 1

            with OpenTelemetrySpan(name="outer-span-2", kind=SpanKind.INTERNAL) as outer_span_2:
                assert isinstance(outer_span_2.span_instance, trace.Span)
                assert outer_span_2.span_instance.kind == OpenTelemetrySpanKind.INTERNAL

                with OpenTelemetrySpan(name="inner-span-2", kind=SpanKind.INTERNAL) as inner_span_2:
                    assert isinstance(inner_span_2.span_instance, NonRecordingSpan)

            assert len(exporter.get_finished_spans()) == 2

        assert len(exporter.get_finished_spans()) == 3
        spans_names_list = [span.name for span in exporter.get_finished_spans()]
        assert spans_names_list == ["outer-span-1", "outer-span-2", "Root"]

    def test_nested_span_suppression_with_nested_client(self, tracer, exporter):
        with tracer.start_as_current_span("Root"):
            with OpenTelemetrySpan(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:
                assert isinstance(outer_span.span_instance, trace.Span)
                assert outer_span.span_instance.kind == OpenTelemetrySpanKind.INTERNAL

                with outer_span.span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
                    assert isinstance(inner_span.span_instance, NonRecordingSpan)

                    with inner_span.span(name="client-span", kind=SpanKind.CLIENT) as client_span:
                        assert isinstance(client_span.span_instance, trace.Span)
                        assert client_span.span_instance.kind == OpenTelemetrySpanKind.CLIENT
                        # Parent of this should be the unsuppressed outer span.
                        assert client_span.span_instance.parent is outer_span.span_instance.context
                    assert len(exporter.get_finished_spans()) == 1

        assert len(exporter.get_finished_spans()) == 3
        spans_names_list = [span.name for span in exporter.get_finished_spans()]
        assert spans_names_list == ["client-span", "outer-span", "Root"]

    def test_nested_span_suppression_with_attributes(self, tracer):
        with tracer.start_as_current_span("Root"):
            with OpenTelemetrySpan(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:

                with outer_span.span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
                    inner_span.add_attribute("foo", "bar")

                    # Attribute added on suppressed span should not be added to the parent span.
                    assert "foo" not in outer_span.span_instance.attributes

                    with inner_span.span(name="client-span", kind=SpanKind.CLIENT) as client_span:
                        client_span.add_attribute("foo", "biz")
                        assert isinstance(client_span.span_instance, trace.Span)
                        assert client_span.span_instance.kind == OpenTelemetrySpanKind.CLIENT

                        # Attribute added on span.
                        assert "foo" in client_span.span_instance.attributes
                        assert client_span.span_instance.attributes["foo"] == "biz"

    def test_nested_span_suppression_deep_nested(self, tracer, exporter):
        with tracer.start_as_current_span("Root"):
            with OpenTelemetrySpan(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:

                with OpenTelemetrySpan(name="inner-span-1", kind=SpanKind.INTERNAL):
                    with OpenTelemetrySpan(name="inner-span-2", kind=SpanKind.INTERNAL):
                        with OpenTelemetrySpan(name="producer-span", kind=SpanKind.PRODUCER) as producer_span:
                            assert producer_span.span_instance.parent is outer_span.span_instance.context
                            with OpenTelemetrySpan(name="inner-span-3", kind=SpanKind.INTERNAL):
                                with OpenTelemetrySpan(name="client-span", kind=SpanKind.CLIENT) as client_span:
                                    assert client_span.span_instance.parent is producer_span.span_instance.context

        assert len(exporter.get_finished_spans()) == 4
        spans_names_list = [span.name for span in exporter.get_finished_spans()]
        assert spans_names_list == ["client-span", "producer-span", "outer-span", "Root"]

    def test_nested_get_current_span(self, tracer):
        with tracer.start_as_current_span("Root"):
            with OpenTelemetrySpan(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:
                with outer_span.span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
                    assert isinstance(inner_span.span_instance, NonRecordingSpan)
                    # get_current_span should return the last non-suppressed parent span.
                    assert inner_span.get_current_span() == outer_span.span_instance
                    # Calling from class instead of instance should yield the same result.
                    assert OpenTelemetrySpan.get_current_span() == outer_span.span_instance

                    with inner_span.span(name="inner-span", kind=SpanKind.CLIENT) as client_span_2:
                        with outer_span.span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span_2:
                            assert isinstance(inner_span_2.span_instance, NonRecordingSpan)
                            # get_current_span should return the last non-suppressed parent span.
                            assert inner_span_2.get_current_span() == client_span_2.span_instance
                        assert client_span_2.get_current_span() == client_span_2.span_instance

                    # After leaving scope of inner client span, get_current_span should return the outer span now.
                    assert inner_span.get_current_span() == outer_span.span_instance

    def test_span_unsuppressed_unentered_context(self):
        # Creating an INTERNAL span without entering the context should not suppress
        # a subsequent INTERNAL span.
        span1 = OpenTelemetrySpan(name="span1", kind=SpanKind.INTERNAL)
        with OpenTelemetrySpan(name="span2", kind=SpanKind.INTERNAL) as span2:
            # This span is not nested in span1, so should not be suppressed.
            assert not isinstance(span2.span_instance, NonRecordingSpan)
            assert isinstance(span2.span_instance, trace.Span)
        span1.finish()

    def test_suppress_http_auto_instrumentation(self, exporter):
        # Enable auto-instrumentation for requests.
        RequestsInstrumentor().instrument()
        from requests import Response

        with mock.patch("requests.adapters.HTTPAdapter.send") as mock_request:
            response = Response()
            response.status_code = 200
            mock_request.return_value = response
            with OpenTelemetrySpan(name="outer-span", kind=SpanKind.INTERNAL):
                with OpenTelemetrySpan(name="client-span", kind=SpanKind.CLIENT):
                    # With CLIENT spans and automatic HTTP instrumentation is suppressed.
                    requests.get("https://www.foo.bar/first")
                assert len(exporter.get_finished_spans()) == 1
                # The following requests should still be auto-instrumented since it's not in the scope
                # of a CLIENT span.
                requests.post("https://www.foo.bar/second")
                requests.get("https://www.foo.bar/third")
                assert len(exporter.get_finished_spans()) == 3
            assert len(exporter.get_finished_spans()) == 4

    def test_start_finish(self, tracer):
        with tracer.start_as_current_span("Root") as parent:
            wrapped_class = OpenTelemetrySpan()
            assert wrapped_class.span_instance.start_time is not None
            assert wrapped_class.span_instance.end_time is None
            wrapped_class.start()
            assert wrapped_class.span_instance.start_time is not None
            assert wrapped_class.span_instance.end_time is None
            wrapped_class.finish()
            assert wrapped_class.span_instance.start_time is not None
            assert wrapped_class.span_instance.end_time is not None

    def test_change_context(self, tracer):
        with tracer.start_as_current_span("Root") as parent:
            with OpenTelemetrySpan() as wrapped_class:
                with OpenTelemetrySpan.change_context(parent):
                    assert trace.get_current_span() is parent

    def test_to_header(self, tracer):
        with tracer.start_as_current_span("Root") as parent:
            wrapped_class = OpenTelemetrySpan()
            headers = wrapped_class.to_header()
            assert "traceparent" in headers
            assert headers["traceparent"].startswith("00-")

            traceparent = wrapped_class.get_trace_parent()
            assert traceparent.startswith("00-")

            assert traceparent == headers["traceparent"]

    def test_links(self, tracer):
        with tracer.start_as_current_span("Root") as parent:
            og_header = {"traceparent": "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-01"}
            with OpenTelemetrySpan() as wrapped_class:
                OpenTelemetrySpan.link_from_headers(og_header)

                assert len(wrapped_class.span_instance.links) == 1
                link = wrapped_class.span_instance.links[0]

                assert link.context.trace_id == int("2578531519ed94423ceae67588eff2c9", 16)
                assert link.context.span_id == int("231ebdc614cb9ddd", 16)

            with OpenTelemetrySpan() as wrapped_class:
                OpenTelemetrySpan.link("00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-01")

                assert len(wrapped_class.span_instance.links) == 1
                link = wrapped_class.span_instance.links[0]

                assert link.context.trace_id == int("2578531519ed94423ceae67588eff2c9", 16)
                assert link.context.span_id == int("231ebdc614cb9ddd", 16)

    def test_links_with_attribute(self, tracer):
        with tracer.start_as_current_span("Root") as parent:
            attributes = {"attribute1": 1, "attribute2": 2}
            og_header = {"traceparent": "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-02"}
            with OpenTelemetrySpan() as wrapped_class:
                OpenTelemetrySpan.link_from_headers(og_header, attributes)

                assert len(wrapped_class.span_instance.links) == 1
                link = wrapped_class.span_instance.links[0]

                assert link.context.trace_id == int("2578531519ed94423ceae67588eff2c9", 16)
                assert link.context.span_id == int("231ebdc614cb9ddd", 16)
                assert "attribute1" in link.attributes
                assert "attribute2" in link.attributes
                assert link.attributes == attributes

            with OpenTelemetrySpan() as wrapped_class:
                OpenTelemetrySpan.link("00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-02", attributes)

                assert len(wrapped_class.span_instance.links) == 1
                link = wrapped_class.span_instance.links[0]

                assert link.context.trace_id == int("2578531519ed94423ceae67588eff2c9", 16)
                assert link.context.span_id == int("231ebdc614cb9ddd", 16)
                assert "attribute1" in link.attributes
                assert "attribute2" in link.attributes
                assert link.attributes == attributes

    def test_add_attribute(self, tracer):
        with tracer.start_as_current_span("Root") as parent:
            wrapped_class = OpenTelemetrySpan(span=parent)
            wrapped_class.add_attribute("test", "test2")
            assert wrapped_class.span_instance.attributes["test"] == "test2"
            assert parent.attributes["test"] == "test2"

    def test_set_http_attributes(self, tracer):
        with tracer.start_as_current_span("Root", kind=OpenTelemetrySpanKind.CLIENT) as parent:
            wrapped_class = OpenTelemetrySpan(span=parent)
            request = mock.Mock()
            setattr(request, "method", "GET")
            setattr(request, "url", "https://foo.bar/path")
            response = mock.Mock()
            setattr(request, "headers", {})
            setattr(response, "status_code", 200)
            wrapped_class.set_http_attributes(request)
            assert wrapped_class.span_instance.kind == OpenTelemetrySpanKind.CLIENT
            assert wrapped_class.span_instance.attributes.get("http.method") == request.method
            assert wrapped_class.span_instance.attributes.get("component") == "http"
            assert wrapped_class.span_instance.attributes.get("http.url") == request.url
            assert wrapped_class.span_instance.attributes.get("http.status_code") == 504
            assert wrapped_class.span_instance.attributes.get("user_agent.original") is None

            request.headers["User-Agent"] = "some user agent"
            request.url = "http://foo.bar:8080/path"
            wrapped_class.set_http_attributes(request, response)
            assert wrapped_class.span_instance.attributes.get("http.status_code") == response.status_code
            assert wrapped_class.span_instance.attributes.get("user_agent.original") == request.headers.get(
                "User-Agent"
            )

            if wrapped_class.span_instance.attributes.get("net.peer.name"):
                assert wrapped_class.span_instance.attributes.get("net.peer.name") == "foo.bar"
                assert wrapped_class.span_instance.attributes.get("net.peer.port") == 8080

    def test_span_kind(self, tracer):
        with tracer.start_as_current_span("Root") as parent:
            wrapped_class = OpenTelemetrySpan(span=parent)

            wrapped_class.kind = SpanKind.UNSPECIFIED
            assert wrapped_class.span_instance.kind == OpenTelemetrySpanKind.INTERNAL
            assert wrapped_class.kind == SpanKind.INTERNAL

            wrapped_class.kind = SpanKind.SERVER
            assert wrapped_class.span_instance.kind == OpenTelemetrySpanKind.SERVER
            assert wrapped_class.kind == SpanKind.SERVER

            wrapped_class.kind = SpanKind.CLIENT
            assert wrapped_class.span_instance.kind == OpenTelemetrySpanKind.CLIENT
            assert wrapped_class.kind == SpanKind.CLIENT

            wrapped_class.kind = SpanKind.PRODUCER
            assert wrapped_class.span_instance.kind == OpenTelemetrySpanKind.PRODUCER
            assert wrapped_class.kind == SpanKind.PRODUCER

            wrapped_class.kind = SpanKind.CONSUMER
            assert wrapped_class.span_instance.kind == OpenTelemetrySpanKind.CONSUMER
            assert wrapped_class.kind == SpanKind.CONSUMER

            wrapped_class.kind = SpanKind.INTERNAL
            assert wrapped_class.span_instance.kind == OpenTelemetrySpanKind.INTERNAL
            assert wrapped_class.kind == SpanKind.INTERNAL

            with pytest.raises(ValueError):
                wrapped_class.kind = "somethingstuid"
