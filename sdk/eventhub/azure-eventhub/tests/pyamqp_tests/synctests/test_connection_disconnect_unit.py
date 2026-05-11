# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Unit tests for Connection._disconnect() cleanup paths (sync).

Mirrors the async tests in tests/pyamqp_tests/asynctests/. See that file for
the full bug description.
"""

from unittest.mock import MagicMock

from azure.eventhub._pyamqp._connection import Connection
from azure.eventhub._pyamqp.constants import ConnectionState


def _make_connection():
    """Build a Connection without going through __init__ (which opens a real
    transport). Only the attributes touched by _disconnect/close are set."""
    connection = Connection.__new__(Connection)
    connection.state = ConnectionState.START
    connection._transport = MagicMock()
    connection._network_trace_params = {
        "amqpConnection": "test",
        "amqpSession": "",
        "amqpLink": "",
    }
    connection._outgoing_endpoints = {}
    connection._transport_closed = False
    return connection


def test_disconnect_closes_transport_when_state_already_end():
    connection = _make_connection()
    connection.state = ConnectionState.END

    connection._disconnect()

    connection._transport.close.assert_called_once()


def test_disconnect_is_idempotent():
    connection = _make_connection()

    connection._disconnect()
    connection._disconnect()

    connection._transport.close.assert_called_once()


def test_disconnect_sets_state_to_end_when_not_already():
    connection = _make_connection()
    assert connection.state != ConnectionState.END

    connection._disconnect()

    assert connection.state == ConnectionState.END
    connection._transport.close.assert_called_once()


def test_disconnect_swallows_transport_close_errors():
    connection = _make_connection()
    connection._transport.close.side_effect = RuntimeError("boom")

    connection._disconnect()

    connection._transport.close.assert_called_once()
