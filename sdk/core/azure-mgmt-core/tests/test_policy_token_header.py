# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
import pytest
from unittest.mock import Mock
from azure.core.exceptions import HttpResponseError
from azure.mgmt.core.policies._policy_token_header import (
    PolicyTokenHeaderPolicy,
)
from azure.core.pipeline.transport import HttpRequest


class MockARMPipelineClient:
    def __init__(self, response):
        self._response = response

    def send_request(self, request, stream=False):
        return self._response


class MockHttpResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data

    def text(self):
        return str(self._json_data)


def test_policy_token_header_policy_adds_header():
    """Test that the policy adds the correct header when policy token is acquired successfully."""

    # Mock client that returns a successful policy token response
    mock_response = MockHttpResponse(200, {"token": "test-token-123", "result": "Succeeded"})
    mock_client = MockARMPipelineClient(mock_response)

    policy = PolicyTokenHeaderPolicy(mock_client, acquire_policy_token=True)

    # Test with a subscription URL
    request = HttpRequest("PUT", "https://management.azure.com/subscriptions/12345/resourceGroups/test")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    policy.on_request(pipeline_request)

    # Verify the header was added
    assert request.headers["x-ms-policy-external-evaluations"] == "test-token-123"


def test_policy_token_header_policy_no_subscription_id():
    """Test that the policy raises an error when no subscription ID is found in the URL."""

    mock_response = MockHttpResponse(200, {"token": "test-token-123", "result": "Succeeded"})
    mock_client = MockARMPipelineClient(mock_response)

    policy = PolicyTokenHeaderPolicy(mock_client, acquire_policy_token=True)

    # Test with a URL without subscription ID
    request = HttpRequest("POST", "https://management.azure.com/providers/Microsoft.Resources")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    with pytest.raises(HttpResponseError, match="Failed to get subscriptionId from request url"):
        policy.on_request(pipeline_request)


def test_policy_token_header_policy_failed_response():
    """Test that the policy raises an error when the policy token response fails."""

    # Mock client that returns a failed response
    mock_response = MockHttpResponse(500, {"error": "Internal server error"})
    mock_client = MockARMPipelineClient(mock_response)

    policy = PolicyTokenHeaderPolicy(mock_client, acquire_policy_token=True)

    request = HttpRequest("PUT", "https://management.azure.com/subscriptions/12345/resourceGroups/test")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    with pytest.raises(HttpResponseError, match="status code is not 200"):
        policy.on_request(pipeline_request)


def test_policy_token_header_policy_unsuccessful_result():
    """Test that the policy raises an error when the policy token acquisition is unsuccessful."""

    # Mock client that returns an unsuccessful result
    mock_response = MockHttpResponse(200, {"result": "Failed", "error": "Token acquisition failed"})
    mock_client = MockARMPipelineClient(mock_response)

    policy = PolicyTokenHeaderPolicy(mock_client, acquire_policy_token=True)

    request = HttpRequest("PUT", "https://management.azure.com/subscriptions/12345/resourceGroups/test")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    with pytest.raises(HttpResponseError, match="Failed to acquire policy token"):
        policy.on_request(pipeline_request)


def test_policy_token_header_policy_disabled_by_default():
    """Test that the policy does not acquire tokens when acquire_policy_token is False by default."""

    mock_response = MockHttpResponse(200, {"token": "test-token-123", "result": "Succeeded"})
    mock_client = MockARMPipelineClient(mock_response)

    # Policy without acquire_policy_token=True
    policy = PolicyTokenHeaderPolicy(mock_client)

    request = HttpRequest("PUT", "https://management.azure.com/subscriptions/12345/resourceGroups/test")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    policy.on_request(pipeline_request)

    # Verify no header was added
    assert "x-ms-policy-external-evaluations" not in request.headers


def test_policy_token_header_policy_context_option_override():
    """Test that context options can override the policy's acquire_policy_token setting."""

    mock_response = MockHttpResponse(200, {"token": "context-token-456", "result": "Succeeded"})
    mock_client = MockARMPipelineClient(mock_response)

    # Policy with acquire_policy_token=False
    policy = PolicyTokenHeaderPolicy(mock_client, acquire_policy_token=False)

    request = HttpRequest("PUT", "https://management.azure.com/subscriptions/12345/resourceGroups/test")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {"acquire_policy_token": True}

    policy.on_request(pipeline_request)

    # Verify the header was added despite the policy default being False
    assert request.headers["x-ms-policy-external-evaluations"] == "context-token-456"


def test_policy_token_header_policy_with_content():
    """Test that the policy handles request content properly when creating the policy request."""

    def verify_policy_request(request, stream=False):
        # Verify the policy request contains the operation details including content
        import json

        body = json.loads(request.content)
        assert body["operation"]["uri"] == "https://management.azure.com/subscriptions/12345/resourceGroups/test"
        assert body["operation"]["method"] == "PUT"
        assert "content" in body["operation"]
        return MockHttpResponse(200, {"token": "content-token-789", "result": "Succeeded"})

    mock_client = Mock()
    mock_client.send_request = verify_policy_request

    policy = PolicyTokenHeaderPolicy(mock_client, acquire_policy_token=True)

    request_content = '{"properties": {"location": "eastus"}}'
    request = HttpRequest("PUT", "https://management.azure.com/subscriptions/12345/resourceGroups/test")
    request.content = request_content

    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    policy.on_request(pipeline_request)

    # Verify the header was added
    assert request.headers["x-ms-policy-external-evaluations"] == "content-token-789"


def test_policy_token_header_policy_get_request_no_token():
    """Test that the policy does not acquire tokens for GET requests even if acquire_policy_token is True."""

    mock_response = MockHttpResponse(200, {"token": "test-token-123", "result": "Succeeded"})
    mock_client = MockARMPipelineClient(mock_response)

    policy = PolicyTokenHeaderPolicy(mock_client, acquire_policy_token=True)

    request = HttpRequest("GET", "https://management.azure.com/providers/Microsoft.Resources")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    policy.on_request(pipeline_request)

    # Verify no header was added
    assert "x-ms-policy-external-evaluations" not in request.headers
