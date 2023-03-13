# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import List, TYPE_CHECKING  # pylint: disable=unused-import

from ._api_versions import DEFAULT_VERSION

from ._generated.models._models import (
    PlayRequest, RecognizeRequest, RecognizeOptions, DtmfOptions, PlayOptions,
    PlaySource as PlaySourceInternal, FileSource as FileSourceInternal
)

from ._generated.models import PlaySourceType
from ._models import (
    CallMediaRecognizeOptions, CallMediaRecognizeDtmfOptions,
    PlaySource, FileSource
)

from ._shared.models import (
    CommunicationIdentifier,
    serialize_identifier
)

if TYPE_CHECKING:
    from ._generated.operations import CallMediaOperations


class CallMedia(object):
    """A client to interact with media of ongoing call.

    :param str call_connection_id:
     Call Connection Id of ongoing call.
    :param ~azure.communication.callautomation._generated.operations.CallMediaOperations call_media_operations:
     The REST version of media client.

    :keyword api_version: Azure Communication Call Automation API version.
     Default value is "2023-01-15-preview".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """
    def __init__(# pylint:disable=missing-client-constructor-parameter-credential
        self,
        call_connection_id: str,
        call_media_operations,   # type: CallMediaOperations
        **kwargs
    ) -> None:
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)

        self.call_connection_id = call_connection_id
        self._call_media_operations = call_media_operations

    @staticmethod
    def _create_play_source_internal(play_source):
        if isinstance(play_source, FileSource):
            file_source = FileSourceInternal(uri=play_source.uri)
            return PlaySourceInternal(
                source_type=PlaySourceType.FILE,
                file_source=file_source,
                play_source_id=play_source.play_source_id
            )
        return None

    def play_to_all(
        self,
        play_source: PlaySource,
        **kwargs
    ) -> None:
        """
        Play to all participants.

        :param play_source: A PlaySource representing the source to play.
        :type play_source: ~azure.communication.callautomation.PlaySource

        :return: None
        :type: None
        """
        if not play_source:
            raise ValueError('play_source cannot be None.')

        self.play(play_source=play_source, play_to=[], **kwargs)

    def play(
        self,
        play_source: PlaySource,
        play_to: List[CommunicationIdentifier],
        **kwargs
    ) -> None:
        """
        Play.

        :param play_source: Required. A PlaySource representing the source to play.
        :type play_source: PlaySource
        :param play_to: Required. The targets to play to.
        :type play_to: list[~azure.communication.callautomation.models.CommunicationIdentifier]

        :return: None
        :type: None
        """

        if not play_source:
            raise ValueError('play_source cannot be None.')

        play_request = PlayRequest(
            play_source_info=self._create_play_source_internal(play_source),
            play_to=[serialize_identifier(identifier)
                     for identifier in play_to],
            play_options=PlayOptions(loop=kwargs.get('loop', False))
        )
        self._call_media_operations.play(self.call_connection_id, play_request)

    def start_recognizing(
        self,
        recognize_options: CallMediaRecognizeOptions
    ) -> None:
        """
        Recognize tones.

        :param recognize_options:  Different attributes for recognize.
        :type recognize_options: ~azure.communication.callautomation.CallMediaRecognizeOptions

        :return: None
        :rtype: None
        """

        if not recognize_options:
            raise ValueError('recognize_options cannot be None.')

        options = RecognizeOptions(
            target_participant=serialize_identifier(
                recognize_options.target_participant),
            interrupt_prompt=recognize_options.interrupt_prompt,
            initial_silence_timeout_in_seconds=recognize_options.initial_silence_timeout
        )

        if isinstance(recognize_options, CallMediaRecognizeDtmfOptions):
            options.dtmf_options = DtmfOptions(
                inter_tone_timeout_in_seconds=recognize_options.inter_tone_timeout,
                max_tones_to_collect=recognize_options.max_tones_to_collect,
                stop_tones=recognize_options.stop_dtmf_tones
            )

        play_source = recognize_options.play_prompt

        recognize_request = RecognizeRequest(
            recognize_input_type=recognize_options.input_type,
            play_prompt=self._create_play_source_internal(play_source),
            interrupt_call_media_operation=recognize_options.interrupt_call_media_operation,
            operation_context=recognize_options.operation_context,
            recognize_options=options
        )

        self._call_media_operations.recognize(
            self.call_connection_id, recognize_request)

    def cancel_all_media_operations(
        self
    ) -> None:
        """
        Cancels all the queued media operations.

        :return: None
        :type: None
        """
        self._call_media_operations.cancel_all_media_operations(
            self.call_connection_id)
