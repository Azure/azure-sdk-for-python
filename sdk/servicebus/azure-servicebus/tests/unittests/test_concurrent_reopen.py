# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Concurrent operations on one handler share a single reopen after a retryable link failure.

When the service closes the connection, every in-flight operation on the receiver fails with a
retryable error and retries. Without serialization each retry opened its own handler, replacing
(and leaking) the others, and one caller's cleanup closed the handler another was opening.
"""
import asyncio  # pylint:disable=do-not-import-asyncio
import datetime
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.servicebus import AutoLockRenewer, ServiceBusClient, ServiceBusReceivedMessage
from azure.servicebus.aio import AutoLockRenewer as AsyncAutoLockRenewer, ServiceBusClient as AsyncServiceBusClient
from azure.servicebus.exceptions import MessageLockLostError, OperationTimeoutError, ServiceBusError
from azure.servicebus._pyamqp.error import AMQPConnectionError, ErrorCondition

CONCURRENCY = 20


def _connection_closed():
    return AMQPConnectionError(ErrorCondition.ConnectionCloseForced, description="connection closed by the service")


def _wait(event):
    if event is not None:
        assert event.wait(5)


async def _wait_async(event):
    if event is not None:
        await asyncio.wait_for(event.wait(), 5)


class _FakeHandler:  # pylint: disable=too-many-instance-attributes
    """Stands in for the AMQP client, for both the sync and the async receiver.

    A broken handler fails every request like a dropped connection, once `all_in_flight` (if given) is set by the
    CONCURRENCY-th request. A closed one fails requests like pyamqp's closed client. The open signals `opening` and
    blocks until `release_open`; the close likewise signals `closing` and blocks until `release_close`, then, with
    `interrupt_close`, raises (sync) or blocks until cancelled (async). Events are threading.Event for the sync
    receiver and asyncio.Event for the async one.
    """

    _link = None  # nothing to drain on close

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        broken=False,
        all_in_flight=None,
        opening=None,
        release_open=None,
        closing=None,
        release_close=None,
        interrupt_close=False,
    ):
        self.broken = broken
        self.all_in_flight = all_in_flight
        self.opening = opening
        self.release_open = release_open
        self.closing = closing
        self.release_close = release_close
        self.interrupt_close = interrupt_close
        self.in_flight = 0
        self.closed = 0
        self._shutdown = False
        self._lock = threading.Lock()

    @staticmethod
    def _signal(event):
        if event is not None:
            event.set()

    def open(self, connection=None):
        self._signal(self.opening)
        _wait(self.release_open)
        time.sleep(0.01)  # let concurrent callers run while the link opens, as a real open does

    async def open_async(self, connection=None):
        self._signal(self.opening)
        await _wait_async(self.release_open)
        await asyncio.sleep(0.01)  # let concurrent callers run while the link opens, as a real open does

    def client_ready(self):
        return True

    async def client_ready_async(self):
        return True

    def close(self):
        self.closed += 1
        self._shutdown = True
        self._signal(self.closing)
        _wait(self.release_close)
        if self.interrupt_close:
            raise RuntimeError("close interrupted")

    async def close_async(self):
        self.closed += 1
        self._shutdown = True
        self._signal(self.closing)
        await _wait_async(self.release_close)
        if self.interrupt_close:
            await asyncio.sleep(10)

    def _enter(self, started):
        with self._lock:
            self.in_flight += 1
            if self.in_flight >= CONCURRENCY:
                self._signal(self.all_in_flight)
        self._signal(started)
        return self.all_in_flight if self.broken else None

    def _result(self, failure):
        if failure is not None:
            raise failure()
        if self.broken:
            raise _connection_closed()
        if self._shutdown:  # what pyamqp raises once the client was closed under the request
            raise AttributeError("'NoneType' object has no attribute '_connection'")
        return "ok"

    def request(self, started=None, gate=None, failure=None):
        _wait(self._enter(started))
        _wait(gate)
        return self._result(failure)

    async def request_async(self, started=None, gate=None, failure=None):
        await _wait_async(self._enter(started))
        await _wait_async(gate)
        return self._result(failure)

    def mgmt_request(self, message, **kwargs):
        self._result(None)
        return 200, "OK", _LOCK_RENEWED

    async def mgmt_request_async(self, message, **kwargs):
        return self.mgmt_request(message, **kwargs)


# A management response renewing a lock until 2100-01-01.
_LOCK_RENEWED = SimpleNamespace(application_properties={}, value={b"expirations": [4102444800000]})


def _locked_message():
    message = MagicMock(spec=ServiceBusReceivedMessage)
    message._is_peeked_message = False
    message._settled = False
    message.lock_token = "00000000-0000-0000-0000-000000000001"
    return message


def _signal_when_opening(receiver, count, event):
    """Sets `event` once `count` calls have entered `receiver._open`."""
    calls = []
    original = receiver._open

    def _open(*args, **kwargs):
        calls.append(None)
        if len(calls) == count:
            event.set()
        return original(*args, **kwargs)

    receiver._open = _open


def _receiver_creating(client_type, make_handler, **kwargs):
    """A receiver whose n-th handler (from 0) is `make_handler(n)`; returns it and the list of created handlers."""
    client = client_type("fake.servicebus.windows.net", MagicMock(), retry_backoff_factor=0.05)
    receiver = client.get_queue_receiver("q", **kwargs)
    created = []

    def create_handler(auth):
        created.append(make_handler(len(created)))
        receiver._handler = created[-1]

    receiver._create_handler = create_handler
    return receiver, created


def _patch_sync_auth():
    return patch("azure.servicebus._servicebus_receiver.create_authentication", lambda c: None)


def _patch_async_auth():
    return patch("azure.servicebus.aio._servicebus_receiver_async.create_authentication", AsyncMock(return_value=None))


def _assert_reopened_once(receiver, created):
    assert len(created) == 2  # the initial handler and exactly one replacement
    assert created[0].closed == 1
    assert created[1].closed == 0
    assert receiver._handler is created[1] and receiver._running


def test_sync_concurrent_failures_share_one_reopen():
    all_in_flight = threading.Event()
    receiver, created = _receiver_creating(
        ServiceBusClient, lambda n: _FakeHandler(broken=n == 0, all_in_flight=all_in_flight)
    )

    def operation():
        receiver._open()
        return receiver._handler.request()

    with _patch_sync_auth():
        receiver._open()
        with ThreadPoolExecutor(CONCURRENCY) as pool:
            futures = [pool.submit(receiver._do_retryable_operation, operation) for _ in range(CONCURRENCY)]
            assert [f.result(timeout=30) for f in futures] == ["ok"] * CONCURRENCY

    _assert_reopened_once(receiver, created)


@pytest.mark.asyncio
async def test_async_concurrent_failures_share_one_reopen():
    all_in_flight = asyncio.Event()
    receiver, created = _receiver_creating(
        AsyncServiceBusClient, lambda n: _FakeHandler(broken=n == 0, all_in_flight=all_in_flight)
    )

    async def operation():
        await receiver._open()
        return await receiver._handler.request_async()

    with _patch_async_auth():
        await receiver._open()
        results = await asyncio.gather(*(receiver._do_retryable_operation(operation) for _ in range(CONCURRENCY)))

    assert results == ["ok"] * CONCURRENCY
    _assert_reopened_once(receiver, created)


def test_sync_stale_failure_from_before_the_first_open_does_not_close_the_reopened_handler():
    all_in_flight, release_slow = threading.Event(), threading.Event()
    receiver, created = _receiver_creating(
        ServiceBusClient, lambda n: _FakeHandler(broken=n == 0, all_in_flight=all_in_flight)
    )

    def operation(gate=None):
        receiver._open()
        return receiver._handler.request(gate=gate)

    with _patch_sync_auth():
        # Nothing has opened the receiver, so the first attempts start without a handler.
        with ThreadPoolExecutor(CONCURRENCY) as pool:
            slow = pool.submit(receiver._do_retryable_operation, operation, gate=release_slow)
            fast = [pool.submit(receiver._do_retryable_operation, operation) for _ in range(CONCURRENCY - 1)]
            assert [f.result(timeout=30) for f in fast] == ["ok"] * (CONCURRENCY - 1)
            assert len(created) == 2
            release_slow.set()  # the slow operation's failure on the first handler arrives after the reopen
            assert slow.result(timeout=30) == "ok"

    _assert_reopened_once(receiver, created)


@pytest.mark.asyncio
async def test_async_stale_failure_from_before_the_first_open_does_not_close_the_reopened_handler():
    all_in_flight, release_slow = asyncio.Event(), asyncio.Event()
    receiver, created = _receiver_creating(
        AsyncServiceBusClient, lambda n: _FakeHandler(broken=n == 0, all_in_flight=all_in_flight)
    )

    async def operation(gate=None):
        await receiver._open()
        return await receiver._handler.request_async(gate=gate)

    with _patch_async_auth():
        slow = asyncio.ensure_future(receiver._do_retryable_operation(operation, gate=release_slow))
        fast = await asyncio.gather(*(receiver._do_retryable_operation(operation) for _ in range(CONCURRENCY - 1)))
        assert fast == ["ok"] * (CONCURRENCY - 1)
        assert len(created) == 2
        release_slow.set()
        assert await asyncio.wait_for(slow, 30) == "ok"

    _assert_reopened_once(receiver, created)


# An attempt that starts with no handler running opens one, or finds one another operation opened, and fails on it:
# the failure closes that handler, so the retry reconnects.
@pytest.mark.parametrize("opened_elsewhere", [False, True])
def test_sync_failure_on_the_handler_an_attempt_opened_is_retried(opened_elsewhere):
    receiver, created = _receiver_creating(ServiceBusClient, lambda n: _FakeHandler(broken=n == 0))
    receiver._config.retry_total = 1

    def operation():
        if opened_elsewhere and not created:
            with ThreadPoolExecutor(1) as pool:
                pool.submit(receiver._open).result(timeout=5)
        receiver._open()
        return receiver._handler.request()

    with _patch_sync_auth():
        assert receiver._do_retryable_operation(operation) == "ok"

    _assert_reopened_once(receiver, created)


@pytest.mark.asyncio
@pytest.mark.parametrize("opened_elsewhere", [False, True])
async def test_async_failure_on_the_handler_an_attempt_opened_is_retried(opened_elsewhere):
    receiver, created = _receiver_creating(AsyncServiceBusClient, lambda n: _FakeHandler(broken=n == 0))
    receiver._config.retry_total = 1

    async def operation():
        if opened_elsewhere and not created:
            await asyncio.ensure_future(receiver._open())  # another task, so another operation's context
        await receiver._open()
        return await receiver._handler.request_async()

    with _patch_async_auth():
        assert await receiver._do_retryable_operation(operation) == "ok"

    _assert_reopened_once(receiver, created)


def test_sync_waiting_for_another_open_honors_the_timeout():
    opening, release = threading.Event(), threading.Event()
    receiver, _ = _receiver_creating(ServiceBusClient, lambda n: _FakeHandler(opening=opening, release_open=release))

    with _patch_sync_auth():
        holder = threading.Thread(target=receiver._open)
        holder.start()
        assert opening.wait(5)
        started = time.monotonic()
        with pytest.raises(OperationTimeoutError):
            receiver._open(timeout=0.3)
        assert time.monotonic() - started < 1
        release.set()
        holder.join(5)

    assert receiver._running


@pytest.mark.asyncio
async def test_async_waiting_for_another_open_honors_the_timeout():
    opening, release = asyncio.Event(), asyncio.Event()
    receiver, _ = _receiver_creating(
        AsyncServiceBusClient, lambda n: _FakeHandler(opening=opening, release_open=release)
    )

    with _patch_async_auth():
        holder = asyncio.ensure_future(receiver._open())
        await asyncio.wait_for(opening.wait(), 5)
        started = time.monotonic()
        with pytest.raises(OperationTimeoutError):
            await receiver._open(timeout=0.3)
        assert time.monotonic() - started < 1
        release.set()
        await asyncio.wait_for(holder, 5)

    assert receiver._running
    assert not receiver._handler_lock.locked()  # the timed-out wait left no acquisition behind


@pytest.mark.asyncio
async def test_async_cancelled_lock_acquire_does_not_release_the_openers_lock():
    opening, release = asyncio.Event(), asyncio.Event()
    receiver, created = _receiver_creating(
        AsyncServiceBusClient, lambda n: _FakeHandler(opening=opening, release_open=release)
    )

    with _patch_async_auth():
        opener = asyncio.ensure_future(receiver._open())
        await asyncio.wait_for(opening.wait(), 5)
        waiter = asyncio.ensure_future(receiver._open(timeout=5))
        for _ in range(10):  # let the waiter queue its acquire on the opener's lock
            await asyncio.sleep(0)
        acquires = [t for t in asyncio.all_tasks() if getattr(t.get_coro(), "__qualname__", "") == "Lock.acquire"]
        assert len(acquires) == 1
        acquires[0].cancel()  # e.g. shutdown code cancelling every task
        await asyncio.wait({waiter}, timeout=5)
        assert waiter.cancelled()
        assert receiver._handler_lock.locked()  # still the opener's
        release.set()
        await asyncio.wait_for(opener, 5)

    assert len(created) == 1 and receiver._running
    assert not receiver._handler_lock.locked()


def test_sync_open_failing_after_the_link_is_up_closes_it():
    renewer = AutoLockRenewer()
    renewer.close()  # registering the session now raises, after the link is up
    receiver, created = _receiver_creating(
        ServiceBusClient, lambda n: _FakeHandler(), session_id="s1", auto_lock_renewer=renewer
    )

    with _patch_sync_auth():
        with pytest.raises(ServiceBusError):
            receiver._open()

    assert created[0].closed == 1
    assert not receiver._running and receiver._handler is None


@pytest.mark.asyncio
async def test_async_open_failing_after_the_link_is_up_closes_it():
    renewer = AsyncAutoLockRenewer()
    await renewer.close()
    receiver, created = _receiver_creating(
        AsyncServiceBusClient, lambda n: _FakeHandler(), session_id="s1", auto_lock_renewer=renewer
    )

    with _patch_async_auth():
        with pytest.raises(ServiceBusError):
            await receiver._open()

    assert created[0].closed == 1
    assert not receiver._running and receiver._handler is None


# An operation is in flight on the handler when another operation's connection failure closes it, so the
# in-flight one then fails with whatever the closed client raises. A receiver retries that on the new handler; a
# session receiver cannot get its session back on a new link, so it still fails. A failure with a definite meaning,
# from the service or the caller, is raised as usual and never retried.
_CLOSED_UNDER_IN_FLIGHT_CASES = [
    pytest.param(None, None, None, id="retried"),
    pytest.param("s1", None, ServiceBusError, id="session"),
    pytest.param(None, lambda: MessageLockLostError(message="lock lost"), MessageLockLostError, id="lock-lost"),
    pytest.param(None, lambda: TypeError("bad argument"), ServiceBusError, id="caller-error"),
]


@pytest.mark.parametrize("session_id, failure, expected", _CLOSED_UNDER_IN_FLIGHT_CASES)
def test_sync_failure_on_a_handler_another_operation_closed(session_id, failure, expected):
    receiver, created = _receiver_creating(ServiceBusClient, lambda n: _FakeHandler(), session_id=session_id)
    started, gate = threading.Event(), threading.Event()
    calls, dropped = [], []

    def in_flight():
        receiver._open()
        calls.append(receiver._handler)
        return receiver._handler.request(started=started, gate=gate, failure=failure)

    def drop_once():
        receiver._open()
        if not dropped:
            dropped.append(True)
            raise _connection_closed()
        return "ok"

    with _patch_sync_auth():
        receiver._open()
        with ThreadPoolExecutor(1) as pool:
            pending = pool.submit(receiver._do_retryable_operation, in_flight)
            assert started.wait(5)
            if session_id is None:
                assert receiver._do_retryable_operation(drop_once) == "ok"  # closes the handler, then reopens
            else:
                with pytest.raises(ServiceBusError):
                    receiver._do_retryable_operation(drop_once)
            gate.set()
            if expected is None:
                assert pending.result(timeout=10) == "ok"
            else:
                assert type(pending.exception(timeout=10)) is expected  # pylint: disable=unidiomatic-typecheck

    assert created[0].closed == 1
    assert calls == ([created[0], created[1]] if expected is None else [created[0]])


@pytest.mark.asyncio
@pytest.mark.parametrize("session_id, failure, expected", _CLOSED_UNDER_IN_FLIGHT_CASES)
async def test_async_failure_on_a_handler_another_operation_closed(session_id, failure, expected):
    receiver, created = _receiver_creating(AsyncServiceBusClient, lambda n: _FakeHandler(), session_id=session_id)
    started, gate = asyncio.Event(), asyncio.Event()
    calls, dropped = [], []

    async def in_flight():
        await receiver._open()
        calls.append(receiver._handler)
        return await receiver._handler.request_async(started=started, gate=gate, failure=failure)

    async def drop_once():
        await receiver._open()
        if not dropped:
            dropped.append(True)
            raise _connection_closed()
        return "ok"

    with _patch_async_auth():
        await receiver._open()
        pending = asyncio.ensure_future(receiver._do_retryable_operation(in_flight))
        await asyncio.wait_for(started.wait(), 5)
        if session_id is None:
            assert await receiver._do_retryable_operation(drop_once) == "ok"
        else:
            with pytest.raises(ServiceBusError):
                await receiver._do_retryable_operation(drop_once)
        gate.set()
        await asyncio.wait({pending}, timeout=10)
        if expected is None:
            assert pending.result() == "ok"
        else:
            assert type(pending.exception()) is expected  # pylint: disable=unidiomatic-typecheck

    assert created[0].closed == 1
    assert calls == ([created[0], created[1]] if expected is None else [created[0]])


# A failure's close of the handler is interrupted (an error, or the caller cancelling the operation): later operations
# still reconnect instead of failing on the half-closed handler.
def test_sync_interrupted_close_lets_later_operations_reconnect():
    closing = threading.Event()
    receiver, created = _receiver_creating(
        ServiceBusClient, lambda n: _FakeHandler(broken=n == 0, closing=closing, interrupt_close=True)
    )

    def operation():
        receiver._open()
        return receiver._handler.request()

    with _patch_sync_auth():
        receiver._open()
        with pytest.raises(RuntimeError):
            receiver._do_retryable_operation(operation)
        assert closing.is_set()
        assert [receiver._do_retryable_operation(operation) for _ in range(3)] == ["ok"] * 3

    assert len(created) == 2
    assert receiver._handler is created[1] and receiver._running


@pytest.mark.asyncio
async def test_async_interrupted_close_lets_later_operations_reconnect():
    closing = asyncio.Event()
    receiver, created = _receiver_creating(
        AsyncServiceBusClient, lambda n: _FakeHandler(broken=n == 0, closing=closing, interrupt_close=True)
    )

    async def operation():
        await receiver._open()
        return await receiver._handler.request_async()

    with _patch_async_auth():
        await receiver._open()
        failing = asyncio.ensure_future(receiver._do_retryable_operation(operation))
        await asyncio.wait_for(closing.wait(), 5)
        failing.cancel()  # e.g. asyncio.wait_for around the operation timing out
        with pytest.raises(asyncio.CancelledError):
            await failing
        for _ in range(3):
            assert await asyncio.wait_for(receiver._do_retryable_operation(operation), 5) == "ok"

    assert len(created) == 2
    assert receiver._handler is created[1] and receiver._running


# While a failure's close of the handler is in progress, the receiver still counts as running (settlement, lock renewal
# and the AutoLockRenewer reject a receiver that is not), and operations starting meanwhile wait for the close and share
# one reopen.
def test_sync_operations_during_a_close_share_the_reopen():
    closing, release_close, both_opening = threading.Event(), threading.Event(), threading.Event()
    receiver, created = _receiver_creating(
        ServiceBusClient, lambda n: _FakeHandler(broken=n == 0, closing=closing, release_close=release_close)
    )

    def operation():
        receiver._open()
        return receiver._handler.request()

    with _patch_sync_auth():
        receiver._open()
        with ThreadPoolExecutor(3) as pool:
            failing = pool.submit(receiver._do_retryable_operation, operation)
            assert closing.wait(5)
            assert receiver._running and receiver._handler is None
            _signal_when_opening(receiver, 2, both_opening)
            renewing = pool.submit(receiver.renew_message_lock, _locked_message())
            other = pool.submit(receiver._do_retryable_operation, operation)
            assert both_opening.wait(5)
            release_close.set()
            assert failing.result(timeout=10) == "ok"
            assert other.result(timeout=10) == "ok"
            assert isinstance(renewing.result(timeout=10), datetime.datetime)

    _assert_reopened_once(receiver, created)


@pytest.mark.asyncio
async def test_async_operations_during_a_close_share_the_reopen():
    closing, release_close, both_opening = asyncio.Event(), asyncio.Event(), asyncio.Event()
    receiver, created = _receiver_creating(
        AsyncServiceBusClient, lambda n: _FakeHandler(broken=n == 0, closing=closing, release_close=release_close)
    )

    async def operation():
        await receiver._open()
        return await receiver._handler.request_async()

    with _patch_async_auth():
        await receiver._open()
        failing = asyncio.ensure_future(receiver._do_retryable_operation(operation))
        await asyncio.wait_for(closing.wait(), 5)
        assert receiver._running and receiver._handler is None
        _signal_when_opening(receiver, 2, both_opening)
        renewing = asyncio.ensure_future(receiver.renew_message_lock(_locked_message()))
        other = asyncio.ensure_future(receiver._do_retryable_operation(operation))
        await asyncio.wait_for(both_opening.wait(), 5)
        release_close.set()
        assert await asyncio.wait_for(failing, 10) == "ok"
        assert await asyncio.wait_for(other, 10) == "ok"
        assert isinstance(await asyncio.wait_for(renewing, 10), datetime.datetime)

    _assert_reopened_once(receiver, created)
