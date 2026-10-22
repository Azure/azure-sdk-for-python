# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from itertools import product
from urllib.parse import urlparse
from unittest.mock import Mock, patch

from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import ClientSecretCredential, TokenCachePersistenceOptions
from azure.identity._enums import RegionalAuthority
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal.user_agent import USER_AGENT
from msal import TokenCache
import msal
import pytest

from helpers import (
    build_aad_response,
    build_id_token,
    get_discovery_response,
    id_token_claims,
    mock_response,
    new_msal_validating_transport,
    Request,
    GET_TOKEN_METHODS,
)


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""

    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        ClientSecretCredential(tenant, "client-id", "secret")

    invalid_ids = {"", "my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        with pytest.raises(ValueError):
            ClientSecretCredential(tenant, "client-id", "secret")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret")
    with pytest.raises(ValueError):
        getattr(credential, get_token_method)()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_policies_configurable(get_token_method):
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    transport = new_msal_validating_transport(
        requests=[Request()], responses=[mock_response(json_payload=build_aad_response(access_token="**"))]
    )

    credential = ClientSecretCredential(
        "tenant-id", "client-id", "client-secret", policies=[ContentDecodePolicy(), policy], transport=transport
    )

    getattr(credential, get_token_method)("scope")

    assert policy.on_request.called


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_user_agent(get_token_method):
    transport = new_msal_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret", transport=transport)

    getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_client_secret_credential(get_token_method):
    client_id = "fake-client-id"
    secret = "fake-client-secret"
    tenant_id = "fake-tenant-id"
    access_token = "***"

    transport = new_msal_validating_transport(
        endpoint="https://localhost/" + tenant_id,
        requests=[Request(url_substring=tenant_id, required_data={"client_id": client_id, "client_secret": secret})],
        responses=[mock_response(json_payload=build_aad_response(access_token=access_token))],
    )

    token = getattr(ClientSecretCredential(tenant_id, client_id, secret, transport=transport), get_token_method)(
        "scope"
    )

    assert token.token == access_token


@pytest.mark.parametrize("authority,get_token_method", product(("localhost", "https://localhost"), GET_TOKEN_METHODS))
def test_authority(authority, get_token_method):
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
        getattr(credential, get_token_method)("scope")

    assert mock_ctor.call_count == 1
    _, kwargs = mock_ctor.call_args
    assert kwargs["authority"] == expected_authority
    mock_ctor.reset_mock()

    # authority can be configured via environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        credential = ClientSecretCredential(tenant_id, "client-id", "secret")
    with patch("msal.ConfidentialClientApplication", mock_ctor):
        getattr(credential, get_token_method)("scope")

    assert mock_ctor.call_count == 1
    _, kwargs = mock_ctor.call_args
    assert kwargs["authority"] == expected_authority


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_regional_authority(get_token_method):
    """the credential should configure MSAL with a regional authority specified via kwarg or environment variable"""

    mock_confidential_client = Mock(
        return_value=Mock(acquire_token_silent_with_error=lambda *_, **__: {"access_token": "**", "expires_in": 3600})
    )

    for region in RegionalAuthority:
        mock_confidential_client.reset_mock()

        # region can be configured via environment variable
        with patch.dict("os.environ", {EnvironmentVariables.AZURE_REGIONAL_AUTHORITY_NAME: region.value}, clear=True):
            credential = ClientSecretCredential("tenant", "client-id", "secret")
        with patch("msal.ConfidentialClientApplication", mock_confidential_client):
            getattr(credential, get_token_method)("scope")

        assert mock_confidential_client.call_count == 1
        _, kwargs = mock_confidential_client.call_args
        if region == RegionalAuthority.AUTO_DISCOVER_REGION:
            assert kwargs["azure_region"] == msal.ConfidentialClientApplication.ATTEMPT_REGION_DISCOVERY
        else:
            assert kwargs["azure_region"] == region.value


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_token_cache_persistent(get_token_method):
    """the credential should use a persistent cache if cache_persistence_options are configured"""

    access_token = "foo token"

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))
        return mock_response(json_payload=build_aad_response(access_token=access_token))

    with patch("azure.identity._internal.msal_credentials._load_persistent_cache") as load_persistent_cache:
        credential = ClientSecretCredential(
            "tenant",
            "client-id",
            "secret",
            cache_persistence_options=TokenCachePersistenceOptions(),
            transport=Mock(send=send),
        )

        assert load_persistent_cache.call_count == 0
        assert credential._cache is None
        assert credential._cae_cache is None

        token = getattr(credential, get_token_method)("scope")
        assert token.token == access_token
        assert load_persistent_cache.call_count == 1
        assert credential._cache is not None
        assert credential._cae_cache is None

        kwargs = {"enable_cae": True}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = getattr(credential, get_token_method)("scope", **kwargs)
        assert load_persistent_cache.call_count == 2
        assert credential._cae_cache is not None


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_token_cache_memory(get_token_method):
    """The credential should default to in-memory cache if no persistence options are provided."""
    access_token = "foo token"

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))
        return mock_response(json_payload=build_aad_response(access_token=access_token))

    with patch("azure.identity._internal.msal_credentials._load_persistent_cache") as load_persistent_cache:
        credential = ClientSecretCredential("tenant", "client-id", "secret", transport=Mock(send=send))

        assert credential._cache is None
        token = getattr(credential, get_token_method)("scope")
        assert token.token == access_token
        assert isinstance(credential._cache, TokenCache)
        assert credential._cae_cache is None
        assert not load_persistent_cache.called

        kwargs = {"enable_cae": True}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = getattr(credential, get_token_method)("scope", **kwargs)
        assert isinstance(credential._cae_cache, TokenCache)
        assert not load_persistent_cache.called


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_cache_multiple_clients(get_token_method):
    """the credential shouldn't use tokens issued to other service principals"""

    access_token_a = "token a"
    access_token_b = "not " + access_token_a
    transport_a = new_msal_validating_transport(
        requests=[Request()], responses=[mock_response(json_payload=build_aad_response(access_token=access_token_a))]
    )
    transport_b = new_msal_validating_transport(
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

        credential_b = ClientSecretCredential(
            "tenant",
            "client-b",
            "secret",
            transport=transport_b,
            cache_persistence_options=TokenCachePersistenceOptions(),
        )

        # A caches a token
        scope = "scope"
        token_a = getattr(credential_a, get_token_method)(scope)
        assert mock_cache_loader.call_count == 1
        assert token_a.token == access_token_a
        assert transport_a.send.call_count == 2  # one MSAL discovery request, one token request

        # B should get a different token for the same scope
        token_b = getattr(credential_b, get_token_method)(scope)
        assert mock_cache_loader.call_count == 2
        assert token_b.token == access_token_b
        assert transport_b.send.call_count == 2

        assert len(list(cache.search(TokenCache.CredentialType.ACCESS_TOKEN))) == 2


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_multitenant_authentication(get_token_method):
    first_tenant = "first-tenant"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs

        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        assert tenant in (first_tenant, second_tenant, "common"), 'unexpected tenant "{}"'.format(tenant)
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))

        token = first_token if tenant == first_tenant else second_token
        return mock_response(json_payload=build_aad_response(access_token=token))

    credential = ClientSecretCredential(
        first_tenant, "client-id", "secret", transport=Mock(send=send), additionally_allowed_tenants=["*"]
    )
    token = getattr(credential, get_token_method)("scope")
    assert token.token == first_token

    kwargs = {"tenant_id": first_tenant}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    token = getattr(credential, get_token_method)("scope", **kwargs)
    assert token.token == first_token

    kwargs = {"tenant_id": second_tenant}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    token = getattr(credential, get_token_method)("scope", **kwargs)
    assert token.token == second_token

    # should still default to the first tenant
    token = getattr(credential, get_token_method)("scope")
    assert token.token == first_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_live_multitenant_authentication(live_service_principal, get_token_method):
    # first create a credential with a non-existent tenant
    credential = ClientSecretCredential(
        "...",
        live_service_principal["client_id"],
        live_service_principal["client_secret"],
        additionally_allowed_tenants=["*"],
    )
    kwargs = {"tenant_id": live_service_principal["tenant_id"]}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    # then get a valid token for an actual tenant
    token = getattr(credential, get_token_method)("https://vault.azure.net/.default", **kwargs)
    assert token.token
    assert token.expires_on


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_multitenant_authentication_not_allowed(get_token_method):
    expected_tenant = "expected-tenant"
    expected_token = "***"

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, expected_tenant))

        tenant = parsed.path.split("/")[1]
        token = expected_token if tenant == expected_tenant else expected_token * 2
        return mock_response(json_payload=build_aad_response(access_token=token))

    credential = ClientSecretCredential(expected_tenant, "client-id", "secret", transport=Mock(send=send))

    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_token

    kwargs = {"tenant_id": expected_tenant}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    token = getattr(credential, get_token_method)("scope", **kwargs)
    assert token.token == expected_token

    kwargs = {"tenant_id": "un" + expected_tenant}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH: "true"}):
        token = getattr(credential, get_token_method)("scope", **kwargs)
        assert token.token == expected_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_client_capabilities(get_token_method):
    """The credential should configure MSAL for capability only if enable_cae is passed in."""

    transport = Mock(send=Mock(side_effect=Exception("this test mocks MSAL, so no request should be sent")))

    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret", transport=transport)
    with patch("msal.ConfidentialClientApplication") as ConfidentialClientApplication:
        credential._get_app()

        assert ConfidentialClientApplication.call_count == 1
        _, kwargs = ConfidentialClientApplication.call_args
        assert kwargs["client_capabilities"] == None

        credential._get_app(enable_cae=True)
        assert ConfidentialClientApplication.call_count == 2
        _, kwargs = ConfidentialClientApplication.call_args
        assert kwargs["client_capabilities"] == ["CP1"]


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_claims_challenge(get_token_method):
    """get_token should pass any claims challenge to MSAL token acquisition APIs"""

    msal_acquire_token_result = dict(
        build_aad_response(access_token="**", id_token=build_id_token()),
        id_token_claims=id_token_claims("issuer", "subject", "audience", upn="upn"),
    )
    expected_claims = '{"access_token": {"essential": "true"}}'

    transport = Mock(send=Mock(side_effect=Exception("this test mocks MSAL, so no request should be sent")))
    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret", transport=transport)
    with patch.object(ClientSecretCredential, "_get_app") as get_mock_app:
        msal_app = get_mock_app()
        msal_app.acquire_token_silent_with_error.return_value = None
        msal_app.acquire_token_for_client.return_value = msal_acquire_token_result

        kwargs = {"claims": expected_claims}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        getattr(credential, get_token_method)("scope", **kwargs)

        assert msal_app.acquire_token_silent_with_error.call_count == 1
        args, kwargs = msal_app.acquire_token_silent_with_error.call_args
        assert kwargs["claims_challenge"] == expected_claims

        assert msal_app.acquire_token_for_client.call_count == 1
        args, kwargs = msal_app.acquire_token_for_client.call_args
        assert kwargs["claims_challenge"] == expected_claims


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_msal_kwargs_filtered(get_token_method):
    msal_acquire_token_result = dict(
        build_aad_response(access_token="**", id_token=build_id_token()),
        id_token_claims=id_token_claims("issuer", "subject", "audience", upn="upn"),
    )
    expected_claims = '{"access_token": {"essential": "true"}}'
    transport = Mock(send=Mock(side_effect=Exception("this test mocks MSAL, so no request should be sent")))
    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret", transport=transport)
    with patch.object(ClientSecretCredential, "_get_app") as get_mock_app:
        msal_app = get_mock_app()
        msal_app.acquire_token_silent_with_error.return_value = None
        msal_app.acquire_token_for_client.return_value = msal_acquire_token_result

        kwargs = {"claims": expected_claims, "enable_cae": True}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        getattr(credential, get_token_method)("scope", **kwargs)

        assert msal_app.acquire_token_silent_with_error.call_count == 1
        _, kwargs = msal_app.acquire_token_silent_with_error.call_args
        assert kwargs["claims_challenge"] == expected_claims
        assert "enable_cae" not in kwargs
