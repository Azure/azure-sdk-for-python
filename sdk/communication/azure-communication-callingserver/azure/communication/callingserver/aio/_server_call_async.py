# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any

from azure.core.tracing.decorator_async import distributed_trace_async

from .._generated.aio.operations import ServerCallsOperations
from .._generated.models import PlayAudioRequest, PhoneNumberIdentifierModel
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
            loop = False,
            operation_context=operation_context,
            audio_file_id=audio_file_id,
            callback_uri=callback_uri
        )

        play_audio_result = await self.server_call_client.play_audio(
            server_call_id=self.server_call_id,
            request=request,
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

        add_participant_result = await self.server_call_client.add_participant(
            server_call_id=self.server_call_id,
            participant=serialize_identifier(participant),
            alternate_caller_id=None if alternate_caller_id == None else PhoneNumberIdentifierModel(value=alternate_caller_id.properties['value']),
            callback_uri=callback_uri,
            operation_context=operation_context,
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
