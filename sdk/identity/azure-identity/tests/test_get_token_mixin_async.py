# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
import asyncio
from asyncio import sleep as real_sleep
import gc
import weakref
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


class MockCredentialWithDelay(GetTokenMixin):
    def __init__(self, cached_token=None):
        super().__init__()
        self.cached_token = cached_token
        self.request_count = 0

    async def _acquire_token_silently(self, *scopes, **kwargs):
        return self.cached_token

    async def _request_token(self, *scopes, **kwargs):
        self.request_count += 1
        request_count = self.request_count
        await real_sleep(0.2)  # Simulate network delay, give other coroutines time to queue up
        self.cached_token = AccessTokenInfo(f"token_{request_count}", int(time.time() + 3600))
        return self.cached_token


CACHED_TOKEN = "cached token"
SCOPE = "scope"


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_no_cached_token(get_token_method):
    """When it has no token cached, a credential should request one every time get_token is called"""

    credential = MockCredential()
    token = await getattr(credential, get_token_method)(SCOPE)

    # Due to double-checking pattern in concurrency control, _acquire_token_silently may be called twice
    assert credential.acquire_token_silently.call_count >= 1
    credential.acquire_token_silently.assert_any_call(SCOPE, claims=None, enable_cae=False, tenant_id=None)
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

    # Due to double-checking pattern in concurrency control, _acquire_token_silently may be called multiple times
    assert credential.acquire_token_silently.call_count >= 1
    credential.acquire_token_silently.assert_any_call(SCOPE, claims=None, enable_cae=False, tenant_id=None)
    credential.request_token.assert_called_once_with(SCOPE, claims=None, enable_cae=False, tenant_id=None)
    assert token.token == MockCredential.NEW_TOKEN.token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_cached_token_outside_refresh_window(get_token_method):
    """A credential shouldn't request a new token when it has a cached one with sufficient validity remaining"""

    credential = MockCredential(
        cached_token=AccessTokenInfo(CACHED_TOKEN, int(time.time() + DEFAULT_REFRESH_OFFSET + 10))
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

    # Due to double-checking pattern in concurrency control, _acquire_token_silently may be called multiple times
    assert credential.acquire_token_silently.call_count >= 1
    credential.acquire_token_silently.assert_any_call(SCOPE, claims=None, enable_cae=False, tenant_id=None)
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


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_concurrent_token_requests(get_token_method):
    """When multiple coroutines request tokens concurrently, only one token request should be made"""
    credential = MockCredentialWithDelay()

    # Launch multiple concurrent token requests
    tasks = [getattr(credential, get_token_method)(SCOPE) for _ in range(5)]
    tokens = await asyncio.gather(*tasks)

    # All tasks should get the same token
    for token in tokens:
        assert token.token == "token_1"

    # Only one token request should have been made despite 5 concurrent calls
    assert credential.request_count == 1


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_concurrent_token_refresh(get_token_method):
    """When multiple coroutines need to refresh tokens concurrently, only one refresh should happen"""

    # Create a credential with a token that needs refresh
    old_token = AccessTokenInfo("old_token", int(time.time() + DEFAULT_REFRESH_OFFSET - 1))
    credential = MockCredentialWithDelay(old_token)

    # Launch multiple concurrent token requests that need refresh
    tasks = [getattr(credential, get_token_method)(SCOPE) for _ in range(5)]
    tokens = await asyncio.gather(*tasks)

    # All tasks should get the refreshed token
    for token in tokens:
        assert token.token == "token_1"

    # Only one refresh should have been made despite 5 concurrent calls needing refresh
    assert credential.request_count == 1


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_concurrent_different_scopes_run_independently(get_token_method):
    """When multiple coroutines request different scopes concurrently, they should run independently"""

    class MockCredentialWithScopeCache(GetTokenMixin):
        def __init__(self):
            super().__init__()
            self.cached_tokens = {}  # Store tokens by scope
            self.request_count = 0

        async def _acquire_token_silently(self, *scopes, **kwargs):
            lock_key = tuple(sorted(scopes))
            return self.cached_tokens.get(lock_key)

        async def _request_token(self, *scopes, **kwargs):
            self.request_count += 1
            request_count = self.request_count
            await real_sleep(0.2)
            lock_key = tuple(sorted(scopes))
            token = AccessTokenInfo(f"token_{lock_key[0]}_{request_count}", int(time.time() + 3600))
            self.cached_tokens[lock_key] = token
            return token

    credential = MockCredentialWithScopeCache()

    # Create different scope combinations
    scope1 = "scope1"
    scope2 = "scope2"
    scope3 = "scope3"

    # Launch concurrent requests for different scopes - these should NOT wait on each other
    tasks = [
        getattr(credential, get_token_method)(scope1),
        getattr(credential, get_token_method)(scope1),  # Same scope - should wait
        getattr(credential, get_token_method)(scope2),  # Different scope - should run independently
        getattr(credential, get_token_method)(scope2),  # Same scope - should wait
        getattr(credential, get_token_method)(scope3),  # Different scope - should run independently
    ]

    tokens = await asyncio.gather(*tasks)

    # Should have made 3 requests total (one for each unique scope)
    assert credential.request_count == 3

    # Check that tokens for the same scope are identical
    assert tokens[0].token == tokens[1].token  # scope1 tokens should be the same
    assert tokens[2].token == tokens[3].token  # scope2 tokens should be the same

    # Check that tokens for different scopes are different
    assert tokens[0].token != tokens[2].token  # scope1 != scope2
    assert tokens[0].token != tokens[4].token  # scope1 != scope3
    assert tokens[2].token != tokens[4].token  # scope2 != scope3


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_concurrent_different_options_run_independently(get_token_method):
    """When multiple coroutines request tokens with different options, they should run independently"""

    class RealisticMockCredential(GetTokenMixin):
        def __init__(self):
            super().__init__()
            self.cached_tokens = {}  # Store tokens by options key
            self.request_count = 0

        async def _acquire_token_silently(self, *scopes, **kwargs):
            # Create a key based on all parameters that matter for caching
            key = (
                tuple(sorted(scopes)),
                kwargs.get("claims"),
                kwargs.get("tenant_id"),
                kwargs.get("enable_cae", False),
            )

            return self.cached_tokens.get(key)

        async def _request_token(self, *scopes, **kwargs):
            self.request_count += 1
            request_count = self.request_count
            await real_sleep(0.2)  # Simulate network delay
            key = (
                tuple(sorted(scopes)),
                kwargs.get("claims"),
                kwargs.get("tenant_id"),
                kwargs.get("enable_cae", False),
            )
            token = AccessTokenInfo(f"token_{request_count}", int(time.time() + 3600))
            self.cached_tokens[key] = token
            return token

    credential = RealisticMockCredential()

    # Create tasks with different options that should run independently
    if get_token_method == "get_token":
        tasks = [
            credential.get_token(SCOPE),  # No options
            credential.get_token(SCOPE),  # Same - should wait
            credential.get_token(SCOPE, tenant_id="tenant1"),  # Different tenant - should run independently
            credential.get_token(SCOPE, tenant_id="tenant1"),  # Same tenant - should wait
            credential.get_token(SCOPE, claims="claim1"),  # Different claims - should run independently
            credential.get_token(SCOPE, enable_cae=True),  # Different enable_cae - should run independently
        ]
    else:  # get_token_info
        tasks = [
            credential.get_token_info(SCOPE),  # No options
            credential.get_token_info(SCOPE),  # Same - should wait
            credential.get_token_info(
                SCOPE, options={"tenant_id": "tenant1"}
            ),  # Different tenant - should run independently
            credential.get_token_info(SCOPE, options={"tenant_id": "tenant1"}),  # Same tenant - should wait
            credential.get_token_info(
                SCOPE, options={"claims": "claim1"}
            ),  # Different claims - should run independently
            credential.get_token_info(
                SCOPE, options={"enable_cae": True}
            ),  # Different enable_cae - should run independently
        ]

    tokens = await asyncio.gather(*tasks)

    # Should have made 4 requests total (one for each unique option combination)
    assert credential.request_count == 4

    # Check that tokens for the same options are identical
    assert tokens[0].token == tokens[1].token  # Same options
    assert tokens[2].token == tokens[3].token  # Same tenant_id

    # Check that tokens for different options are different
    assert tokens[0].token != tokens[2].token  # No options != tenant_id
    assert tokens[0].token != tokens[4].token  # No options != claims
    assert tokens[2].token != tokens[4].token  # tenant_id != claims
    assert tokens[0].token != tokens[5].token  # No options != enable_cae


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_weakref_dictionary_cleanup(get_token_method):
    """Test that locks are automatically cleaned up from the WeakValueDictionary when no longer referenced"""

    class MockCredentialWithLockTracking(GetTokenMixin):
        def __init__(self):
            super().__init__()
            self.cached_tokens = {}
            self.request_count = 0
            self.lock_refs = []  # Store strong references during requests

        async def _acquire_token_silently(self, *scopes, **kwargs):
            return None

        async def _request_token(self, *scopes, **kwargs):
            self.request_count += 1
            # Capture a reference to the current scope's lock
            lock_key = (
                tuple(sorted(scopes)),
                kwargs.get("claims"),
                kwargs.get("tenant_id"),
                kwargs.get("enable_cae", False),
            )
            if lock_key in self._active_locks:
                self.lock_refs.append(self._active_locks[lock_key])
            await asyncio.sleep(0.1)
            lock_key_for_token = tuple(sorted(scopes))
            token = AccessTokenInfo(f"token_{lock_key_for_token[0]}", int(time.time() + 3600))
            self.cached_tokens[lock_key_for_token] = token
            return token

    credential = MockCredentialWithLockTracking()

    # Request tokens for multiple scopes concurrently to create locks
    scope1 = "scope1"
    scope2 = "scope2"
    scope3 = "scope3"

    # Start concurrent requests - these will create locks and hold them during _request_token
    tasks = [
        getattr(credential, get_token_method)(scope1),
        getattr(credential, get_token_method)(scope2),
        getattr(credential, get_token_method)(scope3),
    ]

    # Wait for all requests to complete
    await asyncio.gather(*tasks)

    # At this point, lock_refs contains strong references to the locks
    # that were created during the requests
    initial_lock_count = len(credential.lock_refs)
    assert initial_lock_count == 3, f"Should have captured 3 lock references, got {initial_lock_count}"

    assert len(credential._active_locks) == 3, "WeakValueDictionary should contain 3 locks"

    # Create weak references to track when locks are deallocated
    weak_refs = [weakref.ref(lock) for lock in credential.lock_refs]

    # Verify all locks are still alive (because we hold strong refs in lock_refs)
    assert all(ref() is not None for ref in weak_refs), "All locks should be alive while strong refs exist"

    # Clear the strong references
    credential.lock_refs.clear()

    # Force garbage collection
    gc.collect()

    # After GC, the weak references should be dead
    assert all(ref() is None for ref in weak_refs), "All locks should be GC'd after strong refs are removed"

    # The WeakValueDictionary should automatically clean up dead entries
    # Access the dict to trigger cleanup
    remaining_locks = len(credential._active_locks)

    assert remaining_locks == 0, f"WeakValueDictionary should be empty after GC, but has {remaining_locks} entries"

    # Verify we can still use the credential and create new locks
    credential.lock_refs.clear()
    await getattr(credential, get_token_method)(scope1)

    # A new lock should be created
    assert len(credential.lock_refs) == 1, "Should be able to create new locks after cleanup"


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_concurrent_refresh_with_failure_fallback(get_token_method):
    """When refresh fails during concurrent requests, all should get the old token as fallback"""

    class MockCredentialWithFailure(GetTokenMixin):
        def __init__(self, cached_token):
            super().__init__()
            self.cached_token = cached_token
            self.request_count = 0

        async def _acquire_token_silently(self, *scopes, **kwargs):
            return self.cached_token

        async def _request_token(self, *scopes, **kwargs):
            self.request_count += 1
            await real_sleep(0.2)
            raise Exception("Network error during refresh")

    # Token that needs refresh but is not expired
    old_token = AccessTokenInfo("fallback_token", int(time.time() + DEFAULT_REFRESH_OFFSET - 1))
    credential = MockCredentialWithFailure(old_token)

    # Launch concurrent requests - all should get fallback token
    tasks = [getattr(credential, get_token_method)(SCOPE) for _ in range(5)]
    tokens = await asyncio.gather(*tasks)

    # All should receive the fallback token
    for token in tokens:
        assert token.token == "fallback_token"

    # Only one refresh attempt should have been made
    assert credential.request_count == 1


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_concurrent_refresh_failure_no_fallback(get_token_method):
    """When refresh fails with no cached token, all concurrent requests should get the exception"""

    class MockCredentialWithFailure(GetTokenMixin):
        def __init__(self):
            super().__init__()
            self.request_count = 0

        async def _acquire_token_silently(self, *scopes, **kwargs):
            return None

        async def _request_token(self, *scopes, **kwargs):
            self.request_count += 1
            await real_sleep(0.2)
            raise ValueError("Authentication failed")

    credential = MockCredentialWithFailure()

    # Launch concurrent requests - all should hit the exception
    tasks = [getattr(credential, get_token_method)(SCOPE) for _ in range(3)]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # All results should be ValueError exceptions
    assert all(isinstance(r, ValueError) for r in results)
    assert all(str(r) == "Authentication failed" for r in results)
    assert credential.request_count == 3


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_token_with_refresh_on_attribute(get_token_method):
    """Test that tokens with refresh_on attribute are handled correctly in concurrent scenarios"""

    class MockCredentialWithRefreshOn(GetTokenMixin):
        def __init__(self, cached_token):
            super().__init__()
            self.cached_token = cached_token
            self.request_count = 0

        async def _acquire_token_silently(self, *scopes, **kwargs):
            return self.cached_token

        async def _request_token(self, *scopes, **kwargs):
            self.request_count += 1
            request_count = self.request_count
            await real_sleep(0.2)
            # Create token with refresh_on set to future time
            token = AccessTokenInfo(
                f"token_{request_count}",
                int(time.time() + 3600),
                refresh_on=int(time.time() + 1800),  # Refresh halfway through validity
            )
            self.cached_token = token
            return token

    # Create token with refresh_on in the past (needs immediate refresh)
    old_token = AccessTokenInfo("old_token", int(time.time() + 3600), refresh_on=int(time.time() - 1))
    credential = MockCredentialWithRefreshOn(old_token)

    # Launch concurrent requests
    tasks = [getattr(credential, get_token_method)(SCOPE) for _ in range(5)]
    tokens = await asyncio.gather(*tasks)

    # All should get the new token
    for token in tokens:
        assert token.token == "token_1"

    # Only one refresh should have been made
    assert credential.request_count == 1


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_no_token_refresh_failure_raises(get_token_method):
    """When there's no token and refresh fails, should raise the exception"""

    class MockCredentialNoToken(GetTokenMixin):
        def __init__(self):
            super().__init__()
            self.acquire_called = False
            self.request_called = False

        async def _acquire_token_silently(self, *scopes, **kwargs):
            self.acquire_called = True
            return None

        async def _request_token(self, *scopes, **kwargs):
            self.request_called = True
            raise ValueError("Authentication failed - no credentials")

    credential = MockCredentialNoToken()

    with pytest.raises(ValueError) as exc_info:
        await getattr(credential, get_token_method)(SCOPE)

    assert str(exc_info.value) == "Authentication failed - no credentials"
    assert credential.acquire_called
    assert credential.request_called


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_expired_token_refresh_failure_raises(get_token_method):
    """When token is expired and refresh fails, should raise the exception"""

    class MockCredentialExpiredToken(GetTokenMixin):
        def __init__(self):
            super().__init__()
            self.cached_token = AccessTokenInfo("expired_token", int(time.time() - 100))
            self.request_called = False

        async def _acquire_token_silently(self, *scopes, **kwargs):
            return self.cached_token

        async def _request_token(self, *scopes, **kwargs):
            self.request_called = True
            raise ValueError("Network error during refresh")

    credential = MockCredentialExpiredToken()

    with pytest.raises(ValueError) as exc_info:
        await getattr(credential, get_token_method)(SCOPE)

    assert str(exc_info.value) == "Network error during refresh"
    assert credential.request_called


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_valid_token_in_refresh_window_refresh_fails_returns_old(get_token_method):
    """When token is in refresh window and refresh fails, return the old (still valid) token"""

    class MockCredentialRefreshWindowToken(GetTokenMixin):
        def __init__(self):
            super().__init__()
            # Token in refresh window (expires in 200s, refresh offset is 300s)
            self.cached_token = AccessTokenInfo("old_valid_token", int(time.time() + 200))
            self.request_called = False

        async def _acquire_token_silently(self, *scopes, **kwargs):
            return self.cached_token

        async def _request_token(self, *scopes, **kwargs):
            self.request_called = True
            raise ValueError("Transient network error")

    credential = MockCredentialRefreshWindowToken()
    token = await getattr(credential, get_token_method)(SCOPE)

    assert token.token == "old_valid_token", "Should return old token when refresh fails but token is still valid"
    assert credential.request_called, "Should have attempted refresh for token in refresh window"


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_valid_token_in_refresh_window_refresh_succeeds_returns_new(get_token_method):
    """When token is in refresh window and refresh succeeds, return the new token"""

    class MockCredentialRefreshSuccess(GetTokenMixin):
        def __init__(self):
            super().__init__()
            # Token in refresh window
            self.cached_token = AccessTokenInfo("old_token", int(time.time() + 200))
            self.request_called = False

        async def _acquire_token_silently(self, *scopes, **kwargs):
            return self.cached_token

        async def _request_token(self, *scopes, **kwargs):
            self.request_called = True
            return AccessTokenInfo("new_refreshed_token", int(time.time() + 3600))

    credential = MockCredentialRefreshSuccess()
    token = await getattr(credential, get_token_method)(SCOPE)

    assert token.token == "new_refreshed_token", "Should return new token when refresh succeeds"
    assert credential.request_called
