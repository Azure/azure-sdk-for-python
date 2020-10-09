# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.credentials import AccessToken
from datetime import datetime
from msrest.serialization import TZ_UTC
from azure.communication.chat.aio import ChatThreadClient
from azure.communication.chat import (
    ChatMessagePriority,
    ChatThreadMember,
    CommunicationUser,
)
from unittest_helpers import mock_response
from azure.core.exceptions import HttpResponseError

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

import pytest

credential = Mock()
credential.get_token = Mock(return_value=AccessToken("some_token", datetime.now().replace(tzinfo=TZ_UTC)))

@pytest.mark.asyncio
async def test_update_thread():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    topic = "update topic"
    try:
        await chat_thread_client.update_thread(topic=topic)
    except:
        raised = True

    assert raised == False

@pytest.mark.asyncio
async def test_send_message():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id='1596823919339'
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=201, json_payload={"id": message_id})
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    create_message_result = None
    try:
        priority=ChatMessagePriority.NORMAL
        content='hello world'
        sender_display_name='sender name'

        create_message_result = await chat_thread_client.send_message(
            content,
            priority=priority,
            sender_display_name=sender_display_name)
    except:
        raised = True

    assert raised == False
    assert create_message_result.id == message_id

@pytest.mark.asyncio
async def test_get_message():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id='1596823919339'
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={"id": message_id})
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    message = None
    try:
        message = await chat_thread_client.get_message(message_id)
    except:
        raised = True

    assert raised == False
    assert message.id == message_id

@pytest.mark.asyncio
async def test_list_messages():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id='1596823919339'
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={"value": [{"id": message_id}]})
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    chat_messages = None
    try:
        chat_messages = chat_thread_client.list_messages(results_per_page=1)
    except:
        raised = True

    assert raised == False

    items = []
    async for item in chat_messages:
        items.append(item)

    assert len(items) == 1
    assert items[0].id == message_id


@pytest.mark.asyncio
async def test_list_messages_with_start_time():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={
            "value": [
                {"id": "message_id1", "createdOn": "2020-08-17T18:05:44Z"},
                {"id": "message_id2", "createdOn": "2020-08-17T23:13:33Z"}
                ]})
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    chat_messages = None
    try:
        chat_messages = chat_thread_client.list_messages(
            start_time=datetime(2020, 8, 17, 18, 0, 0)
        )
    except:
        raised = True

    assert raised == False

    items = []
    async for item in chat_messages:
        items.append(item)

    assert len(items) == 2

@pytest.mark.asyncio
async def test_update_message():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id='1596823919339'
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    try:
        content = "updated message content"
        await chat_thread_client.update_message(message_id, content=content)
    except:
        raised = True

    assert raised == False

@pytest.mark.asyncio
async def test_delete_message():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id='1596823919339'
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=204)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    try:
        await chat_thread_client.delete_message(message_id)
    except:
        raised = True

    assert raised == False

@pytest.mark.asyncio
async def test_list_members():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    member_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={"value": [{"id": member_id}]})
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    chat_thread_members = None
    try:
        chat_thread_members = chat_thread_client.list_members()
    except:
        raised = True

    assert raised == False

    items = []
    async for item in chat_thread_members:
        items.append(item)

    assert len(items) == 1

@pytest.mark.asyncio
async def test_add_members():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    new_member_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=207)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    new_member = ChatThreadMember(
            user=CommunicationUser(new_member_id),
            display_name='name',
            share_history_time=datetime.utcnow())
    members = [new_member]

    try:
        await chat_thread_client.add_members(members)
    except:
        raised = True

    assert raised == False

@pytest.mark.asyncio
async def test_remove_member():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    member_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=204)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    try:
        await chat_thread_client.remove_member(CommunicationUser(member_id))
    except:
        raised = True

    assert raised == False

@pytest.mark.asyncio
async def test_send_typing_notification():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    try:
        await chat_thread_client.send_typing_notification()
    except:
        raised = True

    assert raised == False

@pytest.mark.asyncio
async def test_send_read_receipt():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id="1596823919339"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=201)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    try:
        await chat_thread_client.send_read_receipt(message_id)
    except:
        raised = True

    assert raised == False

@pytest.mark.asyncio
async def test_list_read_receipts():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id="1596823919339"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={"value": [{"chatMessageId": message_id}]})
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    read_receipts = None
    try:
        read_receipts = chat_thread_client.list_read_receipts()
    except:
        raised = True

    assert raised == False

    items = []
    async for item in read_receipts:
        items.append(item)

    assert len(items) == 1
