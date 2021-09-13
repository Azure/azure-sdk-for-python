# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Optional, overload, List
from azure.core.tracing.decorator import distributed_trace
from ._generated.operations import CallConnectionsOperations
from ._generated.models import CancelAllMediaOperationsRequest, PlayAudioRequest, \
    AddParticipantRequest, PhoneNumberIdentifierModel, CommunicationIdentifierModel, \
    CreateCallRequest
from ._models import PlayAudioOptions, PlayAudioResult, CancelAllMediaOperationsResult, AddParticipantResult, \
    CreateCallResult, MediaType, EventSubscriptionType
from ._communication_identifier_serializer import (deserialize_identifier,
                                                   serialize_identifier)
from ._shared.models import CommunicationIdentifier


class CallConnection(object):
    def __init__(
        self,
        call_connection_id,  # type: str
        call_connection_client,  # type: CallConnectionsOperations
        **kwargs  # type: Any
    ):  # type: (...) -> None

        self.call_connection_id = call_connection_id
        self.call_connection_client = call_connection_client

    @distributed_trace()
    def create_call(self,
                    source: CommunicationIdentifierModel,
                    targets: List[CommunicationIdentifierModel],
                    alternate_caller_id: PhoneNumberIdentifierModel,
                    subject: str,
                    callback_uri: str,
                    requested_media_types: List[MediaType],
                    requested_call_events: List[EventSubscriptionType],
                    **kwargs: Any
                    ):
        # type: (...) -> CreateCallResult

        request = CreateCallRequest(
            alternate_caller_id=alternate_caller_id,
            targets=targets,
            source=source,
            subject=subject,
            callback_uri=callback_uri,
            requested_media_types=requested_media_types,
            requested_call_events=requested_call_events,
            **kwargs)

        create_call_result = self.call_connection_client.create_call(
            call_request=request)

        return CreateCallResult._from_generated(create_call_result)

    @distributed_trace()
    def hang_up(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> None

        return self.call_connection_client.hangup_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace()
    def cancel_all_media_operations(
        self,
        operation_context=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):  # type: (...) -> CancelAllMediaOperationsResult

        request = CancelAllMediaOperationsRequest(operation_context=operation_context,
                                                  **kwargs)

        cancel_all_media_operations_result = self.call_connection_client.cancel_all_media_operations(
            call_connection_id=self.call_connection_id,
            cancel_all_media_operation_request=request,
            **kwargs
        )

        return CancelAllMediaOperationsResult._from_generated(cancel_all_media_operations_result)

    @distributed_trace()
    def play_audio(
        self,
        audio_file_uri,  # type: str
        play_audio_options,  # type: PlayAudioOptions
        **kwargs,  # type: Any
    ):  # type: (...) -> PlayAudioResult

        try:
            if not audio_file_uri.lower().startswith('http'):
                audio_file_uri = "https://" + audio_file_uri
        except AttributeError:
            raise ValueError("URL must be a string.")

        if not play_audio_options.audio_file_id:
            raise ValueError("audio_file_id can not be None")

        try:
            callback_uri = play_audio_options.callback_uri
            if not callback_uri.lower().startswith('http'):
                callback_uri = "https://" + callback_uri
        except AttributeError:
            raise ValueError("URL must be a string.")

        play_audio_request = PlayAudioRequest(
            audio_file_uri=audio_file_uri,
            loop=False,
            audio_file_id=play_audio_options.audio_file_id,
            callback_uri=callback_uri,
            operation_context=play_audio_options.operation_context,
        )

        play_audio_result = self.call_connection_client.play_audio(
            call_connection_id=self.call_connection_id,
            request=play_audio_request,
            **kwargs
        )

        return PlayAudioResult._from_generated(play_audio_result)

    @distributed_trace()
    def add_participant(
        self,
        participant,  # type: CommunicationIdentifier
        alternate_caller_id,  # type: Optional[str]
        operation_context,  # type: Optional[str]
        **kwargs  # type: Any
    ):  # type: (...) -> AddParticipantResult

        if not participant:
            raise ValueError("participant can not be None")

        request = AddParticipantRequest(participant=serialize_identifier(participant),
                                        alternate_caller_id=None if alternate_caller_id == None else PhoneNumberIdentifierModel(
                                            value=alternate_caller_id.properties['value']),
                                        operation_context=operation_context,
                                        callback_uri=None,
                                        **kwargs)

        add_participant_result = self.call_connection_client.add_participant(call_connection_id=self.call_connection_id,
                                                                             add_participant_request=request)

        return AddParticipantResult._from_generated(add_participant_result)

    @distributed_trace()
    def remove_participant(
        self,
        participant_id,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> None

        return self.call_connection_client.remove_participant(
            call_connection_id=self.call_connection_id,
            participant_id=participant_id,
            **kwargs
        )
