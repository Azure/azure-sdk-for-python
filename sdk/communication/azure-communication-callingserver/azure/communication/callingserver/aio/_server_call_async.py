# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=unsubscriptable-object
# disabled unsubscriptable-object because of pylint bug referenced here:
# https://github.com/PyCQA/pylint/issues/3882

from typing import TYPE_CHECKING, Any, Optional  # pylint: disable=unused-import

from azure.core.tracing.decorator_async import distributed_trace_async

from .._communication_identifier_serializer import serialize_identifier
from .._converters import (AddParticipantRequestConverter,
                          CancelMediaOperationRequestConverter,
                           PlayAudioRequestConverter)
from .._generated.models import (AddParticipantResult,
                                 PhoneNumberIdentifierModel,
                                 PlayAudioResult)
from .._generated.aio._azure_communication_calling_server_service import \
    AzureCommunicationCallingServerService  # pylint: disable=unused-import

if TYPE_CHECKING:
    from .._generated.aio.operations import ServerCallsOperations
    from .._models import PlayAudioOptions
    from .._shared.models import CommunicationIdentifier

class ServerCall:

    def __init__(
        self,
        server_call_id: str,
        server_call_client: 'ServerCallsOperations',
        callingserver_service_client: 'AzureCommunicationCallingServerService'
    ) -> None:
        self.server_call_id = server_call_id
        self._server_call_client = server_call_client
        self._callingserver_service_client = callingserver_service_client

    @distributed_trace_async()
    async def play_audio(
            self,
            audio_file_uri: str,
            play_audio_options: 'PlayAudioOptions',
            **kwargs: Any
        ) -> PlayAudioResult:

        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")

        if not play_audio_options:
            raise ValueError("options can not be None")

        play_audio_request = PlayAudioRequestConverter.convert(audio_file_uri, play_audio_options)

        return await self._server_call_client.play_audio(
            server_call_id=self.server_call_id,
            request=play_audio_request,
            **kwargs
        )

    @distributed_trace_async()
    async def add_participant(
            self,
            participant: 'CommunicationIdentifier',
            callback_uri: str,
            alternate_caller_id: Optional[str] = None,
            operation_context: Optional[str] = None,
            **kwargs: Any
        ) -> AddParticipantResult:

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

        return await self._server_call_client.add_participant(
            server_call_id=self.server_call_id,
            add_participant_request=add_participant_request,
            **kwargs
        )

    @distributed_trace_async()
    async def remove_participant(
            self,
            participant_id: str,
            **kwargs: Any
        ) -> None:

        return await self._server_call_client.remove_participant(
            server_call_id=self.server_call_id,
            participant_id=participant_id,
            **kwargs
        )

    @distributed_trace_async()
    async def cancel_media_operation(
            self,
            media_operation_id: str,
            **kwargs: Any
        ) -> None:

        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        cancel_media_operation_request = CancelMediaOperationRequestConverter.convert(
            media_operation_id=media_operation_id
            )

        return await self._server_call_client.cancel_media_operation(
            server_call_id=self.server_call_id,
            cancel_media_operation_request=cancel_media_operation_request,
            **kwargs
        )

    @distributed_trace_async()
    async def play_audio_to_participant(
            self,
            participant_id: str,
            audio_file_uri: str,
            play_audio_options: 'PlayAudioOptions',
            **kwargs: Any
        ) -> PlayAudioResult:

        if not participant_id:
            raise ValueError("participant_id can not be None")
        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")

        if not play_audio_options:
            raise ValueError("options can not be None")

        play_audio_request = PlayAudioRequestConverter.convert(audio_file_uri, play_audio_options)

        return await self._server_call_client.participant_play_audio(
            server_call_id=self.server_call_id,
            participant_id=participant_id,
            play_audio_request=play_audio_request,
            **kwargs
        )

    @distributed_trace_async()
    async def cancel_participant_media_operation(
            self,
            participant_id: str,
            media_operation_id: str,
            **kwargs: Any
        ) -> None:

        if not participant_id:
            raise ValueError("participant_id can not be None")

        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        cancel_media_operation_request = CancelMediaOperationRequestConverter.convert(
            media_operation_id=media_operation_id
            )

        return await self._server_call_client.cancel_participant_media_operation(
            server_call_id=self.server_call_id,
            participant_id=participant_id,
            cancel_media_operation_request=cancel_media_operation_request,
            **kwargs
        )

    async def close(self) -> None:
        await self._callingserver_service_client.close()

    async def __aenter__(self) -> 'ServerCall':
        await self._callingserver_service_client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._callingserver_service_client.__aexit__(*args)
