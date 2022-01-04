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
    TransferToParticipantRequestConverter,
    TransferToCallRequestConverter,
    CancelParticipantMediaOperationRequestConverter,
    PlayAudioRequestConverter,
    PlayAudioToParticipantRequestConverter,
    AudioGroupRequestConverter,
    MuteParticipantRequestConverter,
    UnmuteParticipantRequestConverter,
    RemoveFromDefaultAudioGroupRequestConverter,
    AddToDefaultAudioGroupRequestConverter,
    UpdateAudioGroupRequestConverter
    )
from .._generated.models import (
    AddParticipantResult,
    CallConnectionProperties,
    PhoneNumberIdentifierModel,
    PlayAudioResult,
    AudioGroupResult,
    CreateAudioGroupResult,
    TransferCallResult,
    CallParticipant,
    AudioRoutingMode
    )
from .._shared.models import CommunicationIdentifier, PhoneNumberIdentifier
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
            alternate_caller_id: Optional[PhoneNumberIdentifier] = None,
            operation_context: Optional[str] = None,
            **kwargs: Any
        ) -> AddParticipantResult:
        """Add participant to the call connection.

        :param participant: Required. The participant identity.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :keyword alternate_caller_id: The alternate caller id.
        :paramtype alternate_caller_id: ~azure.communication.callingserver.models.PhoneNumberIdentifier
        :keyword operation_context: The operation context.
        :paramtype operation_context: str
        :return: AddParticipantResult
        :rtype: ~azure.communication.callingserver.AddParticipantResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        add_participant_request = AddParticipantRequestConverter.convert(
            participant=serialize_identifier(participant),
            alternate_caller_id=(None
                if alternate_caller_id is None
                else PhoneNumberIdentifierModel(value=alternate_caller_id.properties['value'])),
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
        """Mute the participant

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
    async def remove_from_default_audio_group(
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
        remove_from_default_audio_group_request = RemoveFromDefaultAudioGroupRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return await self._call_connection_client.remove_participant_from_default_audio_group(
            call_connection_id=self.call_connection_id,
            remove_from_default_audio_group_request=remove_from_default_audio_group_request,
            **kwargs
        )

    @distributed_trace_async()
    async def add_participant_to_default_audio_group(
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
        add_to_default_audio_group_request = AddToDefaultAudioGroupRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return await self._call_connection_client.add_participant_to_default_audio_group(
            call_connection_id=self.call_connection_id,
            add_to_default_audio_group_request=add_to_default_audio_group_request,
            **kwargs
        )

    @distributed_trace_async()
    async def transfer_to_participant(
            self,
            target_participant: CommunicationIdentifier,
            *,
            alternate_caller_id: Optional[PhoneNumberIdentifier] = None,
            user_to_user_information: Optional[str] = None,
            operation_context: Optional[str] = None,
            **kwargs: Any
        )-> TransferCallResult:
        """Transfer the call to a participant.

        :param target_participant: Required. The target participant.
        :type target_participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :keyword alternate_caller_id: The alternate identity of the transferor if transferring to a pstn
         number.
        :paramtype alternate_caller_id: ~azure.communication.callingserver.models.PhoneNumberIdentifier
        :keyword user_to_user_information: The user to user information.
        :paramtype user_to_user_information: str
        :keyword operation_context: The operation context.
        :paramtype operation_context: str
        :return: TransferCallResult
        :rtype: ~azure.communication.callingserver.TransferCallResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        transfer_to_participant_request = TransferToParticipantRequestConverter.convert(
            target_participant=serialize_identifier(target_participant),
            alternate_caller_id=(None
                if alternate_caller_id is None
                else PhoneNumberIdentifierModel(value=alternate_caller_id.properties['value'])),
            user_to_user_information=user_to_user_information,
            operation_context=operation_context
            )

        return await self._call_connection_client.transfer_to_participant(
            call_connection_id=self.call_connection_id,
            transfer_to_participant_request=transfer_to_participant_request,
            **kwargs
        )

    @distributed_trace_async()
    async def transfer_to_call(
            self,
            target_call_connection_id: str,
            *,
            user_to_user_information: Optional[str] = None,
            operation_context: Optional[str] = None,
            **kwargs: Any
        )-> TransferCallResult:
        """Transfer the current call to another call.

        :param target_call_connection_id: The target call connection id to transfer to.
        :type target_call_connection_id: str
        :keyword user_to_user_information: The user to user information.
        :paramtype user_to_user_information: str
        :keyword operation_context: The operation context.
        :paramtype operation_context: str
        :return: TransferCallResult
        :rtype: ~azure.communication.callingserver.TransferCallResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """

        transfer_to_call_request = TransferToCallRequestConverter.convert(
            target_call_connection_id=target_call_connection_id,
            user_to_user_information=user_to_user_information,
            operation_context=operation_context
            )

        return await self._call_connection_client.transfer_to_call(
            call_connection_id=self.call_connection_id,
            transfer_to_call_request=transfer_to_call_request,
            **kwargs
        )

    @distributed_trace_async()
    async def create_audio_group(
            self,
            audio_routing_mode: AudioRoutingMode,
            targets: List[CommunicationIdentifier],
            **kwargs: Any
        ) -> CreateAudioGroupResult:
        """Create audio group in a call.

        :param audio_routing_mode: Required. The audio routing mode. Possible values include:
         "oneToOne", "multicast".
        :type audio_routing_mode: str or ~azure.communication.callingserver.models.AudioRoutingMode
        :param targets: Required. The target identities that would be receivers in the audio routing
         group.
        :type targets: list[~azure.communication.callingserver.models.CommunicationIdentifier]
        :return: CreateAudioGroupResult
        :rtype: ~azure.communication.callingserver.models.CreateAudioGroupResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        audio_group_request = AudioGroupRequestConverter.convert(
            audio_routing_mode=audio_routing_mode,
            target_identities=[serialize_identifier(m) for m in targets]
            )

        return await self._call_connection_client.create_audio_group(
            call_connection_id=self.call_connection_id,
            audio_group_request=audio_group_request,
            **kwargs
        )

    @distributed_trace_async()
    async def list_audio_groups(
            self,
            audio_group_id: str,
            **kwargs: Any
        ) -> AudioGroupResult:
        """List audio groups in a call.

        :param audio_group_id: Required. The audio group id.
        :type audio_group_id: str
        :return: AudioGroupResult
        :rtype: ~azure.communication.callingserver.models.AudioGroupResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return await self._call_connection_client.get_audio_groups(
            call_connection_id=self.call_connection_id,
            audio_group_id=audio_group_id,
            **kwargs
        )

    @distributed_trace_async()
    async def delete_audio_group(
            self,
            audio_group_id: str,
            **kwargs: Any
        ) -> None:
        """Delete audio group from a call.

        :param audio_group_id: Required. The audio group id.
        :type audio_group_id: str
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return await self._call_connection_client.delete_audio_group(
            call_connection_id=self.call_connection_id,
            audio_group_id=audio_group_id,
            **kwargs
        )

    @distributed_trace_async()
    async def update_audio_group(
            self,
            audio_group_id: str,
            targets: List[CommunicationIdentifier],
            **kwargs: Any
        ) -> None:
        """Update audio group.

        :param audio_group_id: Required. The audio group id.
        :type audio_group_id: str
        :param targets: Required. The target identities that would be receivers in the audio
         group.
        :type targets: list[~azure.communication.callingserver.models.CommunicationIdentifier]
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        update_audio_group_request = UpdateAudioGroupRequestConverter.convert(
            target_identities=[serialize_identifier(m) for m in targets]
            )

        return await self._call_connection_client.update_audio_group(
            call_connection_id=self.call_connection_id,
            audio_group_id=audio_group_id,
            update_audio_group_request=update_audio_group_request,
            **kwargs
        )

    async def close(self) -> None:
        await self._callingserver_service_client.close()

    async def __aenter__(self) -> 'CallConnection':
        await self._callingserver_service_client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._callingserver_service_client.__aexit__(*args)
