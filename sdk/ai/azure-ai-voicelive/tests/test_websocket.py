# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import unittest
from unittest.mock import MagicMock, patch
import json

from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive import VoiceLiveClient, WebsocketConnectionOptions


class TestVoiceLiveWebSocket(unittest.TestCase):

    def setUp(self):
        self.client = VoiceLiveClient(credential=AzureKeyCredential("test-key"), endpoint="wss://test-endpoint.com/v1")

    @patch("azure.ai.voicelive._patch.httpx.URL")
    @patch("aiohttp.ClientSession.ws_connect")
    def test_websocket_connection_creation(self, mock_ws_connect, mock_url):
        # Setup mocks
        mock_connection = MagicMock()
        mock_ws_connect.return_value = mock_connection

        # Setup URL mock
        mock_url_instance = MagicMock()
        mock_url_instance.scheme = "wss"
        mock_url_instance.copy_with.return_value = mock_url_instance
        mock_url.return_value = mock_url_instance

        # Mock the asyncio parts
        with patch("asyncio.new_event_loop") as mock_loop:
            mock_loop.return_value.run_until_complete.return_value = (MagicMock(), mock_connection)
            
            # Test creating a connection
            with self.client.connect(model="test-model") as connection:
                # Verify URL was created correctly
                mock_url.assert_called_with("wss://test-endpoint.com/v1")

                # Verify connect was called with right parameters
                mock_ws_connect.assert_called_once()
                connect_args = mock_ws_connect.call_args

                # Headers should contain api-key
                self.assertIn("headers", connect_args[1])
                headers = connect_args[1]["headers"]
                self.assertIn("api-key", headers)
                self.assertEqual(headers["api-key"], "test-key")

                # Test sending data
                test_data = {"type": "test.event", "data": "test"}
                connection.send(test_data)

                # Verify send was called with JSON string
                connection._connection.send.assert_called_once()

    @patch("aiohttp.ClientSession.ws_connect")
    def test_websocket_options(self, mock_ws_connect):
        # Setup mock
        mock_connection = MagicMock()
        mock_ws_connect.return_value = mock_connection

        # Create options
        ws_options: WebsocketConnectionOptions = {"max_msg_size": 10 * 1024 * 1024, "compression": True}

        # Mock the asyncio parts
        with patch("asyncio.new_event_loop") as mock_loop:
            mock_loop.return_value.run_until_complete.return_value = (MagicMock(), mock_connection)
            
            # Use the options
            with self.client.connect(model="test-model", websocket_connection_options=ws_options) as connection:
                # Verify options were passed to connect
                mock_ws_connect.assert_called_once()
                connect_args = mock_ws_connect.call_args

                # Options should be passed through
                self.assertEqual(connect_args[1]["max_msg_size"], 10 * 1024 * 1024)
                self.assertEqual(connect_args[1]["compress"], True)


if __name__ == "__main__":
    unittest.main()