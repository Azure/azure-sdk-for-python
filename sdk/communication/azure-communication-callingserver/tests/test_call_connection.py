# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
import _test_constants
import _test_utils

from azure.communication.callingserver._shared.models import CommunicationUserIdentifier
from azure.communication.callingserver._models import (CreateCallOptions, MediaType,
    EventSubscriptionType, JoinCallOptions)

class TestCallingServerClient(unittest.TestCase):
    """ UnitTesting Calling Server client methods. """

    def test_create_connection(self):
        calling_server_client = _test_utils.create_mock_calling_server_client(status_code=201,
            payload={
                "callLegId": _test_constants.CALL_ID,
                "callConnectionId": _test_constants.CALL_ID
            })
        source_user = CommunicationUserIdentifier("id1")
        target_users = [CommunicationUserIdentifier("id2")]
        options = CreateCallOptions(
            callback_uri=_test_constants.CALLBACK_URI,
            requested_media_types=[MediaType.AUDIO],
            requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED])

        call_connection = calling_server_client.create_call_connection(source_user,
            target_users, options)
        assert call_connection.call_connection_id == _test_constants.CALL_ID
        assert call_connection.call_connection_client

    def test_play_audio(self):
        call_connection = _test_utils.create_mock_call_connection(status_code=202, payload={
                "operationId": "operationId",
                "status": "completed",
                "operationContext": "operationContext",
                "resultInfo": {
                    "code": "202",
                    "subcode": "0",
                    "message": "message"
                }
            })
        play_audio_result = call_connection.play_audio(audio_file_uri="audioFileUri",
            audio_File_id="audioFileId", callback_uri=_test_constants.CALLBACK_URI,
            operation_context="none", loop=False)
        assert play_audio_result.status == "completed"

    def test_add_participant(self):
        call_connection = _test_utils.create_mock_call_connection(status_code=202, payload={
                "participantId": "participantId"
            })

        user = {"raw_id": "participantId"}
        alternate_id = {"value": "phoneNumber"}
        add_participant_result = call_connection.add_participant(participant=user,
            alternate_call_id=alternate_id, operation_context="none")
        assert add_participant_result.participant_id == "participantId"

    def test_join_call(self):
        calling_server_client = _test_utils.create_mock_calling_server_client(status_code=202,
            payload={
                "callConnectionId": "newParticipantId"
            })
        join_call_options = JoinCallOptions(
            callback_uri=_test_constants.CALLBACK_URI,
            requested_media_types=MediaType.VIDEO,
            requested_call_events=EventSubscriptionType.PARTICIPANTS_UPDATED)
        join_call_result = calling_server_client.join_call(
            server_call_id=_test_constants.CALL_ID,
            source={"raw_id": "newParticipantId"},
            options=join_call_options)
        assert join_call_result.call_connection_id == "newParticipantId"

if __name__ == '__main__':
    unittest.main()
