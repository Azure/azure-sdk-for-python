# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.servicebus import DeleteMessagesResult, ServiceBusReceiver
from azure.servicebus.aio import ServiceBusReceiver as AsyncServiceBusReceiver
from azure.servicebus._common.constants import (
    ERROR_CODE_MESSAGE_NOT_FOUND,
    MGMT_REQUEST_ENQUEUED_TIME_UTC,
    MGMT_REQUEST_MESSAGE_COUNT,
    MGMT_REQUEST_SESSION_ID,
    MGMT_RESPONSE_MESSAGE_ERROR_CONDITION,
    REQUEST_RESPONSE_BATCH_DELETE_MESSAGES_OPERATION,
    NEXT_AVAILABLE_SESSION,
    ServiceBusReceiveMode,
)
from azure.servicebus._common import mgmt_handlers
from azure.servicebus._pyamqp._encode import encode_payload
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus.exceptions import OperationTimeoutError


MAX_DELETE_MESSAGE_COUNT = 500


def test_batch_delete_request_keys_encode_as_amqp_strings():
    message = PyamqpTransport.create_mgmt_msg(
        message={
            MGMT_REQUEST_MESSAGE_COUNT: PyamqpTransport.AMQP_INT_VALUE(1),
            MGMT_REQUEST_ENQUEUED_TIME_UTC: PyamqpTransport.AMQP_TIMESTAMP_VALUE(2),
        },
        application_properties={},
        config=MagicMock(encoding="UTF-8"),
        reply_to="queue/$management",
    )
    encoded = bytearray()
    encode_payload(encoded, message)

    assert b"\xa1\x0dmessage-count" in encoded
    assert b"\xa1\x11enqueued-time-utc" in encoded
    assert b"\xa0\x0dmessage-count" not in encoded
    assert b"\xa0\x11enqueued-time-utc" not in encoded


def test_batch_delete_handler_returns_actual_count_and_only_maps_204_to_zero():
    message = MagicMock()
    message.value = {b"message-count": 2}
    message.application_properties = {}
    transport = MagicMock()

    assert mgmt_handlers.batch_delete_op(200, message, None, transport, 10) == 2
    assert mgmt_handlers.batch_delete_op(204, message, None, transport, 10) == 0

    mgmt_handlers.batch_delete_op(202, message, "unexpected", transport, 10)
    transport.handle_amqp_mgmt_error.assert_called_once()


@pytest.mark.parametrize("deleted_count", [-1, 1.5, 11, True, None])
def test_batch_delete_handler_rejects_malformed_count(deleted_count):
    message = MagicMock()
    message.value = {b"message-count": deleted_count}
    message.application_properties = {}

    with pytest.raises(ValueError, match="valid message-count"):
        mgmt_handlers.batch_delete_op(200, message, None, MagicMock(), 10)


def test_batch_delete_handler_maps_message_not_found_to_aggregate():
    message = MagicMock()
    message.value = {b"message-count": 2}
    message.application_properties = {
        MGMT_RESPONSE_MESSAGE_ERROR_CONDITION: ERROR_CODE_MESSAGE_NOT_FOUND
    }

    assert (
        mgmt_handlers.batch_delete_op(404, message, None, MagicMock(), 10) == 2
    )


@pytest.mark.parametrize("value", [None, {}, {b"message-count": "2"}])
def test_batch_delete_handler_rejects_message_not_found_without_valid_count(value):
    message = MagicMock()
    message.value = value
    message.application_properties = {
        MGMT_RESPONSE_MESSAGE_ERROR_CONDITION: ERROR_CODE_MESSAGE_NOT_FOUND
    }

    with pytest.raises(ValueError, match="valid message-count"):
        mgmt_handlers.batch_delete_op(404, message, None, MagicMock(), 10)


def _receiver(receiver_type, session_id=None):
    receiver = object.__new__(receiver_type)
    receiver._check_live = lambda: None
    receiver._session_id = session_id
    receiver._session = object() if session_id else None
    receiver._handler = MagicMock()
    receiver._amqp_transport = MagicMock()
    receiver._amqp_transport.AMQP_INT_VALUE = lambda value: value
    receiver._amqp_transport.AMQP_TIMESTAMP_VALUE = lambda value: value
    receiver._open_with_retry = (
        AsyncMock() if receiver_type is AsyncServiceBusReceiver else MagicMock()
    )
    receiver._open_mgmt_link_with_retry = (
        AsyncMock() if receiver_type is AsyncServiceBusReceiver else MagicMock()
    )
    receiver._mgmt_request_response_with_retry = MagicMock(
        side_effect=AssertionError("destructive requests must not be retried")
    )
    return receiver


class TestDeleteMessages:
    @pytest.mark.parametrize(
        "session_id,expects_session_advice",
        [(None, False), (NEXT_AVAILABLE_SESSION, True)],
    )
    def test_setup_timeout_advice_only_applies_to_next_available_session(
        self, session_id, expects_session_advice
    ):
        receiver = _receiver(ServiceBusReceiver, session_id=session_id)
        receiver._config = MagicMock(retry_total=0)
        receiver._container_id = "receiver"
        receiver._handle_exception = lambda error: error

        def time_out():
            raise OperationTimeoutError()

        with pytest.raises(OperationTimeoutError) as exc_info:
            receiver._do_retryable_operation(time_out)

        assert ("NEXT_AVAILABLE_SESSION" in str(exc_info.value)) is expects_session_advice

    def test_returns_actual_count_and_uses_one_shot_dispatch(self):
        receiver = _receiver(ServiceBusReceiver)
        cutoff = datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc)
        calls = []

        def dispatch(operation, message, callback, **kwargs):
            calls.append((operation, message, callback, kwargs))
            return 7

        receiver._mgmt_request_response = dispatch

        result = receiver.delete_messages(10, before_enqueued_time=cutoff, timeout=12)

        assert result.deleted_message_count == 7
        assert len(calls) == 1
        assert calls[0][0] == REQUEST_RESPONSE_BATCH_DELETE_MESSAGES_OPERATION
        assert calls[0][2].func is mgmt_handlers.batch_delete_op
        assert calls[0][2].keywords["max_message_count"] == 10
        assert calls[0][1][MGMT_REQUEST_MESSAGE_COUNT] == 10
        assert calls[0][1][MGMT_REQUEST_ENQUEUED_TIME_UTC] == int(
            cutoff.timestamp() * 1000
        )
        assert 0 < calls[0][3]["timeout"] <= 12
        receiver._open_with_retry.assert_called_once_with(timeout=12)
        receiver._open_mgmt_link_with_retry.assert_called_once()
        receiver._mgmt_request_response_with_retry.assert_not_called()

    def test_setup_failure_does_not_dispatch(self):
        receiver = _receiver(ServiceBusReceiver)
        receiver._open_with_retry.side_effect = RuntimeError("open failed")
        receiver._mgmt_request_response = MagicMock()

        with pytest.raises(RuntimeError, match="open failed"):
            receiver.delete_messages(1)

        receiver._mgmt_request_response.assert_not_called()

    def test_management_setup_failure_does_not_dispatch(self):
        receiver = _receiver(ServiceBusReceiver)
        receiver._open_mgmt_link_with_retry.side_effect = RuntimeError("management open failed")
        receiver._mgmt_request_response = MagicMock()

        with pytest.raises(RuntimeError, match="management open failed"):
            receiver.delete_messages(1)

        receiver._mgmt_request_response.assert_not_called()

    def test_dispatch_failure_is_not_retried(self):
        receiver = _receiver(ServiceBusReceiver)
        receiver._mgmt_request_response = MagicMock(
            side_effect=RuntimeError("dispatch failed")
        )

        with pytest.raises(RuntimeError, match="dispatch failed"):
            receiver.delete_messages(1)

        receiver._open_with_retry.assert_called_once_with(timeout=None)
        receiver._mgmt_request_response.assert_called_once()
        receiver._mgmt_request_response_with_retry.assert_not_called()

    def test_dispatch_uses_remaining_timeout_and_stops_when_setup_exhausts_it(self):
        receiver = _receiver(ServiceBusReceiver)
        receiver._mgmt_request_response = MagicMock(return_value=1)

        with patch(
            "azure.servicebus._servicebus_receiver.time.monotonic",
            side_effect=[10.0, 11.0, 11.5],
        ):
            receiver.delete_messages(1, timeout=2)

        assert receiver._mgmt_request_response.call_args.kwargs[
            "timeout"
        ] == pytest.approx(0.5)
        assert receiver._open_mgmt_link_with_retry.call_args.kwargs[
            "timeout"
        ] == pytest.approx(1.0)

        receiver._mgmt_request_response.reset_mock()
        with patch(
            "azure.servicebus._servicebus_receiver.time.monotonic",
            side_effect=[20.0, 21.0],
        ):
            with pytest.raises(OperationTimeoutError, match="Operation timed out"):
                receiver.delete_messages(1, timeout=0.5)

        receiver._mgmt_request_response.assert_not_called()

    def test_forwards_session_id(self):
        receiver = _receiver(ServiceBusReceiver, session_id="session-a")
        captured = {}

        def dispatch(operation, message, callback, **kwargs):
            captured.update(message)
            return 1

        receiver._mgmt_request_response = dispatch

        receiver.delete_messages(1)

        assert captured[MGMT_REQUEST_SESSION_ID] == "session-a"

    def test_populates_session_id_after_setup_resolves_next_session(self):
        receiver = _receiver(ServiceBusReceiver, session_id="<next-available-session>")
        receiver._open_with_retry.side_effect = lambda **_: setattr(
            receiver, "_session_id", "session-a"
        )
        receiver._mgmt_request_response = MagicMock(return_value=1)

        receiver.delete_messages(1)

        message = receiver._mgmt_request_response.call_args.args[1]
        assert message[MGMT_REQUEST_SESSION_ID] == "session-a"

    def test_open_readiness_respects_timeout(self):
        receiver = _receiver(ServiceBusReceiver)
        receiver._running = False
        receiver._connection = None
        receiver._auto_lock_renewer = None
        receiver._receive_mode = ServiceBusReceiveMode.PEEK_LOCK
        receiver._handler._shutdown = False
        receiver._handler.client_ready.return_value = False
        receiver._create_handler = MagicMock()

        with patch(
            "azure.servicebus._servicebus_receiver.create_authentication",
            return_value=None,
        ), patch(
            "azure.servicebus._servicebus_receiver.time.monotonic",
            side_effect=[10.0, 11.0],
        ), patch(
            "azure.servicebus._servicebus_receiver.time.sleep"
        ):
            with pytest.raises(OperationTimeoutError):
                receiver._open(timeout=0.5)

    def test_supports_premium_count(self):
        receiver = _receiver(ServiceBusReceiver)
        receiver._mgmt_request_response = MagicMock(return_value=4000)

        result = receiver.delete_messages(4000)

        assert result.deleted_message_count == 4000
        assert (
            receiver._mgmt_request_response.call_args.args[1][
                MGMT_REQUEST_MESSAGE_COUNT
            ]
            == 4000
        )

    @pytest.mark.parametrize("message_count", [0, -1, 2_147_483_648])
    def test_rejects_counts_outside_service_limit(self, message_count):
        receiver = _receiver(ServiceBusReceiver)
        receiver._mgmt_request_response = MagicMock()

        with pytest.raises(ValueError):
            receiver.delete_messages(message_count)

        receiver._mgmt_request_response.assert_not_called()

    @pytest.mark.parametrize("message_count", [True, 1.5, "1"])
    def test_rejects_non_integer_counts(self, message_count):
        receiver = _receiver(ServiceBusReceiver)
        receiver._mgmt_request_response = MagicMock()

        with pytest.raises(TypeError):
            receiver.delete_messages(message_count)

        receiver._mgmt_request_response.assert_not_called()


class TestPurgeMessages:
    def test_keeps_one_cutoff_and_stops_only_on_zero(self):
        receiver = _receiver(ServiceBusReceiver)
        counts = iter([500, 2, 0])
        calls = []

        def dispatch(operation, message, callback, **kwargs):
            calls.append((message.copy(), kwargs))
            return next(counts)

        receiver._mgmt_request_response = dispatch

        cutoff = datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc)
        result = receiver.purge_messages(before_enqueued_time=cutoff, timeout=18)

        assert result.deleted_message_count == 502
        assert len(calls) == 3
        assert [call[0][MGMT_REQUEST_MESSAGE_COUNT] for call in calls] == [
            500,
            500,
            500,
        ]
        cutoffs = [call[0][MGMT_REQUEST_ENQUEUED_TIME_UTC] for call in calls]
        assert cutoffs[0] == cutoffs[1] == cutoffs[2]
        assert cutoffs[0] == int(cutoff.timestamp() * 1000)
        assert all(0 < call[1]["timeout"] <= 18 for call in calls)

    def test_supports_premium_batch_size(self):
        receiver = _receiver(ServiceBusReceiver)
        counts = iter([4000, 2, 0])
        calls = []

        def dispatch(operation, message, callback, **kwargs):
            calls.append(message.copy())
            return next(counts)

        receiver._mgmt_request_response = dispatch

        result = receiver.purge_messages(max_message_count_per_batch=4000)

        assert result.deleted_message_count == 4002
        assert [call[MGMT_REQUEST_MESSAGE_COUNT] for call in calls] == [
            4000,
            4000,
            4000,
        ]
        cutoffs = [call[MGMT_REQUEST_ENQUEUED_TIME_UTC] for call in calls]
        assert cutoffs[0] == cutoffs[1] == cutoffs[2]

    def test_allows_service_to_enforce_batch_size(self):
        receiver = _receiver(ServiceBusReceiver)
        receiver._mgmt_request_response = MagicMock(return_value=0)

        receiver.purge_messages(max_message_count_per_batch=4001)

        assert receiver._mgmt_request_response.call_args.args[1][MGMT_REQUEST_MESSAGE_COUNT] == 4001

    @pytest.mark.parametrize("message_count", [True, 0, 2_147_483_648])
    def test_rejects_invalid_batch_size(self, message_count):
        receiver = _receiver(ServiceBusReceiver)
        receiver._mgmt_request_response = MagicMock()

        with pytest.raises((TypeError, ValueError)):
            receiver.purge_messages(max_message_count_per_batch=message_count)

        receiver._mgmt_request_response.assert_not_called()

    def test_uses_one_operation_deadline(self):
        receiver = _receiver(ServiceBusReceiver)
        receiver.delete_messages = MagicMock(
            side_effect=[DeleteMessagesResult(1), DeleteMessagesResult(0)]
        )

        with patch(
            "azure.servicebus._servicebus_receiver.time.monotonic",
            side_effect=[10.0, 11.0, 12.0],
        ):
            result = receiver.purge_messages(timeout=5)

        assert result.deleted_message_count == 1
        assert [call.kwargs["timeout"] for call in receiver.delete_messages.call_args_list] == [4.0, 3.0]

    def test_operation_deadline_stops_before_another_dispatch(self):
        receiver = _receiver(ServiceBusReceiver)
        receiver.delete_messages = MagicMock(return_value=DeleteMessagesResult(1))

        with patch(
            "azure.servicebus._servicebus_receiver.time.monotonic",
            side_effect=[20.0, 21.0, 25.1],
        ):
            with pytest.raises(OperationTimeoutError):
                receiver.purge_messages(timeout=5)

        receiver.delete_messages.assert_called_once()


class TestDeleteMessagesAsync:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "session_id,expects_session_advice",
        [(None, False), (NEXT_AVAILABLE_SESSION, True)],
    )
    async def test_setup_timeout_advice_only_applies_to_next_available_session(
        self, session_id, expects_session_advice
    ):
        receiver = _receiver(AsyncServiceBusReceiver, session_id=session_id)
        receiver._config = MagicMock(retry_total=0)
        receiver._container_id = "receiver"

        async def handle_exception(error):
            return error

        async def time_out():
            raise OperationTimeoutError()

        receiver._handle_exception = handle_exception
        with pytest.raises(OperationTimeoutError) as exc_info:
            await receiver._do_retryable_operation(time_out)

        assert ("NEXT_AVAILABLE_SESSION" in str(exc_info.value)) is expects_session_advice

    @pytest.mark.asyncio
    async def test_returns_actual_count_and_uses_one_shot_dispatch(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        cutoff = datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc)
        calls = []

        async def dispatch(operation, message, callback, **kwargs):
            calls.append((operation, message, callback, kwargs))
            return 7

        receiver._mgmt_request_response = dispatch

        result = await receiver.delete_messages(
            10, before_enqueued_time=cutoff, timeout=12
        )

        assert result.deleted_message_count == 7
        assert len(calls) == 1
        assert calls[0][0] == REQUEST_RESPONSE_BATCH_DELETE_MESSAGES_OPERATION
        assert calls[0][2].func is mgmt_handlers.batch_delete_op
        assert calls[0][2].keywords["max_message_count"] == 10
        assert calls[0][1][MGMT_REQUEST_MESSAGE_COUNT] == 10
        assert calls[0][1][MGMT_REQUEST_ENQUEUED_TIME_UTC] == int(
            cutoff.timestamp() * 1000
        )
        assert 0 < calls[0][3]["timeout"] <= 12
        receiver._open_with_retry.assert_awaited_once_with(timeout=12)
        receiver._open_mgmt_link_with_retry.assert_awaited_once()
        receiver._mgmt_request_response_with_retry.assert_not_called()

    @pytest.mark.asyncio
    async def test_setup_failure_does_not_dispatch(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        receiver._open_with_retry.side_effect = RuntimeError("open failed")
        receiver._mgmt_request_response = AsyncMock()

        with pytest.raises(RuntimeError, match="open failed"):
            await receiver.delete_messages(1)

        receiver._mgmt_request_response.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_management_setup_failure_does_not_dispatch(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        receiver._open_mgmt_link_with_retry.side_effect = RuntimeError("management open failed")
        receiver._mgmt_request_response = AsyncMock()

        with pytest.raises(RuntimeError, match="management open failed"):
            await receiver.delete_messages(1)

        receiver._mgmt_request_response.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_populates_session_id_after_setup_resolves_next_session(self):
        receiver = _receiver(
            AsyncServiceBusReceiver, session_id="<next-available-session>"
        )

        async def resolve_session(**_):
            receiver._session_id = "session-a"

        receiver._open_with_retry.side_effect = resolve_session
        receiver._mgmt_request_response = AsyncMock(return_value=1)

        await receiver.delete_messages(1)

        message = receiver._mgmt_request_response.call_args.args[1]
        assert message[MGMT_REQUEST_SESSION_ID] == "session-a"

    @pytest.mark.asyncio
    async def test_open_readiness_respects_timeout(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        receiver._running = False
        receiver._connection = None
        receiver._auto_lock_renewer = None
        receiver._receive_mode = ServiceBusReceiveMode.PEEK_LOCK
        receiver._handler._shutdown = False
        receiver._handler.close_async = AsyncMock()
        receiver._handler.open_async = AsyncMock()
        receiver._handler.client_ready_async = AsyncMock(return_value=False)
        receiver._amqp_transport.drain_and_release_messages_async = AsyncMock()
        receiver._create_handler = MagicMock()

        with patch(
            "azure.servicebus.aio._servicebus_receiver_async.create_authentication",
            new=AsyncMock(return_value=None),
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.time.monotonic",
            side_effect=[10.0, 11.0],
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.asyncio.sleep",
            new=AsyncMock(),
        ):
            with pytest.raises(OperationTimeoutError):
                await receiver._open(timeout=0.5)

    @pytest.mark.asyncio
    async def test_dispatch_failure_is_not_retried(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        receiver._mgmt_request_response = AsyncMock(
            side_effect=RuntimeError("dispatch failed")
        )

        with pytest.raises(RuntimeError, match="dispatch failed"):
            await receiver.delete_messages(1)

        receiver._open_with_retry.assert_awaited_once_with(timeout=None)
        receiver._mgmt_request_response.assert_awaited_once()
        receiver._mgmt_request_response_with_retry.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_uses_remaining_timeout_and_stops_when_setup_exhausts_it(
        self,
    ):
        receiver = _receiver(AsyncServiceBusReceiver)
        receiver._mgmt_request_response = AsyncMock(return_value=1)

        with patch(
            "azure.servicebus.aio._servicebus_receiver_async.time.monotonic",
            side_effect=[10.0, 11.0, 11.5],
        ):
            await receiver.delete_messages(1, timeout=2)

        assert receiver._mgmt_request_response.call_args.kwargs[
            "timeout"
        ] == pytest.approx(0.5)
        assert receiver._open_mgmt_link_with_retry.call_args.kwargs[
            "timeout"
        ] == pytest.approx(1.0)

        receiver._mgmt_request_response.reset_mock()
        with patch(
            "azure.servicebus.aio._servicebus_receiver_async.time.monotonic",
            side_effect=[20.0, 21.0],
        ):
            with pytest.raises(OperationTimeoutError, match="Operation timed out"):
                await receiver.delete_messages(1, timeout=0.5)

        receiver._mgmt_request_response.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_keeps_one_cutoff_and_stops_only_on_zero(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        counts = iter([500, 2, 0])
        calls = []

        async def dispatch(operation, message, callback, **kwargs):
            calls.append((message.copy(), kwargs))
            return next(counts)

        receiver._mgmt_request_response = dispatch

        cutoff = datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc)
        result = await receiver.purge_messages(before_enqueued_time=cutoff, timeout=18)

        assert result.deleted_message_count == 502
        assert len(calls) == 3
        assert [call[0][MGMT_REQUEST_MESSAGE_COUNT] for call in calls] == [
            500,
            500,
            500,
        ]
        cutoffs = [call[0][MGMT_REQUEST_ENQUEUED_TIME_UTC] for call in calls]
        assert cutoffs[0] == cutoffs[1] == cutoffs[2]
        assert cutoffs[0] == int(cutoff.timestamp() * 1000)
        assert all(0 < call[1]["timeout"] <= 18 for call in calls)

    @pytest.mark.asyncio
    async def test_purge_supports_premium_batch_size(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        receiver._mgmt_request_response = AsyncMock(side_effect=[4000, 2, 0])

        result = await receiver.purge_messages(max_message_count_per_batch=4000)

        assert result.deleted_message_count == 4002
        calls = receiver._mgmt_request_response.await_args_list
        assert [call.args[1][MGMT_REQUEST_MESSAGE_COUNT] for call in calls] == [
            4000,
            4000,
            4000,
        ]
        cutoffs = [call.args[1][MGMT_REQUEST_ENQUEUED_TIME_UTC] for call in calls]
        assert cutoffs[0] == cutoffs[1] == cutoffs[2]

    @pytest.mark.asyncio
    async def test_purge_allows_service_to_enforce_batch_size(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        receiver._mgmt_request_response = AsyncMock(return_value=0)

        await receiver.purge_messages(max_message_count_per_batch=4001)

        assert receiver._mgmt_request_response.call_args.args[1][MGMT_REQUEST_MESSAGE_COUNT] == 4001

    @pytest.mark.asyncio
    async def test_purge_uses_one_operation_deadline(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        receiver.delete_messages = AsyncMock(
            side_effect=[DeleteMessagesResult(1), DeleteMessagesResult(0)]
        )

        with patch(
            "azure.servicebus.aio._servicebus_receiver_async.time.monotonic",
            side_effect=[10.0, 11.0, 12.0],
        ):
            result = await receiver.purge_messages(timeout=5)

        assert result.deleted_message_count == 1
        assert [call.kwargs["timeout"] for call in receiver.delete_messages.await_args_list] == [4.0, 3.0]

    @pytest.mark.asyncio
    async def test_purge_deadline_stops_before_another_dispatch(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        receiver.delete_messages = AsyncMock(return_value=DeleteMessagesResult(1))

        with patch(
            "azure.servicebus.aio._servicebus_receiver_async.time.monotonic",
            side_effect=[20.0, 21.0, 25.1],
        ):
            with pytest.raises(OperationTimeoutError):
                await receiver.purge_messages(timeout=5)

        receiver.delete_messages.assert_awaited_once()
