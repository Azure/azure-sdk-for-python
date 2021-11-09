# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List
import utils._test_constants as _test_constants
from azure.communication.callingserver._communication_call_locator_serializer import (
    deserialize_call_locator
    )
from azure.communication.callingserver._communication_identifier_serializer import (
    deserialize_identifier
    )

from azure.communication.callingserver import (
    AudioRoutingMode,
    CreateCallOptions,
    CallMediaType,
    CallingEventSubscriptionType,
    JoinCallOptions,
    PlayAudioOptions,
    PlayAudioResult,
    AddParticipantResult,
    CallConnectionProperties,
    CommunicationUserIdentifier,
    PhoneNumberIdentifier,
    GroupCallLocator,
    ServerCallLocator,
    CallingOperationStatus,
    AnswerCallResult,
    AudioRoutingGroupResult,
    CreateAudioRoutingGroupResult,
    CallRejectReason,
    CallParticipant
    )

class CallingServerUnitTestUtils:

    @staticmethod
    def data_source_test_create_connection():
        options = CreateCallOptions(
                callback_uri=_test_constants.CALLBACK_URI,
                requested_media_types=[CallMediaType.AUDIO],
                requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED])
        options.subject=_test_constants.CALL_SUBJECT
        options.alternate_Caller_Id = PhoneNumberIdentifier(_test_constants.PHONE_NUMBER)

        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            [CommunicationUserIdentifier(_test_constants.RESOURCE_TARGET), PhoneNumberIdentifier(_test_constants.PHONE_NUMBER)],
            options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            [CommunicationUserIdentifier(_test_constants.RESOURCE_TARGET), PhoneNumberIdentifier(_test_constants.PHONE_NUMBER)],
            options,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_join_call():
        options = JoinCallOptions(
                callback_uri=_test_constants.CALLBACK_URI,
                requested_media_types=[CallMediaType.AUDIO],
                requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED])
        options.subject=_test_constants.CALL_SUBJECT

        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            options,
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            options,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_answer_call():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.INCOMING_CALL_CONTEXT,
            _test_constants.CALLBACK_URI,
            [CallMediaType.AUDIO,CallMediaType.VIDEO],
            [CallingEventSubscriptionType.PARTICIPANTS_UPDATED,CallingEventSubscriptionType.TONE_RECEIVED],
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.INCOMING_CALL_CONTEXT,
            _test_constants.CALLBACK_URI,
            [CallMediaType.AUDIO,CallMediaType.VIDEO],
            [CallingEventSubscriptionType.PARTICIPANTS_UPDATED,CallingEventSubscriptionType.TONE_RECEIVED],
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_reject_call():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.INCOMING_CALL_CONTEXT,
            CallRejectReason.BUSY,
            _test_constants.CALLBACK_URI,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.INCOMING_CALL_CONTEXT,
            CallRejectReason.BUSY,
            _test_constants.CALLBACK_URI,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_redirect_call():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.INCOMING_CALL_CONTEXT,
            [CommunicationUserIdentifier(_test_constants.RESOURCE_TARGET)],
            _test_constants.CALLBACK_URI,
            _test_constants.TIMEOUT_IN_SECONDS,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.INCOMING_CALL_CONTEXT,
            [CommunicationUserIdentifier(_test_constants.RESOURCE_TARGET)],
            _test_constants.CALLBACK_URI,
            _test_constants.TIMEOUT_IN_SECONDS,
            True,
            ))

        return parameters


    @staticmethod
    def data_source_test_play_audio():
        options = PlayAudioOptions(
                loop = True,
                audio_file_id=_test_constants.AUDIO_FILE_ID,
                callback_uri=_test_constants.CALLBACK_URI,
                operation_context=_test_constants.OPERATION_CONTEXT
                )

        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            _test_constants.AUDIO_URL,
            options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            _test_constants.AUDIO_URL,
            options,
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            _test_constants.AUDIO_URL,
            options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            _test_constants.AUDIO_URL,
            options,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_play_audio_to_participant():
        play_audio_options = PlayAudioOptions(
                loop = True,
                audio_file_id = _test_constants.AUDIO_FILE_ID,
                callback_uri = _test_constants.CALLBACK_URI,
                operation_context = _test_constants.OPERATION_CONTEXT
                )

        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.AUDIO_URL,
            play_audio_options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.AUDIO_URL,
            play_audio_options,
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.AUDIO_URL,
            play_audio_options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.AUDIO_URL,
            play_audio_options,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_add_participant():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.CALLBACK_URI,
            _test_constants.PHONE_NUMBER,
            _test_constants.OPERATION_CONTEXT,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.CALLBACK_URI,
            _test_constants.PHONE_NUMBER,
            _test_constants.OPERATION_CONTEXT,
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.CALLBACK_URI,
            _test_constants.PHONE_NUMBER,
            _test_constants.OPERATION_CONTEXT,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.CALLBACK_URI,
            _test_constants.PHONE_NUMBER,
            _test_constants.OPERATION_CONTEXT,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_remove_participant_with_call_locator():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_list_participants_with_call_locator():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_get_participant_with_call_locator():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.COMMUNICATION_USER_Id_01),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.COMMUNICATION_USER_Id_01),
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.COMMUNICATION_USER_Id_01),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.COMMUNICATION_USER_Id_01),
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_mute_participant_with_call_locator():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.COMMUNICATION_USER_Id_01),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.COMMUNICATION_USER_Id_01),
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.COMMUNICATION_USER_Id_01),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.COMMUNICATION_USER_Id_01),
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_unmute_participant_with_call_locator():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.COMMUNICATION_USER_Id_01),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.COMMUNICATION_USER_Id_01),
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.COMMUNICATION_USER_Id_01),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.COMMUNICATION_USER_Id_01),
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_cancel_media_operation():

        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            _test_constants.MEDIA_OPERATION_ID,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            _test_constants.MEDIA_OPERATION_ID,
            True,
            ))
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            _test_constants.MEDIA_OPERATION_ID,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            _test_constants.MEDIA_OPERATION_ID,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_cancel_participant_media_operation_with_callLocator():

        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.MEDIA_OPERATION_ID,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.MEDIA_OPERATION_ID,
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.MEDIA_OPERATION_ID,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.MEDIA_OPERATION_ID,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_hold_participant_meeting_audio_with_callLocator():

        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.PARTICIPANT_ID_01),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.PARTICIPANT_ID_01),
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.PARTICIPANT_ID_01),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.PARTICIPANT_ID_01),
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_resume_participant_meeting_audio_with_callLocator():

        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.PARTICIPANT_ID_01),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.PARTICIPANT_ID_01),
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.PARTICIPANT_ID_01),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.PARTICIPANT_ID_01),
            True,
            ))

        return parameters

    @staticmethod
    def verify_play_audio_result(result):
        # type: (PlayAudioResult) -> None
        assert "dummyId" == result.operation_id
        assert CallingOperationStatus.RUNNING == result.status
        assert _test_constants.OPERATION_CONTEXT == result.operation_context

    @staticmethod
    def verify_add_participant_result(result):
        # type: (AddParticipantResult) -> None
        assert _test_constants.PARTICIPANT_ID_01 == result.participant_id

    @staticmethod
    def verify_answer_call_result(result):
        # type: (AnswerCallResult) -> None
        assert result.call_connection_id == _test_constants.CALL_ID

    @staticmethod
    def verify_list_participants_result(result):
        # type: (List[CallParticipant]) -> None
        target_identifier_01 = deserialize_identifier(result[0].identifier)
        assert _test_constants.COMMUNICATION_USER_Id_01 == target_identifier_01.properties['id']
        assert _test_constants.COMMUNICATION_USER_KIND == target_identifier_01.kind
        assert False == result[0].is_muted
        assert _test_constants.PARTICIPANT_ID_01 == result[0].participant_id

        target_identifier_02 = deserialize_identifier(result[1].identifier)
        print(deserialize_identifier(result[0].identifier))
        print(deserialize_identifier(result[1].identifier))
        print(target_identifier_01.properties)
        print(target_identifier_02.properties)
        assert _test_constants.PHONE_NUMBER == target_identifier_02.properties['value']
        assert _test_constants.PHONE_NUMBER_KIND == target_identifier_02.kind
        assert True == result[1].is_muted
        assert _test_constants.PARTICIPANT_ID_02 == result[1].participant_id

    @staticmethod
    def verify_get_participant_result(result):
        # type: (List[CallParticipant]) -> None
        target_identifier_01 = deserialize_identifier(result[0].identifier)
        assert _test_constants.COMMUNICATION_USER_Id_01 == target_identifier_01.properties['id']
        assert _test_constants.COMMUNICATION_USER_KIND == target_identifier_01.kind
        assert False == result[0].is_muted
        assert _test_constants.PARTICIPANT_ID_01 == result[0].participant_id

class CallConnectionUnitTestUtils:

    @staticmethod
    def data_source_test_get_call():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_delete_call():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_hang_up():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_keep_alive():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_cancel_all_media_operations():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_play_audio():
        options = PlayAudioOptions(
                loop = True,
                audio_file_id = _test_constants.AUDIO_FILE_ID,
                callback_uri = _test_constants.CALLBACK_URI,
                operation_context = _test_constants.OPERATION_CONTEXT
                )
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            _test_constants.AUDIO_URL,
            options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            _test_constants.AUDIO_URL,
            options,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_play_audio_to_participant():
        options = PlayAudioOptions(
                loop = True,
                audio_file_id = _test_constants.AUDIO_FILE_ID,
                callback_uri = _test_constants.CALLBACK_URI,
                operation_context = _test_constants.OPERATION_CONTEXT
                )
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.AUDIO_URL,
            options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.AUDIO_URL,
            options,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_add_participant():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.PHONE_NUMBER,
            _test_constants.OPERATION_CONTEXT,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.PHONE_NUMBER,
            _test_constants.OPERATION_CONTEXT,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_transfer_call():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.SERVER_CALL_ID,
            _test_constants.USER_TO_USER_INFORMATION,
            _test_constants.OPERATION_CONTEXT,
            _test_constants.CALLBACK_URI
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.SERVER_CALL_ID,
            _test_constants.USER_TO_USER_INFORMATION,
            _test_constants.OPERATION_CONTEXT,
            _test_constants.CALLBACK_URI,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_remove_participant():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_list_participants():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_get_participant():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_cancel_participant_media_operation():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.MEDIA_OPERATION_ID,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.MEDIA_OPERATION_ID,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_mute_participant():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_unmute_participant():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_hold_participant_meeting_audio():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_resume_participant_meeting_audio():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_create_audio_routing_group():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            AudioRoutingMode.ONE_TO_ONE,
            [CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE)],
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            AudioRoutingMode.ONE_TO_ONE,
            [CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE)],
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_get_audio_routing_group():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            _test_constants.AUDIO_ROUTING_GROUP_ID,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            _test_constants.AUDIO_ROUTING_GROUP_ID,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_delete_audio_routing_group():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            _test_constants.AUDIO_ROUTING_GROUP_ID,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            _test_constants.AUDIO_ROUTING_GROUP_ID,
            True,
            ))

        return parameters

    @staticmethod
    def data_source_test_update_audio_routing_group():
        parameters = []
        parameters.append((
            _test_constants.ClientType_ConnectionString,
            _test_constants.CALL_ID,
            _test_constants.AUDIO_ROUTING_GROUP_ID,
            [CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE)],
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            _test_constants.AUDIO_ROUTING_GROUP_ID,
            [CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE)],
            True,
            ))

        return parameters

    @staticmethod
    def verify_play_audio_result(result):
        # type: (PlayAudioResult) -> None
        assert _test_constants.OPERATION_ID == result.operation_id
        assert CallingOperationStatus.RUNNING == result.status
        assert _test_constants.OPERATION_CONTEXT == result.operation_context

    @staticmethod
    def verify_add_participant_result(result):
        # type: (AddParticipantResult) -> None
        assert _test_constants.PARTICIPANT_ID_01 == result.participant_id

    @staticmethod
    def verify_get_call_result(result):
        # type: (CallConnectionProperties) -> None
        call_locator = deserialize_call_locator(result.call_locator)
        source_identifier = deserialize_identifier(result.source)
        target_identifier_01 = deserialize_identifier(result.targets[0])
        target_identifier_02 = deserialize_identifier(result.targets[1])

        assert _test_constants.SEVERCALL_ID == call_locator.id
        assert _test_constants.SERVER_CALL_LOCATOR == call_locator.kind
        assert _test_constants.COMMUNICATION_USER_Id_01 == source_identifier.properties['id']
        assert _test_constants.COMMUNICATION_USER_KIND == source_identifier.kind
        assert _test_constants.COMMUNICATION_USER_Id_02 == target_identifier_01.properties['id']
        assert _test_constants.COMMUNICATION_USER_KIND == target_identifier_01.kind
        assert _test_constants.PHONE_NUMBER == target_identifier_02.properties['value']
        assert _test_constants.PHONE_NUMBER_KIND == target_identifier_02.kind

        assert _test_constants.CALL_ID == result.call_connection_id
        assert _test_constants.CALL_STATE_CONNECTED == result.call_connection_state
        assert _test_constants.CALL_SUBJECT == result.subject
        assert _test_constants.AppCallbackUrl == result.callback_uri
        assert _test_constants.CALLEVENTS_DTMFRECEIVED == result.requested_call_events[0]
        assert _test_constants.CALLEVENTS_PARTICIPANTSUPDATED == result.requested_call_events[1]
        assert _test_constants.MEDIA_TYPES_AUDIO == result.requested_media_types[0]
        assert _test_constants.MEDIA_TYPES_VIDEO == result.requested_media_types[1]

    @staticmethod
    def verify_create_audio_routing_group(result):
        # type: (CreateAudioRoutingGroupResult) -> None
            assert result.audio_routing_group_id == _test_constants.AUDIO_ROUTING_GROUP_ID

    @staticmethod
    def verify_get_audio_routing_group(result):
        # type: (AudioRoutingGroupResult) -> None
        target_identifier_01 = deserialize_identifier(result.targets[0])
        assert result.audio_routing_mode == AudioRoutingMode.ONE_TO_ONE
        assert _test_constants.RESOURCE_SOURCE == target_identifier_01.properties['id']
        assert _test_constants.COMMUNICATION_USER_KIND == target_identifier_01.kind