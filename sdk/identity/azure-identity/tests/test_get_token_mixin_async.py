# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import concurrent.futures
import pickle
import time
from unittest import mock

from azure.core.credentials import AccessTokenInfo
import pytest

from azure.identity._constants import DEFAULT_REFRESH_OFFSET
from azure.identity.aio._internal import AsyncContextManager
from azure.identity.aio._internal.get_token_mixin import GetTokenMixin

from helpers import GET_TOKEN_METHODS

pytestmark = pytest.mark.asyncio


class MockCredential(AsyncContextManager, GetTokenMixin):
    NEW_TOKEN = AccessTokenInfo("new token", 42)

    def __init__(self, cached_token=None):
        super(MockCredential, self).__init__()
        self.token = cached_token
        self.request_token = mock.Mock(return_value=MockCredential.NEW_TOKEN)
        self.acquire_token_silently = mock.Mock(return_value=cached_token)

    async def close(self) -> None:
        self._cancel_background_refresh_tasks()

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
        cached_token=AccessTokenInfo(CACHED_TOKEN, int(time.time() + DEFAULT_REFRESH_OFFSET + 10))
    )
    token = await getattr(credential, get_token_method)(SCOPE)

    credential.acquire_token_silently.assert_called_once_with(SCOPE, claims=None, enable_cae=False, tenant_id=None)
    assert credential.request_token.call_count == 0
    assert token.token == CACHED_TOKEN


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_cached_token_within_refresh_window(get_token_method):
    """A credential should request a new token inline when its cached one is within the refresh window"""

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
async def test_background_refresh_does_not_block(get_token_method):
    """Background refresh should return the cached token immediately while refreshing in the background"""

    now = int(time.time())
    # Token has plenty of time before expiry but refresh_on has passed, triggering background refresh
    credential = MockCredential(cached_token=AccessTokenInfo(CACHED_TOKEN, now + 3600, refresh_on=now - 1))

    token = await getattr(credential, get_token_method)(SCOPE)

    # The cached token is returned immediately, before the background task completes
    assert token.token == CACHED_TOKEN
    # Wait for background refresh task to complete
    key = ((SCOPE,), None, None, False)
    assert key in credential._background_refresh_tasks
    await asyncio.gather(credential._background_refresh_tasks[key], return_exceptions=True)
    credential.request_token.assert_called_once()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_no_background_refresh_in_trio(get_token_method):
    """When not in asyncio (e.g., trio), refresh should happen inline"""

    now = int(time.time())
    credential = MockCredential(cached_token=AccessTokenInfo(CACHED_TOKEN, now + 3600, refresh_on=now - 1))

    # Simulate a non-asyncio environment by making _uses_asyncio return False
    with mock.patch.object(type(credential), "_uses_asyncio", return_value=False):
        token = await getattr(credential, get_token_method)(SCOPE)

    # Inline refresh returns the new token
    assert token.token == MockCredential.NEW_TOKEN.token
    credential.request_token.assert_called_once_with(SCOPE, claims=None, enable_cae=False, tenant_id=None)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_no_duplicate_background_refresh(get_token_method):
    """If a background refresh is already in progress, a new one should not be started"""

    refresh_started = asyncio.Event()
    refresh_continue = asyncio.Event()

    class SlowMockCredential(MockCredential):
        async def _request_token(self, *scopes, **kwargs):
            refresh_started.set()
            await refresh_continue.wait()
            return self.request_token(*scopes, **kwargs)

    credential = SlowMockCredential(
        cached_token=AccessTokenInfo(CACHED_TOKEN, int(time.time() + 3600), refresh_on=int(time.time()) - 1)
    )

    # First call triggers a background refresh
    token1 = await getattr(credential, get_token_method)(SCOPE)
    assert token1.token == CACHED_TOKEN
    key = ((SCOPE,), None, None, False)
    assert key in credential._background_refresh_tasks
    first_refresh_task = credential._background_refresh_tasks[key]

    # Wait for the background task to start
    await refresh_started.wait()

    # Second call while the first refresh is still in progress should NOT start another task
    token2 = await getattr(credential, get_token_method)(SCOPE)
    assert token2.token == CACHED_TOKEN
    assert credential._background_refresh_tasks[key] is first_refresh_task

    # Let the background refresh complete
    refresh_continue.set()
    await asyncio.gather(first_refresh_task, return_exceptions=True)

    # _request_token should have been called exactly once (no duplicate)
    credential.request_token.assert_called_once()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_different_requests_do_not_share_background_refresh(get_token_method):
    """Different request keys should be allowed to refresh concurrently in the background"""

    scope_1 = "scope-1"
    scope_2 = "scope-2"
    refresh_started_scope_1 = asyncio.Event()
    refresh_started_scope_2 = asyncio.Event()
    refresh_continue = asyncio.Event()

    class SlowMockCredential(MockCredential):
        async def _request_token(self, *scopes, **kwargs):
            if scopes[0] == scope_1:
                refresh_started_scope_1.set()
            elif scopes[0] == scope_2:
                refresh_started_scope_2.set()
            await refresh_continue.wait()
            return self.request_token(*scopes, **kwargs)

    credential = SlowMockCredential(
        cached_token=AccessTokenInfo(CACHED_TOKEN, int(time.time() + 3600), refresh_on=int(time.time()) - 1)
    )

    token1 = await getattr(credential, get_token_method)(scope_1)
    assert token1.token == CACHED_TOKEN
    await refresh_started_scope_1.wait()

    token2 = await getattr(credential, get_token_method)(scope_2)
    assert token2.token == CACHED_TOKEN
    await refresh_started_scope_2.wait()

    key_1 = ((scope_1,), None, None, False)
    key_2 = ((scope_2,), None, None, False)
    assert key_1 in credential._background_refresh_tasks
    assert key_2 in credential._background_refresh_tasks
    assert credential._background_refresh_tasks[key_1] is not credential._background_refresh_tasks[key_2]

    refresh_continue.set()
    await asyncio.gather(
        credential._background_refresh_tasks[key_1],
        credential._background_refresh_tasks[key_2],
        return_exceptions=True,
    )
    assert credential.request_token.call_count == 2


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_background_refresh_failure_returns_cached_token(get_token_method):
    """If the background refresh fails, the caller should still get the cached token"""

    now = int(time.time())
    credential = MockCredential(cached_token=AccessTokenInfo(CACHED_TOKEN, now + 3600, refresh_on=now - 1))
    credential.request_token = mock.Mock(side_effect=Exception("transient error"))

    token = await getattr(credential, get_token_method)(SCOPE)
    assert token.token == CACHED_TOKEN

    key = ((SCOPE,), None, None, False)
    task = credential._background_refresh_tasks.get(key)
    assert task is not None
    await asyncio.gather(task, return_exceptions=True)

    # request_token was called and raised, but the caller was not affected
    credential.request_token.assert_called_once()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_background_refresh_task_cleanup(get_token_method):
    """After a background refresh completes, its task should be removed from the dict"""

    now = int(time.time())
    credential = MockCredential(cached_token=AccessTokenInfo(CACHED_TOKEN, now + 3600, refresh_on=now - 1))

    await getattr(credential, get_token_method)(SCOPE)
    key = ((SCOPE,), None, None, False)
    assert key in credential._background_refresh_tasks

    task = credential._background_refresh_tasks[key]
    await asyncio.gather(task, return_exceptions=True)
    # Allow the done-callback to run
    await asyncio.sleep(0)
    assert key not in credential._background_refresh_tasks


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_cancel_background_refresh_tasks(get_token_method):
    """_cancel_background_refresh_tasks should cancel in-flight tasks (called on close)"""

    refresh_continue = asyncio.Event()

    class SlowMockCredential(MockCredential):
        async def _request_token(self, *scopes, **kwargs):
            await refresh_continue.wait()
            return self.request_token(*scopes, **kwargs)

    now = int(time.time())
    credential = SlowMockCredential(cached_token=AccessTokenInfo(CACHED_TOKEN, now + 3600, refresh_on=now - 1))

    await getattr(credential, get_token_method)(SCOPE)
    key = ((SCOPE,), None, None, False)
    task = credential._background_refresh_tasks[key]
    assert not task.done()

    credential._cancel_background_refresh_tasks()
    assert len(credential._background_refresh_tasks) == 0
    # Wait for the cancellation to fully propagate
    await asyncio.gather(task, return_exceptions=True)
    assert task.cancelled()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_close_cancels_background_refresh(get_token_method):
    """Calling close() directly (without async with) should cancel background tasks"""

    refresh_continue = asyncio.Event()

    class SlowMockCredential(MockCredential):
        async def _request_token(self, *scopes, **kwargs):
            await refresh_continue.wait()
            return self.request_token(*scopes, **kwargs)

    now = int(time.time())
    credential = SlowMockCredential(cached_token=AccessTokenInfo(CACHED_TOKEN, now + 3600, refresh_on=now - 1))

    await getattr(credential, get_token_method)(SCOPE)
    key = ((SCOPE,), None, None, False)
    task = credential._background_refresh_tasks[key]
    assert not task.done()

    await credential.close()
    assert len(credential._background_refresh_tasks) == 0
    await asyncio.gather(task, return_exceptions=True)
    assert task.cancelled()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_pickle_with_active_background_refresh(get_token_method):
    """A credential should be picklable even when a background refresh task is active"""

    now = int(time.time())
    credential = MockCredential(cached_token=AccessTokenInfo(CACHED_TOKEN, now + 3600, refresh_on=now - 1))

    await getattr(credential, get_token_method)(SCOPE)
    key = ((SCOPE,), None, None, False)
    task = credential._background_refresh_tasks.get(key)
    assert task is not None

    # Mock attributes set to None since Mock objects aren't picklable.
    credential.request_token = None
    credential.acquire_token_silently = None
    pickled = pickle.dumps(credential)
    restored = pickle.loads(pickled)
    assert restored._background_refresh_tasks == {}
    assert restored._last_request_time == credential._last_request_time

    # Clean up
    await asyncio.gather(task, return_exceptions=True)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_background_refresh_multithread_event_loops(get_token_method):
    """Background refresh should work when multiple threads each run their own event loop."""

    now = int(time.time())
    credential = MockCredential(cached_token=AccessTokenInfo(CACHED_TOKEN, now + 3600, refresh_on=now - 1))

    def run_in_thread():
        async def get_token():
            return await getattr(credential, get_token_method)(SCOPE)

        return asyncio.run(get_token())

    num_threads = 4
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(run_in_thread) for _ in range(num_threads)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    for token in results:
        assert token.token == CACHED_TOKEN
