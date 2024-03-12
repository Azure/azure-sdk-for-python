# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List, Optional, Union, TYPE_CHECKING
from ._generated.models import (
    CallLocator,
    MediaStreamingConfiguration as MediaStreamingConfigurationRest,
    TranscriptionConfiguration as TranscriptionConfigurationRest,
    FileSource as FileSourceInternal,
    TextSource as TextSourceInternal,
    SsmlSource as SsmlSourceInternal,
    PlaySource as PlaySourceInternal,
    Choice as ChoiceInternal,
    ChannelAffinity as ChannelAffinityInternal
)
from ._shared.models import (
    CommunicationIdentifier,
    CommunicationUserIdentifier,
    PhoneNumberIdentifier,
)
from ._generated.models._enums import PlaySourceType
from ._utils import (
    deserialize_phone_identifier,
    deserialize_identifier,
    deserialize_comm_user_identifier,
    serialize_identifier
)
if TYPE_CHECKING:
    from ._generated.models._enums  import (
        MediaStreamingTransportType,
        MediaStreamingContentType,
        MediaStreamingAudioChannelType,
        TranscriptionTransportType,
        CallConnectionState,
        RecordingState,
        VoiceKind,
        DtmfTone
    )
    from ._generated.models  import (
        CallParticipant as CallParticipantRest,
        CallConnectionProperties as CallConnectionPropertiesRest,
        AddParticipantResponse as AddParticipantResultRest,
        RemoveParticipantResponse as RemoveParticipantResultRest,
        TransferCallResponse as TransferParticipantResultRest,
        RecordingStateResponse as RecordingStateResultRest,
        MuteParticipantsResult as MuteParticipantsResultRest,
        SendDtmfTonesResult as SendDtmfTonesResultRest,
        CancelAddParticipantResponse as CancelAddParticipantResultRest,
    )


class CallInvite:
    """Details of call invitation for outgoing call.

    **DEPRECATED**: This model has been deprecated and will be removed from future releases.
    Please pass in the target `CommunicateIdentifier` directly.

    :param target: Target's identity.
    :type target: ~azure.communication.callautomation.CommunicationIdentifier
    :keyword source_caller_id_number: Caller's phone number identifier.
     Required for PSTN outbound call.
    :paramtype source_caller_id_number: ~azure.communication.callautomation.PhoneNumberIdentifier
    :keyword source_display_name: Set display name for caller
    :paramtype source_display_name: str
    """
    target: CommunicationIdentifier
    """Target's identity."""
    source_caller_id_number: Optional[PhoneNumberIdentifier]
    """ Caller's phone number identifier. Required for PSTN outbound call."""
    source_display_name: Optional[str]
    """Display name for caller"""

    def __init__(  # pylint: disable=unused-argument
        self,
        target: CommunicationIdentifier,
        *,
        source_caller_id_number: Optional[PhoneNumberIdentifier] = None,
        source_display_name: Optional[str] = None,
        **kwargs
    ):
        self.target = target
        self.source_caller_id_number = source_caller_id_number
        self.source_display_name = source_display_name


class ServerCallLocator:
    """The locator to locate ongoing call, using server call id.

    **DEPRECATED**: This model has been deprecated and will be removed from future releases.
    Please pass in the `server_call_id` directly.

    :param server_call_id: The server call id of ongoing call.
    :type server_call_id: str
    """
    server_call_id: str
    """The server call id of ongoing call."""
    kind: str = "serverCallLocator"
    """This is for locating the call with server call id."""

    def __init__(  # pylint: disable=unused-argument
        self,
        server_call_id: str,
        **kwargs
    ):
        self.server_call_id = server_call_id
        self.kind = "serverCallLocator"

    def _to_generated(self):
        return CallLocator(kind=self.kind, server_call_id=self.server_call_id)


class GroupCallLocator:
    """The locator to locate ongoing call, using group call id.

    **DEPRECATED**: This model has been deprecated and will be removed from future releases.
    Please pass in the `group_call_id` directly.

    :param group_call_id: The group call id of ongoing call.
    :type group_call_id: str
    """
    group_call_id: str
    """The group call id of ongoing call."""
    kind: str = "groupCallLocator"
    """This is for locating the call with group call id."""

    def __init__(  # pylint: disable=unused-argument
        self,
        group_call_id: str,
        **kwargs
    ):
        self.group_call_id = group_call_id
        self.kind = "groupCallLocator"

    def _to_generated(self):
        return CallLocator(kind=self.kind, group_call_id=self.group_call_id)


class ChannelAffinity:
    """Channel affinity for a participant.

    All required parameters must be populated in order to send to Azure.

    :param target_participant: The identifier for the participant whose bitstream will be written to the
     channel represented by the channel number. Required.
    :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
    :param channel: Channel number to which bitstream from a particular participant will be written.
    :type channel: int
    """

    target_participant: CommunicationIdentifier
    """The identifier for the participant whose bitstream will be written to the
     channel represented by the channel number. Required."""
    channel: int
    """ Channel number to which bitstream from a particular participant will be written."""

    def __init__(  # pylint: disable=unused-argument
        self,
        target_participant: CommunicationIdentifier,
        channel: int,
        **kwargs
    ):
        self.target_participant = target_participant
        self.channel = channel

    def _to_generated(self):
        return ChannelAffinityInternal(participant=serialize_identifier(self.target_participant), channel=self.channel)

class FileSource:
    """Media file source of URL to be played in action such as Play media.

    :param url: Url for the audio file to be played.
    :type url: str
    :keyword play_source_cache_id: Cached source id of the play media, if it exists.
    :paramtype play_source_cache_id: str
    """

    url: str
    """Url for the audio file to be played."""
    play_source_cache_id: Optional[str]
    """Cached source id of the play media, if it exists."""

    def __init__(  # pylint: disable=unused-argument
        self,
        url: str,
        *,
        play_source_cache_id: Optional[str] = None,
        **kwargs
    ):
        self.url = url
        self.play_source_cache_id = play_source_cache_id

    def _to_generated(self):
        return PlaySourceInternal(
            kind=PlaySourceType.FILE,
            file=FileSourceInternal(uri=self.url),
            play_source_cache_id=self.play_source_cache_id
        )


class TextSource:
    """TextSource to be played in actions such as Play media.

    :keyword text: Text for the cognitive service to be played. Required.
    :paramtype text: str
    :keyword source_locale: Source language locale to be played. Refer to available locales here:
        https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=stt-tts
    :paramtype source_locale: str
    :keyword voice_kind: Voice kind type. Known values are: "male" and "female".
    :paramtype voice_kind: str or ~azure.communication.callautomation.VoiceKind
    :keyword voice_name: Voice name to be played. Refer to available Text-to-speech voices here:
        https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=stt-tts
    :paramtype voice_name: str
    :keyword play_source_cache_id: Cached source id of the play media, if it exists.
    :paramtype play_source_cache_id: str
    :keyword custom_voice_endpoint_id: Endpoint where the custom voice was deployed.
    :paramtype custom_voice_endpoint_id: str
    """

    text: str
    """Text for the cognitive service to be played."""
    source_locale: Optional[str]
    """Source language locale to be played. Refer to available locales here:
        https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=stt-tts"""
    voice_kind: Optional[Union[str, 'VoiceKind']]
    """Voice kind type. Known values are: "male" and "female"."""
    voice_name: Optional[str]
    """Voice name to be played. Refer to available Text-to-speech voices here:
        https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=stt-tts"""
    play_source_cache_id: Optional[str]
    """Cached source id of the play media, if it exists."""
    custom_voice_endpoint_id: Optional[str]
    """Endpoint where the custom voice was deployed."""

    def __init__(
        self,
        *,
        text: str,
        source_locale: Optional[str] = None,
        voice_kind: Optional[Union[str, 'VoiceKind']] = None,
        voice_name: Optional[str] = None,
        play_source_cache_id: Optional[str] = None,
        custom_voice_endpoint_id: Optional[str] = None
    ):
        self.text = text
        self.source_locale = source_locale
        self.voice_kind = voice_kind
        self.voice_name = voice_name
        self.play_source_cache_id = play_source_cache_id
        self.custom_voice_endpoint_id = custom_voice_endpoint_id

    def _to_generated(self):
        return PlaySourceInternal(
            kind=PlaySourceType.TEXT,
            text=TextSourceInternal(
                text=self.text,
                source_locale=self.source_locale,
                voice_kind=self.voice_kind,
                voice_name=self.voice_name,
                custom_voice_endpoint_id=self.custom_voice_endpoint_id),
            play_source_cache_id=self.play_source_cache_id
        )

class SsmlSource:
    """SsmlSource to be played in actions such as Play media.

    :keyword ssml_text: Ssml string for the cognitive service to be played. Required.
    :paramtype ssml_text: str
    :keyword play_source_cache_id: Cached source id of the play media, if it exists.
    :paramtype play_source_cache_id: str
    :keyword custom_voice_endpoint_id: Endpoint id where the custom voice model is deployed.
    :paramtype custom_voice_endpoint_id: str
    """

    ssml_text: str
    """Ssml string for the cognitive service to be played."""
    play_source_cache_id: Optional[str]
    """Cached source id of the play media, if it exists."""
    custom_voice_endpoint_id: Optional[str]
    """Endpoint where the custom voice model was deployed."""

    def __init__(
        self,
        *,
        ssml_text: str,
        play_source_cache_id: Optional[str] = None,
        custom_voice_endpoint_id: Optional[str] = None
    ):
        self.ssml_text = ssml_text
        self.play_source_cache_id = play_source_cache_id
        self.custom_voice_endpoint_id = custom_voice_endpoint_id

    def _to_generated(self):
        return PlaySourceInternal(
            kind=PlaySourceType.SSML,
            ssml=SsmlSourceInternal(
                ssml_text=self.ssml_text,
                custom_voice_endpoint_id=self.custom_voice_endpoint_id),
            play_source_cache_id=self.play_source_cache_id
        )

class MediaStreamingConfiguration:
    """Configuration of Media streaming.

    :param transport_url: Transport URL for media streaming.
    :type transport_url: str
    :param transport_type: The type of transport to be used for media streaming.
    :type transport_type: str or ~azure.communication.callautomation.MediaStreamingTransportType
    :param content_type: Content type to stream, eg. audio, audio/video.
    :type content_type: str or ~azure.communication.callautomation.MediaStreamingContentType
    :param audio_channel_type: Audio channel type to stream, eg. unmixed audio, mixed audio.
    :type audio_channel_type: str or ~azure.communication.callautomation.MediaStreamingAudioChannelType
    """

    transport_url: str
    """Transport URL for media streaming."""
    transport_type: Union[str, 'MediaStreamingTransportType']
    """The type of transport to be used for media streaming."""
    content_type: Union[str, 'MediaStreamingContentType']
    """Content type to stream, eg. audio, audio/video."""
    audio_channel_type: Union[str, 'MediaStreamingAudioChannelType']
    """Audio channel type to stream, eg. unmixed audio, mixed audio."""

    def __init__(
        self,
        transport_url: str,
        transport_type: Union[str, 'MediaStreamingTransportType'],
        content_type: Union[str, 'MediaStreamingContentType'],
        audio_channel_type: Union[str, 'MediaStreamingAudioChannelType']
    ):
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

class TranscriptionConfiguration:
    """Configuration of live transcription.

    :param transport_url: Transport URL for live transcription. Required.
    :type transport_url: str
    :param transport_type: The type of transport to be used for live transcription, eg. Websocket.
     Required. "websocket"
    :type transport_type: str or ~azure.communication.callautomation.TranscriptionTransportType
    :param locale: Defines the locale for the data e.g en-CA, en-AU. Required.
    :type locale: str
    :param start_transcription: Determines if the transcription should be started immediately after
     call is answered or not. Required.
    :type start_transcription: bool
    """

    transport_url: str
    """Transport URL for live transcription."""
    transport_type: Union[str, 'TranscriptionTransportType']
    """The type of transport to be used for live transcription."""
    locale: str
    """Defines the locale for the data."""
    start_transcription: bool
    """Determines if the transcription should be started immediately after call is answered or not."""

    def __init__(
        self,
        transport_url: str,
        transport_type: Union[str, 'TranscriptionTransportType'],
        locale: str,
        start_transcription: bool
    ):
        self.transport_url = transport_url
        self.transport_type = transport_type
        self.locale = locale
        self.start_transcription = start_transcription

    def to_generated(self):
        return TranscriptionConfigurationRest(
            transport_url=self.transport_url,
            transport_type=self.transport_type,
            locale=self.locale,
            start_transcription=self.start_transcription
        )

class CallConnectionProperties:  # pylint: disable=too-many-instance-attributes
    """ Detailed properties of the call.

    :keyword call_connection_id: The call connection id of this call leg.
    :paramtype call_connection_id: str
    :keyword server_call_id: The server call id of this call.
    :paramtype server_call_id: str
    :keyword targets: The targets of the call when the call was originally initiated.
    :paramtype targets: list[~azure.communication.callautomation.CommunicationIdentifier]
    :keyword call_connection_state: The state of the call.
    :paramtype call_connection_state: str or ~azure.communication.callautomation.CallConnectionState
    :keyword callback_url: The callback URL.
    :paramtype callback_url: str
    :keyword media_subscription_id: SubscriptionId for media streaming.
    :paramtype media_subscription_id: str
    :keyword source_caller_id_number:
     The source caller Id, a phone number, that's shown to the
     PSTN participant being invited.
     Required only when calling a PSTN callee.
    :paramtype source_caller_id_number: ~azure.communication.callautomation.PhoneNumberIdentifier
    :keyword source_display_name:  Display name of the call if dialing out.
    :paramtype source_display_name: str
    :keyword source: Source identity of the caller.
    :paramtype source: ~azure.communication.callautomation.CommunicationIdentifier
    :keyword correlation_id: Correlation ID of the call
    :paramtype correlation_id: str
    :keyword answered_by: The identifier that answered the call
    :paramtype answered_by: ~azure.communication.callautomation.CommunicationUserIdentifier
    """

    call_connection_id: Optional[str]
    """The call connection id of this call leg."""
    server_call_id: Optional[str]
    """The server call id of this call."""
    targets: Optional[List[CommunicationIdentifier]]
    """The targets of the call when the call was originally initiated."""
    call_connection_state: Optional[Union[str, 'CallConnectionState']]
    """The state of the call."""
    callback_url: Optional[str]
    """The callback URL."""
    media_subscription_id: Optional[str]
    """SubscriptionId for media streaming."""
    source_caller_id_number: Optional[PhoneNumberIdentifier]
    """The source caller Id, a phone number, that's shown to the
     PSTN participant being invited.
     Required only when calling a PSTN callee."""
    source_display_name: Optional[str]
    """Display name of the call if dialing out."""
    source: Optional[CommunicationIdentifier]
    """Source identity of the caller."""
    correlation_id: Optional[str]
    """Correlation ID of the call"""
    answered_by: Optional[CommunicationIdentifier]
    """The identifier that answered the call"""

    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        targets: Optional[List[CommunicationIdentifier]] = None,
        call_connection_state: Optional[Union[str, 'CallConnectionState']] = None,
        callback_url: Optional[str] = None,
        media_subscription_id: Optional[str] = None,
        source_caller_id_number: Optional[PhoneNumberIdentifier] = None,
        source_display_name: Optional[str] = None,
        source: Optional[CommunicationIdentifier] = None,
        correlation_id: Optional[str] = None,
        answered_by: Optional[CommunicationUserIdentifier] = None
    ):
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.targets = targets
        self.call_connection_state = call_connection_state
        self.callback_url = callback_url
        self.media_subscription_id = media_subscription_id
        self.source_caller_id_number = source_caller_id_number
        self.source_display_name = source_display_name
        self.source = source
        self.correlation_id = correlation_id
        self.answered_by = answered_by

    @classmethod
    def _from_generated(cls, call_connection_properties_generated: 'CallConnectionPropertiesRest'):
        target_models = []
        for target in call_connection_properties_generated.targets:
            target_models.append(deserialize_identifier(target))

        return cls(
            call_connection_id=call_connection_properties_generated.call_connection_id,
            server_call_id=call_connection_properties_generated.server_call_id,
            targets=target_models,
            call_connection_state=call_connection_properties_generated.call_connection_state,
            callback_url=call_connection_properties_generated.callback_uri,
            media_subscription_id=call_connection_properties_generated.media_subscription_id,
            source_caller_id_number=deserialize_phone_identifier(
            call_connection_properties_generated.source_caller_id_number)
            if call_connection_properties_generated.source_caller_id_number
            else None,
            source_display_name=call_connection_properties_generated.source_display_name,
            source=deserialize_identifier(call_connection_properties_generated.source)
            if call_connection_properties_generated.source
            else None,
            correlation_id=call_connection_properties_generated.correlation_id,
            answered_by=deserialize_comm_user_identifier(
                call_connection_properties_generated.answered_by)
            if call_connection_properties_generated.answered_by
            else None
        )


class RecordingProperties:
    """Detailed recording properties of the call.

    :keyword recording_id: Id of this recording operation.
    :paramtype recording_id: str
    :keyword recording_state: state of ongoing recording.
    :paramtype recording_state: str or ~azure.communication.callautomation.RecordingState
    """

    recording_id: Optional[str]
    """Id of this recording operation."""
    recording_state: Optional[Union[str,'RecordingState']]
    """state of ongoing recording."""

    def __init__(
        self,
        *,
        recording_id: Optional[str] = None,
        recording_state: Optional[Union[str,'RecordingState']] = None
    ):
        self.recording_id = recording_id
        self.recording_state = recording_state

    @classmethod
    def _from_generated(cls, recording_state_result: 'RecordingStateResultRest'):
        return cls(
            recording_id=recording_state_result.recording_id,
            recording_state=recording_state_result.recording_state
        )


class CallParticipant:
    """Details of an Azure Communication Service call participant.

    :keyword identifier: Communication identifier of the participant.
    :paramtype identifier: ~azure.communication.callautomation.CommunicationIdentifier
    :keyword is_muted: Is participant muted.
    :paramtype is_muted: bool
    """

    identifier: Optional[CommunicationIdentifier]
    """Communication identifier of the participant."""
    is_muted: bool
    """Is participant muted."""

    def __init__(
        self,
        *,
        identifier: Optional[CommunicationIdentifier] = None,
        is_muted: bool = False
    ):
        self.identifier = identifier
        self.is_muted = is_muted

    @classmethod
    def _from_generated(cls, call_participant_generated: 'CallParticipantRest'):
        return cls(
            identifier=deserialize_identifier(call_participant_generated.identifier),
            is_muted=call_participant_generated.is_muted
        )


class AddParticipantResult:
    """ The result payload for adding participants to the call.

    :keyword participant: Participant that was added with this request.
    :paramtype participant: ~azure.communication.callautomation.CallParticipant
    :keyword operation_context: The operation context provided by client.
    :paramtype operation_context: str
    """

    invitation_id: str
    """invitation ID used to add participant."""
    participant: Optional[CallParticipant]
    """Participant that was added with this request."""
    operation_context: Optional[str]
    """The operation context provided by client."""

    def __init__(
        self,
        *,
        invitation_id: str,
        participant: Optional[CallParticipant] = None,
        operation_context: Optional[str] = None
    ):
        self.invitation_id = invitation_id
        self.participant = participant
        self.operation_context = operation_context

    @classmethod
    def _from_generated(cls, add_participant_result_generated: 'AddParticipantResultRest'):
        return cls(
            invitation_id=add_participant_result_generated.invitation_id,
            participant=CallParticipant._from_generated(  # pylint:disable=protected-access
                add_participant_result_generated.participant
            ),
            operation_context=add_participant_result_generated.operation_context
        )


class RemoveParticipantResult:
    """The response payload for removing participants of the call.

    :keyword operation_context: The operation context provided by client.
    :paramtype operation_context: str
    """

    operation_context: Optional[str]
    """The operation context provided by client."""

    def __init__(
        self,
        *,
        operation_context: Optional[str] = None
    ) -> None:
        self.operation_context = operation_context

    @classmethod
    def _from_generated(cls, remove_participant_result_generated: 'RemoveParticipantResultRest'):
        return cls(operation_context=remove_participant_result_generated.operation_context)


class TransferCallResult:
    """The response payload for transferring the call.

    :keyword operation_context: The operation context provided by client.
    :paramtype operation_context: str
    """

    operation_context: Optional[str]
    """The operation context provided by client."""

    def __init__(
        self,
        *,
        operation_context: Optional[str] = None
    ) -> None:
        self.operation_context = operation_context

    @classmethod
    def _from_generated(cls, transfer_result_generated: 'TransferParticipantResultRest'):
        return cls(operation_context=transfer_result_generated.operation_context)

class RecognitionChoice:
    """
    An IVR choice for the recognize operation.

    :keyword label: Identifier for a given choice. Required.
    :paramtype label: str
    :keyword phrases: List of phrases to recognize. Required.
    :paramtype phrases: list[str]
    :keyword tone: Known values are: "zero", "one", "two", "three", "four", "five", "six", "seven",
     "eight", "nine", "a", "b", "c", "d", "pound", and "asterisk".
    :paramtype tone: str or ~azure.communication.callautomation.DtmfTone
    """

    label: str
    """Identifier for a given choice."""
    phrases: List[str]
    """List of phrases to recognize."""
    tone: Optional[Union[str, 'DtmfTone']]
    """Known values are: "zero", "one", "two", "three", "four", "five", "six", "seven",
     "eight", "nine", "a", "b", "c", "d", "pound", and "asterisk"."""

    def __init__(
        self,
        *,
        label: str,
        phrases: List[str],
        tone: Optional[Union[str, 'DtmfTone']] = None
    ):
        self.label = label
        self.phrases = phrases
        self.tone = tone

    def _to_generated(self):
        return ChoiceInternal(label=self.label, phrases=self.phrases, tone=self.tone)

class MuteParticipantResult:
    """The result payload for muting participant from the call.

    :keyword operation_context: The operation context provided by client.
    :paramtype operation_context: str
    """

    operation_context: Optional[str]
    """The operation context provided by client."""

    def __init__(
        self,
        *,
        operation_context: Optional[str] = None
    ) -> None:
        self.operation_context = operation_context

    @classmethod
    def _from_generated(cls, mute_participant_result_generated: 'MuteParticipantsResultRest'):
        return cls(operation_context=mute_participant_result_generated.operation_context)

class SendDtmfTonesResult:
    """The result payload for send Dtmf tones.
    :keyword operation_context: The operation context provided by client.
    :paramtype operation_context: str
    """

    operation_context: Optional[str]
    """The operation context provided by client."""

    def __init__(
        self,
        *,
        operation_context: Optional[str] = None
    ) -> None:
        self.operation_context = operation_context

    @classmethod
    def _from_generated(cls, send_dtmf_tones_result_generated: 'SendDtmfTonesResultRest'):
        return cls(operation_context=send_dtmf_tones_result_generated.operation_context)

class CancelAddParticipantOperationResult:
    """ The result payload for cancelling add participant request for a participant.
    :keyword invitation_id: Invitation ID that was used to add the participant to the call.
    :paramtype participant: str
    :keyword operation_context: The operation context provided by client.
    :paramtype operation_context: str
    """

    invitation_id: str
    """Invitation ID that was used to add the participant to the call."""
    operation_context: Optional[str]
    """The operation context provided by client."""

    def __init__(
        self,
        *,
        invitation_id: str,
        operation_context: Optional[str] = None
    ):
        self.invitation_id = invitation_id
        self.operation_context = operation_context

    @classmethod
    def _from_generated(cls, cancel_add_participant_operation_result_generated: 'CancelAddParticipantResultRest'):
        return cls(
            invitation_id=cancel_add_participant_operation_result_generated.invitation_id,
            operation_context=cancel_add_participant_operation_result_generated.operation_context
        )
