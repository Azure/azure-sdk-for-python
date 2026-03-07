# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import gc
import pickle
import time
import threading
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


CACHED_TOKEN = "cached token"
SCOPE = "scope"


class PicklableCredential(GetTokenMixin):
    NEW_TOKEN = AccessTokenInfo("new token", 42)

    def __init__(self):
        super().__init__()

    async def _acquire_token_silently(self, *scopes, **kwargs):
        return None

    async def _request_token(self, *scopes, **kwargs):
        return self.NEW_TOKEN

    async def get_token(self, *args, **kwargs):
        return await super().get_token(*args, **kwargs)

    async def get_token_info(self, *args, **kwargs):
        return await super().get_token_info(*args, **kwargs)


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


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_concurrent_same_scope_serialized(get_token_method):
    """Concurrent get_token calls for the same scopes should be serialized by the lock."""
    call_count = 0
    max_concurrent = 0
    current_concurrent = 0

    original_new_token = MockCredential.NEW_TOKEN

    async def slow_request_token(*args, **kwargs):
        nonlocal call_count, max_concurrent, current_concurrent
        current_concurrent += 1
        max_concurrent = max(max_concurrent, current_concurrent)
        call_count += 1
        await asyncio.sleep(0.1)
        current_concurrent -= 1
        return original_new_token

    credential = MockCredential()
    credential._request_token = slow_request_token

    tasks = [getattr(credential, get_token_method)(SCOPE) for _ in range(5)]
    results = await asyncio.gather(*tasks)

    for result in results:
        assert result.token == original_new_token.token
    # With lock, max concurrency for the same scope should be 1
    assert max_concurrent == 1


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_concurrent_different_scopes_parallel(get_token_method):
    """Concurrent get_token calls with different scopes should proceed in parallel."""
    num_tasks = 3
    entered_count = 0
    max_concurrent = 0
    all_entered = asyncio.Event()
    original_new_token = MockCredential.NEW_TOKEN

    async def sync_request_token(*args, **kwargs):
        nonlocal entered_count, max_concurrent
        entered_count += 1
        max_concurrent = max(max_concurrent, entered_count)
        if entered_count >= num_tasks:
            all_entered.set()
        # Wait until all tasks have entered; timeout detects serialization
        try:
            await asyncio.wait_for(all_entered.wait(), timeout=5)
        except asyncio.TimeoutError:
            pass
        entered_count -= 1
        return original_new_token

    credential = MockCredential()
    credential._request_token = sync_request_token

    scopes = [f"scope{i}" for i in range(num_tasks)]
    tasks = [getattr(credential, get_token_method)(s) for s in scopes]
    await asyncio.gather(*tasks)

    # Different scopes use different locks, so all tasks should enter concurrently
    assert max_concurrent == num_tasks


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_lock_released_on_exception(get_token_method):
    """The lock should be released when _request_token raises an exception."""
    credential = MockCredential()
    credential.request_token = mock.Mock(side_effect=Exception("request failed"))

    with pytest.raises(Exception, match="request failed"):
        await getattr(credential, get_token_method)(SCOPE)

    # The lock should be released; a second call should not deadlock
    credential.request_token = mock.Mock(return_value=MockCredential.NEW_TOKEN)
    token = await asyncio.wait_for(getattr(credential, get_token_method)(SCOPE), timeout=5)
    assert token.token == MockCredential.NEW_TOKEN.token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_lock_timeout_proceeds(get_token_method):
    """When the lock times out, the credential should proceed with the token request."""
    original_new_token = MockCredential.NEW_TOKEN

    credential = MockCredential()

    # Acquire the lock manually so the credential's attempt will time out
    lock = credential._get_request_lock((SCOPE,), None, None, False)
    assert lock
    await lock.acquire()

    try:
        with mock.patch("azure.identity.aio._internal.get_token_mixin.DEFAULT_TOKEN_LOCK_TIMEOUT", 0.1):
            token = await asyncio.wait_for(getattr(credential, get_token_method)(SCOPE), timeout=5)
            assert token.token == original_new_token.token
    finally:
        lock.release()


async def test_multithread_different_loops():
    """A credential shared across threads with different event loops should work correctly."""
    credential = MockCredential()
    results = []
    errors = []

    def run_in_thread():
        loop = asyncio.new_event_loop()
        try:
            token = loop.run_until_complete(credential.get_token(SCOPE))
            results.append(token.token)
        except Exception as e:
            errors.append(e)
        finally:
            loop.close()

    threads = [threading.Thread(target=run_in_thread) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)

    assert not errors, f"Errors in threads: {errors}"
    assert len(results) == 3
    for token in results:
        assert token == MockCredential.NEW_TOKEN.token


def test_asyncio_run_loop_cleanup():
    """After asyncio.run() completes, the internally-created event loop should not be
    retained in _locks because WeakKeyDictionary drops keys with no strong references."""
    credential = MockCredential()

    async def use_credential():
        token = await credential.get_token(SCOPE)
        assert token.token == MockCredential.NEW_TOKEN.token
        # While running, the current loop should have a locks entry
        assert len(credential._locks) >= 1

    asyncio.run(use_credential())

    # The loop created by asyncio.run() is now closed and unreferenced
    gc.collect()

    # All loop entries should have been cleaned up
    assert len(credential._locks) == 0


async def test_same_key_returns_same_lock():
    """Calling _get_request_lock with the same arguments should return the same lock object."""
    credential = MockCredential()
    lock1 = credential._get_request_lock(("scope1",), None, None, False)
    lock2 = credential._get_request_lock(("scope1",), None, None, False)
    assert lock1 is lock2


async def test_different_keys_return_different_locks():
    """Calling _get_request_lock with different arguments should return different lock objects."""
    credential = MockCredential()
    lock_a = credential._get_request_lock(("scope1",), None, None, False)
    lock_b = credential._get_request_lock(("scope2",), None, None, False)
    lock_c = credential._get_request_lock(("scope1",), "claims", None, False)
    lock_d = credential._get_request_lock(("scope1",), None, "tenant", False)
    lock_e = credential._get_request_lock(("scope1",), None, None, True)

    locks = [lock_a, lock_b, lock_c, lock_d, lock_e]
    # All locks should be distinct objects
    for i in range(len(locks)):
        for j in range(i + 1, len(locks)):
            assert locks[i] is not locks[j]


async def test_lock_cleaned_up_when_no_strong_reference():
    """Locks in the inner WeakValueDictionary should be removed when no strong reference exists."""
    credential = MockCredential()
    loop = asyncio.get_running_loop()
    key = (("scope_temp",), None, None, False)

    lock = credential._get_request_lock(*key)
    assert lock is not None

    # The inner dict should have an entry for this key
    loop_locks = credential._locks[loop]
    assert loop_locks.get(key) is lock

    # Drop the only strong reference to the lock
    del lock

    gc.collect()

    # The WeakValueDictionary entry should now be gone
    assert loop_locks.get(key) is None


async def test_event_loop_cleanup_removes_locks():
    """When an event loop is garbage-collected, its entry in _locks should be removed."""
    credential = MockCredential()

    # Create a new event loop, use it to populate _locks, then discard it.
    spare_loop = asyncio.new_event_loop()
    key = (("scope_loop",), None, None, False)

    # Manually populate the locks dict for the spare loop
    lock = asyncio.Lock()
    inner = weakref.WeakValueDictionary()
    inner[key] = lock
    credential._locks[spare_loop] = inner

    assert spare_loop in credential._locks

    # Drop all strong references to the spare loop
    del spare_loop

    gc.collect()

    # The outer WeakKeyDictionary should no longer contain the loop entry
    assert len(credential._locks) <= 1  # At most the running loop, not the spare


async def test_lock_persists_while_strong_reference_held():
    """A lock should remain in the WeakValueDictionary as long as a strong reference is held."""
    credential = MockCredential()
    loop = asyncio.get_running_loop()
    key = (("scope_persist",), None, None, False)

    lock = credential._get_request_lock(*key)

    gc.collect()

    # Lock should still be present because we hold a strong reference
    assert credential._locks[loop].get(key) is lock


async def test_multiple_scopes_independent_cleanup():
    """Locks for different scope keys should be independently garbage-collected."""
    credential = MockCredential()
    loop = asyncio.get_running_loop()

    key_a = (("scopeA",), None, None, False)
    key_b = (("scopeB",), None, None, False)

    lock_a = credential._get_request_lock(*key_a)
    lock_b = credential._get_request_lock(*key_b)

    loop_locks = credential._locks[loop]
    assert loop_locks.get(key_a) is lock_a
    assert loop_locks.get(key_b) is lock_b

    # Drop only the reference to lock_a
    del lock_a

    gc.collect()

    # lock_a's entry should be cleaned up, but lock_b should remain
    assert loop_locks.get(key_a) is None
    assert loop_locks.get(key_b) is lock_b


async def test_pickle_roundtrip():
    """GetTokenMixin instances should be picklable."""
    credential = PicklableCredential()
    token = await credential.get_token(SCOPE)
    assert token.token == PicklableCredential.NEW_TOKEN.token

    pickled = pickle.dumps(credential)
    restored = pickle.loads(pickled)

    assert restored._last_request_time == credential._last_request_time
    assert isinstance(restored._locks, weakref.WeakKeyDictionary)
    assert len(restored._locks) == 0

    # Ensure the restored credential still works
    token = await restored.get_token(SCOPE)
    assert token.token == PicklableCredential.NEW_TOKEN.token
