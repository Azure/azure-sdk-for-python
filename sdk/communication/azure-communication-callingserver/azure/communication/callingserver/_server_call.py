# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any

from azure.core.tracing.decorator import distributed_trace

from ._generated.aio.operations import ServerCallsOperations
from ._generated.models import PlayAudioRequest
from ._models import PlayAudioResult


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
        audio_file_uri: str,
        audio_File_id: str,
        callback_uri: str,
        operation_context: str,
        **kwargs: Any
    ):
        # type: (...) -> PlayAudioResult
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
            loop = kwargs.get('loop', False),
            operation_context=operation_context,
            audio_file_id=audio_File_id,
            callback_uri=callback_uri
            **kwargs
        )

        play_audio_result = self.server_call_client.play_audio(
            server_call_id=self.server_call_id,
            request=request,
        )

        return PlayAudioResult._from_generated(play_audio_result)

    def close(self):
        # type: () -> None
        self.server_call_client.close()

    def __enter__(self):
        # type: () -> ServerCall
        self.server_call_client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self.server_call_client.__exit__(*args)  # pylint:disable=no-member
