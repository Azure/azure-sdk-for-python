# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from unittest.mock import Mock, patch
from urllib.parse import urlparse

import pytest
from azure.identity._constants import EnvironmentVariables
from azure.identity.aio._authn_client import AsyncAuthnClient

from helpers import mock_response
from helpers_async import wrap_in_future


@pytest.mark.asyncio
@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
async def test_request_url(authority):
    tenant_id = "expected_tenant"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"

    def mock_send(request, **kwargs):
        actual = urlparse(request.url)
        assert actual.scheme == "https"
        assert actual.netloc == expected_netloc
        assert actual.path.startswith("/" + tenant_id)
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": "*"})

    client = AsyncAuthnClient(tenant=tenant_id, transport=Mock(send=wrap_in_future(mock_send)), authority=authority)
    await client.request_token(("scope",))

    # authority can be configured via environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        client = AsyncAuthnClient(tenant=tenant_id, transport=Mock(send=wrap_in_future(mock_send)))
        await client.request_token(("scope",))
