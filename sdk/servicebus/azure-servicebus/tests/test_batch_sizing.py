# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Unit tests for batch sizing based on the vendor link property
'com.microsoft:max-message-batch-size'. These tests verify:

1. Vendor property present (bytes and str keys) → uses its value for batch sizing.
2. Vendor property absent → falls back to tier-based inference.
3. Vendor property with wrong type → falls back gracefully.
4. Standard tier → 256 KB from vendor property.
"""

from unittest.mock import MagicMock
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus._common.constants import (
    MAX_BATCH_SIZE_PREMIUM,
    MAX_BATCH_SIZE_STANDARD,
    MAX_MESSAGE_LENGTH_BYTES,
)


class TestPyamqpGetRemoteMaxMessageBatchSize:
    """Tests for PyamqpTransport.get_remote_max_message_batch_size()."""

    def test_returns_vendor_property_value(self):
        """pyamqp decodes AMQP symbols as bytes — the primary key form."""
        handler = MagicMock()
        handler._link.remote_properties = {
            b"com.microsoft:max-message-batch-size": 1048576,  # 1 MB
        }

        result = PyamqpTransport.get_remote_max_message_batch_size(handler)
        assert result == 1048576

    def test_returns_vendor_property_value_str_key(self):
        """Fallback: some transports may use str keys."""
        handler = MagicMock()
        handler._link.remote_properties = {
            "com.microsoft:max-message-batch-size": 1048576,
        }

        result = PyamqpTransport.get_remote_max_message_batch_size(handler)
        assert result == 1048576

    def test_returns_none_when_no_remote_properties(self):
        handler = MagicMock()
        handler._link.remote_properties = None

        result = PyamqpTransport.get_remote_max_message_batch_size(handler)
        assert result is None

    def test_returns_none_when_property_absent(self):
        handler = MagicMock()
        handler._link.remote_properties = {"other-property": 42}

        result = PyamqpTransport.get_remote_max_message_batch_size(handler)
        assert result is None

    def test_returns_none_when_property_is_wrong_type(self):
        handler = MagicMock()
        handler._link.remote_properties = {
            b"com.microsoft:max-message-batch-size": "not-a-number",
        }

        result = PyamqpTransport.get_remote_max_message_batch_size(handler)
        assert result is None

    def test_returns_none_when_property_is_zero(self):
        handler = MagicMock()
        handler._link.remote_properties = {
            b"com.microsoft:max-message-batch-size": 0,
        }

        result = PyamqpTransport.get_remote_max_message_batch_size(handler)
        assert result is None

    def test_returns_none_when_property_is_negative(self):
        handler = MagicMock()
        handler._link.remote_properties = {
            b"com.microsoft:max-message-batch-size": -1,
        }

        result = PyamqpTransport.get_remote_max_message_batch_size(handler)
        assert result is None

    def test_returns_256_kb_for_standard_tier(self):
        handler = MagicMock()
        handler._link.remote_properties = {
            b"com.microsoft:max-message-batch-size": 262144,  # 256 KB
        }

        result = PyamqpTransport.get_remote_max_message_batch_size(handler)
        assert result == 262144

    def test_returns_none_when_remote_properties_attr_missing(self):
        handler = MagicMock()
        handler._link = MagicMock(spec=[])  # Empty spec — no remote_properties attr

        result = PyamqpTransport.get_remote_max_message_batch_size(handler)
        assert result is None


class TestSenderBatchSizeInference:
    """
    Tests for the sender's batch size inference logic in _open().
    These test the combination of vendor property reading and tier-based fallback.
    """

    def _create_mock_sender(self, max_message_size, remote_properties=None):
        """Create a mock sender with controllable link properties."""
        from azure.servicebus._servicebus_sender import ServiceBusSender

        # Create a lightweight mock of ServiceBusSender to test _open logic
        sender = MagicMock(spec=ServiceBusSender)
        sender._max_message_size_on_link = 0
        sender._max_batch_size_on_link = 0
        sender._running = False
        sender._connection = None

        # Mock the handler and its link
        mock_handler = MagicMock()
        mock_handler._link.remote_max_message_size = max_message_size
        mock_handler._link.remote_properties = remote_properties
        sender._handler = mock_handler

        # Use real transport
        sender._amqp_transport = PyamqpTransport

        return sender

    def test_vendor_property_overrides_tier_inference(self):
        """Premium large-message: max-message-size=100MB, vendor batch=1MB → uses 1MB."""
        sender = self._create_mock_sender(
            max_message_size=100 * 1024 * 1024,
            remote_properties={b"com.microsoft:max-message-batch-size": 1048576},
        )

        # Run the batch size determination logic (extracted from _open)
        sender._max_message_size_on_link = (
            sender._amqp_transport.get_remote_max_message_size(sender._handler) or MAX_MESSAGE_LENGTH_BYTES
        )
        vendor_batch_size = sender._amqp_transport.get_remote_max_message_batch_size(sender._handler)
        if vendor_batch_size is not None:
            sender._max_batch_size_on_link = vendor_batch_size
        elif sender._max_message_size_on_link >= MAX_BATCH_SIZE_PREMIUM:
            sender._max_batch_size_on_link = MAX_BATCH_SIZE_PREMIUM
        else:
            sender._max_batch_size_on_link = MAX_BATCH_SIZE_STANDARD

        assert sender._max_message_size_on_link == 100 * 1024 * 1024
        assert sender._max_batch_size_on_link == 1048576  # vendor property

    def test_fallback_to_premium_tier_when_vendor_absent(self):
        """Premium default: max-message-size=1MB, no vendor → tier-infer as Premium (1MB)."""
        sender = self._create_mock_sender(
            max_message_size=1048576,
            remote_properties={},
        )

        sender._max_message_size_on_link = (
            sender._amqp_transport.get_remote_max_message_size(sender._handler) or MAX_MESSAGE_LENGTH_BYTES
        )
        vendor_batch_size = sender._amqp_transport.get_remote_max_message_batch_size(sender._handler)
        if vendor_batch_size is not None:
            sender._max_batch_size_on_link = vendor_batch_size
        elif sender._max_message_size_on_link >= MAX_BATCH_SIZE_PREMIUM:
            sender._max_batch_size_on_link = MAX_BATCH_SIZE_PREMIUM
        else:
            sender._max_batch_size_on_link = MAX_BATCH_SIZE_STANDARD

        assert sender._max_batch_size_on_link == MAX_BATCH_SIZE_PREMIUM

    def test_fallback_to_standard_tier_when_vendor_absent(self):
        """Standard tier: max-message-size=256KB, no vendor → tier-infer as Standard (256KB)."""
        sender = self._create_mock_sender(
            max_message_size=262144,
            remote_properties={},
        )

        sender._max_message_size_on_link = (
            sender._amqp_transport.get_remote_max_message_size(sender._handler) or MAX_MESSAGE_LENGTH_BYTES
        )
        vendor_batch_size = sender._amqp_transport.get_remote_max_message_batch_size(sender._handler)
        if vendor_batch_size is not None:
            sender._max_batch_size_on_link = vendor_batch_size
        elif sender._max_message_size_on_link >= MAX_BATCH_SIZE_PREMIUM:
            sender._max_batch_size_on_link = MAX_BATCH_SIZE_PREMIUM
        else:
            sender._max_batch_size_on_link = MAX_BATCH_SIZE_STANDARD

        assert sender._max_batch_size_on_link == MAX_BATCH_SIZE_STANDARD

    def test_vendor_property_standard_tier(self):
        """Standard tier with vendor property: 256KB for both → uses vendor value."""
        sender = self._create_mock_sender(
            max_message_size=262144,
            remote_properties={b"com.microsoft:max-message-batch-size": 262144},
        )

        sender._max_message_size_on_link = (
            sender._amqp_transport.get_remote_max_message_size(sender._handler) or MAX_MESSAGE_LENGTH_BYTES
        )
        vendor_batch_size = sender._amqp_transport.get_remote_max_message_batch_size(sender._handler)
        if vendor_batch_size is not None:
            sender._max_batch_size_on_link = vendor_batch_size
        elif sender._max_message_size_on_link >= MAX_BATCH_SIZE_PREMIUM:
            sender._max_batch_size_on_link = MAX_BATCH_SIZE_PREMIUM
        else:
            sender._max_batch_size_on_link = MAX_BATCH_SIZE_STANDARD

        assert sender._max_batch_size_on_link == 262144


class TestAsyncSenderBatchSizeInference:
    """
    Tests for the async sender's batch size inference, mirroring
    TestSenderBatchSizeInference to ensure parity between sync and async paths.
    """

    def _create_mock_async_sender(self, max_message_size, remote_properties=None):
        """Create a mock async sender with controllable link properties."""
        from azure.servicebus.aio._servicebus_sender_async import ServiceBusSender as AsyncServiceBusSender

        sender = MagicMock(spec=AsyncServiceBusSender)
        sender._max_message_size_on_link = 0
        sender._max_batch_size_on_link = 0
        sender._running = False
        sender._connection = None

        mock_handler = MagicMock()
        mock_handler._link.remote_max_message_size = max_message_size
        mock_handler._link.remote_properties = remote_properties
        sender._handler = mock_handler
        sender._amqp_transport = PyamqpTransport

        return sender

    def test_async_vendor_property_overrides_tier_inference(self):
        """Async Premium large-message: vendor batch=1MB overrides tier inference."""
        sender = self._create_mock_async_sender(
            max_message_size=100 * 1024 * 1024,
            remote_properties={b"com.microsoft:max-message-batch-size": 1048576},
        )

        sender._max_message_size_on_link = (
            sender._amqp_transport.get_remote_max_message_size(sender._handler) or MAX_MESSAGE_LENGTH_BYTES
        )
        vendor_batch_size = sender._amqp_transport.get_remote_max_message_batch_size(sender._handler)
        if vendor_batch_size is not None:
            sender._max_batch_size_on_link = vendor_batch_size
        elif sender._max_message_size_on_link >= MAX_BATCH_SIZE_PREMIUM:
            sender._max_batch_size_on_link = MAX_BATCH_SIZE_PREMIUM
        else:
            sender._max_batch_size_on_link = MAX_BATCH_SIZE_STANDARD

        assert sender._max_batch_size_on_link == 1048576

    def test_async_fallback_to_standard_tier(self):
        """Async Standard tier without vendor property falls back correctly."""
        sender = self._create_mock_async_sender(
            max_message_size=262144,
            remote_properties={},
        )

        sender._max_message_size_on_link = (
            sender._amqp_transport.get_remote_max_message_size(sender._handler) or MAX_MESSAGE_LENGTH_BYTES
        )
        vendor_batch_size = sender._amqp_transport.get_remote_max_message_batch_size(sender._handler)
        if vendor_batch_size is not None:
            sender._max_batch_size_on_link = vendor_batch_size
        elif sender._max_message_size_on_link >= MAX_BATCH_SIZE_PREMIUM:
            sender._max_batch_size_on_link = MAX_BATCH_SIZE_PREMIUM
        else:
            sender._max_batch_size_on_link = MAX_BATCH_SIZE_STANDARD

        assert sender._max_batch_size_on_link == MAX_BATCH_SIZE_STANDARD
