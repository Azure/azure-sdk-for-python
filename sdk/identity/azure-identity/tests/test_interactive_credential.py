# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import socket
import threading
import time

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import InteractiveBrowserCredential
from azure.identity._internal import AuthCodeRedirectServer
import pytest
from six.moves import urllib

from helpers import mock_response, Request, validating_transport

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

@patch(
    "azure.identity._credentials.browser.webbrowser.open", lambda _: None
)  # prevent the credential opening a browser
def test_interactive_credential():
    oauth_state = "state"
    expected_token = "access-token"

    transport = validating_transport(
        requests=[Request()] * 2,  # not validating requests because they're formed by MSAL
        responses=[
            # expecting tenant discovery then a token request
            mock_response(json_payload={"authorization_endpoint": "https://a/b", "token_endpoint": "https://a/b"}),
            mock_response(
                json_payload={
                    "access_token": expected_token,
                    "expires_in": 42,
                    "token_type": "Bearer",
                    "ext_expires_in": 42,
                }
            ),
        ],
    )

    # mock local server fakes successful authentication by immediately returning a well-formed response
    auth_code_response = {"code": "authorization-code", "state": [oauth_state]}
    server_class = Mock(return_value=Mock(wait_for_redirect=lambda: auth_code_response))

    credential = InteractiveBrowserCredential(
        client_id="guid",
        client_secret="secret",
        server_class=server_class,
        transport=transport,
        instance_discovery=False,  # kwargs are passed to MSAL; this one prevents an AAD verification request
    )

    # ensure the request beginning the flow has a known state value
    with patch("azure.identity._credentials.browser.uuid.uuid4", lambda: oauth_state):
        token = credential.get_token("scope")
    assert token.token == expected_token


@patch(
    "azure.identity._credentials.browser.webbrowser.open", lambda _: None
)  # prevent the credential opening a browser
def test_interactive_credential_timeout():
    # mock transport handles MSAL's tenant discovery
    transport = Mock(
        send=lambda _, **__: mock_response(
            json_payload={"authorization_endpoint": "https://a/b", "token_endpoint": "https://a/b"}
        )
    )

    # mock local server blocks long enough to exceed the timeout
    timeout = 0.01
    server_instance = Mock(wait_for_redirect=functools.partial(time.sleep, timeout + 0.01))
    server_class = Mock(return_value=server_instance)

    credential = InteractiveBrowserCredential(
        client_id="guid",
        client_secret="secret",
        server_class=server_class,
        timeout=timeout,
        transport=transport,
        instance_discovery=False,  # kwargs are passed to MSAL; this one prevents an AAD verification request
    )

    with pytest.raises(ClientAuthenticationError) as ex:
        credential.get_token("scope")
    assert "timed out" in ex.value.message.lower()


def test_redirect_server():
    for port in range(8400, 9000):
        try:
            server = AuthCodeRedirectServer(port, timeout=10)
            redirect_uri = "http://localhost:{}".format(port)
            break
        except socket.error:
            continue  # keep looking for an open port

    expected_param = "expected-param"
    expected_value = "expected-value"

    # the server's wait is blocking, so we do it on another thread
    thread = threading.Thread(target=server.wait_for_redirect, name=__name__)
    thread.daemon = True
    thread.start()

    # send a request, verify the server exposes the query
    url = "http://localhost:{}/?{}={}".format(port, expected_param, expected_value)
    response = urllib.request.urlopen(url)

    assert response.code == 200
    assert server.query_params[expected_param] == [expected_value]
