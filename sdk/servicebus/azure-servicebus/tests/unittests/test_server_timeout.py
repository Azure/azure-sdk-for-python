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

import pytest

from azure.servicebus._common.constants import REQUEST_RESPONSE_TIMEOUT
from azure.servicebus._common.utils import get_server_timeout_ms
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport


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
        handler._open = lambda: None
        handler._handler = MagicMock()
        handler._config = MagicMock(encoding="UTF-8")
        handler._mgmt_target = "queue/$management"
        return handler, captured

    def test_default_sent_when_caller_gave_no_timeout(self):
        # The gap this closes: without a caller timeout the service previously received no bound at
        # all.
        handler, captured = self._make_handler()
        handler._mgmt_request_response(b"op", {}, lambda *a: None, timeout=None)
        assert captured[REQUEST_RESPONSE_TIMEOUT] == {"TYPE": "UINT", "VALUE": 60000}

    def test_remaining_time_less_buffer_sent(self):
        handler, captured = self._make_handler()
        handler._mgmt_request_response(b"op", {}, lambda *a: None, timeout=10)
        assert captured[REQUEST_RESPONSE_TIMEOUT] == {"TYPE": "UINT", "VALUE": 9000}

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
        # Operations such as list_sessions pass `keep_alive_associated_link=False` and start from an
        # empty property map; they must still be bounded.
        handler, captured = self._make_handler()
        handler._mgmt_request_response(
            b"op",
            {},
            lambda *a: None,
            keep_alive_associated_link=False,
            timeout=None,
        )
        assert captured == {REQUEST_RESPONSE_TIMEOUT: {"TYPE": "UINT", "VALUE": 60000}}


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

        async def fake_open():
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
        assert captured[REQUEST_RESPONSE_TIMEOUT] == {"TYPE": "UINT", "VALUE": 9000}
