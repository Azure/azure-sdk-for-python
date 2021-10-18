# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-public-methods
from typing import TYPE_CHECKING, List, Any, Optional  # pylint: disable=unused-import
from azure.core.tracing.decorator import distributed_trace
from .utils._utils import CallingServerUtils
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
    CallParticipant,
    AudioRoutingMode
    )
from ._shared.models import CommunicationIdentifier

if TYPE_CHECKING:
    from ._generated.operations import CallConnectionsOperations
    from ._models import PlayAudioOptions

class CallConnection(object):
    def __init__(
            self,
            call_connection_id,  # type: str
            call_connection_client  # type: CallConnectionsOperations
        ): # type: (...) -> None

        self.call_connection_id = call_connection_id
        self._call_connection_client = call_connection_client

    @distributed_trace()
    def get_call(
            self,
            **kwargs  # type: Any
        ): # type: (...) -> CallConnectionProperties

        return self._call_connection_client.get_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace()
    def delete_call(
            self,
            **kwargs  # type: Any
        ): # type: (...) -> None

        return self._call_connection_client.delete_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace()
    def hang_up(
            self,
            **kwargs  # type: Any
        ): # type: (...) -> None

        return self._call_connection_client.hangup_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace()
    def keep_alive(
            self,
            **kwargs  # type: Any
        ): # type: (...) -> None

        return self._call_connection_client.keep_alive(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace()
    def cancel_all_media_operations(
            self,
            **kwargs  # type: Any
        ): # type: (...) -> None

        return self._call_connection_client.cancel_all_media_operations(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    @distributed_trace()
    def play_audio(
            self,
            audio_file_uri,  # type: str
            play_audio_options,  # type: PlayAudioOptions
            **kwargs  # type: Any
        ): # type: (...) -> PlayAudioResult

        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")

        if not CallingServerUtils.is_valid_url(audio_file_uri):
            raise ValueError("audio_file_uri is invalid")

        if not play_audio_options:
            raise ValueError("options can not be None")

        if not play_audio_options.audio_file_id:
            raise ValueError("audio_file_id can not be None")

        if not CallingServerUtils.is_valid_url(play_audio_options.callback_uri):
            raise ValueError("callback_uri is invalid")

        play_audio_request = PlayAudioRequestConverter.convert(audio_file_uri, play_audio_options)

        return self._call_connection_client.play_audio(
            call_connection_id=self.call_connection_id,
            request=play_audio_request,
            **kwargs
        )

    @distributed_trace()
    def add_participant(
            self,
            participant,  # type: CommunicationIdentifier
            alternate_caller_id=None,  # type: Optional[str]
            operation_context=None,  # type: Optional[str]
            **kwargs  # type: Any
        ): # type: (...) -> AddParticipantResult

        if not participant:
            raise ValueError("participant can not be None")

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

        remove_participant_request = RemoveParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return self._call_connection_client.remove_participant(
            call_connection_id=self.call_connection_id,
            remove_participant_request=remove_participant_request,
            **kwargs
        )

    @distributed_trace()
    def get_participants(
            self,
            **kwargs  # type: Any
        ): # type: (...) -> List[CallParticipant]

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
            audio_file_uri,  # type: str
            play_audio_options,  # type: PlayAudioOptions
            **kwargs  # type: Any
        ): # type: (...) -> PlayAudioResult

        if not participant:
            raise ValueError("participant can not be None")

        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")

        if not CallingServerUtils.is_valid_url(audio_file_uri):
            raise ValueError("audio_file_uri is invalid")

        if not play_audio_options:
            raise ValueError("play_audio_options can not be None")

        if not CallingServerUtils.is_valid_url(play_audio_options.callback_uri):
            raise ValueError("callback_uri is invalid")

        play_audio_to_participant_request = PlayAudioToParticipantRequestConverter.convert(
            identifier=serialize_identifier(participant),
            audio_file_uri=audio_file_uri,
            play_audio_options=play_audio_options
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

        if not participant:
            raise ValueError("participant can not be None")

        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

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

        if not participant:
            raise ValueError("participant can not be None")

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

        if not participant:
            raise ValueError("participant can not be None")

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

        if not participant:
            raise ValueError("participant can not be None")

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

        if not participant:
            raise ValueError("participant can not be None")

        resume_participant_meeting_audio_request = ResumeMeetingAudioRequestConverter.convert(
            identifier=serialize_identifier(participant)
            )

        return self._call_connection_client.resume_participant_meeting_audio(
            call_connection_id=self.call_connection_id,
            resume_meeting_audio_request=resume_participant_meeting_audio_request,
            **kwargs
        )

    @distributed_trace()
    def transfer_call(
            self,
            target_participant,  # type: CommunicationIdentifier
            target_call_connection_id,  # type: str
            user_to_user_information=None,  # type: Optional[str]
            operation_context=None,  # type: str
            callback_uri=None,  # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> None

        if not target_participant:
            raise ValueError("target_participant can not be None")
        if not target_call_connection_id:
            raise ValueError("target_call_connection_id can not be None")

        transfer_call_request = TransferCallRequestConverter.convert(
            target_participant=serialize_identifier(target_participant),
            target_call_connection_id=target_call_connection_id,
            user_to_user_information=user_to_user_information,
            operation_context=operation_context,
            callback_uri=callback_uri
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

        if not audio_routing_mode:
            raise ValueError("audio_routing_mode can not be None")
        if not targets:
            raise ValueError("targets can not be None")

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
    def get_audio_routing_groups(
            self,
            audio_routing_group_id,  # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> AudioRoutingGroupResult

        if not audio_routing_group_id:
            raise ValueError("audio_routing_group_id can not be None")

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

        if not audio_routing_group_id:
            raise ValueError("audio_routing_group_id can not be None")

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

        if not audio_routing_group_id:
            raise ValueError("audio_routing_group_id can not be None")
        if not targets:
            raise ValueError("targets can not be None")

        update_audio_routing_group_request = UpdateAudioRoutingGroupRequestConverter.convert(
            target_identities=[serialize_identifier(m) for m in targets]
            )

        return self._call_connection_client.update_audio_routing_group(
            call_connection_id=self.call_connection_id,
            audio_routing_group_id=audio_routing_group_id,
            update_audio_routing_group_request=update_audio_routing_group_request,
            **kwargs
        )
