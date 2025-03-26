# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""The tests for opentelemetry_span.py"""
from unittest import mock

from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.trace import (
    NonRecordingSpan,
    SpanKind as OpenTelemetrySpanKind,
    StatusCode as OpenTelemetryStatusCode,
)
import pytest
import requests


from azure.core.exceptions import ClientAuthenticationError
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.core.tracing import SpanKind, AbstractSpan
from azure.core import __version__ as core_version
from azure.core import PipelineClient
from azure.core.tracing.decorator import distributed_trace


@pytest.mark.skipif(int(core_version.split(".")[1]) < 30, reason="Test requires an azure-core with runtime-checkable")
def test_structural_subtyping():
    # assert issubclass(OpenTelemetrySpan, AbstractSpan)
    assert isinstance(OpenTelemetrySpan(), AbstractSpan)


def span_kind_to_otel_kind(kind: SpanKind) -> OpenTelemetrySpanKind:
    """Convert Azure SDK span kind to OpenTelemetry span kind."""
    if kind == SpanKind.INTERNAL:
        return OpenTelemetrySpanKind.INTERNAL
    elif kind == SpanKind.CLIENT:
        return OpenTelemetrySpanKind.CLIENT
    elif kind == SpanKind.SERVER:
        return OpenTelemetrySpanKind.SERVER
    elif kind == SpanKind.PRODUCER:
        return OpenTelemetrySpanKind.PRODUCER
    elif kind == SpanKind.CONSUMER:
        return OpenTelemetrySpanKind.CONSUMER
    else:
        raise ValueError(f"Unknown span kind: {kind}")


class TestOpentelemetryWrapper:
    def test_span_passed_in(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span(name="parent") as parent:
            wrapped_span = OpenTelemetrySpan(parent)

            assert wrapped_span.span_instance.name == "parent"
            assert parent is trace.get_current_span()
            assert wrapped_span.span_instance is trace.get_current_span()

            assert parent is trace.get_current_span()

    def test_no_span_passed_in_with_no_environ(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as parent:
            with OpenTelemetrySpan() as wrapped_span:

                assert wrapped_span.span_instance.name == "span"
                assert wrapped_span.span_instance is trace.get_current_span()

            assert parent is trace.get_current_span()

    def test_span(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as parent:
            with OpenTelemetrySpan() as wrapped_span:
                assert wrapped_span.span_instance is trace.get_current_span()

                with wrapped_span.span() as child:
                    assert child.span_instance.name == "span"
                    assert child.span_instance is trace.get_current_span()
                    assert child.span_instance.parent is wrapped_span.span_instance.context

    @pytest.mark.parametrize("outer_span_kind", [SpanKind.INTERNAL, SpanKind.CLIENT, SpanKind.PRODUCER])
    def test_nested_span_suppression(self, tracing_helper, outer_span_kind):
        with tracing_helper.tracer.start_as_current_span("Root"):
            with OpenTelemetrySpan(name="outer-span", kind=outer_span_kind) as outer_span:
                assert isinstance(outer_span.span_instance, trace.Span)
                assert outer_span.span_instance.kind == span_kind_to_otel_kind(outer_span_kind)

                with outer_span.span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
                    assert isinstance(inner_span.span_instance, NonRecordingSpan)

                assert len(tracing_helper.exporter.get_finished_spans()) == 0
            assert len(tracing_helper.exporter.get_finished_spans()) == 1

        assert len(tracing_helper.exporter.get_finished_spans()) == 2
        spans_names_list = [span.name for span in tracing_helper.exporter.get_finished_spans()]
        assert spans_names_list == ["outer-span", "Root"]

    @pytest.mark.parametrize("outer_span_kind", [SpanKind.SERVER, SpanKind.CONSUMER])
    def test_no_nested_span_suppression_under_server(self, tracing_helper, outer_span_kind):
        with OpenTelemetrySpan(name="outer-span", kind=outer_span_kind) as outer_span:
            assert outer_span.span_instance.kind == span_kind_to_otel_kind(outer_span_kind)

            with outer_span.span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
                assert isinstance(inner_span.span_instance, trace.Span)

            assert len(tracing_helper.exporter.get_finished_spans()) == 1
        assert len(tracing_helper.exporter.get_finished_spans()) == 2

    def test_nested_span_suppression_with_multiple_outer_spans(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as root:
            with OpenTelemetrySpan(name="outer-span-1", kind=SpanKind.INTERNAL) as outer_span_1:
                assert isinstance(outer_span_1.span_instance, trace.Span)
                assert outer_span_1.span_instance.kind == OpenTelemetrySpanKind.INTERNAL

                with OpenTelemetrySpan(name="inner-span-1", kind=SpanKind.INTERNAL) as inner_span_1:
                    assert isinstance(inner_span_1.span_instance, NonRecordingSpan)

            assert len(tracing_helper.exporter.get_finished_spans()) == 1
            assert trace.get_current_span() is root

            with OpenTelemetrySpan(name="outer-span-2", kind=SpanKind.INTERNAL) as outer_span_2:
                assert isinstance(outer_span_2.span_instance, trace.Span)
                assert outer_span_2.span_instance.kind == OpenTelemetrySpanKind.INTERNAL

                with OpenTelemetrySpan(name="inner-span-2", kind=SpanKind.INTERNAL) as inner_span_2:
                    assert isinstance(inner_span_2.span_instance, NonRecordingSpan)

            assert len(tracing_helper.exporter.get_finished_spans()) == 2

        assert len(tracing_helper.exporter.get_finished_spans()) == 3
        spans_names_list = [span.name for span in tracing_helper.exporter.get_finished_spans()]
        assert spans_names_list == ["outer-span-1", "outer-span-2", "Root"]

    def test_suppress_http_auto_instrumentation_policy(self, tracing_helper):
        from azure.core.rest import HttpRequest
        from azure.core.pipeline.transport import RequestsTransport
        from azure.core.pipeline.policies import DistributedTracingPolicy
        from azure.core.settings import settings

        settings.tracing_implementation = "opentelemetry"

        class FooClient:
            def __init__(self, endpoint: str):
                policies = [DistributedTracingPolicy()]
                self._client = PipelineClient(endpoint, policies=policies, transport=RequestsTransport())

            @distributed_trace
            def foo(self):
                request = HttpRequest("GET", "https://foo.bar")
                response = self._client.send_request(request)
                return response

        requests_instrumentor = RequestsInstrumentor()
        requests_instrumentor.instrument()

        from requests import Response

        with mock.patch("requests.adapters.HTTPAdapter.send") as mock_request:
            response = Response()
            response.status_code = 200
            response.raw = mock.MagicMock()
            mock_request.return_value = response

            client = FooClient("https://foo.bar")
            client.foo()

            finished_spans = tracing_helper.exporter.get_finished_spans()
            # One span for the method and one span for the HTTP request.
            assert len(finished_spans) == 2

        requests_instrumentor.uninstrument()
        settings.tracing_implementation = None

    def test_nested_span_suppression_with_nested_client(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root"):
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
                    assert len(tracing_helper.exporter.get_finished_spans()) == 1

        assert len(tracing_helper.exporter.get_finished_spans()) == 3
        spans_names_list = [span.name for span in tracing_helper.exporter.get_finished_spans()]
        assert spans_names_list == ["client-span", "outer-span", "Root"]

    def test_nested_span_suppression_with_attributes(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root"):
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

    def test_nested_span_suppression_deep_nested(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root"):
            with OpenTelemetrySpan(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:

                with OpenTelemetrySpan(name="inner-span-1", kind=SpanKind.INTERNAL):
                    with OpenTelemetrySpan(name="inner-span-2", kind=SpanKind.INTERNAL):
                        with OpenTelemetrySpan(name="producer-span", kind=SpanKind.PRODUCER) as producer_span:
                            assert producer_span.span_instance.parent is outer_span.span_instance.context
                            with OpenTelemetrySpan(name="inner-span-3", kind=SpanKind.INTERNAL):
                                with OpenTelemetrySpan(name="client-span", kind=SpanKind.CLIENT) as client_span:
                                    assert client_span.span_instance.parent is producer_span.span_instance.context

        assert len(tracing_helper.exporter.get_finished_spans()) == 4
        spans_names_list = [span.name for span in tracing_helper.exporter.get_finished_spans()]
        assert spans_names_list == ["client-span", "producer-span", "outer-span", "Root"]

    def test_nested_get_current_span(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as otel_span:
            with OpenTelemetrySpan(name="outer-span", kind=SpanKind.INTERNAL) as outer_span:
                with outer_span.span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span:
                    assert isinstance(inner_span.span_instance, NonRecordingSpan)
                    # get_current_span should return the last non-suppressed parent span.
                    assert inner_span.get_current_span() == outer_span.span_instance
                    # Calling from class instead of instance should yield the same result.
                    assert OpenTelemetrySpan.get_current_span() == outer_span.span_instance

                    with inner_span.span(name="inner-span", kind=SpanKind.PRODUCER) as producer_span:
                        with outer_span.span(name="inner-span", kind=SpanKind.INTERNAL) as inner_span_2:
                            assert isinstance(inner_span_2.span_instance, NonRecordingSpan)
                            # get_current_span should return the last non-suppressed parent span.
                            assert inner_span_2.get_current_span() == producer_span.span_instance
                        assert producer_span.get_current_span() == producer_span.span_instance

                    # After leaving scope of inner client span, get_current_span should return the outer span now.
                    assert inner_span.get_current_span() == outer_span.span_instance
                assert trace.get_current_span() == outer_span.span_instance
            assert trace.get_current_span() == otel_span

    def test_exit_closes_span(self, tracing_helper):
        with OpenTelemetrySpan(name="span", kind=SpanKind.INTERNAL):
            pass
        finished = tracing_helper.exporter.get_finished_spans()
        assert len(finished) == 1
        assert finished[0].status.status_code == OpenTelemetryStatusCode.UNSET
        assert False == trace.get_current_span().get_span_context().is_valid

    def test_span_unsuppressed_unentered_context(self):
        # Creating an INTERNAL span without entering the context should not suppress
        # a subsequent INTERNAL span.
        span1 = OpenTelemetrySpan(name="span1", kind=SpanKind.INTERNAL)
        with OpenTelemetrySpan(name="span2", kind=SpanKind.INTERNAL) as span2:
            # This span is not nested in span1, so should not be suppressed.
            assert not isinstance(span2.span_instance, NonRecordingSpan)
            assert isinstance(span2.span_instance, trace.Span)
        span1.finish()

    @pytest.mark.parametrize("outer_span_kind", [SpanKind.INTERNAL, SpanKind.CLIENT, SpanKind.PRODUCER])
    def test_suppress_http_auto_instrumentation(self, tracing_helper, outer_span_kind):
        # Enable auto-instrumentation for requests.
        RequestsInstrumentor().instrument()
        from requests import Response

        with mock.patch("requests.adapters.HTTPAdapter.send") as mock_request:
            response = Response()
            response.status_code = 200
            mock_request.return_value = response
            with OpenTelemetrySpan(name="outer-span", kind=outer_span_kind):
                with OpenTelemetrySpan(name="client-span", kind=SpanKind.INTERNAL):
                    # INTERNAL and non-Azure SDK HTTP spans are suppressed.
                    requests.get("https://www.foo.bar/first")
                assert len(tracing_helper.exporter.get_finished_spans()) == 0
            assert len(tracing_helper.exporter.get_finished_spans()) == 1
            # The following requests should still be auto-instrumented since it's not in the scope
            # of a CLIENT span.
            requests.post("https://www.foo.bar/second")
            requests.get("https://www.foo.bar/third")
            assert len(tracing_helper.exporter.get_finished_spans()) == 3

    @pytest.mark.parametrize("span_kind", [SpanKind.SERVER, SpanKind.CONSUMER])
    def test_dont_suppress_http_auto_instrumentation_under_server(self, tracing_helper, span_kind):
        # Enable auto-instrumentation for requests.
        RequestsInstrumentor().instrument()
        from requests import Response

        with mock.patch("requests.adapters.HTTPAdapter.send") as mock_request:
            response = Response()
            response.status_code = 200
            mock_request.return_value = response
            with OpenTelemetrySpan(name="span", kind=span_kind):
                requests.get("https://www.foo.bar/first")
                assert len(tracing_helper.exporter.get_finished_spans()) == 1

    def test_start_finish(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as parent:
            wrapped_class = OpenTelemetrySpan()
            assert wrapped_class.span_instance.start_time is not None
            assert wrapped_class.span_instance.end_time is None
            wrapped_class.start()
            assert wrapped_class.span_instance.start_time is not None
            assert wrapped_class.span_instance.end_time is None
            wrapped_class.finish()
            assert wrapped_class.span_instance.start_time is not None
            assert wrapped_class.span_instance.end_time is not None

    def test_change_context(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as parent:
            span1 = OpenTelemetrySpan(name="span1", kind=SpanKind.INTERNAL)
            with span1.change_context(span1):
                assert trace.get_current_span() is span1.span_instance
            assert trace.get_current_span() is parent
            span1.span_instance.set_attribute("key1", "value1")

            with OpenTelemetrySpan(name="span2", kind=SpanKind.CLIENT) as span2:
                assert trace.get_current_span() is span2.span_instance

                with span1.change_context(span1):
                    assert trace.get_current_span() is span1.span_instance
                span1.span_instance.set_attribute("key2", "value2")
                assert trace.get_current_span() is span2.span_instance

            assert trace.get_current_span() is parent
            assert len(tracing_helper.exporter.get_finished_spans()) == 1
            span1.finish()

            spans = tracing_helper.exporter.get_finished_spans()
            assert len(spans) == 2

            assert spans[1].attributes["key1"] == "value1"
            assert spans[1].attributes["key2"] == "value2"

    def test_change_context_nested(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as parent:
            with OpenTelemetrySpan(name="outer", kind=SpanKind.INTERNAL) as outer:
                with OpenTelemetrySpan.change_context(parent):
                    assert trace.get_current_span() is parent
                assert trace.get_current_span() == outer.span_instance
                with OpenTelemetrySpan.change_context(parent):
                    assert trace.get_current_span() is parent
                assert trace.get_current_span() is outer.span_instance

                inner = OpenTelemetrySpan(name="inner", kind=SpanKind.INTERNAL)
                with OpenTelemetrySpan.change_context(inner):
                    assert trace.get_current_span() is outer.span_instance

                    with OpenTelemetrySpan(name="client", kind=SpanKind.CLIENT) as client:
                        assert trace.get_current_span() is client.span_instance

                assert trace.get_current_span() is outer.span_instance

            assert trace.get_current_span() is parent

    def test_to_header(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as parent:
            wrapped_class = OpenTelemetrySpan()
            headers = wrapped_class.to_header()
            assert "traceparent" in headers
            assert headers["traceparent"].startswith("00-")

            traceparent = wrapped_class.get_trace_parent()
            assert traceparent.startswith("00-")

            assert traceparent == headers["traceparent"]

    def test_links(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as parent:
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

    def test_links_with_attribute(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as parent:
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

    def test_parent_context(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root"):
            parent_header = {"traceparent": "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-01"}
            span = OpenTelemetrySpan(name="test_span", context=parent_header)
            assert span.span_instance.context.trace_id == int("2578531519ed94423ceae67588eff2c9", 16)
            assert span.span_instance.parent.span_id == int("231ebdc614cb9ddd", 16)

    def test_empty_parent_context(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as root:
            span = OpenTelemetrySpan(name="test_span", context={})
            # Parent of span should be current span context if context is empty.
            assert span.span_instance.parent is root.context

            span = OpenTelemetrySpan(name="test_span2", context=None)
            # Parent of span should be current span context if context is None or not specified.
            assert span.span_instance.parent is root.context

            span = OpenTelemetrySpan(name="test_span3", context={"no_traceparent": "foo"})
            # Parent of span should be None if context is not empty but does not contain traceparent.
            assert span.span_instance.parent is None

        span = OpenTelemetrySpan(name="test_span3")
        # If no outer span and no context, parent should be None.
        assert span.span_instance.parent is None

    def test_add_attribute(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as parent:
            wrapped_class = OpenTelemetrySpan(span=parent)
            wrapped_class.add_attribute("test", "test2")
            assert wrapped_class.span_instance.attributes["test"] == "test2"
            assert parent.attributes["test"] == "test2"

    def test_set_http_attributes_v1_19_0(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root", kind=OpenTelemetrySpanKind.CLIENT) as parent:
            wrapped_class = OpenTelemetrySpan(span=parent, schema_version="1.19.0")
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

    def test_set_http_attributes_v1_23_1(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root", kind=OpenTelemetrySpanKind.CLIENT) as parent:
            wrapped_class = OpenTelemetrySpan(span=parent, schema_version="1.23.1")
            request = mock.Mock()
            setattr(request, "method", "GET")
            setattr(request, "url", "https://foo.bar/path")
            response = mock.Mock()
            setattr(request, "headers", {})
            setattr(response, "status_code", 200)
            wrapped_class.set_http_attributes(request)
            assert wrapped_class.span_instance.kind == OpenTelemetrySpanKind.CLIENT
            assert wrapped_class.span_instance.attributes.get("http.request.method") == request.method
            assert wrapped_class.span_instance.attributes.get("component") == "http"
            assert wrapped_class.span_instance.attributes.get("url.full") == request.url
            assert wrapped_class.span_instance.attributes.get("http.response.status_code") == 504
            assert wrapped_class.span_instance.attributes.get("user_agent.original") is None

            request.headers["User-Agent"] = "some user agent"
            request.url = "http://foo.bar:8080/path"
            wrapped_class.set_http_attributes(request, response)
            assert wrapped_class.span_instance.attributes.get("http.response.status_code") == response.status_code
            assert wrapped_class.span_instance.attributes.get("user_agent.original") == request.headers.get(
                "User-Agent"
            )

            if wrapped_class.span_instance.attributes.get("net.peer.name"):
                assert wrapped_class.span_instance.attributes.get("server.address") == "foo.bar"
                assert wrapped_class.span_instance.attributes.get("server.port") == 8080

    def test_span_kind(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as parent:
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

    def test_error_type_attribute_builtin_error(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root") as parent:
            with pytest.raises(ValueError):
                with OpenTelemetrySpan() as wrapped_class:
                    raise ValueError("This is a test error")

        finished = tracing_helper.exporter.get_finished_spans()
        assert len(finished) == 2

        assert finished[0].attributes.get("error.type") == "ValueError"
        assert finished[0].name == "span"
        assert finished[0].status.status_code == OpenTelemetryStatusCode.ERROR
        assert finished[0].status.description == "ValueError: This is a test error"

        assert finished[1].name == "Root"
        assert finished[1].status.status_code == OpenTelemetryStatusCode.UNSET

    def test_error_type_attribute_azure_error(self, tracing_helper):
        with pytest.raises(ClientAuthenticationError):
            with tracing_helper.tracer.start_as_current_span("Root") as parent:
                with OpenTelemetrySpan(name="span") as span:
                    raise ClientAuthenticationError("This is a test error")
        finished = tracing_helper.exporter.get_finished_spans()
        assert len(finished) == 2

        assert finished[0].attributes.get("error.type") == "azure.core.exceptions.ClientAuthenticationError"
        assert finished[0].name == "span"
        assert finished[0].status.status_code == OpenTelemetryStatusCode.ERROR
        assert finished[0].status.description == "azure.core.exceptions.ClientAuthenticationError: This is a test error"

        assert finished[1].name == "Root"
        assert finished[1].status.status_code == OpenTelemetryStatusCode.ERROR

    def test_error_in_change_context(self, tracing_helper):
        span = OpenTelemetrySpan(name="span")

        try:
            with span.change_context(span):
                raise ClientAuthenticationError("This is a test error")
        except ClientAuthenticationError:
            pass

        assert len(tracing_helper.exporter.get_finished_spans()) == 0
        span.finish()

        finished = tracing_helper.exporter.get_finished_spans()

        assert finished[0].name == "span"
        assert finished[0].status.status_code == OpenTelemetryStatusCode.UNSET
