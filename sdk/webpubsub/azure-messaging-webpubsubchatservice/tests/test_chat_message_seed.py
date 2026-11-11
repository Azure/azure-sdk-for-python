# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from aiohttp import WSMsgType

from chat_message_seed import (
    create_chat_message_async,
    verify_chat_connection_async,
)


class _FakeWebSocket:
    def __init__(self, failing_event=None):
        self.failing_event = failing_event
        self.sent_messages = []
        self.closed = False
        self._connected = False

    async def receive(self):
        if not self._connected:
            self._connected = True
            data = {"type": "system", "event": "connected"}
        else:
            request = self.sent_messages[-1]
            succeeded = request["event"] != self.failing_event
            data = {
                "type": "invokeResponse",
                "invocationId": request["invocationId"],
                "success": succeeded,
            }
            if not succeeded:
                data["error"] = {"name": "Forbidden", "message": "Denied"}
        return SimpleNamespace(type=WSMsgType.TEXT, data=json.dumps(data))

    async def send_str(self, data):
        self.sent_messages.append(json.loads(data))

    async def close(self):
        self.closed = True


class _FakeClientSession:
    def __init__(self, web_socket):
        self.web_socket = web_socket
        self.closed = False
        self.connection = None

    async def ws_connect(self, url, **kwargs):
        self.connection = (url, kwargs)
        return self.web_socket

    async def close(self):
        self.closed = True


class ChatMessageSeedTest(unittest.IsolatedAsyncioTestCase):
    async def test_verify_chat_connection_logs_in(self):
        web_socket = _FakeWebSocket()
        session = _FakeClientSession(web_socket)

        with patch("chat_message_seed.ClientSession", return_value=session):
            await verify_chat_connection_async("wss://example.test/client")

        self.assertEqual(
            session.connection,
            (
                "wss://example.test/client",
                {"protocols": ("json.webpubsub.azure.v1",)},
            ),
        )
        self.assertEqual(
            [message["event"] for message in web_socket.sent_messages],
            ["chat.login"],
        )
        self.assertTrue(web_socket.closed)
        self.assertTrue(session.closed)

    async def test_create_chat_message_logs_in_then_sends_to_conversation(self):
        web_socket = _FakeWebSocket()
        session = _FakeClientSession(web_socket)

        with patch("chat_message_seed.ClientSession", return_value=session):
            await create_chat_message_async("wss://example.test/client", "conversation-id", "hello")

        self.assertEqual(
            [message["event"] for message in web_socket.sent_messages],
            ["chat.login", "chat.sendTextMessage"],
        )
        self.assertEqual(web_socket.sent_messages[0]["dataType"], "text")
        self.assertEqual(web_socket.sent_messages[0]["data"], "")
        self.assertEqual(
            web_socket.sent_messages[1]["data"],
            {
                "conversation": {"conversationId": "conversation-id"},
                "content": "hello",
            },
        )
        self.assertTrue(web_socket.closed)
        self.assertTrue(session.closed)

    async def test_create_chat_message_surfaces_invocation_failure(self):
        web_socket = _FakeWebSocket(failing_event="chat.sendTextMessage")
        session = _FakeClientSession(web_socket)

        with patch("chat_message_seed.ClientSession", return_value=session):
            with self.assertRaisesRegex(RuntimeError, "chat.sendTextMessage invocation failed"):
                await create_chat_message_async("wss://example.test/client", "conversation-id", "hello")

        self.assertTrue(web_socket.closed)
        self.assertTrue(session.closed)


if __name__ == "__main__":
    unittest.main()
