import unittest
import pytest
try:
    from unittest import mock
except ImportError:
    import mock

import aiohttp
from azure.eventhub._pyamqp.aio._transport_async import WebSocketTransportAsync


class WebsocketException(unittest.TestCase):

    @mock.patch('azure.eventhub._pyamqp.aio.transport_async.WebSocketTransportAsync.ws._receive_bytes')
    async def test_websocket_exception_async(self, receive_bytes):
        receive_bytes.raises(aiohttp.ClientOSError)
        web_transport = WebSocketTransportAsync("my_host")
        self.assertRaises(ConnectionError, web_transport._read(1,[]))
    