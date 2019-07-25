# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Code shared between the async and the sync test_decorator files."""

import os

from azure.core.settings import settings
from azure.core.tracing.context import tracing_context
from azure.core.tracing.ext.opencensus_span import OpenCensusSpan
from opencensus.trace import execution_context
from opencensus.trace.base_exporter import Exporter
from opencensus.trace.span_data import SpanData
from collections import defaultdict
from opencensus.trace import execution_context

try:
    from unittest import mock
except ImportError:
    import mock


class ContextHelper(object):
    def __init__(self, environ={}, tracer_to_use=None):
        self.orig_tracer = OpenCensusSpan.get_current_tracer()
        self.orig_current_span = OpenCensusSpan.get_current_span()
        self.orig_sdk_context_span = tracing_context.current_span.get()
        self.os_env = mock.patch.dict(os.environ, environ)
        self.tracer_to_use = tracer_to_use

    def __enter__(self):
        self.orig_tracer = OpenCensusSpan.get_current_tracer()
        self.orig_current_span = OpenCensusSpan.get_current_span()
        self.orig_sdk_context_span = tracing_context.current_span.get()
        execution_context.clear()
        tracing_context.current_span.clear()
        if self.tracer_to_use is not None:
            settings.tracing_implementation.set_value(self.tracer_to_use)
        self.os_env.start()
        execution_context.clear()
        tracing_context.current_span.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        OpenCensusSpan.set_current_tracer(self.orig_tracer)
        OpenCensusSpan.set_current_span(self.orig_current_span)
        tracing_context.current_span.set(self.orig_sdk_context_span)
        settings.tracing_implementation.unset_value()
        self.os_env.stop()


class Node:
    def __init__(self, span_data):
        self.span_data = span_data  # type: SpanData
        self.parent = None
        self.children = []


class MockExporter(Exporter):
    def __init__(self):
        self.root = None  # type: SpanData
        self._all_nodes = []
        self.parent_dict = defaultdict(list)

    def export(self, span_datas):
        # type: (List[SpanData]) -> None
        sp = span_datas[0]  # type: SpanData
        node = Node(sp)
        if not node.span_data.parent_span_id:
            self.root = node
        parent_span_id = node.span_data.parent_span_id
        self.parent_dict[parent_span_id].append(node)
        self._all_nodes.append(node)

    def build_tree(self):
        for node in self._all_nodes:
            if node.span_data.span_id in self.parent_dict:
                node.children = sorted(self.parent_dict[node.span_data.span_id], key=lambda x: x.span_data.start_time)
