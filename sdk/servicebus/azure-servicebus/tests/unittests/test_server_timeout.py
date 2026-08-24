# Copyright (c) Microsoft Corporation. All rights reserved.

"""Unit tests for the management server-timeout.

Management operations send the `com.microsoft:server-timeout` property, asking the service to
bound the operation on its side. The value is the caller's remaining time less a one second
buffer, so the service answers before the client gives up, or 60 seconds when the caller
supplied no timeout.

Previously no bound was sent at all, so a stalled service could hold a management call until
the AMQP link itself failed. Matches the .NET, Java and Go SDKs.
"""

from unittest.mock import MagicMock

import struct

import pytest

from azure.servicebus._common import mgmt_handlers
from azure.servicebus._common.constants import (
    ERROR_CODE_TIMEOUT,
    MAX_SERVER_TIMEOUT_MS,
    MGMT_RESPONSE_MESSAGE_ERROR_CONDITION,
    REQUEST_RESPONSE_TIMEOUT,
)
from azure.servicebus._common.utils import get_server_timeout_ms
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus.exceptions import OperationTimeoutError


class TestServerTimeoutMillis:
    """`get_server_timeout_ms` converts the caller's remaining time into the
    value advertised to the service."""

    @pytest.mark.parametrize(
        "remaining_seconds,expected_ms",
        [
            (None, 60000),  # no caller timeout: the default, not "no bound at all"
            (120, 119000),
            (60, 59000),  # equals the default, but must still take the buffer path
            (10, 9000),
            (1.5, 500),
            (1, 0),  # at the buffer, nothing left to give the service
            (0.5, 0),
            (-5, 0),  # deadline already passed: clamped, never a negative uint
        ],
    )
    def test_remaining_time_less_buffer(self, remaining_seconds, expected_ms):
        assert get_server_timeout_ms(remaining_seconds) == expected_ms

    def test_wire_contract(self):
        # The key .NET and Java send, encoded as an unsigned int of milliseconds.
        assert REQUEST_RESPONSE_TIMEOUT == b"com.microsoft:server-timeout"
        encoded = PyamqpTransport.AMQP_UINT_VALUE(get_server_timeout_ms(None))
        assert encoded == {"TYPE": "UINT", "VALUE": 60000}

    @pytest.mark.parametrize("remaining_seconds", [4294968, 5_000_000, 1e12, float("inf")])
    def test_capped_at_the_amqp_uint_maximum(self, remaining_seconds):
        # `timeout` is only bounded at zero, so a large value would overflow the uint encoder.
        result = get_server_timeout_ms(remaining_seconds)
        assert result <= MAX_SERVER_TIMEOUT_MS
        struct.pack(">I", result)  # raises if it does not fit

    def test_just_below_the_cap_is_not_clamped(self):
        assert get_server_timeout_ms(4294967) == 4294966000


class TestManagementRequestSetsServerTimeout:
    """The property must actually reach the outgoing management message, on both
    the associated-link and no-associated-link paths."""

    def _make_handler(self):
        from azure.servicebus._base_handler import BaseHandler

        captured = {}

        def fake_create_mgmt_msg(message, application_properties, config, reply_to, **kwargs):
            captured.clear()
            captured.update(application_properties)
            return MagicMock()

        handler = BaseHandler.__new__(BaseHandler)
        handler._amqp_transport = MagicMock()
        handler._amqp_transport.create_mgmt_msg = fake_create_mgmt_msg
        handler._amqp_transport.AMQP_UINT_VALUE = PyamqpTransport.AMQP_UINT_VALUE
        handler._amqp_transport.get_handler_link_name = lambda h: "link-1"
        handler._amqp_transport.mgmt_client_request = lambda *args, **kwargs: "response"
        handler._amqp_transport.TIMEOUT_ERROR = TimeoutError
        handler._open = lambda timeout=None: None
        handler._handler = MagicMock()
        handler._config = MagicMock(encoding="UTF-8")
        handler._mgmt_target = "queue/$management"
        return handler, captured

    def test_default_sent_when_caller_gave_no_timeout(self):
        # The gap this closes: previously no bound was sent at all.
        handler, captured = self._make_handler()
        handler._mgmt_request_response(b"op", {}, lambda *a: None, timeout=None)
        assert captured[REQUEST_RESPONSE_TIMEOUT] == {"TYPE": "UINT", "VALUE": 60000}

    def test_remaining_time_less_buffer_sent(self):
        handler, captured = self._make_handler()
        handler._mgmt_request_response(b"op", {}, lambda *a: None, timeout=10)
        # Link acquisition is deducted from the attempt, so this is at most 9000.
        assert captured[REQUEST_RESPONSE_TIMEOUT]["TYPE"] == "UINT"
        assert 8900 <= captured[REQUEST_RESPONSE_TIMEOUT]["VALUE"] <= 9000

    def test_clamped_below_buffer(self):
        handler, captured = self._make_handler()
        handler._mgmt_request_response(b"op", {}, lambda *a: None, timeout=0.4)
        assert captured[REQUEST_RESPONSE_TIMEOUT] == {"TYPE": "UINT", "VALUE": 0}

    def test_associated_link_name_preserved(self):
        handler, captured = self._make_handler()
        handler._mgmt_request_response(b"op", {}, lambda *a: None, timeout=None)
        assert b"associated-link-name" in captured
        assert REQUEST_RESPONSE_TIMEOUT in captured

    def test_sent_on_calls_without_an_associated_link(self):
        # list_sessions passes keep_alive_associated_link=False, starting from an empty map.
        handler, captured = self._make_handler()
        handler._mgmt_request_response(
            b"op",
            {},
            lambda *a: None,
            keep_alive_associated_link=False,
            timeout=None,
        )
        assert captured == {REQUEST_RESPONSE_TIMEOUT: {"TYPE": "UINT", "VALUE": 60000}}


class TestServiceTimeoutResponse:
    """The response half: the service's answer must surface as a retryable
    `OperationTimeoutError`, which rests on `com.microsoft:timeout` in `errorCondition`."""

    @staticmethod
    def _response(condition):
        message = MagicMock()
        message.application_properties = {MGMT_RESPONSE_MESSAGE_ERROR_CONDITION: condition}
        return message

    def test_timeout_condition_raises_retryable_operation_timeout_error(self):
        with pytest.raises(OperationTimeoutError) as exc_info:
            mgmt_handlers.default(408, self._response(ERROR_CODE_TIMEOUT), "The operation timed out.", PyamqpTransport)

        assert exc_info.value._retryable is True

    def test_success_returns_the_value_untouched(self):
        message = self._response(None)
        message.value = {"ok": True}
        assert mgmt_handlers.default(200, message, None, PyamqpTransport) == {"ok": True}

    def test_uamqp_maps_the_same_condition(self):
        # Skip on uamqp itself: the transport module imports without it, but UamqpTransport is not defined.
        pytest.importorskip("uamqp", reason="uamqp not installed")
        from azure.servicebus._transport._uamqp_transport import UamqpTransport

        with pytest.raises(OperationTimeoutError):
            mgmt_handlers.default(
                408,
                self._response(ERROR_CODE_TIMEOUT),
                "The operation timed out.",
                UamqpTransport,
            )


class TestUamqpValueType:
    """uamqp is the one place the value type changes: pyamqp uses a plain dict, uamqp an `AMQPuInt`."""

    def test_transport_supplied_type_is_what_reaches_the_message(self):

        from azure.servicebus._base_handler import BaseHandler

        sentinel = object()
        captured = {}

        def fake_create_mgmt_msg(message, application_properties, config, reply_to, **kwargs):
            captured.update(application_properties)
            return MagicMock()

        handler = BaseHandler.__new__(BaseHandler)
        handler._amqp_transport = MagicMock()
        handler._amqp_transport.create_mgmt_msg = fake_create_mgmt_msg
        handler._amqp_transport.AMQP_UINT_VALUE = lambda ms: sentinel
        handler._amqp_transport.get_handler_link_name = lambda h: "link-1"
        handler._amqp_transport.mgmt_client_request = lambda *args, **kwargs: "response"
        handler._amqp_transport.TIMEOUT_ERROR = TimeoutError
        handler._open = lambda timeout=None: None
        handler._handler = MagicMock()
        handler._config = MagicMock(encoding="UTF-8")
        handler._mgmt_target = "queue/$management"

        handler._mgmt_request_response(b"op", {}, lambda *a: None, timeout=None)
        assert captured[REQUEST_RESPONSE_TIMEOUT] is sentinel

    def test_real_uamqp_type_encodes_in_application_properties(self):
        uamqp = pytest.importorskip("uamqp", reason="uamqp not installed")
        from azure.servicebus._transport._uamqp_transport import UamqpTransport

        value = UamqpTransport.AMQP_UINT_VALUE(get_server_timeout_ms(None))
        assert isinstance(value, uamqp.types.AMQPuInt)

        message = UamqpTransport.create_mgmt_msg(
            message={"operation": "peek"},
            application_properties={REQUEST_RESPONSE_TIMEOUT: value},
            config=MagicMock(encoding="UTF-8"),
            reply_to="queue/$management",
        )

        assert message.encode_message()


class TestAsyncParity:
    """The async management path is a separate implementation and can drift from the sync one."""

    @pytest.mark.asyncio
    async def test_async_management_sets_server_timeout(self):
        from azure.servicebus.aio._base_handler_async import BaseHandler as AsyncBaseHandler

        captured = {}

        def fake_create_mgmt_msg(message, application_properties, config, reply_to, **kwargs):
            captured.clear()
            captured.update(application_properties)
            return MagicMock()

        async def fake_request(*args, **kwargs):
            return "response"

        async def fake_open(timeout=None):
            return None

        handler = AsyncBaseHandler.__new__(AsyncBaseHandler)
        handler._amqp_transport = MagicMock()
        handler._amqp_transport.create_mgmt_msg = fake_create_mgmt_msg
        handler._amqp_transport.AMQP_UINT_VALUE = PyamqpTransport.AMQP_UINT_VALUE
        handler._amqp_transport.get_handler_link_name = lambda h: "link-1"
        handler._amqp_transport.mgmt_client_request_async = fake_request
        handler._amqp_transport.TIMEOUT_ERROR = TimeoutError
        handler._open = fake_open
        handler._handler = MagicMock()
        handler._config = MagicMock(encoding="UTF-8")
        handler._mgmt_target = "queue/$management"

        await handler._mgmt_request_response(b"op", {}, lambda *a: None, timeout=None)
        assert captured[REQUEST_RESPONSE_TIMEOUT] == {"TYPE": "UINT", "VALUE": 60000}

        await handler._mgmt_request_response(b"op", {}, lambda *a: None, timeout=10)
        # Link acquisition is deducted from the attempt, so this is at most 9000.
        assert captured[REQUEST_RESPONSE_TIMEOUT]["TYPE"] == "UINT"
        assert 8900 <= captured[REQUEST_RESPONSE_TIMEOUT]["VALUE"] <= 9000
