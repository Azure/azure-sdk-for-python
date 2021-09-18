# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.communication.callingserver import (
    PlayAudioResult,
    CallConnection,
    ServerCall,
    CancelAllMediaOperationsResult,
    AddParticipantResult,
    OperationStatus
    )
from azure.communication.callingserver.aio import CallConnection as CallConnectionAsync

class CallingServerLiveTestUtils:

    def validate_callconnection(call_connection_async: CallConnection):
        assert call_connection_async is not None
        assert call_connection_async.call_connection_id is not None
        assert len(call_connection_async.call_connection_id) != 0

    def validate_play_audio_result(play_audio_result: PlayAudioResult):
        assert play_audio_result is not None
        assert play_audio_result.operation_id is not None
        assert len(play_audio_result.operation_id) != 0
        assert play_audio_result.status is not None
        assert play_audio_result.status == OperationStatus.RUNNING

    def validate_cancel_all_media_operations(cancel_all_media_operations_result: CancelAllMediaOperationsResult):
        assert cancel_all_media_operations_result is not None
        assert cancel_all_media_operations_result.operation_id is not None
        assert len(cancel_all_media_operations_result.operation_id) != 0
        assert cancel_all_media_operations_result.status is not None
        assert cancel_all_media_operations_result.status == OperationStatus.COMPLETED

    def validate_add_participant(add_participant_result: AddParticipantResult):
        assert add_participant_result is not None
        assert add_participant_result.participant_id is not None
        assert len(add_participant_result.participant_id) != 0


