# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the retry policy."""
import functools
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO
import pytest
from azure.core.configuration import ConnectionConfiguration
from azure.core.exceptions import (
    AzureError,
    ServiceRequestError,
    ServiceRequestTimeoutError,
    ServiceResponseError,
    ServiceResponseTimeoutError,
)
from azure.core.pipeline.policies import (
    RetryPolicy,
    RetryMode,
)
from azure.core.pipeline import Pipeline, PipelineResponse
from azure.core.pipeline.transport._base import SupportedFormat
from azure.core.pipeline.transport import (
    HttpRequest as PipelineTransportHttpRequest,
    HttpResponse as PipelineTransportHttpResponse,
    HttpTransport,
)
from azure.core.pipeline.transport._requests_basic import RestRequestsTransportResponse
from azure.core.rest import (
    HttpRequest as RestHttpRequest,
    HttpResponse as RestHttpResponse,
)
import tempfile
import os
import time

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from itertools import product

class MockInternalResponse(object):
    def __init__(self):
        self.status_code = 200
        self.headers = {}
        self.reason = "OK"
        self._content_consumed = True
        self.content = "hello"

    def close(self):
        pass

def test_retry_code_class_variables():
    retry_policy = RetryPolicy()
    assert retry_policy._RETRY_CODES is not None
    assert 408 in retry_policy._RETRY_CODES
    assert 429 in retry_policy._RETRY_CODES
    assert 501 not in retry_policy._RETRY_CODES

def test_retry_types():
    history = ["1", "2", "3"]
    settings = {
        'history': history,
        'backoff': 1,
        'max_backoff': 10
    }
    retry_policy = RetryPolicy()
    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 4

    retry_policy = RetryPolicy(retry_mode=RetryMode.Fixed)
    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 1

    retry_policy = RetryPolicy(retry_mode=RetryMode.Exponential)
    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 4

request_types = (PipelineTransportHttpRequest, RestHttpRequest)
response_types = (PipelineTransportHttpResponse, RestHttpResponse)
retry_after_inputs = ('0', '800', '1000', '1200')
full_combination = list(product(request_types, response_types, retry_after_inputs))

@pytest.mark.parametrize("request_type, response_type, retry_after_input", full_combination)
def test_retry_after(request_type, response_type, retry_after_input):
    retry_policy = RetryPolicy()
    request = request_type("GET", "https://bing.com")
    if hasattr(response_type, "content"):
        response = response_type(request=request, internal_response=None)
    else:
        response = response_type(request, None)
    response.headers["retry-after-ms"] = retry_after_input
    pipeline_response = PipelineResponse(request, response, None)
    retry_after = retry_policy.get_retry_after(pipeline_response)
    seconds = float(retry_after_input)
    assert retry_after == seconds/1000.0
    response.headers.pop("retry-after-ms")
    response.headers["Retry-After"] = retry_after_input
    retry_after = retry_policy.get_retry_after(pipeline_response)
    assert retry_after == float(retry_after_input)
    response.headers["retry-after-ms"] = 500
    retry_after = retry_policy.get_retry_after(pipeline_response)
    assert retry_after == float(retry_after_input)

@pytest.mark.parametrize("request_type, response_type, retry_after_input", full_combination)
def test_x_ms_retry_after(request_type, response_type, retry_after_input):
    retry_policy = RetryPolicy()
    request = request_type("GET", "https://bing.com")
    if hasattr(response_type, "content"):
        response = response_type(request=request, internal_response=None)
    else:
        response = response_type(request, None)
    response.headers["x-ms-retry-after-ms"] = retry_after_input
    pipeline_response = PipelineResponse(request, response, None)
    retry_after = retry_policy.get_retry_after(pipeline_response)
    seconds = float(retry_after_input)
    assert retry_after == seconds/1000.0
    response.headers.pop("x-ms-retry-after-ms")
    response.headers["Retry-After"] = retry_after_input
    retry_after = retry_policy.get_retry_after(pipeline_response)
    assert retry_after == float(retry_after_input)
    response.headers["x-ms-retry-after-ms"] = 500
    retry_after = retry_policy.get_retry_after(pipeline_response)
    assert retry_after == float(retry_after_input)

@pytest.mark.parametrize("request_type,response_type", [(PipelineTransportHttpRequest, PipelineTransportHttpResponse), (RestHttpRequest, RestRequestsTransportResponse)])
def test_retry_on_429(request_type, response_type):
    class MockTransport(HttpTransport):
        def __init__(self):
            self._count = 0
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def close(self):
            pass
        def open(self):
            pass

        @property
        def supported_formats(self):
            return [SupportedFormat.REST] if hasattr(response_type, "content") else [SupportedFormat.PIPELINE_TRANSPORT]

        def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            self._count += 1
            # only returning pipeline transport http responses, bc this is how the transport.sends return stuff
            response = PipelineTransportHttpResponse(request, None)
            response.status_code = 429
            if hasattr(response_type, "content"):
                response.internal_response = MockInternalResponse()
            return response

    http_request = request_type('GET', 'http://127.0.0.1/')
    http_retry = RetryPolicy(retry_total = 1)
    transport = MockTransport()
    pipeline = Pipeline(transport, [http_retry])
    pipeline.run(http_request)
    assert transport._count == 2

@pytest.mark.parametrize("request_type,response_type", [(PipelineTransportHttpRequest, PipelineTransportHttpResponse), (RestHttpRequest, RestRequestsTransportResponse)])
def test_no_retry_on_201(request_type, response_type):
    class MockTransport(HttpTransport):
        def __init__(self):
            self._count = 0
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def close(self):
            pass
        def open(self):
            pass

        @property
        def supported_formats(self):
            return [SupportedFormat.REST] if hasattr(response_type, "content") else [SupportedFormat.PIPELINE_TRANSPORT]

        def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            self._count += 1
            # in the transport, we keep it just pipelien transport
            response = PipelineTransportHttpResponse(request, None)
            if hasattr(response_type, "content"):
                # when transforming the pipelien transport to rest later, we need an internal response
                response.internal_response = MockInternalResponse()
            response.status_code = 201
            headers = {"Retry-After": "1"}
            response.headers = headers
            return response

    http_request = request_type('GET', 'http://127.0.0.1/')
    http_retry = RetryPolicy(retry_total = 1)
    transport = MockTransport()
    pipeline = Pipeline(transport, [http_retry])
    pipeline.run(http_request)
    assert transport._count == 1

@pytest.mark.parametrize("request_type,response_type", [(PipelineTransportHttpRequest, PipelineTransportHttpResponse), (RestHttpRequest, RestRequestsTransportResponse)])
def test_retry_seekable_stream(request_type, response_type):
    class MockTransport(HttpTransport):
        def __init__(self):
            self._first = True
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def close(self):
            pass
        def open(self):
            pass

        def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            if self._first:
                self._first = False
                request.body.seek(0,2)
                raise AzureError('fail on first')
            position = request.body.tell()
            assert position == 0
            response = PipelineTransportHttpResponse(request, None)
            if hasattr(response_type, "content"):
                response.internal_response = MockInternalResponse()

            response.status_code = 400
            return response

        @property
        def supported_formats(self):
            return [SupportedFormat.REST] if hasattr(response_type, "content") else [SupportedFormat.PIPELINE_TRANSPORT]

    data = BytesIO(b"Lots of dataaaa")
    if hasattr(request_type, "content"):
        http_request = request_type('GET', 'http://127.0.0.1/', content=data)
    else:
        http_request = request_type('GET', 'http://127.0.0.1/')
        http_request.set_streamed_data_body(data)
    http_retry = RetryPolicy(retry_total = 1)
    pipeline = Pipeline(MockTransport(), [http_retry])
    pipeline.run(http_request)

@pytest.mark.parametrize("request_type,response_type", [(PipelineTransportHttpRequest, PipelineTransportHttpResponse), (RestHttpRequest, RestRequestsTransportResponse)])
def test_retry_seekable_file(request_type, response_type):
    class MockTransport(HttpTransport):
        def __init__(self):
            self._first = True
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def close(self):
            pass
        def open(self):
            pass

        @property
        def supported_formats(self):
            return [SupportedFormat.REST] if hasattr(response_type, "content") else [SupportedFormat.PIPELINE_TRANSPORT]

        def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            if self._first:
                self._first = False
                for value in request.files.values():
                    name, body = value[0], value[1]
                    if name and body and hasattr(body, 'read'):
                        body.seek(0,2)
                        raise AzureError('fail on first')
            for value in request.files.values():
                name, body = value[0], value[1]
                if name and body and hasattr(body, 'read'):
                    position = body.tell()
                    assert not position
                    response = PipelineTransportHttpResponse(request, None)
                    response.status_code = 400
                    if hasattr(response_type, "content"):
                        response.internal_response = MockInternalResponse()
                    return response

    file = tempfile.NamedTemporaryFile(delete=False)
    file.write(b'Lots of dataaaa')
    file.close()

    headers = {'Content-Type': "multipart/form-data"}
    with open(file.name, 'rb') as f:
        form_data_content = {
            'fileContent': f,
            'fileName': f.name,
        }
        if hasattr(request_type, "content"):
            http_request = request_type('GET', 'http://127.0.0.1/', headers=headers, files=form_data_content)
        else:
            http_request = request_type('GET', 'http://127.0.0.1/', headers=headers)
            http_request.set_formdata_body(form_data_content)
        http_retry = RetryPolicy(retry_total=1)
        pipeline = Pipeline(MockTransport(), [http_retry])
        pipeline.run(http_request)
    os.unlink(f.name)


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_retry_timeout(request_type, add_supported_format_rest_to_mock):
    timeout = 1

    def send(request, **kwargs):
        assert kwargs["connection_timeout"] <= timeout, "policy should set connection_timeout not to exceed timeout"
        raise ServiceResponseError("oops")

    transport = Mock(
        spec=HttpTransport,
        send=Mock(wraps=send),
        connection_config=ConnectionConfiguration(connection_timeout=timeout * 2),
        sleep=time.sleep,
    )
    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport, [RetryPolicy(timeout=timeout)])

    with pytest.raises(ServiceResponseTimeoutError):
        response = pipeline.run(request_type("GET", "http://127.0.0.1/"))


@pytest.mark.parametrize("request_type,response_type", [(PipelineTransportHttpRequest, PipelineTransportHttpResponse), (RestHttpRequest, RestHttpResponse)])
def test_timeout_defaults(request_type, response_type, add_supported_format_rest_to_mock):
    """When "timeout" is not set, the policy should not override the transport's timeout configuration"""

    def send(request, **kwargs):
        for arg in ("connection_timeout", "read_timeout"):
            assert arg not in kwargs, "policy should defer to transport configuration when not given a timeout"
        # transport send just deals with PipelineTransportHttpResponses
        response = PipelineTransportHttpResponse(request, None)
        response.status_code = 200
        return response


    transport = Mock(
        spec_set=HttpTransport,
        send=Mock(wraps=send),
        sleep=Mock(side_effect=Exception("policy should not sleep: its first send succeeded")),
    )
    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport, [RetryPolicy()])

    pipeline.run(request_type("GET", "http://127.0.0.1/"))
    assert transport.send.call_count == 1, "policy should not retry: its first send succeeded"


@pytest.mark.parametrize(
    "transport_error,expected_timeout_error",
    ((ServiceRequestError, ServiceRequestTimeoutError), (ServiceResponseError, ServiceResponseTimeoutError)),
)
def test_does_not_sleep_after_timeout_pipeline_transport(transport_error, expected_timeout_error, add_supported_format_rest_to_mock):
    # With default settings policy will sleep twice before exhausting its retries: 1.6s, 3.2s.
    # It should not sleep the second time when given timeout=1
    timeout = 1

    transport = Mock(
        spec=HttpTransport,
        send=Mock(side_effect=transport_error("oops")),
        sleep=Mock(wraps=time.sleep),
    )
    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport, [RetryPolicy(timeout=timeout)])

    with pytest.raises(expected_timeout_error):
        pipeline.run(PipelineTransportHttpRequest("GET", "http://127.0.0.1/"))

    assert transport.sleep.call_count == 1

@pytest.mark.parametrize(
    "transport_error,expected_timeout_error",
    ((ServiceRequestError, ServiceRequestTimeoutError), (ServiceResponseError, ServiceResponseTimeoutError)),
)
def test_does_not_sleep_after_timeout_rest(transport_error, expected_timeout_error, add_supported_format_rest_to_mock):
    # With default settings policy will sleep twice before exhausting its retries: 1.6s, 3.2s.
    # It should not sleep the second time when given timeout=1
    timeout = 1

    transport = Mock(
        spec=HttpTransport,
        send=Mock(side_effect=transport_error("oops")),
        sleep=Mock(wraps=time.sleep),
    )
    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport, [RetryPolicy(timeout=timeout)])

    with pytest.raises(expected_timeout_error):
        pipeline.run(RestHttpRequest("GET", "http://127.0.0.1/"))

    assert transport.sleep.call_count == 1

