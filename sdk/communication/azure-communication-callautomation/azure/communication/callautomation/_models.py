# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, List, Optional, Union

from ._generated.models import (
CallLocator,
StartCallRecordingRequest as StartCallRecordingRequestRest,
RecordingContentType, RecordingChannelType, RecordingFormatType,
CommunicationIdentifierModel,
RecordingStorageType,
RecognizeInputType
)

class ServerCallLocator(object):
    def __init__(
        self,
        *,
        locatorid: str,
        **kwargs: Any
    ) -> None:

        super().__init__(**kwargs)
        self.id = locatorid
        self.kind = "serverCallLocator"

    def _to_generated(self):

        return CallLocator( kind=self.kind,
        server_call_id=self.id
        )

class GroupCallLocator(object):
    def __init__(
        self,
        *,
        locatorid: str,
        **kwargs: Any
    ) -> None:

        super().__init__(**kwargs)
        self.id = locatorid
        self.kind = "groupCallLocator"

    def _to_generated(self):

        return CallLocator( kind=self.kind,
        group_call_id=self.id
        )

class StartCallRecordingRequest(object):
    def __init__(
        self,
        *,
        call_locator: ServerCallLocator|GroupCallLocator,
        recording_state_callback_uri: Optional[str] = None,
        recording_content_type: Optional[Union[str, "RecordingContentType"]] = None,
        recording_channel_type: Optional[Union[str, "RecordingChannelType"]] = None,
        recording_format_type: Optional[Union[str, "RecordingFormatType"]] = None,
        audio_channel_participant_ordering: Optional[List["CommunicationIdentifierModel"]] = None,
        recording_storage_type: Optional[Union[str, "RecordingStorageType"]] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword call_locator: The call locator. Required.
        :paramtype call_locator: ~azure.communication.callautomation.models.CallLocator
        :keyword recording_state_callback_uri: The uri to send notifications to.
        :paramtype recording_state_callback_uri: str
        :keyword recording_content_type: The content type of call recording. Known values are: "audio"
         and "audioVideo".
        :paramtype recording_content_type: str or
         ~azure.communication.callautomation.models.RecordingContentType
        :keyword recording_channel_type: The channel type of call recording. Known values are: "mixed"
         and "unmixed".
        :paramtype recording_channel_type: str or
         ~azure.communication.callautomation.models.RecordingChannelType
        :keyword recording_format_type: The format type of call recording. Known values are: "wav",
         "mp3", and "mp4".
        :paramtype recording_format_type: str or
         ~azure.communication.callautomation.models.RecordingFormatType
        :keyword audio_channel_participant_ordering: The sequential order in which audio channels are
         assigned to participants in the unmixed recording.
         When 'recordingChannelType' is set to 'unmixed' and `audioChannelParticipantOrdering is not
         specified,
         the audio channel to participant mapping will be automatically assigned based on the order in
         which participant
         first audio was detected.  Channel to participant mapping details can be found in the metadata
         of the recording.
        :paramtype audio_channel_participant_ordering:
         list[~azure.communication.callautomation.models.CommunicationIdentifierModel]
        :keyword recording_storage_type: Recording storage mode. ``External`` enables bring your own
         storage. Known values are: "acs" and "azureBlob".
        :paramtype recording_storage_type: str or
         ~azure.communication.callautomation.models.RecordingStorageType
        """
        super().__init__(**kwargs)
        self.call_locator = call_locator
        self.recording_state_callback_uri = recording_state_callback_uri
        self.recording_content_type = recording_content_type
        self.recording_channel_type = recording_channel_type
        self.recording_format_type = recording_format_type
        self.audio_channel_participant_ordering = audio_channel_participant_ordering
        self.recording_storage_type = recording_storage_type


    def _to_generated(self):

        return StartCallRecordingRequestRest( call_locator=self.call_locator._to_generated(),
        recording_state_callback_uri=self.recording_state_callback_uri,
        recording_content_type=self.recording_content_type,
        recording_channel_type=self.recording_channel_type,
        recording_format_type=self.recording_format_type,
        audio_channel_participant_ordering=self.audio_channel_participant_ordering,
        recording_storage_type=self.recording_storage_type
        )


class RecordingStateResponse(object):
    """RecordingStateResponse.

    :ivar recording_id:
    :vartype recording_id: str
    :ivar recording_state: Known values are: "active" and "inactive".
    :vartype recording_state: str or ~azure.communication.callautomation.models.RecordingState
    """

    # pylint:disable=protected-access

    def __init__(
        self,
        **kwargs # type: Any
    ):
        # type: (...) -> None
        self.recording_id = kwargs['recording_id']
        self.recording_state = kwargs['recording_state']

    @classmethod
    def _from_generated(cls, recording_state_response):

        return cls(
            recording_id=recording_state_response.recording_id,
            recording_state=recording_state_response.recording_state
        )


class PlaySource(object):
    """
    The PlaySource model.

    :ivar play_source_id: Defines the identifier to be used for caching related media.
    :vartype play_source_id: str
    """
    def __init__(
            self,
            **kwargs
    ):
        self.play_source_id = kwargs['play_source_id']


class FileSource(PlaySource):
    """
    The FileSource model.

    :ivar uri: Uri for the audio file to be played.
    :vartype uri: str
    """
    def __init__(
            self,
            **kwargs
    ):
        self.uri = kwargs['uri']
        super().__init__(kwargs)


class TextSource(PlaySource):
    """
    The TextSource model.

    :ivar text: Text for the cognitive service to be played.
    :vartype text: str
    :ivar source_locale: Source language locale to be played.
    :vartype source_locale: str
    :ivar voice_gender: Voice gender type.
    :vartype voice_gender: str or ~azure.communication.callautomation.models.Gender
    :ivar voice_name: Voice name to be played.
    :vartype voice_name: str
    """
    def __init__(
            self,
            **kwargs
    ):
        self.text = kwargs['text']
        self.source_locale = kwargs['source_locale']
        self.voice_gender = kwargs['voice_gender']
        self.voice_name = kwargs['voice_name']
        super().__init__(kwargs)


class CallMediaRecognizeOptions(object):
    """
    Options to configure the Recognize operation.

    :ivar input_type: Determines the type of the recognition.
    :vartype input_type: str or ~azure.communication.callautomation.models.RecognizeInputType
    :ivar target_participant: Target participant of DTFM tone recognition.
    :vartype target_participant: ~azure.communication.callautomation.models.CommunicationIdentifierModel
    :ivar initial_silence_timeout: Time to wait for first input after prompt in seconds (if any).
    :vartype initial_silence_timeout: int
    :ivar play_prompt: The source of the audio to be played for recognition.
    :vartype play_prompt: ~azure.communication.callautomation.models.PlaySource
    :ivar interrupt_call_media_operation: If set recognize can barge into other existing queued-up/currently-processing requests.
    :vartype interrupt_call_media_operation: bool
    :ivar operation_context: The value to identify context of the operation.
    :vartype operation_context: str
    :ivar interrupt_prompt: Determines if we interrupt the prompt and start recognizing.
    :vartype interrupt_prompt: bool
    """
    def __init__(
            self, 
            input_type, 
            target_participant, 
            **kwargs
    ):
        self.input_type = input_type
        self.target_participant = target_participant
        self.initial_silence_timeout = 5
        self.play_prompt = kwargs['play_prompt']
        self.interrupt_call_media_operation = kwargs['interrupt_call_media_operation']
        self.stop_current_operations = kwargs['stop_current_operations']
        self.operation_context = kwargs['operation_context']
        self.interrupt_prompt = kwargs['interrupt_prompt']


class CallMediaRecognizeDtmfOptions(CallMediaRecognizeOptions):
    """
    The recognize configuration specific to Dtmf.

    :ivar max_tones_to_collect: Maximum number of DTMFs to be collected.
    :vartype max_tones_to_collect: int
    :ivar inter_tone_timeout: Time to wait between DTMF inputs to stop recognizing.
    :vartype inter_tone_timeout: int
    :ivar stop_dtmf_tones: List of tones that will stop recognizing.
    :vartype stop_dtmf_tones: list[~azure.communication.callautomation.models.Tone]
    """
    def __init__(
            self, 
            target_participant, 
            max_tones_to_collect, 
            **kwargs
    ):
        self.max_tones_to_collect = max_tones_to_collect
        self.inter_tone_timeout = kwargs['inter_tone_timeout']
        self.stop_dtmf_tones = kwargs['stop_dtmf_tones']
        super().__init__(RecognizeInputType.DTMF, target_participant, kwargs)


class CallMediaRecognizeChoiceOptions(CallMediaRecognizeOptions):
    """
    The Recognize configurations specific for Recognize Choice.

    :ivar recognize_choices: List of recognize choices
    :vartype recognize_choices: list[~azure.communication.callautomation.models.Choice]
    """
    def __init__(
            self, 
            target_participant, 
            recognize_choices, 
            **kwargs
    ):
        self.recognize_choices = recognize_choices
        super().__init__(RecognizeInputType.CHOICES, target_participant, kwargs)