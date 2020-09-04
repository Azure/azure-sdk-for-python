# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time

try:
    from unittest import mock
except ImportError:
    import mock

from azure.core.credentials import AccessToken
import pytest

from azure.identity._constants import DEFAULT_REFRESH_OFFSET
from azure.identity._internal.get_token_mixin import GetTokenMixin


class MockCredential(GetTokenMixin):
    NEW_TOKEN = AccessToken("new token", 42)

    def __init__(self, cached_token=None):
        super(MockCredential, self).__init__()
        self.request_token = mock.Mock(return_value=MockCredential.NEW_TOKEN)
        self.acquire_token_silently = mock.Mock(return_value=cached_token)

    def _acquire_token_silently(self, *scopes):
        return self.acquire_token_silently(*scopes)

    def _request_token(self, *scopes, **kwargs):
        return self.request_token(*scopes, **kwargs)

    def get_token(self, *_, **__):
        return super(MockCredential, self).get_token(*_, **__)


CACHED_TOKEN = "cached token"
SCOPE = "scope"


def test_no_cached_token():
    """When it has no token cached, a credential should request one every time get_token is called"""

    credential = MockCredential()
    token = credential.get_token(SCOPE)

    credential.acquire_token_silently.assert_called_once_with(SCOPE)
    credential.request_token.assert_called_once_with(SCOPE)
    assert token.token == MockCredential.NEW_TOKEN.token


def test_token_acquisition_failure():
    """When the credential has no token cached, every get_token call should prompt a token request"""

    credential = MockCredential()
    credential.request_token = mock.Mock(side_effect=Exception("whoops"))
    for i in range(4):
        with pytest.raises(Exception):
            credential.get_token(SCOPE)
        assert credential.request_token.call_count == i + 1
        credential.request_token.assert_called_with(SCOPE)


def test_expired_token():
    """A credential should request a token when it has an expired token cached"""

    now = time.time()
    credential = MockCredential(cached_token=AccessToken(CACHED_TOKEN, now - 1))
    token = credential.get_token(SCOPE)

    credential.acquire_token_silently.assert_called_once_with(SCOPE)
    credential.request_token.assert_called_once_with(SCOPE)
    assert token.token == MockCredential.NEW_TOKEN.token


def test_cached_token_outside_refresh_window():
    """A credential shouldn't request a new token when it has a cached one with sufficient validity remaining"""

    credential = MockCredential(cached_token=AccessToken(CACHED_TOKEN, time.time() + DEFAULT_REFRESH_OFFSET + 1))
    token = credential.get_token(SCOPE)

    credential.acquire_token_silently.assert_called_once_with(SCOPE)
    assert credential.request_token.call_count == 0
    assert token.token == CACHED_TOKEN


def test_cached_token_within_refresh_window():
    """A credential should request a new token when its cached one is within the refresh window"""

    credential = MockCredential(cached_token=AccessToken(CACHED_TOKEN, time.time() + DEFAULT_REFRESH_OFFSET - 1))
    token = credential.get_token(SCOPE)

    credential.acquire_token_silently.assert_called_once_with(SCOPE)
    credential.request_token.assert_called_once_with(SCOPE)
    assert token.token == MockCredential.NEW_TOKEN.token


def test_retry_delay():
    """A credential should wait between requests when trying to refresh a token"""

    now = time.time()
    credential = MockCredential(cached_token=AccessToken(CACHED_TOKEN, now + DEFAULT_REFRESH_OFFSET - 1))

    # the credential should swallow exceptions during proactive refresh attempts
    credential.request_token = mock.Mock(side_effect=Exception("whoops"))
    for i in range(4):
        token = credential.get_token(SCOPE)
        assert token.token == CACHED_TOKEN
        credential.acquire_token_silently.assert_called_with(SCOPE)
        credential.request_token.assert_called_once_with(SCOPE)
