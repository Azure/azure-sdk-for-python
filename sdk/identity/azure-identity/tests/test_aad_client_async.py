# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
from unittest.mock import Mock

from azure.core.exceptions import ClientAuthenticationError
from azure.identity.aio._internal.aad_client import AadClient
import pytest


class MockClient(AadClient):
    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop("session")
        super(MockClient, self).__init__(*args, **kwargs)

    def _get_client_session(self, **kwargs):
        return self.session


@pytest.mark.asyncio
async def test_uses_msal_correctly():
    session = Mock()
    transport = Mock()
    session.get = session.post = transport

    client = MockClient("client id", "tenant id", session=session)

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
async def test_respects_authority():
    my_authority = "my.authority.com"

    def check_url(url, **kwargs):
        nonlocal authority_respected
        authority_respected = url.startswith("https://" + my_authority)

    transport = Mock(side_effect=check_url)
    session = Mock(get=transport, post=transport)
    client = MockClient("client id", "tenant id", session=session, authority=my_authority)

    coros = [
        client.obtain_token_by_authorization_code("code", "uri", "scope"),
        client.obtain_token_by_refresh_token({"secret": "refresh token"}, "scope"),
    ]

    for coro in coros:
        authority_respected = False
        with pytest.raises(ClientAuthenticationError):
            # raises because the mock transport returns nothing
            await coro
        assert authority_respected
