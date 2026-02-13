# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the retry policy."""
import random

try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO
import pytest
from itertools import product
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
from azure.core.pipeline.transport import (
    HttpTransport,
)
import tempfile
import os
import time

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from utils import HTTP_REQUESTS, request_and_responses_product, HTTP_RESPONSES, create_http_response


def test_retry_code_class_variables():
    retry_policy = RetryPolicy()
    assert retry_policy._RETRY_CODES is not None
    assert 408 in retry_policy._RETRY_CODES
    assert 429 in retry_policy._RETRY_CODES
    assert 501 not in retry_policy._RETRY_CODES


def test_retry_types():
    # With this history, the backoff without jitter would be 4
    history = ["1", "2", "3"]
    settings = {"history": history, "backoff": 1, "max_backoff": 10, "jitter": 0.0}
    retry_policy = RetryPolicy()
    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 4

    retry_policy = RetryPolicy(retry_mode=RetryMode.Fixed)
    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 1

    retry_policy = RetryPolicy(retry_mode=RetryMode.Exponential)
    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 4


@pytest.mark.parametrize(
    "retry_after_input,http_request,http_response",
    product(["0", "800", "1000", "1200", "0.9"], HTTP_REQUESTS, HTTP_RESPONSES),
)
def test_retry_after(retry_after_input, http_request, http_response):
    retry_policy = RetryPolicy()
    request = http_request("GET", "http://localhost")
    response = create_http_response(http_response, request, None)
    response.headers["retry-after-ms"] = retry_after_input
    pipeline_response = PipelineResponse(request, response, None)
    retry_after = retry_policy.get_retry_after(pipeline_response)
    seconds = float(retry_after_input)
    assert retry_after == seconds / 1000.0
    response.headers.pop("retry-after-ms")
    response.headers["Retry-After"] = retry_after_input
    retry_after = retry_policy.get_retry_after(pipeline_response)
    assert retry_after == float(retry_after_input)
    response.headers["retry-after-ms"] = 500
    retry_after = retry_policy.get_retry_after(pipeline_response)
    assert retry_after == float(retry_after_input)


@pytest.mark.parametrize(
    "retry_after_input,http_request,http_response",
    product(["0", "800", "1000", "1200", "0.9"], HTTP_REQUESTS, HTTP_RESPONSES),
)
def test_x_ms_retry_after(retry_after_input, http_request, http_response):
    retry_policy = RetryPolicy()
    request = http_request("GET", "http://localhost")
    response = create_http_response(http_response, request, None)
    response.headers["x-ms-retry-after-ms"] = retry_after_input
    pipeline_response = PipelineResponse(request, response, None)
    retry_after = retry_policy.get_retry_after(pipeline_response)
    seconds = float(retry_after_input)
    assert retry_after == seconds / 1000.0
    response.headers.pop("x-ms-retry-after-ms")
    response.headers["Retry-After"] = retry_after_input
    retry_after = retry_policy.get_retry_after(pipeline_response)
    assert retry_after == float(retry_after_input)
    response.headers["x-ms-retry-after-ms"] = 500
    retry_after = retry_policy.get_retry_after(pipeline_response)
    assert retry_after == float(retry_after_input)


@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_retry_on_429(http_request, http_response):
    class MockTransport(HttpTransport):
        def __init__(self):
            self._count = 0

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def close(self):
            pass

        def open(self):
            pass

        def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            self._count += 1
            response = create_http_response(http_response, request, None)
            response.status_code = 429
            return response

    http_request = http_request("GET", "http://localhost/")
    http_retry = RetryPolicy(retry_total=1)
    transport = MockTransport()
    pipeline = Pipeline(transport, [http_retry])
    pipeline.run(http_request)
    assert transport._count == 2


@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_no_retry_on_201(http_request, http_response):
    class MockTransport(HttpTransport):
        def __init__(self):
            self._count = 0

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def close(self):
            pass

        def open(self):
            pass

        def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            self._count += 1
            response = create_http_response(http_response, request, None)
            response.status_code = 201
            headers = {"Retry-After": "1"}
            response.headers = headers
            return response

    http_request = http_request("GET", "http://localhost/")
    http_retry = RetryPolicy(retry_total=1)
    transport = MockTransport()
    pipeline = Pipeline(transport, [http_retry])
    pipeline.run(http_request)
    assert transport._count == 1


@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_retry_seekable_stream(http_request, http_response):
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
                request.body.seek(0, 2)
                raise AzureError("fail on first")
            position = request.body.tell()
            assert position == 0
            response = create_http_response(http_response, request, None)
            response.status_code = 400
            return response

    data = BytesIO(b"Lots of dataaaa")
    http_request = http_request("GET", "http://localhost/")
    http_request.set_streamed_data_body(data)
    http_retry = RetryPolicy(retry_total=1)
    pipeline = Pipeline(MockTransport(), [http_retry])
    pipeline.run(http_request)


@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_retry_seekable_file(http_request, http_response):
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
                for value in request.files.values():
                    name, body = value[0], value[1]
                    if name and body and hasattr(body, "read"):
                        body.seek(0, 2)
                        raise AzureError("fail on first")
            for value in request.files.values():
                name, body = value[0], value[1]
                if name and body and hasattr(body, "read"):
                    position = body.tell()
                    assert not position
                    response = create_http_response(http_response, request, None)
                    response.status_code = 400
                    return response

    file = tempfile.NamedTemporaryFile(delete=False)
    file.write(b"Lots of dataaaa")
    file.close()
    http_request = http_request("GET", "http://localhost/")
    headers = {"Content-Type": "multipart/form-data"}
    http_request.headers = headers
    with open(file.name, "rb") as f:
        form_data_content = {
            "fileContent": f,
            "fileName": f.name,
        }
        http_request.set_formdata_body(form_data_content)
        http_retry = RetryPolicy(retry_total=1)
        pipeline = Pipeline(MockTransport(), [http_retry])
        pipeline.run(http_request)
    os.unlink(f.name)


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_retry_timeout(http_request):
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
    pipeline = Pipeline(transport, [RetryPolicy(timeout=timeout)])

    with pytest.raises(ServiceResponseTimeoutError):
        response = pipeline.run(http_request("GET", "http://localhost/"))


@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_timeout_defaults(http_request, http_response):
    """When "timeout" is not set, the policy should not override the transport's timeout configuration"""

    def send(request, **kwargs):
        for arg in ("connection_timeout", "read_timeout"):
            assert arg not in kwargs, "policy should defer to transport configuration when not given a timeout"
        response = create_http_response(http_response, request, None)
        response.status_code = 200
        return response

    transport = Mock(
        spec_set=HttpTransport,
        send=Mock(wraps=send),
        sleep=Mock(side_effect=Exception("policy should not sleep: its first send succeeded")),
    )
    pipeline = Pipeline(transport, [RetryPolicy()])

    pipeline.run(http_request("GET", "http://localhost/"))
    assert transport.send.call_count == 1, "policy should not retry: its first send succeeded"


combinations = [(ServiceRequestError, ServiceRequestTimeoutError), (ServiceResponseError, ServiceResponseTimeoutError)]


@pytest.mark.parametrize(
    "combinations,http_request",
    product(combinations, HTTP_REQUESTS),
)
def test_does_not_sleep_after_timeout(combinations, http_request):
    # It should not sleep the second time if timeout was exceeded during the first retry.
    transport_error, expected_timeout_error = combinations
    timeout = 0.5

    transport = Mock(
        spec=HttpTransport,
        send=Mock(side_effect=transport_error("oops")),
        sleep=Mock(wraps=time.sleep),
    )
    pipeline = Pipeline(transport, [RetryPolicy(timeout=timeout)])

    with pytest.raises(expected_timeout_error):
        pipeline.run(http_request("GET", "http://localhost/"))

    assert transport.sleep.call_count == 1


def test_configure_retries_uses_constructor_values():
    """Test that configure_retries method correctly gets values from constructor."""
    # Test with custom constructor values
    retry_policy = RetryPolicy(
        retry_total=5,
        retry_connect=2,
        retry_read=4,
        retry_status=1,
        retry_backoff_factor=0.5,
        retry_backoff_max=60,
        retry_jitter_factor=0.4,
        timeout=300,
    )

    # Call configure_retries with empty options to ensure it uses constructor values
    retry_settings = retry_policy.configure_retries({})

    # Verify that configure_retries returns constructor values as defaults
    assert retry_settings["total"] == 5
    assert retry_settings["connect"] == 2
    assert retry_settings["read"] == 4
    assert retry_settings["status"] == 1
    assert retry_settings["backoff"] == 0.5
    assert retry_settings["max_backoff"] == 60
    assert retry_settings["jitter"] == 0.4
    assert retry_settings["timeout"] == 300
    assert retry_settings["methods"] == frozenset(["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"])
    assert retry_settings["history"] == []


def test_configure_retries_options_override_constructor():
    """Test that options passed to configure_retries override constructor values."""
    # Test with custom constructor values
    retry_policy = RetryPolicy(
        retry_total=5,
        retry_connect=2,
        retry_read=4,
        retry_status=1,
        retry_backoff_factor=0.5,
        retry_jitter_factor=0.3,
        retry_backoff_max=60,
        timeout=300,
    )

    # Call configure_retries with options that should override constructor values
    options = {
        "retry_total": 8,
        "retry_connect": 6,
        "retry_read": 7,
        "retry_status": 3,
        "retry_backoff_factor": 1.0,
        "retry_jitter_factor": 0.4,
        "retry_backoff_max": 180,
        "timeout": 600,
        "retry_on_methods": frozenset(["GET", "POST"]),
    }
    retry_settings = retry_policy.configure_retries(options)

    # Verify that configure_retries returns option values, not constructor values
    assert retry_settings["total"] == 8
    assert retry_settings["connect"] == 6
    assert retry_settings["read"] == 7
    assert retry_settings["status"] == 3
    assert retry_settings["backoff"] == 1.0
    assert retry_settings["max_backoff"] == 180
    assert retry_settings["jitter"] == 0.4
    assert retry_settings["timeout"] == 600
    assert retry_settings["methods"] == frozenset(["GET", "POST"])
    assert retry_settings["history"] == []

    # Verify options dict was modified (values were popped)
    assert "retry_total" not in options
    assert "retry_connect" not in options
    assert "retry_read" not in options
    assert "retry_status" not in options
    assert "retry_backoff_factor" not in options
    assert "retry_backoff_max" not in options
    assert "retry_jitter_factor" not in options
    assert "timeout" not in options
    assert "retry_on_methods" not in options


def test_configure_retries_default_values():
    """Test that configure_retries uses default values when no constructor args or options provided."""
    # Test with default constructor
    retry_policy = RetryPolicy()

    # Call configure_retries with empty options
    retry_settings = retry_policy.configure_retries({})

    # Verify default values from RetryPolicyBase.__init__
    assert retry_settings["total"] == 10  # default retry_total
    assert retry_settings["connect"] == 3  # default retry_connect
    assert retry_settings["read"] == 3  # default retry_read
    assert retry_settings["status"] == 3  # default retry_status
    assert retry_settings["backoff"] == 0.8  # default retry_backoff_factor
    assert retry_settings["max_backoff"] == 120  # default retry_backoff_max (BACKOFF_MAX)
    assert retry_settings["jitter"] == 0.2  # default retry_jitter_factor
    assert retry_settings["timeout"] == 604800  # default timeout
    assert retry_settings["methods"] == frozenset(["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"])
    assert retry_settings["history"] == []


def test_get_backoff_time_with_jitter():
    """Test that jitter is applied when configured."""
    random.seed(42)

    retry_policy = RetryPolicy(retry_jitter_factor=0.2)

    # Test with first attempt (should still apply jitter if history has entries)
    history = ["attempt1"]
    settings = {"history": history, "backoff": 1.0, "max_backoff": 10, "jitter": 0.2}

    # Collect multiple results to verify jitter is working
    results = []
    for _ in range(10):
        backoff_time = retry_policy.get_backoff_time(settings)
        results.append(backoff_time)
        # Base backoff is 1.0, jitter is ±0.2, so result should be between 0.8 and 1.2
        assert 0.8 <= backoff_time <= 1.2

    # Verify we get different values (jitter is working)
    unique_results = set(results)
    assert len(unique_results) > 1  # Should have some variation due to jitter


def test_get_backoff_time_without_jitter():
    """Test that no jitter is applied when jitter factor is 0."""
    retry_policy = RetryPolicy(retry_jitter_factor=0.0)

    history = ["attempt1"]
    settings = {"history": history, "backoff": 1.0, "max_backoff": 10, "jitter": 0.0}

    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 1.0  # Should be exactly the base value


def test_get_backoff_time_jitter_with_exponential_backoff():
    """Test that jitter works correctly with exponential backoff."""
    random.seed(123)

    retry_policy = RetryPolicy(retry_mode=RetryMode.Exponential, retry_jitter_factor=0.1)

    # Test with multiple attempts
    history = ["attempt1", "attempt2", "attempt3"]
    settings = {"history": history, "backoff": 1.0, "max_backoff": 10, "jitter": 0.1}

    backoff_time = retry_policy.get_backoff_time(settings)

    # Base exponential backoff would be 1.0 * (2 ** (3-1)) = 4.0
    # With 10% jitter, result should be between 3.6 and 4.4
    expected_base = 4.0
    jitter_amount = expected_base * 0.1
    assert (expected_base - jitter_amount) <= backoff_time <= (expected_base + jitter_amount)


def test_get_backoff_time_jitter_with_fixed_backoff():
    """Test that jitter works correctly with fixed backoff."""
    random.seed(456)

    retry_policy = RetryPolicy(retry_mode=RetryMode.Fixed, retry_jitter_factor=0.3)

    history = ["attempt1", "attempt2", "attempt3"]
    settings = {"history": history, "backoff": 2.0, "max_backoff": 10, "jitter": 0.3}

    backoff_time = retry_policy.get_backoff_time(settings)

    # Base fixed backoff is 2.0
    # With 30% jitter, result should be between 1.4 and 2.6
    assert 1.4 <= backoff_time <= 2.6


def test_get_backoff_time_jitter_respects_max_backoff():
    """Test that jitter respects the max_backoff limit."""
    random.seed(789)

    retry_policy = RetryPolicy(retry_jitter_factor=0.5)

    # Create a scenario where base backoff would exceed max_backoff
    history = ["attempt1", "attempt2", "attempt3", "attempt4", "attempt5"]
    settings = {"history": history, "backoff": 2.0, "max_backoff": 5.0, "jitter": 0.5}  # This will cap the backoff

    backoff_time = retry_policy.get_backoff_time(settings)

    # Base exponential would be 2.0 * (2 ** (5-1)) = 32.0, but capped at 5.0
    # With 50% jitter on the capped value, result should be between 2.5 and 7.5
    assert 2.5 <= backoff_time <= 7.5


def test_get_backoff_time_jitter_prevents_negative_values():
    """Test that jitter cannot result in negative backoff times."""
    random.seed(101)

    retry_policy = RetryPolicy(retry_jitter_factor=1.5)  # Very high jitter factor

    history = ["attempt1"]
    settings = {"history": history, "backoff": 0.1, "max_backoff": 10, "jitter": 1.5}  # Very small base backoff

    # Run multiple times to ensure we never get negative values
    for _ in range(100):
        backoff_time = retry_policy.get_backoff_time(settings)
        assert backoff_time >= 0


def test_get_backoff_time_empty_history():
    """Test that backoff time is 0 when history is empty."""
    retry_policy = RetryPolicy(retry_jitter_factor=0.2)

    settings = {"history": [], "backoff": 1.0, "max_backoff": 10, "jitter": 0.2}

    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 0
