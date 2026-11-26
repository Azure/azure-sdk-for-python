# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Credential requests borrow the application loop without owning its lifetime."""

import asyncio
import functools
import json
import threading
from types import SimpleNamespace

import pytest

from azure.cosmos._backend._async_credential_bridge import AsyncTokenCredentialBridge
from azure.cosmos._backend.credentials import resolve_credential


@pytest.mark.parametrize("returns_awaitable", [False, True], ids=["plain-token", "opaque-coroutine"])
def test_context_manager_token_result_matches_legacy_policy_rust(monkeypatch, returns_awaitable):
    from azure.core.credentials import AccessToken
    from azure.core.pipeline import PipelineContext, PipelineRequest
    from azure.core.rest import HttpRequest
    from azure.cosmos.aio import CosmosClient
    from azure.cosmos.aio._auth_policy_async import AsyncCosmosBearerTokenCredentialPolicy
    from azure.cosmos.aio._backend import binding_adapter

    scope = "https://account.example/.default"
    token = AccessToken("example-token-not-for-use", 4102444800)
    calls = []

    class Credential:
        async def __aenter__(self):
            raise AssertionError("The SDK must not enter the customer's credential")

        async def __aexit__(self, *exc):
            raise AssertionError("The SDK must not close the customer's credential")

        def get_token(self, *scopes, **kwargs):
            calls.append((scopes, asyncio.get_running_loop()))
            if returns_awaitable:
                async def complete():
                    return token
                return complete()
            return token

    credential = Credential()
    handle = object()
    released = []
    received = []

    def acquire(_endpoint, _key, _config, bridge):
        received.append(bridge._start_token_request(scope).result(timeout=5))
        return handle

    monkeypatch.setattr(
        binding_adapter,
        "_rust_module",
        SimpleNamespace(
            acquire_driver_handle=acquire,
            release_driver_handle=released.append,
            _DriverResponseError=type("_DriverResponseError", (RuntimeError,), {}),
            _DriverTransportError=type("_DriverTransportError", (RuntimeError,), {}),
        ),
    )
    client = CosmosClient("https://account.example", credential, _backend="rust")
    assert not calls

    async def run():
        try:
            request = PipelineRequest(HttpRequest("GET", "https://account.example"), PipelineContext(None))
            await AsyncCosmosBearerTokenCredentialPolicy(credential, scope).on_request(request)
            assert request.http_request.headers["Authorization"] == f"type=aad&ver=1.0&sig={token.token}"
            await client._adapter.initialize()
            assert received == [token]
            assert calls == [((scope,), asyncio.get_running_loop())] * 2
        finally:
            await client.close()

    asyncio.run(run())
    assert released == [handle]


@pytest.mark.parametrize("method_name", ["get_token", "get_token_info"])
@pytest.mark.parametrize("decoration", ["wrapped", "asyncio_marked"])
def test_credential_resolution_and_bridge_agree_on_async_methods_rust(
    credential_owner_loop, method_name, decoration
):
    token = SimpleNamespace(token="test-token", expires_on=4102444800)

    async def token_method(*scopes):
        assert scopes == ("scope",)
        return token

    def decorated(*scopes):
        return token_method(*scopes)

    if decoration == "wrapped":
        decorated = functools.wraps(token_method)(decorated)
    else:
        marker = getattr(asyncio.coroutines, "_is_coroutine", None)
        if marker is None:
            pytest.skip("This Python version has no legacy asyncio coroutine marker")
        setattr(decorated, "_is_coroutine", marker)
        if not asyncio.iscoroutinefunction(decorated):
            pytest.skip("This Python version no longer recognizes asyncio coroutine markers")

    credential = SimpleNamespace(**{method_name: decorated})
    with pytest.raises(TypeError, match="Synchronous CosmosClient"):
        resolve_credential(credential)
    master_key, resolved = resolve_credential(credential, allow_async=True)
    assert master_key is None
    assert resolved is credential
    bridge = AsyncTokenCredentialBridge.acquire(resolved, loop=credential_owner_loop)
    try:
        assert bridge._start_token_request("scope").result(timeout=2) is token
    finally:
        bridge._close_cosmos_async_bridge()


@pytest.mark.parametrize("error_type", [TimeoutError, asyncio.CancelledError])
def test_bridge_preserves_credential_exception_identity_rust(credential_owner_loop, error_type):
    error = error_type("credential failed")
    original_cause = ValueError("credential cause")
    error.__cause__ = original_cause

    class Credential:
        async def get_token(self, *scopes):
            raise error

    bridge = AsyncTokenCredentialBridge(Credential(), loop=credential_owner_loop)
    try:
        with pytest.raises(error_type) as caught:
            bridge._start_token_request("scope").result(timeout=2)
        assert caught.value is error
        assert caught.value.__cause__ is original_cause
    finally:
        bridge._close_cosmos_async_bridge()


def test_native_result_cancellation_reaches_credential_coroutine_rust(credential_owner_loop):
    started = threading.Event()
    cancelled = threading.Event()

    class Credential:
        async def get_token(self, *scopes):
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

    bridge = AsyncTokenCredentialBridge(Credential(), loop=credential_owner_loop)
    try:
        future = bridge._start_token_request("scope")
        assert started.wait(2)
        future.cancel()
        assert cancelled.wait(2)
        assert not bridge._pending
    finally:
        bridge._close_cosmos_async_bridge()
    assert credential_owner_loop.is_running()


def test_last_release_cancels_only_bridge_owned_work_rust():
    async def run():
        started, cancelled = asyncio.Event(), asyncio.Event()
        credential_closed = False

        class Credential:
            async def get_token(self, *scopes):
                started.set()
                try:
                    await asyncio.Event().wait()
                finally:
                    cancelled.set()

            async def close(self):
                nonlocal credential_closed
                credential_closed = True

        credential = Credential()
        first = AsyncTokenCredentialBridge.acquire(credential)
        second = AsyncTokenCredentialBridge.acquire(credential)
        unrelated = asyncio.create_task(asyncio.Event().wait())
        try:
            pending = first._start_token_request("scope")
            await asyncio.wait_for(started.wait(), 2)
            first._close_cosmos_async_bridge()
            assert not pending.done()
            second._close_cosmos_async_bridge()
            await asyncio.wait_for(cancelled.wait(), 2)
            assert pending.cancelled()
            assert not unrelated.done()
            assert not credential_closed
            assert asyncio.get_running_loop().is_running()
        finally:
            if first._refcount:
                first._close_cosmos_async_bridge()
            if second._refcount:
                second._close_cosmos_async_bridge()
            unrelated.cancel()
            await asyncio.gather(unrelated, return_exceptions=True)

    asyncio.run(run())


def test_shared_credential_cannot_move_between_active_application_loops_rust(credential_owner_loop):
    credential = object()
    first = AsyncTokenCredentialBridge.acquire(credential, loop=credential_owner_loop)

    async def run():
        with pytest.raises(RuntimeError, match="different application loop"):
            AsyncTokenCredentialBridge.acquire(credential)
        with pytest.raises(RuntimeError, match="original application loop"):
            first.check_owner_loop(asyncio.get_running_loop())

    try:
        asyncio.run(run())
    finally:
        first._close_cosmos_async_bridge()


def test_stopped_or_closed_owner_loop_is_rejected_rust():
    loop = asyncio.new_event_loop()
    try:
        with pytest.raises(RuntimeError, match="must be running"):
            AsyncTokenCredentialBridge(object(), loop=loop)
    finally:
        loop.close()
    with pytest.raises(RuntimeError, match="must be running"):
        AsyncTokenCredentialBridge(object(), loop=loop)


def test_closed_bridge_rejects_scheduling_without_creating_coroutine_rust(credential_owner_loop):
    class Credential:
        async def get_token(self, *scopes):
            raise AssertionError("closed bridge must not execute credential")

    bridge = AsyncTokenCredentialBridge(Credential(), loop=credential_owner_loop)
    bridge._close_cosmos_async_bridge()
    with pytest.raises(RuntimeError, match="closed"):
        bridge._start_token_request("scope")


def test_real_identity_credential_keeps_its_application_session_before_and_after_cosmos_rust(monkeypatch):
    from azure.core.pipeline.transport import AsyncHttpResponse
    from azure.core.pipeline.transport._aiohttp import AioHttpTransport
    from azure.identity.aio import ClientSecretCredential
    from azure.cosmos import CosmosClient
    from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
    from azure.cosmos.aio._backend import binding_adapter

    class TokenResponse(AsyncHttpResponse):
        def __init__(self, request, token):
            super().__init__(request, None)
            self.status_code = 200
            self.headers = {"Content-Type": "application/json"}
            self.reason = "OK"
            self._body = json.dumps(
                {
                    "access_token": token,
                    "expires_in": 3600,
                    "token_type": "Bearer",
                }
            ).encode()

        def body(self):
            return self._body

    class SessionTransport(AioHttpTransport):
        def __init__(self):
            super().__init__()
            self.loops = []

        async def send(self, request, **kwargs):
            await self.open()
            loop = asyncio.get_running_loop()
            self.loops.append(loop)
            assert self.session._loop is loop
            assert request.method == "POST"
            assert request.url.endswith("/oauth2/v2.0/token")
            return TokenResponse(request, f"offline-token-{len(self.loops)}")

    transport = SessionTransport()
    credential = ClientSecretCredential(
        "tenant",
        "client",
        "unused-offline-secret",
        disable_instance_discovery=True,
        transport=transport,
    )
    with pytest.raises(TypeError, match="Synchronous CosmosClient"):
        CosmosClient("https://account.example", credential, _backend="rust")
    # Construction must remain possible before an application loop starts.
    client = AsyncCosmosClient("https://account.example", credential, _backend="rust")
    assert client._adapter._token_credential is credential
    handles = []

    def acquire(endpoint, key, config, bridge):
        assert threading.current_thread() is not threading.main_thread()
        token = bridge._start_token_request("https://cosmos.azure.com/.default").result(5)
        assert token.token == "offline-token-2"
        handle = object()
        handles.append(handle)
        return handle

    async def read(handle, prepared, **kwargs):
        assert handle is handles[0]
        return 200, 0, {}, b'{"id":"item","pk":"A"}', None

    released = []
    monkeypatch.setattr(
        binding_adapter,
        "_rust_module",
        SimpleNamespace(
            acquire_driver_handle=acquire,
            read_item_async=read,
            release_driver_handle=released.append,
        ),
    )

    async def run():
        try:
            first = await credential.get_token("https://first.example/.default")
            assert first.token == "offline-token-1"
            session = transport.session
            async with client:
                item = (
                    await client.get_database_client("db")
                    .get_container_client("c")
                    .read_item(
                        "item",
                        partition_key="A",
                    )
                )
                assert item["id"] == "item"
                assert client._adapter._token_credential._loop is asyncio.get_running_loop()
                with pytest.raises(RuntimeError, match="original application loop"):
                    await asyncio.to_thread(lambda: asyncio.run(client._adapter.initialize()))
            assert released == handles
            assert not session.closed
            third = await credential.get_token("https://after-cosmos.example/.default")
            assert third.token == "offline-token-3"
            assert transport.loops == [asyncio.get_running_loop()] * 3
        finally:
            await client.close()
            await credential.close()

    asyncio.run(run())
