# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the distributed tracing policy."""
import logging

from azure.core.pipeline import PipelineResponse, PipelineRequest, PipelineContext
from azure.core.pipeline.policies import DistributedTracingPolicy, UserAgentPolicy
from azure.core.pipeline.transport import HttpRequest, HttpResponse
from azure.core.settings import settings
from tracing_common import FakeSpan
import time
import pytest

try:
    from unittest import mock
except ImportError:
    import mock


def test_distributed_tracing_policy_solo():
    """Test policy with no other policy and happy path"""
    settings.tracing_implementation.set_value(FakeSpan)
    with FakeSpan(name="parent") as root_span:
        policy = DistributedTracingPolicy()

        request = HttpRequest("GET", "http://127.0.0.1/temp?query=query")
        request.headers["x-ms-client-request-id"] = "some client request id"

        pipeline_request = PipelineRequest(request, PipelineContext(None))
        policy.on_request(pipeline_request)

        response = HttpResponse(request, None)
        response.headers = request.headers
        response.status_code = 202
        response.headers["x-ms-request-id"] = "some request id"

        assert request.headers.get("traceparent") == '123456789'

        policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))
        time.sleep(0.001)
        policy.on_request(pipeline_request)
        try:
            raise ValueError("Transport trouble")
        except:
            policy.on_exception(pipeline_request)

    # Check on_response
    network_span = root_span.children[0]
    assert network_span.name == "/temp"
    assert network_span.attributes.get("http.method") == "GET"
    assert network_span.attributes.get("component") == "http"
    assert network_span.attributes.get("http.url") == "http://127.0.0.1/temp?query=query"
    assert network_span.attributes.get("http.user_agent") is None
    assert network_span.attributes.get("x-ms-request-id") == "some request id"
    assert network_span.attributes.get("x-ms-client-request-id") == "some client request id"
    assert network_span.attributes.get("http.status_code") == 202

    # Check on_exception
    network_span = root_span.children[1]
    assert network_span.name == "/temp"
    assert network_span.attributes.get("http.method") == "GET"
    assert network_span.attributes.get("component") == "http"
    assert network_span.attributes.get("http.url") == "http://127.0.0.1/temp?query=query"
    assert network_span.attributes.get("x-ms-client-request-id") == "some client request id"
    assert network_span.attributes.get("http.user_agent") is None
    assert network_span.attributes.get("x-ms-request-id") == None
    assert network_span.attributes.get("http.status_code") == 504


def test_distributed_tracing_policy_attributes():
    """Test policy with no other policy and happy path"""
    settings.tracing_implementation.set_value(FakeSpan)
    with FakeSpan(name="parent") as root_span:
        policy = DistributedTracingPolicy(tracing_attributes={
            'myattr': 'myvalue'
        })

        request = HttpRequest("GET", "http://127.0.0.1/temp?query=query")

        pipeline_request = PipelineRequest(request, PipelineContext(None))
        policy.on_request(pipeline_request)

        response = HttpResponse(request, None)
        response.headers = request.headers
        response.status_code = 202

        policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

    # Check on_response
    network_span = root_span.children[0]
    assert network_span.attributes.get("myattr") == "myvalue"


def test_distributed_tracing_policy_badurl(caplog):
    """Test policy with a bad url that will throw, and be sure policy ignores it"""
    settings.tracing_implementation.set_value(FakeSpan)
    with FakeSpan(name="parent") as root_span:
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

        assert request.headers.get("traceparent") is None  # Got not network trace

        policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))
        time.sleep(0.001)

        policy.on_request(pipeline_request)
        try:
            raise ValueError("Transport trouble")
        except:
            policy.on_exception(pipeline_request)

    assert len(root_span.children) == 0


def test_distributed_tracing_policy_with_user_agent():
    """Test policy working with user agent."""
    settings.tracing_implementation.set_value(FakeSpan)
    with mock.patch.dict('os.environ', {"AZURE_HTTP_USER_AGENT": "mytools"}):
        with FakeSpan(name="parent") as root_span:
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

            assert request.headers.get("traceparent") == '123456789'

            policy.on_response(pipeline_request, pipeline_response)

            time.sleep(0.001)
            policy.on_request(pipeline_request)
            try:
                raise ValueError("Transport trouble")
            except:
                policy.on_exception(pipeline_request)

            user_agent.on_response(pipeline_request, pipeline_response)

        network_span = root_span.children[0]
        assert network_span.name == "/"
        assert network_span.attributes.get("http.method") == "GET"
        assert network_span.attributes.get("component") == "http"
        assert network_span.attributes.get("http.url") == "http://127.0.0.1"
        assert network_span.attributes.get("http.user_agent").endswith("mytools")
        assert network_span.attributes.get("x-ms-request-id") == "some request id"
        assert network_span.attributes.get("x-ms-client-request-id") == "some client request id"
        assert network_span.attributes.get("http.status_code") == 202

        network_span = root_span.children[1]
        assert network_span.name == "/"
        assert network_span.attributes.get("http.method") == "GET"
        assert network_span.attributes.get("component") == "http"
        assert network_span.attributes.get("http.url") == "http://127.0.0.1"
        assert network_span.attributes.get("http.user_agent").endswith("mytools")
        assert network_span.attributes.get("x-ms-client-request-id") == "some client request id"
        assert network_span.attributes.get("x-ms-request-id") is None
        assert network_span.attributes.get("http.status_code") == 504
        # Exception should propagate status for Opencensus
        assert network_span.status == 'Transport trouble'


def test_span_namer():
    settings.tracing_implementation.set_value(FakeSpan)
    with FakeSpan(name="parent") as root_span:

        request = HttpRequest("GET", "http://127.0.0.1/temp?query=query")
        pipeline_request = PipelineRequest(request, PipelineContext(None))

        def fixed_namer(http_request):
            assert http_request is request
            return "overridenname"

        policy = DistributedTracingPolicy(network_span_namer=fixed_namer)

        policy.on_request(pipeline_request)

        response = HttpResponse(request, None)
        response.headers = request.headers
        response.status_code = 202

        policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

        def operation_namer(http_request):
            assert http_request is request
            return "operation level name"

        pipeline_request.context.options['network_span_namer'] = operation_namer

        policy.on_request(pipeline_request)

        response = HttpResponse(request, None)
        response.headers = request.headers
        response.status_code = 202

        policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

    # Check init kwargs
    network_span = root_span.children[0]
    assert network_span.name == "overridenname"

    # Check operation kwargs
    network_span = root_span.children[1]
    assert network_span.name == "operation level name"
