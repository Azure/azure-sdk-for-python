# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import asyncio
import json
import sys
from pathlib import Path
from itertools import product
from urllib.parse import urlparse
from unittest.mock import Mock, patch
from test_certificate_credential import PEM_CERT_PATH

import msal
from devtools_testutils import is_live
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import TokenCachePersistenceOptions, UsernamePasswordCredential
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal.aad_client_base import JWT_BEARER_ASSERTION
from azure.identity._internal.user_agent import USER_AGENT
from azure.identity.aio import OnBehalfOfCredential
import pytest

from helpers import build_aad_response, get_discovery_response, mock_response, FAKE_CLIENT_ID, GET_TOKEN_METHODS
from helpers_async import AsyncMockTransport
from recorded_test_case import RecordedTestCase

missing_variables = [
    var
    for var in (
        "OBO_CERT_BYTES",
        "OBO_CLIENT_ID",
        "OBO_CLIENT_SECRET",
        "OBO_PASSWORD",
        "OBO_SCOPE",
        "OBO_TENANT_ID",
        "OBO_USERNAME",
    )
    if var not in os.environ
]


class TestOboAsync(RecordedTestCase):
    def load_settings(self):
        if is_live():
            self.obo_settings = {
                "cert_bytes": os.environ["OBO_CERT_BYTES"],
                "client_id": os.environ["OBO_CLIENT_ID"],
                "client_secret": os.environ["OBO_CLIENT_SECRET"],
                "password": os.environ["OBO_PASSWORD"],
                "scope": os.environ["OBO_SCOPE"],
                "tenant_id": os.environ["OBO_TENANT_ID"],
                "username": os.environ["OBO_USERNAME"],
            }
        else:
            self.obo_settings = {
                "cert_bytes": open(PEM_CERT_PATH, "rb").read(),
                "client_id": FAKE_CLIENT_ID,
                "client_secret": "secret",
                "password": "fake-password",
                "scope": "api://scope",
                "tenant_id": "tenant",
                "username": "username",
            }

    @pytest.mark.manual
    @pytest.mark.skipif(any(missing_variables), reason="No value for environment variables")
    @RecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_obo(self):
        self.load_settings()
        client_id = self.obo_settings["client_id"]
        client_secret = self.obo_settings["client_secret"]
        tenant_id = self.obo_settings["tenant_id"]

        user_credential = UsernamePasswordCredential(
            client_id, self.obo_settings["username"], self.obo_settings["password"], tenant_id=tenant_id
        )
        assertion = user_credential.get_token(self.obo_settings["scope"]).token
        credential = OnBehalfOfCredential(tenant_id, client_id, client_secret=client_secret, user_assertion=assertion)
        await credential.get_token(self.obo_settings["scope"])

    @pytest.mark.manual
    @pytest.mark.skipif(any(missing_variables), reason="No value for environment variables")
    @RecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_obo_cert(self):
        self.load_settings()
        client_id = self.obo_settings["client_id"]
        tenant_id = self.obo_settings["tenant_id"]

        user_credential = UsernamePasswordCredential(
            client_id, self.obo_settings["username"], self.obo_settings["password"], tenant_id=tenant_id
        )
        assertion = user_credential.get_token(self.obo_settings["scope"]).token
        credential = OnBehalfOfCredential(
            tenant_id, client_id, client_certificate=self.obo_settings["cert_bytes"], user_assertion=assertion
        )
        await credential.get_token(self.obo_settings["scope"])


@pytest.mark.asyncio
async def test_close():
    transport = AsyncMockTransport()
    credential = OnBehalfOfCredential(
        "tenant-id", "client-id", client_secret="client-secret", user_assertion="assertion", transport=transport
    )

    await credential.close()

    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_context_manager():
    transport = AsyncMockTransport()
    credential = OnBehalfOfCredential(
        "tenant-id", "client-id", client_secret="client-secret", user_assertion="assertion", transport=transport
    )

    async with credential:
        assert transport.__aenter__.call_count == 1
        assert not transport.__aexit__.called

    assert transport.__aenter__.call_count == 1
    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_multitenant_authentication(get_token_method):
    first_tenant = "first-tenant"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    async def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        assert request.headers["User-Agent"].startswith(USER_AGENT)
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        assert tenant in (first_tenant, second_tenant), 'unexpected tenant "{}"'.format(tenant)
        token = first_token if tenant == first_tenant else second_token
        return mock_response(json_payload=build_aad_response(access_token=token, uid="uid", utid="utid"))

    transport = Mock(send=Mock(wraps=send))
    credential = OnBehalfOfCredential(
        first_tenant,
        "client-id",
        client_secret="secret",
        user_assertion="assertion",
        transport=transport,
        additionally_allowed_tenants=["*"],
    )
    token = await getattr(credential, get_token_method)("scope")
    assert token.token == first_token
    assert transport.send.call_count == 1

    kwargs = {"tenant_id": first_tenant}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    token = await getattr(credential, get_token_method)("scope", **kwargs)
    assert token.token == first_token
    assert transport.send.call_count == 1  # should be a cached token

    kwargs = {"tenant_id": second_tenant}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    token = await getattr(credential, get_token_method)("scope", **kwargs)
    assert token.token == second_token
    assert transport.send.call_count == 2

    # should still default to the first tenant
    token = await getattr(credential, get_token_method)("scope")
    assert token.token == first_token
    assert transport.send.call_count == 2  # should be a cached token


@pytest.mark.asyncio
@pytest.mark.parametrize("authority,get_token_method", product(("localhost", "https://localhost"), GET_TOKEN_METHODS))
async def test_authority(authority, get_token_method):
    """the credential should accept an authority, with or without scheme, as an argument or environment variable"""

    tenant_id = "expected-tenant"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority
    expected_authority = "https://{}/{}".format(expected_netloc, tenant_id)
    expected_token = "***"

    async def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        assert request.url.startswith(expected_authority)
        return mock_response(json_payload=build_aad_response(access_token=expected_token))

    transport = Mock(send=send)
    credential = OnBehalfOfCredential(
        tenant_id,
        "client-id",
        client_secret="secret",
        user_assertion="assertion",
        authority=authority,
        transport=transport,
    )
    token = await getattr(credential, get_token_method)("scope")
    assert token.token == expected_token

    # authority can be configured via environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        credential = OnBehalfOfCredential(
            tenant_id, "client-id", client_secret="secret", user_assertion="assertion", transport=transport
        )
    token = await getattr(credential, get_token_method)("scope")
    assert token.token == expected_token


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_policies_configurable(get_token_method):
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock(), on_exception=lambda _: False)

    async def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))
        return mock_response(json_payload=build_aad_response(access_token="***"))

    credential = OnBehalfOfCredential(
        "tenant-id",
        "client-id",
        client_secret="client-secret",
        user_assertion="assertion",
        policies=[ContentDecodePolicy(), policy],
        transport=Mock(send=send),
    )
    await getattr(credential, get_token_method)("scope")
    assert policy.on_request.called


def test_invalid_cert():
    """The credential should raise ValueError when given invalid cert bytes"""
    with pytest.raises(ValueError):
        OnBehalfOfCredential("tenant-id", "client-id", client_certificate=b"not a cert", user_assertion="assertion")


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
@pytest.mark.parametrize("enable_cae", [True, False])
async def test_refresh_token(get_token_method, enable_cae):
    first_token = "***"
    second_token = first_token * 2
    refresh_token = "refresh-token"
    requests = 0

    async def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        nonlocal requests
        assert requests < 3, "unexpected request"
        requests += 1
        if requests == 1:
            assert "refresh_token" not in request.body
            return mock_response(
                json_payload=build_aad_response(
                    access_token=first_token, refresh_token=refresh_token, expires_in=0, uid="uid", utid="utid"
                )
            )
        if requests == 2:
            assert request.body["refresh_token"] == refresh_token
            return mock_response(json_payload=build_aad_response(access_token=second_token))

    credential = OnBehalfOfCredential(
        "tenant-id", "client-id", client_secret="secret", user_assertion="assertion", transport=Mock(send=send)
    )

    kwargs = {"enable_cae": enable_cae}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}

    token = await getattr(credential, get_token_method)("scope", **kwargs)
    assert token.token == first_token

    token = await getattr(credential, get_token_method)("scope", **kwargs)
    assert token.token == second_token

    assert requests == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_no_cross_user_token_from_shared_cache(get_token_method):
    """A credential must not return another account's cached token before exchanging its own user assertion.

    Regression test for AZSDK-H03: when multiple OnBehalfOfCredential instances share a token cache, a credential
    constructed with user B's assertion must exchange that assertion and return B's token rather than a token
    already cached for a different account (user A) from a prior exchange.
    """
    shared_cache = msal.TokenCache()

    def make_send(user, access_token, exchanges):
        async def send(request, **kwargs):
            if request.body.get("grant_type") == "urn:ietf:params:oauth:grant-type:jwt-bearer":
                exchanges.append(user)
            return mock_response(json_payload=build_aad_response(access_token=access_token, uid=user, utid="utid"))

        return send

    a_exchanges = []
    credential_a = OnBehalfOfCredential(
        "tenant-id",
        "client-id",
        client_secret="secret",
        user_assertion="assertion-a",
        transport=Mock(send=make_send("a", "ACCESS-TOKEN-A", a_exchanges)),
        cache=shared_cache,
    )
    token_a = await getattr(credential_a, get_token_method)("scope")
    assert token_a.token == "ACCESS-TOKEN-A"
    assert a_exchanges == ["a"]

    b_exchanges = []
    credential_b = OnBehalfOfCredential(
        "tenant-id",
        "client-id",
        client_secret="secret",
        user_assertion="assertion-b",
        transport=Mock(send=make_send("b", "ACCESS-TOKEN-B", b_exchanges)),
        cache=shared_cache,
    )
    token_b = await getattr(credential_b, get_token_method)("scope")

    assert token_b.token == "ACCESS-TOKEN-B", "credential returned another account's cached token"
    assert b_exchanges == ["b"], "credential did not exchange its own user assertion"


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_no_cross_user_refresh_token_from_shared_cache(get_token_method):
    shared_cache = msal.TokenCache()

    async def send_a(request, **kwargs):
        assert "refresh_token" not in request.body
        return mock_response(
            json_payload=build_aad_response(
                access_token="ACCESS-TOKEN-A",
                refresh_token="REFRESH-TOKEN-A",
                expires_in=0,
                uid="a",
                utid="utid",
            )
        )

    b_requests = []

    async def send_b(request, **kwargs):
        refresh_token = request.body.get("refresh_token")
        b_requests.append(refresh_token)
        if refresh_token is None:
            return mock_response(
                json_payload=build_aad_response(
                    access_token="ACCESS-TOKEN-B",
                    refresh_token="REFRESH-TOKEN-B",
                    expires_in=0,
                    uid="b",
                    utid="utid",
                )
            )

        assert refresh_token == "REFRESH-TOKEN-B"
        return mock_response(json_payload=build_aad_response(access_token="REFRESHED-ACCESS-TOKEN-B"))

    credential_a = OnBehalfOfCredential(
        "tenant-id",
        "client-id",
        client_secret="secret",
        user_assertion="assertion-a",
        transport=Mock(send=send_a),
        cache=shared_cache,
    )
    token_a = await getattr(credential_a, get_token_method)("scope")
    assert token_a.token == "ACCESS-TOKEN-A"

    credential_b = OnBehalfOfCredential(
        "tenant-id",
        "client-id",
        client_secret="secret",
        user_assertion="assertion-b",
        transport=Mock(send=send_b),
        cache=shared_cache,
    )
    token_b = await getattr(credential_b, get_token_method)("scope")
    assert token_b.token == "ACCESS-TOKEN-B"

    refreshed_token_b = await getattr(credential_b, get_token_method)("scope")
    assert refreshed_token_b.token == "REFRESHED-ACCESS-TOKEN-B"
    assert b_requests == [None, "REFRESH-TOKEN-B"]
    assert credential_b._client.last_home_account_id == "b.utid"


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
@pytest.mark.parametrize("expired", [True, False])
async def test_shared_cache_per_request_credentials(get_token_method, expired):
    """Per-request credentials reuse exact-assertion tokens, including after refresh.

    Different assertions for one account can coexist, as with concurrent sessions or upstream token renewal.
    """
    shared_cache = msal.TokenCache()
    requests = []

    async def send(request, **kwargs):
        assertion = request.body.get("assertion")
        refresh_token = request.body.get("refresh_token")
        requests.append((assertion, refresh_token))
        if refresh_token:
            assert refresh_token == "refresh-a"
            return mock_response(json_payload=build_aad_response(access_token="refreshed-a"))
        return mock_response(
            json_payload=build_aad_response(
                access_token="access-" + assertion,
                refresh_token="refresh-" + assertion,
                expires_in=0 if expired and assertion == "a" else 3600,
                uid="same-user",
                utid="tenant",
            )
        )

    transport = AsyncMockTransport(send=send)
    for assertion, expected_token in (
        ("a", "access-a"),
        ("b", "access-b"),
        ("a", "refreshed-a" if expired else "access-a"),
        ("a", "refreshed-a" if expired else "access-a"),
        ("b", "access-b"),
    ):
        async with OnBehalfOfCredential(
            "tenant-id",
            "client-id",
            client_secret="secret",
            user_assertion=assertion,
            cache=shared_cache,
            transport=transport,
        ) as credential:
            assert (await getattr(credential, get_token_method)("scope")).token == expected_token

    assert requests == ([("a", None), ("b", None), (None, "refresh-a")] if expired else [("a", None), ("b", None)])


@pytest.fixture
def persistent_obo_cache(tmp_path, monkeypatch):
    from msal_extensions import FilePersistence

    def get_persistence(**kwargs):
        return FilePersistence(str(tmp_path / kwargs["cache_name"]))

    monkeypatch.setattr("azure.identity._persistent_cache._get_persistence", get_persistence)
    return TokenCachePersistenceOptions(name="obo-test", allow_unencrypted_storage=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
@pytest.mark.parametrize("enable_cae", [True, False])
@pytest.mark.parametrize("account_info", [True, False])
async def test_persistent_cache_new_instance(persistent_obo_cache, get_token_method, enable_cae, account_info):
    """A new per-request credential reads the same assertion's token from a separate persistent cache object."""

    async def send(request, **kwargs):
        assert request.body["client_id"] == "client-id"
        assert request.body["assertion"] == "assertion"
        return mock_response(
            json_payload=build_aad_response(
                access_token="cached-token",
                uid="user" if account_info else None,
                utid="tenant" if account_info else None,
            )
        )

    transport = AsyncMockTransport(send=Mock(wraps=send))
    options = {"enable_cae": enable_cae}
    kwargs = {"options": options} if get_token_method == "get_token_info" else options
    caches = []
    for _ in range(2):
        async with OnBehalfOfCredential(
            "tenant-id",
            "client-id",
            client_secret="secret",
            user_assertion="assertion",
            cache_persistence_options=persistent_obo_cache,
            transport=transport,
        ) as credential:
            token = await getattr(credential, get_token_method)("scope", **kwargs)
            assert token.token == "cached-token"
            caches.append(credential._client._get_cache(enable_cae=enable_cae))
    assert caches[0] is not caches[1]
    assert transport.send.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
@pytest.mark.parametrize("enable_cae", [True, False])
@pytest.mark.parametrize("same_account", [True, False])
@pytest.mark.parametrize("expired", [True, False])
async def test_persistent_cache_assertion_isolation(
    persistent_obo_cache, get_token_method, enable_cae, same_account, expired
):
    """Assertion renewal must not overwrite another assertion's access or refresh tokens, even for one account."""
    requests = []

    async def send(request, **kwargs):
        assert request.body["client_id"] == "client-id"
        assertion = request.body.get("assertion")
        refresh_token = request.body.get("refresh_token")
        requests.append((assertion, refresh_token))
        if refresh_token:
            assert refresh_token == "refresh-a"
            # A rotation response need not identify the account.
            return mock_response(
                json_payload=build_aad_response(
                    access_token="refreshed-a",
                    refresh_token="rotated-a",
                    expires_in=0,
                )
            )
        return mock_response(
            json_payload=build_aad_response(
                access_token="access-" + assertion,
                refresh_token="refresh-" + assertion,
                expires_in=0 if expired else 3600,
                uid="same-user" if same_account else assertion,
                utid="tenant",
            )
        )

    transport = AsyncMockTransport(send=Mock(wraps=send))
    options = {"enable_cae": enable_cae}
    kwargs = {"options": options} if get_token_method == "get_token_info" else options
    for assertion in ("a", "b", "a"):
        async with OnBehalfOfCredential(
            "tenant-id",
            "client-id",
            client_secret="secret",
            user_assertion=assertion,
            cache_persistence_options=persistent_obo_cache,
            transport=transport,
        ) as credential:
            token = await getattr(credential, get_token_method)("scope", **kwargs)
            assert token.token == ("refreshed-a" if expired and len(requests) == 3 else "access-" + assertion)
    assert requests == ([("a", None), ("b", None), (None, "refresh-a")] if expired else [("a", None), ("b", None)])

    if expired:

        async def send_rotated(request, **kwargs):
            assert request.body["refresh_token"] == "rotated-a"
            return mock_response(json_payload=build_aad_response(access_token="after-rotation"))

        async with OnBehalfOfCredential(
            "tenant-id",
            "client-id",
            client_secret="secret",
            user_assertion="a",
            cache_persistence_options=persistent_obo_cache,
            transport=AsyncMockTransport(send=send_rotated),
        ) as credential:
            assert (await getattr(credential, get_token_method)("scope", **kwargs)).token == "after-rotation"


@pytest.mark.asyncio
@pytest.mark.parametrize("enable_cae", [True, False])
async def test_persistent_cache_ignores_unbound_entries(persistent_obo_cache, enable_cae):
    from azure.identity._persistent_cache import _load_persistent_cache

    cache = _load_persistent_cache(persistent_obo_cache, enable_cae)
    cache.add(
        {
            "client_id": "client-id",
            "scope": ["scope"],
            "token_endpoint": "https://login.microsoftonline.com/tenant-id/oauth2/v2.0/token",
            "response": build_aad_response(
                access_token="legacy-token",
                refresh_token="legacy-refresh",
                uid="user",
                utid="tenant",
            ),
        }
    )

    async def send(request, **kwargs):
        assert request.body["assertion"] == "assertion"
        assert "refresh_token" not in request.body
        return mock_response(json_payload=build_aad_response(access_token="bound-token"))

    transport = AsyncMockTransport(send=Mock(wraps=send))
    async with OnBehalfOfCredential(
        "tenant-id",
        "client-id",
        client_secret="secret",
        user_assertion="assertion",
        cache_persistence_options=persistent_obo_cache,
        transport=transport,
    ) as credential:
        assert (await credential.get_token("scope", enable_cae=enable_cae)).token == "bound-token"
    assert transport.send.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("expired", [True, False])
async def test_persistent_cache_client_tenant_and_authority_isolation(persistent_obo_cache, expired):
    requests = []

    async def send(request, **kwargs):
        assert "refresh_token" not in request.body
        requests.append(request.url)
        return mock_response(
            json_payload=build_aad_response(
                access_token=request.body["client_id"] + ":" + request.url,
                refresh_token="refresh",
                expires_in=0 if expired else 3600,
                uid="same-user",
                utid="home-tenant",
            )
        )

    for client, authority, tenant in (
        ("client-id", "https://login.microsoftonline.com", "tenant-a"),
        ("client-id", "https://login.microsoftonline.com", "tenant-b"),
        ("client-id", "https://other-authority", "tenant-a"),
        ("other-client", "https://login.microsoftonline.com", "tenant-a"),
    ):
        async with OnBehalfOfCredential(
            "tenant-a",
            client,
            client_secret="secret",
            user_assertion="assertion",
            authority=authority,
            additionally_allowed_tenants=["tenant-b"],
            cache_persistence_options=persistent_obo_cache,
            transport=AsyncMockTransport(send=send),
        ) as credential:
            token = await credential.get_token("scope", tenant_id=tenant)
            assert token.token == f"{client}:{authority}/{tenant}/oauth2/v2.0/token"
    assert len(requests) == 4


@pytest.mark.asyncio
async def test_persistent_cache_claims_and_scopes(persistent_obo_cache):
    requests = []

    async def send(request, **kwargs):
        requests.append((request.body["scope"], request.body.get("claims")))
        return mock_response(json_payload=build_aad_response(access_token=str(len(requests))))

    for scope, claims in (("scope", None), ("other-scope", None), ("scope", '{"access_token": {}}')):
        async with OnBehalfOfCredential(
            "tenant-id",
            "client-id",
            client_secret="secret",
            user_assertion="assertion",
            cache_persistence_options=persistent_obo_cache,
            transport=AsyncMockTransport(send=send),
        ) as credential:
            token = await credential.get_token(scope, claims=claims)
            assert token.token == str(len(requests))
    assert requests == [("scope", None), ("other-scope", None), ("scope", '{"access_token": {}}')]


@pytest.mark.asyncio
async def test_persistent_cache_concurrent_writers(persistent_obo_cache):
    ready = asyncio.Event()
    requests = []

    async def send(request, **kwargs):
        assertion = request.body["assertion"]
        requests.append(assertion)
        if len(requests) == 2:
            ready.set()
        await ready.wait()
        return mock_response(
            json_payload=build_aad_response(
                access_token=assertion,
                uid="same-user",
                utid="tenant",
            )
        )

    async def acquire(assertion, transport):
        async with OnBehalfOfCredential(
            "tenant-id",
            "client-id",
            client_secret="secret",
            user_assertion=assertion,
            cache_persistence_options=persistent_obo_cache,
            transport=transport,
        ) as credential:
            assert (await credential.get_token("scope")).token == assertion

    await asyncio.gather(*(acquire(user, AsyncMockTransport(send=send)) for user in ("a", "b")))
    no_network = AsyncMockTransport(send=Mock(side_effect=AssertionError("unexpected exchange")))
    await asyncio.gather(*(acquire(user, no_network) for user in ("a", "b")))
    assert sorted(requests) == ["a", "b"]


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_grant", [True, False])
async def test_persistent_cache_refresh_updates_are_assertion_bound(persistent_obo_cache, invalid_grant):
    async def exchange(request, **kwargs):
        return mock_response(
            json_payload=build_aad_response(
                access_token="expired",
                refresh_token="shared-refresh-secret",
                expires_in=0,
                uid="same-user",
                utid="tenant",
            )
        )

    for assertion in ("a", "b"):
        async with OnBehalfOfCredential(
            "tenant-id",
            "client-id",
            client_secret="secret",
            user_assertion=assertion,
            cache_persistence_options=persistent_obo_cache,
            transport=AsyncMockTransport(send=exchange),
        ) as credential:
            await credential.get_token("scope")

    a_requests = []

    async def refresh_a(request, **kwargs):
        a_requests.append(request.body["grant_type"])
        if request.body.get("refresh_token"):
            assert request.body["refresh_token"] == "shared-refresh-secret"
            if invalid_grant:
                return mock_response(status_code=400, json_payload={"error": "invalid_grant"})
            return mock_response(json_payload=build_aad_response(access_token="refreshed-a", refresh_token="rotated-a"))
        assert request.body["assertion"] == "a"
        return mock_response(json_payload=build_aad_response(access_token="exchanged-a"))

    async with OnBehalfOfCredential(
        "tenant-id",
        "client-id",
        client_secret="secret",
        user_assertion="a",
        cache_persistence_options=persistent_obo_cache,
        transport=AsyncMockTransport(send=refresh_a),
    ) as credential:
        token = await credential.get_token("scope")
        assert token.token == ("exchanged-a" if invalid_grant else "refreshed-a")
        refresh_tokens = credential._client.get_cached_refresh_tokens(["scope"])
        assert [entry["secret"] for entry in refresh_tokens] == ([] if invalid_grant else ["rotated-a"])

    assert a_requests == (
        ["refresh_token", "urn:ietf:params:oauth:grant-type:jwt-bearer"] if invalid_grant else ["refresh_token"]
    )

    async def refresh_b(request, **kwargs):
        assert request.body["refresh_token"] == "shared-refresh-secret"
        assert "assertion" not in request.body
        return mock_response(json_payload=build_aad_response(access_token="refreshed-b"))

    async with OnBehalfOfCredential(
        "tenant-id",
        "client-id",
        client_secret="secret",
        user_assertion="b",
        cache_persistence_options=persistent_obo_cache,
        transport=AsyncMockTransport(send=refresh_b),
    ) as credential:
        assert (await credential.get_token("scope")).token == "refreshed-b"


@pytest.mark.asyncio
@pytest.mark.parametrize("enable_cae", [True, False])
@pytest.mark.parametrize("expired", [True, False])
async def test_persistent_cache_separate_processes(tmp_path, enable_cae, expired):
    worker = Path(__file__).with_name("obo_cache_process.py")

    async def run(assertion, mode):
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(worker),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        settings = json.dumps(
            {
                "directory": str(tmp_path),
                "assertion": assertion,
                "mode": mode,
                "enable_cae": enable_cae,
                "expired": expired,
            }
        ).encode()
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(settings), timeout=30)
        finally:
            if process.returncode is None:
                process.kill()
                await process.wait()
        assert process.returncode == 0, stdout.decode() + stderr.decode()
        return json.loads(stdout)

    writers = await asyncio.gather(*(run(user, "write") for user in ("a", "b")))
    for user, result in zip(("a", "b"), writers):
        assert result["token"] == "access-" + user
        assert result["requests"] == ["urn:ietf:params:oauth:grant-type:jwt-bearer"]

    for user in ("a", "b"):
        result = await run(user, "refresh" if expired else "read")
        assert result["token"] == ("refreshed-" if expired else "access-") + user
        assert result["requests"] == (["refresh_token"] if expired else [])
        assert [entry["secret"] for entry in result["refresh_tokens"]] == [
            ("rotated-" if expired else "refresh-") + user
        ]
        # A third process must read the refreshed access token and rotated refresh token from disk.
        repeated = await run(user, "read")
        assert repeated["token"] == result["token"]
        assert repeated["requests"] == []
        assert repeated["refresh_tokens"] == result["refresh_tokens"]


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""
    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        OnBehalfOfCredential(tenant, "client-id", client_secret="secret", user_assertion="assertion")
    invalid_ids = {"my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        with pytest.raises(ValueError):
            OnBehalfOfCredential(tenant, "client-id", client_secret="secret", user_assertion="assertion")


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_no_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with no scopes"""
    credential = OnBehalfOfCredential(
        "tenant-id", "client-id", client_secret="client-secret", user_assertion="assertion"
    )
    with pytest.raises(ValueError):
        await getattr(credential, get_token_method)()


@pytest.mark.asyncio
async def test_no_user_assertion():
    """The credential should raise ValueError when ctoring with no user_assertion"""
    with pytest.raises(TypeError):
        credential = OnBehalfOfCredential("tenant-id", "client-id", client_secret="client-secret")


@pytest.mark.asyncio
async def test_no_client_credential():
    """The credential should raise ValueError when ctoring with no client_secret or client_certificate"""
    with pytest.raises(TypeError):
        credential = OnBehalfOfCredential("tenant-id", "client-id", user_assertion="assertion")


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_client_assertion_func(get_token_method):
    """The credential should accept a client_assertion_func"""
    expected_client_assertion = "client-assertion"
    expected_user_assertion = "user-assertion"
    expected_token = "***"
    func_call_count = 0

    def client_assertion_func():
        nonlocal func_call_count
        func_call_count += 1
        return expected_client_assertion

    async def send(request, **kwargs):
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))

        assert request.data.get("client_assertion") == expected_client_assertion
        assert request.data.get("client_assertion_type") == JWT_BEARER_ASSERTION
        assert request.data.get("assertion") == expected_user_assertion
        return mock_response(json_payload=build_aad_response(access_token=expected_token))

    transport = Mock(send=send)
    credential = OnBehalfOfCredential(
        "tenant-id",
        "client-id",
        client_assertion_func=client_assertion_func,
        user_assertion=expected_user_assertion,
        transport=transport,
    )
    token = await getattr(credential, get_token_method)("scope")
    assert token.token == expected_token
    assert func_call_count == 1


@pytest.mark.asyncio
async def test_client_assertion_func_with_client_certificate():
    """The credential should raise when given both client_assertion_func and client_certificate"""
    with pytest.raises(ValueError) as ex:
        OnBehalfOfCredential(
            "tenant-id",
            "client-id",
            client_assertion_func=lambda: "client-assertion",
            client_certificate=b"cert",
            user_assertion="assertion",
        )
    assert "It is invalid to specify more than one of the following" in str(ex.value)
