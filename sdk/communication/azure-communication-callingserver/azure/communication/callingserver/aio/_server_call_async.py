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
                           PlayAudioRequestConverter)
from .._generated.models import (AddParticipantResult,
                                 PhoneNumberIdentifierModel,
                                 PlayAudioResult)

if TYPE_CHECKING:
    from .._generated.aio.operations import ServerCallsOperations
    from .._models import PlayAudioOptions
    from .._shared.models import CommunicationIdentifier

class ServerCall:

    def __init__(
        self,
        server_call_id: str,
        server_call_client: 'ServerCallsOperations'
    ) -> None:
        self.server_call_id = server_call_id
        self._server_call_client = server_call_client

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


    async def close(self) -> None:
        """Close the :class:
        `~azure.communication.callingserver.aio.ServerCall` session.
        """
        await self._server_call_client.close()

    async def __aenter__(self) -> "ServerCall":
        await self._server_call_client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._server_call_client.__aexit__(*args)
