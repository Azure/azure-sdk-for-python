# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import utils._test_constants as _test_constants
from azure.communication.callingserver._communication_call_locator_serializer import (
    deserialize_call_locator
    )
from azure.communication.callingserver._communication_identifier_serializer import (
    deserialize_identifier
    )
from azure.communication.callingserver import (
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
    CallingOperationStatus
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
            _test_constants.AUDIO_FILE_URI,
            options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            _test_constants.AUDIO_FILE_URI,
            options,
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            _test_constants.AUDIO_FILE_URI,
            options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            _test_constants.AUDIO_FILE_URI,
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
            _test_constants.AUDIO_FILE_URI,
            play_audio_options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            ServerCallLocator(_test_constants.SEVERCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.AUDIO_FILE_URI,
            play_audio_options,
            True,
            ))

        parameters.append((
            _test_constants.ClientType_ConnectionString,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.AUDIO_FILE_URI,
            play_audio_options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            GroupCallLocator(_test_constants.GROUPCALL_ID),
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.AUDIO_FILE_URI,
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
    def data_source_test_remove_participant():
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
    def data_source_test_cancel_participant_media_operation():

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
    def verify_play_audio_result(result):
        # type: (PlayAudioResult) -> None
        assert "dummyId" == result.operation_id
        assert CallingOperationStatus.RUNNING == result.status
        assert _test_constants.OPERATION_CONTEXT == result.operation_context

    @staticmethod
    def verify_add_participant_result(result):
        # type: (AddParticipantResult) -> None
        assert _test_constants.PARTICIPANT_ID == result.participant_id

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
            _test_constants.AUDIO_FILE_URI,
            options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            _test_constants.AUDIO_FILE_URI,
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
            _test_constants.AUDIO_FILE_URI,
            options,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.AUDIO_FILE_URI,
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
            _test_constants.USER_TO_USER_INFORMATION,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
            _test_constants.USER_TO_USER_INFORMATION,
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
    def verify_play_audio_result(result):
        # type: (PlayAudioResult) -> None
        assert _test_constants.OPERATION_ID == result.operation_id
        assert CallingOperationStatus.RUNNING == result.status
        assert _test_constants.OPERATION_CONTEXT == result.operation_context

    @staticmethod
    def verify_add_participant_result(result):
        # type: (AddParticipantResult) -> None
        assert _test_constants.PARTICIPANT_ID == result.participant_id

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
