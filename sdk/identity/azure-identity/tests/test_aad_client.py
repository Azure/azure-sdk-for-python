# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools

from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal import AadClient, AadClientCertificate

import pytest
from msal import TokenCache
from six.moves.urllib_parse import urlparse

from helpers import build_aad_response, mock_response
from test_certificate_credential import PEM_CERT_PATH

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

@pytest.mark.skip(reason="Adding body to HttpResponseError str. Not an issue bc we don't automatically log errors")
def test_exceptions_do_not_expose_secrets():
    secret = "secret"
    body = {"error": "bad thing", "access_token": secret, "refresh_token": secret}
    response = mock_response(status_code=403, json_payload=body)
    transport = Mock(send=Mock(return_value=response))
    client = AadClient("tenant id", "client id", transport=transport)

    fns = [
        functools.partial(client.obtain_token_by_authorization_code, "code", "uri", "scope"),
        functools.partial(
            client.obtain_token_by_refresh_token,
            "refresh token",
            ("scope"),
        ),
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
        client.obtain_token_by_client_certificate("", AadClientCertificate(open(PEM_CERT_PATH, "rb").read()))
    assert transport.send.call_count > 1
    transport.send.reset_mock()

    with pytest.raises(ServiceRequestError, match=message):
        client.obtain_token_by_client_secret("", "")
    assert transport.send.call_count > 1
    transport.send.reset_mock()

    with pytest.raises(ServiceRequestError, match=message):
        client.obtain_token_by_jwt_assertion("", "")
    assert transport.send.call_count > 1
    transport.send.reset_mock()

    with pytest.raises(ServiceRequestError, match=message):
        client.obtain_token_by_refresh_token("", "")
    assert transport.send.call_count > 1


def test_shared_cache():
    """The client should return only tokens associated with its own client_id"""

    client_id_a = "client-id-a"
    client_id_b = "client-id-b"
    scope = "scope"
    expected_token = "***"
    tenant_id = "tenant"
    authority = "https://localhost/" + tenant_id

    cache = TokenCache()
    cache.add(
        {
            "response": build_aad_response(access_token=expected_token),
            "client_id": client_id_a,
            "scope": [scope],
            "token_endpoint": "/".join((authority, tenant_id, "oauth2/v2.0/token")),
        }
    )

    common_args = dict(authority=authority, cache=cache, tenant_id=tenant_id)
    client_a = AadClient(client_id=client_id_a, **common_args)
    client_b = AadClient(client_id=client_id_b, **common_args)

    # A has a cached token
    token = client_a.get_cached_access_token([scope])
    assert token.token == expected_token

    # which B shouldn't return
    assert client_b.get_cached_access_token([scope]) is None


def test_multitenant_cache():
    client_id = "client-id"
    scope = "scope"
    expected_token = "***"
    tenant_a = "tenant-a"
    tenant_b = "tenant-b"
    tenant_c = "tenant-c"
    tenant_d = "tenant-d"
    authority = "https://localhost/" + tenant_a
    message = "additionally_allowed_tenants"

    cache = TokenCache()
    cache.add(
        {
            "response": build_aad_response(access_token=expected_token),
            "client_id": client_id,
            "scope": [scope],
            "token_endpoint": "/".join((authority, tenant_a, "oauth2/v2.0/token")),
        }
    )

    common_args = dict(authority=authority, cache=cache, client_id=client_id)
    client_a = AadClient(tenant_id=tenant_a, **common_args)
    client_b = AadClient(tenant_id=tenant_b, **common_args)

    # A has a cached token
    token = client_a.get_cached_access_token([scope])
    assert token.token == expected_token

    # which B shouldn't return
    assert client_b.get_cached_access_token([scope]) is None

    # but C allows multitenant auth and should therefore return the token from tenant_a when appropriate
    client_c = AadClient(tenant_id=tenant_c, additionally_allowed_tenants=['*'], **common_args)
    assert client_c.get_cached_access_token([scope]) is None
    token = client_c.get_cached_access_token([scope], tenant_id=tenant_a)
    assert token.token == expected_token

    # but d does not add target tenant into allowed list therefore fail
    client_d = AadClient(tenant_id=tenant_d, **common_args)
    assert client_d.get_cached_access_token([scope]) is None
    with pytest.raises(ClientAuthenticationError, match=message):
        client_d.get_cached_access_token([scope], tenant_id=tenant_a)
