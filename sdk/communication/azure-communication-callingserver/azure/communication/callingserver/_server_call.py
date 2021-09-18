# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Any, Optional  # pylint: disable=unused-import
from urllib.parse import urlparse

from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline.transport import AsyncHttpResponse

from ._communication_identifier_serializer import serialize_identifier
from ._converters import (AddParticipantRequestConverter,
                          CancelMediaOperationRequestConverter,
                          PlayAudioRequestConverter)
from ._generated.models import (AddParticipantResult,
                                CallRecordingProperties,
                                CommunicationIdentifierModel,
                                PhoneNumberIdentifierModel,
                                PlayAudioResult,
                                StartCallRecordingRequest,
                                StartCallRecordingResult)

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

        play_audio_request = PlayAudioRequestConverter.convert(audio_file_uri, play_audio_options)

        return self._server_call_client.play_audio(
            server_call_id=self.server_call_id,
            request=play_audio_request,
            **kwargs
        )

    @distributed_trace()
    def start_recording(
            self,
            recording_state_callback_uri, # type: str
            **kwargs, # type: Any
    ): # type: (...) -> StartCallRecordingResult

        if not recording_state_callback_uri:
            raise ValueError("recording_state_callback_uri cannot be None")

        if not bool(urlparse(recording_state_callback_uri).netloc):
            raise ValueError("recording_state_callback_uri has to be an absolute URL")

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
            recording_id, # type: str
            **kwargs, # type: Any
    ): # type: (...) -> AsyncHttpResponse

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
            recording_id, # type: str
            **kwargs, # type: Any
    ): # type: (...) -> AsyncHttpResponse

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
            recording_id, # type: str
            **kwargs, # type: Any
    ): # type: (...) -> AsyncHttpResponse

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
            recording_id, # type: str
            **kwargs, # type: Any
    ): # type: (...) -> CallRecordingProperties

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
            alternate_caller_id,  # type: Optional[str]
            operation_context,  # type: Optional[str]
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
