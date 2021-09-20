# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import time
from typing import List
from devtools_testutils import is_live
from ._test_constants import RESOURCE_IDENTIFIER
from azure.communication.callingserver import (
    CommunicationUserIdentifier,
    CreateCallOptions,
    CallingServerClient,
    CallConnection,
    PlayAudioResult,
    CallConnection,
    CancelAllMediaOperationsResult,
    AddParticipantResult,
    OperationStatus,
    MediaType,
    EventSubscriptionType
    )

class CallingServerLiveTestUtils:

    @staticmethod
    def validate_callconnection(call_connection):
        # type: (CallConnection) -> None
        assert call_connection is not None
        assert call_connection.call_connection_id is not None
        assert len(call_connection.call_connection_id) != 0

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
    def cancel_all_media_operations_for_group_call(call_connections):
        # type: (List[CallConnection]) -> None
        if call_connections is None:
            return
        for connection in call_connections:
            if connection is not None:
                connection.cancel_all_media_operations()

    @staticmethod
    def clean_up_connections(call_connections):
        # type: (List[CallConnection]) -> None
        if call_connections is None:
            return
        for connection in call_connections:
            if connection is not None:
                connection.hang_up()

    @staticmethod
    def get_fixed_user_id(user_guid):
        # type: (str) -> str
        return "8:acs:" + RESOURCE_IDENTIFIER + "_" + user_guid

    @staticmethod
    def sleep_if_in_live_mode():
        # type: () -> None
        if is_live():
            time.sleep(10)

    @staticmethod
    def create_group_calls(
        callingserver_client,  # type: CallingServerClient
        group_id,  # type: str
        from_user,  # type: str
        to_user,  # type: str
        call_back_uri,  # type: str
        ): # type: (...) -> List[CallConnection]
        from_participant = CommunicationUserIdentifier(from_user)
        to_participant = CommunicationUserIdentifier(to_user)
        group_calls = []

        from_call_connection = None
        to_call_connection = None
        try:
            # join from_participant to Server Call
            from_options = CreateCallOptions(
                callback_uri=call_back_uri,
                requested_media_types=[MediaType.AUDIO],
                requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED]
            )
            from_call_connection = callingserver_client.join_call(group_id, from_participant, from_options)
            CallingServerLiveTestUtils.validate_callconnection(from_call_connection)
            CallingServerLiveTestUtils.sleep_if_in_live_mode()

            # join to_participant to Server Call
            to_options = CreateCallOptions(
                callback_uri=call_back_uri,
                requested_media_types=[MediaType.AUDIO],
                requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED]
            )
            to_call_connection = callingserver_client.join_call(group_id, to_participant, to_options)
            CallingServerLiveTestUtils.validate_callconnection(from_call_connection)
            CallingServerLiveTestUtils.sleep_if_in_live_mode()

            group_calls.append(from_call_connection)
            group_calls.append(to_call_connection)

            return group_calls

        except Exception as err:
            print("An exception occurred: ", err)

            if from_call_connection is not None:
                from_call_connection.hang_up()
            if to_call_connection is not None:
                to_call_connection.hang_up()
            raise err
