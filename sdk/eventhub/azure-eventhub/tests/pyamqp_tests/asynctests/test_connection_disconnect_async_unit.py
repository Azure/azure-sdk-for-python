# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Unit tests for Connection._disconnect() cleanup paths.

Covers the regression where Connection.close() entering its exception handler
set state to END without closing the transport, and the subsequent
_disconnect() call (from the finally block) early-returned and never closed
the transport, leaking the aiohttp ClientSession.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from azure.eventhub._pyamqp.aio._connection_async import Connection
from azure.eventhub._pyamqp.constants import ConnectionState


def _make_connection():
    """Build a Connection without going through __init__ (which opens a real
    transport). Only the attributes touched by _disconnect/close are set."""
    connection = Connection.__new__(Connection)
    connection.state = ConnectionState.START
    connection._transport = MagicMock()
    connection._transport.close = AsyncMock()
    connection._network_trace_params = {
        "amqpConnection": "test",
        "amqpSession": "",
        "amqpLink": "",
    }
    connection._outgoing_endpoints = {}
    connection._transport_closed = False
    return connection


@pytest.mark.asyncio
async def test_disconnect_closes_transport_when_state_already_end():
    """When Connection.close() enters its exception handler it sets state to
    END before calling _disconnect() in the finally block. The previous
    implementation early-returned in that case and never closed the transport.
    """
    connection = _make_connection()
    connection.state = ConnectionState.END

    await connection._disconnect()

    connection._transport.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_disconnect_is_idempotent():
    """_disconnect() may be called more than once (e.g. once from
    _incoming_close and again from Connection.close()'s finally). The transport
    must only be closed once."""
    connection = _make_connection()

    await connection._disconnect()
    await connection._disconnect()

    connection._transport.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_disconnect_sets_state_to_end_when_not_already():
    """The normal _disconnect() path still transitions state to END."""
    connection = _make_connection()
    assert connection.state != ConnectionState.END

    await connection._disconnect()

    assert connection.state == ConnectionState.END
    connection._transport.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_disconnect_swallows_transport_close_errors():
    """Errors from transport.close() must not propagate out of _disconnect() —
    the connection is shutting down and any leaked resource will be GC'd."""
    connection = _make_connection()
    connection._transport.close = AsyncMock(side_effect=RuntimeError("boom"))

    await connection._disconnect()

    connection._transport.close.assert_awaited_once()
