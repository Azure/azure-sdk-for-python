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
    @patch("websockets.sync.client.connect")
    def test_websocket_connection_creation(self, mock_connect, mock_url):
        # Setup mocks
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Setup URL mock
        mock_url_instance = MagicMock()
        mock_url_instance.scheme = "wss"
        mock_url_instance.copy_with.return_value = mock_url_instance
        mock_url.return_value = mock_url_instance

        # Test creating a connection
        with self.client.connect(model="test-model") as connection:
            # Verify URL was created correctly
            mock_url.assert_called_with("wss://test-endpoint.com/v1")

            # Verify connect was called with right parameters
            mock_connect.assert_called_once()
            connect_args = mock_connect.call_args

            # Headers should contain Authorization
            self.assertIn("additional_headers", connect_args[1])
            headers = connect_args[1]["additional_headers"]
            self.assertIn("Authorization", headers)
            self.assertEqual(headers["Authorization"], "Bearer test-key")

            # Test sending data
            test_data = {"type": "test.event", "data": "test"}
            connection.send(test_data)

            # Verify send was called correctly
            mock_connection.send.assert_called_with(json.dumps(test_data))

    @patch("websockets.sync.client.connect")
    def test_websocket_options(self, mock_connect):
        # Setup mock
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Create options
        ws_options: WebsocketConnectionOptions = {"max_size": 10 * 1024 * 1024, "compression": "deflate"}

        # Use the options
        with self.client.connect(model="test-model", websocket_connection_options=ws_options) as connection:
            # Verify options were passed to connect
            mock_connect.assert_called_once()
            connect_args = mock_connect.call_args

            # Options should be passed through
            self.assertEqual(connect_args[1]["max_size"], 10 * 1024 * 1024)
            self.assertEqual(connect_args[1]["compression"], "deflate")


if __name__ == "__main__":
    unittest.main()
