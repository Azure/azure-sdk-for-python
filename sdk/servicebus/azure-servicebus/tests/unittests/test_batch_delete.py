# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import ast
import asyncio
import threading
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.servicebus import DeleteMessagesResult, ServiceBusClient, ServiceBusReceiver, ServiceBusSubQueue
from azure.servicebus.aio import ServiceBusClient as AsyncServiceBusClient, ServiceBusReceiver as AsyncServiceBusReceiver
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
from azure.servicebus._base_handler import BaseHandler
from azure.servicebus.aio._base_handler_async import BaseHandler as AsyncBaseHandler
from azure.servicebus._pyamqp._encode import encode_payload
from azure.servicebus._pyamqp.client import AMQPClient
from azure.servicebus._pyamqp.aio._client_async import AMQPClientAsync
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus.aio._transport._pyamqp_transport_async import PyamqpTransportAsync
from azure.servicebus.exceptions import OperationTimeoutError


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_default_open_with_timeout_forwards_budget(is_async):
    handler = object.__new__(AsyncBaseHandler if is_async else BaseHandler)
    handler._open = AsyncMock() if is_async else MagicMock()
    if is_async:
        await handler._open_with_timeout(1.5)
        handler._open.assert_awaited_once_with(timeout=1.5)
    else:
        handler._open_with_timeout(1.5)
        handler._open.assert_called_once_with(timeout=1.5)


@pytest.mark.parametrize("sample", [
    ("sync_samples", "sample_code_servicebus.py"),
    ("async_samples", "sample_code_servicebus_async.py"),
])
def test_destructive_sample_examples_are_standalone(sample):
    source = Path(__file__).resolve().parents[2].joinpath("samples", *sample).read_text(encoding="utf-8")
    tree = ast.parse(source)
    startup = ast.Module(
        body=[node for node in tree.body if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))],
        type_ignores=[],
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id.startswith(("example_delete", "example_purge"))
        for node in ast.walk(startup)
    )


@pytest.mark.parametrize("uamqp_transport", [False, True], ids=["pyamqp", "uamqp"])
def test_batch_delete_request_keys_encode_as_amqp_strings(uamqp_transport):
    transport = PyamqpTransport
    if uamqp_transport:
        pytest.importorskip("uamqp")
        from azure.servicebus._transport._uamqp_transport import UamqpTransport
        transport = UamqpTransport
    message = transport.create_mgmt_msg(
        message={
            MGMT_REQUEST_MESSAGE_COUNT: transport.AMQP_INT_VALUE(1),
            MGMT_REQUEST_ENQUEUED_TIME_UTC: transport.AMQP_TIMESTAMP_VALUE(2),
        },
        application_properties={},
        config=MagicMock(encoding="UTF-8"),
        reply_to="queue/$management",
    )
    if uamqp_transport:
        encoded = message.encode_message()
    else:
        encoded = bytearray()
        encode_payload(encoded, message)

    assert b"\xa1\x0dmessage-count" in encoded
    assert b"\xa1\x11enqueued-time-utc" in encoded
    assert b"\xa0\x0dmessage-count" not in encoded
    assert b"\xa0\x11enqueued-time-utc" not in encoded


@pytest.mark.parametrize("deleted_count", [0, 2])
def test_batch_delete_uamqp_response_round_trip(deleted_count):
    uamqp = pytest.importorskip("uamqp")
    from azure.servicebus._transport._uamqp_transport import UamqpTransport
    response = uamqp.Message(body={b"message-count": deleted_count}, application_properties={b"status-code": 200})
    decoded = uamqp.Message.decode_from_bytes(response.encode_message())
    assert mgmt_handlers.batch_delete_op(200, decoded, None, UamqpTransport, 10) == deleted_count


def test_batch_delete_handler_returns_actual_count_and_rejects_204():
    message = MagicMock()
    message.value = {b"message-count": 2}
    message.application_properties = {}
    transport = MagicMock()

    assert mgmt_handlers.batch_delete_op(200, message, None, transport, 10) == 2

    mgmt_handlers.batch_delete_op(204, message, "missing count", transport, 10)
    transport.handle_amqp_mgmt_error.assert_called_once()
    transport.reset_mock()
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


@pytest.mark.parametrize("cleanup_error", [None, RuntimeError("close failed")])
def test_failed_management_link_open_is_evicted_before_retry(cleanup_error):
    client = object.__new__(AMQPClient)
    client._mgmt_links = {}
    client._mgmt_link_lock = threading.Lock()
    client._session = MagicMock()
    client.auth_complete = MagicMock(return_value=True)
    failed_link = MagicMock()
    failed_link.open.side_effect = RuntimeError("attach failed")
    failed_link.close.side_effect = cleanup_error
    ready_link = MagicMock()
    ready_link.ready.return_value = True

    with patch(
        "azure.servicebus._pyamqp.client.ManagementOperation",
        side_effect=[failed_link, ready_link],
    ) as operation_type:
        with pytest.raises(RuntimeError, match="attach failed"):
            client.open_mgmt_link()
        assert client._mgmt_links == {}
        failed_link.close.assert_called_once()

        assert client.open_mgmt_link() is ready_link

    assert operation_type.call_count == 2


def test_management_link_setup_converts_timeout_error():
    client = MagicMock()
    client.open_mgmt_link.side_effect = TimeoutError("setup timed out")

    with pytest.raises(OperationTimeoutError):
        PyamqpTransport.mgmt_client_setup(client, node="$management", timeout=1)


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize(
    "setup_error", [TimeoutError("setup timed out"), RuntimeError("setup failed"), asyncio.CancelledError()]
)
async def test_cached_management_link_is_not_closed_by_failed_borrower(is_async, setup_error):
    client = object.__new__(AMQPClientAsync if is_async else AMQPClient)
    link = MagicMock()
    client._mgmt_links = {"$management": link}
    if is_async:
        client._mgmt_link_lock_async = asyncio.Lock()
        client.auth_complete_async = AsyncMock(return_value=True)
        link.ready = AsyncMock(side_effect=setup_error)
        link.close = AsyncMock()
    else:
        client._mgmt_link_lock = threading.Lock()
        client.auth_complete = MagicMock(return_value=True)
        link.ready.side_effect = setup_error
    with pytest.raises(type(setup_error)) as caught:
        if is_async:
            await client.open_mgmt_link_async()
        else:
            client.open_mgmt_link()
    assert caught.value is setup_error
    assert client._mgmt_links == {"$management": link}
    link.close.assert_not_called()
    link.ready.side_effect = None
    link.ready.return_value = True
    if is_async:
        assert await client.open_mgmt_link_async() is link
    else:
        assert client.open_mgmt_link() is link


@pytest.mark.asyncio
@pytest.mark.parametrize("setup_error", [RuntimeError("attach failed"), asyncio.CancelledError()])
@pytest.mark.parametrize("cleanup_error", [None, RuntimeError("close failed"), asyncio.CancelledError()])
async def test_failed_async_management_link_open_is_evicted_before_retry(setup_error, cleanup_error):
    client = object.__new__(AMQPClientAsync)
    client._mgmt_links = {}
    client._mgmt_link_lock_async = asyncio.Lock()
    client._session = MagicMock()
    client.auth_complete_async = AsyncMock(return_value=True)
    failed_link = MagicMock()
    failed_link.open = AsyncMock(side_effect=setup_error)
    failed_link.close = AsyncMock(side_effect=cleanup_error)
    ready_link = MagicMock()
    ready_link.open = AsyncMock()
    ready_link.ready = AsyncMock(return_value=True)

    with patch(
        "azure.servicebus._pyamqp.aio._client_async.ManagementOperation",
        side_effect=[failed_link, ready_link],
    ) as operation_type:
        with pytest.raises(type(setup_error)) as caught:
            await client.open_mgmt_link_async()
        assert caught.value is setup_error
        assert client._mgmt_links == {}
        failed_link.close.assert_awaited_once()

        assert await client.open_mgmt_link_async() is ready_link

    assert operation_type.call_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("timeout", [None, 0])
@pytest.mark.parametrize("cancel_setup", [False, True])
async def test_unbounded_async_setup_does_not_stall_on_cleanup(timeout, cancel_setup):
    client = object.__new__(AMQPClientAsync)
    client._mgmt_links = {}
    client._mgmt_link_lock_async = asyncio.Lock()
    client._session = MagicMock()
    opening = asyncio.Event()
    setup_error = RuntimeError("attach failed")

    async def open_link():
        opening.set()
        if not cancel_setup:
            raise setup_error
        await asyncio.Event().wait()

    link = MagicMock(open=AsyncMock(side_effect=open_link), close=AsyncMock(side_effect=asyncio.Event().wait))
    with patch("azure.servicebus._pyamqp.aio._client_async.ManagementOperation", return_value=link):
        task = asyncio.create_task(client.open_mgmt_link_async(timeout=timeout))
        try:
            await opening.wait()
            if cancel_setup:
                task.cancel()
            done, _ = await asyncio.wait({task}, timeout=2)
            assert task in done, "Management cleanup must finish without a second cancellation."
            with pytest.raises(asyncio.CancelledError if cancel_setup else RuntimeError) as caught:
                await task
            if not cancel_setup:
                assert caught.value is setup_error
            assert client._mgmt_links == {}
            link.close.assert_awaited_once()
        finally:
            if not task.done():
                task.cancel()
                with pytest.raises((RuntimeError, asyncio.CancelledError)):
                    await task


@pytest.mark.asyncio
@pytest.mark.parametrize("client_type", [ServiceBusClient, AsyncServiceBusClient])
@pytest.mark.parametrize("subscription", [False, True])
@pytest.mark.parametrize("operation", ["delete_messages", "purge_messages"])
@pytest.mark.parametrize("sub_queue,suffix", [
    (ServiceBusSubQueue.DEAD_LETTER, "/$DeadLetterQueue"),
    (ServiceBusSubQueue.TRANSFER_DEAD_LETTER, "/$Transfer/$DeadLetterQueue"),
])
async def test_client_created_subqueue_batch_delete_routing(client_type, subscription, operation, sub_queue, suffix):
    client = client_type("example.servicebus.windows.net", MagicMock())
    is_async = client_type is AsyncServiceBusClient
    try:
        if subscription:
            receiver = client.get_subscription_receiver("topic", "subscription", sub_queue=sub_queue)
            entity_path = "topic/Subscriptions/subscription"
        else:
            receiver = client.get_queue_receiver("queue", sub_queue=sub_queue)
            entity_path = "queue"
        receiver._open = AsyncMock() if is_async else MagicMock()
        expected_node = (entity_path + suffix + "/$management").encode("UTF-8")
        setup_method = "mgmt_client_setup_async" if is_async else "mgmt_client_setup"
        request_method = "mgmt_client_request_async" if is_async else "mgmt_client_request"
        with patch.object(receiver._amqp_transport, setup_method) as setup, patch.object(
            receiver._amqp_transport, request_method, return_value=0
        ) as dispatch:
            args = (1,) if operation == "delete_messages" else ()
            if is_async:
                await getattr(receiver, operation)(*args)
            else:
                getattr(receiver, operation)(*args)
            assert setup.call_args.kwargs["node"] == expected_node
            assert dispatch.call_args.kwargs["node"] == expected_node
            assert dispatch.call_args.kwargs["operation"] == REQUEST_RESPONSE_BATCH_DELETE_MESSAGES_OPERATION
    finally:
        if is_async:
            await client.close()
        else:
            client.close()


@pytest.mark.asyncio
async def test_async_management_link_setup_converts_timeout_error():
    client = MagicMock()
    client.open_mgmt_link_async = AsyncMock(side_effect=TimeoutError("setup timed out"))

    with pytest.raises(OperationTimeoutError):
        await PyamqpTransportAsync.mgmt_client_setup_async(
            client, node="$management", timeout=1
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("phase", ["lock", "open", "auth", "ready", "open_cleanup", "auth_cleanup_lock"])
async def test_async_management_setup_deadline_prevents_dispatch(phase):
    client = object.__new__(AMQPClientAsync)
    client._mgmt_links = {}
    client._mgmt_link_lock_async = asyncio.Lock()
    client._session = MagicMock()
    client.auth_complete_async = AsyncMock(return_value=True)
    link = MagicMock(open=AsyncMock(), ready=AsyncMock(return_value=True), close=AsyncMock())
    blocked = AsyncMock(side_effect=asyncio.Event().wait)
    if phase == "lock":
        await client._mgmt_link_lock_async.acquire()
        client._mgmt_links["$management"] = link
    elif phase == "auth":
        client.auth_complete_async = blocked
    elif phase == "open_cleanup":
        link.open = blocked
        link.close = AsyncMock(side_effect=asyncio.Event().wait)
    elif phase == "auth_cleanup_lock":
        async def blocked_auth():
            await client._mgmt_link_lock_async.acquire()
            await blocked()

        client.auth_complete_async = AsyncMock(side_effect=blocked_auth)
    else:
        setattr(link, phase, blocked)
    receiver = _receiver(AsyncServiceBusReceiver)
    receiver._config = MagicMock(retry_total=0, try_timeout=None, encoding="UTF-8")
    receiver._container_id = "receiver"
    receiver._mgmt_target = "$management"
    receiver._handler = client
    receiver._amqp_transport = PyamqpTransportAsync
    receiver._open_with_timeout = AsyncMock()
    receiver._handle_exception = AsyncMock(side_effect=lambda error: error)
    receiver._mgmt_request_response = AsyncMock()
    receiver._open_mgmt_link_with_retry = AsyncServiceBusReceiver._open_mgmt_link_with_retry.__get__(receiver)
    try:
        with patch("azure.servicebus._pyamqp.aio._client_async.ManagementOperation", return_value=link):
            with pytest.raises(OperationTimeoutError):
                await asyncio.wait_for(receiver.delete_messages(1, timeout=0.05), timeout=1)
        receiver._mgmt_request_response.assert_not_awaited()
        if phase == "lock":
            assert client._mgmt_links == {"$management": link}
            link.close.assert_not_called()
        else:
            blocked.assert_awaited_once()
            assert client._mgmt_links == {}
            link.close.assert_called_once()
    finally:
        if phase in ("lock", "auth_cleanup_lock"):
            client._mgmt_link_lock_async.release()


class TestDeleteMessages:
    @pytest.mark.parametrize(
        "session_id,suppress_session_advice,expects_session_advice",
        [
            (None, False, False),
            (NEXT_AVAILABLE_SESSION, False, True),
            (NEXT_AVAILABLE_SESSION, True, False),
        ],
    )
    def test_setup_timeout_advice_only_applies_to_next_available_session(
        self, session_id, suppress_session_advice, expects_session_advice
    ):
        receiver = _receiver(ServiceBusReceiver, session_id=session_id)
        receiver._config = MagicMock(retry_total=0)
        receiver._container_id = "receiver"
        receiver._handle_exception = lambda error: error

        def time_out():
            raise OperationTimeoutError()

        with pytest.raises(OperationTimeoutError) as exc_info:
            receiver._do_retryable_operation(
                time_out,
                suppress_next_session_timeout_message=suppress_session_advice,
            )

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
        receiver._open_with_retry.assert_called_once_with(
            timeout=12, suppress_next_session_timeout_message=True
        )
        receiver._open_mgmt_link_with_retry.assert_called_once()
        setup_kwargs = receiver._open_mgmt_link_with_retry.call_args.kwargs
        assert setup_kwargs["suppress_next_session_timeout_message"] is True
        assert 0 < setup_kwargs["timeout"] <= 12
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

        receiver._open_with_retry.assert_called_once_with(
            timeout=None, suppress_next_session_timeout_message=True
        )
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

    def test_management_setup_shares_timeout_with_receiver_reopen(self):
        receiver = _receiver(ServiceBusReceiver)
        receiver._config = MagicMock(
            retry_total=0, encoding="UTF-8", try_timeout=None
        )
        receiver._container_id = "receiver"
        receiver._mgmt_target = "$management"
        receiver._open_with_timeout = MagicMock()
        receiver._amqp_transport.mgmt_client_setup = MagicMock()

        with patch(
            "azure.servicebus._base_handler.time.monotonic",
            side_effect=[10.0, 10.0, 10.0, 10.5],
        ):
            ServiceBusReceiver._open_mgmt_link_with_retry(receiver, timeout=2)

        receiver._open_with_timeout.assert_called_once()
        receiver_timeout = receiver._open_with_timeout.call_args.args[0]
        assert 0 < receiver_timeout <= 2
        receiver._amqp_transport.mgmt_client_setup.assert_called_once()
        setup_args = receiver._amqp_transport.mgmt_client_setup.call_args
        assert setup_args.args == (receiver._handler,)
        assert setup_args.kwargs["node"] == receiver._mgmt_target.encode("UTF-8")
        assert setup_args.kwargs["timeout"] == pytest.approx(receiver_timeout - 0.5)

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

    def test_open_authentication_consumes_timeout(self):
        receiver = _receiver(ServiceBusReceiver)
        receiver._running = False
        receiver._connection = None
        receiver._handler = None
        receiver._create_handler = MagicMock()

        with patch(
            "azure.servicebus._servicebus_receiver.create_authentication",
            return_value=None,
        ), patch(
            "azure.servicebus._servicebus_receiver.time.monotonic",
            side_effect=[10.0, 11.0],
        ):
            with pytest.raises(OperationTimeoutError):
                receiver._open(timeout=0.5)

        receiver._create_handler.assert_not_called()

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
        "session_id,suppress_session_advice,expects_session_advice",
        [
            (None, False, False),
            (NEXT_AVAILABLE_SESSION, False, True),
            (NEXT_AVAILABLE_SESSION, True, False),
        ],
    )
    async def test_setup_timeout_advice_only_applies_to_next_available_session(
        self, session_id, suppress_session_advice, expects_session_advice
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
            await receiver._do_retryable_operation(
                time_out,
                suppress_next_session_timeout_message=suppress_session_advice,
            )

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
        receiver._open_with_retry.assert_awaited_once_with(
            timeout=12, suppress_next_session_timeout_message=True
        )
        receiver._open_mgmt_link_with_retry.assert_awaited_once()
        setup_kwargs = receiver._open_mgmt_link_with_retry.await_args.kwargs
        assert setup_kwargs["suppress_next_session_timeout_message"] is True
        assert 0 < setup_kwargs["timeout"] <= 12
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

        async def await_operation(awaitable, _deadline, _message):
            return await awaitable

        async def discard_cleanup(close_coro, _deadline):
            close_coro.close()

        with patch(
            "azure.servicebus.aio._servicebus_receiver_async.create_authentication",
            new=AsyncMock(return_value=None),
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.get_link_ready_deadline",
            return_value=10.5,
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.check_link_ready_deadline",
            side_effect=[None, None, None, OperationTimeoutError()],
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.close_handler_with_deadline",
            new=AsyncMock(),
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.open_handler_with_deadline",
            new=AsyncMock(),
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.close_handler_for_cleanup",
            side_effect=discard_cleanup,
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.await_with_deadline",
            side_effect=await_operation,
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.asyncio.sleep",
            new=AsyncMock(),
        ):
            with pytest.raises(OperationTimeoutError):
                await receiver._open(timeout=0.5)

    @pytest.mark.asyncio
    async def test_open_authentication_consumes_timeout(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        receiver._running = False
        receiver._connection = None
        receiver._handler = None
        receiver._create_handler = MagicMock()

        async def authentication_timeout(awaitable, _deadline, _message):
            awaitable.close()
            raise OperationTimeoutError()

        with patch(
            "azure.servicebus.aio._servicebus_receiver_async.create_authentication",
            new=AsyncMock(return_value=None),
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.get_link_ready_deadline",
            return_value=10.5,
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.check_link_ready_deadline",
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.await_with_deadline",
            side_effect=authentication_timeout,
        ):
            with pytest.raises(OperationTimeoutError):
                await receiver._open(timeout=0.5)

        receiver._create_handler.assert_not_called()

    @pytest.mark.asyncio
    async def test_open_does_not_create_awaitable_after_timeout(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        receiver._running = False
        receiver._connection = None
        receiver._handler = None
        authentication = AsyncMock(return_value=None)

        with patch(
            "azure.servicebus.aio._servicebus_receiver_async.create_authentication",
            new=authentication,
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.get_link_ready_deadline",
            return_value=10.5,
        ), patch(
            "azure.servicebus.aio._servicebus_receiver_async.check_link_ready_deadline",
            side_effect=OperationTimeoutError(),
        ):
            with pytest.raises(OperationTimeoutError):
                await receiver._open(timeout=0.5)

        authentication.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_failure_is_not_retried(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        receiver._mgmt_request_response = AsyncMock(
            side_effect=RuntimeError("dispatch failed")
        )

        with pytest.raises(RuntimeError, match="dispatch failed"):
            await receiver.delete_messages(1)

        receiver._open_with_retry.assert_awaited_once_with(
            timeout=None, suppress_next_session_timeout_message=True
        )
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
    async def test_management_setup_shares_timeout_with_receiver_reopen(self):
        receiver = _receiver(AsyncServiceBusReceiver)
        receiver._config = MagicMock(
            retry_total=0, encoding="UTF-8", try_timeout=None
        )
        receiver._container_id = "receiver"
        receiver._mgmt_target = "$management"
        clock = MagicMock(return_value=10.0)

        async def open_receiver(_timeout):
            clock.return_value = 10.5

        receiver._open_with_timeout = AsyncMock(side_effect=open_receiver)
        receiver._amqp_transport.mgmt_client_setup_async = AsyncMock()

        with patch(
            "azure.servicebus.aio._base_handler_async.time.monotonic",
            clock,
        ):
            await AsyncServiceBusReceiver._open_mgmt_link_with_retry(
                receiver, timeout=2
            )

        receiver._open_with_timeout.assert_awaited_once()
        receiver_timeout = receiver._open_with_timeout.await_args.args[0]
        assert 0 < receiver_timeout <= 2
        receiver._amqp_transport.mgmt_client_setup_async.assert_awaited_once()
        setup_args = receiver._amqp_transport.mgmt_client_setup_async.await_args
        assert setup_args.args == (receiver._handler,)
        assert setup_args.kwargs["node"] == receiver._mgmt_target.encode("UTF-8")
        assert setup_args.kwargs["timeout"] == pytest.approx(receiver_timeout - 0.5)

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
