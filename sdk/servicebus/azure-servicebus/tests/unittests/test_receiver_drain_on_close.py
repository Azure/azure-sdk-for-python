# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# pylint: disable=protected-access

"""
Unit tests for releasing buffered-but-unconsumed messages when a receive client
is closed (regression guard for azure-sdk-for-python#42917).

When ``receive_messages`` grants AMQP link credit, the broker may transfer more
messages than the application consumes before the call returns. Those surplus
messages sit in the client-side buffer ``_received_messages``. Prior to the fix,
``close``/``close_async`` cleared that buffer without settling it, leaving the
messages locked at the broker until lock expiry (delaying redelivery and
inflating the delivery count).

These tests assert the drain-on-close behavior directly against the pyamqp
``ReceiveClient`` / ``ReceiveClientAsync`` close paths, with no network:

* PEEK_LOCK (``ReceiverSettleMode.Second``): every buffered message is released
  (``released`` disposition) before the buffer is cleared.
* RECEIVE_AND_DELETE (``ReceiverSettleMode.First``): messages are already settled
  on transfer, so nothing is released (asymmetry — the SAME buffered input yields
  releases in one mode and none in the other).
* A failure while releasing must never block close.
"""

import queue

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from azure.servicebus._pyamqp.client import ReceiveClient, AMQPClient
from azure.servicebus._pyamqp.aio._client_async import ReceiveClientAsync, AMQPClientAsync
from azure.servicebus._pyamqp.constants import ReceiverSettleMode
from azure.servicebus._pyamqp.performatives import TransferFrame


def _buffer_with(*deliveries):
    """Build a _received_messages queue holding (TransferFrame, message) tuples.

    Mirrors what the receive callback puts on the buffer: the transfer frame
    (which carries delivery_id at index 1 and delivery_tag at index 2) paired
    with the decoded message.
    """
    buf = queue.Queue()
    for delivery_id, delivery_tag in deliveries:
        frame = TransferFrame(handle=0, delivery_id=delivery_id, delivery_tag=delivery_tag)
        buf.put((frame, MagicMock(name=f"message-{delivery_id}")))
    return buf


def _make_sync_client(settle_mode, buffer):
    """Create an uninitialized ReceiveClient with only the attributes close() touches."""
    client = ReceiveClient.__new__(ReceiveClient)
    client._received_messages = buffer
    client._receive_settle_mode = settle_mode
    client.settle_messages = MagicMock(name="settle_messages")
    return client


def _make_async_client(settle_mode, buffer):
    """Create an uninitialized ReceiveClientAsync with only the attributes close_async() touches."""
    client = ReceiveClientAsync.__new__(ReceiveClientAsync)
    client._received_messages = buffer
    client._receive_settle_mode = settle_mode
    client.settle_messages_async = AsyncMock(name="settle_messages_async")
    return client


class TestSyncReceiverDrainOnClose:
    def test_peek_lock_releases_all_buffered_messages(self):
        buffer = _buffer_with((10, b"tag-10"), (11, b"tag-11"), (12, b"tag-12"))
        client = _make_sync_client(ReceiverSettleMode.Second, buffer)

        with patch.object(AMQPClient, "close") as super_close:
            client.close()

        # Every buffered delivery is released with the 'released' disposition,
        # keyed by (delivery_id, delivery_tag) from the transfer frame.
        assert client.settle_messages.call_count == 3
        released = [
            (args[0], args[1], args[2]) for args, _ in client.settle_messages.call_args_list
        ]
        assert released == [
            (10, b"tag-10", "released"),
            (11, b"tag-11", "released"),
            (12, b"tag-12", "released"),
        ]
        # Buffer is drained and the parent close still runs.
        assert client._received_messages.empty()
        super_close.assert_called_once()

    def test_receive_and_delete_does_not_release(self):
        # SAME buffered input as the PEEK_LOCK case — asymmetry is driven only by mode.
        buffer = _buffer_with((10, b"tag-10"), (11, b"tag-11"), (12, b"tag-12"))
        client = _make_sync_client(ReceiverSettleMode.First, buffer)

        with patch.object(AMQPClient, "close") as super_close:
            client.close()

        client.settle_messages.assert_not_called()
        super_close.assert_called_once()

    def test_empty_buffer_releases_nothing(self):
        client = _make_sync_client(ReceiverSettleMode.Second, queue.Queue())

        with patch.object(AMQPClient, "close") as super_close:
            client.close()

        client.settle_messages.assert_not_called()
        super_close.assert_called_once()

    def test_release_failure_does_not_block_close(self):
        buffer = _buffer_with((10, b"tag-10"), (11, b"tag-11"))
        client = _make_sync_client(ReceiverSettleMode.Second, buffer)
        # Simulate a faulted / already-detached link raising on disposition.
        client.settle_messages.side_effect = ValueError("link detached")

        with patch.object(AMQPClient, "close") as super_close:
            client.close()  # must not raise

        # We stop releasing on the first failure but still tear down cleanly.
        assert client.settle_messages.call_count == 1
        assert client._received_messages.empty()
        super_close.assert_called_once()


class TestAsyncReceiverDrainOnClose:
    @pytest.mark.asyncio
    async def test_peek_lock_releases_all_buffered_messages(self):
        buffer = _buffer_with((20, b"tag-20"), (21, b"tag-21"))
        client = _make_async_client(ReceiverSettleMode.Second, buffer)

        with patch.object(AMQPClientAsync, "close_async", new=AsyncMock()) as super_close:
            await client.close_async()

        assert client.settle_messages_async.call_count == 2
        released = [
            (args[0], args[1], args[2]) for args, _ in client.settle_messages_async.call_args_list
        ]
        assert released == [
            (20, b"tag-20", "released"),
            (21, b"tag-21", "released"),
        ]
        assert client._received_messages.empty()
        super_close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_receive_and_delete_does_not_release(self):
        buffer = _buffer_with((20, b"tag-20"), (21, b"tag-21"))
        client = _make_async_client(ReceiverSettleMode.First, buffer)

        with patch.object(AMQPClientAsync, "close_async", new=AsyncMock()) as super_close:
            await client.close_async()

        client.settle_messages_async.assert_not_called()
        super_close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_release_failure_does_not_block_close(self):
        buffer = _buffer_with((20, b"tag-20"), (21, b"tag-21"))
        client = _make_async_client(ReceiverSettleMode.Second, buffer)
        client.settle_messages_async.side_effect = ValueError("link detached")

        with patch.object(AMQPClientAsync, "close_async", new=AsyncMock()) as super_close:
            await client.close_async()  # must not raise

        assert client.settle_messages_async.call_count == 1
        assert client._received_messages.empty()
        super_close.assert_awaited_once()
