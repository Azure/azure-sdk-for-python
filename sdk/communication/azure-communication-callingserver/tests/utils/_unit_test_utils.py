# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import utils._test_constants as _test_constants

from azure.communication.callingserver import (
    CreateCallOptions,
    MediaType,
    EventSubscriptionType,
    JoinCallOptions,
    PlayAudioOptions,
    PlayAudioResult,
    AddParticipantResult,
    CommunicationUserIdentifier,
    CancelAllMediaOperationsResult,
    PhoneNumberIdentifier,
    GroupCallLocator,
    ServerCallLocator,
    OperationStatus
    )

class CallingServerUnitTestUtils:

    @staticmethod
    def data_source_test_create_connection():
        options = CreateCallOptions(
                callback_uri=_test_constants.CALLBACK_URI,
                requested_media_types=[MediaType.AUDIO],
                requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED])
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
                requested_media_types=[MediaType.AUDIO],
                requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED])
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
        assert OperationStatus.RUNNING == result.status
        assert _test_constants.OPERATION_CONTEXT == result.operation_context

    @staticmethod
    def verify_add_participant_result(result):
        # type: (AddParticipantResult) -> None
        assert _test_constants.PARTICIPANT_ID == result.participant_id

class CallConnectionUnitTestUtils:

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
            _test_constants.OPERATION_CONTEXT,
            ))

        parameters.append((
            _test_constants.ClientType_ManagedIdentity,
            _test_constants.CALL_ID,
            _test_constants.OPERATION_CONTEXT,
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
    def verify_cancel_all_media_operations_result(result):
        # type: (CancelAllMediaOperationsResult) -> None
        assert "dummyId" == result.operation_id
        assert OperationStatus.COMPLETED == result.status
        assert _test_constants.OPERATION_CONTEXT == result.operation_context

    @staticmethod
    def verify_play_audio_result(result):
        # type: (PlayAudioResult) -> None
        assert "dummyId" == result.operation_id
        assert OperationStatus.RUNNING == result.status
        assert _test_constants.OPERATION_CONTEXT == result.operation_context

    @staticmethod
    def verify_add_participant_result(result):
        # type: (AddParticipantResult) -> None
        assert _test_constants.PARTICIPANT_ID == result.participant_id
