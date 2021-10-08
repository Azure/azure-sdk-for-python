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
from ..utils._utils import CallingServerUtils
from .._communication_identifier_serializer import serialize_identifier
from .._converters import (
    AddParticipantRequestConverter,
    RemoveParticipantRequestConverter,
    CancelAllMediaOperationsConverter,
    TransferCallRequestConverter,
    CancelParticipantMediaOperationRequestConverter,
    PlayAudioRequestConverter,
    PlayAudioToParticipantRequestConverter
    )
from .._generated.models import (
    AddParticipantResult,
    CallConnectionProperties,
    CancelAllMediaOperationsResult,
    PhoneNumberIdentifierModel,
    PlayAudioResult
    )
from .._shared.models import CommunicationIdentifier
from .._generated.aio._azure_communication_calling_server_service import \
    AzureCommunicationCallingServerService  # pylint: disable=unused-import

if TYPE_CHECKING:
    from .._generated.aio.operations import CallConnectionsOperations
    from .._models import PlayAudioOptions

class CallConnection:
    def __init__(
            self,
            call_connection_id: str,
            call_connection_client: 'CallConnectionsOperations',
            callingserver_service_client: 'AzureCommunicationCallingServerService'
        ) -> None:

        self.call_connection_id = call_connection_id
        self._call_connection_client = call_connection_client
        self._callingserver_service_client = callingserver_service_client

    @distributed_trace_async()
    async def get_call(
            self,
            **kwargs: Any
        ) -> CallConnectionProperties:
        return await self._call_connection_client.get_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def hang_up(
            self,
            **kwargs: Any
        ) -> None:

        return await self._call_connection_client.hangup_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def cancel_all_media_operations(
            self,
            operation_context: Optional[str] = None,
            **kwargs: Any
        ) -> CancelAllMediaOperationsResult:

        cancel_all_media_operations_request = CancelAllMediaOperationsConverter.convert(operation_context)

        return await self._call_connection_client.cancel_all_media_operations(
            call_connection_id=self.call_connection_id,
            cancel_all_media_operation_request=cancel_all_media_operations_request,
            **kwargs
        )

    @distributed_trace_async()
    async def play_audio(
            self,
            audio_file_uri: str,
            play_audio_options: 'PlayAudioOptions',
            **kwargs: Any
        ) -> PlayAudioResult:

        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")

        if not CallingServerUtils.is_valid_url(audio_file_uri):
            raise ValueError("audio_file_uri is invalid")

        if not play_audio_options:
            raise ValueError("options can not be None")

        if not play_audio_options.audio_file_id:
            raise ValueError("audio_file_id can not be None")

        if not CallingServerUtils.is_valid_url(play_audio_options.callback_uri):
            raise ValueError("callback_uri is invalid")

        play_audio_request = PlayAudioRequestConverter.convert(audio_file_uri, play_audio_options)

        return await self._call_connection_client.play_audio(
            call_connection_id=self.call_connection_id,
            request=play_audio_request,
            **kwargs
        )

    @distributed_trace_async()
    async def add_participant(
            self,
            participant: CommunicationIdentifier,
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
            operation_context=operation_context
            )

        return await self._call_connection_client.add_participant(
            call_connection_id=self.call_connection_id,
            add_participant_request=add_participant_request,
            **kwargs
        )

    @distributed_trace_async()
    async def remove_participant(
            self,
            participant: CommunicationIdentifier,
            **kwargs: Any
        ) -> None:

        remove_participant_request = RemoveParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return await self._call_connection_client.remove_participant(
            call_connection_id=self.call_connection_id,
            remove_participant_request=remove_participant_request,
            **kwargs
        )

    @distributed_trace_async()
    async def play_audio_to_participant(
            self,
            participant: CommunicationIdentifier,
            audio_file_uri: str,
            play_audio_options: 'PlayAudioOptions',
            **kwargs: Any
        ) -> PlayAudioResult:

        if not participant:
            raise ValueError("participant can not be None")

        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")

        if not CallingServerUtils.is_valid_url(audio_file_uri):
            raise ValueError("audio_file_uri is invalid")

        if not play_audio_options:
            raise ValueError("play_audio_options can not be None")

        if not play_audio_options.audio_file_id:
            raise ValueError("audio_file_id can not be None")

        if not CallingServerUtils.is_valid_url(play_audio_options.callback_uri):
            raise ValueError("callback_uri is invalid")

        play_audio_to_participant_request = PlayAudioToParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant),
            audio_file_uri=audio_file_uri,
            play_audio_options=play_audio_options
            )

        return await self._call_connection_client.participant_play_audio(
            call_connection_id=self.call_connection_id,
            play_audio_to_participant_request=play_audio_to_participant_request,
            **kwargs
        )

    @distributed_trace_async()
    async def cancel_participant_media_operation(
            self,
            participant: CommunicationIdentifier,
            media_operation_id: str,
            **kwargs: Any
        )-> None:

        if not participant:
            raise ValueError("participant can not be None")

        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        cancel_media_operation_request = CancelParticipantMediaOperationRequestConverter.convert(
            identifier=serialize_identifier(participant),
            media_operation_id=media_operation_id
            )

        return await self._call_connection_client.cancel_participant_media_operation(
            call_connection_id=self.call_connection_id,
            cancel_media_operation_request=cancel_media_operation_request,
            **kwargs
        )

    @distributed_trace_async()
    async def transfer_call(
            self,
            target_participant: CommunicationIdentifier,
            user_to_user_information: Optional[str] = None,
            **kwargs: Any
        )-> None:

        if not target_participant:
            raise ValueError("target_participant can not be None")

        transfer_call_request = TransferCallRequestConverter.convert(
            target_participant=serialize_identifier(target_participant),
            user_to_user_information=user_to_user_information
            )

        return await self._call_connection_client.transfer(
            call_connection_id=self.call_connection_id,
            transfer_call_request=transfer_call_request,
            **kwargs
        )

    async def close(self) -> None:
        await self._callingserver_service_client.close()

    async def __aenter__(self) -> 'CallConnection':
        await self._callingserver_service_client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._callingserver_service_client.__aexit__(*args)
