# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import random
import socket
import threading
import time

from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.identity import CredentialUnavailableError, InteractiveBrowserCredential
from azure.identity._exceptions import AuthenticationRequiredError
from azure.identity._internal import AuthCodeRedirectServer
from azure.identity._internal.user_agent import USER_AGENT
from msal import TokenCache
import pytest
from six.moves import urllib, urllib_parse

from helpers import (
    build_aad_response,
    build_id_token,
    get_discovery_response,
    mock_response,
    msal_validating_transport,
    Request,
    validating_transport,
)

try:
    from unittest.mock import ANY, Mock, patch
except ImportError:  # python < 3.3
    from mock import ANY, Mock, patch  # type: ignore


WEBBROWSER_OPEN = InteractiveBrowserCredential.__module__ + ".webbrowser.open"


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


def test_authenticate():
    client_id = "client-id"
    environment = "localhost"
    issuer = "https://" + environment
    tenant_id = "some-tenant"
    authority = issuer + "/" + tenant_id

    access_token = "***"
    scope = "scope"

    # mock AAD response with id token
    object_id = "object-id"
    home_tenant = "home-tenant-id"
    username = "me@work.com"
    id_token = build_id_token(aud=client_id, iss=issuer, object_id=object_id, tenant_id=home_tenant, username=username)
    auth_response = build_aad_response(
        uid=object_id, utid=home_tenant, access_token=access_token, refresh_token="**", id_token=id_token
    )

    transport = validating_transport(
        requests=[Request(url_substring=issuer)] * 3,
        responses=[get_discovery_response(authority)] * 2 + [mock_response(json_payload=auth_response)],
    )

    # mock local server fakes successful authentication by immediately returning a well-formed response
    oauth_state = "state"
    auth_code_response = {"code": "authorization-code", "state": [oauth_state]}
    server_class = Mock(return_value=Mock(wait_for_redirect=lambda: auth_code_response))

    with patch(InteractiveBrowserCredential.__module__ + ".uuid.uuid4", lambda: oauth_state):
        with patch(WEBBROWSER_OPEN, lambda _: True):
            credential = InteractiveBrowserCredential(
                _cache=TokenCache(),
                authority=environment,
                client_id=client_id,
                _server_class=server_class,
                tenant_id=tenant_id,
                transport=transport,
            )
            record = credential._authenticate(scopes=(scope,))

    assert record.authority == environment
    assert record.home_account_id == object_id + "." + home_tenant
    assert record.tenant_id == home_tenant
    assert record.username == username

    # credential should have a cached access token for the scope used in authenticate
    with patch(WEBBROWSER_OPEN, Mock(side_effect=Exception("credential should authenticate silently"))):
        token = credential.get_token(scope)
    assert token.token == access_token


def test_disable_automatic_authentication():
    """When configured for strict silent auth, the credential should raise when silent auth fails"""

    empty_cache = TokenCache()  # empty cache makes silent auth impossible
    transport = Mock(send=Mock(side_effect=Exception("no request should be sent")))
    credential = InteractiveBrowserCredential(
        _disable_automatic_authentication=True, transport=transport, _cache=empty_cache
    )

    with patch(WEBBROWSER_OPEN, Mock(side_effect=Exception("credential shouldn't try interactive authentication"))):
        with pytest.raises(AuthenticationRequiredError):
            credential.get_token("scope")


@patch("azure.identity._credentials.browser.webbrowser.open", lambda _: True)
def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())
    client_id = "client-id"
    transport = validating_transport(
        requests=[Request()] * 2,
        responses=[
            get_discovery_response(),
            mock_response(json_payload=build_aad_response(access_token="**", id_token=build_id_token(aud=client_id))),
        ],
    )

    # mock local server fakes successful authentication by immediately returning a well-formed response
    oauth_state = "oauth-state"
    auth_code_response = {"code": "authorization-code", "state": [oauth_state]}
    server_class = Mock(return_value=Mock(wait_for_redirect=lambda: auth_code_response))

    credential = InteractiveBrowserCredential(
        policies=[policy], client_id=client_id, transport=transport, _server_class=server_class, _cache=TokenCache()
    )

    with patch("azure.identity._credentials.browser.uuid.uuid4", lambda: oauth_state):
        credential.get_token("scope")

    assert policy.on_request.called


@patch("azure.identity._credentials.browser.webbrowser.open", lambda _: True)
def test_user_agent():
    client_id = "client-id"
    transport = validating_transport(
        requests=[Request(), Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[
            get_discovery_response(),
            mock_response(json_payload=build_aad_response(access_token="**", id_token=build_id_token(aud=client_id))),
        ],
    )

    # mock local server fakes successful authentication by immediately returning a well-formed response
    oauth_state = "oauth-state"
    auth_code_response = {"code": "authorization-code", "state": [oauth_state]}
    server_class = Mock(return_value=Mock(wait_for_redirect=lambda: auth_code_response))

    credential = InteractiveBrowserCredential(
        client_id=client_id, transport=transport, _server_class=server_class, _cache=TokenCache()
    )

    with patch("azure.identity._credentials.browser.uuid.uuid4", lambda: oauth_state):
        credential.get_token("scope")


@patch("azure.identity._credentials.browser.webbrowser.open")
@pytest.mark.parametrize("redirect_url", ("https://localhost:8042", None))
def test_interactive_credential(mock_open, redirect_url):
    mock_open.side_effect = _validate_auth_request_url
    oauth_state = "state"
    client_id = "client-id"
    expected_refresh_token = "refresh-token"
    expected_token = "access-token"
    expires_in = 3600
    authority = "authority"
    tenant_id = "tenant-id"
    endpoint = "https://{}/{}".format(authority, tenant_id)

    transport = msal_validating_transport(
        endpoint="https://{}/{}".format(authority, tenant_id),
        requests=[Request(url_substring=endpoint)]
        + [
            Request(
                authority=authority, url_substring=endpoint, required_data={"refresh_token": expected_refresh_token}
            )
        ],
        responses=[
            mock_response(
                json_payload=build_aad_response(
                    access_token=expected_token,
                    expires_in=expires_in,
                    refresh_token=expected_refresh_token,
                    uid="uid",
                    utid=tenant_id,
                    id_token=build_id_token(aud=client_id, object_id="uid", tenant_id=tenant_id, iss=endpoint),
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

    args = {
        "authority": authority,
        "tenant_id": tenant_id,
        "client_id": client_id,
        "transport": transport,
        "_cache": TokenCache(),
        "_server_class": server_class,
    }
    if redirect_url:  # avoid passing redirect_url=None
        args["redirect_uri"] = redirect_url

    credential = InteractiveBrowserCredential(**args)

    # The credential's auth code request includes a uuid which must be included in the redirect. Patching to
    # set the uuid requires less code here than a proper mock server.
    with patch("azure.identity._credentials.browser.uuid.uuid4", lambda: oauth_state):
        token = credential.get_token("scope")
    assert token.token == expected_token
    assert mock_open.call_count == 1
    assert server_class.call_count == 1

    if redirect_url:
        server_class.assert_called_once_with(redirect_url, timeout=ANY)

    # token should be cached, get_token shouldn't prompt again
    token = credential.get_token("scope")
    assert token.token == expected_token
    assert mock_open.call_count == 1
    assert server_class.call_count == 1

    # expired access token -> credential should use refresh token instead of prompting again
    now = time.time()
    with patch("time.time", lambda: now + expires_in):
        token = credential.get_token("scope")
    assert token.token == expected_token
    assert mock_open.call_count == 1

    # ensure all expected requests were sent
    assert transport.send.call_count == 4


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
        timeout=timeout, transport=transport, _cache=TokenCache(), _server_class=GuaranteedTimeout
    )

    with patch(WEBBROWSER_OPEN, lambda _: True):
        with pytest.raises(ClientAuthenticationError) as ex:
            credential.get_token("scope")
    assert "timed out" in ex.value.message.lower()


def test_redirect_server():
    # binding a random port prevents races when running the test in parallel
    server = None
    for _ in range(4):
        try:
            port = random.randint(1024, 65535)
            url = "http://127.0.0.1:{}".format(port)
            server = AuthCodeRedirectServer(url, timeout=10)
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
    response = urllib.request.urlopen(url + "?{}={}".format(expected_param, expected_value))  # nosec

    assert response.code == 200
    assert server.query_params[expected_param] == [expected_value]


@patch("azure.identity._credentials.browser.webbrowser.open", lambda _: False)
def test_no_browser():
    transport = validating_transport(requests=[Request()] * 2, responses=[get_discovery_response()] * 2)
    credential = InteractiveBrowserCredential(
        client_id="client-id", _server_class=Mock(), transport=transport, _cache=TokenCache()
    )
    with pytest.raises(ClientAuthenticationError, match=r".*browser.*"):
        credential.get_token("scope")


def test_cannot_bind_port():
    """get_token should raise CredentialUnavailableError when the redirect listener can't bind a port"""

    credential = InteractiveBrowserCredential(_server_class=Mock(side_effect=socket.error))
    with pytest.raises(CredentialUnavailableError):
        credential.get_token("scope")


def test_cannot_bind_redirect_uri():
    """When a user specifies a redirect URI, the credential shouldn't attempt to bind another"""

    expected_uri = "http://localhost:42"

    server = Mock(side_effect=socket.error)
    credential = InteractiveBrowserCredential(redirect_uri=expected_uri, _server_class=server)

    with pytest.raises(CredentialUnavailableError):
        credential.get_token("scope")

    server.assert_called_once_with(expected_uri, timeout=ANY)


def _validate_auth_request_url(url):
    parsed_url = urllib_parse.urlparse(url)
    params = urllib_parse.parse_qs(parsed_url.query)
    assert params.get("prompt") == ["select_account"], "Auth code request doesn't specify 'prompt=select_account'."

    # when used as a Mock's side_effect, this method's return value is the Mock's return value
    # (the real webbrowser.open returns a bool)
    return True
