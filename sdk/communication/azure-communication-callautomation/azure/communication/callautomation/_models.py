# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List, Optional, Union, TYPE_CHECKING, Dict
from ._generated.models import (
    CallLocator,
    MediaStreamingConfiguration as MediaStreamingConfigurationRest,
    FileSource as FileSourceInternal,
    PlaySource as PlaySourceInternal
)
from ._shared.models import (
    CommunicationIdentifier,
    PhoneNumberIdentifier,
)
from ._generated.models._enums import (
    PlaySourceType,
)
from ._utils import (
    deserialize_phone_identifier,
    deserialize_identifier
)
if TYPE_CHECKING:
    from ._generated.models._enums  import (
        MediaStreamingTransportType,
        MediaStreamingContentType,
        MediaStreamingAudioChannelType,
        CallConnectionState,
        RecordingState
    )
    from ._generated.models  import (
        CallParticipant as CallParticipantRest,
        CallConnectionProperties as CallConnectionPropertiesRest,
        AddParticipantResponse as AddParticipantResultRest,
        RemoveParticipantResponse as RemoveParticipantResultRest,
        TransferCallResponse as TransferParticipantResultRest,
        RecordingStateResponse as RecordingStateResultRest,
    )

class CallInvite(object):
    """Details of call invitation for outgoing call.

    :ivar target: Target's identity.
    :vartype target: ~azure.communication.callautomation.CommunicationIdentifier
    :ivar source_caller_id_number: Caller's phone number identifier.
     Required for PSTN outbound call.
    :vartype source_caller_id_number: ~azure.communication.callautomation.PhoneNumberIdentifier
    :ivar source_display_name: Set display name for caller
    :vartype source_display_name: str
    :ivar sip_headers: Custom context for PSTN
    :vartype sip_headers: dict[str, str]
    :ivar voip_headers: Custom context for VOIP
    :vartype voip_headers: dict[str, str]
    """
    def __init__(
        self,
        target: CommunicationIdentifier,
        *,
        source_caller_id_number: Optional[PhoneNumberIdentifier] = None,
        source_display_name: Optional[str] = None,
        sip_headers: Optional[Dict[str, str]] = None,
        voip_headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """CallInvitation that can be used to do outbound calls, such as creating call.

        :param target: Target's identity.
        :type target: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword source_caller_id_number: Caller's phone number identifier.
         Required for PSTN outbound call.
        :paramtype source_caller_id_number: ~azure.communication.callautomation.PhoneNumberIdentifier
        :keyword source_display_name: Set display name for caller
        :paramtype source_display_name: str
        :keyword sip_headers: Custom context for PSTN calls
        :paramtype sip_headers: str
        :keyword voip_headers: Custom context for VOIP calls
        :paramtype voip_headers: str
        """
        super().__init__(**kwargs)
        self.target = target
        self.source_caller_id_number = source_caller_id_number
        self.source_display_name = source_display_name
        self.sip_headers = sip_headers
        self.voip_headers = voip_headers

class ServerCallLocator(object):
    """The locator to locate ongoing call, using server call id.

    :ivar server_call_id: The server call id of ongoing call.
    :vartype server_call_id: str
    """
    def __init__(
        self,
        server_call_id: str,
        **kwargs
    ):
        """The locator to locate ongoing call, using server call id.

        :param server_call_id: The server call id of ongoing call.
        :type server_call_id: str
        """
        super().__init__(**kwargs)
        self.id = server_call_id
        self.kind = "serverCallLocator"

    def _to_generated(self):
        return CallLocator(kind=self.kind,
                           server_call_id=self.id)

class GroupCallLocator(object):
    """The locator to locate ongoing call, using group call id.

    :ivar group_call_id: The group call id of ongoing call.
    :vartype group_call_id: str
    """
    def __init__(
        self,
        group_call_id: str,
        **kwargs
    ):
        """The locator to locate ongoing call, using group call id.

        :param group_call_id: The group call id of ongoing call.
        :type group_call_id: str
        """
        super().__init__(**kwargs)
        self.id = group_call_id
        self.kind = "groupCallLocator"

    def _to_generated(self):
        return CallLocator(kind=self.kind,
                           group_call_id=self.id)

class FileSource(object):
    """Media file source of URL to be played in action such as Play media.

    :ivar url: Url for the audio file to be played.
    :vartype url: str
    :ivar play_source_id: source id of the play media.
    :vartype play_source_id: str
    """
    def __init__(
        self,
        url: str,
        *,
        play_source_id: Optional[str] = None,
        **kwargs
    ):
        """Media file source of URL to be played in action such as Play media.

        :param url: Url for the audio file to be played.
        :type url: str
        :keyword play_source_id: source id of the play media.
        :paramtype play_source_id: str
        """
        super().__init__(**kwargs)
        self.url = url
        self.play_source_id = play_source_id

    def _to_generated(self):
        return PlaySourceInternal(
                source_type=PlaySourceType.FILE,
                file_source=FileSourceInternal(uri=self.url),
                play_source_id=self.play_source_id
            )

class MediaStreamingConfiguration(object):
    """Configuration of Media streaming.

    :ivar transport_url: Transport URL for media streaming.
    :vartype transport_url: str
    :ivar transport_type: The type of transport to be used for media streaming.
    :vartype transport_type: str or ~azure.communication.callautomation.MediaStreamingTransportType
    :ivar content_type: Content type to stream, eg. audio, audio/video.
    :vartype content_type: str or ~azure.communication.callautomation.MediaStreamingContentType
    :ivar audio_channel_type: Audio channel type to stream, eg. unmixed audio, mixed audio.
    :vartype audio_channel_type: str or ~azure.communication.callautomation.MediaStreamingAudioChannelType
    """
    def __init__(
        self,
        transport_url: str,
        transport_type: Union[str, 'MediaStreamingTransportType'],
        content_type: Union[str, 'MediaStreamingContentType'],
        audio_channel_type: Union[str, 'MediaStreamingAudioChannelType'],
        **kwargs
    ):
        """Configuration of Media streaming details.

        :param transport_url: Transport URL for media streaming.
        :type transport_url: str
        :param transport_type: The type of transport to be used for media streaming.
        :type transport_type: str or ~azure.communication.callautomation.MediaStreamingTransportType
        :param content_type: Content type to stream, eg. audio, audio/video.
        :type content_type: str or ~azure.communication.callautomation.MediaStreamingContentType
        :param audio_channel_type: Audio channel type to stream, eg. unmixed audio, mixed audio.
        :type audio_channel_type: str or ~azure.communication.callautomation.MediaStreamingAudioChannelType
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

class CallConnectionProperties():
    """ Detailed properties of the call.

    :ivar call_connection_id: The call connection id of this call leg.
    :vartype call_connection_id: str
    :ivar server_call_id: The server call id of this call.
    :vartype server_call_id: str
    :ivar targets: The targets of the call when the call was originally initiated.
    :vartype targets: list[~azure.communication.callautomation.CommunicationIdentifier]
    :ivar call_connection_state: The state of the call.
    :vartype call_connection_state: str or ~azure.communication.callautomation.CallConnectionState
    :ivar callback_url: The callback URL.
    :vartype callback_url: str
    :ivar media_subscription_id: SubscriptionId for media streaming.
    :vartype media_subscription_id: str
    :ivar source_caller_id_number:
     The source caller Id, a phone number, that's shown to the
     PSTN participant being invited.
     Required only when calling a PSTN callee.
    :vartype source_caller_id_number: ~azure.communication.callautomation.PhoneNumberIdentifier
    :ivar source_display_name:  Display name of the call if dialing out.
    :vartype source_display_name: str
    :ivar source_identity: Source identity of the caller.
    :vartype source_identity: ~azure.communication.callautomation.CommunicationIdentifier
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        targets: Optional[List[CommunicationIdentifier]] = None,
        call_connection_state:
        Optional[Union[str, 'CallConnectionState']] = None,
        callback_url: Optional[str] = None,
        media_subscription_id: Optional[str] = None,
        source_caller_id_number: Optional[PhoneNumberIdentifier] = None,
        source_display_name: Optional[str] = None,
        source_identity: Optional[CommunicationIdentifier] = None,
        **kwargs
    ):
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
            source_identity=deserialize_identifier(call_connection_properties_generated.source_identity)
            if call_connection_properties_generated.source_identity
            else None)

class RecordingProperties(object):
    """Detailed recording properties of the call.

    :ivar recording_id: Id of this recording operation.
    :vartype recording_id: str
    :ivar recording_state: state of ongoing recording.
    :vartype recording_state: str or ~azure.communication.callautomation.RecordingState
    """
    def __init__(
        self,
        *,
        recording_id: Optional[str] = None,
        recording_state: Optional['RecordingState'] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.recording_id = recording_id
        self.recording_state = recording_state

    @classmethod
    def _from_generated(cls, recording_state_result: 'RecordingStateResultRest'):
        return cls(
            recording_id=recording_state_result.recording_id,
            recording_state=recording_state_result.recording_state)

class CallParticipant(object):
    """Details of an Azure Communication Service call participant.

    :ivar identifier: Communication identifier of the participant.
    :vartype identifier: ~azure.communication.callautomation.CommunicationIdentifier
    :ivar is_muted: Is participant muted.
    :vartype is_muted: bool
    """
    def __init__(
        self,
        *,
        identifier: Optional[CommunicationIdentifier] = None,
        is_muted: Optional[bool] = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.identifier = identifier
        self.is_muted = is_muted

    @classmethod
    def _from_generated(cls, call_participant_generated: 'CallParticipantRest'):
        return cls(
            identifier=deserialize_identifier(call_participant_generated.identifier),
            is_muted=call_participant_generated.is_muted)

class AddParticipantResult(object):
    """ The result payload for adding participants to the call.

    :ivar participant: Participant that was added with this request.
    :vartype participant: ~azure.communication.callautomation.CallParticipant
    :ivar operation_context: The operation context provided by client.
    :vartype operation_context: str
    """
    def __init__(
        self,
        *,
        participant: Optional[CallParticipant] = None,
        operation_context: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.participant = participant
        self.operation_context = operation_context

    @classmethod
    def _from_generated(cls, add_participant_result_generated: 'AddParticipantResultRest'):
        return cls(participant=CallParticipant._from_generated(# pylint:disable=protected-access
            add_participant_result_generated.participant),
            operation_context=add_participant_result_generated.operation_context)

class RemoveParticipantResult(object):
    """The response payload for removing participants of the call.

    :ivar operation_context: The operation context provided by client.
    :vartype operation_context: str
    """
    def __init__(
        self,
        *,
        operation_context: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.operation_context = operation_context

    @classmethod
    def _from_generated(cls, remove_participant_result_generated: 'RemoveParticipantResultRest'):
        return cls(operation_context=remove_participant_result_generated.operation_context)

class TransferCallResult(object):
    """The response payload for transferring the call.

    :ivar operation_context: The operation context provided by client.
    :vartype operation_context: str
    """
    def __init__(
        self,
        *,
        operation_context: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.operation_context = operation_context

    @classmethod
    def _from_generated(cls, transfer_result_generated: 'TransferParticipantResultRest'):
        return cls(operation_context=transfer_result_generated.operation_context)
