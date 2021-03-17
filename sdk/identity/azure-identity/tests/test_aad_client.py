# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import time

from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError
from azure.identity._constants import EnvironmentVariables, DEFAULT_REFRESH_OFFSET, DEFAULT_TOKEN_REFRESH_RETRY_DELAY
from azure.identity._internal import AadClient, AadClientCertificate
from azure.core.credentials import AccessToken

import pytest
from msal import TokenCache
from six.moves.urllib_parse import urlparse

from helpers import build_aad_response, mock_response
from test_certificate_credential import CERT_PATH

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore


def test_error_reporting():
    error_name = "everything's sideways"
    error_description = "something went wrong"
    error_response = {"error": error_name, "error_description": error_description}

    response = mock_response(status_code=403, json_payload=error_response)
    transport = Mock(send=Mock(return_value=response))
    client = AadClient("tenant id", "client id", transport=transport)

    fns = [
        functools.partial(client.obtain_token_by_authorization_code, ("scope",), "code", "uri"),
        functools.partial(client.obtain_token_by_refresh_token, ("scope",), "refresh token"),
    ]

    # exceptions raised for AAD errors should contain AAD's error description
    for fn in fns:
        with pytest.raises(ClientAuthenticationError) as ex:
            fn()
        message = str(ex.value)
        assert error_name in message and error_description in message
        assert transport.send.call_count == 1
        transport.send.reset_mock()


def test_exceptions_do_not_expose_secrets():
    secret = "secret"
    body = {"error": "bad thing", "access_token": secret, "refresh_token": secret}
    response = mock_response(status_code=403, json_payload=body)
    transport = Mock(send=Mock(return_value=response))
    client = AadClient("tenant id", "client id", transport=transport)

    fns = [
        functools.partial(client.obtain_token_by_authorization_code, "code", "uri", "scope"),
        functools.partial(client.obtain_token_by_refresh_token, "refresh token", ("scope"),),
    ]

    def assert_secrets_not_exposed():
        for fn in fns:
            with pytest.raises(ClientAuthenticationError) as ex:
                fn()
            assert secret not in str(ex.value)
            assert secret not in repr(ex.value)
            assert transport.send.call_count == 1
            transport.send.reset_mock()

    # AAD errors shouldn't provoke exceptions exposing secrets
    assert_secrets_not_exposed()

    # neither should unexpected AAD responses
    del body["error"]
    assert_secrets_not_exposed()


@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
def test_request_url(authority):
    tenant_id = "expected-tenant"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"

    def send(request, **_):
        actual = urlparse(request.url)
        assert actual.scheme == "https"
        assert actual.netloc == expected_netloc
        assert actual.path.startswith("/" + tenant_id)
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": "***"})

    client = AadClient(tenant_id, "client id", transport=Mock(send=send), authority=authority)

    client.obtain_token_by_authorization_code("scope", "code", "uri")
    client.obtain_token_by_refresh_token("scope", "refresh token")

    # authority can be configured via environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        client = AadClient(tenant_id=tenant_id, client_id="client id", transport=Mock(send=send))
    client.obtain_token_by_authorization_code("scope", "code", "uri")
    client.obtain_token_by_refresh_token("scope", "refresh token")


@pytest.mark.parametrize("secret", (None, "client secret"))
def test_authorization_code(secret):
    tenant_id = "tenant-id"
    client_id = "client-id"
    auth_code = "code"
    scope = "scope"
    redirect_uri = "https://localhost"
    access_token = "***"

    def send(request, **_):
        assert request.data["client_id"] == client_id
        assert request.data["code"] == auth_code
        assert request.data["grant_type"] == "authorization_code"
        assert request.data["redirect_uri"] == redirect_uri
        assert request.data["scope"] == scope
        assert request.data.get("client_secret") == secret

        return mock_response(json_payload={"access_token": access_token, "expires_in": 42})

    transport = Mock(send=Mock(wraps=send))

    client = AadClient(tenant_id, client_id, transport=transport)
    token = client.obtain_token_by_authorization_code(
        scopes=(scope,), code=auth_code, redirect_uri=redirect_uri, client_secret=secret
    )

    assert token.token == access_token
    assert transport.send.call_count == 1


def test_client_secret():
    tenant_id = "tenant-id"
    client_id = "client-id"
    scope = "scope"
    secret = "refresh-token"
    access_token = "***"

    def send(request, **_):
        assert request.data["client_id"] == client_id
        assert request.data["client_secret"] == secret
        assert request.data["grant_type"] == "client_credentials"
        assert request.data["scope"] == scope

        return mock_response(json_payload={"access_token": access_token, "expires_in": 42})

    transport = Mock(send=Mock(wraps=send))

    client = AadClient(tenant_id, client_id, transport=transport)
    token = client.obtain_token_by_client_secret(scopes=(scope,), secret=secret)

    assert token.token == access_token
    assert transport.send.call_count == 1


def test_refresh_token():
    tenant_id = "tenant-id"
    client_id = "client-id"
    scope = "scope"
    refresh_token = "refresh-token"
    access_token = "***"

    def send(request, **_):
        assert request.data["client_id"] == client_id
        assert request.data["grant_type"] == "refresh_token"
        assert request.data["refresh_token"] == refresh_token
        assert request.data["scope"] == scope

        return mock_response(json_payload={"access_token": access_token, "expires_in": 42})

    transport = Mock(send=Mock(wraps=send))

    client = AadClient(tenant_id, client_id, transport=transport)
    token = client.obtain_token_by_refresh_token(scopes=(scope,), refresh_token=refresh_token)

    assert token.token == access_token
    assert transport.send.call_count == 1


def test_evicts_invalid_refresh_token():
    """when AAD rejects a refresh token, the client should evict that token from its cache"""

    tenant_id = "tenant-id"
    client_id = "client-id"
    invalid_token = "invalid-refresh-token"

    cache = TokenCache()
    cache.add({"response": build_aad_response(uid="id1", utid="tid1", access_token="*", refresh_token=invalid_token)})
    cache.add({"response": build_aad_response(uid="id2", utid="tid2", access_token="*", refresh_token="...")})
    assert len(cache.find(TokenCache.CredentialType.REFRESH_TOKEN)) == 2
    assert len(cache.find(TokenCache.CredentialType.REFRESH_TOKEN, query={"secret": invalid_token})) == 1

    def send(request, **_):
        assert request.data["refresh_token"] == invalid_token
        return mock_response(json_payload={"error": "invalid_grant"}, status_code=400)

    transport = Mock(send=Mock(wraps=send))

    client = AadClient(tenant_id, client_id, transport=transport, cache=cache)
    with pytest.raises(ClientAuthenticationError):
        client.obtain_token_by_refresh_token(scopes=("scope",), refresh_token=invalid_token)

    assert transport.send.call_count == 1
    assert len(cache.find(TokenCache.CredentialType.REFRESH_TOKEN)) == 1
    assert len(cache.find(TokenCache.CredentialType.REFRESH_TOKEN, query={"secret": invalid_token})) == 0


def test_should_refresh():
    client = AadClient("test", "test")
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


def test_retries_token_requests():
    """The client should retry token requests"""

    message = "can't connect"
    transport = Mock(send=Mock(side_effect=ServiceRequestError(message)))
    client = AadClient("tenant-id", "client-id", transport=transport)

    with pytest.raises(ServiceRequestError, match=message):
        client.obtain_token_by_authorization_code("", "", "")
    assert transport.send.call_count > 1
    transport.send.reset_mock()

    with pytest.raises(ServiceRequestError, match=message):
        client.obtain_token_by_client_certificate("", AadClientCertificate(open(CERT_PATH, "rb").read()))
    assert transport.send.call_count > 1
    transport.send.reset_mock()

    with pytest.raises(ServiceRequestError, match=message):
        client.obtain_token_by_client_secret("", "")
    assert transport.send.call_count > 1
    transport.send.reset_mock()

    with pytest.raises(ServiceRequestError, match=message):
        client.obtain_token_by_refresh_token("", "")
    assert transport.send.call_count > 1
    transport.send.reset_mock()
