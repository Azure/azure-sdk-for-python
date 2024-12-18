# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.identity.aio import get_bearer_token_provider

import pytest


class MockCredential:
    async def get_token(self, *scopes, **kwargs):
        assert len(scopes) == 1
        assert scopes[0] == "scope"
        return AccessToken("mock_token", 42)


class MockCredentialTokenInfo:
    async def get_token_info(self, *scopes, **kwargs):
        assert len(scopes) == 1
        assert scopes[0] == "scope"
        return AccessTokenInfo("mock_token_2", 42)


@pytest.mark.asyncio
async def test_get_bearer_token_provider():

    func = get_bearer_token_provider(MockCredential(), "scope")  # type: ignore
    assert await func() == "mock_token"

    func = get_bearer_token_provider(MockCredentialTokenInfo(), "scope")  # type: ignore
    assert await func() == "mock_token_2"
