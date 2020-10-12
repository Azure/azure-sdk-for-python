# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import ClientSecretCredential
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


def test_enable_persistent_cache():
    """the credential should use the persistent cache only when given _enable_persistent_cache=True"""

    required_arguments = ("tenant-id", "client-id", "secret")
    persistent_cache = "azure.identity._internal.persistent_cache"

    # credential should default to an in memory cache
    raise_when_called = Mock(side_effect=Exception("credential shouldn't attempt to load a persistent cache"))
    with patch(persistent_cache + "._load_persistent_cache", raise_when_called):
        ClientSecretCredential(*required_arguments)

        # allowing an unencrypted cache doesn't count as opting in to the persistent cache
        ClientSecretCredential(*required_arguments, _allow_unencrypted_cache=True)

    # keyword argument opts in to persistent cache
    with patch(persistent_cache + ".msal_extensions") as mock_extensions:
        ClientSecretCredential(*required_arguments, _enable_persistent_cache=True)
    assert mock_extensions.PersistedTokenCache.call_count == 1

    # opting in on an unsupported platform raises an exception
    with patch(persistent_cache + ".sys.platform", "commodore64"):
        with pytest.raises(NotImplementedError):
            ClientSecretCredential(*required_arguments, _enable_persistent_cache=True)
        with pytest.raises(NotImplementedError):
            ClientSecretCredential(*required_arguments, _enable_persistent_cache=True, _allow_unencrypted_cache=True)


@patch("azure.identity._internal.persistent_cache.sys.platform", "linux2")
@patch("azure.identity._internal.persistent_cache.msal_extensions")
def test_persistent_cache_linux(mock_extensions):
    """The credential should use an unencrypted cache when encryption is unavailable and the user explicitly opts in.

    This test was written when Linux was the only platform on which encryption may not be available.
    """

    required_arguments = ("tenant-id", "client-id", "secret")

    # the credential should prefer an encrypted cache even when the user allows an unencrypted one
    ClientSecretCredential(*required_arguments, _enable_persistent_cache=True, _allow_unencrypted_cache=True)
    assert mock_extensions.PersistedTokenCache.called_with(mock_extensions.LibsecretPersistence)
    mock_extensions.PersistedTokenCache.reset_mock()

    # (when LibsecretPersistence's dependencies aren't available, constructing it raises ImportError)
    mock_extensions.LibsecretPersistence = Mock(side_effect=ImportError)

    # encryption unavailable, no opt in to unencrypted cache -> credential should raise
    with pytest.raises(ValueError):
        ClientSecretCredential(*required_arguments, _enable_persistent_cache=True)

    ClientSecretCredential(*required_arguments, _enable_persistent_cache=True, _allow_unencrypted_cache=True)
    assert mock_extensions.PersistedTokenCache.called_with(mock_extensions.FilePersistence)


def test_persistent_cache_multiple_clients():
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
    with patch("azure.identity._internal.persistent_cache._load_persistent_cache") as mock_cache_loader:
        mock_cache_loader.return_value = Mock(wraps=cache)
        credential_a = ClientSecretCredential(
            "tenant-id", "client-a", "...", _enable_persistent_cache=True, transport=transport_a
        )
        assert mock_cache_loader.call_count == 1, "credential should load the persistent cache"
        credential_b = ClientSecretCredential(
            "tenant-id", "client-b", "...", _enable_persistent_cache=True, transport=transport_b
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
