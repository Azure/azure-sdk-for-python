# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
from unittest.mock import Mock, patch
from urllib.parse import urlparse

from azure.core.credentials import AccessToken
from azure.identity import CredentialUnavailableError, KnownAuthorities
from azure.identity.aio import DefaultAzureCredential, SharedTokenCacheCredential
from azure.identity.aio._credentials.azure_cli import AzureCliCredential
from azure.identity.aio._credentials.managed_identity import ManagedIdentityCredential
from azure.identity._constants import EnvironmentVariables
import pytest

from helpers import mock_response, Request
from helpers_async import async_validating_transport, get_completed_future, wrap_in_future
from test_shared_cache_credential import build_aad_response, get_account_event, populated_cache


@pytest.mark.asyncio
async def test_iterates_only_once():
    """When a credential succeeds, DefaultAzureCredential should use that credential thereafter, ignoring the others"""

    unavailable_credential = Mock(get_token=Mock(side_effect=CredentialUnavailableError(message="...")))
    successful_credential = Mock(get_token=Mock(return_value=get_completed_future(AccessToken("***", 42))))

    credential = DefaultAzureCredential()
    credential.credentials = [
        unavailable_credential,
        successful_credential,
        Mock(get_token=Mock(side_effect=Exception("iteration didn't stop after a credential provided a token"))),
    ]

    for n in range(3):
        await credential.get_token("scope")
        assert unavailable_credential.get_token.call_count == 1
        assert successful_credential.get_token.call_count == n + 1


@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
def test_authority(authority):
    """the credential should accept authority configuration by keyword argument or environment"""

    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"

    def test_initialization(mock_credential, expect_argument):
        DefaultAzureCredential(authority=authority)
        assert mock_credential.call_count == 1

        # N.B. if os.environ has been patched somewhere in the stack, that patch is in place here
        environment = dict(os.environ, **{EnvironmentVariables.AZURE_AUTHORITY_HOST: authority})
        with patch.dict(DefaultAzureCredential.__module__ + ".os.environ", environment, clear=True):
            DefaultAzureCredential()
        assert mock_credential.call_count == 2

        for _, kwargs in mock_credential.call_args_list:
            if expect_argument:
                actual = urlparse(kwargs["authority"])
                assert actual.scheme == "https"
                assert actual.netloc == expected_netloc
            else:
                assert "authority" not in kwargs

    # authority should be passed to EnvironmentCredential as a keyword argument
    environment = {var: "foo" for var in EnvironmentVariables.CLIENT_SECRET_VARS}
    with patch(DefaultAzureCredential.__module__ + ".EnvironmentCredential") as mock_credential:
        with patch.dict("os.environ", environment, clear=True):
            test_initialization(mock_credential, expect_argument=True)

    # authority should be passed to SharedTokenCacheCredential as a keyword argument
    with patch(DefaultAzureCredential.__module__ + ".SharedTokenCacheCredential") as mock_credential:
        mock_credential.supported = lambda: True
        with patch.dict("os.environ", {}, clear=True):
            test_initialization(mock_credential, expect_argument=True)

    # authority should not be passed to ManagedIdentityCredential
    with patch(DefaultAzureCredential.__module__ + ".ManagedIdentityCredential") as mock_credential:
        with patch.dict("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "_"}, clear=True):
            test_initialization(mock_credential, expect_argument=False)

    # authority should not be passed to AzureCliCredential
    with patch(DefaultAzureCredential.__module__ + ".AzureCliCredential") as mock_credential:
        with patch(DefaultAzureCredential.__module__ + ".SharedTokenCacheCredential") as shared_cache:
            shared_cache.supported = lambda: False
            with patch.dict("os.environ", {}, clear=True):
                test_initialization(mock_credential, expect_argument=False)


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

    # when exclude_managed_identity_credential is set to True, check if ManagedIdentityCredential instance is not present
    credential = DefaultAzureCredential(exclude_managed_identity_credential=True)
    assert_credentials_not_present(credential, ManagedIdentityCredential)

    if SharedTokenCacheCredential.supported():
        credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
        assert_credentials_not_present(credential, SharedTokenCacheCredential)

    credential = DefaultAzureCredential(exclude_cli_credential=True)
    assert_credentials_not_present(credential, AzureCliCredential)


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
