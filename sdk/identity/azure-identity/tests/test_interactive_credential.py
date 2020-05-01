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
from azure.identity import AuthenticationRequiredError, InteractiveBrowserCredential
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
    Request,
    validating_transport,
)

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore


WEBBROWSER_OPEN = InteractiveBrowserCredential.__module__ + ".webbrowser.open"


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
                server_class=server_class,
                tenant_id=tenant_id,
                transport=transport,
            )
            record = credential.authenticate(scopes=(scope,))

    # credential should have a cached access token for the scope used in authenticate
    with patch(WEBBROWSER_OPEN, Mock(side_effect=Exception("credential should authenticate silently"))):
        token = credential.get_token(scope)
    assert token.token == access_token

    assert record.authority == environment
    assert record.home_account_id == object_id + "." + home_tenant
    assert record.tenant_id == home_tenant
    assert record.username == username


def test_disable_automatic_authentication():
    """When configured for strict silent auth, the credential should raise when silent auth fails"""

    empty_cache = TokenCache()  # empty cache makes silent auth impossible
    transport = Mock(send=Mock(side_effect=Exception("no request should be sent")))
    credential = InteractiveBrowserCredential(
        disable_automatic_authentication=True, transport=transport, _cache=empty_cache
    )

    with patch(WEBBROWSER_OPEN, Mock(side_effect=Exception("credential shouldn't try interactive authentication"))):
        with pytest.raises(AuthenticationRequiredError):
            credential.get_token("scope")


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

    credential = InteractiveBrowserCredential(
        policies=[policy], transport=transport, server_class=server_class, _cache=TokenCache()
    )

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

    credential = InteractiveBrowserCredential(transport=transport, server_class=server_class, _cache=TokenCache())

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

    credential = InteractiveBrowserCredential(
        authority=authority,
        tenant_id=tenant_id,
        client_id=client_id,
        server_class=server_class,
        transport=transport,
        instance_discovery=False,
        validate_authority=False,
        _cache=TokenCache(),
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
        server_class=server_class,
        timeout=timeout,
        transport=transport,
        instance_discovery=False,  # kwargs are passed to MSAL; this one prevents an AAD verification request
        _cache=TokenCache(),
    )

    with pytest.raises(ClientAuthenticationError) as ex:
        credential.get_token("scope")
    assert "timed out" in ex.value.message.lower()


def test_redirect_server():
    # binding a random port prevents races when running the test in parallel
    server = None
    for _ in range(4):
        try:
            port = random.randint(1024, 65535)
            server = AuthCodeRedirectServer(port, timeout=10)
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
    url = "http://127.0.0.1:{}/?{}={}".format(port, expected_param, expected_value)
    response = urllib.request.urlopen(url)

    assert response.code == 200
    assert server.query_params[expected_param] == [expected_value]


@patch("azure.identity._credentials.browser.webbrowser.open", lambda _: False)
def test_no_browser():
    transport = validating_transport(requests=[Request()] * 2, responses=[get_discovery_response()] * 2)
    credential = InteractiveBrowserCredential(
        client_id="client-id", server_class=Mock(), transport=transport, _cache=TokenCache()
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
