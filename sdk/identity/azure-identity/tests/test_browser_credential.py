# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import platform
import random
import socket
import threading
import time
import urllib
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.pipeline.transport import RequestsTransport
from azure.identity import AuthenticationRequiredError, CredentialUnavailableError, InteractiveBrowserCredential
from azure.identity._internal import AuthCodeRedirectServer
from azure.identity._internal.user_agent import USER_AGENT
import pytest
from unittest.mock import ANY, Mock, patch

from helpers import (
    build_aad_response,
    build_id_token,
    get_discovery_response,
    id_token_claims,
    mock_response,
    Request,
    validating_transport,
)


WEBBROWSER_OPEN = InteractiveBrowserCredential.__module__ + ".webbrowser.open"


@pytest.mark.manual
def test_browser_credential():
    transport = Mock(wraps=RequestsTransport())
    credential = InteractiveBrowserCredential(transport=transport)
    scope = "https://management.azure.com/.default"  # N.B. this is valid only in Public Cloud

    record = credential.authenticate(scopes=(scope,))
    assert record.authority
    assert record.home_account_id
    assert record.tenant_id
    assert record.username

    # credential should have a cached access token for the scope used in authenticate
    with patch(WEBBROWSER_OPEN, Mock(side_effect=Exception("credential should authenticate silently"))):
        token = credential.get_token(scope)
    assert token.token

    credential = InteractiveBrowserCredential(transport=transport)
    token = credential.get_token(scope)
    assert token.token

    with patch(WEBBROWSER_OPEN, Mock(side_effect=Exception("credential should authenticate silently"))):
        second_token = credential.get_token(scope)
    assert second_token.token == token.token

    # every request should have the correct User-Agent
    for call in transport.send.call_args_list:
        args, _ = call
        request = args[0]
        assert request.headers["User-Agent"] == USER_AGENT


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""

    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        InteractiveBrowserCredential(tenant_id=tenant)

    invalid_ids = {"my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        with pytest.raises(ValueError):
            InteractiveBrowserCredential(tenant_id=tenant)


def test_no_scopes():
    """The credential should raise when get_token is called with no scopes"""

    with pytest.raises(ValueError):
        InteractiveBrowserCredential().get_token()


def test_policies_configurable():
    # the policy raises an exception so this test can run without authenticating i.e. opening a browser
    expected_message = "test_policies_configurable"
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock(side_effect=Exception(expected_message)))

    credential = InteractiveBrowserCredential(policies=[policy])

    with pytest.raises(ClientAuthenticationError) as ex:
        credential.get_token("scope")

    assert expected_message in ex.value.message
    assert policy.on_request.called


def test_disable_automatic_authentication():
    """When configured for strict silent auth, the credential should raise when silent auth fails"""

    transport = Mock(send=Mock(side_effect=Exception("no request should be sent")))
    credential = InteractiveBrowserCredential(
        disable_automatic_authentication=True, transport=transport, client_credential="client_credential"
    )

    with patch(WEBBROWSER_OPEN, Mock(side_effect=Exception("credential shouldn't try interactive authentication"))):
        with pytest.raises(AuthenticationRequiredError):
            credential.get_token("scope")


def test_timeout():
    """get_token should raise ClientAuthenticationError when the server times out without receiving a redirect"""

    timeout = 0.01

    class GuaranteedTimeout(AuthCodeRedirectServer, object):
        def handle_request(self):
            time.sleep(timeout + 0.01)
            super(GuaranteedTimeout, self).handle_request()

    # mock transport handles MSAL's tenant discovery
    transport = Mock(
        send=lambda _, **__: mock_response(
            json_payload={"authorization_endpoint": "https://a/b", "token_endpoint": "https://a/b"}
        )
    )

    credential = InteractiveBrowserCredential(
        timeout=timeout, transport=transport, _server_class=GuaranteedTimeout, client_credential="client_credential"
    )

    with patch(WEBBROWSER_OPEN, lambda _: True):
        with pytest.raises(ClientAuthenticationError) as ex:
            credential.get_token("scope")
    assert "timed out" in ex.value.message.lower()


def test_redirect_server():
    # binding a random port prevents races when running the test in parallel
    server = None
    hostname = "127.0.0.1"
    for _ in range(4):
        try:
            port = random.randint(1024, 65535)
            server = AuthCodeRedirectServer(hostname, port, timeout=10)
            break
        except socket.error:
            continue  # keep looking for an open port

    assert server, "failed to start redirect server"

    expected_param = "expected-param"
    expected_value = "expected-value"

    # the server's wait is blocking, so we do it on another thread
    thread = threading.Thread(target=server.wait_for_redirect)
    thread.daemon = True
    thread.start()

    # send a request, verify the server exposes the query
    url = "http://{}:{}".format(hostname, port) + "?{}={}".format(expected_param, expected_value)
    response = urllib.request.urlopen(url)  # nosec

    assert response.code == 200
    assert server.query_params[expected_param] == expected_value


def test_no_browser():
    """The credential should raise CredentialUnavailableError when it can't open a browser"""

    transport = validating_transport(requests=[Request()] * 2, responses=[get_discovery_response()] * 2)
    credential = InteractiveBrowserCredential(
        client_id="client-id", _server_class=Mock(), transport=transport, client_credential="client_credential"
    )
    with patch(InteractiveBrowserCredential.__module__ + "._open_browser", lambda _: False):
        with pytest.raises(CredentialUnavailableError, match=r".*browser.*"):
            credential.get_token("scope")


def test_redirect_uri():
    """The credential should configure the redirect server to use a given redirect_uri"""

    expected_hostname = "localhost"
    expected_port = 42424
    expected_message = "test_redirect_uri"
    server = Mock(side_effect=Exception(expected_message))  # exception prevents this test actually authenticating
    credential = InteractiveBrowserCredential(
        redirect_uri="https://{}:{}".format(expected_hostname, expected_port),
        _server_class=server,
        client_credential="client_credential",
    )
    with pytest.raises(ClientAuthenticationError) as ex:
        credential.get_token("scope")

    assert expected_message in ex.value.message
    server.assert_called_once_with(expected_hostname, expected_port, timeout=ANY)


@pytest.mark.parametrize("redirect_uri", ("http://localhost", "host", "host:42"))
def test_invalid_redirect_uri(redirect_uri):
    """The credential should raise ValueError when redirect_uri is invalid or doesn't include a port"""

    with pytest.raises(ValueError):
        InteractiveBrowserCredential(redirect_uri=redirect_uri, client_credential="client_credential")


def test_cannot_bind_port():
    """get_token should raise CredentialUnavailableError when the redirect listener can't bind a port"""

    credential = InteractiveBrowserCredential(
        _server_class=Mock(side_effect=socket.error), client_credential="client_credential"
    )
    with pytest.raises(CredentialUnavailableError):
        credential.get_token("scope")


def test_cannot_bind_redirect_uri():
    """When a user specifies a redirect URI, the credential shouldn't attempt to bind another"""

    server = Mock(side_effect=socket.error)
    credential = InteractiveBrowserCredential(
        redirect_uri="http://localhost:42", _server_class=server, client_credential="client_credential"
    )

    with pytest.raises(CredentialUnavailableError):
        credential.get_token("scope")

    server.assert_called_once_with("localhost", 42, timeout=ANY)
