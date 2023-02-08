from typing import Any, List, Optional, TYPE_CHECKING, Union
from ._generated.models import RecognizeInputType


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
    :vartype voice_gender: 
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
    :vartype input_type: 
    :ivar target_participant: Target participant of DTFM tone recognition.
    :vartype target_participant:
    :ivar initial_silence_timeout: Time to wait for first input after prompt in seconds (if any).
    :vartype initial_silence_timeout: int
    :ivar play_prompt: The source of the audio to be played for recognition.
    :vartype play_prompt:
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