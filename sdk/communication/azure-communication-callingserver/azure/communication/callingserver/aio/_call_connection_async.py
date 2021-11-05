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
from ..utils._utils import CallingServerUtils
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
    CallParticipant,
    AudioRoutingMode
    )
from .._shared.models import CommunicationIdentifier
from .._generated.aio._azure_communication_calling_server_service import \
    AzureCommunicationCallingServerService  # pylint: disable=unused-import

if TYPE_CHECKING:
    from .._generated.aio.operations import CallConnectionsOperations
    from .._models import PlayAudioOptions

class CallConnection:

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
        return await self._call_connection_client.get_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def delete_call(
            self,
            **kwargs: Any
        ) -> None:

        return await self._call_connection_client.delete_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def hang_up(
            self,
            **kwargs: Any
        ) -> None:

        return await self._call_connection_client.hangup_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def keep_alive(
            self,
            **kwargs: Any
        ) -> None:

        return await self._call_connection_client.keep_alive(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def cancel_all_media_operations(
            self,
            **kwargs: Any
        ) -> None:


        return await self._call_connection_client.cancel_all_media_operations(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def play_audio(
            self,
            audio_url: str,
            play_audio_options: 'PlayAudioOptions',
            **kwargs: Any
        ) -> PlayAudioResult:

        play_audio_request = PlayAudioRequestConverter.convert(audio_url, play_audio_options)

        return await self._call_connection_client.play_audio(
            call_connection_id=self.call_connection_id,
            request=play_audio_request,
            **kwargs
        )

    @distributed_trace_async()
    async def add_participant(
            self,
            participant: CommunicationIdentifier,
            alternate_caller_id: Optional[str] = None,
            operation_context: Optional[str] = None,
            **kwargs: Any
        ) -> AddParticipantResult:

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

        remove_participant_request = RemoveParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return await self._call_connection_client.remove_participant(
            call_connection_id=self.call_connection_id,
            remove_participant_request=remove_participant_request,
            **kwargs
        )

    @distributed_trace_async()
    async def get_participants(
            self,
            **kwargs: Any
        )-> List[CallParticipant]:

        return await self._call_connection_client.get_participants(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace_async()
    async def get_participant(
            self,
            participant: CommunicationIdentifier,
            **kwargs  # type: Any
        ) -> List[CallParticipant]:

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
            play_audio_options: 'PlayAudioOptions',
            **kwargs: Any
        ) -> PlayAudioResult:

        play_audio_to_participant_request = PlayAudioToParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant),
            audio_url=audio_url,
            play_audio_options=play_audio_options
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

        resume_participant_meeting_audio_request = ResumeMeetingAudioRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return await self._call_connection_client.resume_participant_meeting_audio(
            call_connection_id=self.call_connection_id,
            resume_meeting_audio_request=resume_participant_meeting_audio_request,
            **kwargs
        )

    @distributed_trace_async()
    async def transfer_call(
            self,
            target_participant: CommunicationIdentifier,
            target_call_connection_id: str,
            user_to_user_information: Optional[str] = None,
            operation_context: Optional[str] = None,
            callback_uri: Optional[str] = None,
            **kwargs: Any
        )-> None:

        transfer_call_request = TransferCallRequestConverter.convert(
            target_participant=serialize_identifier(target_participant),
            target_call_connection_id=target_call_connection_id,
            user_to_user_information=user_to_user_information,
            operation_context=operation_context,
            callback_uri=callback_uri
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
    async def get_audio_routing_groups(
            self,
            audio_routing_group_id: str,
            **kwargs: Any
        ) -> AudioRoutingGroupResult:

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
