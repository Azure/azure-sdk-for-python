# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-public-methods
from typing import TYPE_CHECKING, List, Any  # pylint: disable=unused-import
from azure.core.tracing.decorator import distributed_trace
from ._communication_identifier_serializer import serialize_identifier
from ._converters import (
    AddParticipantRequestConverter,
    GetParticipantRequestConverter,
    RemoveParticipantRequestConverter,
    TransferCallRequestConverter,
    CancelParticipantMediaOperationRequestConverter,
    PlayAudioRequestConverter,
    PlayAudioToParticipantRequestConverter,
    AudioRoutingGroupRequestConverter,
    MuteParticipantRequestConverter,
    UnmuteParticipantRequestConverter,
    HoldMeetingAudioRequestConverter,
    ResumeMeetingAudioRequestConverter,
    UpdateAudioRoutingGroupRequestConverter
    )
from ._generated.models import (
    AddParticipantResult,
    CallConnectionProperties,
    PhoneNumberIdentifierModel,
    PlayAudioResult,
    AudioRoutingGroupResult,
    CreateAudioRoutingGroupResult,
    TransferCallResult,
    CallParticipant,
    AudioRoutingMode
    )
from ._shared.models import CommunicationIdentifier

if TYPE_CHECKING:
    from ._generated.operations import CallConnectionsOperations

class CallConnection(object):
    """An client to interact with the AzureCommunicationService Callingserver gateway.

    This client provides operations on top of a established call connection.

    :param str call_connection_id:
        The id of this call connection.
    :param CallConnectionsOperations call_connection_client:
        The call connection client.
    """
    def __init__(
            self,
            call_connection_id,  # type: str
            call_connection_client,  # type: CallConnectionsOperations
        ): # type: (...) -> None

        self.call_connection_id = call_connection_id
        self._call_connection_client = call_connection_client

    @distributed_trace()
    def get_call(
            self,
            **kwargs  # type: Any
        ): # type: (...) -> CallConnectionProperties
        """Get CallConnectionProperties of this CallConnection.

        :return: CallConnectionProperties
        :rtype: ~azure.communication.callingserver.CallConnectionProperties
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._call_connection_client.get_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace()
    def delete_call(
            self,
            **kwargs  # type: Any
        ): # type: (...) -> None
        """Terminates the conversation for all participants in the call.

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._call_connection_client.delete_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace()
    def hang_up(
            self,
            **kwargs  # type: Any
        ): # type: (...) -> None
        """Hangup the call.

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._call_connection_client.hangup_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace()
    def keep_alive(
            self,
            **kwargs  # type: Any
        ): # type: (...) -> None
        """Keep the call alive.

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._call_connection_client.keep_alive(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace()
    def cancel_all_media_operations(
            self,
            **kwargs  # type: Any
        ): # type: (...) -> None
        """Cancels all the currently active and pending PlayAudio operations in the call.

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._call_connection_client.cancel_all_media_operations(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace()
    def play_audio(
            self,
            audio_url,  # type: str
            is_looped=False,  # type: bool
            **kwargs  # type: Any
        ): # type: (...) -> PlayAudioResult
        """Play audio in the call.

        :param audio_url: Required. The media resource uri of the play audio request.
         Currently only Wave file (.wav) format audio prompts are supported.
         More specifically, the audio content in the wave file must be mono (single-channel),
         16-bit samples with a 16,000 (16KHz) sampling rate.
        :type audio_url: str
        :param is_looped: The flag indicating whether audio file needs to be played in loop or
         not.
        :type is_looped: bool
        :keyword operation_context: The value to identify context of the operation.
        :paramtype operation_context: str
        :keyword audio_file_id: An id for the media in the AudioFileUri, using which we cache the media
         resource.
        :paramtype audio_file_id: str
        :keyword callback_uri: The callback Uri to receive PlayAudio status notifications.
        :paramtype callback_uri: str
        :return: PlayAudioResult
        :rtype: ~azure.communication.callingserver.PlayAudioResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        operation_context = kwargs.pop("operation_context", None)
        audio_file_id = kwargs.pop("audio_file_id", None)
        callback_uri = kwargs.pop("callback_uri", None)

        play_audio_request = PlayAudioRequestConverter.convert(
            audio_url=audio_url,
            loop=is_looped,
            operation_context=operation_context,
            audio_file_id=audio_file_id,
            callback_uri=callback_uri
            )

        return self._call_connection_client.play_audio(
            call_connection_id=self.call_connection_id,
            play_audio_request=play_audio_request,
            **kwargs
        )

    @distributed_trace()
    def add_participant(
            self,
            participant,  # type: CommunicationIdentifier
            **kwargs  # type: Any
        ): # type: (...) -> AddParticipantResult
        """Add participant to the call connection.

        :param participant: Required. The participant identity.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :keyword alternate_caller_id: The alternate caller id.
        :paramtype alternate_caller_id: str
        :keyword operation_context: The operation context.
        :paramtype operation_context: str
        :return: AddParticipantResult
        :rtype: ~azure.communication.callingserver.AddParticipantResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        alternate_caller_id = kwargs.pop("alternate_caller_id", None)
        operation_context = kwargs.pop("operation_context", None)

        alternate_caller_id = (None
            if alternate_caller_id is None
            else PhoneNumberIdentifierModel(value=alternate_caller_id))

        add_participant_request = AddParticipantRequestConverter.convert(
            participant=serialize_identifier(participant),
            alternate_caller_id=alternate_caller_id,
            operation_context=operation_context
            )

        return self._call_connection_client.add_participant(
            call_connection_id=self.call_connection_id,
            add_participant_request=add_participant_request,
            **kwargs
        )

    @distributed_trace()
    def remove_participant(
            self,
            participant,  # type: CommunicationIdentifier
            **kwargs  # type: Any
        ): # type: (...) -> None
        """Remove participant from the call using identifier.

        :param participant: Required. The identifier of the participant to be removed from the call.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        remove_participant_request = RemoveParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return self._call_connection_client.remove_participant(
            call_connection_id=self.call_connection_id,
            remove_participant_request=remove_participant_request,
            **kwargs
        )

    @distributed_trace()
    def list_participants(
            self,
            **kwargs  # type: Any
        ): # type: (...) -> List[CallParticipant]
        """Get participants from a call.

        :return: List[CallParticipant]
        :rtype: List[~azure.communication.callingserver.models.CallParticipant]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._call_connection_client.get_participants(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace()
    def get_participant(
            self,
            participant,  # type: CommunicationIdentifier
            **kwargs  # type: Any
        ): # type: (...) -> List[CallParticipant]
        """Get participant from the call using identifier.

        :param participant: Required. The identifier of the target participant.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :return: List[CallParticipant]
        :rtype: List[~azure.communication.callingserver.models.CallParticipant]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        get_participant_request = GetParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return self._call_connection_client.get_participant(
            call_connection_id=self.call_connection_id,
            get_participant_request=get_participant_request,
            **kwargs
        )

    @distributed_trace()
    def play_audio_to_participant(
            self,
            participant,  # type: CommunicationIdentifier
            audio_url,  # type: str
            is_looped=False,  # type: bool
            **kwargs  # type: Any
        ): # type: (...) -> PlayAudioResult
        """Play audio to a participant.

        :param participant: Required. The media resource uri of the play audio request.
        :type participant: str
        :param audio_url: Required. The media resource uri of the play audio request.
         Currently only Wave file (.wav) format audio prompts are supported.
         More specifically, the audio content in the wave file must be mono (single-channel),
         16-bit samples with a 16,000 (16KHz) sampling rate.
        :type audio_url: str
        :param is_looped: The flag indicating whether audio file needs to be played in loop or
         not.
        :type is_looped: bool
        :keyword operation_context: The value to identify context of the operation.
        :paramtype operation_context: str
        :keyword audio_file_id: An id for the media in the AudioFileUri, using which we cache the media
         resource.
        :paramtype audio_file_id: str
        :keyword callback_uri: The callback Uri to receive PlayAudio status notifications.
        :paramtype callback_uri: str
        :return: PlayAudioResult
        :rtype: ~azure.communication.callingserver.PlayAudioResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        operation_context = kwargs.pop("operation_context", None)
        audio_file_id = kwargs.pop("audio_file_id", None)
        callback_uri = kwargs.pop("callback_uri", None)

        play_audio_to_participant_request = PlayAudioToParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant),
            audio_url=audio_url,
            loop=is_looped,
            operation_context=operation_context,
            audio_file_id=audio_file_id,
            callback_uri=callback_uri
            )

        return self._call_connection_client.participant_play_audio(
            call_connection_id=self.call_connection_id,
            play_audio_to_participant_request=play_audio_to_participant_request,
            **kwargs
        )

    @distributed_trace()
    def cancel_participant_media_operation(
            self,
            participant,  # type: CommunicationIdentifier
            media_operation_id,  # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> None
        """Cancel media operation for a participant.

        :param participant: Required. The identifier of the participant.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :param media_operation_id: Required. The operationId of the media operation to cancel.
        :type media_operation_id: str
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        cancel_media_operation_request = CancelParticipantMediaOperationRequestConverter.convert(
            identifier=serialize_identifier(participant),
            media_operation_id=media_operation_id
            )

        return self._call_connection_client.cancel_participant_media_operation(
            call_connection_id=self.call_connection_id,
            cancel_media_operation_request=cancel_media_operation_request,
            **kwargs
        )

    @distributed_trace()
    def mute_participant(
            self,
            participant,  # type: CommunicationIdentifier
            **kwargs  # type: Any
        ):  # type: (...) -> None
        """Mutes the participant.

        :param participant: Required. The identifier of the participant to be muted in the call.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        mute_participant_request = MuteParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return self._call_connection_client.mute_participant(
            call_connection_id=self.call_connection_id,
            mute_participant_request=mute_participant_request,
            **kwargs
        )

    @distributed_trace()
    def unmute_participant(
            self,
            participant,  # type: CommunicationIdentifier
            **kwargs  # type: Any
        ):  # type: (...) -> None
        """Unmute participant in the call.

        :param participant: Required. The identifier of the participant to be unmute in the call.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        unmute_participant_request = UnmuteParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return self._call_connection_client.unmute_participant(
            call_connection_id=self.call_connection_id,
            unmute_participant_request=unmute_participant_request,
            **kwargs
        )

    @distributed_trace()
    def hold_participant_meeting_audio(
            self,
            participant,  # type: CommunicationIdentifier
            **kwargs  # type: Any
        ):  # type: (...) -> None
        """Removes the participant from the meeting's default audio mix so the participant
         does not hear anything from the meeting and cannot add audio into the meeting.

        :param participant: Required. The identifier of the participant.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        hold_meeting_audio_request = HoldMeetingAudioRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return self._call_connection_client.hold_participant_meeting_audio(
            call_connection_id=self.call_connection_id,
            hold_meeting_audio_request=hold_meeting_audio_request,
            **kwargs
        )

    @distributed_trace()
    def resume_participant_meeting_audio(
            self,
            participant,  # type: CommunicationIdentifier
            **kwargs  # type: Any
        ):  # type: (...) -> None
        """Adds the participant back into the meeting's default audio mix so the participant
         begins to hear everything from the meeting and can add audio into the meeting.

        :param participant: Required. The identifier of the participant.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        resume_participant_meeting_audio_request = ResumeMeetingAudioRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return self._call_connection_client.resume_participant_meeting_audio(
            call_connection_id=self.call_connection_id,
            resume_meeting_audio_request=resume_participant_meeting_audio_request,
            **kwargs
        )

    @distributed_trace()
    def transfer(
            self,
            target_participant,  # type: CommunicationIdentifier
            target_call_connection_id,  # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> TransferCallResult
        """Transfer the call.

        :param target_participant: Required. The target participant.
        :type target_participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :param target_call_connection_id: The target call connection id to transfer to.
        :type target_call_connection_id: str
        :keyword alternate_caller_id: The alternate identity of the transferor if transferring to a pstn
         number.
        :paramtype alternate_caller_id: str
        :keyword user_to_user_information: The user to user information.
        :paramtype user_to_user_information: str
        :keyword operation_context: The operation context.
        :paramtype operation_context: str
        :return: TransferCallResult
        :rtype: ~azure.communication.callingserver.TransferCallResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        alternate_caller_id = kwargs.pop("alternate_caller_id", None)
        user_to_user_information = kwargs.pop("user_to_user_information", None)
        operation_context = kwargs.pop("operation_context", None)

        alternate_caller_id = (None
            if alternate_caller_id is None
            else PhoneNumberIdentifierModel(value=alternate_caller_id))

        transfer_call_request = TransferCallRequestConverter.convert(
            target_participant=serialize_identifier(target_participant),
            target_call_connection_id=target_call_connection_id,
            alternate_caller_id=alternate_caller_id,
            user_to_user_information=user_to_user_information,
            operation_context=operation_context
            )

        return self._call_connection_client.transfer(
            call_connection_id=self.call_connection_id,
            transfer_call_request=transfer_call_request,
            **kwargs
        )

    @distributed_trace()
    def create_audio_routing_group(
            self,
            audio_routing_mode,  # type: AudioRoutingMode
            targets, # type: List[CommunicationIdentifier]
            **kwargs  # type: Any
        ):  # type: (...) -> CreateAudioRoutingGroupResult
        """Create audio routing group in a call.

        :param audio_routing_mode: Required. The audio routing mode. Possible values include:
         "oneToOne", "multicast".
        :type audio_routing_mode: str or ~azure.communication.callingserver.models.AudioRoutingMode
        :param targets: Required. The target identities that would be receivers in the audio routing
         group.
        :type targets: list[~azure.communication.callingserver.models.CommunicationIdentifier]
        :return: CreateAudioRoutingGroupResult
        :rtype: ~azure.communication.callingserver.models.CreateAudioRoutingGroupResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        audio_routing_group_request = AudioRoutingGroupRequestConverter.convert(
            audio_routing_mode=audio_routing_mode,
            target_identities=[serialize_identifier(m) for m in targets]
            )

        return self._call_connection_client.create_audio_routing_group(
            call_connection_id=self.call_connection_id,
            audio_routing_group_request=audio_routing_group_request,
            **kwargs
        )

    @distributed_trace()
    def list_audio_routing_groups(
            self,
            audio_routing_group_id,  # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> AudioRoutingGroupResult
        """List audio routing group in a call.

        :param audio_routing_group_id: Required. The audio routing group id.
        :type audio_routing_group_id: str
        :return: AudioRoutingGroupResult
        :rtype: ~azure.communication.callingserver.models.AudioRoutingGroupResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._call_connection_client.get_audio_routing_groups(
            call_connection_id=self.call_connection_id,
            audio_routing_group_id=audio_routing_group_id,
            **kwargs
        )

    @distributed_trace()
    def delete_audio_routing_group(
            self,
            audio_routing_group_id,  # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> None
        """Delete audio routing group from a call.

        :param audio_routing_group_id: Required. The audio routing group id.
        :type audio_routing_group_id: str
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._call_connection_client.delete_audio_routing_group(
            call_connection_id=self.call_connection_id,
            audio_routing_group_id=audio_routing_group_id,
            **kwargs
        )

    @distributed_trace()
    def update_audio_routing_group(
            self,
            audio_routing_group_id,  # type: str
            targets, # type: List[CommunicationIdentifier]
            **kwargs  # type: Any
        ):  # type: (...) -> None
        """Update audio routing group.

        :param audio_routing_group_id: Required. The audio routing group id.
        :type audio_routing_group_id: str
        :param targets: Required. The target identities that would be receivers in the audio routing
         group.
        :type targets: list[~azure.communication.callingserver.models.CommunicationIdentifier]
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        update_audio_routing_group_request = UpdateAudioRoutingGroupRequestConverter.convert(
            target_identities=[serialize_identifier(m) for m in targets]
            )

        return self._call_connection_client.update_audio_routing_group(
            call_connection_id=self.call_connection_id,
            audio_routing_group_id=audio_routing_group_id,
            update_audio_routing_group_request=update_audio_routing_group_request,
            **kwargs
        )
