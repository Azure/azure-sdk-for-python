# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import ClientSecretCredential, TokenCachePersistenceOptions
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal.user_agent import USER_AGENT
from msal import TokenCache
import pytest
from six.moves.urllib_parse import urlparse

from helpers import build_aad_response, mock_response, msal_validating_transport, Request, validating_transport

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""

    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        ClientSecretCredential(tenant, "client-id", "secret")

    invalid_ids = {"", "my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        with pytest.raises(ValueError):
            ClientSecretCredential(tenant, "client-id", "secret")


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret")
    with pytest.raises(ValueError):
        credential.get_token()


def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    transport = msal_validating_transport(
        requests=[Request()], responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = ClientSecretCredential(
        "tenant-id", "client-id", "client-secret", policies=[ContentDecodePolicy(), policy], transport=transport
    )

    credential.get_token("scope")

    assert policy.on_request.called


def test_user_agent():
    transport = msal_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret", transport=transport)

    credential.get_token("scope")


def test_client_secret_credential():
    client_id = "fake-client-id"
    secret = "fake-client-secret"
    tenant_id = "fake-tenant-id"
    access_token = "***"

    transport = msal_validating_transport(
        endpoint="https://localhost/" + tenant_id,
        requests=[Request(url_substring=tenant_id, required_data={"client_id": client_id, "client_secret": secret})],
        responses=[mock_response(json_payload=build_aad_response(access_token=access_token))],
    )

    token = ClientSecretCredential(tenant_id, client_id, secret, transport=transport).get_token("scope")

    assert token.token == access_token


@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
def test_authority(authority):
    """the credential should accept an authority, with or without scheme, as an argument or environment variable"""

    tenant_id = "expected-tenant"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority
    expected_authority = "https://{}/{}".format(expected_netloc, tenant_id)

    mock_ctor = Mock(
        return_value=Mock(acquire_token_silent_with_error=lambda *_, **__: {"access_token": "**", "expires_in": 42})
    )

    credential = ClientSecretCredential(tenant_id, "client-id", "secret", authority=authority)
    with patch("msal.ConfidentialClientApplication", mock_ctor):
        # must call get_token because the credential constructs the MSAL application lazily
        credential.get_token("scope")

    assert mock_ctor.call_count == 1
    _, kwargs = mock_ctor.call_args
    assert kwargs["authority"] == expected_authority
    mock_ctor.reset_mock()

    # authority can be configured via environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        credential = ClientSecretCredential(tenant_id, "client-id", "secret")
    with patch("msal.ConfidentialClientApplication", mock_ctor):
        credential.get_token("scope")

    assert mock_ctor.call_count == 1
    _, kwargs = mock_ctor.call_args
    assert kwargs["authority"] == expected_authority


def test_token_cache():
    """the credential should default to an in memory cache, and optionally use a persistent cache"""

    with patch("azure.identity._persistent_cache.msal_extensions") as mock_msal_extensions:
        credential = ClientSecretCredential("tenant", "client-id", "secret")
        assert not mock_msal_extensions.PersistedTokenCache.called
        assert isinstance(credential._cache, TokenCache)

        ClientSecretCredential(
            "tenant", "client-id", "secret", cache_persistence_options=TokenCachePersistenceOptions(),
        )
        assert mock_msal_extensions.PersistedTokenCache.call_count == 1


def test_cache_multiple_clients():
    """the credential shouldn't use tokens issued to other service principals"""

    access_token_a = "token a"
    access_token_b = "not " + access_token_a
    transport_a = msal_validating_transport(
        requests=[Request()], responses=[mock_response(json_payload=build_aad_response(access_token=access_token_a))]
    )
    transport_b = msal_validating_transport(
        requests=[Request()], responses=[mock_response(json_payload=build_aad_response(access_token=access_token_b))]
    )

    cache = TokenCache()
    with patch("azure.identity._internal.msal_credentials._load_persistent_cache") as mock_cache_loader:
        mock_cache_loader.return_value = Mock(wraps=cache)
        credential_a = ClientSecretCredential(
            "tenant",
            "client-a",
            "secret",
            transport=transport_a,
            cache_persistence_options=TokenCachePersistenceOptions(),
        )
        assert mock_cache_loader.call_count == 1, "credential should load the persistent cache"

        credential_b = ClientSecretCredential(
            "tenant",
            "client-b",
            "secret",
            transport=transport_b,
            cache_persistence_options=TokenCachePersistenceOptions(),
        )
        assert mock_cache_loader.call_count == 2, "credential should load the persistent cache"

    # A caches a token
    scope = "scope"
    token_a = credential_a.get_token(scope)
    assert token_a.token == access_token_a
    assert transport_a.send.call_count == 3  # two MSAL discovery requests, one token request

    # B should get a different token for the same scope
    token_b = credential_b.get_token(scope)
    assert token_b.token == access_token_b
    assert transport_b.send.call_count == 3

    assert len(cache.find(TokenCache.CredentialType.ACCESS_TOKEN)) == 2
