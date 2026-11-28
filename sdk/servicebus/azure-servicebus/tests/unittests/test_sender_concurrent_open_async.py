# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=protected-access

"""Regression tests for concurrent cold-start opens of the async sender (#35618).

Several coroutines sharing one `ServiceBusSender` can all reach `_open()` before any of
them has marked the sender running. Without serialization a second caller closes and
replaces the handler the first caller is still opening, which surfaced as
`AttributeError: 'NoneType' object has no attribute 'client_ready_async'`.

`_open()` now takes a per-sender lock. These tests pin three properties of it:

* concurrent opens build, open and keep exactly one handler;
* the wait for another caller's open is bounded by the waiting caller's own timeout,
  and that wait is charged to the same budget as the rest of link acquisition;
* a failed or timed-out open never leaves the lock held.

The handler is a scripted fake whose `open_async` blocks on an `asyncio.Event`, so the
interleaving is driven by the test rather than by real network or scheduler timing.
"""

import asyncio  # pylint:disable=do-not-import-asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import azure.servicebus._common.utils as utils_module
import azure.servicebus.aio._servicebus_sender_async as sender_module
from azure.servicebus.exceptions import OperationTimeoutError

# Bounds how long a broken implementation can stall a test before it fails.
_TEST_GUARD_SECONDS = 5


class _FakeHandler:
    """A send client whose open can be held open, or made to fail, by the test."""

    def __init__(self, open_gate=None, open_error=None):
        self._open_gate = open_gate
        self._open_error = open_error
        self.open_started = asyncio.Event()
        self.open_calls = 0
        self.close_calls = 0
        # Read by the transport once the link is ready, to size messages and batches.
        self._link = SimpleNamespace(remote_max_message_size=1024, remote_properties=None)

    async def open_async(self, connection=None):
        self.open_calls += 1
        self.open_started.set()
        if self._open_gate is not None:
            await self._open_gate.wait()
        if self._open_error is not None:
            raise self._open_error

    async def client_ready_async(self):
        return True

    async def close_async(self):
        self.close_calls += 1


class _Clock:
    """A monotonic clock that only moves when the test moves it."""

    def __init__(self):
        self.now = 1000.0

    def monotonic(self):
        return self.now

    time = monotonic


async def _no_auth(_client):
    return None


async def _let_other_tasks_run():
    # A few loop iterations are enough for a queued caller to reach the point where it
    # either blocks on the lock or, without one, closes and rebuilds the handler.
    for _ in range(5):
        await asyncio.sleep(0)


def _sender(*handlers):
    """A sender whose `_create_handler` hands out the given handlers in order."""
    from azure.servicebus.aio import ServiceBusClient

    client = ServiceBusClient("fake.servicebus.windows.net", MagicMock())
    sender = client.get_queue_sender("q")
    created = []
    remaining = list(handlers)

    def create_handler(auth):
        handler = remaining.pop(0)
        created.append(handler)
        sender._handler = handler

    sender._create_handler = create_handler
    return sender, created


class TestConcurrentColdOpen:
    @pytest.mark.asyncio
    async def test_concurrent_opens_build_and_keep_one_handler(self):
        gate = asyncio.Event()
        first = _FakeHandler(open_gate=gate)
        spare = _FakeHandler()
        sender, created = _sender(first, spare)

        with patch.object(sender_module, "create_authentication", _no_auth):
            opener = asyncio.ensure_future(sender._open())
            await first.open_started.wait()
            joiner = asyncio.ensure_future(sender._open())
            await _let_other_tasks_run()
            # Without the lock the joiner would already have closed `first` and built `spare`.
            assert created == [first]

            gate.set()
            await asyncio.wait_for(asyncio.gather(opener, joiner), _TEST_GUARD_SECONDS)

        assert created == [first]
        assert first.open_calls == 1
        assert first.close_calls == 0
        assert sender._handler is first
        assert sender._running
        assert not sender._open_lock.locked()

    @pytest.mark.asyncio
    async def test_a_failed_open_releases_the_lock_for_the_next_caller(self):
        failing = _FakeHandler(open_error=ValueError("open failed"))
        healthy = _FakeHandler()
        sender, created = _sender(failing, healthy)

        with patch.object(sender_module, "create_authentication", _no_auth):
            with pytest.raises(ValueError, match="open failed"):
                await sender._open()
            await asyncio.wait_for(sender._open(), _TEST_GUARD_SECONDS)

        assert created == [failing, healthy]
        assert sender._handler is healthy
        assert sender._running
        assert not sender._open_lock.locked()


class TestLockWaitIsBoundedByTheTimeout:
    @pytest.mark.asyncio
    async def test_waiting_for_a_stalled_open_times_out_within_the_budget(self):
        # The first caller has no timeout and its open never finishes on its own, so an
        # unbounded lock wait would block the second caller for as long as the first stalls.
        gate = asyncio.Event()
        first = _FakeHandler(open_gate=gate)
        sender, created = _sender(first)

        with patch.object(sender_module, "create_authentication", _no_auth):
            opener = asyncio.ensure_future(sender._open())
            await first.open_started.wait()
            try:
                with pytest.raises(OperationTimeoutError, match="concurrent open"):
                    await asyncio.wait_for(sender._open(timeout=0.05), _TEST_GUARD_SECONDS)
                # The caller that gave up never built a handler of its own.
                assert created == [first]
            finally:
                gate.set()
                await asyncio.wait_for(opener, _TEST_GUARD_SECONDS)

        assert sender._handler is first
        assert sender._running
        # Timing out while queued must not leave the lock held.
        assert not sender._open_lock.locked()

    @pytest.mark.asyncio
    async def test_time_spent_waiting_is_charged_to_the_same_budget(self):
        # One budget covers the whole link acquisition: a caller that waited past its
        # deadline for another caller's open must not start over with a fresh deadline.
        clock = _Clock()
        gate = asyncio.Event()
        first = _FakeHandler(open_gate=gate, open_error=ValueError("first open failed"))
        spare = _FakeHandler()
        sender, created = _sender(first, spare)

        with patch.object(utils_module, "time", clock):
            with patch.object(sender_module, "create_authentication", _no_auth):
                opener = asyncio.ensure_future(sender._open())
                await first.open_started.wait()
                waiter = asyncio.ensure_future(sender._open(timeout=10))
                await _let_other_tasks_run()

                # The first open outlasts the waiter's whole budget, then fails and frees the lock.
                clock.now += 11
                gate.set()
                with pytest.raises(ValueError, match="first open failed"):
                    await asyncio.wait_for(opener, _TEST_GUARD_SECONDS)
                with pytest.raises(OperationTimeoutError):
                    await asyncio.wait_for(waiter, _TEST_GUARD_SECONDS)

        assert created == [first], "the waiter opened a new link after its budget ran out"
        assert not sender._running
        assert not sender._open_lock.locked()
