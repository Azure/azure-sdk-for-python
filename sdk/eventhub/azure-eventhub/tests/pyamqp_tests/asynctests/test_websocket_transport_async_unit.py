# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Unit tests for WebSocketTransportAsync covering close/connect cleanup paths.

These tests do not require a live Event Hubs instance; aiohttp is mocked so that
the cleanup behavior of WebSocketTransportAsync can be exercised in isolation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from azure.eventhub._pyamqp.aio._transport_async import WebSocketTransportAsync


def _make_transport():
    transport = WebSocketTransportAsync("example.servicebus.windows.net")
    transport.network_trace_params = {}
    return transport


@pytest.mark.asyncio
async def test_close_calls_session_close_even_if_sock_close_raises():
    """If sock.close() raises, the aiohttp ClientSession must still be closed.

    Regression test for the leak where WebSocketTransportAsync.close() called
    self.sock.close() and self.session.close() sequentially without try/except,
    leaving the aiohttp ClientSession unclosed when sock.close() raised.
    """
    transport = _make_transport()
    sock = MagicMock()
    sock.close = AsyncMock(side_effect=RuntimeError("ws already closed"))
    session = MagicMock()
    session.close = AsyncMock()
    transport.sock = sock
    transport.session = session
    transport.connected = True

    await transport.close()

    sock.close.assert_awaited_once()
    session.close.assert_awaited_once()
    assert transport.connected is False


@pytest.mark.asyncio
async def test_close_handles_none_sock_and_session():
    """close() must not raise if sock/session were never assigned."""
    transport = _make_transport()
    transport.sock = None
    transport.session = None
    transport.connected = True

    await transport.close()

    assert transport.connected is False


@pytest.mark.asyncio
async def test_close_swallows_session_close_errors():
    """Errors from session.close() must not propagate, mirroring the sibling
    AsyncTransport.close() pattern which logs and continues."""
    transport = _make_transport()
    sock = MagicMock()
    sock.close = AsyncMock()
    session = MagicMock()
    session.close = AsyncMock(side_effect=RuntimeError("aiohttp boom"))
    transport.sock = sock
    transport.session = session
    transport.connected = True

    await transport.close()

    session.close.assert_awaited_once()
    assert transport.connected is False


@pytest.mark.asyncio
async def test_connect_closes_previous_session_on_reconnect():
    """When connect() is called and a previous session already exists (reconnect
    path), the previous session must be closed before a new one is created.
    """
    from aiohttp import ClientConnectorError

    transport = _make_transport()
    previous_session = MagicMock()
    previous_session.close = AsyncMock()
    transport.session = previous_session

    # Force connect() to fail fast after the previous-session cleanup so we can
    # assert the cleanup happened. ClientConnectorError is one of the existing
    # handled exception types in connect().
    fake_session = MagicMock()
    fake_session.ws_connect = AsyncMock(
        side_effect=ClientConnectorError(MagicMock(), OSError("nope"))
    )
    fake_session.close = AsyncMock()

    with patch(
        "aiohttp.ClientSession", return_value=fake_session
    ), pytest.raises(ConnectionError):
        await transport.connect()

    previous_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_closes_new_session_on_client_connector_error():
    """When ws_connect raises ClientConnectorError, the newly created
    ClientSession must be closed before the error is re-raised."""
    from aiohttp import ClientConnectorError

    transport = _make_transport()
    transport.session = None

    fake_session = MagicMock()
    fake_session.ws_connect = AsyncMock(
        side_effect=ClientConnectorError(MagicMock(), OSError("nope"))
    )
    fake_session.close = AsyncMock()

    with patch(
        "aiohttp.ClientSession", return_value=fake_session
    ), pytest.raises(ConnectionError):
        await transport.connect()

    fake_session.close.assert_awaited_once()
    assert transport.session is None


@pytest.mark.asyncio
async def test_connect_closes_new_session_on_unexpected_exception():
    """When ws_connect raises something other than ClientConnectorError, the
    newly created session must still be closed before the exception
    propagates."""
    transport = _make_transport()
    transport.session = None

    fake_session = MagicMock()
    fake_session.ws_connect = AsyncMock(side_effect=RuntimeError("unexpected"))
    fake_session.close = AsyncMock()

    with patch(
        "aiohttp.ClientSession", return_value=fake_session
    ), pytest.raises(RuntimeError):
        await transport.connect()

    fake_session.close.assert_awaited_once()
    assert transport.session is None
