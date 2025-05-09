# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for the distributed tracing policy."""
from unittest import mock
import pytest

from corehttp.rest import HttpRequest
from corehttp.runtime.policies import (
    DistributedHttpTracingPolicy,
    UserAgentPolicy,
    RetryPolicy,
)
from corehttp.settings import settings
from corehttp.runtime.pipeline import PipelineRequest, PipelineContext, PipelineResponse, Pipeline
from corehttp.transport import HttpTransport
from corehttp.transport.requests import RequestsTransport
from opentelemetry.trace import format_span_id, format_trace_id
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from utils import HTTP_RESPONSES, create_http_response


@pytest.mark.parametrize("http_response", HTTP_RESPONSES)
def test_distributed_tracing_policy(tracing_helper, http_response):
    """Test policy when the HTTP response corresponds to a success."""
    with tracing_helper.tracer.start_as_current_span("Root") as root_span:
        policy = DistributedHttpTracingPolicy()

        request = HttpRequest("GET", "http://localhost/temp?query=query")
        pipeline_request = PipelineRequest(request, PipelineContext(None))
        policy.on_request(pipeline_request)

        response = create_http_response(http_response, request, None, headers=request.headers, status_code=202)

        traceparent = request.headers.get("traceparent")
        assert traceparent is not None
        assert traceparent.startswith("00-")

        policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 2
    assert finished_spans[0].name == "GET"
    assert finished_spans[0].parent is root_span.get_span_context()

    span_context = finished_spans[0].get_span_context()
    assert traceparent.split("-")[1] == format_trace_id(span_context.trace_id)
    assert traceparent.split("-")[2] == format_span_id(span_context.span_id)

    assert finished_spans[0].attributes.get(policy._HTTP_REQUEST_METHOD) == "GET"
    assert finished_spans[0].attributes.get(policy._URL_FULL) == "http://localhost/temp?query=query"
    assert finished_spans[0].attributes.get(policy._SERVER_ADDRESS) == "localhost"
    assert finished_spans[0].attributes.get(policy._USER_AGENT_ORIGINAL) is None
    assert finished_spans[0].attributes.get(policy._HTTP_RESPONSE_STATUS_CODE) == 202
    assert finished_spans[1].name == "Root"


@pytest.mark.parametrize("http_response", HTTP_RESPONSES)
def test_distributed_tracing_policy_error_response(tracing_helper, http_response):
    """Test policy when the HTTP response corresponds to an error."""
    with tracing_helper.tracer.start_as_current_span("Root"):
        policy = DistributedHttpTracingPolicy()

        request = HttpRequest("GET", "http://localhost/temp?query=query")
        pipeline_request = PipelineRequest(request, PipelineContext(None))
        policy.on_request(pipeline_request)

        response = create_http_response(http_response, request, None, headers=request.headers, status_code=403)

        policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert finished_spans[0].name == "GET"
    assert finished_spans[0].attributes.get("error.type") == "403"


@pytest.mark.parametrize("http_response", HTTP_RESPONSES)
def test_distributed_tracing_policy_custom_instrumentation_config(tracing_helper, http_response):
    """Test policy when a custom instrumentation config is provided."""
    instrumentation_config = {
        "library_name": "mylibrary",
        "library_version": "1.0.0",
        "attributes": {"namespace": "Sample.Namespace"},
    }
    with tracing_helper.tracer.start_as_current_span("Root"):
        policy = DistributedHttpTracingPolicy(instrumentation_config=instrumentation_config)

        request = HttpRequest("GET", "http://localhost/temp?query=query")
        pipeline_request = PipelineRequest(request, PipelineContext(None))
        policy.on_request(pipeline_request)

        response = create_http_response(http_response, request, None, headers=request.headers, status_code=403)

        policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert finished_spans[0].name == "GET"
    assert finished_spans[0].attributes.get(policy._ERROR_TYPE) == "403"
    assert finished_spans[0].instrumentation_scope.name == "mylibrary"
    assert finished_spans[0].instrumentation_scope.version == "1.0.0"
    assert finished_spans[0].instrumentation_scope.attributes.get("namespace") == "Sample.Namespace"


@pytest.mark.parametrize("http_response", HTTP_RESPONSES)
def test_distributed_tracing_policy_with_user_agent_policy(tracing_helper, http_response):
    """Test policy when used with the UserAgentPolicy."""
    with mock.patch.dict("os.environ", {"CORE_HTTP_USER_AGENT": "test-user-agent"}):
        with tracing_helper.tracer.start_as_current_span("Root") as root_span:
            policy = DistributedHttpTracingPolicy()
            user_agent_policy = UserAgentPolicy()

            request = HttpRequest("GET", "http://localhost/temp?query=query")
            pipeline_request = PipelineRequest(request, PipelineContext(None))
            user_agent_policy.on_request(pipeline_request)
            policy.on_request(pipeline_request)

            response = create_http_response(http_response, request, None, headers=request.headers, status_code=202)

            traceparent = request.headers.get("traceparent")
            assert traceparent is not None
            assert traceparent.startswith("00-")

            pipeline_response = PipelineResponse(request, response, PipelineContext(None))

            policy.on_response(pipeline_request, pipeline_response)
            user_agent_policy.on_response(pipeline_request, pipeline_response)

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 2
    assert finished_spans[0].name == "GET"
    assert finished_spans[0].parent is root_span.get_span_context()

    span_context = finished_spans[0].get_span_context()
    assert traceparent.split("-")[1] == format_trace_id(span_context.trace_id)
    assert traceparent.split("-")[2] == format_span_id(span_context.span_id)

    assert finished_spans[0].attributes.get(policy._HTTP_REQUEST_METHOD) == "GET"
    assert finished_spans[0].attributes.get(policy._URL_FULL) == "http://localhost/temp?query=query"
    assert finished_spans[0].attributes.get(policy._SERVER_ADDRESS) == "localhost"
    assert finished_spans[0].attributes.get(policy._USER_AGENT_ORIGINAL) is not None
    assert finished_spans[0].attributes.get(policy._USER_AGENT_ORIGINAL).endswith("test-user-agent")
    assert finished_spans[0].attributes.get(policy._HTTP_RESPONSE_STATUS_CODE) == 202
    assert finished_spans[1].name == "Root"


@pytest.mark.parametrize("http_response", HTTP_RESPONSES)
def test_span_retry_attributes(tracing_helper, http_response):
    """Test that the retry count is added to the span attributes."""

    class MockTransport(HttpTransport):
        def __init__(self):
            self._count = 0

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def close(self):
            pass

        def open(self):
            pass

        def send(self, request, **kwargs):
            self._count += 1
            response = create_http_response(http_response, request, None, status_code=429)
            return response

    http_request = HttpRequest("GET", "http://localhost/")
    retry_policy = RetryPolicy(retry_total=2)
    distributed_tracing_policy = DistributedHttpTracingPolicy()
    transport = MockTransport()

    with tracing_helper.tracer.start_as_current_span("Root") as root_span:
        policies = [retry_policy, distributed_tracing_policy]
        pipeline = Pipeline(transport, policies=policies)
        pipeline.run(http_request)

    assert transport._count == 3

    finished_spans = tracing_helper.exporter.get_finished_spans()
    parent_context = root_span.get_span_context()
    assert len(finished_spans) == 4
    assert finished_spans[0].parent == parent_context
    assert finished_spans[0].attributes.get(distributed_tracing_policy._HTTP_RESEND_COUNT) is None
    assert finished_spans[0].attributes.get(distributed_tracing_policy._URL_FULL) == "http://localhost/"

    assert finished_spans[1].parent == parent_context
    assert finished_spans[1].attributes.get(distributed_tracing_policy._HTTP_RESEND_COUNT) == 1
    assert finished_spans[1].attributes.get(distributed_tracing_policy._URL_FULL) == "http://localhost/"

    assert finished_spans[2].parent == parent_context
    assert finished_spans[2].attributes.get(distributed_tracing_policy._HTTP_RESEND_COUNT) == 2
    assert finished_spans[2].attributes.get(distributed_tracing_policy._URL_FULL) == "http://localhost/"


@pytest.mark.parametrize("http_response", HTTP_RESPONSES)
def test_distributed_tracing_policy_with_tracing_options(tracing_helper, http_response):
    """Test policy when tracing options are provided."""
    settings.tracing_enabled = False
    with tracing_helper.tracer.start_as_current_span("Root") as root_span:
        policy = DistributedHttpTracingPolicy()

        request = HttpRequest("GET", "http://localhost/temp?query=query")
        pipeline_request = PipelineRequest(request, PipelineContext(None))
        pipeline_request.context.options["tracing_options"] = {
            "enabled": True,
            "attributes": {"custom_key": "custom_value"},
        }

        policy.on_request(pipeline_request)
        response = create_http_response(http_response, request, None, headers=request.headers, status_code=202)
        policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 2

    assert finished_spans[0].name == "GET"
    assert finished_spans[0].parent is root_span.get_span_context()

    assert finished_spans[0].attributes.get(policy._HTTP_REQUEST_METHOD) == "GET"
    assert finished_spans[0].attributes.get(policy._URL_FULL) == "http://localhost/temp?query=query"
    assert finished_spans[0].attributes.get(policy._SERVER_ADDRESS) == "localhost"
    assert finished_spans[0].attributes.get(policy._USER_AGENT_ORIGINAL) is None
    assert finished_spans[0].attributes.get(policy._HTTP_RESPONSE_STATUS_CODE) == 202
    assert finished_spans[0].attributes.get("custom_key") == "custom_value"


@pytest.mark.parametrize("http_response", HTTP_RESPONSES)
def test_distributed_tracing_policy_disabled(tracing_helper, http_response):
    """Test policy when tracing is enabled globally but disabled on the operation."""
    with tracing_helper.tracer.start_as_current_span("Root"):
        policy = DistributedHttpTracingPolicy()

        request = HttpRequest("GET", "http://localhost/temp?query=query")
        pipeline_request = PipelineRequest(request, PipelineContext(None))
        pipeline_request.context.options["tracing_options"] = {
            "enabled": False,
        }
        policy.on_request(pipeline_request)
        response = create_http_response(http_response, request, None, headers=request.headers)
        policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 1
    assert finished_spans[0].name == "Root"


def test_suppress_http_auto_instrumentation(port, tracing_helper):
    """Test that automatic HTTP instrumentation is suppressed when a request is made through the pipeline."""
    # Enable auto-instrumentation for requests.
    requests_instrumentor = RequestsInstrumentor()
    requests_instrumentor.instrument()
    policy = DistributedHttpTracingPolicy()
    transport = RequestsTransport()

    request = HttpRequest("GET", f"http://localhost:{port}/basic/string")
    with Pipeline(transport, policies=[policy]) as pipeline:
        pipeline.run(request)

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 1
    assert finished_spans[0].attributes.get(policy._HTTP_REQUEST_METHOD) == "GET"
    assert finished_spans[0].attributes.get(policy._URL_FULL) == f"http://localhost:{port}/basic/string"
    assert finished_spans[0].attributes.get(policy._SERVER_ADDRESS) == "localhost"
    assert finished_spans[0].attributes.get(policy._HTTP_RESPONSE_STATUS_CODE) == 200

    requests_instrumentor.uninstrument()
