# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.exceptions import ServiceRequestError
from azure.identity._internal.msal_client import MsalClient

import pytest

from helpers import mock, mock_response, validating_transport, Request


def test_retries_requests():
    """The client should retry token requests"""

    message = "can't connect"
    transport = mock.Mock(send=mock.Mock(side_effect=ServiceRequestError(message)))
    client = MsalClient(transport=transport)

    with pytest.raises(ServiceRequestError, match=message):
        client.post("https://localhost")
    assert transport.send.call_count > 1
    transport.send.reset_mock()

    with pytest.raises(ServiceRequestError, match=message):
        client.get("https://localhost")
    assert transport.send.call_count > 1


def test_get_error_response():
    first_result = {"error": "first"}
    first_response = mock_response(401, json_payload=first_result)
    second_result = {"error": "second"}
    second_response = mock_response(401, json_payload=second_result)
    transport = validating_transport(
        requests=[Request(url="https://localhost")] * 2, responses=[first_response, second_response]
    )

    client = MsalClient(transport=transport)

    for result in (first_result, second_result):
        assert not client.get_error_response(result)

    client.get("https://localhost")
    response = client.get_error_response(first_result)
    assert response is first_response

    client.post("https://localhost")
    response = client.get_error_response(second_result)
    assert response is second_response

    assert not client.get_error_response(first_result)


def test_string_response_content():
    """Test client handling string response content with error message"""
    # String response content with error message
    string_error = "Some string error message containing the word error"
    response = mock.Mock(status_code=401, headers={})
    response.text = lambda encoding=None: string_error
    response.headers["content-type"] = "text/plain"
    response.content_type = "text/plain"

    # Create a transport that returns the string response
    transport = validating_transport(
        requests=[Request(url="https://localhost")],
        responses=[response],
    )

    client = MsalClient(transport=transport)

    # Make a request to store the auth error.
    client.get("https://localhost")
    error_code, saved_response = getattr(client._local, "error", (None, None))

    assert error_code == "oauth_error"
    assert saved_response is response
