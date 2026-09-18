# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest.mock import Mock, patch
from urllib.parse import urlparse

from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.identity import AuthorizationCodeCredential
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal.user_agent import USER_AGENT
import msal
import pytest

from helpers import build_aad_response, mock_response, Request, validating_transport, GET_TOKEN_METHODS


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = AuthorizationCodeCredential("tenant-id", "client-id", "auth-code", "http://localhost")
    with pytest.raises(ValueError):
        getattr(credential, get_token_method)()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_policies_configurable(get_token_method):
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    def send(*_, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        return mock_response(json_payload=build_aad_response(access_token="**"))

    credential = AuthorizationCodeCredential(
        "tenant-id", "client-id", "auth-code", "http://localhost", policies=[policy], transport=Mock(send=send)
    )

    getattr(credential, get_token_method)("scope")

    assert policy.on_request.called


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_user_agent(get_token_method):
    transport = validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = AuthorizationCodeCredential(
        "tenant-id", "client-id", "auth-code", "http://localhost", transport=transport
    )

    getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_tenant_id(get_token_method):
    transport = validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = AuthorizationCodeCredential(
        "tenant-id",
        "client-id",
        "auth-code",
        "http://localhost",
        transport=transport,
        additionally_allowed_tenants=["*"],
    )

    kwargs = {"tenant_id": "tenant_id"}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    getattr(credential, get_token_method)("scope", **kwargs)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
@pytest.mark.parametrize("enable_cae", [True, False])
def test_auth_code_credential(get_token_method, enable_cae):
    client_id = "client id"
    secret = "fake-client-secret"
    tenant_id = "tenant"
    expected_code = "auth code"
    redirect_uri = "https://localhost"
    expected_access_token = "access"
    expected_refresh_token = "refresh"
    expected_scope = "scope"

    auth_response = build_aad_response(
        access_token=expected_access_token, refresh_token=expected_refresh_token, uid="uid", utid="utid"
    )
    transport = validating_transport(
        requests=[
            Request(  # first call should redeem the auth code
                url_substring=tenant_id,
                required_data={
                    "client_id": client_id,
                    "client_secret": secret,
                    "code": expected_code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                    "scope": expected_scope,
                },
            ),
            Request(  # third call should redeem the refresh token
                url_substring=tenant_id,
                required_data={
                    "client_id": client_id,
                    "client_secret": secret,
                    "grant_type": "refresh_token",
                    "refresh_token": expected_refresh_token,
                    "scope": expected_scope,
                },
            ),
        ],
        responses=[mock_response(json_payload=auth_response)] * 2,
    )
    cache = msal.TokenCache()
    cae_cache = msal.TokenCache()

    credential = AuthorizationCodeCredential(
        client_id=client_id,
        client_secret=secret,
        tenant_id=tenant_id,
        authorization_code=expected_code,
        redirect_uri=redirect_uri,
        transport=transport,
        cache=cache,
        cae_cache=cae_cache,
    )

    # first call should redeem the auth code
    kwargs = {"enable_cae": enable_cae}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    token = getattr(credential, get_token_method)(expected_scope, **kwargs)
    assert token.token == expected_access_token
    assert transport.send.call_count == 1

    # no auth code -> credential should return cached token
    token = getattr(credential, get_token_method)(expected_scope, **kwargs)
    assert token.token == expected_access_token
    assert transport.send.call_count == 1

    # no auth code, no cached token -> credential should redeem refresh token
    cache_being_used = cae_cache if enable_cae else cache
    cached_tokens = list(cache_being_used.search(cache_being_used.CredentialType.ACCESS_TOKEN))
    assert cached_tokens
    cached_access_token = cached_tokens[0]
    cache_being_used.remove_at(cached_access_token)
    token = getattr(credential, get_token_method)(expected_scope, **kwargs)
    assert token.token == expected_access_token
    assert transport.send.call_count == 2


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
        assert tenant in (first_tenant, second_tenant), 'unexpected tenant "{}"'.format(tenant)
        token = first_token if tenant == first_tenant else second_token
        return mock_response(
            json_payload=build_aad_response(access_token=token, refresh_token="**", uid="uid", utid="utid")
        )

    credential = AuthorizationCodeCredential(
        first_tenant,
        "client-id",
        "authcode",
        "https://localhost",
        transport=Mock(send=send),
        additionally_allowed_tenants=["*"],
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
def test_multitenant_authentication_not_allowed(get_token_method):
    expected_tenant = "expected-tenant"
    expected_token = "***"

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        token = expected_token if tenant == expected_tenant else expected_token * 2
        return mock_response(
            json_payload=build_aad_response(access_token=token, refresh_token="**", uid="uid", utid="utid")
        )

    credential = AuthorizationCodeCredential(
        expected_tenant,
        "client-id",
        "authcode",
        "https://localhost",
        transport=Mock(send=send),
        additionally_allowed_tenants=["*"],
    )

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
    token = getattr(credential, get_token_method)("scope", **kwargs)
    assert token.token == expected_token * 2

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH: "true"}):
        kwargs = {"tenant_id": "un" + expected_tenant}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = getattr(credential, get_token_method)("scope", **kwargs)
        assert token.token == expected_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_cross_user_token_from_shared_cache(get_token_method):
    """A credential holding an unredeemed authorization code must not return another account's cached token.

    Regression test for AZSDK-H03: when multiple AuthorizationCodeCredential instances share a token cache (e.g. a
    persistent cache), a credential constructed with user B's authorization code must redeem that code and return
    B's token rather than returning a token already cached for a different account (user A).
    """

    shared_cache = msal.TokenCache()
    tenant_id = "tenant-id"
    client_id = "client-id"

    def make_send(expected_code, access_token, uid, redeemed):
        def send(request, **kwargs):
            if request.body.get("code") == expected_code:
                redeemed.append(True)
            return mock_response(json_payload=build_aad_response(access_token=access_token, uid=uid, utid="utid"))

        return send

    # user A redeems its code first, populating the shared cache with A's token
    a_redeemed = []
    credential_a = AuthorizationCodeCredential(
        tenant_id,
        client_id,
        "CODE-A",
        "https://localhost",
        transport=Mock(send=make_send("CODE-A", "ACCESS-TOKEN-A", "uid-a", a_redeemed)),
        cache=shared_cache,
    )
    token_a = getattr(credential_a, get_token_method)("scope")
    assert token_a.token == "ACCESS-TOKEN-A"
    assert a_redeemed

    # user B's credential shares the cache but hasn't redeemed its own code yet
    b_redeemed = []
    credential_b = AuthorizationCodeCredential(
        tenant_id,
        client_id,
        "CODE-B",
        "https://localhost",
        transport=Mock(send=make_send("CODE-B", "ACCESS-TOKEN-B", "uid-b", b_redeemed)),
        cache=shared_cache,
    )
    token_b = getattr(credential_b, get_token_method)("scope")

    assert token_b.token == "ACCESS-TOKEN-B", "credential returned another account's cached token"
    assert b_redeemed, "credential did not redeem its own authorization code"


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_cross_user_refresh_token_from_shared_cache(get_token_method):
    """A credential must not use another account's cached refresh token either.

    After B's initial exchange establishes its account, removing B's cached access token should cause the
    credential to redeem a refresh token bound to B's account rather than one belonging to A.
    """

    shared_cache = msal.TokenCache()
    tenant_id = "tenant-id"
    client_id = "client-id"

    def make_send(user, access_token, refresh_token, redemptions):
        def send(request, **kwargs):
            body = request.body
            if body.get("grant_type") == "authorization_code":
                redemptions.append(("code", user))
            elif body.get("grant_type") == "refresh_token":
                assert body["refresh_token"] == refresh_token, "used another account's refresh token"
                redemptions.append(("refresh_token", user))
            return mock_response(
                json_payload=build_aad_response(
                    access_token=access_token, refresh_token=refresh_token, uid="uid-" + user, utid="utid"
                )
            )

        return send

    a_events = []
    credential_a = AuthorizationCodeCredential(
        tenant_id,
        client_id,
        "CODE-A",
        "https://localhost",
        transport=Mock(send=make_send("a", "ACCESS-TOKEN-A", "REFRESH-TOKEN-A", a_events)),
        cache=shared_cache,
    )
    getattr(credential_a, get_token_method)("scope")

    b_events = []
    credential_b = AuthorizationCodeCredential(
        tenant_id,
        client_id,
        "CODE-B",
        "https://localhost",
        transport=Mock(send=make_send("b", "ACCESS-TOKEN-B", "REFRESH-TOKEN-B", b_events)),
        cache=shared_cache,
    )
    token_b = getattr(credential_b, get_token_method)("scope")
    assert token_b.token == "ACCESS-TOKEN-B"

    # remove B's cached access token so the credential must fall back to a cached refresh token
    cached = list(
        shared_cache.search(shared_cache.CredentialType.ACCESS_TOKEN, query={"home_account_id": "uid-b.utid"})
    )
    assert cached
    shared_cache.remove_at(cached[0])

    token_b_again = getattr(credential_b, get_token_method)("scope")
    assert token_b_again.token == "ACCESS-TOKEN-B"
    assert ("refresh_token", "b") in b_events, "credential should have redeemed its own refresh token"
    assert ("refresh_token", "a") not in b_events, "credential must not redeem another account's refresh token"


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_cross_user_token_without_client_info(get_token_method):
    """The account-binding protection must also work when the STS omits "client_info", falling back to the ID
    token's "sub" claim (mirroring MSAL's own fallback behavior)."""

    from helpers import build_id_token

    shared_cache = msal.TokenCache()
    tenant_id = "tenant-id"
    client_id = "client-id"

    def make_send(expected_code, access_token, sub, redeemed):
        def send(request, **kwargs):
            if request.body.get("code") == expected_code:
                redeemed.append(True)
            return mock_response(
                json_payload=build_aad_response(
                    access_token=access_token, id_token=build_id_token(aud=client_id, sub=sub)
                )
            )

        return send

    a_redeemed = []
    credential_a = AuthorizationCodeCredential(
        tenant_id,
        client_id,
        "CODE-A",
        "https://localhost",
        transport=Mock(send=make_send("CODE-A", "ACCESS-TOKEN-A", "subject-a", a_redeemed)),
        cache=shared_cache,
    )
    token_a = getattr(credential_a, get_token_method)("scope")
    assert token_a.token == "ACCESS-TOKEN-A"
    assert a_redeemed
    # the fallback must have parsed "subject-a" from the ID token's "sub" claim, not left the account unbound
    assert credential_a._client.last_home_account_id == "subject-a"

    b_redeemed = []
    credential_b = AuthorizationCodeCredential(
        tenant_id,
        client_id,
        "CODE-B",
        "https://localhost",
        transport=Mock(send=make_send("CODE-B", "ACCESS-TOKEN-B", "subject-b", b_redeemed)),
        cache=shared_cache,
    )
    token_b = getattr(credential_b, get_token_method)("scope")

    assert token_b.token == "ACCESS-TOKEN-B", "credential returned another account's cached token"
    assert b_redeemed, "credential did not redeem its own authorization code"
    # confirms the ID-token fallback, not merely the "auth code still unredeemed" gate, established B's identity
    assert credential_b._client.last_home_account_id == "subject-b"

    # a subsequent call must use B's account-scoped cache entry, not A's, proving the fallback identity is honored
    token_b_second = getattr(credential_b, get_token_method)("scope")
    assert token_b_second.token == "ACCESS-TOKEN-B"
    assert len(b_redeemed) == 1, "second call should have used the cache, not redeemed a new code"
