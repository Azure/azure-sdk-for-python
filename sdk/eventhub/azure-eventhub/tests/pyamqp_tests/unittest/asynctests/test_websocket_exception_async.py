import sys
import pytest
import asyncio
from unittest.mock import patch
from azure.eventhub._pyamqp.aio._transport_async import WebSocketTransportAsync


# class WebsocketException(unittest.TestCase):
@pytest.mark.asyncio
@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="Python 3.8 or less is not supported for this test"
)
async def test_websocket_aiohttp_exception_async():
    import aiohttp
    with patch.object(aiohttp.ClientSession, "ws_connect", side_effect=aiohttp.ClientOSError):
        transport = WebSocketTransportAsync(host="my_host")
        with pytest.raises(aiohttp.ClientOSError):
            await transport.connect()
