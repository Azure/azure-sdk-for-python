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
from azure.core.tracing.context import tracing_context
from azure.core.tracing.decorator import distributed_tracing_decorator
from azure.core.tracing.decorator_async import distributed_tracing_decorator_async
from azure.core.settings import settings
from azure.core.tracing.ext.opencensus_span import OpenCensusSpan
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

    @distributed_tracing_decorator_async
    async def make_request(self, numb_times, **kwargs):
        if numb_times < 1:
            return None
        response = self.pipeline.run(self.request, **kwargs)
        await self.get_foo()
        await self.make_request(numb_times - 1, **kwargs)
        return response

    @distributed_tracing_decorator_async
    async def get_foo(self):
        return 5

@pytest.mark.asyncio
async def test_with_nothing_imported():
    with ContextHelper():
        opencensus = sys.modules["opencensus"]
        del sys.modules["opencensus"]
        client = MockClient(assert_current_span=True)
        with pytest.raises(AssertionError):
            await client.make_request(3)
        sys.modules["opencensus"] = opencensus

@pytest.mark.asyncio
async def test_with_opencensus_imported_but_not_used():
    with ContextHelper():
        client = MockClient(assert_current_span=True)
        await client.make_request(3)

@pytest.mark.asyncio
async def test_with_opencencus_used():
    with ContextHelper():
        trace = tracer_module.Tracer(sampler=AlwaysOnSampler())
        parent = trace.start_span(name="OverAll")
        client = MockClient(policies=[])
        await client.get_foo(parent_span=parent)
        await client.get_foo()
        assert len(parent.children) == 3
        assert parent.children[0].name == "MockClient.__init__"
        assert not parent.children[0].children
        assert parent.children[1].name == "MockClient.get_foo"
        assert not parent.children[1].children
        parent.finish()
        trace.finish()

@pytest.mark.asyncio
async def for_test_different_settings():
    with ContextHelper():
        trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=mock.Mock(Exporter))
        with trace.start_span(name="OverAll") as parent:
            client = MockClient()
            await client.make_request(2)
            with trace.span("child") as child:
                await client.make_request(2, parent_span=parent)
                assert OpenCensusSpan.get_current_span() == child
                await client.make_request(2)
            assert len(parent.children) == 3
            assert parent.children[0].name == "MockClient.__init__"
            assert parent.children[1].name == "MockClient.make_request"
            assert parent.children[1].children[0].name == "MockClient.get_foo"
            assert parent.children[1].children[1].name == "MockClient.make_request"
            assert parent.children[2].name == "MockClient.make_request"
            assert parent.children[2].children[0].name == "MockClient.get_foo"
            assert parent.children[2].children[1].name == "MockClient.make_request"
            children = parent.children[1].children
            assert len(children) == 2
        trace.finish()

@pytest.mark.asyncio
async def test_span_with_opencensus_complicated():
    for_test_different_settings()

@pytest.mark.asyncio
async def test_span_with_opencensus_passed_in_complicated():
    with ContextHelper(tracer_to_use="opencensus"):
        for_test_different_settings()
