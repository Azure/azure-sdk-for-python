import pytest
import asyncio
from unittest.mock import patch

import aiohttp
from azure.eventhub._pyamqp.aio._transport_async import WebSocketTransportAsync


# class WebsocketException(unittest.TestCase):
@pytest.mark.asyncio
async def test_websocket_aiohttp_exception_async():
    with patch.object(aiohttp.ClientSession, "ws_connect", side_effect=aiohttp.ClientOSError):
        transport = WebSocketTransportAsync(host="my_host")
        with pytest.raises(aiohttp.ClientOSError):
            await transport.connect()
