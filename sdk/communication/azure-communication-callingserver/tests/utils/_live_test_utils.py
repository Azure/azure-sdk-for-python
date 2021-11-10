# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import time, uuid
import re
from typing import List
from devtools_testutils import is_live
from ._test_constants import RESOURCE_IDENTIFIER, AZURE_TENANT_ID
from azure_devtools.scenario_tests import RecordingProcessor
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.callingserver import (
    CommunicationUserIdentifier,
    CreateCallOptions,
    CallingServerClient,
    CallConnection,
    PlayAudioResult,
    CallConnection,
    AddParticipantResult,
    CallingOperationStatus,
    CallMediaType,
    CallingEventSubscriptionType,
    GroupCallLocator
    )

class RequestReplacerProcessor(RecordingProcessor):
    def __init__(self, keys=None, replacement="sanitized"):
        self._keys = keys if keys else []
        self._replacement = replacement

    def process_request(self, request):
        request.uri = re.sub('/calling/serverCalls/([^/?]+)',
            '/calling/serverCalls/{}'.format(self._replacement), request.uri)
        return request

class CallingServerLiveTestUtils:

    @staticmethod
    def validate_callconnection(call_connection):
        # type: (CallConnection) -> None
        assert call_connection is not None
        assert call_connection.call_connection_id is not None
        assert len(call_connection.call_connection_id) != 0

    @staticmethod
    def validate_play_audio_result(play_audio_result):
        # type: (PlayAudioResult) -> None
        assert play_audio_result is not None
        assert play_audio_result.operation_id is not None
        assert len(play_audio_result.operation_id) != 0
        assert play_audio_result.status is not None
        assert play_audio_result.status == CallingOperationStatus.RUNNING

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
                requested_media_types=[CallMediaType.AUDIO],
                requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED]
            )
            from_call_connection = callingserver_client.join_call(GroupCallLocator(group_id), from_participant, from_options)
            CallingServerLiveTestUtils.validate_callconnection(from_call_connection)
            CallingServerLiveTestUtils.sleep_if_in_live_mode()

            # join to_participant to Server Call
            to_options = CreateCallOptions(
                callback_uri=call_back_uri,
                requested_media_types=[CallMediaType.AUDIO],
                requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED]
            )
            to_call_connection = callingserver_client.join_call(GroupCallLocator(group_id), to_participant, to_options)
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

    @staticmethod
    def get_new_user_id(connection_str):
        if is_live():
            identity_client = CommunicationIdentityClient.from_connection_string(connection_str)
            user = identity_client.create_user()
            return user.properties['id']

        return "8:acs:" + AZURE_TENANT_ID + "_" + str(uuid.uuid4())

    @staticmethod
    def get_group_id(test_name):
        # If tests are running in live mode, we want them to all
        # have unique groupId's so they do not conflict with other
        # recording tests running in live mode.
        if is_live():
            return str(uuid.uuid4())

        # For recording tests we need to make sure the groupId
        # matches the recorded groupId, or the call will fail.
        return CallingServerLiveTestUtils.get_playback_group_id(test_name)

    @staticmethod
    def get_playback_group_id(test_name):
        # For recording tests we need to make sure the groupId
        # matches the recorded groupId, or the call will fail.
        return str(uuid.uuid3(uuid.NAMESPACE_OID, test_name))

    @staticmethod
    # For recording tests, a new delete url should be generated.
    def get_delete_url():
        return "https://storage.asm.skype.com/v1/objects/0-wus-d10-0172bbc567cf530ac27da36ec99579f3"

    @staticmethod
    def get_invalid_delete_url():
        return "https://storage.asm.skype.com/v1/objects/0-eus-d3-00000000000000000000000000000000"