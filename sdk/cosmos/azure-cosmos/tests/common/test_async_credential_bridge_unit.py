# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Credential scheduling, policy conflicts, cancellation and shutdown."""
import asyncio
import threading

import pytest

from azure.cosmos._backend._async_credential_bridge import AsyncTokenCredentialBridge


@pytest.mark.parametrize("setting", ["token_timeout", "join_timeout"])
@pytest.mark.parametrize("value", [float("inf"), float("nan"), -1, True, "1"])
def test_bridge_rejects_invalid_timeouts(setting, value):
    with pytest.raises(ValueError, match=setting):
        AsyncTokenCredentialBridge(object(), **{setting: value})


@pytest.mark.parametrize("setting", ["token_timeout", "join_timeout"])
def test_shared_bridge_rejects_policy_conflict_without_adding_hold(setting):
    credential = object()
    first = AsyncTokenCredentialBridge.acquire(credential, **{setting: 1.0})
    try:
        with pytest.raises(ValueError, match="same bridge timeouts"):
            AsyncTokenCredentialBridge.acquire(credential, **{setting: 2.0})
        assert first._refcount == 1
    finally:
        first._close_cosmos_async_bridge()


def test_credential_timeout_error_is_not_swallowed_by_sliced_wait():
    class Credential:
        async def get_token(self, *scopes):
            raise TimeoutError("credential's own timeout")

    bridge = AsyncTokenCredentialBridge(Credential(), token_timeout=1.0)
    try:
        with pytest.raises(TimeoutError, match="credential's own timeout"):
            bridge.get_token("scope")
    finally:
        bridge._close_cosmos_async_bridge()


def test_native_result_cancellation_reaches_credential_coroutine():
    started = threading.Event()
    cancelled = threading.Event()

    class Credential:
        async def get_token(self, *scopes):
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

    bridge = AsyncTokenCredentialBridge(Credential())
    try:
        future = bridge._start_token_request("scope")
        assert started.wait(2)
        future.cancel()
        assert cancelled.wait(2)
        assert not bridge._pending
    finally:
        bridge._close_cosmos_async_bridge()
    assert bridge._thread is not None and not bridge._thread.is_alive()


def test_incomplete_shutdown_is_reported_and_cannot_start_second_loop(caplog):
    started = threading.Event()
    release = threading.Event()

    class Credential:
        async def get_token(self, *scopes):
            started.set()
            # Intentionally uncooperative customer code; always released in finally.
            release.wait(3)

    credential = Credential()
    bridge = AsyncTokenCredentialBridge.acquire(credential, join_timeout=0.01)
    try:
        bridge._start_token_request("scope")
        assert started.wait(2)
        bridge._close_cosmos_async_bridge()
        assert bridge._thread.is_alive()
        assert "did not stop" in caplog.text
        bridge._close_cosmos_async_bridge()
        assert caplog.text.count("did not stop") == 1
        with pytest.raises(RuntimeError, match="still shutting down"):
            AsyncTokenCredentialBridge.acquire(credential, join_timeout=0.01)
    finally:
        release.set()
        bridge._thread.join(3)
    assert not bridge._thread.is_alive()
    replacement = AsyncTokenCredentialBridge.acquire(credential)
    replacement._close_cosmos_async_bridge()


def test_closed_bridge_rejects_scheduling_without_creating_coroutine():
    class Credential:
        async def get_token(self, *scopes):
            raise AssertionError("closed bridge must not execute credential")

    bridge = AsyncTokenCredentialBridge(Credential())
    bridge._close_cosmos_async_bridge()
    with pytest.raises(RuntimeError, match="closed"):
        bridge._start_token_request("scope")
