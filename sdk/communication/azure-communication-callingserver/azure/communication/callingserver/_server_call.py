# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, List

from azure.core.tracing.decorator import distributed_trace

from ._generated.aio.operations import ServerCallsOperations
from ._generated.models import PlayAudioRequest, StartCallRecordingRequest, \
    CallRecordingProperties, AddParticipantRequest, PhoneNumberIdentifierModel, \
    CommunicationIdentifierModel, JoinCallRequest
from ._models import PlayAudioResult, JoinCallResult, AddParticipantResult, \
    StartCallRecordingResult, MediaType, EventSubscriptionType
from ._communication_identifier_serializer import (deserialize_identifier,
                                                   serialize_identifier)
from azure.core.pipeline.transport import AsyncHttpResponse

class ServerCall(object):

    def __init__(
        self,
        server_call_id: str,  # type: str
        server_call_client: ServerCallsOperations,  # type: AsyncTokenCredential
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        self.server_call_id = server_call_id
        self.server_call_client = server_call_client

    @distributed_trace()
    def play_audio(
        self,
        audio_file_uri, # type: str
        loop, # type: bool
        audio_file_id, # type: str
        callback_uri, # type: str
        operation_context = None, # type: Optional[str]
        **kwargs, # type: Any
    ): # type: (...) -> PlayAudioResult

        try:
            if not audio_file_uri.lower().startswith('http'):
                audio_file_uri = "https://" + audio_file_uri
        except AttributeError:
            raise ValueError("URL must be a string.")

        if not audio_file_id:
            raise ValueError("audio_File_id can not be None")

        try:
            if not callback_uri.lower().startswith('http'):
                callback_uri = "https://" + callback_uri
        except AttributeError:
            raise ValueError("URL must be a string.")

        if not operation_context:
            raise ValueError("operation_context can not be None")

        request = PlayAudioRequest(
            audio_file_uri=audio_file_uri,
            loop = loop,
            operation_context=operation_context,
            audio_file_id=audio_file_id,
            callback_uri=callback_uri
        )

        play_audio_result = self.server_call_client.play_audio(
            server_call_id=self.server_call_id,
            request=request,
            **kwargs
        )

        return PlayAudioResult._from_generated(play_audio_result)

    @distributed_trace()
    def start_recording(
            self,
            server_call_id, # type: str
            recording_state_callback_uri, # type: str
            **kwargs, # type: Any
    ): # type: (...) -> StartCallRecordingResult

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        start_call_recording_request = StartCallRecordingRequest(
            recording_state_callback_uri=recording_state_callback_uri,
            **kwargs
        )

        start_recording_result = self.server_call_client.start_recording(
            server_call_id=self.server_call_id,
            request=start_call_recording_request
        )

        return StartCallRecordingResult._from_generated(start_recording_result)


    @distributed_trace()
    def pause_recording(
            self,
            server_call_id, # type: str
            recording_id, # type: str
            **kwargs, # type: Any
    ): # type: (...) -> AsyncHttpResponse

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        pause_recording_result = self.server_call_client.pause_recording(
            server_call_id=self.server_call_id,
            recording_id=recording_id,
        )

        return pause_recording_result

    @distributed_trace()
    def resume_recording(
            self,
            server_call_id, # type: str
            recording_id, # type: str
            **kwargs, # type: Any
    ): # type: (...) -> AsyncHttpResponse

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        resume_recording_result = self.server_call_client.resume_recording(
            server_call_id=self.server_call_id,
            recording_id=recording_id,
        )

        return resume_recording_result


    @distributed_trace()
    def stop_recording(
            self,
            server_call_id, # type: str
            recording_id, # type: str
            **kwargs, # type: Any
    ): # type: (...) -> AsyncHttpResponse

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        stop_recording_result = self.server_call_client.stop_recording(
            server_call_id=self.server_call_id,
            recording_id=recording_id,
        )

        return stop_recording_result


    @distributed_trace()
    def get_recording_properities(
            self,
            server_call_id, # type: str
            recording_id, # type: str
            **kwargs, # type: Any
    ): # type: (...) -> CallRecordingProperties

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        recording_status_result = self.server_call_client.get_recording_properties(
            server_call_id=self.server_call_id,
            recording_id=recording_id,
        )

        return CallRecordingProperties._from_generated(recording_status_result)


    @distributed_trace()
    def join_call(
            self,
            source: CommunicationIdentifierModel, 
            subject, # type: str 
            callback_uri, # type: str 
            requested_media_types: List[MediaType],
            requested_call_events: List[EventSubscriptionType],
            **kwargs, # type: Any
    ): # type: (...) -> JoinCallResult

        request = JoinCallRequest(
            source = source,
            subject = subject,
            callback_uri = callback_uri,
            requested_media_types = requested_media_types,
            requested_call_events = requested_call_events,
            **kwargs
        )

        join_call_result = self.server_call_client.join_call(server_call_id=self.server_call_id,
        call_request=request)

        return JoinCallResult._from_generated(join_call_result)

    @distributed_trace()
    def add_participant(
            self,
            participant, # type: CommunicationIdentifier
            callback_uri, # type: str
            alternate_caller_id, # type: Optional[str]
            operation_context, # type: Optional[str]
            **kwargs # type: Any
        ): # type: (...) -> AddParticipantResult

        if not participant:
            raise ValueError("participant can not be None")

        add_participant_result = self.server_call_client.add_participant(
            server_call_id=self.server_call_id,
            participant=serialize_identifier(participant),
            alternate_caller_id=None if alternate_caller_id == None else PhoneNumberIdentifierModel(value=alternate_caller_id.properties['value']),
            callback_uri=callback_uri,
            operation_context=operation_context,
            **kwargs
        )

        return AddParticipantResult._from_generated(add_participant_result)

    @distributed_trace()
    def remove_participant(
            self,
            participant_id, # type: str
            **kwargs # type: Any
        ): # type: (...) -> None

        return self.server_call_client.remove_participant(
            server_call_id=self.server_call_id,
            participant_id=participant_id,
            **kwargs
        )
