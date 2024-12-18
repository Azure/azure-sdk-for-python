# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest import mock

from azure.core.credentials import AccessTokenInfo
import pytest

from azure.identity._constants import DEFAULT_REFRESH_OFFSET
from azure.identity.aio._internal.get_token_mixin import GetTokenMixin

from helpers import GET_TOKEN_METHODS

pytestmark = pytest.mark.asyncio


class MockCredential(GetTokenMixin):
    NEW_TOKEN = AccessTokenInfo("new token", 42)

    def __init__(self, cached_token=None):
        super(MockCredential, self).__init__()
        self.token = cached_token
        self.request_token = mock.Mock(return_value=MockCredential.NEW_TOKEN)
        self.acquire_token_silently = mock.Mock(return_value=cached_token)

    async def _acquire_token_silently(self, *scopes, **kwargs):
        return self.acquire_token_silently(*scopes, **kwargs)

    async def _request_token(self, *scopes, **kwargs):
        return self.request_token(*scopes, **kwargs)

    async def get_token(self, *_, **__):
        return await super().get_token(*_, **__)

    async def get_token_info(self, *_, **__):
        return await super().get_token_info(*_, **__)


CACHED_TOKEN = "cached token"
SCOPE = "scope"


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_no_cached_token(get_token_method):
    """When it has no token cached, a credential should request one every time get_token is called"""

    credential = MockCredential()
    token = await getattr(credential, get_token_method)(SCOPE)

    credential.acquire_token_silently.assert_called_once_with(SCOPE, claims=None, enable_cae=False, tenant_id=None)
    credential.request_token.assert_called_once_with(SCOPE, claims=None, enable_cae=False, tenant_id=None)
    assert token.token == MockCredential.NEW_TOKEN.token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_tenant_id(get_token_method):
    credential = MockCredential()
    kwargs = {"tenant_id": "tenant_id"}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    token = await getattr(credential, get_token_method)(SCOPE, **kwargs)

    assert token.token == MockCredential.NEW_TOKEN.token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_token_acquisition_failure(get_token_method):
    """When the credential has no token cached, every get_token call should prompt a token request"""

    credential = MockCredential()
    credential.request_token = mock.Mock(side_effect=Exception("whoops"))
    for i in range(4):
        with pytest.raises(Exception):
            await getattr(credential, get_token_method)(SCOPE)
        assert credential.request_token.call_count == i + 1
        credential.request_token.assert_called_with(SCOPE, claims=None, enable_cae=False, tenant_id=None)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_expired_token(get_token_method):
    """A credential should request a token when it has an expired token cached"""

    now = int(time.time())
    credential = MockCredential(cached_token=AccessTokenInfo(CACHED_TOKEN, now - 1))
    token = await getattr(credential, get_token_method)(SCOPE)

    credential.acquire_token_silently.assert_called_once_with(SCOPE, claims=None, enable_cae=False, tenant_id=None)
    credential.request_token.assert_called_once_with(SCOPE, claims=None, enable_cae=False, tenant_id=None)
    assert token.token == MockCredential.NEW_TOKEN.token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_cached_token_outside_refresh_window(get_token_method):
    """A credential shouldn't request a new token when it has a cached one with sufficient validity remaining"""

    credential = MockCredential(
        cached_token=AccessTokenInfo(CACHED_TOKEN, int(time.time() + DEFAULT_REFRESH_OFFSET + 1))
    )
    token = await getattr(credential, get_token_method)(SCOPE)

    credential.acquire_token_silently.assert_called_once_with(SCOPE, claims=None, enable_cae=False, tenant_id=None)
    assert credential.request_token.call_count == 0
    assert token.token == CACHED_TOKEN


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_cached_token_within_refresh_window(get_token_method):
    """A credential should request a new token when its cached one is within the refresh window"""

    credential = MockCredential(
        cached_token=AccessTokenInfo(CACHED_TOKEN, int(time.time() + DEFAULT_REFRESH_OFFSET - 1))
    )
    token = await getattr(credential, get_token_method)(SCOPE)

    credential.acquire_token_silently.assert_called_once_with(SCOPE, claims=None, enable_cae=False, tenant_id=None)
    credential.request_token.assert_called_once_with(SCOPE, claims=None, enable_cae=False, tenant_id=None)
    assert token.token == MockCredential.NEW_TOKEN.token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_retry_delay(get_token_method):
    """A credential should wait between requests when trying to refresh a token"""

    now = time.time()
    credential = MockCredential(cached_token=AccessTokenInfo(CACHED_TOKEN, int(now + DEFAULT_REFRESH_OFFSET - 1)))

    # the credential should swallow exceptions during proactive refresh attempts
    credential.request_token = mock.Mock(side_effect=Exception("whoops"))
    for i in range(4):
        token = await getattr(credential, get_token_method)(SCOPE)
        assert token.token == CACHED_TOKEN
        credential.acquire_token_silently.assert_called_with(SCOPE, claims=None, enable_cae=False, tenant_id=None)
        credential.request_token.assert_called_once_with(SCOPE, claims=None, enable_cae=False, tenant_id=None)
