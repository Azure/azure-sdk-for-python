# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any

from azure.core.tracing.decorator import distributed_trace

from ._generated.aio.operations import ServerCallsOperations
from ._generated.models import PlayAudioRequest, StartCallRecordingRequest, StartCallRecordingResult
from ._generated.models._models import PauseCallRecordingResult, ResumeCallRecordingResult, StopCallRecordingResult, \
        DownloadContentResult, CallRecordingStatusResult
from ._generated.operations._content_downloader import ContentDownloader
from ._models import PlayAudioResult


class ServerCall(object):

    def __init__(
        self,
        server_call_id: str,  # type: str
        server_call_client: ServerCallsOperations,  # type: AsyncTokenCredential,
        content_downloader_client: ContentDownloader,
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        self.server_call_id = server_call_id
        self.server_call_client = server_call_client
        self.content_downloader_client = content_downloader_client

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

    @distributed_trace()
    def start_recording(
            self,
            server_call_id: str,
            recording_state_callback_uri: str,
            **kwargs: Any
    ):
        # type: (...) -> StartCallRecordingResult

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        request = StartCallRecordingRequest(
            recording_state_callback_uri=recording_state_callback_uri,
            **kwargs
        )

        start_recording_result = self.server_call_client.start_recording(
            server_call_id=self.server_call_id,
            request=request
        )

        return StartCallRecordingResult._from_generated(start_recording_result)


    @distributed_trace()
    def pause_recording(
            self,
            server_call_id: str,
            recording_id: str,
            **kwargs: Any
    ):
        # type: (...) -> PauseCallRecordingResult

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        pause_recording_result = self.server_call_client.pause_recording(
            server_call_id=self.server_call_id,
            recording_id=recording_id,
        )

        return PauseCallRecordingResult._from_generated(pause_recording_result)

    @distributed_trace()
    def resume_recording(
            self,
            server_call_id: str,
            recording_id: str,
            **kwargs: Any
    ):
        # type: (...) -> ResumeCallRecordingResult

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        resume_recording_result = self.server_call_client.resume_recording(
            server_call_id=self.server_call_id,
            recording_id=recording_id,
        )

        return ResumeCallRecordingResult._from_generated(resume_recording_result)

    @distributed_trace()
    def stop_recording(
            self,
            server_call_id: str,
            recording_id: str,
            **kwargs: Any
    ):
        # type: (...) -> StopCallRecordingResult

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        stop_recording_result = self.server_call_client.stop_recording(
            server_call_id=self.server_call_id,
            recording_id=recording_id,
        )

        return StopCallRecordingResult._from_generated(stop_recording_result)

    @distributed_trace()
    def get_recording_status(
            self,
            server_call_id: str,
            recording_id: str,
            **kwargs: Any
    ):
        # type: (...) -> CallRecordingStatusResult

        if not server_call_id:
            raise ValueError("server_call_id cannot be None")

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        recording_status_result = self.server_call_client.get_recording_properties(
            server_call_id=self.server_call_id,
            recording_id=recording_id,
        )
        return CallRecordingStatusResult._from_generated(recording_status_result)

    @distributed_trace()
    def download_content(
            self,
            content_url: str,
            **kwargs: Any
    ):
        # type: (...) -> DownloadContentResult

        if not content_url:
            raise ValueError("content_url cannot be None")


        content_url_result = self.content_downloader_client.download_content(
            content_url=content_url,
        )

        return DownloadContentResult._from_generated(content_url_result)

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
