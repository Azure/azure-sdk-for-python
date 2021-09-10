# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any

from azure.core.tracing.decorator_async import distributed_trace_async

from .._generated.aio.operations import ServerCallsOperations
from .._generated.models import PlayAudioRequest, PhoneNumberIdentifierModel
from .._converters import PlayAudioRequestConverter, AddParticipantRequestConverter
from .._models import PlayAudioOptions, PlayAudioResult, AddParticipantResult
from .._communication_identifier_serializer import (deserialize_identifier,
                                                   serialize_identifier)

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

    @distributed_trace_async()
    async def play_audio(
            self,
            audio_file_uri, # type: str
            play_audio_options, # type: PlayAudioOptions
            **kwargs, # type: str: Any
        ): # type: (...) -> PlayAudioResult

        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")

        if not play_audio_options:
            raise ValueError("options can not be None")

        play_audio_request = PlayAudioRequestConverter.convert(audio_file_uri, play_audio_options)

        play_audio_result = await self.server_call_client.play_audio(
            server_call_id=self.server_call_id,
            request=play_audio_request,
            **kwargs
        )

        return PlayAudioResult._from_generated(play_audio_result)

    @distributed_trace_async()
    async def add_participant(
            self,
            participant,  # type: CommunicationIdentifier
            callback_uri,  # type: str
            alternate_caller_id, # type: Optional[str]
            operation_context, # type: Optional[str]
            **kwargs # type: Any
        ): # type: (...) -> AddParticipantResult

        if not participant:
            raise ValueError("participant can not be None")

        alternate_caller_id = None if alternate_caller_id == None else PhoneNumberIdentifierModel(value=alternate_caller_id)

        add_participant_request = AddParticipantRequestConverter.convert(
            participant = serialize_identifier(participant),
            alternate_caller_id = alternate_caller_id,
            operation_context = operation_context,
            callback_uri = callback_uri
            )

        add_participant_result = await self.server_call_client.add_participant(
            server_call_id=self.server_call_id,
            add_participant_request=add_participant_request,
            **kwargs
        )

        return AddParticipantResult._from_generated(add_participant_result)

    @distributed_trace_async()
    async def remove_participant(
            self,
            participant_id,  # type: str
            **kwargs # type: Any
        ): # type: (...) -> None

        return await self.server_call_client.remove_participant(
            server_call_id=self.server_call_id,
            participant_id=participant_id,
            **kwargs
        )


    async def close(self) -> None:
        """Close the :class:
        `~azure.communication.callingserver.aio.ServerCall` session.
        """
        await self.server_call_client.close()

    async def __aenter__(self) -> "ServerCall":
        await self.server_call_client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self.server_call_client.__aexit__(*args)
