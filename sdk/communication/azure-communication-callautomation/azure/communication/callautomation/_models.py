# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List, Optional, Union, TYPE_CHECKING
from ._generated.models import (
    CallLocator,
    FileSource as FileSourceInternal,
    PlaySource as PlaySourceInternal,
    ChannelAffinity as ChannelAffinityInternal
)
from ._shared.models import (
    CommunicationIdentifier,
    CommunicationUserIdentifier,
    PhoneNumberIdentifier,
)
from ._generated.models._enums import (
    PlaySourceType,
)
from ._utils import (
    deserialize_phone_identifier,
    deserialize_identifier,
    deserialize_comm_user_identifier,
    serialize_identifier
)
if TYPE_CHECKING:
    from ._generated.models._enums  import (
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
    """
    def __init__(
        self,
        target: CommunicationIdentifier,
        *,
        source_caller_id_number: Optional[PhoneNumberIdentifier] = None,
        source_display_name: Optional[str] = None,
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
        """
        super().__init__(**kwargs)
        self.target = target
        self.source_caller_id_number = source_caller_id_number
        self.source_display_name = source_display_name

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

class ChannelAffinity(object):
    """Channel affinity for a participant.

    All required parameters must be populated in order to send to Azure.

    :ivar target_participant: The identifier for the participant whose bitstream will be written to the
     channel
     represented by the channel number. Required.
    :vartype target_participant: ~azure.communication.callautomation.CommunicationIdentifier
    :ivar channel: Channel number to which bitstream from a particular participant will be written.
    :vartype channel: int
    """

    def __init__(
        self,
        target_participant: CommunicationIdentifier,
        channel: int,
        **kwargs
    ):
        """
        :keyword target_participant: The identifier for the participant whose bitstream will be written to the
         channel
         represented by the channel number. Required.
        :paramtype target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword channel: Channel number to which bitstream from a particular participant will be
         written.
        :paramtype channel: int
        """
        super().__init__(**kwargs)
        self.target_participant = target_participant
        self.channel = channel

    def _to_generated(self):
        return ChannelAffinityInternal(participant= serialize_identifier(self.target_participant), channel=self.channel)

class FileSource(object):
    """Media file source of URL to be played in action such as Play media.

    :ivar url: Url for the audio file to be played.
    :vartype url: str
    :ivar play_source_cache_id: source id of the play media.
    :vartype play_source_cache_id: str
    """
    def __init__(
        self,
        url: str,
        *,
        play_source_cache_id: Optional[str] = None,
        **kwargs
    ):
        """Media file source of URL to be played in action such as Play media.

        :param url: Url for the audio file to be played.
        :type url: str
        :keyword play_source_cache_id: source id of the play media.
        :paramtype play_source_cache_id: str
        """
        super().__init__(**kwargs)
        self.url = url
        self.play_source_cache_id = play_source_cache_id

    def _to_generated(self):
        return PlaySourceInternal(
            kind=PlaySourceType.FILE,
            play_source_cache_id=self.play_source_cache_id,
            file=FileSourceInternal(uri=self.url)
        )

class CallConnectionProperties(): # type: ignore # pylint: disable=too-many-instance-attributes
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
    :ivar source_caller_id_number:
     The source caller Id, a phone number, that's shown to the
     PSTN participant being invited.
     Required only when calling a PSTN callee.
    :vartype source_caller_id_number: ~azure.communication.callautomation.PhoneNumberIdentifier
    :ivar source_display_name:  Display name of the call if dialing out.
    :vartype source_display_name: str
    :ivar source: Source identity of the caller.
    :vartype source: ~azure.communication.callautomation.CommunicationIdentifier
    :ivar correlation_id: Correlation ID of the call
    :vartype correlation_id: str
    :ivar answered_by: The identifier that answered the call
    :vartype answered_by: ~azure.communication.callautomation.CommunicationUserIdentifier
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
        source_caller_id_number: Optional[PhoneNumberIdentifier] = None,
        source_display_name: Optional[str] = None,
        source: Optional[CommunicationIdentifier] = None,
        correlation_id: Optional[str] = None,
        answered_by: Optional[CommunicationUserIdentifier] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.targets = targets
        self.call_connection_state = call_connection_state
        self.callback_url = callback_url
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
