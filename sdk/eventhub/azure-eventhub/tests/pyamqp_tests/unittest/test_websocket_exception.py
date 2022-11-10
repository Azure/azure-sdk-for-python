import unittest
import aiohttp
from mock import patch
from azure.eventhub._pyamqp.aio._transport_async import WebSocketTransportAsync


class WebsocketException(unittest.TestCase):

    @patch('aiohttp.client_ws.ClientWebSocketResponse.receive_bytes')
    async def test_websocket_exception_async(self, receive_bytes):
        receive_bytes.raises(aiohttp.ClientOSError)
        web_transport = WebSocketTransportAsync("my_host")
        self.assertRaises(ConnectionError, web_transport._read(1,[]))
    