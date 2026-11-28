# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# pylint: disable=protected-access

"""
Unit tests for the async ``AutoLockRenewer`` pruning completed renewal futures
(regression guard for azure-sdk-for-python#48366).

Prior to the fix, ``AutoLockRenewer.register()`` appended each renewal
``asyncio.Future`` to a list ``self._futures`` and never removed it when the
renewal finished -- the list was only drained by ``close()``. A long-lived
renewer (the documented one-per-app pattern) therefore accumulated one entry per
message processed for the whole run: unbounded memory growth reclaimed only on
``close()``.

The fix makes ``_futures`` a ``set`` and registers
``renew_future.add_done_callback(self._futures.discard)`` so a future leaves the
set as soon as its renewal coroutine completes -- keeping the set bounded by the
number of *active* renewals rather than the all-time count of ``register()``
calls. ``close()`` is unchanged (``await asyncio.wait(self._futures)`` still
awaits the remaining active futures).

These tests exercise ``register`` / the done-callback / ``close`` directly with a
stub receiver and message, no network.
"""

import asyncio  # pylint: disable=do-not-import-asyncio
import datetime

import pytest
from unittest.mock import AsyncMock

from azure.servicebus._common.message import ServiceBusReceivedMessage
from azure.servicebus._common.utils import utc_now
from azure.servicebus.aio import AutoLockRenewer


class _StubReceiver:
    """Minimal stand-in for a ServiceBusReceiver that the renewer touches."""

    def __init__(self, renew_raises=False):
        self._running = True
        self.renew_message_lock = AsyncMock(
            side_effect=ValueError("boom") if renew_raises else None
        )


class _StubMessage(ServiceBusReceivedMessage):
    """A ServiceBusReceivedMessage that passes register() validation.

    ``locked_until_utc`` and ``_lock_expired`` are read-only properties on the
    base class; override them so the stub can drive the renewer without the heavy
    real ``__init__``.
    """

    locked_until_utc = property(lambda self: self._locked)  # type: ignore[assignment]
    _lock_expired = property(lambda self: self._expired)  # type: ignore[assignment]

    def __init__(self, receiver, *, settled=True, lock_seconds=60):
        now = utc_now()
        self._received_timestamp_utc = now
        self._locked = now + datetime.timedelta(seconds=lock_seconds)
        self._settled = settled
        self._expired = False
        self._receiver = receiver


async def _drain_callbacks():
    """Yield to the loop so deferred add_done_callback discards run."""
    for _ in range(10):
        await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_futures_is_a_set():
    """The collection is a set (identity-keyed, O(1) discard)."""
    renewer = AutoLockRenewer()
    assert isinstance(renewer._futures, set)
    await renewer.close()


@pytest.mark.asyncio
async def test_completed_renewals_are_pruned():
    """Core regression: settled registrations complete and leave the set empty.

    Fails against the pre-fix code, where every registered future stays in the
    list until close().
    """
    renewer = AutoLockRenewer()
    renewer._sleep_time = 0
    receiver = _StubReceiver()
    async with renewer:
        for _ in range(500):
            # already-settled -> the renewal coroutine returns immediately
            renewer.register(receiver, _StubMessage(receiver, settled=True))
        await _drain_callbacks()
        assert len(renewer._futures) == 0
    assert len(renewer._futures) == 0


@pytest.mark.asyncio
async def test_close_awaits_active_renewals():
    """An active (unsettled) renewal stays tracked and close() drains it."""
    renewer = AutoLockRenewer()
    renewer._sleep_time = 0
    receiver = _StubReceiver()
    async with renewer:
        renewer.register(receiver, _StubMessage(receiver, settled=False, lock_seconds=60))
        await _drain_callbacks()
        # unsettled -> the renewal loop keeps running, so the future is retained
        assert len(renewer._futures) == 1
        active = next(iter(renewer._futures))
        assert not active.done()
    # close() set _shutdown, the loop exited, and close awaited the future
    assert active.done()


@pytest.mark.asyncio
async def test_errored_renewal_is_pruned():
    """A renewal that raises still completes, so its future is pruned too."""
    renewer = AutoLockRenewer()
    renewer._sleep_time = 0
    receiver = _StubReceiver(renew_raises=True)
    async with renewer:
        # lock already due -> enters the renew branch -> receiver.renew_message_lock raises
        renewer.register(receiver, _StubMessage(receiver, settled=False, lock_seconds=0))
        await _drain_callbacks()
        assert len(renewer._futures) == 0
    receiver.renew_message_lock.assert_awaited()


@pytest.mark.asyncio
async def test_only_completed_futures_are_removed():
    """Asymmetry guard: settled registrations prune; an active one remains."""
    renewer = AutoLockRenewer()
    renewer._sleep_time = 0
    receiver = _StubReceiver()
    async with renewer:
        for _ in range(50):
            renewer.register(receiver, _StubMessage(receiver, settled=True))
        renewer.register(receiver, _StubMessage(receiver, settled=False, lock_seconds=60))
        await _drain_callbacks()
        # the 50 settled ones are pruned; only the active renewal remains
        assert len(renewer._futures) == 1
        assert not next(iter(renewer._futures)).done()
