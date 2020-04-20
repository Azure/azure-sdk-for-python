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
async def test_request_url():
    authority = "authority.com"
    tenant = "expected_tenant"

    def mock_send(request, **kwargs):
        scheme, netloc, path, _, _, _ = urlparse(request.url)
        assert scheme == "https"
        assert netloc == authority
        assert path.startswith("/" + tenant)
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": "***"})

    client = AsyncAuthnClient(tenant=tenant, transport=Mock(send=wrap_in_future(mock_send)), authority=authority)
    await client.request_token(("scope",))

    # authority can be configured via environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        client = AsyncAuthnClient(tenant=tenant, transport=Mock(send=wrap_in_future(mock_send)))
        await client.request_token(("scope",))
