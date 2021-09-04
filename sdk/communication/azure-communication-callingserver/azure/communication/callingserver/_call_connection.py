# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, overload

from azure.core.tracing.decorator import distributed_trace

from ._generated.operations import CallConnectionsOperations
from ._generated.models import CancelAllMediaOperationsRequest, PlayAudioRequest, PhoneNumberIdentifierModel
from ._converters import PlayAudioRequestConverter
from ._models import PlayAudioOptions, PlayAudioResult, CancelAllMediaOperationsResult, AddParticipantResult
from ._communication_identifier_serializer import (deserialize_identifier,
                                                   serialize_identifier)

class CallConnection(object):
    def __init__(
            self,
            call_connection_id, # type: str
            call_connection_client, # type: CallConnectionsOperations
            **kwargs  # type: Any
        ): # type: (...) -> None

        self.call_connection_id = call_connection_id
        self.call_connection_client = call_connection_client

    @distributed_trace()
    def hang_up(
            self,
            **kwargs # type: Any
        ): # type: (...) -> None

        return self.call_connection_client.hangup_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace()
    def cancel_all_media_operations(
            self,
            operation_context = None, # type: Optional[str]
            **kwargs # type: Any
        ): # type: (...) -> CancelAllMediaOperationsResult

        if operation_context is not None:
            kwargs['operation_context'] = operation_context
        request = CancelAllMediaOperationsRequest(**kwargs)

        cancel_all_media_operations_result = await self.call_connection_client.cancel_all_media_operations(
            call_connection_id=self.call_connection_id,
            cancel_all_media_operation_request=request,
            **kwargs
        )

        return CancelAllMediaOperationsResult._from_generated(cancel_all_media_operations_result)

    @distributed_trace()
    def play_audio(
            self,
            audio_file_uri, # type: str
            loop, # type: bool
            audio_file_id, # type: str
            callback_uri, # type: str
            operation_context = None, # type: Optional[str]
            **kwargs, # type: str: Any
        ): # type: (...) -> PlayAudioResult

        try:
            if not audio_file_uri.lower().startswith('http'):
                audio_file_uri = "https://" + audio_file_uri
        except AttributeError:
            raise ValueError("URL must be a string.")

        if not audio_file_id:
            raise ValueError("audio_file_id can not be None")

        try:
            if not callback_uri.lower().startswith('http'):
                callback_uri = "https://" + callback_uri
        except AttributeError:
            raise ValueError("URL must be a string.")

        play_audio_options = PlayAudioOptions(
            audio_file_uri=audio_file_uri,
            loop = loop,
            audio_file_id=audio_file_id,
            callback_uri=callback_uri,
            operation_context=operation_context,
        )

        return self.play_audio(
            playaudio_options=play_audio_options,
            **kwargs
        )

    @distributed_trace()
    @overload
    def play_audio(
            self,
            play_audio_options, # type: PlayAudioOptions
            **kwargs, # type: str: Any
        ): # type: (...) -> PlayAudioResult

        if not play_audio_options:
            raise ValueError("options can not be None")

        play_audio_request = PlayAudioRequestConverter.convert(play_audio_options)

        play_audio_result = await self.call_connection_client.play_audio(
            call_connection_id=self.call_connection_id,
            request=play_audio_request,
            **kwargs
        )

        return PlayAudioResult._from_generated(play_audio_result)

    @distributed_trace()
    def add_participant(
            self,
            participant,  # type: CommunicationIdentifier
            alternate_caller_id, # type: Optional[str]
            operation_context, # type: Optional[str]
            **kwargs # type: Any
        ): # type: (...) -> AddParticipantResult

        if not participant:
            raise ValueError("participant can not be None")

        add_participant_result = self.call_connection_client.add_participant(
            call_connection_id=self.call_connection_id,
            participant=serialize_identifier(participant),
            alternate_caller_id=None if alternate_caller_id == None else PhoneNumberIdentifierModel(value=alternate_caller_id.properties['value']),
            operation_context=operation_context,
            callback_uri=None,
            **kwargs
        )

        return AddParticipantResult._from_generated(add_participant_result)

    @distributed_trace()
    def remove_participant(
            self,
            participant_id,  # type: str
            **kwargs # type: Any
        ): # type: (...) -> None

        return await self.call_connection_client.remove_participant(
            call_connection_id=self.call_connection_id,
            participant_id=participant_id,
            **kwargs
        )