# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""The tests for decorators.py and common.py"""

import unittest

try:
    from unittest import mock
except ImportError:
    import mock

import sys
import os
from azure.core import HttpRequest
from azure.core.pipeline import Pipeline, PipelineResponse
from azure.core.pipeline.policies import HTTPPolicy
from azure.core.pipeline.transport import HttpTransport
from azure.core.tracing import common
from azure.core.tracing.context import tracing_context
from azure.core.tracing.decorator import distributed_trace
from azure.core.settings import settings
from azure.core.tracing.ext.opencensus_span import OpenCensusSpan
from opencensus.trace import tracer as tracer_module
from opencensus.trace.samplers import AlwaysOnSampler
from tracing_common import ContextHelper, MockExporter
import time
import pytest

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import List


class MockClient:
    @distributed_trace
    def __init__(self, policies=None, assert_current_span=False):
        time.sleep(0.001)
        self.request = HttpRequest("GET", "https://bing.com")
        if policies is None:
            policies = []
        policies.append(mock.Mock(spec=HTTPPolicy, send=self.verify_request))
        self.policies = policies
        self.transport = mock.Mock(spec=HttpTransport)
        self.pipeline = Pipeline(self.transport, policies=policies)

        self.expected_response = mock.Mock(spec=PipelineResponse)
        self.assert_current_span = assert_current_span

    def verify_request(self, request):
        current_span = tracing_context.current_span.get()
        if self.assert_current_span:
            assert current_span is not None
        return self.expected_response

    @distributed_trace
    def make_request(self, numb_times, **kwargs):
        time.sleep(0.001)
        if numb_times < 1:
            return None
        response = self.pipeline.run(self.request, **kwargs)
        self.get_foo()
        self.make_request(numb_times - 1, **kwargs)
        return response

    @distributed_trace
    def get_foo(self):
        time.sleep(0.001)
        return 5

class TestCommon(object):
    def test_set_span_context(self):
        with ContextHelper(environ={"AZURE_SDK_TRACING_IMPLEMENTATION": "opencensus"}):
            wrapper = settings.tracing_implementation()
            assert wrapper is OpenCensusSpan
            assert tracing_context.current_span.get() is None
            assert wrapper.get_current_span() is None
            parent = OpenCensusSpan()
            common.set_span_contexts(parent)
            assert parent.span_instance == wrapper.get_current_span()
            assert tracing_context.current_span.get() == parent

    def test_get_parent_span(self):
        with ContextHelper():
            opencensus = sys.modules["opencensus"]
            del sys.modules["opencensus"]

            parent = common.get_parent_span(None)
            assert parent is None

            sys.modules["opencensus"] = opencensus
            parent = common.get_parent_span(None)
            assert parent.span_instance.name == "azure-sdk-for-python-first_parent_span"

            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler())
            parent = common.get_parent_span(None)
            assert parent.span_instance.name == "azure-sdk-for-python-first_parent_span"
            parent.finish()

            some_span = tracer.start_span(name="some_span")
            new_parent = common.get_parent_span(None)
            assert new_parent.span_instance.name == "some_span"
            some_span.finish()

            should_be_old_parent = common.get_parent_span(parent.span_instance)
            assert should_be_old_parent.span_instance == parent.span_instance

    def test_should_use_trace(self):
        with ContextHelper(environ={"AZURE_TRACING_ONLY_PROPAGATE": "yes"}):
            parent_span = OpenCensusSpan()
            assert common.should_use_trace(parent_span) == False
            assert common.should_use_trace(None) == False
        parent_span = OpenCensusSpan()
        assert common.should_use_trace(parent_span)
        assert common.should_use_trace(None) == False


class TestDecorator(object):
    def test_with_nothing_imported(self):
        with ContextHelper():
            opencensus = sys.modules["opencensus"]
            del sys.modules["opencensus"]
            client = MockClient(assert_current_span=True)
            with pytest.raises(AssertionError):
                client.make_request(3)
            sys.modules["opencensus"] = opencensus

    def test_with_opencensus_imported_but_not_used(self):
        with ContextHelper():
            client = MockClient(assert_current_span=True)
            client.make_request(3)

    def test_with_opencencus_used(self):
        with ContextHelper():
            exporter = MockExporter()
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
            parent = trace.start_span(name="OverAll")
            client = MockClient(policies=[])
            client.get_foo(parent_span=parent)
            client.get_foo()
            parent.finish()
            trace.finish()
            exporter.build_tree()
            parent = exporter.root
            assert len(parent.children) == 3
            assert parent.children[0].span_data.name == "MockClient.__init__"
            assert not parent.children[0].children
            assert parent.children[1].span_data.name == "MockClient.get_foo"
            assert not parent.children[1].children

    @pytest.mark.parametrize("value", ["opencensus", None])
    def test_span_with_opencensus_complicated(self, value):
        with ContextHelper(tracer_to_use=value) as ctx:
            exporter = MockExporter()
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
            with trace.start_span(name="OverAll") as parent:
                client = MockClient()
                client.make_request(2)
                with trace.span("child") as child:
                    time.sleep(0.001)
                    client.make_request(2, parent_span=parent)
                    assert OpenCensusSpan.get_current_span() == child
                    client.make_request(2)
            trace.finish()
            exporter.build_tree()
            parent = exporter.root
            assert len(parent.children) == 4
            assert parent.children[0].span_data.name == "MockClient.__init__"
            assert parent.children[1].span_data.name == "MockClient.make_request"
            assert parent.children[1].children[0].span_data.name == "MockClient.get_foo"
            assert parent.children[1].children[1].span_data.name == "MockClient.make_request"
            assert parent.children[2].span_data.name == "child"
            assert parent.children[2].children[0].span_data.name == "MockClient.make_request"
            assert parent.children[3].span_data.name == "MockClient.make_request"
            assert parent.children[3].children[0].span_data.name == "MockClient.get_foo"
            assert parent.children[3].children[1].span_data.name == "MockClient.make_request"
            children = parent.children[1].children
            assert len(children) == 2

    def test_should_only_propagate(self):
        with ContextHelper(should_only_propagate=True):
            exporter = MockExporter()
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
            with trace.start_span(name="OverAll") as parent:
                client = MockClient()
                client.make_request(2)
                with trace.span("child") as child:
                    client.make_request(2, parent_span=parent)
                    assert OpenCensusSpan.get_current_span() == child
                    client.make_request(2)
            trace.finish()
            exporter.build_tree()
            parent = exporter.root
            assert len(parent.children) == 1
            assert parent.children[0].span_data.name == "child"
            assert not parent.children[0].children
