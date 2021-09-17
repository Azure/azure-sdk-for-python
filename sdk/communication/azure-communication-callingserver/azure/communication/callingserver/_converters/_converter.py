# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .._models import JoinCallOptions, PlayAudioOptions
from .._shared.models import CommunicationIdentifier
from .._generated.models import (
    JoinCallRequest,
    PlayAudioRequest,
    TransferCallRequest,
    CommunicationIdentifierModel,
    AddParticipantRequest,
    CancelMediaOperationRequest,
    PhoneNumberIdentifierModel
    )

class JoinCallRequestConverter(object):
    @staticmethod
    def convert(
        source, # type: CommunicationIdentifierModel
        join_call_options # type: JoinCallOptions
        ): # type: (...) -> JoinCallRequest

        if not source:
            raise ValueError("source can not be None")
        if not join_call_options:
            raise ValueError("join_call_options can not be None")

        return JoinCallRequest(
            source=source,
            callback_uri=join_call_options.callback_uri,
            requested_media_types=join_call_options.requested_media_types,
            requested_call_events=join_call_options.requested_call_events,
            subject=join_call_options.subject
            )


class PlayAudioRequestConverter(object):
    @staticmethod
    def convert(
        audio_file_uri, # type: str
        play_audio_options # type: PlayAudioOptions
        ): # type: (...) -> PlayAudioRequest

        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")
        if not play_audio_options:
            raise ValueError("playaudio_options can not be None")

        return PlayAudioRequest(
            audio_file_uri=audio_file_uri,
            loop=play_audio_options.loop,
            operation_context=play_audio_options,
            audio_file_id=play_audio_options.audio_file_id,
            callback_uri=play_audio_options.callback_uri
            )

class AddParticipantRequestConverter(object):
    @staticmethod
    def convert(
        participant, # type: CommunicationIdentifierModel
        alternate_caller_id=None, # type: PhoneNumberIdentifierModel
        operation_context=None, # type: str
        callback_uri=None # type: str
        ): # type: (...) -> AddParticipantRequest

        if not participant:
            raise ValueError("participant can not be None")

        return AddParticipantRequest(
            alternate_caller_id=alternate_caller_id,
            participant=participant,
            operation_context=operation_context,
            callback_uri=callback_uri
            )

class CancelMediaOperationRequestConverter(object):
    @staticmethod
    def convert(
        media_operation_id, # type: str
        ): # type: (...) -> CancelMediaOperationRequest

        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        return CancelMediaOperationRequest(
            media_operation_id=media_operation_id
        )

class TransferCallRequestConverter(object):
    @staticmethod
    def convert(
        target_participant, # type: CommunicationIdentifierModel
        user_to_user_information=None, # type: str
        ): # type: (...) -> TransferCallRequest

        if not target_participant:
            raise ValueError("target_participant can not be None")

        return TransferCallRequest(
            target_participant=target_participant,
            user_to_user_information=user_to_user_information
        )
