# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import socket
import threading
import time

from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.identity import InteractiveBrowserCredential
from azure.identity._internal import AuthCodeRedirectServer
from azure.identity._internal.user_agent import USER_AGENT

import pytest
from six.moves import urllib, urllib_parse

from helpers import build_aad_response, get_discovery_response, mock_response, Request, validating_transport

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore


@patch("azure.identity._credentials.browser.webbrowser.open", lambda _: True)
def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    transport = validating_transport(
        requests=[Request()] * 2,
        responses=[get_discovery_response(), mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    # mock local server fakes successful authentication by immediately returning a well-formed response
    oauth_state = "oauth-state"
    auth_code_response = {"code": "authorization-code", "state": [oauth_state]}
    server_class = Mock(return_value=Mock(wait_for_redirect=lambda: auth_code_response))

    credential = InteractiveBrowserCredential(policies=[policy], transport=transport, server_class=server_class)

    with patch("azure.identity._credentials.browser.uuid.uuid4", lambda: oauth_state):
        credential.get_token("scope")

    assert policy.on_request.called


@patch("azure.identity._credentials.browser.webbrowser.open", lambda _: True)
def test_user_agent():
    transport = validating_transport(
        requests=[Request(), Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[get_discovery_response(), mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    # mock local server fakes successful authentication by immediately returning a well-formed response
    oauth_state = "oauth-state"
    auth_code_response = {"code": "authorization-code", "state": [oauth_state]}
    server_class = Mock(return_value=Mock(wait_for_redirect=lambda: auth_code_response))

    credential = InteractiveBrowserCredential(transport=transport, server_class=server_class)

    with patch("azure.identity._credentials.browser.uuid.uuid4", lambda: oauth_state):
        credential.get_token("scope")


@patch("azure.identity._credentials.browser.webbrowser.open")
def test_interactive_credential(mock_open):
    mock_open.side_effect = _validate_auth_request_url
    oauth_state = "state"
    client_id = "client-id"
    expected_refresh_token = "refresh-token"
    expected_token = "access-token"
    expires_in = 3600
    authority = "authority"
    tenant_id = "tenant_id"
    endpoint = "https://{}/{}".format(authority, tenant_id)

    discovery_response = get_discovery_response(endpoint=endpoint)
    transport = validating_transport(
        requests=[Request(url_substring=endpoint)] * 3
        + [
            Request(
                authority=authority, url_substring=endpoint, required_data={"refresh_token": expected_refresh_token}
            )
        ],
        responses=[
            discovery_response,  # instance discovery
            discovery_response,  # tenant discovery
            mock_response(
                json_payload=build_aad_response(
                    access_token=expected_token,
                    expires_in=expires_in,
                    refresh_token=expected_refresh_token,
                    uid="uid",
                    utid="utid",
                    token_type="Bearer",
                )
            ),
            mock_response(
                json_payload=build_aad_response(access_token=expected_token, expires_in=expires_in, token_type="Bearer")
            ),
        ],
    )

    # mock local server fakes successful authentication by immediately returning a well-formed response
    auth_code_response = {"code": "authorization-code", "state": [oauth_state]}
    server_class = Mock(return_value=Mock(wait_for_redirect=lambda: auth_code_response))

    credential = InteractiveBrowserCredential(
        authority=authority,
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret="secret",
        server_class=server_class,
        transport=transport,
        instance_discovery=False,
        validate_authority=False,
    )

    # The credential's auth code request includes a uuid which must be included in the redirect. Patching to
    # set the uuid requires less code here than a proper mock server.
    with patch("azure.identity._credentials.browser.uuid.uuid4", lambda: oauth_state):
        token = credential.get_token("scope")
    assert token.token == expected_token
    assert mock_open.call_count == 1

    # token should be cached, get_token shouldn't prompt again
    token = credential.get_token("scope")
    assert token.token == expected_token
    assert mock_open.call_count == 1

    # As of MSAL 1.0.0, applications build a new client every time they redeem a refresh token.
    # Here we patch the private method they use for the sake of test coverage.
    # TODO: this will probably break when this MSAL behavior changes
    app = credential._get_app()
    app._build_client = lambda *_: app.client  # pylint:disable=protected-access
    now = time.time()

    # expired access token -> credential should use refresh token instead of prompting again
    with patch("time.time", lambda: now + expires_in):
        token = credential.get_token("scope")
    assert token.token == expected_token
    assert mock_open.call_count == 1

    # ensure all expected requests were sent
    assert transport.send.call_count == 4


@patch("azure.identity._credentials.browser.webbrowser.open", lambda _: True)
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


@patch("azure.identity._credentials.browser.webbrowser.open", lambda _: False)
def test_no_browser():
    transport = validating_transport(requests=[Request()] * 2, responses=[get_discovery_response()] * 2)
    credential = InteractiveBrowserCredential(
        client_id="client-id", client_secret="secret", server_class=Mock(), transport=transport
    )
    with pytest.raises(ClientAuthenticationError, match=r".*browser.*"):
        credential.get_token("scope")


def _validate_auth_request_url(url):
    parsed_url = urllib_parse.urlparse(url)
    params = urllib_parse.parse_qs(parsed_url.query)
    assert params.get("prompt") == ["select_account"], "Auth code request doesn't specify 'prompt=select_account'."

    # when used as a Mock's side_effect, this method's return value is the Mock's return value
    # (the real webbrowser.open returns a bool)
    return True
