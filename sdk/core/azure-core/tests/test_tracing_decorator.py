# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
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
from azure.core.tracing.decorator import distributed_tracing_decorator
from azure.core.settings import settings
from azure.core.tracing.ext.opencensus_wrapper import OpenCensusSpan
from opencensus.trace import tracer as tracer_module
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.trace.base_exporter import Exporter
import pytest


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
        if self.tracer_to_use is not None:
            settings.tracing_implementation.set_value(self.tracer_to_use)
        self.os_env.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        OpenCensusSpan.set_current_tracer(self.orig_tracer)
        OpenCensusSpan.set_current_span(self.orig_current_span)
        tracing_context.current_span.set(self.orig_sdk_context_span)
        settings.tracing_implementation.unset_value()
        self.os_env.stop()


class MockClient:
    @distributed_tracing_decorator
    def __init__(self, policies=None, assert_current_span=False):
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

    @distributed_tracing_decorator
    def make_request(self, numb_times, **kwargs):
        if numb_times < 1:
            return None
        response = self.pipeline.run(self.request, **kwargs)
        self.get_foo()
        self.make_request(numb_times - 1, **kwargs)
        return response

    @distributed_tracing_decorator
    def get_foo(self):
        return 5


class TestCommon(unittest.TestCase):
    def test_get_opencensus_wrapper_if_opencensus_is_imported(self):
        opencensus = sys.modules["opencensus"]
        del sys.modules["opencensus"]
        assert common.get_opencensus_wrapper_if_opencensus_is_imported() == None
        sys.modules["opencensus"] = opencensus
        assert common.get_opencensus_wrapper_if_opencensus_is_imported() is OpenCensusSpan

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

    def test_get_parent(self):
        with ContextHelper():
            opencensus = sys.modules["opencensus"]
            del sys.modules["opencensus"]

            parent, orig_tracing_context, orig_span_inst = common.get_parent({})
            assert orig_span_inst is None
            assert parent is None
            assert orig_tracing_context is None

            sys.modules["opencensus"] = opencensus
            parent, orig_tracing_context, orig_span_inst = common.get_parent({})
            assert orig_span_inst is None
            assert parent.span_instance.name == "azure-sdk-for-python-first_parent_span"
            assert orig_tracing_context is None

            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler())
            parent, orig_tracing_context, orig_span_inst = common.get_parent({})
            assert orig_span_inst is None
            assert parent.span_instance.name == "azure-sdk-for-python-first_parent_span"
            assert orig_tracing_context is None
            parent.finish()

            some_span = tracer.start_span(name="some_span")
            new_parent, orig_tracing_context, orig_span_inst = common.get_parent({})
            assert orig_span_inst == some_span
            assert new_parent.span_instance.name == "some_span"
            assert orig_tracing_context is None

            kwarg = {"parent_span": parent.span_instance}
            should_be_old_parent, orig_tracing_context, orig_span_inst = common.get_parent(kwarg)
            assert kwarg.get("parent_span") is None
            assert orig_span_inst == some_span
            assert should_be_old_parent.span_instance == parent.span_instance
            assert orig_tracing_context is None

    def test_should_use_trace(self):
        with ContextHelper(environ={"AZURE_TRACING_ONLY_PROPAGATE": "yes"}):
            parent_span = OpenCensusSpan()
            assert common.should_use_trace(parent_span) == False
            assert common.should_use_trace(None) == False
        parent_span = OpenCensusSpan()
        assert common.should_use_trace(parent_span)
        assert common.should_use_trace(None) == False


class TestDecorator(unittest.TestCase):
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
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler())
            parent = trace.start_span(name="OverAll")
            client = MockClient(policies=[])
            client.get_foo(parent_span=parent)
            client.get_foo()
            assert len(parent.children) == 3
            assert parent.children[0].name == "MockClient.__init__"
            assert not parent.children[0].children
            assert parent.children[1].name == "MockClient.get_foo"
            assert not parent.children[1].children
            parent.finish()
            trace.finish()

    def for_test_different_settings(self):
        with ContextHelper():
            trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=mock.Mock(Exporter))
            with trace.start_span(name="OverAll") as parent:
                client = MockClient()
                client.make_request(2)
                with parent.span("child") as child:
                    client.make_request(2, parent_span=child)
                client.make_request(2)
                assert len(parent.children) == 4
                assert parent.children[0].name == "MockClient.__init__"
                assert parent.children[1].name == "MockClient.make_request"
                assert parent.children[2].children[0].name == "MockClient.make_request"
                children = parent.children[1].children
                assert len(children) == 2
            trace.finish()

    def test_span_with_opencensus_complicated(self):
        self.for_test_different_settings()

    def test_span_with_opencensus_passed_in_complicated(self):
        with ContextHelper(tracer_to_use="opencensus"):
            self.for_test_different_settings()


if __name__ == "__main__":
    unittest.main()
