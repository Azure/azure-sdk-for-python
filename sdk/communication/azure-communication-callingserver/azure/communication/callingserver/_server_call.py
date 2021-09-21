# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Any, Optional  # pylint: disable=unused-import

from azure.core.tracing.decorator import distributed_trace

from ._communication_identifier_serializer import serialize_identifier
from ._converters import (AddParticipantRequestConverter,
                          CancelMediaOperationRequestConverter,
                          PlayAudioRequestConverter)
from ._generated.models import (AddParticipantResult,
                                PhoneNumberIdentifierModel,
                                PlayAudioResult,
                                StartCallRecordingRequest,
                                StartCallRecordingResult,
                                CallRecordingProperties)

from azure.core.pipeline.transport import AsyncHttpResponse

if TYPE_CHECKING:
    from ._generated.operations import ServerCallsOperations
    from ._models import PlayAudioOptions
    from ._shared.models import CommunicationIdentifier

class ServerCall(object):

    def __init__(
        self,
        server_call_id,  # type: str
        server_call_client  # type: ServerCallsOperations
    ):  # type: (...) -> None
        self.server_call_id = server_call_id
        self._server_call_client = server_call_client

    @distributed_trace()
    def play_audio(
        self,
        audio_file_uri,  # type: str
        play_audio_options,  # type: PlayAudioOptions
        **kwargs  # type: Any
    ):  # type: (...) -> PlayAudioResult

        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")

        if not play_audio_options:
            raise ValueError("options can not be None")

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

        if not play_audio_options.operation_context:
            raise ValueError("operation_context can not be None")

        play_audio_request = PlayAudioRequestConverter.convert(
            audio_file_uri, play_audio_options)

        return self._server_call_client.play_audio(
            server_call_id=self.server_call_id,
            request=play_audio_request,
            **kwargs
        )

    @distributed_trace()
    def start_recording(
        self,
        server_call_id,  # type: str
        recording_state_callback_uri,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> StartCallRecordingResult

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        start_call_recording_request = StartCallRecordingRequest(
            recording_state_callback_uri=recording_state_callback_uri,
            **kwargs
        )

        return self._server_call_client.start_recording(
            server_call_id=self.server_call_id,
            request=start_call_recording_request,
            **kwargs
        )

    @distributed_trace()
    def pause_recording(
        self,
        server_call_id,  # type: str
        recording_id,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> AsyncHttpResponse

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        return self._server_call_client.pause_recording(
            server_call_id=self.server_call_id,
            recording_id=recording_id,
            **kwargs
        )

    @distributed_trace()
    def resume_recording(
        self,
        server_call_id,  # type: str
        recording_id,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> AsyncHttpResponse

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        return self._server_call_client.resume_recording(
            server_call_id=self.server_call_id,
            recording_id=recording_id,
            **kwargs
        )

    @distributed_trace()
    def stop_recording(
        self,
        server_call_id,  # type: str
        recording_id,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> AsyncHttpResponse

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        return self._server_call_client.stop_recording(
            server_call_id=self.server_call_id,
            recording_id=recording_id,
            **kwargs
        )

    @distributed_trace()
    def get_recording_properities(
        self,
        server_call_id,  # type: str
        recording_id,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> CallRecordingProperties

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        return self._server_call_client.get_recording_properties(
            server_call_id=self.server_call_id,
            recording_id=recording_id,
            **kwargs
        )

    @distributed_trace()
    def add_participant(
        self,
        participant,  # type: CommunicationIdentifier
        callback_uri,  # type: str
        alternate_caller_id=None,  # type: Optional[str]
        operation_context=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):  # type: (...) -> AddParticipantResult

        if not participant:
            raise ValueError("participant can not be None")

        alternate_caller_id = (None
                               if alternate_caller_id is None
                               else PhoneNumberIdentifierModel(value=alternate_caller_id))

        add_participant_request = AddParticipantRequestConverter.convert(
            participant=serialize_identifier(participant),
            alternate_caller_id=alternate_caller_id,
            operation_context=operation_context,
            callback_uri=callback_uri
        )

        return self._server_call_client.add_participant(
            server_call_id=self.server_call_id,
            add_participant_request=add_participant_request,
            **kwargs
        )

    @distributed_trace()
    def remove_participant(
        self,
        participant_id,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> None

        return self._server_call_client.remove_participant(
            server_call_id=self.server_call_id,
            participant_id=participant_id,
            **kwargs
        )

    @distributed_trace()
    def cancel_media_operation(
            self,
            media_operation_id,  # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> None

        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        cancel_media_operation_request = CancelMediaOperationRequestConverter.convert(
            media_operation_id=media_operation_id
            )
        return self._server_call_client.cancel_media_operation(
            server_call_id=self.server_call_id,
            cancel_media_operation_request=cancel_media_operation_request,
            **kwargs
        )

    @distributed_trace()
    def cancel_participant_media_operation(
            self,
            participant_id,  # type: str
            media_operation_id,  # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> None

        if not participant_id:
            raise ValueError("participant_id can not be None")

        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        cancel_media_operation_request = CancelMediaOperationRequestConverter.convert(
            media_operation_id=media_operation_id
            )

        return self._server_call_client.cancel_participant_media_operation(
            server_call_id=self.server_call_id,
            participant_id=participant_id,
            cancel_media_operation_request=cancel_media_operation_request,
            **kwargs
        )
