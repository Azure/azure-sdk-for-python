# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from unittest.mock import Mock, patch
from urllib.parse import urlparse

from azure.core.credentials import AccessToken
from azure.identity import KnownAuthorities
from azure.identity.aio import DefaultAzureCredential, SharedTokenCacheCredential
from azure.identity._constants import EnvironmentVariables
import pytest

from helpers import mock_response


@pytest.mark.asyncio
async def test_default_credential_authority():
    # TODO need a mock cache to test SharedTokenCacheCredential
    you_shall_not_pass = "sentinel"
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

    async def exercise_credentials(authority_kwarg, expected_authority=None):
        expected_authority = expected_authority or authority_kwarg
        async def send(request, **_):
            scheme, netloc, path, _, _, _ = urlparse(request.url)
            assert scheme == "https"
            assert netloc == expected_authority
            assert path.startswith("/" + tenant_id)
            return response

        # environment credential configured with client secret should respect authority
        environment = {
            EnvironmentVariables.AZURE_CLIENT_ID: "client_id",
            EnvironmentVariables.AZURE_CLIENT_SECRET: "secret",
            EnvironmentVariables.AZURE_TENANT_ID: tenant_id,
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
            transport = Mock(send=asyncio.coroutine(lambda *_, **__: response))
            if authority_kwarg:
                credential = DefaultAzureCredential(authority=authority_kwarg, transport=transport)
            else:
                credential = DefaultAzureCredential(transport=transport)
            access_token, _ = await credential.get_token("scope")
            assert access_token == expected_access_token

    # all credentials not representing managed identities should use a specified authority or default to public cloud
    await exercise_credentials("authority.com")
    await exercise_credentials(None, KnownAuthorities.AZURE_PUBLIC_CLOUD)
