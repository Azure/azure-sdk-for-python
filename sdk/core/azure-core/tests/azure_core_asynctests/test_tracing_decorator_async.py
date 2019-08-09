# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""The tests for decorators_async.py"""

try:
    from unittest import mock
except ImportError:
    import mock

import sys
from azure.core import HttpRequest
from azure.core.pipeline import Pipeline, PipelineResponse
from azure.core.pipeline.policies import HTTPPolicy
from azure.core.pipeline.transport import HttpTransport
from azure.core.tracing.context import tracing_context
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.ext.opencensus_span import OpenCensusSpan
from opencensus.trace import tracer as tracer_module
from opencensus.trace.samplers import AlwaysOnSampler
from tracing_common import ContextHelper, MockExporter
import pytest
import time


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

    @distributed_trace_async
    async def make_request(self, numb_times, **kwargs):
        time.sleep(0.001)
        if numb_times < 1:
            return None
        response = self.pipeline.run(self.request, **kwargs)
        await self.get_foo()
        await self.make_request(numb_times - 1, **kwargs)
        return response

    @distributed_trace_async
    async def get_foo(self):
        time.sleep(0.001)
        return 5

    @distributed_trace_async(name_of_span="different name")
    async def check_name_is_different(self):
        time.sleep(0.001)


@pytest.mark.asyncio
async def test_decorator_has_different_name():
    with ContextHelper():
        exporter = MockExporter()
        trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
        with trace.span("overall"):
            client = MockClient()
            await client.check_name_is_different()
        trace.finish()
        exporter.build_tree()
        parent = exporter.root
        assert len(parent.children) == 2
        assert parent.children[0].span_data.name == "MockClient.__init__"
        assert parent.children[1].span_data.name == "different name"


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
        exporter = MockExporter()
        trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
        parent = trace.start_span(name="OverAll")
        client = MockClient(policies=[])
        await client.get_foo(parent_span=parent)
        await client.get_foo()
        parent.finish()
        trace.finish()
        exporter.build_tree()
        parent = exporter.root
        assert len(parent.children) == 3
        assert parent.children[0].span_data.name == "MockClient.__init__"
        assert not parent.children[0].children
        assert parent.children[1].span_data.name == "MockClient.get_foo"
        assert not parent.children[1].children


@pytest.mark.parametrize("value", [None, "opencensus"])
@pytest.mark.asyncio
async def test_span_with_opencensus_complicated(value):
    with ContextHelper(tracer_to_use=value):
        exporter = MockExporter()
        trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
        with trace.start_span(name="OverAll") as parent:
            client = MockClient()
            await client.make_request(2)
            with trace.span("child") as child:
                time.sleep(0.001)
                await client.make_request(2, parent_span=parent)
                assert OpenCensusSpan.get_current_span() == child
                await client.make_request(2)
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
