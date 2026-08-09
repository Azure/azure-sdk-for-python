# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for the shared-bridge timeout first-wins warning.

A single async credential maps to one shared ``AsyncTokenCredentialBridge``
(one background loop, one set of timeouts). A later ``acquire`` of the same
credential with different ``token_timeout`` / ``join_timeout`` cannot retune the
already-running loop, so it keeps the first caller's values. These tests pin that
the divergence is *surfaced* (a WARNING is logged naming both values) rather than
silently swallowed, and that the first caller's values actually win.

Pure unit tests: the constructor starts no thread until the bridge is used, so no
event loop, network, emulator, or rust binding is required.
"""
from __future__ import annotations

import logging

import pytest

from azure.cosmos._backend import _async_credential_bridge as bridge_mod
from azure.cosmos._backend._async_credential_bridge import AsyncTokenCredentialBridge


class _FakeAsyncCredential:
    """Minimal async credential: only needs a coroutine ``get_token`` so the
    bridge selects a token method. Never actually called by these tests."""

    async def get_token(self, *scopes, **kwargs):  # pragma: no cover - never awaited
        raise AssertionError("token fetch must not happen in these unit tests")


@pytest.fixture
def clean_registry():
    """Drop any bridge these tests register so they don't leak across tests."""
    before = set(bridge_mod._REGISTRY)  # noqa: SLF001
    yield
    for key in list(bridge_mod._REGISTRY):  # noqa: SLF001
        if key not in before:
            bridge_mod._REGISTRY.pop(key, None)  # noqa: SLF001


def test_divergent_token_timeout_warns_and_first_wins(clean_registry, caplog):
    """Prove a later token timeout is ignored with a clear warning."""
    credential = _FakeAsyncCredential()

    first = AsyncTokenCredentialBridge.acquire(credential, token_timeout=1.0)
    assert first._token_timeout == 1.0  # noqa: SLF001

    with caplog.at_level(logging.WARNING, logger=bridge_mod.__name__):
        second = AsyncTokenCredentialBridge.acquire(credential, token_timeout=9.0)

    # Same shared bridge, first caller's value retained (first-wins).
    assert second is first
    assert second._token_timeout == 1.0  # noqa: SLF001

    # The divergence was surfaced, naming both the kept and the ignored value.
    warnings = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert any("token_timeout" in m and "1.0" in m and "9.0" in m for m in warnings), warnings


def test_divergent_join_timeout_warns_and_first_wins(clean_registry, caplog):
    """Prove a later shutdown timeout is ignored with a clear warning."""
    credential = _FakeAsyncCredential()

    first = AsyncTokenCredentialBridge.acquire(credential, join_timeout=2.0)
    assert first._join_timeout == 2.0  # noqa: SLF001

    with caplog.at_level(logging.WARNING, logger=bridge_mod.__name__):
        AsyncTokenCredentialBridge.acquire(credential, join_timeout=8.0)

    assert first._join_timeout == 2.0  # noqa: SLF001
    warnings = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert any("join_timeout" in m and "2.0" in m and "8.0" in m for m in warnings), warnings


def test_matching_timeouts_do_not_warn(clean_registry, caplog):
    """Prove repeated timeout settings do not produce a misleading warning."""
    credential = _FakeAsyncCredential()

    # First acquire with explicit values; the second repeats them, including the
    # env-resolved join default (join_timeout=None resolves to the same value the
    # constructor stored), so no divergence should be reported.
    AsyncTokenCredentialBridge.acquire(credential, token_timeout=3.0)
    with caplog.at_level(logging.WARNING, logger=bridge_mod.__name__):
        AsyncTokenCredentialBridge.acquire(credential, token_timeout=3.0, join_timeout=None)

    warnings = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert warnings == [], "identical timeouts must not warn: {}".format(warnings)
