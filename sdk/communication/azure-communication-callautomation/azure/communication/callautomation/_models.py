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
    RecordingContentType, RecordingChannelType, RecordingFormatType,
    CallConnectionStateModel,
    RecordingStorageType,
    MediaStreamingConfiguration as MediaStreamingConfigurationRest,
    CallParticipant as CallParticipantRest,
    CallConnectionProperties as CallConnectionPropertiesRest,
    AddParticipantResultRest
)
from ._shared.models import (
    CommunicationIdentifier,
    PhoneNumberIdentifier,
)
from ._communication_identifier_serializer import (
    deserialize_phone_identifier,
    deserialize_identifier
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

class RecordingStateResult(object):
    """
    RecordingStateResult.

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
    def _from_generated(cls, recording_state_result):

        return cls(
            recording_id=recording_state_result.recording_id,
            recording_state=recording_state_result.recording_state
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

    :ivar url: Url for the audio file to be played.
    :vartype url: str
    """

    def __init__(
            self,
            **kwargs
    ):
        self.url = kwargs['url']
        super().__init__(play_source_id=kwargs.get('play_source_id'))

class Gender(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Voice gender type."""

    MALE = "male"
    FEMALE = "female"


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
        source_caller_id_number: Optional[PhoneNumberIdentifier] = None,
        source_display_name: Optional[str] = None,
        sip_headers: Optional[Dict[str, str]] = None,
        voip_headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword target: Target's identity. Required.
        :paramtype target: ~azure.communication.callautomation._shared.models.CommunicationIdentifier
        :keyword source_caller_id_number: Caller's phone number identifier
        :paramtype source_caller_id_number: ~azure.communication.callautomation._shared.models.PhoneNumberIdentifier
        :keyword source_display_name: Set display name for caller
        :paramtype source_display_name: str
        :keyword sip_headers: Custom context for PSTN
        :paramtype sip_headers: str
        :keyword voip_headers: Custom context for VOIP
        :paramtype voip_headers: str
        """
        super().__init__(**kwargs)
        self.target = target
        self.source_caller_id_number = source_caller_id_number
        self.source_display_name = source_display_name
        self.sip_headers = sip_headers
        self.voip_headers = voip_headers
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
        callback_url: Optional[str] = None,
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
         list[~azure.communication.callautomation._shared.models.CommunicationIdentifier]
        :keyword call_connection_state: The state of the call connection. Known values are: "unknown",
         "connecting", "connected", "transferring", "transferAccepted", "disconnecting", and
         "disconnected".
        :paramtype call_connection_state: str or CallConnectionStateModel
        :keyword callback_url: The callback URL.
        :paramtype callback_url: str
        :keyword media_subscription_id: SubscriptionId for media streaming.
        :paramtype media_subscription_id: str
        :keyword source_caller_id_number: The source caller Id, a phone number, that's shown to the
         PSTN participant being invited.
         Required only when calling a PSTN callee.
        :paramtype source_caller_id_number: ~azure.communication.callautomation._shared.models.PhoneNumberIdentifier
        :keyword source_display_name: Display name of the call if dialing out to a pstn number.
        :paramtype source_display_name: str
        :keyword source_identity: Source identity.
        :paramtype source_identity: ~azure.communication.callautomation._shared.models.CommunicationIdentifier
        """
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.targets = targets
        self.call_connection_state = call_connection_state
        self.callback_url = callback_url
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
            callback_url=call_connection_properties_generated.callback_uri,
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
    """
    Contract model of an ACS call participant.
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
        :paramtype identifier: ~azure.communication.callautomation._shared.models.CommunicationIdentifier
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

class AddParticipantResult(object):
    """
    The result payload for adding participants to the call.
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
    def _from_generated(cls, add_participant_result_generated: AddParticipantResultRest):
        return cls(participant=CallParticipant._from_generated(# pylint:disable=protected-access
            add_participant_result_generated.participant),
            operation_context=add_participant_result_generated.operation_context)


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
        :param transport_url:
            Transport URL for media streaming.
        :paramtype transport_url: str
        :param transport_type:
            The type of transport to be used for media streaming.
            Known values are: "websocket"
        :paramtype transport_type: str or MediaStreamingTransportType
        :param content_type:
            Content type to stream, eg. audio, audio/video.
            Known values are: "audio"
        :paramtype content_type: str or MediaStreamingContentType
        :param audio_channel_type:
            Audio channel type to stream, eg. unmixed audio, mixed audio.
            Known values are: "mixed" and "unmixed".
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
