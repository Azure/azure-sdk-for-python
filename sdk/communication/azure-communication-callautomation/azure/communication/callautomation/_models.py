# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, List, Optional, Union

from enum import Enum
from typing import Dict

from azure.core import CaseInsensitiveEnumMeta

from ._generated.models import (
    CallLocator,
    StartCallRecordingRequest as StartCallRecordingRequestRest,
    RecordingContentType, RecordingChannelType, RecordingFormatType,
    CommunicationIdentifierModel,
    CallConnectionStateModel,
    RecordingStorageType,
    RecognizeInputType,
    MediaStreamingConfiguration as MediaStreamingConfigurationRest,
    CallParticipant as CallParticipantRest,
    CallConnectionProperties as CallConnectionPropertiesRest,
    GetParticipantsResponse as GetParticipantsResponseRest,
    AddParticipantResponse as AddParticipantResponseRest
)

from ._shared.models import (
    CommunicationIdentifier,
    PhoneNumberIdentifier,
)

from ._communication_identifier_serializer import (
    deserialize_phone_identifier,
    deserialize_identifier,
    serialize_identifier
)

class ServerCallLocator(object):
    """
    The locator used for joining or taking action on a server call.

    :ivar locator_id: The server call id.
    :vartype locator_id: str
    """
    def __init__(
        self,
        *,
        locator_id: str,
        **kwargs: Any
    ) -> None:

        super().__init__(**kwargs)
        self.id = locator_id
        self.kind = "serverCallLocator"

    def _to_generated(self):

        return CallLocator(kind=self.kind,
                           server_call_id=self.id
                           )


class GroupCallLocator(object):
    """
    The locator used for joining or taking action on a group call.

    :ivar locator_id: The group call id.
    :vartype locator_id: str
    """
    def __init__(
        self,
        *,
        locator_id: str,
        **kwargs: Any
    ) -> None:

        super().__init__(**kwargs)
        self.id = locator_id
        self.kind = "groupCallLocator"

    def _to_generated(self):

        return CallLocator(kind=self.kind,
                           group_call_id=self.id
                           )


class StartRecordingOptions(object):
    def __init__(
        self,
        *,
        call_locator: Union[ServerCallLocator, GroupCallLocator],
        recording_state_callback_uri: Optional[str] = None,
        recording_content: Optional[Union[str,
                                               "RecordingContent"]] = None,
        recording_channel: Optional[Union[str,
                                               "RecordingChannel"]] = None,
        recording_format: Optional[Union[str,
                                              "RecordingFormat"]] = None,
        audio_channel_participant_ordering: Optional[List["CommunicationIdentifier"]] = None,
        recording_storage: Optional[Union[str,
                                               "RecordingStorage"]] = None,
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
         ~azure.communication.callautomation.models.RecordingContent
        :keyword recording_channel_type: The channel type of call recording. Known values are: "mixed"
         and "unmixed".
        :paramtype recording_channel_type: str or
         ~azure.communication.callautomation.models.RecordingChannel
        :keyword recording_format_type: The format type of call recording. Known values are: "wav",
         "mp3", and "mp4".
        :paramtype recording_format_type: str or
         ~azure.communication.callautomation.models.RecordingFormat
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
        self.recording_content_type = recording_content
        self.recording_channel_type = recording_channel
        self.recording_format_type = recording_format
        self.audio_channel_participant_ordering = audio_channel_participant_ordering
        self.recording_storage_type = recording_storage

    def _to_generated(self):
        audio_channel_participant_ordering_list:List[CommunicationIdentifierModel] = None
        if self.audio_channel_participant_ordering is not None:
            audio_channel_participant_ordering_list=[
                serialize_identifier(identifier) for identifier
                in self.audio_channel_participant_ordering]

        return StartCallRecordingRequestRest(
            call_locator=self.call_locator._to_generated(# pylint:disable=protected-access
            ),
            recording_state_callback_uri=self.recording_state_callback_uri,
            recording_content_type=self.recording_content_type,
            recording_channel_type=self.recording_channel_type,
            recording_format_type=self.recording_format_type,
            audio_channel_participant_ordering=audio_channel_participant_ordering_list,
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
        **kwargs  # type: Any
    ):
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
        super().__init__(play_source_id=kwargs.get('play_source_id'))

class Gender(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Voice gender type."""

    MALE = "male"
    FEMALE = "female"


class CallMediaRecognizeOptions(object):
    """
    Options to configure the Recognize operation.

    :ivar input_type: Determines the type of the recognition.
    :vartype input_type: str or ~azure.communication.callautomation.models.RecognizeInputType
    :ivar target_participant: Target participant of DTMF tone recognition.
    :vartype target_participant: ~azure.communication.callautomation.models.CommunicationIdentifierModel
    :ivar initial_silence_timeout: Time to wait for first input after prompt in seconds (if any).
    :vartype initial_silence_timeout: int
    :ivar play_prompt: The source of the audio to be played for recognition.
    :vartype play_prompt: ~azure.communication.callautomation.models.PlaySource
    :ivar interrupt_call_media_operation: If set recognize can barge into
     other existing queued-up/currently-processing requests.
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
        self.play_prompt = kwargs.get('play_prompt')
        self.interrupt_call_media_operation = kwargs.get(
            'interrupt_call_media_operation')
        self.stop_current_operations = kwargs.get('stop_current_operations')
        self.operation_context = kwargs.get('operation_context')
        self.interrupt_prompt = kwargs.get('interrupt_prompt')


class CallMediaRecognizeDtmfOptions(CallMediaRecognizeOptions):
    """
    The recognize configuration specific to DTMF.

    :ivar max_tones_to_collect: Maximum number of DTMF to be collected.
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
        self.inter_tone_timeout = kwargs.get('inter_tone_timeout')
        self.stop_dtmf_tones = kwargs.get('stop_dtmf_tones')
        super().__init__(RecognizeInputType.DTMF, target_participant, **kwargs)


class DtmfTone(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Tone."""

    ZERO = "zero"
    ONE = "one"
    TWO = "two"
    THREE = "three"
    FOUR = "four"
    FIVE = "five"
    SIX = "six"
    SEVEN = "seven"
    EIGHT = "eight"
    NINE = "nine"
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    POUND = "pound"
    ASTERISK = "asterisk"

class CallInvite(object):
    def __init__(
        self,
        target: CommunicationIdentifier,
        *,
        sourceCallIdNumber: Optional[PhoneNumberIdentifier] = None,
        sourceDisplayName: Optional[str] = None,
        sipHeaders: Optional[Dict[str, str]] = None,
        voipHeaders: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword target: Target's identity. Required.
        :paramtype target: CommunicationIdentifier
        :keyword sourceCallIdNumber: Caller's phone number identifier
        :paramtype sourceCallIdNumber: PhoneNumberIdentifier
        :keyword sourceDisplayName: Set display name for caller
        :paramtype sourceDisplayName: str
        :keyword sipHeaders: Custom context for PSTN
        :paramtype sipHeaders: str
        :keyword voipHeaders: Custom context for VOIP
        :paramtype voipHeaders: str
        """
        super().__init__(**kwargs)
        self.target = target
        self.sourceCallIdNumber = sourceCallIdNumber
        self.sourceDisplayName = sourceDisplayName
        self.sipHeaders = sipHeaders
        self.voipHeaders = voipHeaders


class CallConnectionProperties(object):
    """Properties of a call connection."""

    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        targets: Optional[List[CommunicationIdentifier]] = None,
        call_connection_state: Optional[Union[str,
                                              CallConnectionStateModel]] = None,
        callback_uri: Optional[str] = None,
        media_subscription_id: Optional[str] = None,
        source_caller_id_number: Optional[PhoneNumberIdentifier] = None,
        source_display_name: Optional[str] = None,
        source_identity: Optional[CommunicationIdentifier] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword call_connection_id: The call connection id.
        :paramtype call_connection_id: str
        :keyword server_call_id: The server call id.
        :paramtype server_call_id: str
        :keyword targets: The targets of the call.
        :paramtype targets:
         list[CommunicationIdentifier]
        :keyword call_connection_state: The state of the call connection. Known values are: "unknown",
         "connecting", "connected", "transferring", "transferAccepted", "disconnecting", and
         "disconnected".
        :paramtype call_connection_state: str or CallConnectionStateModel
        :keyword callback_uri: The callback URI.
        :paramtype callback_uri: str
        :keyword media_subscription_id: SubscriptionId for media streaming.
        :paramtype media_subscription_id: str
        :keyword source_caller_id_number: The source caller Id, a phone number, that's shown to the
         PSTN participant being invited.
         Required only when calling a PSTN callee.
        :paramtype source_caller_id_number: PhoneNumberIdentifier
        :keyword source_display_name: Display name of the call if dialing out to a pstn number.
        :paramtype source_display_name: str
        :keyword source_identity: Source identity.
        :paramtype source_identity: CommunicationIdentifier
        """
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.targets = targets
        self.call_connection_state = call_connection_state
        self.callback_uri = callback_uri
        self.media_subscription_id = media_subscription_id
        self.source_caller_id_number = source_caller_id_number
        self.source_display_name = source_display_name
        self.source_identity = source_identity

    @classmethod
    def _from_generated(cls, call_connection_properties_generated: CallConnectionPropertiesRest):
        target_models = []
        for target in call_connection_properties_generated.targets:
            target_models.append(deserialize_identifier(target))

        return cls(
            call_connection_id=call_connection_properties_generated.call_connection_id,
            server_call_id=call_connection_properties_generated.server_call_id,
            targets=target_models,
            call_connection_state=call_connection_properties_generated.call_connection_state,
            callback_uri=call_connection_properties_generated.callback_uri,
            media_subscription_id=call_connection_properties_generated.media_subscription_id,
            source_caller_id_number=deserialize_phone_identifier(
            call_connection_properties_generated.source_caller_id_number)
            if call_connection_properties_generated.source_caller_id_number
            else None,
            source_display_name=call_connection_properties_generated.source_display_name,
            source_identity=deserialize_identifier(call_connection_properties_generated.source_identity)
            if call_connection_properties_generated.source_identity
            else None)


class CallParticipant(object):
    """Contract model of an ACS call participant.
    """

    def __init__(
        self,
        identifier: CommunicationIdentifier,
        *,
        is_muted: Optional[bool] = False,
        **kwargs: Any
    ) -> None:
        """
        :keyword identifier: Communication identifier of the participant.
        :paramtype identifier: CommunicationIdentifier
        :keyword is_muted: Is participant muted.
        :paramtype is_muted: bool
        """
        super().__init__(**kwargs)
        self.identifier = identifier
        self.is_muted = is_muted

    @classmethod
    def _from_generated(cls, call_participant_generated: CallParticipantRest):
        return cls(
            identifier=deserialize_identifier(call_participant_generated.identifier),
            is_muted=call_participant_generated.is_muted)

class GetParticipantsResponse(object):
    """The response payload for getting participants of the call."""

    def __init__(
        self,
        values: List[CallParticipant],
        *,
        next_link: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword values: List of the current participants in the call.
        :paramtype values: list[CallParticipant]
        :keyword next_link: Continue of the list of participants.
        :paramtype next_link: str
        """
        super().__init__(**kwargs)
        self.values = values
        self.next_link = next_link

    @classmethod
    def _from_generated(cls, get_participant_response_generated: GetParticipantsResponseRest):
        return cls(values=[CallParticipant._from_generated(# pylint:disable=protected-access
            participant) for participant in get_participant_response_generated.values],
            next_link=get_participant_response_generated.next_link)


class AddParticipantResponse(object):
    """The response payload for adding participants to the call.
    """

    def __init__(
        self,
        participant: CallParticipant,
        *,
        operation_context: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword participant: List of current participants in the call.
        :paramtype participant: CallParticipant
        :keyword operation_context: The operation context provided by client.
        :paramtype operation_context: str
        """
        super().__init__(**kwargs)
        self.participant = participant
        self.operation_context = operation_context

    @classmethod
    def _from_generated(cls, add_participant_response_generated: AddParticipantResponseRest):
        return cls(participant=CallParticipant._from_generated(# pylint:disable=protected-access
            add_participant_response_generated.participant),
            operation_context=add_participant_response_generated.operation_context)


class MediaStreamingAudioChannelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Audio channel type to stream, eg. unmixed audio, mixed audio."""

    MIXED = "mixed"
    UNMIXED = "unmixed"


class MediaStreamingContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Content type to stream, eg. audio, audio/video."""

    AUDIO = "audio"


class MediaStreamingTransportType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of transport to be used for media streaming, eg. Websocket."""

    WEBSOCKET = "websocket"


class MediaStreamingConfiguration(object):
    """Configuration of Media streaming.

    All required parameters must be populated in order to send to Azure.
    """

    def __init__(
        self,
        transport_url: str,
        transport_type: Union[str, MediaStreamingTransportType],
        content_type: Union[str, MediaStreamingContentType],
        audio_channel_type: Union[str, MediaStreamingAudioChannelType],
        **kwargs: Any
    ) -> None:
        """
        :keyword transport_url: Transport URL for media streaming. Required.
        :paramtype transport_url: str
        :keyword transport_type: The type of transport to be used for media streaming, eg. Websocket.
         Required. "websocket"
        :paramtype transport_type: str or MediaStreamingTransportType
        :keyword content_type: Content type to stream, eg. audio, audio/video. Required. "audio"
        :paramtype content_type: str or MediaStreamingContentType
        :keyword audio_channel_type: Audio channel type to stream, eg. unmixed audio, mixed audio.
         Required. Known values are: "mixed" and "unmixed".
        :paramtype audio_channel_type: str or MediaStreamingAudioChannelType
        """
        super().__init__(**kwargs)
        self.transport_url = transport_url
        self.transport_type = transport_type
        self.content_type = content_type
        self.audio_channel_type = audio_channel_type

    def to_generated(self):
        return MediaStreamingConfigurationRest(
            transport_url=self.transport_url,
            transport_type=self.transport_type,
            content_type=self.content_type,
            audio_channel_type=self.audio_channel_type
            )


class CallRejectReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The rejection reason."""

    NONE = "none"
    BUSY = "busy"
    FORBIDDEN = "forbidden"


class RecordingContent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Recording content type."""

    AUDIO = RecordingContentType.AUDIO.value
    AUDIO_VIDEO = RecordingContentType.AUDIO_VIDEO.value

class RecordingChannel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Recording channel type."""

    MIXED = RecordingChannelType.MIXED.value
    UNMIXED = RecordingChannelType.UNMIXED.value

class RecordingFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Recording format type."""
    WAV = RecordingFormatType.WAV.value
    MP4 = RecordingFormatType.MP4.value
    MP3 = RecordingFormatType.MP3.value

class RecordingStorage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Recording storage type."""

    ACS = RecordingStorageType.ACS.value
    BLOB_STORAGE = RecordingStorageType.BLOB_STORAGE.value
