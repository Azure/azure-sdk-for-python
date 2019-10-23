# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential, SharedTokenCacheCredential
from azure.identity._constants import EnvironmentVariables
from six.moves.urllib_parse import urlparse

from helpers import mock_response

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore


def test_default_credential_authority():
    # TODO need a mock cache to test SharedTokenCacheCredential
    authority = "authority.com"
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

    def send(request, **_):
        scheme, netloc, path, _, _, _ = urlparse(request.url)
        assert scheme == "https"
        assert netloc == authority
        assert path.startswith("/" + tenant_id)
        return response

    # environment credential configured with client secret should respect authority
    environment = {
        EnvironmentVariables.AZURE_CLIENT_ID: "client_id",
        EnvironmentVariables.AZURE_CLIENT_SECRET: "secret",
        EnvironmentVariables.AZURE_TENANT_ID: tenant_id,
    }
    with patch("os.environ", environment):
        access_token, _ = DefaultAzureCredential(authority=authority, transport=Mock(send=send)).get_token("scope")
        assert access_token == expected_access_token

    # managed identity credential should ignore authority
    with patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "https://some.url"}):
        transport = Mock(send=lambda *_, **__: response)
        access_token, _ = DefaultAzureCredential(authority=authority, transport=transport).get_token("scope")
        assert access_token == expected_access_token
