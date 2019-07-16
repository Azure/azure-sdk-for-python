# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the distributed tracing policy."""

from azure.core.pipeline import PipelineResponse, PipelineRequest, PipelineContext
from azure.core.pipeline.policies.distributed_tracing import DistributedTracingPolicy
from azure.core.pipeline.policies.universal import UserAgentPolicy
from azure.core.pipeline.transport import HttpRequest, HttpResponse
from opencensus.trace import tracer as tracer_module
from opencensus.trace.samplers import AlwaysOnSampler
from tracing_common import ContextHelper, MockExporter


def test_distributed_tracing_policy_solo():
    """Test policy with no other policy and happy path"""
    with ContextHelper():
        exporter = MockExporter()
        trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
        policy = DistributedTracingPolicy()

        request = HttpRequest("GET", "http://127.0.0.1/")

        pipeline_request = PipelineRequest(request, PipelineContext(None))
        policy.on_request(pipeline_request)

        response = HttpResponse(request, None)
        response.headers = request.headers
        response.status_code = 202
        response.headers["x-ms-request-id"] = "some request id"

        ctx = trace.span_context
        header = trace.propagator.to_headers(ctx)
        assert request.headers.get("traceparent") == header.get("traceparent")

        policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

        trace.finish()
        exporter.build_tree()
        parent = exporter.root
        network_span = parent.children[0]
        assert network_span.span_data.name == "span - http call"
        assert network_span.span_data.attributes.get("http.method") == "GET"
        assert network_span.span_data.attributes.get("http.url") == "http://127.0.0.1/"
        assert network_span.span_data.attributes.get("http.user_agent") == ""
        assert network_span.span_data.attributes.get("x-ms-request-id") == "some request id"
        assert network_span.span_data.attributes.get("http.status_code") == 202


def test_distributed_tracing_policy_exception():
    """Test Policy on when an exception happens."""
    with ContextHelper():
        exporter = MockExporter()
        trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
        policy = DistributedTracingPolicy()

        request = HttpRequest("GET", "http://127.0.0.1/")

        pipeline_request = PipelineRequest(request, PipelineContext(None))
        policy.on_request(pipeline_request)

        ctx = trace.span_context
        header = trace.propagator.to_headers(ctx)
        assert request.headers.get("traceparent") == header.get("traceparent")

        policy.on_exception(pipeline_request)

        trace.finish()
        exporter.build_tree()
        parent = exporter.root
        network_span = parent.children[0]
        assert network_span.span_data.name == "span - http call"
        assert network_span.span_data.attributes.get("http.method") == "GET"
        assert network_span.span_data.attributes.get("http.url") == "http://127.0.0.1/"
        assert network_span.span_data.attributes.get("http.user_agent") == ""
        assert network_span.span_data.attributes.get("x-ms-request-id") is None
        assert network_span.span_data.attributes.get("http.status_code") == 504


def test_distributed_tracing_policy_with_usergent():
    """Test policy working with user agent."""
    with ContextHelper(environ={"AZURE_HTTP_USER_AGENT": "mytools"}):
        exporter = MockExporter()
        trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
        policy = DistributedTracingPolicy()

        request = HttpRequest("GET", "http://127.0.0.1/")

        pipeline_request = PipelineRequest(request, PipelineContext(None))

        user_agent = UserAgentPolicy()
        user_agent.on_request(pipeline_request)
        policy.on_request(pipeline_request)

        response = HttpResponse(request, None)
        response.headers = request.headers
        response.status_code = 202
        response.headers["x-ms-request-id"] = "some request id"
        pipeline_response = PipelineResponse(request, response, PipelineContext(None))

        ctx = trace.span_context
        header = trace.propagator.to_headers(ctx)
        assert request.headers.get("traceparent") == header.get("traceparent")

        policy.on_response(pipeline_request, pipeline_response)
        user_agent.on_response(pipeline_request, pipeline_response)

        trace.finish()
        exporter.build_tree()
        parent = exporter.root
        network_span = parent.children[0]
        assert network_span.span_data.name == "span - http call"
        assert network_span.span_data.attributes.get("http.method") == "GET"
        assert network_span.span_data.attributes.get("http.url") == "http://127.0.0.1/"
        assert network_span.span_data.attributes.get("http.user_agent").endswith("mytools")
        assert network_span.span_data.attributes.get("x-ms-request-id") == "some request id"
        assert network_span.span_data.attributes.get("http.status_code") == 202
