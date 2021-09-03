# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any

from azure.core.tracing.decorator import distributed_trace

from ._generated.operations import CallConnectionsOperations

from ._generated.models import CancelAllMediaOperationsRequest, PlayAudioRequest, AddParticipantRequest, PhoneNumberIdentifierModel, CommunicationIdentifierModel

class CallConnection(object):
    def __init__(
        self,
        call_connection_id: str,  # type: str
        call_connection_client: CallConnectionsOperations,  # type: AsyncTokenCredential
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        self.call_connection_id = call_connection_id
        self.call_connection_client = call_connection_client

    @distributed_trace()
    def hang_up(
        self,
        **kwargs: Any
    ):
        # type: (...) -> None

        return self.call_connection_client.hangup_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    
    @distributed_trace()
    def cancel_all_media_operations(self,
    operation_context,
    **kwargs # type: Any
    ):

        request = CancelAllMediaOperationsRequest(**kwargs)

        return self.call_connection_client.cancel_all_media_operations(
            call_connection_id=self.call_connection_id,
             cancel_all_media_operation_request=request,
             **kwargs
             )
        

    @distributed_trace()
    def play_audio(
        self,
        audio_file_uri: str,
        audio_File_id: str,
        callback_uri: str,
        operation_context: str,
        loop: bool,
        **kwargs: Any
    ):
        try:
            if not audio_file_uri.lower().startswith('http'):
                audio_file_uri = "https://" + audio_file_uri
        except AttributeError:
            raise ValueError("URL must be a string.")

        if not audio_File_id:
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
            audio_file_id=audio_File_id,
            callback_uri=callback_uri,
            **kwargs
        )

        return self.call_connection_client.play_audio(
            call_connection_id=self.call_connection_id,
            request=request,
        )


    @distributed_trace()
    def add_participant(self,
    participant: CommunicationIdentifierModel,
    alternate_call_id: PhoneNumberIdentifierModel,
    operation_context: str,
    **kwargs: Any
    ):

        request = AddParticipantRequest(alternate_caller_id=alternate_call_id,
        participant=participant,
        operation_context=operation_context,
        callback_uri=None, 
        **kwargs)

        return self.call_connection_client.add_participant(call_connection_id=self.call_connection_id, 
        add_participant_request=request)


    @distributed_trace()
    def remove_participant(self,
    participant_id: str,
    **kwargs: Any
    ):
        if not participant_id:
            raise ValueError("participant_id can not be None")

        return self.call_connection_client.remove_participant(call_connection_id=self.call_connection_id,
        participant_id=participant_id,
        **kwargs)


    def close(self):
        # type: () -> None
        self.call_connection_client.close()

    def __enter__(self):
        # type: () -> CallConnection
        self.call_connection_client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self.call_connection_client.__exit__(*args)  # pylint:disable=no-member
