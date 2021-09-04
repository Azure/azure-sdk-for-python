# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .._models import JoinCallOptions, PlayAudioOptions
from .._shared.models import CommunicationIdentifier
from .._generated.models import JoinCallRequest, PlayAudioRequest

class JoinCallRequestConverter(object):
    @classmethod
    def convert(self, source: CommunicationIdentifier, join_call_options: JoinCallOptions):
        if not source:
            raise ValueError("source can not be None")
        if not join_call_options:
            raise ValueError("join_call_options can not be None")

        return JoinCallRequest(
            source=source,
            callback_uri=join_call_options.callback_uri,
            requested_media_types=join_call_options.requested_media_types,
            requested_call_events=join_call_options.requested_call_events,
            subject= join_call_options.subject)


class PlayAudioRequestConverter(object):
    @classmethod
    def convert(self, play_audio_options: PlayAudioOptions):

        if not play_audio_options:
            raise ValueError("playaudio_options can not be None")

        return PlayAudioRequest(
            audio_file_uri=play_audio_options.audio_file_uri,
            loop = play_audio_options.loop,
            operation_context=play_audio_options,
            audio_file_id=play_audio_options.audio_file_id,
            callback_uri=play_audio_options.callback_uri)
