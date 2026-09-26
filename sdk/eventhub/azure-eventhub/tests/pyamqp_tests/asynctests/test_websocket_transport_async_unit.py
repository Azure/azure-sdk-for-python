# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Unit tests for WebSocketTransportAsync covering close/connect cleanup paths.

These tests do not require a live Event Hubs instance; aiohttp is mocked so that
the cleanup behavior of WebSocketTransportAsync can be exercised in isolation.
"""

import asyncio
import ssl

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

@pytest.mark.asyncio
async def test_connect_reconnect_with_already_converted_ssl_opts():
    """A reconnect must not fail inside _build_ssl_opts when self.sslopts is
    already an SSLContext (converted by the previous connect), and the previous
    session must still be closed."""
    from aiohttp import ClientConnectorError

    transport = _make_transport()
    # Simulate the state left behind by a previous connect(): sslopts was
    # replaced with the converted SSLContext and a session is still assigned.
    transport.sslopts = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    previous_session = MagicMock()
    previous_session.close = AsyncMock()
    transport.session = previous_session

    fake_session = MagicMock()
    fake_session.ws_connect = AsyncMock(
        side_effect=ClientConnectorError(MagicMock(), OSError("nope"))
    )
    fake_session.close = AsyncMock()

    with patch(
        "aiohttp.ClientSession", return_value=fake_session
    ), pytest.raises(ConnectionError):
        await transport.connect()

    # No TypeError from `"context" in sslopts`; the previous session was closed.
    previous_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_closes_session_on_cancellation():
    """Cancellation during ws_connect() must close the new ClientSession and
    clear the reference, while CancelledError still propagates to the caller."""
    transport = _make_transport()
    transport.session = None

    fake_session = MagicMock()
    fake_session.ws_connect = AsyncMock(side_effect=asyncio.CancelledError())
    fake_session.close = AsyncMock()

    with patch(
        "aiohttp.ClientSession", return_value=fake_session
    ), pytest.raises(asyncio.CancelledError):
        await transport.connect()

    fake_session.close.assert_awaited_once()
    assert transport.session is None


@pytest.mark.asyncio
async def test_close_cleans_up_when_sock_close_is_cancelled():
    """Cancellation while awaiting sock.close() must still run session cleanup
    and reset state, while CancelledError propagates to the caller."""
    transport = _make_transport()
    sock = MagicMock()
    sock.close = AsyncMock(side_effect=asyncio.CancelledError())
    session = MagicMock()
    session.close = AsyncMock()
    transport.sock = sock
    transport.session = session
    transport.connected = True

    with pytest.raises(asyncio.CancelledError):
        await transport.close()

    sock.close.assert_awaited_once()
    session.close.assert_awaited_once()
    assert transport.sock is None
    assert transport.session is None
    assert transport.connected is False


@pytest.mark.asyncio
async def test_close_session_safely_clears_reference_before_close():
    """If session.close() itself is cancelled, the transport must not retain
    the reference: clearing it first guarantees no leak even though the
    CancelledError propagates."""
    transport = _make_transport()
    session = MagicMock()
    session.close = AsyncMock(side_effect=asyncio.CancelledError())
    transport.session = session

    with pytest.raises(asyncio.CancelledError):
        await transport._close_session_safely()

    session.close.assert_awaited_once()
    assert transport.session is None
