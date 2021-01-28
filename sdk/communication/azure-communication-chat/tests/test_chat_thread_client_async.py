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
    ChatThreadParticipant,
    CommunicationUser,
    ChatMessageType
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
async def test_update_topic():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=204)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    topic = "update topic"
    try:
        await chat_thread_client.update_topic(topic=topic)
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

    create_message_result_id = None
    try:
        content='hello world'
        sender_display_name='sender name'

        create_message_result_id = await chat_thread_client.send_message(
            content,
            sender_display_name=sender_display_name)
    except:
        raised = True

    assert raised == False
    assert create_message_result_id == message_id

@pytest.mark.asyncio
async def test_send_message_w_type():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id='1596823919339'
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=201, json_payload={"id": message_id})
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    create_message_result_id = None

    chat_message_types = [ChatMessageType.TEXT, ChatMessageType.HTML,
                          ChatMessageType.PARTICIPANT_ADDED, ChatMessageType.PARTICIPANT_REMOVED,
                          ChatMessageType.TOPIC_UPDATED,
                          "text", "html", "participant_added", "participant_removed", "topic_updated"]

    for chat_message_type in chat_message_types:
        try:
            content='hello world'
            sender_display_name='sender name'

            create_message_result_id = await chat_thread_client.send_message(
                content,
                chat_message_type=chat_message_type,
                sender_display_name=sender_display_name)
        except:
            raised = True

        assert raised == False
        assert create_message_result_id == message_id

@pytest.mark.asyncio
async def test_send_message_w_invalid_type_throws_error():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id='1596823919339'
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=201, json_payload={"id": message_id})
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    create_message_result_id = None

    chat_message_types = ["ChatMessageType.TEXT", "ChatMessageType.HTML",
                          "ChatMessageType.PARTICIPANT_ADDED", "ChatMessageType.PARTICIPANT_REMOVED",
                          "ChatMessageType.TOPIC_UPDATED"]
    for chat_message_type in chat_message_types:
        try:
            content='hello world'
            sender_display_name='sender name'

            create_message_result_id = await chat_thread_client.send_message(
                content,
                chat_message_type=chat_message_type,
                sender_display_name=sender_display_name)
        except:
            raised = True

        assert raised == True


@pytest.mark.asyncio
async def test_get_message():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id='1596823919339'
    raised = False
    message_str = "Hi I am Bob."

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={
                        "id": message_id,
                        "type": "text",
                        "sequenceId": "3",
                        "version": message_id,
                        "content": {
                            "message": message_str,
                            "topic": "Lunch Chat thread",
                            "participants": [
                                {
                                    "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b",
                                    "displayName": "Bob",
                                    "shareHistoryTime": "2020-10-30T10:50:50Z"
                                }
                            ],
                            "initiator": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"
                        },
                        "senderDisplayName": "Bob",
                        "createdOn": "2021-01-27T01:37:33Z",
                        "senderId": "8:acs:46849534-eb08-4ab7-bde7-c36928cd1547_00000007-e155-1f06-1db7-3a3a0d00004b"
                    })
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    message = None
    try:
        message = await chat_thread_client.get_message(message_id)
    except:
        raised = True

    assert raised == False
    assert message.id == message_id
    assert message.type == ChatMessageType.TEXT
    assert message.content.message == message_str
    assert len(message.content.participants) > 0

@pytest.mark.asyncio
async def test_list_messages():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id='1596823919339'
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={"value": [{
                        "id": message_id,
                        "type": "text",
                        "sequenceId": "3",
                        "version": message_id,
                        "content": {
                            "message": "message_str",
                            "topic": "Lunch Chat thread",
                            "participants": [
                                {
                                    "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b",
                                    "displayName": "Bob",
                                    "shareHistoryTime": "2020-10-30T10:50:50Z"
                                }
                            ],
                            "initiator": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"
                        },
                        "senderDisplayName": "Bob",
                        "createdOn": "2021-01-27T01:37:33Z",
                        "senderId": "8:acs:46849534-eb08-4ab7-bde7-c36928cd1547_00000007-e155-1f06-1db7-3a3a0d00004b"
                    }]})
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
                {
                    "id": "message_id1",
                    "type": "text",
                    "sequenceId": "3",
                    "version": "message_id1",
                    "content": {
                        "message": "message_str",
                        "topic": "Lunch Chat thread",
                        "participants": [
                            {
                                "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b",
                                "displayName": "Bob",
                                "shareHistoryTime": "2020-10-30T10:50:50Z"
                            }
                        ],
                        "initiator": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"
                    },
                    "senderDisplayName": "Bob",
                    "createdOn": "2020-08-17T18:05:44Z",
                    "senderId": "8:acs:46849534-eb08-4ab7-bde7-c36928cd1547_00000007-e155-1f06-1db7-3a3a0d00004b"
                },
                {
                    "id": "message_id2",
                    "type": "text",
                    "sequenceId": "3",
                    "version": "message_id2",
                    "content": {
                        "message": "message_str",
                        "topic": "Lunch Chat thread",
                        "participants": [
                            {
                                "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b",
                                "displayName": "Bob",
                                "shareHistoryTime": "2020-10-30T10:50:50Z"
                            }
                        ],
                        "initiator": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"
                    },
                    "senderDisplayName": "Bob",
                    "createdOn": "2020-08-17T23:13:33Z",
                    "senderId": "8:acs:46849534-eb08-4ab7-bde7-c36928cd1547_00000007-e155-1f06-1db7-3a3a0d00004b"
                }]})
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
        return mock_response(status_code=204)
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
async def test_list_participants():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    participant_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={"value": [{"id": participant_id}]})
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    chat_thread_participants = None
    try:
        chat_thread_participants = chat_thread_client.list_participants()
    except:
        raised = True

    assert raised == False

    items = []
    async for item in chat_thread_participants:
        items.append(item)

    assert len(items) == 1

@pytest.mark.asyncio
async def test_list_participants_with_results_per_page():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    participant_id_1 = "8:acs:9b665d53-8164-4923-ad5d-5e983b07d2e7_00000006-5399-552c-b274-5a3a0d0000dc"
    participant_id_2 = "8:acs:9b665d53-8164-4923-ad5d-5e983b07d2e7_00000006-9d32-35c9-557d-5a3a0d0002f1"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={
                "value": [
                    {"id": participant_id_1},
                    {"id": participant_id_2}
                ]})
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    chat_thread_participants = None
    try:
        chat_thread_participants = chat_thread_client.list_participants(results_per_page=2)
    except:
        raised = True

    assert raised == False

    items = []
    async for item in chat_thread_participants:
        items.append(item)

    assert len(items) == 2


@pytest.mark.asyncio
async def test_add_participant():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    new_participant_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=201)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    new_participant = ChatThreadParticipant(
            user=CommunicationUser(new_participant_id),
            display_name='name',
            share_history_time=datetime.utcnow())

    try:
        await chat_thread_client.add_participant(new_participant)
    except:
        raised = True

    assert raised == False

@pytest.mark.asyncio
async def test_add_participants():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    new_participant_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=201)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    new_participant = ChatThreadParticipant(
            user=CommunicationUser(new_participant_id),
            display_name='name',
            share_history_time=datetime.utcnow())
    participants = [new_participant]

    try:
        await chat_thread_client.add_participants(participants)
    except:
        raised = True

    assert raised == False

@pytest.mark.asyncio
async def test_remove_participant():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    participant_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=204)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    try:
        await chat_thread_client.remove_participant(CommunicationUser(participant_id))
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
        return mock_response(status_code=200)
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

@pytest.mark.asyncio
async def test_list_read_receipts_with_results_per_page():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id_1 = "1596823919339"
    message_id_2 = "1596823919340"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={
            "value": [
                {"chatMessageId": message_id_1},
                {"chatMessageId": message_id_2}
            ]})
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    read_receipts = None
    try:
        read_receipts = chat_thread_client.list_read_receipts(results_per_page=2)
    except:
        raised = True

    assert raised == False

    items = []
    async for item in read_receipts:
        items.append(item)

    assert len(items) == 2

@pytest.mark.asyncio
async def test_list_read_receipts_with_results_per_page_and_skip():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id_1 = "1596823919339"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={
            "value": [
                {"chatMessageId": message_id_1}
            ]})
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    read_receipts = None
    try:
        read_receipts = chat_thread_client.list_read_receipts(results_per_page=1, skip=1)
    except:
        raised = True

    assert raised == False

    items = []
    async for item in read_receipts:
        items.append(item)

    assert len(items) == 1
