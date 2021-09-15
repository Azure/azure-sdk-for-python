# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Any, Optional  # pylint: disable=unused-import

from azure.core.tracing.decorator_async import distributed_trace_async

from .._communication_identifier_serializer import serialize_identifier
from .._converters import (AddParticipantRequestConverter,
                           PlayAudioRequestConverter)
from .._generated.models import (AddParticipantResult,
                                 CancelAllMediaOperationsRequest,
                                 CancelAllMediaOperationsResult,
                                 PhoneNumberIdentifierModel, PlayAudioResult)
from .._shared.models import CommunicationIdentifier

if TYPE_CHECKING:
    from .._generated.aio.operations import CallConnectionsOperations
    from .._models import PlayAudioOptions

class CallConnection(object):
    def __init__(
            self,
            call_connection_id: str,
            call_connection_client: CallConnectionsOperations
        ) -> None:

        self.call_connection_id = call_connection_id
        self._call_connection_client = call_connection_client

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
            operation_context: Optional[str],
            **kwargs: Any
        ) -> CancelAllMediaOperationsResult:

        if operation_context is not None:
            kwargs['operation_context'] = operation_context
        request = CancelAllMediaOperationsRequest(**kwargs)

        return await self._call_connection_client.cancel_all_media_operations(
            call_connection_id=self.call_connection_id,
            cancel_all_media_operation_request=request,
            **kwargs
        )

    @distributed_trace_async()
    async def play_audio(
            self,
            audio_file_uri: str,
            play_audio_options: PlayAudioOptions,
            **kwargs: Any
        ) -> PlayAudioResult:

        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")

        if not play_audio_options:
            raise ValueError("options can not be None")

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
            alternate_caller_id: Optional[str],
            operation_context: Optional[str],
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
            participant_id: str,
            **kwargs: Any
        ) -> None:

        return await self._call_connection_client.remove_participant(
            call_connection_id=self.call_connection_id,
            participant_id=participant_id,
            **kwargs
        )

    async def close(self) -> None:
        """Close the :class:
        `~azure.communication.callingserver.aio.CallConnection` session.
        """
        await self._call_connection_client.close()

    async def __aenter__(self) -> "CallConnection":
        await self._call_connection_client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._call_connection_client.__aexit__(*args)
