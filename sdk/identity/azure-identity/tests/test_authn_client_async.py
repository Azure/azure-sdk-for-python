# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest.mock import Mock, patch
from urllib.parse import urlparse

import pytest
from azure.core.credentials import AccessToken
from azure.identity._constants import EnvironmentVariables, DEFAULT_REFRESH_OFFSET, DEFAULT_TOKEN_REFRESH_RETRY_DELAY
from azure.identity.aio._authn_client import AsyncAuthnClient

from helpers import mock_response
from helpers_async import wrap_in_future


@pytest.mark.asyncio
@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
async def test_request_url(authority):
    tenant_id = "expected-tenant"
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


def test_should_refresh():
    client = AsyncAuthnClient(endpoint="http://foo")
    now = int(time.time())

    # do not need refresh
    token = AccessToken("token", now + DEFAULT_REFRESH_OFFSET + 1)
    should_refresh = client.should_refresh(token)
    assert not should_refresh

    # need refresh
    token = AccessToken("token", now + DEFAULT_REFRESH_OFFSET - 1)
    should_refresh = client.should_refresh(token)
    assert should_refresh

    # not exceed cool down time, do not refresh
    token = AccessToken("token", now + DEFAULT_REFRESH_OFFSET - 1)
    client._last_refresh_time = now - DEFAULT_TOKEN_REFRESH_RETRY_DELAY + 1
    should_refresh = client.should_refresh(token)
    assert not should_refresh
