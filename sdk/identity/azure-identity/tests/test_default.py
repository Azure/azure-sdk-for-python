# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.credentials import AccessToken
from azure.identity import (
    DefaultAzureCredential,
    InteractiveBrowserCredential,
    KnownAuthorities,
    SharedTokenCacheCredential,
)
from azure.identity._constants import EnvironmentVariables
from azure.identity._credentials.managed_identity import ImdsCredential, MsiCredential
from six.moves.urllib_parse import urlparse

from helpers import mock_response

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore


def test_default_credential_authority():
    # TODO need a mock cache to test SharedTokenCacheCredential
    tenant_id = "expected_tenant"
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

    def exercise_credentials(authority_kwarg, expected_authority=None):
        expected_authority = expected_authority or authority_kwarg

        def send(request, **_):
            url = urlparse(request.url)
            assert url.scheme == "https"
            assert url.netloc == expected_authority
            assert url.path.startswith("/" + tenant_id)
            return response

        # environment credential configured with client secret should respect authority
        environment = {
            EnvironmentVariables.AZURE_CLIENT_ID: "client_id",
            EnvironmentVariables.AZURE_CLIENT_SECRET: "secret",
            EnvironmentVariables.AZURE_TENANT_ID: tenant_id,
        }
        with patch("os.environ", environment):
            transport = Mock(send=send)
            access_token, _ = DefaultAzureCredential(authority=authority_kwarg, transport=transport).get_token("scope")
            assert access_token == expected_access_token

        # managed identity credential should ignore authority
        with patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "https://some.url"}):
            transport = Mock(send=lambda *_, **__: response)
            access_token, _ = DefaultAzureCredential(authority=authority_kwarg, transport=transport).get_token("scope")
            assert access_token == expected_access_token

    # all credentials not representing managed identities should use a specified authority or default to public cloud
    exercise_credentials("authority.com")
    exercise_credentials(None, KnownAuthorities.AZURE_PUBLIC_CLOUD)


def test_exclude_options():
    def assert_credentials_not_present(chain, *excluded_credential_classes):
        actual = {c.__class__ for c in chain.credentials}
        assert len(actual)

        # no unexpected credential is in the chain
        excluded = set(excluded_credential_classes)
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

    # interactive auth is excluded by default
    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    actual = {c.__class__ for c in credential.credentials}
    default = {c.__class__ for c in DefaultAzureCredential().credentials}
    assert actual - default == {InteractiveBrowserCredential}
