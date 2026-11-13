# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""A credential and owner loop may share only one token-timeout policy."""

from contextlib import ExitStack

import pytest

from azure.cosmos._backend import _async_credential_bridge as bridge_mod
from azure.cosmos._backend._async_credential_bridge import AsyncTokenCredentialBridge


class _FakeAsyncCredential:
    async def get_token(self, *scopes, **kwargs):
        raise AssertionError("these tests must not fetch tokens")


@pytest.mark.parametrize("initial,conflicting", [(1.0, 9.0), (None, 9.0)])
def test_divergent_timeout_rejects_acquisition_without_changing_policy_rust(
    credential_owner_loop,
    initial,
    conflicting,
):
    credential = _FakeAsyncCredential()
    key = (id(credential), credential_owner_loop)
    with ExitStack() as cleanup:
        first = AsyncTokenCredentialBridge.acquire(credential, initial, loop=credential_owner_loop)
        cleanup.callback(first._close_cosmos_async_bridge)
        with pytest.raises(ValueError, match="same bridge timeouts"):
            second = AsyncTokenCredentialBridge.acquire(credential, conflicting, loop=credential_owner_loop)
            cleanup.callback(second._close_cosmos_async_bridge)
        assert first._token_timeout == initial
        assert first._refcount == 1
        assert bridge_mod._REGISTRY[key] is first
        assert not first._closed
    assert key not in bridge_mod._REGISTRY
    assert credential_owner_loop.is_running()


def test_matching_timeouts_share_one_hold_per_acquisition_rust(credential_owner_loop):
    credential = _FakeAsyncCredential()
    key = (id(credential), credential_owner_loop)
    with ExitStack() as cleanup:
        first = AsyncTokenCredentialBridge.acquire(credential, 3, loop=credential_owner_loop)
        cleanup.callback(first._close_cosmos_async_bridge)
        with ExitStack() as second_use:
            second = AsyncTokenCredentialBridge.acquire(credential, 3.0, loop=credential_owner_loop)
            second_use.callback(second._close_cosmos_async_bridge)
            assert second is first
            assert first._refcount == 2
        assert first._refcount == 1
        assert not first._closed
    assert key not in bridge_mod._REGISTRY
    assert credential_owner_loop.is_running()
