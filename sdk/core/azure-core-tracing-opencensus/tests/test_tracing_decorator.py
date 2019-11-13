# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""The tests for decorators.py and common.py"""

try:
    from unittest import mock
except ImportError:
    import mock

import sys
import time

import pytest
from azure.core.pipeline import Pipeline, PipelineResponse
from azure.core.pipeline.policies import HTTPPolicy
from azure.core.pipeline.transport import HttpTransport, HttpRequest
from azure.core.settings import settings
from azure.core.tracing import common
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.ext.opencensus_span import OpenCensusSpan
from opencensus.trace import tracer as tracer_module, execution_context
from opencensus.trace.samplers import AlwaysOnSampler
from tracing_common import ContextHelper, MockExporter


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
        if self.assert_current_span:
            assert execution_context.get_current_span() is not None
        return self.expected_response

    @distributed_trace
    def make_request(self, numb_times, **kwargs):
        time.sleep(0.001)
        if numb_times < 1:
            return None
        response = self.pipeline.run(self.request, **kwargs)
        self.get_foo(merge_span=True)
        kwargs['merge_span'] = True
        self.make_request(numb_times - 1, **kwargs)
        return response

    @distributed_trace
    def merge_span_method(self):
        return self.get_foo(merge_span=True)

    @distributed_trace
    def no_merge_span_method(self):
        return self.get_foo()

    @distributed_trace
    def get_foo(self):
        time.sleep(0.001)
        return 5

    @distributed_trace(name_of_span="different name")
    def check_name_is_different(self):
        time.sleep(0.001)

    @distributed_trace
    def raising_exception(self):
        raise ValueError("Something went horribly wrong here")


def random_function():
    pass


class TestCommon(object):
    def test_get_function_and_class_name(self):
        with ContextHelper():
            client = MockClient()
            assert common.get_function_and_class_name(client.get_foo, client) == "MockClient.get_foo"
            assert common.get_function_and_class_name(random_function) == "random_function"


class TestDecorator(object):
    def test_decorator_has_different_name(self):
        with ContextHelper():
            exporter = MockExporter()
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
            with trace.span("overall"):
                client = MockClient()
                client.check_name_is_different()
            trace.finish()
            exporter.build_tree()
            parent = exporter.root
            assert len(parent.children) == 2
            assert parent.children[0].span_data.name == "MockClient.__init__"
            assert parent.children[1].span_data.name == "different name"

    @pytest.mark.skip(reason="Don't think this test makes sense anymore")
    def test_with_nothing_imported(self):
        with ContextHelper():
            opencensus = sys.modules["opencensus"]
            del sys.modules["opencensus"]
            try:
                client = MockClient(assert_current_span=True)
                with pytest.raises(AssertionError):
                    client.make_request(3)
            finally:
                sys.modules["opencensus"] = opencensus

    @pytest.mark.skip(reason="Don't think this test makes sense anymore")
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
    def test_span_with_opencensus_merge_span(self, value):
        with ContextHelper(tracer_to_use=value) as ctx:
            exporter = MockExporter()
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
            with trace.start_span(name="OverAll") as parent:
                client = MockClient()
                client.merge_span_method()
                client.no_merge_span_method()
            trace.finish()
            exporter.build_tree()
            parent = exporter.root
            assert len(parent.children) == 3
            assert parent.children[0].span_data.name == "MockClient.__init__"
            assert not parent.children[0].children
            assert parent.children[1].span_data.name == "MockClient.merge_span_method"
            assert not parent.children[1].children
            assert parent.children[2].span_data.name == "MockClient.no_merge_span_method"
            assert parent.children[2].children[0].span_data.name == "MockClient.get_foo"

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
            assert not parent.children[0].children
            assert parent.children[1].span_data.name == "MockClient.make_request"
            assert not parent.children[1].children
            assert parent.children[2].span_data.name == "child"
            assert parent.children[2].children[0].span_data.name == "MockClient.make_request"
            assert parent.children[3].span_data.name == "MockClient.make_request"
            assert not parent.children[3].children

    @pytest.mark.parametrize("value", ["opencensus", None])
    def test_span_with_exception(self, value):
        """Assert that if an exception is raised, the next sibling method is actually a sibling span.
        """
        with ContextHelper(tracer_to_use=value):
            exporter = MockExporter()
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
            with trace.span("overall"):
                client = MockClient()
                try:
                    client.raising_exception()
                except:
                    pass
                client.get_foo()
            trace.finish()
            exporter.build_tree()
            parent = exporter.root
            assert len(parent.children) == 3
            assert parent.children[0].span_data.name == "MockClient.__init__"
            assert parent.children[1].span_data.name == "MockClient.raising_exception"
            # Exception should propagate status for Opencensus
            assert parent.children[1].span_data.status.message == 'Something went horribly wrong here'
            assert parent.children[2].span_data.name == "MockClient.get_foo"
