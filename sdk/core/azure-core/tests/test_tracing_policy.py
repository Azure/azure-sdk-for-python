# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the distributed tracing policy."""
import logging
import time
import urllib
from unittest import mock

from azure.core.pipeline import Pipeline, PipelineResponse, PipelineRequest, PipelineContext
from azure.core.pipeline.policies import DistributedTracingPolicy, UserAgentPolicy, RetryPolicy
from azure.core.pipeline.transport import HttpTransport, RequestsTransport
from azure.core.settings import settings
from azure.core.tracing._models import SpanKind
from azure.core.tracing._abstract_span import HttpSpanMixin
import pytest
from opentelemetry.trace import format_span_id, format_trace_id
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from utils import HTTP_RESPONSES, HTTP_REQUESTS, create_http_response, request_and_responses_product
from tracing_common import FakeSpan


class TestTracingPolicyPluginImplementation:

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_solo(self, tracing_implementation, http_request, http_response):
        """Test policy with no other policy and happy path"""
        with FakeSpan(name="parent") as root_span:
            policy = DistributedTracingPolicy()

            request = http_request("GET", "http://localhost/temp?query=query")
            request.headers[policy._REQUEST_ID] = "some client request id"

            pipeline_request = PipelineRequest(request, PipelineContext(None))
            policy.on_request(pipeline_request)

            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 202
            response.headers[policy._RESPONSE_ID] = "some request id"

            assert request.headers.get("traceparent") == "00-12345-GET-01"

            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))
            time.sleep(0.001)
            policy.on_request(pipeline_request)
            try:
                raise ValueError("Transport trouble")
            except:
                policy.on_exception(pipeline_request)

        # Check on_response
        network_span = root_span.children[0]
        assert network_span.name == "GET"
        assert network_span.attributes.get(HttpSpanMixin._HTTP_METHOD) == "GET"
        assert network_span.attributes.get(HttpSpanMixin._HTTP_URL) == "http://localhost/temp?query=query"
        assert network_span.attributes.get(HttpSpanMixin._NET_PEER_NAME) == "localhost"
        assert network_span.attributes.get(HttpSpanMixin._HTTP_USER_AGENT) is None
        assert network_span.attributes.get(policy._RESPONSE_ID_ATTR) == "some request id"
        assert network_span.attributes.get(policy._REQUEST_ID_ATTR) == "some client request id"
        assert network_span.attributes.get(HttpSpanMixin._HTTP_STATUS_CODE) == 202
        assert policy._ERROR_TYPE not in network_span.attributes

        # Check on_exception
        network_span = root_span.children[1]
        assert network_span.name == "GET"
        assert network_span.attributes.get(HttpSpanMixin._HTTP_METHOD) == "GET"
        assert network_span.attributes.get(HttpSpanMixin._HTTP_URL) == "http://localhost/temp?query=query"
        assert network_span.attributes.get(policy._REQUEST_ID_ATTR) == "some client request id"
        assert network_span.attributes.get(HttpSpanMixin._HTTP_USER_AGENT) is None
        assert network_span.attributes.get(policy._RESPONSE_ID_ATTR) == None
        assert network_span.attributes.get(HttpSpanMixin._HTTP_STATUS_CODE) == 504
        assert network_span.attributes.get(policy._ERROR_TYPE)

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_error_response(self, tracing_implementation, http_request, http_response):
        """Test policy when the HTTP response corresponds to an error."""
        with FakeSpan(name="parent") as root_span:
            policy = DistributedTracingPolicy(tracing_attributes={"myattr": "myvalue"})

            request = http_request("GET", "http://localhost/temp?query=query")

            pipeline_request = PipelineRequest(request, PipelineContext(None))
            policy.on_request(pipeline_request)

            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 403

            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))
            network_span = root_span.children[0]
            assert network_span.name == "GET"
            assert network_span.attributes.get(policy._ERROR_TYPE) == "403"

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_attributes(self, tracing_implementation, http_request, http_response):
        """Test policy with no other policy and happy path"""
        with FakeSpan(name="parent") as root_span:
            policy = DistributedTracingPolicy(tracing_attributes={"myattr": "myvalue"})

            request = http_request("GET", "http://localhost/temp?query=query")

            pipeline_request = PipelineRequest(request, PipelineContext(None))
            policy.on_request(pipeline_request)

            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 202

            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

        # Check on_response
        network_span = root_span.children[0]
        assert network_span.attributes.get("myattr") == "myvalue"

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_attributes_per_operation(
        self, tracing_implementation, http_request, http_response
    ):
        """Test policy with no other policy and happy path"""
        with FakeSpan(name="parent") as root_span:
            policy = DistributedTracingPolicy(tracing_attributes={"myattr": "myvalue"})

            request = http_request("GET", "http://localhost/temp?query=query")

            pipeline_request = PipelineRequest(request, PipelineContext(None, tracing_attributes={"foo": "bar"}))
            policy.on_request(pipeline_request)

            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 202

            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

        # Check on_response
        network_span = root_span.children[0]
        assert network_span.attributes.get("foo") == "bar"

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_exception(self, caplog, tracing_implementation, http_request, http_response):
        """Test policy with an exception during on_request before span is created, and be sure policy ignores it"""

        def bad_namer(http_request):
            path = urllib.parse.urlparse(http_request.url).path
            return f"{http_request.method} {path}"

        with FakeSpan(name="parent") as root_span:
            # Force an exception before the network span is created with invalid URL parsing.
            policy = DistributedTracingPolicy(network_span_namer=bad_namer)

            request = http_request("GET", "http://[[[")
            request.headers[policy._REQUEST_ID] = "some client request id"

            pipeline_request = PipelineRequest(request, PipelineContext(None))
            with caplog.at_level(logging.WARNING, logger="azure.core.pipeline.policies.distributed_tracing"):
                policy.on_request(pipeline_request)
            assert "Unable to start network span" in caplog.text

            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 202
            response.headers[policy._RESPONSE_ID] = "some request id"

            assert request.headers.get("traceparent") is None  # Got not network trace

            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))
            time.sleep(0.001)

            policy.on_request(pipeline_request)
            try:
                raise ValueError("Transport trouble")
            except:
                policy.on_exception(pipeline_request)

        assert len(root_span.children) == 0

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_with_user_agent(self, tracing_implementation, http_request, http_response):
        """Test policy working with user agent."""
        with mock.patch.dict("os.environ", {"AZURE_HTTP_USER_AGENT": "mytools"}):
            with FakeSpan(name="parent") as root_span:
                policy = DistributedTracingPolicy()

                request = http_request("GET", "http://localhost")
                request.headers[policy._REQUEST_ID] = "some client request id"

                pipeline_request = PipelineRequest(request, PipelineContext(None))

                user_agent = UserAgentPolicy()
                user_agent.on_request(pipeline_request)
                policy.on_request(pipeline_request)

                response = create_http_response(http_response, request, None)
                response.headers = request.headers
                response.status_code = 202
                response.headers[policy._RESPONSE_ID] = "some request id"
                pipeline_response = PipelineResponse(request, response, PipelineContext(None))

                assert request.headers.get("traceparent") == "00-12345-GET-01"

                policy.on_response(pipeline_request, pipeline_response)

                time.sleep(0.001)
                policy.on_request(pipeline_request)
                try:
                    raise ValueError("Transport trouble")
                except:
                    policy.on_exception(pipeline_request)

                user_agent.on_response(pipeline_request, pipeline_response)

            network_span = root_span.children[0]
            assert network_span.name == "GET"
            assert network_span.attributes.get(HttpSpanMixin._HTTP_METHOD) == "GET"
            assert network_span.attributes.get(HttpSpanMixin._HTTP_URL) == "http://localhost"
            assert network_span.attributes.get(HttpSpanMixin._HTTP_USER_AGENT).endswith("mytools")
            assert network_span.attributes.get(policy._RESPONSE_ID_ATTR) == "some request id"
            assert network_span.attributes.get(policy._REQUEST_ID_ATTR) == "some client request id"
            assert network_span.attributes.get(HttpSpanMixin._HTTP_STATUS_CODE) == 202

            network_span = root_span.children[1]
            assert network_span.name == "GET"
            assert network_span.attributes.get(HttpSpanMixin._HTTP_METHOD) == "GET"
            assert network_span.attributes.get(HttpSpanMixin._HTTP_URL) == "http://localhost"
            assert network_span.attributes.get(HttpSpanMixin._HTTP_USER_AGENT).endswith("mytools")
            assert network_span.attributes.get(policy._REQUEST_ID_ATTR) == "some client request id"
            assert network_span.attributes.get(policy._RESPONSE_ID_ATTR) is None
            assert network_span.attributes.get(HttpSpanMixin._HTTP_STATUS_CODE) == 504
            # Exception should propagate status for Opencensus
            assert network_span.status == "Transport trouble"

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_span_retry_attributes(self, tracing_implementation, http_request, http_response):
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
                response = create_http_response(http_response, request, None)
                response.status_code = 429
                return response

        http_request = http_request("GET", "http://localhost/")
        retry_policy = RetryPolicy(retry_total=2)
        distributed_tracing_policy = DistributedTracingPolicy()
        transport = MockTransport()

        with FakeSpan(name="parent") as root_span:
            pipeline = Pipeline(transport, [retry_policy, distributed_tracing_policy])
            pipeline.run(http_request)
        assert transport._count == 3
        assert len(root_span.children) == 3
        assert root_span.children[0].attributes.get("http.request.resend_count") is None
        assert root_span.children[1].attributes.get("http.request.resend_count") == 1
        assert root_span.children[2].attributes.get("http.request.resend_count") == 2

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_span_namer(self, tracing_implementation, http_request, http_response):
        with FakeSpan(name="parent") as root_span:

            request = http_request("GET", "http://localhost/temp?query=query")
            pipeline_request = PipelineRequest(request, PipelineContext(None))

            def fixed_namer(http_request):
                assert http_request is request
                return "overriddenname"

            policy = DistributedTracingPolicy(network_span_namer=fixed_namer)

            policy.on_request(pipeline_request)

            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 202

            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

            def operation_namer(http_request):
                assert http_request is request
                return "operation level name"

            pipeline_request.context.options["network_span_namer"] = operation_namer

            policy.on_request(pipeline_request)

            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 202

            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

        # Check init kwargs
        network_span = root_span.children[0]
        assert network_span.name == "overriddenname"

        # Check operation kwargs
        network_span = root_span.children[1]
        assert network_span.name == "operation level name"

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_with_tracing_options(self, tracing_implementation, http_request, http_response):
        """Test policy when tracing options are provided."""
        settings.tracing_enabled = False
        with FakeSpan(name="parent") as root_span:
            policy = DistributedTracingPolicy()

            request = http_request("GET", "http://localhost/temp?query=query")
            pipeline_request = PipelineRequest(request, PipelineContext(None))
            pipeline_request.context.options["tracing_options"] = {
                "enabled": True,
                "attributes": {"custom_key": "custom_value"},
            }

            policy.on_request(pipeline_request)
            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 202
            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

        assert len(root_span.children) == 1
        network_span = root_span.children[0]
        assert network_span.attributes.get("custom_key") == "custom_value"

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_with_tracing_disabled(
        self, tracing_implementation, http_request, http_response
    ):
        """Test policy when tracing is disabled through user options."""
        with FakeSpan(name="parent") as root_span:
            policy = DistributedTracingPolicy()

            request = http_request("GET", "http://localhost/temp?query=query")
            pipeline_request = PipelineRequest(request, PipelineContext(None))
            pipeline_request.context.options["tracing_options"] = {"enabled": False}

            policy.on_request(pipeline_request)
            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 202
            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

        assert len(root_span.children) == 0


class TestTracingPolicyNativeTracing:
    """Test the distributed tracing policy with the native core tracer."""

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy(self, tracing_helper, http_request, http_response):
        """Test policy when the HTTP response corresponds to a success."""
        with tracing_helper.tracer.start_as_current_span("Root") as root_span:
            policy = DistributedTracingPolicy()

            request = http_request("GET", "http://localhost/temp?query=query")
            pipeline_request = PipelineRequest(request, PipelineContext(None))
            policy.on_request(pipeline_request)

            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 202

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

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_error_response(self, tracing_helper, http_request, http_response):
        """Test policy when the HTTP response corresponds to an error."""
        with tracing_helper.tracer.start_as_current_span("Root"):
            policy = DistributedTracingPolicy()

            request = http_request("GET", "http://localhost/temp?query=query")
            pipeline_request = PipelineRequest(request, PipelineContext(None))
            policy.on_request(pipeline_request)

            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 403

            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

        finished_spans = tracing_helper.exporter.get_finished_spans()
        assert finished_spans[0].name == "GET"
        assert finished_spans[0].attributes.get("error.type") == "403"

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_custom_instrumentation_config(
        self, tracing_helper, http_request, http_response
    ):
        """Test policy when a custom tracer provider is provided."""
        config = {
            "library_name": "my-library",
            "library_version": "1.0.0",
            "attributes": {"az.namespace": "Sample.Namespace"},
        }

        with tracing_helper.tracer.start_as_current_span("Root"):
            policy = DistributedTracingPolicy(instrumentation_config=config)

            request = http_request("GET", "http://localhost/temp?query=query")
            pipeline_request = PipelineRequest(request, PipelineContext(None))
            policy.on_request(pipeline_request)

            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 403

            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

        finished_spans = tracing_helper.exporter.get_finished_spans()
        assert finished_spans[0].name == "GET"
        assert finished_spans[0].attributes.get(policy._ERROR_TYPE) == "403"
        assert finished_spans[0].instrumentation_scope.name == "my-library"
        assert finished_spans[0].instrumentation_scope.version == "1.0.0"
        assert finished_spans[0].instrumentation_scope.attributes.get("az.namespace") == "Sample.Namespace"

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_exception(self, caplog, tracing_helper, http_request, http_response):
        """Test policy with an exception during on_request before span is created, and be sure policy ignores it."""

        def bad_namer(http_request):
            path = urllib.parse.urlparse(http_request.url).path
            return f"{http_request.method} {path}"

        with tracing_helper.tracer.start_as_current_span("Root"):
            policy = DistributedTracingPolicy(network_span_namer=bad_namer)

            request = http_request("GET", "http://[[[")
            pipeline_request = PipelineRequest(request, PipelineContext(None))
            with caplog.at_level(logging.WARNING, logger="azure.core.pipeline.policies.distributed_tracing"):
                policy.on_request(pipeline_request)
            assert "Unable to start network span" in caplog.text

            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 403

            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

        # A span for the request should not have been created.
        finished_spans = tracing_helper.exporter.get_finished_spans()
        assert len(finished_spans) == 1
        assert finished_spans[0].name == "Root"

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_with_user_agent_policy(self, tracing_helper, http_request, http_response):
        """Test policy when used with the UserAgentPolicy."""
        with mock.patch.dict("os.environ", {"AZURE_HTTP_USER_AGENT": "test-user-agent"}):
            with tracing_helper.tracer.start_as_current_span("Root") as root_span:
                policy = DistributedTracingPolicy()
                user_agent_policy = UserAgentPolicy()

                request = http_request("GET", "http://localhost/temp?query=query")
                pipeline_request = PipelineRequest(request, PipelineContext(None))
                user_agent_policy.on_request(pipeline_request)
                policy.on_request(pipeline_request)

                response = create_http_response(http_response, request, None)
                response.headers = request.headers
                response.status_code = 202

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

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_span_retry_attributes(self, tracing_helper, http_request, http_response):
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
                response = create_http_response(http_response, request, None)
                response.status_code = 429
                return response

        http_request = http_request("GET", "http://localhost/")
        retry_policy = RetryPolicy(retry_total=2)
        distributed_tracing_policy = DistributedTracingPolicy()
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

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_with_tracing_options(self, tracing_helper, http_request, http_response):
        """Test policy when tracing options are provided."""
        settings.tracing_enabled = False
        with tracing_helper.tracer.start_as_current_span("Root") as root_span:
            policy = DistributedTracingPolicy()

            request = http_request("GET", "http://localhost/temp?query=query")
            pipeline_request = PipelineRequest(request, PipelineContext(None))
            pipeline_request.context.options["tracing_options"] = {
                "enabled": True,
                "attributes": {"custom_key": "custom_value"},
            }

            policy.on_request(pipeline_request)
            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 202
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

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_distributed_tracing_policy_disabled(self, tracing_helper, http_request, http_response):
        """Test policy when tracing is enabled globally but disabled on the operation."""
        with tracing_helper.tracer.start_as_current_span("Root"):
            policy = DistributedTracingPolicy()

            request = http_request("GET", "http://localhost/temp?query=query")
            pipeline_request = PipelineRequest(request, PipelineContext(None))
            pipeline_request.context.options["tracing_options"] = {
                "enabled": False,
            }
            policy.on_request(pipeline_request)
            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

        finished_spans = tracing_helper.exporter.get_finished_spans()
        assert len(finished_spans) == 1
        assert finished_spans[0].name == "Root"

    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    def test_suppress_http_auto_instrumentation(self, port, tracing_helper, http_request):
        """Test that automatic HTTP instrumentation is suppressed when a request is made through the pipeline."""
        # Enable auto-instrumentation for requests.
        requests_instrumentor = RequestsInstrumentor()
        requests_instrumentor.instrument()
        policy = DistributedTracingPolicy()
        transport = RequestsTransport()

        request = http_request("GET", f"http://localhost:{port}/basic/string")
        with Pipeline(transport, policies=[policy]) as pipeline:
            pipeline.run(request)

        finished_spans = tracing_helper.exporter.get_finished_spans()
        assert len(finished_spans) == 1
        assert finished_spans[0].attributes.get(policy._HTTP_REQUEST_METHOD) == "GET"
        assert finished_spans[0].attributes.get(policy._URL_FULL) == f"http://localhost:{port}/basic/string"
        assert finished_spans[0].attributes.get(policy._SERVER_ADDRESS) == "localhost"
        assert finished_spans[0].attributes.get(policy._HTTP_RESPONSE_STATUS_CODE) == 200

        requests_instrumentor.uninstrument()

    @pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
    def test_tracing_impl_takes_precedence(self, tracing_implementation, http_request, http_response):
        """Test that a tracing implementation takes precedence over the native tracing."""
        settings.tracing_enabled = True

        assert settings.tracing_implementation() is FakeSpan
        assert settings.tracing_enabled

        with FakeSpan(name="parent") as root_span:
            policy = DistributedTracingPolicy()

            request = http_request("GET", "http://localhost/temp?query=query")

            pipeline_request = PipelineRequest(request, PipelineContext(None))
            policy.on_request(pipeline_request)

            response = create_http_response(http_response, request, None)
            response.headers = request.headers
            response.status_code = 202

            policy.on_response(pipeline_request, PipelineResponse(request, response, PipelineContext(None)))

        assert len(root_span.children) == 1
        network_span = root_span.children[0]
        assert network_span.name == "GET"
        assert network_span.kind == SpanKind.CLIENT
