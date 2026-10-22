import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from aiohttp import ClientConnectorError
import pytest

from azure.eventhub._pyamqp.aio._transport_async import WebSocketTransportAsync


def _client_connector_error():
    connection_key = MagicMock(host="example.servicebus.windows.net", port=443, ssl=True)
    return ClientConnectorError(connection_key, OSError("connection failed"))


def _session_with_connect_error(error):
    session = MagicMock()
    session.ws_connect = AsyncMock(side_effect=error)
    session.close = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_websocket_aiohttp_exception_async():
    import aiohttp

    with patch.object(aiohttp.ClientSession, "ws_connect", side_effect=aiohttp.ClientOSError):
        transport = WebSocketTransportAsync(host="my_host")
        with pytest.raises(aiohttp.ClientOSError):
            await transport.connect()


@pytest.mark.asyncio
async def test_connect_closes_session_on_client_connector_error():
    transport = WebSocketTransportAsync("example.servicebus.windows.net")
    session = _session_with_connect_error(_client_connector_error())

    with patch("aiohttp.ClientSession", return_value=session):
        with pytest.raises(ConnectionError):
            await transport.connect()

    session.close.assert_awaited_once()
    assert transport.session is None


@pytest.mark.asyncio
async def test_connect_closes_session_on_unexpected_error():
    transport = WebSocketTransportAsync("example.servicebus.windows.net")
    session = _session_with_connect_error(RuntimeError("unexpected"))

    with patch("aiohttp.ClientSession", return_value=session):
        with pytest.raises(RuntimeError, match="unexpected"):
            await transport.connect()

    session.close.assert_awaited_once()
    assert transport.session is None


@pytest.mark.asyncio
async def test_connect_closes_session_on_cancelled_error():
    transport = WebSocketTransportAsync("example.servicebus.windows.net")
    session = _session_with_connect_error(asyncio.CancelledError())

    with patch("aiohttp.ClientSession", return_value=session):
        with pytest.raises(asyncio.CancelledError):
            await transport.connect()

    session.close.assert_awaited_once()
    assert transport.session is None


@pytest.mark.asyncio
async def test_connect_preserves_error_when_session_cleanup_fails():
    transport = WebSocketTransportAsync("example.servicebus.windows.net")
    session = _session_with_connect_error(RuntimeError("connect failed"))
    session.close = AsyncMock(side_effect=RuntimeError("cleanup failed"))

    with patch("aiohttp.ClientSession", return_value=session):
        with pytest.raises(RuntimeError, match="connect failed"):
            await transport.connect()

    session.close.assert_awaited_once()
    assert transport.session is None


@pytest.mark.asyncio
async def test_connect_closes_previous_session_before_replacing_it():
    transport = WebSocketTransportAsync("example.servicebus.windows.net")
    previous_session = MagicMock()
    previous_session.close = AsyncMock()
    transport.session = previous_session

    sock = MagicMock()
    sock.close = AsyncMock()
    session = MagicMock()
    session.ws_connect = AsyncMock(return_value=sock)
    session.close = AsyncMock()

    with patch("aiohttp.ClientSession", return_value=session):
        await transport.connect()

    previous_session.close.assert_awaited_once()
    await transport.close()


@pytest.mark.asyncio
async def test_close_closes_session_when_socket_close_fails():
    transport = WebSocketTransportAsync("example.servicebus.windows.net")
    transport.connected = True
    transport.sock = MagicMock()
    transport.sock.close = AsyncMock(side_effect=RuntimeError("socket close failed"))
    session = MagicMock()
    session.close = AsyncMock()
    transport.session = session

    with pytest.raises(RuntimeError, match="socket close failed"):
        await transport.close()

    session.close.assert_awaited_once()
    assert transport.sock is None
    assert transport.session is None
    assert transport.connected is False
