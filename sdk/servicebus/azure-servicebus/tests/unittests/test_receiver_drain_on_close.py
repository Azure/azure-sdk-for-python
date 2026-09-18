# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# pylint: disable=protected-access,unused-argument

"""
Unit tests for draining and releasing buffered/in-flight messages when a Service
Bus receiver is closed (regression guard for azure-sdk-for-python#42917).

When ``receive_messages`` grants AMQP link credit, the broker may transfer more
messages than the application consumes before the call returns. Those messages
end up either in the client-side buffer ``_received_messages`` or still in flight
on the wire (leftover credit). Prior to the fix, closing the receiver cleared the
buffer without settling it and never drained the link, leaving those messages
locked at the broker until lock expiry (delaying redelivery and inflating the
delivery count).

The fix lives in the Service Bus transport layer (keeping the vendored ``_pyamqp``
package untouched):

  * ``PyamqpTransport.drain_and_release_messages`` (and the async
    twin) drains the link -- ``flow(link_credit=0, drain=True)`` + pumping the
    connection until quiescent, bounded by a timeout -- then releases every
    buffered message with the ``released`` disposition.
  * ``ServiceBusReceiver._close_handler`` calls it, gated to non-session
    PEEK_LOCK receivers. The non-session gate matches the .NET SDK (whose
    ``AmqpReceiver.CloseAsync`` drains when ``!isSessionReceiver && LinkCredit > 0``);
    the PEEK_LOCK gate is a Python-specific refinement -- a pre-settled
    RECEIVE_AND_DELETE delivery cannot be ``released``-settled.

These tests exercise the transport method directly and the receiver gating, with
no network.
"""

import queue
import time

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from azure.servicebus import ServiceBusReceiveMode
from azure.servicebus._servicebus_receiver import ServiceBusReceiver
from azure.servicebus._base_handler import BaseHandler
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus.aio._servicebus_receiver_async import ServiceBusReceiver as ServiceBusReceiverAsync
from azure.servicebus.aio._base_handler_async import BaseHandler as BaseHandlerAsync
from azure.servicebus.aio._transport._pyamqp_transport_async import PyamqpTransportAsync
from azure.servicebus._pyamqp.performatives import TransferFrame


def _buffer_with(*deliveries):
    buf = queue.Queue()
    for delivery_id, delivery_tag in deliveries:
        frame = TransferFrame(handle=0, delivery_id=delivery_id, delivery_tag=delivery_tag)
        buf.put((frame, MagicMock(name=f"message-{delivery_id}")))
    return buf


def _handler(*, is_closed=False, credit=5, buffer=None, connection=None, is_async=False):
    h = MagicMock(name="handler")
    h._link = MagicMock(name="link")
    h._link._is_closed = is_closed
    h._link.current_link_credit = credit
    h._link.flow = AsyncMock(name="flow") if is_async else MagicMock(name="flow")
    if connection is None:
        connection = MagicMock(name="connection")
        connection.listen = AsyncMock(name="listen") if is_async else MagicMock(name="listen")
    h._connection = connection
    h._received_messages = buffer if buffer is not None else queue.Queue()
    h._socket_timeout = 0.2
    if is_async:
        h.settle_messages_async = AsyncMock(name="settle_messages_async")
    else:
        h.settle_messages = MagicMock(name="settle_messages")
    return h


# --------------------------------------------------------------------------- #
# Transport method: drain + release                                           #
# --------------------------------------------------------------------------- #

class TestPyamqpTransportDrain:
    def test_drain_sent_and_buffer_released(self):
        h = _handler(credit=5, buffer=_buffer_with((10, b"tag-10"), (11, b"tag-11")))
        PyamqpTransport.drain_and_release_messages(h)

        h._link.flow.assert_called_once_with(link_credit=0, drain=True)
        assert h._connection.listen.call_count >= 1
        released = [(a[0], a[1], a[2]) for a, _ in h.settle_messages.call_args_list]
        assert released == [(10, b"tag-10", "released"), (11, b"tag-11", "released")]
        assert h._received_messages.empty()

    def test_pulls_inflight_then_releases(self):
        buffer = queue.Queue()
        connection = MagicMock(name="connection")
        calls = {"n": 0}

        def _listen(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                frame = TransferFrame(handle=0, delivery_id=99, delivery_tag=b"tag-99")
                buffer.put((frame, MagicMock()))

        connection.listen = MagicMock(side_effect=_listen)
        h = _handler(credit=3, buffer=buffer, connection=connection)

        PyamqpTransport.drain_and_release_messages(h)

        h._link.flow.assert_called_once_with(link_credit=0, drain=True)
        h.settle_messages.assert_called_once_with(99, b"tag-99", "released")

    def test_no_credit_skips_drain_but_releases_buffer(self):
        # A prefetch receiver can hit zero credit with deliveries still buffered:
        # skip the drain flow, but the buffered messages must still be released.
        h = _handler(credit=0, buffer=_buffer_with((10, b"tag-10")))
        PyamqpTransport.drain_and_release_messages(h)
        h._link.flow.assert_not_called()
        h.settle_messages.assert_called_once_with(10, b"tag-10", "released")
        assert h._received_messages.empty()

    def test_no_credit_empty_buffer_is_noop(self):
        h = _handler(credit=0)
        PyamqpTransport.drain_and_release_messages(h)
        h._link.flow.assert_not_called()
        h.settle_messages.assert_not_called()

    def test_skipped_when_link_closed(self):
        h = _handler(credit=5, is_closed=True, buffer=_buffer_with((10, b"tag-10")))
        PyamqpTransport.drain_and_release_messages(h)
        h._link.flow.assert_not_called()
        h.settle_messages.assert_not_called()  # cannot settle through a closed link

    def test_skipped_when_link_none(self):
        h = _handler(credit=5)
        h._link = None
        PyamqpTransport.drain_and_release_messages(h)  # must not raise
        h.settle_messages.assert_not_called()

    def test_drain_failure_still_releases_buffer(self):
        # Drain failure must not skip the release (separate try blocks).
        h = _handler(credit=5, buffer=_buffer_with((10, b"tag-10")))
        h._link.flow.side_effect = ValueError("link faulted")
        PyamqpTransport.drain_and_release_messages(h)  # must not raise
        h.settle_messages.assert_called_once_with(10, b"tag-10", "released")
        assert h._received_messages.empty()

    def test_bounded_by_deadline_even_with_blocking_listen(self):
        # A large socket_timeout must not let a single blocking read overrun the cap:
        # each listen() should wait at most the remaining drain budget.
        buffer = queue.Queue()
        connection = MagicMock(name="connection")

        def _listen(*args, **kwargs):
            time.sleep(kwargs.get("wait", 0))  # block for the requested wait
            frame = TransferFrame(handle=0, delivery_id=1, delivery_tag=b"t")
            buffer.put((frame, MagicMock()))  # never quiescent

        connection.listen = MagicMock(side_effect=_listen)
        h = _handler(credit=3, buffer=buffer, connection=connection)
        h._socket_timeout = 5  # much larger than the drain cap

        start = time.time()
        with patch("azure.servicebus._transport._pyamqp_transport.RECEIVE_LINK_DRAIN_TIMEOUT", 0.1):
            PyamqpTransport.drain_and_release_messages(h)
        elapsed = time.time() - start

        assert h._connection.listen.call_count >= 1
        assert elapsed < 2.0  # bounded by the cap, not the 5s socket timeout


class TestPyamqpTransportDrainAsync:
    @pytest.mark.asyncio
    async def test_drain_sent_and_buffer_released(self):
        h = _handler(credit=5, buffer=_buffer_with((20, b"tag-20"), (21, b"tag-21")), is_async=True)
        await PyamqpTransportAsync.drain_and_release_messages_async(h)

        h._link.flow.assert_awaited_once_with(link_credit=0, drain=True)
        assert h._connection.listen.await_count >= 1
        released = [(a[0], a[1], a[2]) for a, _ in h.settle_messages_async.call_args_list]
        assert released == [(20, b"tag-20", "released"), (21, b"tag-21", "released")]
        assert h._received_messages.empty()

    @pytest.mark.asyncio
    async def test_pulls_inflight_then_releases(self):
        buffer = queue.Queue()
        connection = MagicMock(name="connection")
        calls = {"n": 0}

        async def _listen(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                frame = TransferFrame(handle=0, delivery_id=88, delivery_tag=b"tag-88")
                buffer.put((frame, MagicMock()))

        connection.listen = AsyncMock(side_effect=_listen)
        h = _handler(credit=3, buffer=buffer, connection=connection, is_async=True)

        await PyamqpTransportAsync.drain_and_release_messages_async(h)

        h._link.flow.assert_awaited_once_with(link_credit=0, drain=True)
        h.settle_messages_async.assert_awaited_once_with(88, b"tag-88", "released")

    @pytest.mark.asyncio
    async def test_no_credit_skips_drain_but_releases_buffer(self):
        h = _handler(credit=0, buffer=_buffer_with((20, b"tag-20")), is_async=True)
        await PyamqpTransportAsync.drain_and_release_messages_async(h)
        h._link.flow.assert_not_called()
        h.settle_messages_async.assert_awaited_once_with(20, b"tag-20", "released")
        assert h._received_messages.empty()

    @pytest.mark.asyncio
    async def test_drain_failure_still_releases_buffer(self):
        h = _handler(credit=5, buffer=_buffer_with((20, b"tag-20")), is_async=True)
        h._link.flow.side_effect = ValueError("link faulted")
        await PyamqpTransportAsync.drain_and_release_messages_async(h)  # must not raise
        h.settle_messages_async.assert_awaited_once_with(20, b"tag-20", "released")
        assert h._received_messages.empty()

    @pytest.mark.asyncio
    async def test_bounded_by_deadline_even_with_blocking_listen(self):
        import asyncio  # pylint: disable=do-not-import-asyncio

        buffer = queue.Queue()
        connection = MagicMock(name="connection")

        async def _listen(*args, **kwargs):
            await asyncio.sleep(kwargs.get("wait", 0))  # block for the requested wait
            frame = TransferFrame(handle=0, delivery_id=1, delivery_tag=b"t")
            buffer.put((frame, MagicMock()))  # never quiescent

        connection.listen = AsyncMock(side_effect=_listen)
        h = _handler(credit=3, buffer=buffer, connection=connection, is_async=True)
        h._socket_timeout = 5  # much larger than the drain cap

        start = time.time()
        with patch("azure.servicebus.aio._transport._pyamqp_transport_async.RECEIVE_LINK_DRAIN_TIMEOUT", 0.1):
            await PyamqpTransportAsync.drain_and_release_messages_async(h)
        elapsed = time.time() - start

        assert h._connection.listen.await_count >= 1
        assert elapsed < 2.0  # bounded by the cap, not the 5s socket timeout

    @pytest.mark.asyncio
    async def test_no_credit_empty_buffer_is_noop(self):
        h = _handler(credit=0, is_async=True)
        await PyamqpTransportAsync.drain_and_release_messages_async(h)
        h._link.flow.assert_not_called()
        h.settle_messages_async.assert_not_called()

    @pytest.mark.asyncio
    async def test_skipped_when_link_closed(self):
        h = _handler(credit=5, is_closed=True, buffer=_buffer_with((20, b"tag-20")), is_async=True)
        await PyamqpTransportAsync.drain_and_release_messages_async(h)
        h._link.flow.assert_not_called()
        h.settle_messages_async.assert_not_called()  # cannot settle through a closed link

    @pytest.mark.asyncio
    async def test_skipped_when_link_none(self):
        h = _handler(credit=5, is_async=True)
        h._link = None
        await PyamqpTransportAsync.drain_and_release_messages_async(h)  # must not raise
        h.settle_messages_async.assert_not_called()


# --------------------------------------------------------------------------- #
# Receiver gating: only non-session PEEK_LOCK receivers drain on close         #
# --------------------------------------------------------------------------- #

def _sync_receiver(mode, session):
    r = ServiceBusReceiver.__new__(ServiceBusReceiver)
    r._handler = MagicMock(name="handler")
    r._message_iter = None
    r._receive_mode = mode
    r._session = session
    r._amqp_transport = MagicMock(name="transport")
    r._amqp_transport.drain_and_release_messages = MagicMock(name="drain")
    return r


def _async_receiver(mode, session):
    r = ServiceBusReceiverAsync.__new__(ServiceBusReceiverAsync)
    r._handler = MagicMock(name="handler")
    r._message_iter = None
    r._receive_mode = mode
    r._session = session
    r._amqp_transport = MagicMock(name="transport")
    r._amqp_transport.drain_and_release_messages_async = AsyncMock(name="drain")
    return r


class TestReceiverCloseGating:
    def test_peek_lock_non_session_drains(self):
        r = _sync_receiver(ServiceBusReceiveMode.PEEK_LOCK, session=None)
        with patch.object(BaseHandler, "_close_handler"):
            r._close_handler()
        r._amqp_transport.drain_and_release_messages.assert_called_once_with(r._handler)

    def test_receive_and_delete_does_not_drain(self):
        r = _sync_receiver(ServiceBusReceiveMode.RECEIVE_AND_DELETE, session=None)
        with patch.object(BaseHandler, "_close_handler"):
            r._close_handler()
        r._amqp_transport.drain_and_release_messages.assert_not_called()

    def test_session_receiver_does_not_drain(self):
        r = _sync_receiver(ServiceBusReceiveMode.PEEK_LOCK, session=MagicMock(name="session"))
        with patch.object(BaseHandler, "_close_handler"):
            r._close_handler()
        r._amqp_transport.drain_and_release_messages.assert_not_called()

    @pytest.mark.asyncio
    async def test_peek_lock_non_session_drains_async(self):
        r = _async_receiver(ServiceBusReceiveMode.PEEK_LOCK, session=None)
        with patch.object(BaseHandlerAsync, "_close_handler", new=AsyncMock()):
            await r._close_handler()
        r._amqp_transport.drain_and_release_messages_async.assert_awaited_once_with(r._handler)

    @pytest.mark.asyncio
    async def test_receive_and_delete_does_not_drain_async(self):
        r = _async_receiver(ServiceBusReceiveMode.RECEIVE_AND_DELETE, session=None)
        with patch.object(BaseHandlerAsync, "_close_handler", new=AsyncMock()):
            await r._close_handler()
        r._amqp_transport.drain_and_release_messages_async.assert_not_called()

    @pytest.mark.asyncio
    async def test_session_receiver_does_not_drain_async(self):
        r = _async_receiver(ServiceBusReceiveMode.PEEK_LOCK, session=MagicMock(name="session"))
        with patch.object(BaseHandlerAsync, "_close_handler", new=AsyncMock()):
            await r._close_handler()
        r._amqp_transport.drain_and_release_messages_async.assert_not_called()
