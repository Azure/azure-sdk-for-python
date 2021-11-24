# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=unsubscriptable-object,too-many-public-methods
# disabled unsubscriptable-object because of pylint bug referenced here:
# https://github.com/PyCQA/pylint/issues/3882

from typing import TYPE_CHECKING, List, Any, Optional  # pylint: disable=unused-import
from azure.core.tracing.decorator_async import distributed_trace_async
from .._communication_identifier_serializer import serialize_identifier
from .._converters import (
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
from .._generated.models import (
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
from .._shared.models import CommunicationIdentifier
from .._generated.aio._azure_communication_calling_server_service import \
    AzureCommunicationCallingServerService  # pylint: disable=unused-import

if TYPE_CHECKING:
    from .._generated.aio.operations import CallConnectionsOperations

class CallConnection:
    """An client to interact with the AzureCommunicationService Callingserver gateway.

    This client provides operations on top of a established call connection.

    :param str call_connection_id:
        The id of this call connection.
    :param CallConnectionsOperations call_connection_client:
        The call connection client.
    """
    def __init__(
            self,
            call_connection_id: str,
            call_connection_client: 'CallConnectionsOperations',
            callingserver_service_client: 'AzureCommunicationCallingServerService'
        ) -> None:

        self.call_connection_id = call_connection_id
        self._call_connection_client = call_connection_client
        self._callingserver_service_client = callingserver_service_client

    @distributed_trace_async()
    async def get_call(
            self,
            **kwargs: Any
        ) -> CallConnectionProperties:
        """Get CallConnectionProperties of this CallConnection.

        :return: CallConnectionProperties
        :rtype: ~azure.communication.callingserver.CallConnectionProperties
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return await self._call_connection_client.get_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def delete(
            self,
            **kwargs: Any
        ) -> None:
        """Terminates the conversation for all participants in the call.

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return await self._call_connection_client.delete_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def hang_up(
            self,
            **kwargs: Any
        ) -> None:
        """Hangup the call.

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return await self._call_connection_client.hangup_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def keep_alive(
            self,
            **kwargs: Any
        ) -> None:
        """Keep the call alive.

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return await self._call_connection_client.keep_alive(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def cancel_all_media_operations(
            self,
            **kwargs: Any
        ) -> None:
        """Cancels all the currently active and pending PlayAudio operations in the call.

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return await self._call_connection_client.cancel_all_media_operations(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def play_audio(
            self,
            audio_url: str,
            is_looped: bool = False,
            *,
            operation_context: Optional[str] = None,
            audio_file_id: Optional[str] = None,
            **kwargs: Any
        ) -> PlayAudioResult:
        """Redirect the call.

        :param call_locator: Required. The call locator.
        :type call_locator: ~azure.communication.callingserver.models.CallLocator
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
        :return: PlayAudioResult
        :rtype: ~azure.communication.callingserver.PlayAudioResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        play_audio_request = PlayAudioRequestConverter.convert(
            audio_url=audio_url,
            loop=is_looped,
            operation_context=operation_context,
            audio_file_id=audio_file_id
            )

        return await self._call_connection_client.play_audio(
            call_connection_id=self.call_connection_id,
            play_audio_request=play_audio_request,
            **kwargs
        )

    @distributed_trace_async()
    async def add_participant(
            self,
            participant: CommunicationIdentifier,
            *,
            alternate_caller_id: Optional[str] = None,
            operation_context: Optional[str] = None,
            **kwargs: Any
        ) -> AddParticipantResult:
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
        alternate_caller_id = (None
            if alternate_caller_id is None
            else PhoneNumberIdentifierModel(value=alternate_caller_id))

        add_participant_request = AddParticipantRequestConverter.convert(
            participant=serialize_identifier(participant),
            alternate_caller_id=alternate_caller_id,
            operation_context=operation_context
            )

        return await self._call_connection_client.add_participant(
            call_connection_id=self.call_connection_id,
            add_participant_request=add_participant_request,
            **kwargs
        )

    @distributed_trace_async()
    async def remove_participant(
            self,
            participant: CommunicationIdentifier,
            **kwargs: Any
        ) -> None:
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

        return await self._call_connection_client.remove_participant(
            call_connection_id=self.call_connection_id,
            remove_participant_request=remove_participant_request,
            **kwargs
        )

    @distributed_trace_async()
    async def list_participants(
            self,
            **kwargs: Any
        )-> List[CallParticipant]:
        """Get participants from a call.

        :return: List[CallParticipant]
        :rtype: List[~azure.communication.callingserver.models.CallParticipant]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return await self._call_connection_client.get_participants(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def get_participant(
            self,
            participant: CommunicationIdentifier,
            **kwargs  # type: Any
        ) -> CallParticipant:
        """Get participant from the call using identifier.

        :param participant: Required. The identifier of the target participant.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :return: CallParticipant
        :rtype: ~azure.communication.callingserver.models.CallParticipant
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        get_participant_request = GetParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return await self._call_connection_client.get_participant(
            call_connection_id=self.call_connection_id,
            get_participant_request=get_participant_request,
            **kwargs
        )

    @distributed_trace_async()
    async def play_audio_to_participant(
            self,
            participant: CommunicationIdentifier,
            audio_url: str,
            is_looped: bool = False,
            *,
            operation_context: Optional[str] = None,
            audio_file_id: Optional[str] = None,
            **kwargs: Any
        ) -> PlayAudioResult:
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
        :return: PlayAudioResult
        :rtype: ~azure.communication.callingserver.PlayAudioResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        play_audio_to_participant_request = PlayAudioToParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant),
            audio_url=audio_url,
            loop=is_looped,
            operation_context=operation_context,
            audio_file_id=audio_file_id
            )

        return await self._call_connection_client.participant_play_audio(
            call_connection_id=self.call_connection_id,
            play_audio_to_participant_request=play_audio_to_participant_request,
            **kwargs
        )

    @distributed_trace_async()
    async def cancel_participant_media_operation(
            self,
            participant: CommunicationIdentifier,
            media_operation_id: str,
            **kwargs: Any
        )-> None:
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

        return await self._call_connection_client.cancel_participant_media_operation(
            call_connection_id=self.call_connection_id,
            cancel_media_operation_request=cancel_media_operation_request,
            **kwargs
        )

    @distributed_trace_async()
    async def mute_participant(
            self,
            participant: CommunicationIdentifier,
            **kwargs: Any
        ) -> None:
        """Mutes the participant

        :param participant: Required. The identifier of the participant to be muted in the call.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        mute_participant_request = MuteParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return await self._call_connection_client.mute_participant(
            call_connection_id=self.call_connection_id,
            mute_participant_request=mute_participant_request,
            **kwargs
        )

    @distributed_trace_async()
    async def unmute_participant(
            self,
            participant: CommunicationIdentifier,
            **kwargs: Any
        ) -> None:
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

        return await self._call_connection_client.unmute_participant(
            call_connection_id=self.call_connection_id,
            unmute_participant_request=unmute_participant_request,
            **kwargs
        )

    @distributed_trace_async()
    async def hold_participant_meeting_audio(
            self,
            participant: CommunicationIdentifier,
            **kwargs: Any
        ) -> None:
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

        return await self._call_connection_client.hold_participant_meeting_audio(
            call_connection_id=self.call_connection_id,
            hold_meeting_audio_request=hold_meeting_audio_request,
            **kwargs
        )

    @distributed_trace_async()
    async def resume_participant_meeting_audio(
            self,
            participant: CommunicationIdentifier,
            **kwargs: Any
        )  -> None:
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

        return await self._call_connection_client.resume_participant_meeting_audio(
            call_connection_id=self.call_connection_id,
            resume_meeting_audio_request=resume_participant_meeting_audio_request,
            **kwargs
        )

    @distributed_trace_async()
    async def transfer(
            self,
            target_participant: CommunicationIdentifier,
            target_call_connection_id: str,
            *,
            alternate_caller_id: Optional[str] = None,
            user_to_user_information: Optional[str] = None,
            operation_context: Optional[str] = None,
            **kwargs: Any
        )-> TransferCallResult:
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

        return await self._call_connection_client.transfer(
            call_connection_id=self.call_connection_id,
            transfer_call_request=transfer_call_request,
            **kwargs
        )

    @distributed_trace_async()
    async def create_audio_routing_group(
            self,
            audio_routing_mode: AudioRoutingMode,
            targets: List[CommunicationIdentifier],
            **kwargs: Any
        ) -> CreateAudioRoutingGroupResult:
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

        return await self._call_connection_client.create_audio_routing_group(
            call_connection_id=self.call_connection_id,
            audio_routing_group_request=audio_routing_group_request,
            **kwargs
        )

    @distributed_trace_async()
    async def list_audio_routing_groups(
            self,
            audio_routing_group_id: str,
            **kwargs: Any
        ) -> AudioRoutingGroupResult:
        """List audio routing groups in a call.

        :param audio_routing_group_id: Required. The audio routing group id.
        :type audio_routing_group_id: str
        :return: AudioRoutingGroupResult
        :rtype: ~azure.communication.callingserver.models.AudioRoutingGroupResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return await self._call_connection_client.get_audio_routing_groups(
            call_connection_id=self.call_connection_id,
            audio_routing_group_id=audio_routing_group_id,
            **kwargs
        )

    @distributed_trace_async()
    async def delete_audio_routing_group(
            self,
            audio_routing_group_id: str,
            **kwargs: Any
        ) -> None:
        """Delete audio routing group from a call.

        :param audio_routing_group_id: Required. The audio routing group id.
        :type audio_routing_group_id: str
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return await self._call_connection_client.delete_audio_routing_group(
            call_connection_id=self.call_connection_id,
            audio_routing_group_id=audio_routing_group_id,
            **kwargs
        )

    @distributed_trace_async()
    async def update_audio_routing_group(
            self,
            audio_routing_group_id: str,
            targets: List[CommunicationIdentifier],
            **kwargs: Any
        ) -> None:
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

        return await self._call_connection_client.update_audio_routing_group(
            call_connection_id=self.call_connection_id,
            audio_routing_group_id=audio_routing_group_id,
            update_audio_routing_group_request=update_audio_routing_group_request,
            **kwargs
        )

    async def close(self) -> None:
        await self._callingserver_service_client.close()

    async def __aenter__(self) -> 'CallConnection':
        await self._callingserver_service_client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._callingserver_service_client.__aexit__(*args)
