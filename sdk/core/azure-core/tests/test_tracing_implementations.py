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
from opencensus.trace import tracer as tracer_module
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.trace.base_exporter import Exporter
from opencensus.common.utils import timestamp_to_microseconds
import os


class Node:
    def __init__(self, span_data):
        self.span_data = span_data  # type: SpanData
        self.parent = None
        self.children = []


class MockExporter(Exporter):
    def __init__(self):
        self.root = None
        self._all_nodes = []

    def export(self, span_datas):
        # type: (List[SpanData]) -> None
        sp = span_datas[0]  # type: SpanData
        node = Node(sp)
        if not node.span_data.parent_span_id:
            self.root = node
        self._all_nodes.append(node)

    def build_tree(self):
        parent_dict = {}
        for node in self._all_nodes:
            parent_span_id = node.span_data.parent_span_id
            if parent_span_id not in parent_dict:
                parent_dict[parent_span_id] = []
            parent_dict[parent_span_id].append(node)

        for node in self._all_nodes:
            if node.span_data.span_id in parent_dict:
                node.children = sorted(
                    parent_dict[node.span_data.span_id], key=lambda x: timestamp_to_microseconds(x.span_data.start_time)
                )


class ContextHelper(object):
    def __init__(self, environ={}):
        self.orig_tracer = OpenCensusSpan.get_current_tracer()
        self.orig_current_span = OpenCensusSpan.get_current_span()
        self.os_env = mock.patch.dict(os.environ, environ)

    def __enter__(self):
        self.orig_tracer = OpenCensusSpan.get_current_tracer()
        self.orig_current_span = OpenCensusSpan.get_current_span()
        self.os_env.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        OpenCensusSpan.set_current_tracer(self.orig_tracer)
        OpenCensusSpan.set_current_span(self.orig_current_span)
        self.os_env.stop()


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
            OpenCensusSpan.link(og_header)
            assert len(wrapped_class.span_instance.links) == 1
            link = wrapped_class.span_instance.links[0]
            assert link.trace_id == "2578531519ed94423ceae67588eff2c9"
            assert link.span_id == "231ebdc614cb9ddd"

    def test_add_attribute(self):
        with ContextHelper() as ctx:
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler())
            parent = trace.start_span()
            wrapped_class = OpenCensusSpan(span=parent)
            wrapped_class.add_attribute("test", "test2")
            assert wrapped_class.span_instance.attributes["test"] == "test2"
            assert parent.attributes["test"] == "test2"
