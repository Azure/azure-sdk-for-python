import pytest
import asyncio
from unittest.mock import patch

import aiohttp
from azure.eventhub._pyamqp.aio._transport_async import WebSocketTransportAsync


# class WebsocketException(unittest.TestCase):
async def test_websocket_aiohttp_exception():
    with patch.object(aiohttp.ClientSession,'ws_connect', side_effect=aiohttp.ClientOSError):
        transport = WebSocketTransportAsync(host="my_host")
        with pytest.raises(ConnectionError):
            await transport.connect()
