# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .._models import (JoinCallOptions, PlayAudioOptions, CommunicationUserIdentifierModel,
    CommunicationIdentifierModel, PhoneNumberIdentifierModel)
from .._shared.models import CommunicationIdentifier, CommunicationUserIdentifier, MicrosoftTeamsUserIdentifier, PhoneNumberIdentifier, UnknownIdentifier
from .._generated.models import (
    JoinCallRequest,
    PlayAudioRequest,
    CommunicationIdentifierModel,
    AddParticipantRequest,
    PhoneNumberIdentifierModel,
    MicrosoftTeamsUserIdentifierModel
    )
from .._generated.models._azure_communication_calling_server_service_enums import CommunicationCloudEnvironmentModel

class JoinCallRequestConverter(object):
    @classmethod
    def convert(
        self,
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
            subject= join_call_options.subject
            )


class PlayAudioRequestConverter(object):
    @classmethod
    def convert(
        self,
        audio_file_uri: str,
        play_audio_options: PlayAudioOptions
        ): # type: (...) -> PlayAudioRequest

        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")
        if not play_audio_options:
            raise ValueError("playaudio_options can not be None")

        return PlayAudioRequest(
            audio_file_uri=audio_file_uri,
            loop = play_audio_options.loop,
            operation_context=play_audio_options,
            audio_file_id=play_audio_options.audio_file_id,
            callback_uri=play_audio_options.callback_uri
            )

class AddParticipantRequestConverter(object):
    @classmethod
    def convert(
        self,
        participant: CommunicationIdentifierModel,
        alternate_caller_id: PhoneNumberIdentifierModel = None,
        operation_context: str = None
        ): # type: (...) -> AddParticipantRequest

        if not participant:
            raise ValueError("participant can not be None")

        return AddParticipantRequest(
            alternate_caller_id = alternate_caller_id,
            participant = participant,
            operation_context=operation_context,
            callback_uri=None
            )

class CommunicationIdentifierConverter():
    @classmethod
    def convert(cls, identifier: CommunicationIdentifier):
        if not identifier:
            raise ValueError("idenfier can not be None")
        
        if isinstance(identifier, CommunicationUserIdentifier):
            return CommunicationIdentifierModel(
                communication_user= CommunicationUserIdentifierModel(
                    id=identifier.raw_id if identifier.raw_id is not None else identifier.properties["id"]
                )
            )
            

        if isinstance(identifier, PhoneNumberIdentifier):
            return CommunicationIdentifierModel(
                raw_id=identifier.raw_id,
                phone_number=PhoneNumberIdentifierModel(value=identifier.properties["value"])
            )
        
        if isinstance(identifier, MicrosoftTeamsUserIdentifier):
            return CommunicationIdentifierModel(
                raw_id=identifier.raw_id,
                microsoft_teams_user=MicrosoftTeamsUserIdentifierModel(
                    is_anonymous=identifier.properties["is_anonymous"],
                    user_id=identifier.properties["user_id"],
                    cloud=CommunicationCloudEnvironmentModel(identifier.properties["cloud"][0])
                )
            )

        if isinstance(identifier, UnknownIdentifier):
            return CommunicationIdentifierModel(raw_id=identifier.raw_id)
        
        raise ValueError(f"Unknown identifier class #{identifier.__class__}")
