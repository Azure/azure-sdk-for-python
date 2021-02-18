# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""These tests use the synchronous AuthnClient as a driver to test functionality
of the sans I/O AuthnClientBase shared with AsyncAuthnClient."""
import json
import time

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

from azure.core.credentials import AccessToken
from azure.identity._authn_client import AuthnClient
from azure.identity._constants import EnvironmentVariables, DEFAULT_REFRESH_OFFSET, DEFAULT_TOKEN_REFRESH_RETRY_DELAY
import pytest
from six.moves.urllib_parse import urlparse
from helpers import mock_response


def test_deserialization_expires_integers():
    now = 6
    expires_in = 59 - now
    expires_on = now + expires_in
    access_token = "***"
    expected_access_token = AccessToken(access_token, expires_on)
    scope = "scope"

    # response with expires_on only
    token_payload = {"access_token": access_token, "expires_on": expires_on, "token_type": "Bearer", "resource": scope}
    mock_send = Mock(return_value=mock_response(json_payload=token_payload))
    token = AuthnClient(endpoint="http://foo", transport=Mock(send=mock_send)).request_token(scope)
    assert token == expected_access_token

    # response with expires_in as well
    token_payload = {
        "access_token": access_token,
        "expires_in": expires_in,
        "token_type": "Bearer",
        "ext_expires_in": expires_in,
    }
    with patch(AuthnClient.__module__ + ".time.time") as mock_time:
        mock_time.return_value = now
        mock_send = Mock(return_value=mock_response(json_payload=token_payload))
        token = AuthnClient(endpoint="http://foo", transport=Mock(send=mock_send)).request_token(scope)
        assert token == expected_access_token


def test_deserialization_app_service_msi():
    now = 6
    expires_in = 59 - now
    expires_on = now + expires_in
    access_token = "***"
    expected_access_token = AccessToken(access_token, expires_on)
    scope = "scope"

    # response with expires_on only and it's a datetime string (App Service MSI, Linux)
    token_payload = {
        "access_token": access_token,
        "expires_on": "01/01/1970 00:00:{} +00:00".format(now + expires_in),
        "token_type": "Bearer",
        "resource": scope,
    }
    mock_send = Mock(return_value=mock_response(json_payload=token_payload))
    token = AuthnClient(endpoint="http://foo", transport=Mock(send=mock_send)).request_token(scope)
    assert token == expected_access_token


def test_deserialization_expires_strings():
    now = 6
    expires_in = 59 - now
    expires_on = now + expires_in
    access_token = "***"
    expected_access_token = AccessToken(access_token, expires_on)
    scope = "scope"

    # response with string expires_in and expires_on (IMDS, Cloud Shell)
    token_payload = {
        "access_token": access_token,
        "expires_in": str(expires_in),
        "ext_expires_in": str(expires_in),
        "expires_on": str(expires_on),
        "token_type": "Bearer",
        "resource": scope,
    }
    mock_send = Mock(return_value=mock_response(json_payload=token_payload))
    token = AuthnClient(endpoint="http://foo", transport=Mock(send=mock_send)).request_token(scope)
    assert token == expected_access_token


def test_caching_when_only_expires_in_set():
    """the cache should function when auth responses don't include an explicit expires_on"""

    access_token = "token"
    now = 42
    expires_in = 1800
    expires_on = now + expires_in
    expected_token = AccessToken(access_token, expires_on)

    mock_send = Mock(
        return_value=mock_response(
            json_payload={"access_token": access_token, "expires_in": expires_in, "token_type": "Bearer"}
        )
    )

    client = AuthnClient(endpoint="http://foo", transport=Mock(send=mock_send))
    with patch("azure.identity._authn_client.time.time") as mock_time:
        mock_time.return_value = 42
        token = client.request_token(["scope"])
        assert token.token == expected_token.token
        assert token.expires_on == expected_token.expires_on

        cached_token = client.get_cached_token(["scope"])
        assert cached_token == expected_token


def test_expires_in_strings():
    expected_token = "token"

    mock_send = Mock(
        return_value=mock_response(
            json_payload={
                "access_token": expected_token,
                "expires_in": "42",
                "ext_expires_in": "42",
                "token_type": "Bearer",
            }
        )
    )

    now = int(time.time())
    with patch("azure.identity._authn_client.time.time") as mock_time:
        mock_time.return_value = now
        token = AuthnClient(endpoint="http://foo", transport=Mock(send=mock_send)).request_token("scope")
    assert token.token == expected_token
    assert token.expires_on == now + 42


def test_cache_expiry():
    access_token = "token"
    now = 42
    expires_in = 1800
    expires_on = now + expires_in
    expected_token = AccessToken(access_token, expires_on)
    token_payload = {"access_token": access_token, "expires_in": expires_in, "token_type": "Bearer"}
    mock_send = Mock(return_value=mock_response(json_payload=token_payload))

    client = AuthnClient(endpoint="http://foo", transport=Mock(send=mock_send))
    with patch("azure.identity._authn_client.time.time") as mock_time:
        # populate the cache with a valid token
        mock_time.return_value = now
        token = client.request_token("scope")
        assert token.token == expected_token.token
        assert token.expires_on == expected_token.expires_on

        cached_token = client.get_cached_token("scope")
        assert cached_token == expected_token

        # advance time past the cached token's expires_on
        mock_time.return_value = expires_on + 3600
        cached_token = client.get_cached_token("scope")
        assert not cached_token

        # request a new token
        new_token = "new token"
        token_payload["access_token"] = new_token
        token = client.request_token("scope")
        assert token.token == new_token

        # it should be cached
        cached_token = client.get_cached_token("scope")
        assert cached_token.token == new_token


def test_cache_scopes():
    scope_a = "scope_a"
    scope_b = "scope_b"
    scope_ab = scope_a + " " + scope_b
    expected_tokens = {
        scope_a: {"access_token": scope_a, "expires_in": 1 << 31, "ext_expires_in": 1 << 31, "token_type": "Bearer"},
        scope_b: {"access_token": scope_b, "expires_in": 1 << 31, "ext_expires_in": 1 << 31, "token_type": "Bearer"},
        scope_ab: {"access_token": scope_ab, "expires_in": 1 << 31, "ext_expires_in": 1 << 31, "token_type": "Bearer"},
    }

    def mock_send(request, **kwargs):
        token = expected_tokens[request.data["resource"]]
        return mock_response(json_payload=token)

    client = AuthnClient(endpoint="http://foo", transport=Mock(send=mock_send))

    # if the cache has a token for a & b, it should hit for a, b, a & b
    token = client.request_token([scope_a, scope_b], form_data={"resource": scope_ab})
    assert token.token == scope_ab
    for scope in (scope_a, scope_b):
        assert client.get_cached_token([scope]).token == scope_ab
    assert client.get_cached_token([scope_a, scope_b]).token == scope_ab

    # if the cache has only tokens for a and b alone, a & b should miss
    client = AuthnClient(endpoint="http://foo", transport=Mock(send=mock_send))
    for scope in (scope_a, scope_b):
        token = client.request_token([scope], form_data={"resource": scope})
        assert token.token == scope
        assert client.get_cached_token([scope]).token == scope
    assert not client.get_cached_token([scope_a, scope_b])


@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
def test_request_url(authority):
    tenant_id = "expected-tenant"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"

    def validate_url(url):
        actual = urlparse(url)
        assert actual.scheme == "https"
        assert actual.netloc == expected_netloc
        assert actual.path.startswith("/" + tenant_id)

    def mock_send(request, **kwargs):
        validate_url(request.url)
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": "***"})

    client = AuthnClient(tenant=tenant_id, transport=Mock(send=mock_send), authority=authority)
    client.request_token(("scope",))
    request = client.get_refresh_token_grant_request({"secret": "***"}, "scope")
    validate_url(request.url)

    # authority can be configured via environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        client = AuthnClient(tenant=tenant_id, transport=Mock(send=mock_send))
        client.request_token(("scope",))
        request = client.get_refresh_token_grant_request({"secret": "***"}, "scope")
        validate_url(request.url)


def test_should_refresh():
    client = AuthnClient(endpoint="http://foo")
    now = int(time.time())

    # do not need refresh
    token = AccessToken("token", now + DEFAULT_REFRESH_OFFSET + 1)
    should_refresh = client.should_refresh(token)
    assert not should_refresh

    # need refresh
    token = AccessToken("token", now + DEFAULT_REFRESH_OFFSET - 1)
    should_refresh = client.should_refresh(token)
    assert should_refresh

    # not exceed cool down time, do not refresh
    token = AccessToken("token", now + DEFAULT_REFRESH_OFFSET - 1)
    client._last_refresh_time = now - DEFAULT_TOKEN_REFRESH_RETRY_DELAY + 1
    should_refresh = client.should_refresh(token)
    assert not should_refresh
