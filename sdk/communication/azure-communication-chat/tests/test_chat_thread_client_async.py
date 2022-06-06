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
    ChatParticipant,
    ChatMessageType
)
from azure.communication.chat._shared.models import(
    CommunicationUserIdentifier
)
from unittest_helpers import mock_response
from azure.core.exceptions import HttpResponseError

from unittest.mock import Mock, patch

import pytest
import time
import calendar

def _convert_datetime_to_utc_int(input):
    return int(calendar.timegm(input.utctimetuple()))


async def mock_get_token():
    return AccessToken("some_token", _convert_datetime_to_utc_int(datetime.now().replace(tzinfo=TZ_UTC)))

credential = Mock(get_token=mock_get_token)


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
        metadata={ "tags": "tag" }

        create_message_result = await chat_thread_client.send_message(
            content,
            sender_display_name=sender_display_name,
            metadata=metadata)
        create_message_result_id = create_message_result.id
    except:
        raised = True

    assert raised == False
    assert create_message_result_id == message_id

@pytest.mark.asyncio
async def test_send_message_w_type():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id='1596823919339'
    raised = False
    message_str = "Hi I am Bob."

    create_message_result_id = None

    chat_message_types = [ChatMessageType.TEXT, ChatMessageType.HTML, "text", "html"]

    for chat_message_type in chat_message_types:

        async def mock_send(*_, **__):
            return mock_response(status_code=201, json_payload={
                    "id": message_id,
                    "type": chat_message_type,
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

        try:
            content='hello world'
            sender_display_name='sender name'

            create_message_result = await chat_thread_client.send_message(
                content,
                chat_message_type=chat_message_type,
                sender_display_name=sender_display_name)
            create_message_result_id = create_message_result.id
        except:
            raised = True

        assert raised == False
        assert create_message_result_id == message_id

@pytest.mark.asyncio
async def test_send_message_w_invalid_type_throws_error():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id='1596823919339'
    raised = False

    # the payload is irrelevant - it'll fail before
    async def mock_send(*_, **__):
        return mock_response(status_code=201, json_payload={"id": message_id})
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    create_message_result_id = None

    chat_message_types = [ChatMessageType.PARTICIPANT_ADDED, ChatMessageType.PARTICIPANT_REMOVED,
                              ChatMessageType.TOPIC_UPDATED, "participant_added", "participant_removed", "topic_updated",
                              "ChatMessageType.TEXT", "ChatMessageType.HTML",
                              "ChatMessageType.PARTICIPANT_ADDED", "ChatMessageType.PARTICIPANT_REMOVED",
                              "ChatMessageType.TOPIC_UPDATED"]

    for chat_message_type in chat_message_types:
        try:
            content='hello world'
            sender_display_name='sender name'

            create_message_result = await chat_thread_client.send_message(
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
                                    "communicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                                    "displayName": "Bob",
                                    "shareHistoryTime": "2020-10-30T10:50:50Z"
                                }
                            ],
                            "initiatorCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}}
                        },
                        "senderDisplayName": "Bob",
                        "createdOn": "2021-01-27T01:37:33Z",
                        "senderCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                        "deletedOn": "2021-01-27T01:37:33Z",
                        "editedOn": "2021-01-27T01:37:33Z",
                        "metadata": {
                            "tags": "tag"
                        }
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
    assert message.metadata["tags"] == "tag"
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
                                    "communicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                                    "displayName": "Bob",
                                    "shareHistoryTime": "2020-10-30T10:50:50Z"
                                }
                            ],
                            "initiatorCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}}
                        },
                        "senderDisplayName": "Bob",
                        "createdOn": "2021-01-27T01:37:33Z",
                        "senderCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                        "deletedOn": "2021-01-27T01:37:33Z",
                        "editedOn": "2021-01-27T01:37:33Z"
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
                    "id": "message_id_1",
                    "type": "text",
                    "sequenceId": "3",
                    "version": "message_id_1",
                    "content": {
                        "message": "message_str",
                        "topic": "Lunch Chat thread",
                        "participants": [
                            {
                                "communicationIdentifier": {"rawId": "string", "communicationUser": {
                                    "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                                "displayName": "Bob",
                                "shareHistoryTime": "2020-10-30T10:50:50Z"
                            }
                        ],
                        "initiatorCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}}
                    },
                    "senderDisplayName": "Bob",
                    "createdOn": "2021-01-27T01:37:33Z",
                    "senderCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                        "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                    "deletedOn": "2021-01-27T01:37:33Z",
                    "editedOn": "2021-01-27T01:37:33Z"
                },
                {
                    "id": "message_id_2",
                    "type": "text",
                    "sequenceId": "3",
                    "version": "message_id_2",
                    "content": {
                        "message": "message_str",
                        "topic": "Lunch Chat thread",
                        "participants": [
                            {
                                "communicationIdentifier": {"rawId": "string", "communicationUser": {
                                    "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                                "displayName": "Bob",
                                "shareHistoryTime": "2020-10-30T10:50:50Z"
                            }
                        ],
                        "initiatorCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}}
                    },
                    "senderDisplayName": "Bob",
                    "createdOn": "2021-01-27T01:37:33Z",
                    "senderCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                        "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                    "deletedOn": "2021-01-27T01:37:33Z",
                    "editedOn": "2021-01-27T01:37:33Z"
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
async def test_update_message_content():
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
async def test_update_message_metadata():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    message_id='1596823919339'
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=204)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    try:
        metadata={ "tags": "tag" }
        await chat_thread_client.update_message(message_id, metadata=metadata)
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
        return mock_response(status_code=200, json_payload={"value": [
            {
                "communicationIdentifier": {
                    "rawId": participant_id,
                    "communicationUser": {
                        "id": participant_id
                    }
                },
                "displayName": "Bob",
                "shareHistoryTime": "2020-10-30T10:50:50Z"
            }
        ]})
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
                    {
                        "communicationIdentifier": {
                            "rawId": participant_id_1,
                            "communicationUser": {
                                "id": participant_id_1
                            }
                        },
                        "displayName": "Bob",
                        "shareHistoryTime": "2020-10-30T10:50:50Z"
                    },
                    {
                        "communicationIdentifier": {
                            "rawId": participant_id_2,
                            "communicationUser": {
                                "id": participant_id_2
                            }
                        },
                        "displayName": "Bob",
                        "shareHistoryTime": "2020-10-30T10:50:50Z"
                    }
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
async def test_add_participants():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    new_participant_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=201)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    new_participant = ChatParticipant(
            identifier=CommunicationUserIdentifier(new_participant_id),
            display_name='name',
            share_history_time=datetime.utcnow())
    participants = [new_participant]

    try:
        await chat_thread_client.add_participants(participants)
    except:
        raised = True

    assert raised == False

@pytest.mark.asyncio
async def test_add_participants_w_failed_participants_returns_nonempty_list():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    new_participant_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
    raised = False
    error_message = "some error message"

    async def mock_send(*_, **__):
        return mock_response(status_code=201, json_payload={
            "invalidParticipants": [
                {
                    "code": "string",
                    "message": error_message,
                    "target": new_participant_id,
                    "details": []
                }
            ]
        })
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    new_participant = ChatParticipant(
            identifier=CommunicationUserIdentifier(new_participant_id),
            display_name='name',
            share_history_time=datetime.utcnow())
    participants = [new_participant]

    try:
        result = await chat_thread_client.add_participants(participants)
    except:
        raised = True

    assert raised == False
    assert len(result) == 1

    failed_participant = result[0][0]
    communication_error = result[0][1]

    assert new_participant.identifier.properties['id'] == failed_participant.identifier.properties['id']
    assert new_participant.display_name == failed_participant.display_name
    assert new_participant.share_history_time == failed_participant.share_history_time
    assert error_message == communication_error.message

@pytest.mark.asyncio
async def test_remove_participant():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    participant_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=204)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    try:
        await chat_thread_client.remove_participant(identifier=CommunicationUserIdentifier(participant_id))
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
async def test_send_typing_notification_with_sender_display_name():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200)
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    try:
        await chat_thread_client.send_typing_notification(sender_display_name="John")
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
        return mock_response(status_code=200, json_payload={"value": [
            {
                "chatMessageId": message_id,
                "senderCommunicationIdentifier": {
                    "rawId": "string",
                    "communicationUser": {
                        "id": "string"
                    }
                }
            }
        ]})
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
                {
                    "chatMessageId": message_id_1,
                    "senderCommunicationIdentifier": {
                        "rawId": "string",
                        "communicationUser": {
                            "id": "string"
                        }
                    }
                },
                {
                    "chatMessageId": message_id_2,
                    "senderCommunicationIdentifier": {
                        "rawId": "string",
                        "communicationUser": {
                            "id": "string"
                        }
                    }
                }
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
                {
                    "chatMessageId": message_id_1,
                    "senderCommunicationIdentifier": {
                        "rawId": "string",
                        "communicationUser": {
                            "id": "string"
                        }
                    }
                }
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

@pytest.mark.asyncio
async def test_get_properties():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={
                "id": thread_id,
                "topic": "Lunch Chat thread",
                "createdOn": "2020-10-30T10:50:50Z",
                "deletedOn": "2020-10-30T10:50:50Z",
                "createdByCommunicationIdentifier": {"rawId": "string", "communicationUser": {"id": "string"}}
                })
    chat_thread_client = ChatThreadClient("https://endpoint", credential, thread_id, transport=Mock(send=mock_send))

    get_thread_result = None
    try:
        get_thread_result = await chat_thread_client.get_properties()
    except:
        raised = True

    assert raised == False
    assert get_thread_result.id == thread_id
