# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, List, TYPE_CHECKING  # pylint: disable=unused-import
from urllib.parse import urlparse
from azure.core.credentials import TokenCredential

from ._version import SDK_MONIKER
from ._api_versions import DEFAULT_VERSION

from ._generated._client import AzureCommunicationCallAutomationService
from ._shared.utils import get_authentication_policy, parse_connection_str

from ._generated.models._models import (
PlayRequest, RecognizeRequest, RecognizeOptions, DtmfOptions, CommunicationIdentifierModel, 
PlaySource as PlaySourceInternal, FileSource as FileSourceInternal, 
TextSource as TextSourceInternal
)

from ._generated.models import PlaySourceType
from ._models import CallMediaRecognizeOptions, CallMediaRecognizeDtmfOptions, CallMediaRecognizeChoiceOptions, PlaySource, FileSource, TextSource

if TYPE_CHECKING:
    from ._generated.operations import CallMediaOperations

class CallMediaClient(object):
    def __init__(
        self,
        endpoint,  # type: str
        credential,  # type: TokenCredential
        call_connection_id,  # type: str
        call_media_client,  # type: CallMediaOperations
        **kwargs
    ):
        
        # type: (...) -> None
        if not credential:
            raise ValueError("credential can not be None")

        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(endpoint.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._endpoint = endpoint
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._credential = credential

        self.call_connection_id = call_connection_id
        self._call_media_client = call_media_client

        self._client = AzureCommunicationCallAutomationService(
            self._endpoint,
            api_version = self._api_version,
            authentication_policy=get_authentication_policy(endpoint, credential),
            sdk_moniker = SDK_MONIKER,
            **kwargs)

    def play_to_all(
        self, 
        play_source, 
        **kwargs
    ):
        """
        Play to all participants.

        :param play_source: A PlaySource representing the source to play.
        """
        self.play(play_source=play_source, play_to=[])

    def play(
        self, 
        play_source: PlaySource, 
        play_to: List[CommunicationIdentifierModel],
        **kwargs
    ):
        """
        Play.

        :param play_source: Required. A PlaySource representing the source to play.
        :type play_source: PlaySource
        :param play_to: Required. The targets to play to.
        :type play_to: 

        """
        play_source_internal = PlaySourceInternal()
        if isinstance(play_source, FileSource):
            file_source = FileSourceInternal(uri=play_source.uri)
            play_source_internal.source_type = PlaySourceType.FILE
            play_source_internal.file_source = file_source
            play_source_internal.play_source_id = play_source.play_source_id
        
        if isinstance(play_source, TextSource):
            text_source = TextSourceInternal(text=play_source.text)
            text_source.voice_gender = play_source.voice_gender
            text_source.source_locale = play_source.source_locale
            text_source.voice_name = play_source.voice_name
            play_source_internal.source_type = PlaySourceType.TEXT
            play_source_internal.play_source_id = play_source.play_source_id
            play_source_internal.text_source = text_source

        play_request = PlayRequest(play_source_internal, play_to)
        self._client.call_media.play(self.call_connection_id, play_request)


    def start_recognizing(
        self, 
        recognize_options: CallMediaRecognizeOptions
    ):
        """
        Recognize tones.

        :param recognize_options:  Different attributes for recognize.
        :type recognize_options: azure.communication..RecognizeOptions
        :return: None
        :rtype: None
        """

        options = RecognizeOptions(
            target_participant=recognize_options.target_participant, 
            interrupt_prompt=recognize_options.interrupt_prompt, 
            initial_silence_timeout_in_seconds=recognize_options.initial_silence_timeout
        )

        if isinstance(recognize_options, CallMediaRecognizeDtmfOptions):
            options.dtmf_options = DtmfOptions(
                inter_tone_timeout_in_seconds=recognize_options.inter_tone_timeout,
                max_tones_to_collect=recognize_options.max_tones_to_collect,
                stop_tones=recognize_options.stop_dtmf_tones
            )

        if isinstance(recognize_options, CallMediaRecognizeChoiceOptions):
            options.choices = recognize_options.recognize_choices

        recognize_request = RecognizeRequest(
            recognize_input_type=recognize_options.input_type,
            play_prompt=recognize_options.play_prompt,
            interrupt_call_media_operation=recognize_options.interrupt_call_media_operation,
            operation_context=recognize_options.operation_context,
            recognize_options=recognize_options
        )

        self._client.call_media.recognize(self.call_connection_id, recognize_request)


    def cancel_all_media_operations(
        self
    ):
        """
        Cancels all the queued media operations.
        
        """

        self._client.call_media.cancel_all_media_operations(self.call_connection_id)