# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the distributed tracing policy."""
import logging

from azure.core.pipeline import PipelineResponse, PipelineRequest, PipelineContext
from azure.core.pipeline.policies import DistributedTracingPolicy, UserAgentPolicy
from azure.core.pipeline.transport import HttpRequest, HttpResponse
from opencensus.trace import tracer as tracer_module
from opencensus.trace.samplers import AlwaysOnSampler
from azure.core.tracing.ext.opencensus_span import OpenCensusSpan
from tracing_common import ContextHelper, MockExporter
import time
import pytest


def test_distributed_tracing_policy_solo():
    """Test policy with no other policy and happy path"""
    with ContextHelper():
        exporter = MockExporter()
        trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
        with trace.span("parent"):
            policy = DistributedTracingPolicy()

            request = HttpRequest("GET", "http://127.0.0.1/temp?query=query")
            request.headers["x-ms-client-request-id"] = "some client request id"

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
            time.sleep(0.001)
            policy.on_request(pipeline_request)
            policy.on_exception(pipeline_request)

        trace.finish()
        exporter.build_tree()
        parent = exporter.root
        network_span = parent.children[0]
        assert network_span.span_data.name == "/temp"
        assert network_span.span_data.attributes.get("http.method") == "GET"
        assert network_span.span_data.attributes.get("component") == "http"
        assert network_span.span_data.attributes.get("http.url") == "http://127.0.0.1/temp?query=query"
        assert network_span.span_data.attributes.get("http.user_agent") is None
        assert network_span.span_data.attributes.get("x-ms-request-id") == "some request id"
        assert network_span.span_data.attributes.get("x-ms-client-request-id") == "some client request id"
        assert network_span.span_data.attributes.get("http.status_code") == 202

        network_span = parent.children[1]
        assert network_span.span_data.name == "/temp"
        assert network_span.span_data.attributes.get("http.method") == "GET"
        assert network_span.span_data.attributes.get("component") == "http"
        assert network_span.span_data.attributes.get("http.url") == "http://127.0.0.1/temp?query=query"
        assert network_span.span_data.attributes.get("x-ms-client-request-id") == "some client request id"
        assert network_span.span_data.attributes.get("http.user_agent") is None
        assert network_span.span_data.attributes.get("x-ms-request-id") == None
        assert network_span.span_data.attributes.get("http.status_code") == 504


def test_distributed_tracing_policy_badurl(caplog):
    """Test policy with a bad url that will throw, and be sure policy ignores it"""
    with ContextHelper():
        exporter = MockExporter()
        trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
        with trace.span("parent"):
            policy = DistributedTracingPolicy()

            request = HttpRequest("GET", "http://[[[")
            request.headers["x-ms-client-request-id"] = "some client request id"

            pipeline_request = PipelineRequest(request, PipelineContext(None))
            with caplog.at_level(logging.WARNING, logger="azure.core.pipeline.policies.distributed_tracing"):
                policy.on_request(pipeline_request)
            assert "Unable to start network span" in caplog.text

            response = HttpResponse(request, None)
            response.headers = request.headers
            response.status_code = 202
            response.headers["x-ms-request-id"] = "some request id"

            ctx = trace.span_context
            header = trace.propagator.to_headers(ctx)
            assert request.headers.get("traceparent") is None  # Got not network trace

            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))
            time.sleep(0.001)
            policy.on_request(pipeline_request)
            policy.on_exception(pipeline_request)

        trace.finish()
        exporter.build_tree()
        parent = exporter.root
        assert len(parent.children) == 0


def test_distributed_tracing_policy_with_user_agent():
    """Test policy working with user agent."""
    with ContextHelper(environ={"AZURE_HTTP_USER_AGENT": "mytools"}):
        exporter = MockExporter()
        trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
        with trace.span("parent"):
            policy = DistributedTracingPolicy()

            request = HttpRequest("GET", "http://127.0.0.1")
            request.headers["x-ms-client-request-id"] = "some client request id"

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

            time.sleep(0.001)
            policy.on_request(pipeline_request)
            try:
                raise ValueError("Transport trouble")
            except:
                policy.on_exception(pipeline_request)

            user_agent.on_response(pipeline_request, pipeline_response)

        trace.finish()
        exporter.build_tree()
        parent = exporter.root
        network_span = parent.children[0]
        assert network_span.span_data.name == "/"
        assert network_span.span_data.attributes.get("http.method") == "GET"
        assert network_span.span_data.attributes.get("component") == "http"
        assert network_span.span_data.attributes.get("http.url") == "http://127.0.0.1"
        assert network_span.span_data.attributes.get("http.user_agent").endswith("mytools")
        assert network_span.span_data.attributes.get("x-ms-request-id") == "some request id"
        assert network_span.span_data.attributes.get("x-ms-client-request-id") == "some client request id"
        assert network_span.span_data.attributes.get("http.status_code") == 202

        network_span = parent.children[1]
        assert network_span.span_data.name == "/"
        assert network_span.span_data.attributes.get("http.method") == "GET"
        assert network_span.span_data.attributes.get("component") == "http"
        assert network_span.span_data.attributes.get("http.url") == "http://127.0.0.1"
        assert network_span.span_data.attributes.get("http.user_agent").endswith("mytools")
        assert network_span.span_data.attributes.get("x-ms-client-request-id") == "some client request id"
        assert network_span.span_data.attributes.get("x-ms-request-id") is None
        assert network_span.span_data.attributes.get("http.status_code") == 504
        # Exception should propagate status for Opencensus
        assert network_span.span_data.status.message == 'Transport trouble'

