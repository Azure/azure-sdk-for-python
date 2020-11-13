# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest.mock import Mock, patch
from urllib.parse import urlparse

from azure.core.credentials import AccessToken
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal.user_agent import USER_AGENT
from azure.identity.aio import ClientSecretCredential
from msal import TokenCache
import pytest

from helpers import build_aad_response, mock_response, Request
from helpers_async import async_validating_transport, AsyncMockTransport, wrap_in_future


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""

    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        ClientSecretCredential(tenant, "client-id", "secret")

    invalid_ids = {"", "my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        with pytest.raises(ValueError):
            ClientSecretCredential(tenant, "client-id", "secret")


@pytest.mark.asyncio
async def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret")
    with pytest.raises(ValueError):
        await credential.get_token()


@pytest.mark.asyncio
async def test_close():
    transport = AsyncMockTransport()
    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret", transport=transport)

    await credential.close()

    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_context_manager():
    transport = AsyncMockTransport()
    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret", transport=transport)

    async with credential:
        assert transport.__aenter__.call_count == 1

    assert transport.__aenter__.call_count == 1
    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    async def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    credential = ClientSecretCredential(
        "tenant-id", "client-id", "client-secret", policies=[ContentDecodePolicy(), policy], transport=Mock(send=send)
    )

    await credential.get_token("scope")

    assert policy.on_request.called


@pytest.mark.asyncio
async def test_user_agent():
    transport = async_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret", transport=transport)

    await credential.get_token("scope")


@pytest.mark.asyncio
async def test_client_secret_credential():
    client_id = "fake-client-id"
    secret = "fake-client-secret"
    tenant_id = "fake-tenant-id"
    access_token = "***"

    transport = async_validating_transport(
        requests=[Request(url_substring=tenant_id, required_data={"client_id": client_id, "client_secret": secret})],
        responses=[
            mock_response(
                json_payload={
                    "token_type": "Bearer",
                    "expires_in": 42,
                    "ext_expires_in": 42,
                    "access_token": access_token,
                }
            )
        ],
    )

    token = await ClientSecretCredential(
        tenant_id=tenant_id, client_id=client_id, client_secret=secret, transport=transport
    ).get_token("scope")

    # not validating expires_on because doing so requires monkeypatching time, and this is tested elsewhere
    assert token.token == access_token


@pytest.mark.asyncio
@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
async def test_request_url(authority):
    """the credential should accept an authority, with or without scheme, as an argument or environment variable"""

    tenant_id = "expected-tenant"
    access_token = "***"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"

    async def mock_send(request, **kwargs):
        actual = urlparse(request.url)
        assert actual.scheme == "https"
        assert actual.netloc == expected_netloc
        assert actual.path.startswith("/" + tenant_id)
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": access_token})

    credential = ClientSecretCredential(
        tenant_id, "client-id", "secret", transport=Mock(send=mock_send), authority=authority
    )
    token = await credential.get_token("scope")
    assert token.token == access_token

    # authority can be configured via environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        credential = ClientSecretCredential(tenant_id, "client-id", "secret", transport=Mock(send=mock_send))
        await credential.get_token("scope")
    assert token.token == access_token


@pytest.mark.asyncio
async def test_cache():
    expired = "this token's expired"
    now = int(time.time())
    expired_on = now - 3600
    expired_token = AccessToken(expired, expired_on)
    token_payload = {
        "access_token": expired,
        "expires_in": 0,
        "ext_expires_in": 0,
        "expires_on": expired_on,
        "not_before": now,
        "token_type": "Bearer",
    }
    mock_send = Mock(return_value=mock_response(json_payload=token_payload))
    transport = Mock(send=wrap_in_future(mock_send))
    scope = "scope"

    credential = ClientSecretCredential("tenant-id", "client-id", "secret", transport=transport)

    # get_token initially returns the expired token because the credential
    # doesn't check whether tokens it receives from the service have expired
    token = await credential.get_token(scope)
    assert token == expired_token

    access_token = "new token"
    token_payload["access_token"] = access_token
    token_payload["expires_on"] = now + 3600
    valid_token = AccessToken(access_token, now + 3600)

    # second call should observe the cached token has expired, and request another
    token = await credential.get_token(scope)
    assert token == valid_token
    assert mock_send.call_count == 2


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


@pytest.mark.asyncio
async def test_persistent_cache_multiple_clients():
    """the credential shouldn't use tokens issued to other service principals"""

    access_token_a = "token a"
    access_token_b = "not " + access_token_a
    transport_a = async_validating_transport(
        requests=[Request()], responses=[mock_response(json_payload=build_aad_response(access_token=access_token_a))]
    )
    transport_b = async_validating_transport(
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
    token_a = await credential_a.get_token(scope)
    assert token_a.token == access_token_a
    assert transport_a.send.call_count == 1

    # B should get a different token for the same scope
    token_b = await credential_b.get_token(scope)
    assert token_b.token == access_token_b
    assert transport_b.send.call_count == 1
