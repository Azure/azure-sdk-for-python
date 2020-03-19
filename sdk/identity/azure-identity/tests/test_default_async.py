# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
from unittest.mock import Mock, patch
from urllib.parse import urlparse

from azure.identity import KnownAuthorities
from azure.identity.aio import DefaultAzureCredential, SharedTokenCacheCredential
from azure.identity.aio._credentials.managed_identity import ImdsCredential, MsiCredential
from azure.identity._constants import EnvironmentVariables
import pytest

from helpers import mock_response, Request
from helpers_async import async_validating_transport, wrap_in_future
from test_shared_cache_credential import build_aad_response, get_account_event, populated_cache


@pytest.mark.asyncio
async def test_default_credential_authority():
    authority = "authority.com"
    expected_access_token = "***"
    response = mock_response(
        json_payload={
            "access_token": expected_access_token,
            "expires_in": 0,
            "expires_on": 42,
            "not_before": 0,
            "resource": "scope",
            "token_type": "Bearer",
        }
    )

    async def exercise_credentials(authority_kwarg, expected_authority=None):
        expected_authority = expected_authority or authority_kwarg

        async def send(request, **_):
            url = urlparse(request.url)
            assert url.scheme == "https", "Unexpected scheme '{}'".format(url.scheme)
            assert url.netloc == expected_authority, "Expected authority '{}', actual was '{}'".format(
                expected_authority, url.netloc
            )
            return response

        # environment credential configured with client secret should respect authority
        environment = {
            EnvironmentVariables.AZURE_CLIENT_ID: "client_id",
            EnvironmentVariables.AZURE_CLIENT_SECRET: "secret",
            EnvironmentVariables.AZURE_TENANT_ID: "tenant_id",
        }
        with patch("os.environ", environment):
            transport = Mock(send=send)
            if authority_kwarg:
                credential = DefaultAzureCredential(authority=authority_kwarg, transport=transport)
            else:
                credential = DefaultAzureCredential(transport=transport)
            access_token, _ = await credential.get_token("scope")
            assert access_token == expected_access_token

        # managed identity credential should ignore authority
        with patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "https://some.url"}):
            transport = Mock(send=wrap_in_future(lambda *_, **__: response))
            if authority_kwarg:
                credential = DefaultAzureCredential(authority=authority_kwarg, transport=transport)
            else:
                credential = DefaultAzureCredential(transport=transport)
            access_token, _ = await credential.get_token("scope")
            assert access_token == expected_access_token

        # shared cache credential should respect authority
        upn = os.environ.get(EnvironmentVariables.AZURE_USERNAME, "spam@eggs")  # preferring environment values to
        tenant = os.environ.get(EnvironmentVariables.AZURE_TENANT_ID, "tenant")  # prevent failure during live runs
        account = get_account_event(username=upn, uid="guid", utid=tenant, authority=authority_kwarg)
        cache = populated_cache(account)
        with patch.object(SharedTokenCacheCredential, "supported"):
            credential = DefaultAzureCredential(_cache=cache, authority=authority_kwarg, transport=Mock(send=send))
        access_token, _ = await credential.get_token("scope")
        assert access_token == expected_access_token

    # all credentials not representing managed identities should use a specified authority or default to public cloud
    await exercise_credentials("authority.com")
    await exercise_credentials(None, KnownAuthorities.AZURE_PUBLIC_CLOUD)


def test_exclude_options():
    def assert_credentials_not_present(chain, *credential_classes):
        actual = {c.__class__ for c in chain.credentials}
        assert len(actual)

        # no unexpected credential is in the chain
        excluded = set(credential_classes)
        assert len(actual & excluded) == 0

        # only excluded credentials have been excluded from the default
        default = {c.__class__ for c in DefaultAzureCredential().credentials}
        assert actual <= default  # n.b. we know actual is non-empty
        assert default - actual <= excluded

    # with no environment variables set, ManagedIdentityCredential = ImdsCredential
    with patch("os.environ", {}):
        credential = DefaultAzureCredential(exclude_managed_identity_credential=True)
        assert_credentials_not_present(credential, ImdsCredential, MsiCredential)

    # with $MSI_ENDPOINT set, ManagedIdentityCredential = MsiCredential
    with patch("os.environ", {"MSI_ENDPOINT": "spam"}):
        credential = DefaultAzureCredential(exclude_managed_identity_credential=True)
        assert_credentials_not_present(credential, ImdsCredential, MsiCredential)

    if SharedTokenCacheCredential.supported():
        credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
        assert_credentials_not_present(credential, SharedTokenCacheCredential)


@pytest.mark.asyncio
async def test_shared_cache_tenant_id():
    expected_access_token = "expected-access-token"
    refresh_token_a = "refresh-token-a"
    refresh_token_b = "refresh-token-b"

    # The value of upn is arbitrary because this test verifies the credential's behavior given a specified
    # tenant. During a complete live test run, $AZURE_USERNAME will have a value which DefaultAzureCredential
    # should pass to SharedTokenCacheCredential. This test will fail if the mock accounts don't match that value.
    upn = os.environ.get(EnvironmentVariables.AZURE_USERNAME, "spam@eggs")

    tenant_a = "tenant-a"
    tenant_b = "tenant-b"

    # two cached accounts, same username, different tenants -> shared_cache_tenant_id should prevail
    account_a = get_account_event(username=upn, uid="another-guid", utid=tenant_a, refresh_token=refresh_token_a)
    account_b = get_account_event(username=upn, uid="more-guid", utid=tenant_b, refresh_token=refresh_token_b)
    cache = populated_cache(account_a, account_b)

    credential = get_credential_for_shared_cache_test(
        refresh_token_b, expected_access_token, cache, shared_cache_tenant_id=tenant_b
    )
    token = await credential.get_token("scope")
    assert token.token == expected_access_token

    # redundantly specifying shared_cache_username makes no difference
    credential = get_credential_for_shared_cache_test(
        refresh_token_b, expected_access_token, cache, shared_cache_tenant_id=tenant_b, shared_cache_username=upn
    )
    token = await credential.get_token("scope")
    assert token.token == expected_access_token

    # shared_cache_tenant_id should prevail over AZURE_TENANT_ID
    with patch("os.environ", {EnvironmentVariables.AZURE_TENANT_ID: tenant_a}):
        credential = get_credential_for_shared_cache_test(
            refresh_token_b, expected_access_token, cache, shared_cache_tenant_id=tenant_b
        )
    token = await credential.get_token("scope")
    assert token.token == expected_access_token

    # AZURE_TENANT_ID should be used when shared_cache_tenant_id isn't specified
    with patch("os.environ", {EnvironmentVariables.AZURE_TENANT_ID: tenant_b}):
        credential = get_credential_for_shared_cache_test(refresh_token_b, expected_access_token, cache)
    token = await credential.get_token("scope")
    assert token.token == expected_access_token


@pytest.mark.asyncio
async def test_shared_cache_username():
    expected_access_token = "expected-access-token"
    refresh_token_a = "refresh-token-a"
    refresh_token_b = "refresh-token-b"
    upn_a = "spam@eggs"
    upn_b = "eggs@spam"

    # The value of tenant_id is arbitrary because this test verifies the credential's behavior given a specified
    # username. During a complete live test run, $AZURE_TENANT_ID will have a value which DefaultAzureCredential
    # should pass to SharedTokenCacheCredential. This test will fail if the mock accounts don't match that value.
    tenant_id = os.environ.get(EnvironmentVariables.AZURE_TENANT_ID, "the-tenant")

    # two cached accounts, same tenant, different usernames -> shared_cache_username should prevail
    account_a = get_account_event(username=upn_a, uid="another-guid", utid=tenant_id, refresh_token=refresh_token_a)
    account_b = get_account_event(username=upn_b, uid="more-guid", utid=tenant_id, refresh_token=refresh_token_b)
    cache = populated_cache(account_a, account_b)

    credential = get_credential_for_shared_cache_test(
        refresh_token_a, expected_access_token, cache, shared_cache_username=upn_a
    )
    token = await credential.get_token("scope")
    assert token.token == expected_access_token

    # shared_cache_username should prevail over AZURE_USERNAME
    with patch("os.environ", {EnvironmentVariables.AZURE_USERNAME: upn_b}):
        credential = get_credential_for_shared_cache_test(
            refresh_token_a, expected_access_token, cache, shared_cache_username=upn_a
        )
    token = await credential.get_token("scope")
    assert token.token == expected_access_token

    # AZURE_USERNAME should be used when shared_cache_username isn't specified
    with patch("os.environ", {EnvironmentVariables.AZURE_USERNAME: upn_b}):
        credential = get_credential_for_shared_cache_test(refresh_token_b, expected_access_token, cache)
    token = await credential.get_token("scope")
    assert token.token == expected_access_token


def get_credential_for_shared_cache_test(expected_refresh_token, expected_access_token, cache, **kwargs):
    exclude_other_credentials = {
        option: True for option in ("exclude_environment_credential", "exclude_managed_identity_credential")
    }

    # validating transport will raise if the shared cache credential isn't used, or selects the wrong refresh token
    transport = async_validating_transport(
        requests=[Request(required_data={"refresh_token": expected_refresh_token})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_access_token))],
    )

    # this credential uses a mock shared cache, so it works on all platforms
    with patch.object(SharedTokenCacheCredential, "supported", lambda: True):
        return DefaultAzureCredential(_cache=cache, transport=transport, **exclude_other_credentials, **kwargs)
