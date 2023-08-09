# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest.mock import Mock, patch
from urllib.parse import urlparse

from azure.core.credentials import AccessToken
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import TokenCachePersistenceOptions
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

    async def send(*_, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
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


@pytest.mark.asyncio
async def test_token_cache():
    """the credential should default to an in memory cache, and optionally use a persistent cache"""

    access_token = "token"
    transport = async_validating_transport(
        requests=[Request(), Request()],
        responses=[
            mock_response(json_payload=build_aad_response(access_token=access_token)),
            mock_response(json_payload=build_aad_response(access_token=access_token)),
        ],
    )

    with patch("azure.identity._internal.aad_client_base._load_persistent_cache") as load_persistent_cache:
        with patch("azure.identity._internal.aad_client_base.TokenCache") as mock_token_cache:
            credential = ClientSecretCredential("tenant", "client-id", "secret", transport=transport)
            assert mock_token_cache.call_count == 0
            assert not load_persistent_cache.called

            await credential.get_token("scope")
            assert mock_token_cache.call_count == 1
            assert load_persistent_cache.call_count == 0
            assert credential._client._cache is not None
            assert credential._client._cae_cache is None

            await credential.get_token("scope", enable_cae=True)
            assert mock_token_cache.call_count == 2
            assert load_persistent_cache.call_count == 0
            assert credential._client._cae_cache is not None


@pytest.mark.asyncio
async def test_token_cache_persistent():
    """the credential should use persistent cache if passed in cache options."""

    access_token = "token"
    transport = async_validating_transport(
        requests=[Request(), Request()],
        responses=[
            mock_response(json_payload=build_aad_response(access_token=access_token)),
            mock_response(json_payload=build_aad_response(access_token=access_token)),
        ],
    )

    with patch("azure.identity._internal.aad_client_base._load_persistent_cache") as load_persistent_cache:
        credential = ClientSecretCredential(
            "tenant",
            "client-id",
            "secret",
            cache_persistence_options=TokenCachePersistenceOptions(),
            transport=transport,
        )
        await credential.get_token("scope")
        assert load_persistent_cache.call_count == 1
        assert credential._client._cache is not None
        assert credential._client._cae_cache is None
        args, _ = load_persistent_cache.call_args
        assert args[1] is False

        await credential.get_token("scope", enable_cae=True)
        assert load_persistent_cache.call_count == 2
        assert credential._client._cae_cache is not None
        args, _ = load_persistent_cache.call_args
        assert args[1] is True


@pytest.mark.asyncio
async def test_cache_multiple_clients():
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
    with patch("azure.identity._internal.aad_client_base._load_persistent_cache") as mock_cache_loader:
        mock_cache_loader.return_value = Mock(wraps=cache)
        credential_a = ClientSecretCredential(
            "tenant",
            "client-a",
            "secret",
            transport=transport_a,
            cache_persistence_options=TokenCachePersistenceOptions(),
        )
        assert mock_cache_loader.call_count == 0, "credential should not load the persistent cache yet"

        credential_b = ClientSecretCredential(
            "tenant",
            "client-b",
            "secret",
            transport=transport_b,
            cache_persistence_options=TokenCachePersistenceOptions(),
        )
        assert mock_cache_loader.call_count == 0, "credential should not load the persistent cache yet"

        # A caches a token
        scope = "scope"
        token_a = await credential_a.get_token(scope)
        assert token_a.token == access_token_a
        assert transport_a.send.call_count == 1
        assert mock_cache_loader.call_count == 1
        args, _ = mock_cache_loader.call_args
        assert args[1] is False

        # B should get a different token for the same scope
        token_b = await credential_b.get_token(scope)
        assert token_b.token == access_token_b
        assert transport_b.send.call_count == 1
        assert mock_cache_loader.call_count == 2

        assert len(cache.find(TokenCache.CredentialType.ACCESS_TOKEN)) == 2


@pytest.mark.asyncio
async def test_multitenant_authentication():
    first_tenant = "first-tenant"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    async def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs

        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        assert tenant in (first_tenant, second_tenant), 'unexpected tenant "{}"'.format(tenant)

        token = first_token if tenant == first_tenant else second_token
        return mock_response(json_payload=build_aad_response(access_token=token))

    credential = ClientSecretCredential(
        first_tenant, "client-id", "secret", transport=Mock(send=send), additionally_allowed_tenants=["*"]
    )
    token = await credential.get_token("scope")
    assert token.token == first_token

    token = await credential.get_token("scope", tenant_id=first_tenant)
    assert token.token == first_token

    token = await credential.get_token("scope", tenant_id=second_tenant)
    assert token.token == second_token

    # should still default to the first tenant
    token = await credential.get_token("scope")
    assert token.token == first_token


@pytest.mark.asyncio
async def test_live_multitenant_authentication(live_service_principal):
    # first create a credential with a non-existent tenant
    credential = ClientSecretCredential(
        "...",
        live_service_principal["client_id"],
        live_service_principal["client_secret"],
        additionally_allowed_tenants=["*"],
    )
    # then get a valid token for an actual tenant
    token = await credential.get_token(
        "https://vault.azure.net/.default", tenant_id=live_service_principal["tenant_id"]
    )
    assert token.token
    assert token.expires_on


@pytest.mark.asyncio
async def test_multitenant_authentication_not_allowed():
    expected_tenant = "expected-tenant"
    expected_token = "***"

    async def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        token = expected_token if tenant == expected_tenant else expected_token * 2
        return mock_response(json_payload=build_aad_response(access_token=token))

    credential = ClientSecretCredential(
        expected_tenant, "client-id", "secret", transport=Mock(send=send), additionally_allowed_tenants=["*"]
    )

    token = await credential.get_token("scope")
    assert token.token == expected_token

    token = await credential.get_token("scope", tenant_id=expected_tenant)
    assert token.token == expected_token

    token = await credential.get_token("scope", tenant_id="un" + expected_tenant)
    assert token.token == expected_token * 2

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH: "true"}):
        token = await credential.get_token("scope", tenant_id="un" + expected_tenant)
        assert token.token == expected_token
