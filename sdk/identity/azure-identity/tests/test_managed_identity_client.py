# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import time

from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError
from azure.core.pipeline.transport import HttpRequest
from azure.identity._internal.managed_identity_client import ManagedIdentityClient
import pytest

from helpers import mock, mock_response, Request, validating_transport


def test_caching():
    scope = "scope"
    now = int(time.time())
    expected_expires_on = now + 3600
    expected_token = "*"
    transport = validating_transport(
        requests=[Request(url="http://localhost")],
        responses=[
            mock_response(
                json_payload={
                    "access_token": expected_token,
                    "expires_in": 3600,
                    "expires_on": expected_expires_on,
                    "resource": scope,
                    "token_type": "Bearer",
                }
            )
        ],
    )
    client = ManagedIdentityClient(
        request_factory=lambda _, __: HttpRequest("GET", "http://localhost"), transport=transport
    )

    token = client.get_cached_token(scope)
    assert not token

    with mock.patch(ManagedIdentityClient.__module__ + ".time.time", lambda: now):
        token = client.request_token(scope)
    assert token.expires_on == expected_expires_on
    assert token.token == expected_token

    token = client.get_cached_token(scope)
    assert token.expires_on == expected_expires_on
    assert token.token == expected_token


def test_deserializes_json_from_text():
    """The client should gracefully handle a response with a JSON body and content-type text/plain"""

    scope = "scope"
    now = int(time.time())
    expected_expires_on = now + 3600
    expected_token = "*"

    def send(request, **_):
        body = json.dumps(
            {
                "access_token": expected_token,
                "expires_in": 3600,
                "expires_on": expected_expires_on,
                "resource": scope,
                "token_type": "Bearer",
            }
        )
        return mock.Mock(
            status_code=200,
            headers={"Content-Type": "text/plain"},
            content_type="text/plain",
            text=lambda encoding=None: body,
        )

    client = ManagedIdentityClient(
        request_factory=lambda _, __: HttpRequest("GET", "http://localhost"), transport=mock.Mock(send=send)
    )

    token = client.request_token(scope)
    assert token.expires_on == expected_expires_on
    assert token.token == expected_token


def test_retry():
    """ManagedIdentityClient should retry token requests"""

    message = "can't connect"
    transport = mock.Mock(send=mock.Mock(side_effect=ServiceRequestError(message)))
    request_factory = mock.Mock()

    client = ManagedIdentityClient(request_factory, transport=transport)

    for method in ("GET", "POST"):
        request_factory.return_value = HttpRequest(method, "https://localhost")
        with pytest.raises(ServiceRequestError, match=message):
            client.request_token("scope")
        assert transport.send.call_count > 1
        transport.send.reset_mock()


@pytest.mark.parametrize("content_type", ("text/html", "application/json"))
def test_unexpected_content(content_type):
    content = "<html><body>not JSON</body></html>"

    def send(request, **_):
        return mock.Mock(
            status_code=200,
            headers={"Content-Type": content_type},
            content_type=content_type,
            text=lambda encoding=None: content,
        )

    client = ManagedIdentityClient(
        request_factory=lambda _, __: HttpRequest("GET", "http://localhost"), transport=mock.Mock(send=send)
    )

    with pytest.raises(ClientAuthenticationError) as ex:
        client.request_token("scope")
    assert ex.value.response.text() == content

    if "json" not in content_type:
        assert content_type in ex.value.message
