# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import asyncio
import json
import time
import uuid

from aiohttp import ClientSession, ClientTimeout, WSMsgType


_TIMEOUT = 30
_SUBPROTOCOL = "json.webpubsub.azure.v1"


async def _receive_message(web_socket, predicate, description):
    deadline = time.monotonic() + _TIMEOUT
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(f"Timed out waiting for {description}.")
        raw_message = await asyncio.wait_for(web_socket.receive(), remaining)
        if raw_message.type == WSMsgType.ERROR:
            raise RuntimeError(f"WebSocket failed while waiting for {description}.") from web_socket.exception()
        if raw_message.type in (
            WSMsgType.CLOSE,
            WSMsgType.CLOSED,
            WSMsgType.CLOSING,
        ):
            raise RuntimeError(f"Connection closed while waiting for {description}.")
        if raw_message.type != WSMsgType.TEXT:
            continue
        message = json.loads(raw_message.data)
        if isinstance(message, dict) and predicate(message):
            return message


async def _invoke(web_socket, event_name, data_type, data):
    invocation_id = str(uuid.uuid4())
    await web_socket.send_str(
        json.dumps(
            {
                "type": "invoke",
                "invocationId": invocation_id,
                "target": "event",
                "event": event_name,
                "dataType": data_type,
                "data": data,
            },
            separators=(",", ":"),
        )
    )
    response = await _receive_message(
        web_socket,
        lambda message: message.get("type") == "invokeResponse" and message.get("invocationId") == invocation_id,
        f"{event_name} invocation response",
    )
    if not response.get("success"):
        raise RuntimeError(f"{event_name} invocation failed: {response}")
    return response.get("data")


async def _connect_and_login(client_access_url):
    session = ClientSession(timeout=ClientTimeout(total=_TIMEOUT))
    web_socket = None
    try:
        web_socket = await session.ws_connect(
            client_access_url,
            protocols=(_SUBPROTOCOL,),
        )
        await _receive_message(
            web_socket,
            lambda message: message.get("type") == "system" and message.get("event") == "connected",
            "connected event",
        )
        await _invoke(web_socket, "chat.login", "text", "")
        return session, web_socket
    except BaseException:
        if web_socket is not None:
            await web_socket.close()
        await session.close()
        raise


async def create_chat_message_async(client_access_url, conversation_id, content):
    session, web_socket = await _connect_and_login(client_access_url)
    try:
        await _invoke(
            web_socket,
            "chat.sendTextMessage",
            "json",
            {
                "conversation": {"conversationId": conversation_id},
                "content": content,
            },
        )
    finally:
        await web_socket.close()
        await session.close()


def create_chat_message(client_access_url, conversation_id, content):
    asyncio.run(create_chat_message_async(client_access_url, conversation_id, content))


async def verify_chat_connection_async(client_access_url):
    session, web_socket = await _connect_and_login(client_access_url)
    try:
        return
    finally:
        await web_socket.close()
        await session.close()


def verify_chat_connection(client_access_url):
    asyncio.run(verify_chat_connection_async(client_access_url))
