# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import unittest
import pytest

from azure.communication.callingserver._shared.models import CommunicationUserIdentifier
from azure.communication.callingserver._models import (CreateCallOptions, MediaType,
    EventSubscriptionType, JoinCallOptions)
from azure.communication.callingserver.aio import CallingServerClient

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore

CALL_ID = "callId"
CALLBACK_URI = "callBackUri"
CONNECTION_STRING = "endpoint=https://REDACTED.communication.azure.com/;accesskey=eyJhbG=="

def _create_mock_call_connection(status_code, payload):
    calling_server_client = _create_mock_calling_server_client(status_code, payload)
    return calling_server_client.get_call_connection(CALL_ID)

def _create_mock_calling_server_client(status_code, payload):
    async def mock_send(*_, **__):
        return _mock_response(status_code=status_code, json_payload=payload)

    return _create_calling_server_client(mock_send)

def _create_calling_server_client(mock_transport=None):
    if mock_transport is None:
        return CallingServerClient.from_connection_string(CONNECTION_STRING)
    return CallingServerClient.from_connection_string(CONNECTION_STRING,
        transport=Mock(send=mock_transport))

def _mock_response(status_code=200, headers=None, json_payload=None):
    response = Mock(status_code=status_code, headers=headers or {})
    if json_payload is not None:
        response.text = lambda encoding=None: json.dumps(json_payload)
        response.headers["content-type"] = "application/json"
        response.content_type = "application/json"
    else:
        response.text = lambda encoding=None: ""
        response.headers["content-type"] = "text/plain"
        response.content_type = "text/plain"
    return response

@pytest.mark.asyncio
async def test_create_connection():
    calling_server_client = _create_mock_calling_server_client(status_code=201, payload={
            "callLegId": CALL_ID,
            "callConnectionId": CALL_ID
        })
    source_user = CommunicationUserIdentifier("id1")
    target_users = [CommunicationUserIdentifier("id2")]
    options = CreateCallOptions(
        callback_uri=CALLBACK_URI,
        requested_media_types=[MediaType.AUDIO],
        requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED])

    call_connection = await calling_server_client.create_call_connection(source_user,
        target_users, options)
    assert call_connection.call_connection_id == CALL_ID
    assert call_connection.call_connection_client

@pytest.mark.asyncio
async def test_get_call_connection():
    calling_server_client = _create_calling_server_client()
    call_connection = calling_server_client.get_call_connection(CALL_ID)
    assert call_connection is not None
    assert call_connection.call_connection_id == CALL_ID

@pytest.mark.asyncio
async def test_play_audio():
    call_connection = _create_mock_call_connection(status_code=202, payload={
            "operationId": "operationId",
            "status": "completed",
            "operationContext": "operationContext",
            "resultInfo": {
                "code": "202",
                "subcode": "0",
                "message": "message"
            }
        })
    play_audio_result = await call_connection.play_audio(audio_file_uri="audioFileUri",
        audio_file_id="audioFileId", callback_uri=CALLBACK_URI,
        operation_context="none", loop=False)
    assert play_audio_result.status == "completed"

@pytest.mark.asyncio
async def test_add_participant():
    call_connection = _create_mock_call_connection(status_code=202, payload={
            "participantId": "participantId"
        })

    user = {"raw_id": "participantId"}
    alternate_id = {"value": "phoneNumber"}
    add_participant_result = await call_connection.add_participant(participant=user,
        alternate_call_id=alternate_id, operation_context="none")
    assert add_participant_result.participant_id == "participantId"

@pytest.mark.asyncio
async def test_join_call():
    calling_server_client = _create_mock_calling_server_client(status_code=202, payload={
        "callConnectionId": "newParticipantId"
    })
    join_call_options = JoinCallOptions(
        callback_uri=CALLBACK_URI,
        requested_media_types=MediaType.VIDEO,
        requested_call_events=EventSubscriptionType.PARTICIPANTS_UPDATED)
    join_call_result = await calling_server_client.join_call(server_call_id=CALL_ID,
        source={"raw_id": "newParticipantId"}, options=join_call_options)
    assert join_call_result.call_connection_id == "newParticipantId"

if __name__ == '__main__':
    unittest.main()
