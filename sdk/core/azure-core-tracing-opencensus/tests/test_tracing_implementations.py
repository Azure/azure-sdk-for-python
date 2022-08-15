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

from azure.core.tracing.ext.opencensus_span import OpenCensusSpan
from azure.core.tracing import SpanKind, Link
from opencensus.trace import tracer as tracer_module
from opencensus.trace.attributes import Attributes
from opencensus.trace.span import SpanKind as OpenCensusSpanKind
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.trace.base_exporter import Exporter
from tracing_common import MockExporter, ContextHelper
import os

import pytest

class TestOpencensusWrapper(unittest.TestCase):
    def test_span_passed_in(self):
        with ContextHelper():
            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler())
            with tracer.start_span(name="parent") as parent:
                wrapped_span = OpenCensusSpan(parent)
            assert wrapped_span.span_instance.name == "parent"
            assert wrapped_span.span_instance.context_tracer.trace_id == tracer.span_context.trace_id
            wrapped_span.finish()
            tracer.finish()

    def test_no_span_passed_in_with_no_environ(self):
        with ContextHelper() as ctx:
            tracer = OpenCensusSpan.get_current_tracer()
            wrapped_span = OpenCensusSpan()
            assert wrapped_span.span_instance.name == "span"
            assert wrapped_span.span_instance.context_tracer.span_context.trace_id == tracer.span_context.trace_id
            assert ctx.orig_tracer == tracer
            wrapped_span.finish()

    def test_no_span_but_in_trace(self):
        with ContextHelper():
            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler())
            wrapped_span = OpenCensusSpan()
            assert wrapped_span.span_instance.name == "span"
            assert wrapped_span.span_instance.context_tracer.trace_id == tracer.span_context.trace_id
            wrapped_span.finish()
            tracer.finish()

    def test_span(self):
        exporter = MockExporter()
        with ContextHelper() as ctx:
            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
            assert OpenCensusSpan.get_current_tracer() is tracer
            wrapped_class = OpenCensusSpan()
            assert tracer.current_span() == wrapped_class.span_instance
            child = wrapped_class.span()
            assert tracer.current_span() == child.span_instance
            assert child.span_instance.name == "span"
            assert child.span_instance.context_tracer.trace_id == tracer.span_context.trace_id
            assert child.span_instance.parent_span is wrapped_class.span_instance
            tracer.finish()
        exporter.build_tree()
        parent = exporter.root
        assert len(parent.children) == 1
        assert parent.children[0].span_data.span_id == child.span_instance.span_id

    def test_start_finish(self):
        with ContextHelper() as ctx:
            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler())
            parent = OpenCensusSpan()
            wrapped_class = parent.span()
            assert wrapped_class.span_instance.end_time is None
            wrapped_class.start()
            wrapped_class.finish()
            assert wrapped_class.span_instance.start_time is not None
            assert wrapped_class.span_instance.end_time is not None
            parent.finish()
            tracer.finish()

    def test_to_header(self):
        with ContextHelper() as ctx:
            og_header = {"traceparent": "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-01"}
            ctx = tracer_module.trace_context_http_header_format.TraceContextPropagator().from_headers(og_header)
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), span_context=ctx)
            wrapped_class = OpenCensusSpan()
            headers = wrapped_class.to_header()
            new_header = {
                "traceparent": "00-2578531519ed94423ceae67588eff2c9-{}-01".format(wrapped_class.span_instance.span_id)
            }
            assert headers == new_header

    def test_links(self):
        with ContextHelper() as ctx:
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler())
            og_header = {"traceparent": "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-01"}
            wrapped_class = OpenCensusSpan()
            OpenCensusSpan.link_from_headers(og_header)
            assert len(wrapped_class.span_instance.links) == 1
            link = wrapped_class.span_instance.links[0]
            assert link.trace_id == "2578531519ed94423ceae67588eff2c9"
            assert link.span_id == "231ebdc614cb9ddd"

    def test_links_with_attributes(self):
        attributes = {"attr1": 1}
        with ContextHelper() as ctx:
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler())
            og_header = {"traceparent": "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-02"}
            wrapped_class = OpenCensusSpan()
            OpenCensusSpan.link_from_headers(og_header, attributes)
            assert len(wrapped_class.span_instance.links) == 1
            link = wrapped_class.span_instance.links[0]
            assert link.trace_id == "2578531519ed94423ceae67588eff2c9"
            assert link.span_id == "231ebdc614cb9ddd"
            assert link.attributes == attributes
            assert "attr1" in link.attributes

    def test_add_attribute(self):
        with ContextHelper() as ctx:
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler())
            parent = trace.start_span()
            wrapped_class = OpenCensusSpan(span=parent)
            wrapped_class.add_attribute("test", "test2")
            assert wrapped_class.span_instance.attributes["test"] == "test2"
            assert parent.attributes["test"] == "test2"

    def test_passing_kind_in_ctor(self):
        with ContextHelper() as ctx:
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler())
            parent = trace.start_span()
            wrapped_class = OpenCensusSpan(kind=SpanKind.CLIENT)
            assert wrapped_class.kind == SpanKind.CLIENT

    def test_passing_links_in_ctor(self):
        with ContextHelper() as ctx:
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler())
            parent = trace.start_span()
            wrapped_class = OpenCensusSpan(
                links=[Link(
                    headers= {"traceparent": "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-01"}
                    )
                ]
            )
            assert len(wrapped_class.span_instance.links) == 1
            link = wrapped_class.span_instance.links[0]
            assert link.trace_id == "2578531519ed94423ceae67588eff2c9"
            assert link.span_id == "231ebdc614cb9ddd"

    def test_passing_links_in_ctor_with_attr(self):
        attributes = {"attr1": 1}
        with ContextHelper() as ctx:
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler())
            parent = trace.start_span()
            wrapped_class = OpenCensusSpan(
                links=[Link(
                    headers= {"traceparent": "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-01"},
                    attributes=attributes
                    )
                ]
            )
            assert len(wrapped_class.span_instance.links) == 1
            link = wrapped_class.span_instance.links[0]
            assert link.attributes is not None
            assert link.trace_id == "2578531519ed94423ceae67588eff2c9"
            assert link.span_id == "231ebdc614cb9ddd"


    def test_set_http_attributes(self):
        with ContextHelper():
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler())
            parent = trace.start_span()
            wrapped_class = OpenCensusSpan(span=parent)
            request = mock.Mock()
            setattr(request, "method", "GET")
            setattr(request, "url", "some url")
            response = mock.Mock()
            setattr(request, "headers", {})
            setattr(response, "status_code", 200)
            wrapped_class.set_http_attributes(request)
            assert wrapped_class.span_instance.span_kind == OpenCensusSpanKind.CLIENT
            assert wrapped_class.span_instance.attributes.get("http.method") == request.method
            assert wrapped_class.span_instance.attributes.get("component") == "http"
            assert wrapped_class.span_instance.attributes.get("http.url") == request.url
            assert wrapped_class.span_instance.attributes.get("http.status_code") == 504
            assert wrapped_class.span_instance.attributes.get("http.user_agent") is None
            request.headers["User-Agent"] = "some user agent"
            wrapped_class.set_http_attributes(request, response)
            assert wrapped_class.span_instance.attributes.get("http.status_code") == response.status_code
            assert wrapped_class.span_instance.attributes.get("http.user_agent") == request.headers.get("User-Agent")

    def test_span_kind(self):
        with ContextHelper():
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler())
            parent = trace.start_span()
            wrapped_class = OpenCensusSpan(span=parent)

            wrapped_class.kind = SpanKind.UNSPECIFIED
            assert wrapped_class.span_instance.span_kind == OpenCensusSpanKind.UNSPECIFIED
            assert wrapped_class.kind == SpanKind.UNSPECIFIED

            wrapped_class.kind = SpanKind.SERVER
            assert wrapped_class.span_instance.span_kind == OpenCensusSpanKind.SERVER
            assert wrapped_class.kind == SpanKind.SERVER

            wrapped_class.kind = SpanKind.CLIENT
            assert wrapped_class.span_instance.span_kind == OpenCensusSpanKind.CLIENT
            assert wrapped_class.kind == SpanKind.CLIENT

            # opencensus doesn't support producer, put client instead
            wrapped_class.kind = SpanKind.PRODUCER
            assert wrapped_class.span_instance.span_kind == OpenCensusSpanKind.CLIENT
            assert wrapped_class.kind == SpanKind.CLIENT

            # opencensus doesn't support consumer, put client instead
            wrapped_class.kind = SpanKind.CONSUMER
            assert wrapped_class.span_instance.span_kind == OpenCensusSpanKind.CLIENT
            assert wrapped_class.kind == SpanKind.CLIENT

            # opencensus doesn't support consumer, put client instead
            wrapped_class.kind = SpanKind.INTERNAL
            assert wrapped_class.span_instance.span_kind == OpenCensusSpanKind.UNSPECIFIED
            assert wrapped_class.kind == SpanKind.UNSPECIFIED
