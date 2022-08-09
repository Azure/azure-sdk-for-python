# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""The tests for opencensus_span.py"""

import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from opentelemetry import trace
from opentelemetry.trace import SpanKind as OpenTelemetrySpanKind

from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.core.tracing import SpanKind
import os

import pytest


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
            setattr(request, "url", "some url")
            response = mock.Mock()
            setattr(request, "headers", {})
            setattr(response, "status_code", 200)
            wrapped_class.set_http_attributes(request)
            assert wrapped_class.span_instance.kind == OpenTelemetrySpanKind.CLIENT
            assert wrapped_class.span_instance.attributes.get("http.method") == request.method
            assert wrapped_class.span_instance.attributes.get("component") == "http"
            assert wrapped_class.span_instance.attributes.get("http.url") == request.url
            assert wrapped_class.span_instance.attributes.get("http.status_code") == 504
            assert wrapped_class.span_instance.attributes.get("http.user_agent") is None
            request.headers["User-Agent"] = "some user agent"
            wrapped_class.set_http_attributes(request, response)
            assert wrapped_class.span_instance.attributes.get("http.status_code") == response.status_code
            assert wrapped_class.span_instance.attributes.get("http.user_agent") == request.headers.get("User-Agent")

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
                wrapped_class.kind = "somethingstuid" # what should be done here?
