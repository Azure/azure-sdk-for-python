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
    CommunicationIdentifierModel,
    AddParticipantRequest,
    PhoneNumberIdentifierModel
    )

class JoinCallRequestConverter(object):
    @staticmethod
    def _convert(
        source: CommunicationIdentifierModel,
        join_call_options: JoinCallOptions
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
    def _convert(
        audio_file_uri: str,
        play_audio_options: PlayAudioOptions
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
    def _convert(
        participant: CommunicationIdentifierModel,
        alternate_caller_id: PhoneNumberIdentifierModel = None,
        operation_context: str = None,
        callback_uri: str = None
        ): # type: (...) -> AddParticipantRequest

        if not participant:
            raise ValueError("participant can not be None")

        return AddParticipantRequest(
            alternate_caller_id=alternate_caller_id,
            participant=participant,
            operation_context=operation_context,
            callback_uri=callback_uri
            )
