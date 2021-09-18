# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import List
from ._test_constants import RESOURCE_IDENTIFIER
from azure.communication.callingserver import (
    PlayAudioResult,
    CallConnection,
    CancelAllMediaOperationsResult,
    AddParticipantResult,
    OperationStatus
    )

class CallingServerLiveTestUtils:

    @staticmethod
    def validate_callconnection(call_connection_async):
        # type: (CallConnection) -> None
        assert call_connection_async is not None
        assert call_connection_async.call_connection_id is not None
        assert len(call_connection_async.call_connection_id) != 0

    @staticmethod
    def validate_play_audio_result(play_audio_result: PlayAudioResult):
        # type: (PlayAudioResult) -> None
        assert play_audio_result is not None
        assert play_audio_result.operation_id is not None
        assert len(play_audio_result.operation_id) != 0
        assert play_audio_result.status is not None
        assert play_audio_result.status == OperationStatus.RUNNING

    @staticmethod
    def validate_cancel_all_media_operations(cancel_all_media_operations_result):
        # type: (CancelAllMediaOperationsResult) -> None
        assert cancel_all_media_operations_result is not None
        assert cancel_all_media_operations_result.operation_id is not None
        assert len(cancel_all_media_operations_result.operation_id) != 0
        assert cancel_all_media_operations_result.status is not None
        assert cancel_all_media_operations_result.status == OperationStatus.COMPLETED

    @staticmethod
    def validate_add_participant(add_participant_result):
        # type: (AddParticipantResult) -> None
        assert add_participant_result is not None
        assert add_participant_result.participant_id is not None
        assert len(add_participant_result.participant_id) != 0

    @staticmethod
    def clean_up_connections_async(call_connections):
        # type: (List[CallConnection]) -> None
        if call_connections is None:
            return

        for connection in call_connections:
            if connection is not None:
                try:
                    connection.hang_up()
                except Exception as err:
                    print("Error hanging up: " + str(err))

    @staticmethod
    def get_fixed_user_id(user_guid):
        # type: (str) -> str
        return "8:acs:" + RESOURCE_IDENTIFIER + "_" + user_guid
