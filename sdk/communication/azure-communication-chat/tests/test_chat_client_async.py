# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.credentials import AccessToken
from azure.communication.chat.aio import (
    ChatClient,
    CommunicationUserCredential
)
from azure.communication.chat import (
    ChatThreadMember,
    CommunicationUser
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

credential = Mock()
credential.get_token = Mock(return_value=AccessToken("some_token", datetime.now().replace(tzinfo=TZ_UTC)))

@pytest.mark.asyncio
async def test_create_chat_thread():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"

    async def mock_send(*_, **__):
        return mock_response(status_code=207, json_payload={"multipleStatus": [{"id": thread_id, "statusCode": 201, "type": "Thread"}]})

    chat_client = ChatClient("https://endpoint", credential, transport=Mock(send=mock_send))

    topic="test topic"
    user = CommunicationUser("8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041")
    members=[ChatThreadMember(
        user=user,
        display_name='name',
        share_history_time=datetime.utcnow()
    )]
    chat_thread_client = await chat_client.create_chat_thread(topic, members)
    assert chat_thread_client.thread_id == thread_id

@pytest.mark.asyncio
async def test_create_chat_thread_raises_error():
    async def mock_send(*_, **__):
        return mock_response(status_code=400, json_payload={"msg": "some error"})
    chat_client = ChatClient("https://endpoint", credential, transport=Mock(send=mock_send))

    topic="test topic",
    user = CommunicationUser("8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041")
    members=[ChatThreadMember(
        user=user,
        display_name='name',
        share_history_time=datetime.utcnow()
    )]

    raised = False
    try:
        await chat_client.create_chat_thread(topic=topic, thread_members=members)
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
async def test_get_chat_thread():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={
                "id": thread_id,
                "created_by": "8:acs:resource_user",
                "members": [{"id": "", "display_name": "name", "share_history_time": "1970-01-01T00:00:00Z"}]
                })
    chat_client = ChatClient("https://endpoint", credential, transport=Mock(send=mock_send))

    get_thread_result = None
    try:
        get_thread_result = await chat_client.get_chat_thread(thread_id)
    except:
        raised = True

    assert raised == False
    assert get_thread_result.id == thread_id

@pytest.mark.asyncio
async def test_list_chat_threads():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    raised = False

    async def mock_send(*_, **__):
        return mock_response(status_code=200, json_payload={"value": [{"id": thread_id}]})
    chat_client = ChatClient("https://endpoint", credential, transport=Mock(send=mock_send))

    chat_thread_infos = None
    try:
        chat_thread_infos = chat_client.list_chat_threads()
    except:
        raised = True

    assert raised == False

    items = []
    async for item in chat_thread_infos:
        items.append(item)

    assert len(items) == 1
    assert items[0].id == thread_id


def test_get_thread_client():
    thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
    chat_client = ChatClient("https://endpoint", credential)
    chat_thread_client = chat_client.get_chat_thread_client(thread_id)

    assert chat_thread_client.thread_id == thread_id