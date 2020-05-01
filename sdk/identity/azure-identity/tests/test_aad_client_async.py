# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest.mock import Mock, patch
from urllib.parse import urlparse

from azure.identity._constants import EnvironmentVariables
from azure.identity.aio._internal.aad_client import AadClient
import pytest

from helpers import mock_response


class MockClient(AadClient):
    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop("session")
        super(MockClient, self).__init__(*args, **kwargs)

    def _get_client_session(self, **kwargs):
        return self.session


@pytest.mark.asyncio
async def test_uses_msal_correctly():
    transport = Mock()
    session = Mock(get=transport, post=transport)

    client = MockClient("tenant id", "client id", session=session)

    # MSAL will raise on each call because the mock transport returns nothing useful.
    # That's okay because we only want to verify the transport was called, i.e. that
    # the client used the MSAL API correctly, such that MSAL tried to send a request.
    with pytest.raises(Exception):
        await client.obtain_token_by_authorization_code("code", "redirect uri", "scope")
    assert transport.call_count == 1

    transport.reset_mock()

    with pytest.raises(Exception):
        await client.obtain_token_by_refresh_token("refresh token", "scope")
    assert transport.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
async def test_request_url(authority):
    tenant_id = "expected_tenant"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"

    async def send(request, **_):
        actual = urlparse(request.url)
        assert actual.scheme == "https"
        assert actual.netloc == expected_netloc
        assert actual.path.startswith("/" + tenant_id)
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": "***"})

    client = AadClient(tenant_id, "client id", transport=Mock(send=send), authority=authority)

    await client.obtain_token_by_authorization_code("code", "uri", "scope")
    await client.obtain_token_by_refresh_token("refresh token", "scope")

    # authority can be configured via environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        client = AadClient(tenant_id=tenant_id, client_id="client id", transport=Mock(send=send))
    await client.obtain_token_by_authorization_code("code", "uri", "scope")
    await client.obtain_token_by_refresh_token("refresh token", "scope")
