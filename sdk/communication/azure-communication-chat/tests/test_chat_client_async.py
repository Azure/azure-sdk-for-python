# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.credentials import AccessToken
from azure.communication.chat.aio import (
    ChatClient
)
from azure.communication.chat import ChatParticipant

from azure.communication.chat._shared.models import(
    CommunicationUserIdentifier
)
from unittest_helpers import mock_response
from azure.core.exceptions import HttpResponseError
from datetime import datetime
from msrest.serialization import TZ_UTC

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

import pytest
import time
import calendar

def _convert_datetime_to_utc_int(input):
    return int(calendar.timegm(input.utctimetuple()))


async def mock_get_token():
    return AccessToken("some_token", _convert_datetime_to_utc_int(datetime.now().replace(tzinfo=TZ_UTC)))

credential = Mock(get_token=mock_get_token)


@pytest.mark.asyncio
async def test_create_chat_thread():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"

    async def mock_send(*_, **__):
        return mock_response(status_code=201, json_payload={
            "chatThread": {
                "id": thread_id,
                "topic": "test topic",
                "createdOn": "2020-12-03T21:09:17Z",
                "createdBy": "8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
            }
        })

    chat_client = ChatClient("https://endpoint", credential, transport=Mock(send=mock_send))

    topic="test topic"
    user = CommunicationUserIdentifier("8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041")
    participants=[ChatParticipant(
        identifier=user,
        display_name='name',
        share_history_time=datetime.utcnow()
    )]
    create_chat_thread_result = await chat_client.create_chat_thread(topic, thread_participants=participants)
    assert create_chat_thread_result.chat_thread.id == thread_id

@pytest.mark.asyncio
async def test_create_chat_thread_w_repeatability_request_id():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    idempotency_token = "b66d6031-fdcc-41df-8306-e524c9f226b8"
    async def mock_send(*_, **__):
        return mock_response(status_code=201, json_payload={
            "chatThread": {
                "id": thread_id,
                "topic": "test topic",
                "createdOn": "2020-12-03T21:09:17Z",
                "createdBy": "8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
            }
        })

    chat_client = ChatClient("https://endpoint", credential, transport=Mock(send=mock_send))

    topic="test topic"
    user = CommunicationUserIdentifier("8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041")
    participants=[ChatParticipant(
        identifier=user,
        display_name='name',
        share_history_time=datetime.utcnow()
    )]
    create_chat_thread_result = await chat_client.create_chat_thread(topic=topic,
                                                              thread_participants=participants,
                                                              idempotency_token=idempotency_token)
    assert create_chat_thread_result.chat_thread.id == thread_id

@pytest.mark.asyncio
async def test_create_chat_thread_raises_error():
    async def mock_send(*_, **__):
        return mock_response(status_code=400, json_payload={"msg": "some error"})
    chat_client = ChatClient("https://endpoint", credential, transport=Mock(send=mock_send))

    topic="test topic",
    user = CommunicationUserIdentifier("8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041")
    participants=[ChatParticipant(
        identifier=user,
        display_name='name',
        share_history_time=datetime.utcnow()
    )]

    raised = False
    try:
        await chat_client.create_chat_thread(topic=topic, thread_participants=participants)
    except:
        raised = True

    assert raised == True

@pytest.mark.asyncio
async def test_delete_chat_thread():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=204)
    chat_client = ChatClient("https://endpoint", credential, transport=Mock(send=mock_send))

    raised = False
    try:
        await chat_client.delete_chat_thread(thread_id)
    except:
        raised = True

    assert raised == False

@pytest.mark.asyncio
async def test_list_chat_threads():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={"value": [{"id": thread_id}]})
    chat_client = ChatClient("https://endpoint", credential, transport=Mock(send=mock_send))

    chat_threads = None
    try:
        chat_threads = chat_client.list_chat_threads()
    except:
        raised = True

    assert raised == False

    items = []
    async for item in chat_threads:
        items.append(item)

    assert len(items) == 1
    assert items[0].id == thread_id


def test_get_thread_client():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    chat_client = ChatClient("https://endpoint", credential)
    chat_thread_client = chat_client.get_chat_thread_client(thread_id)

    assert chat_thread_client.thread_id == thread_id