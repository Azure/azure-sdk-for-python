# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Any, Optional  # pylint: disable=unused-import

from azure.core.tracing.decorator import distributed_trace

from ._communication_identifier_serializer import serialize_identifier
from ._converters import (
    AddParticipantRequestConverter,
    CancelAllMediaOperationsConverter,
    TransferCallRequestConverter,
    CancelMediaOperationRequestConverter,
    PlayAudioRequestConverter
    )
from ._generated.models import (AddParticipantResult,
                                CancelAllMediaOperationsResult,
                                PhoneNumberIdentifierModel,
                                PlayAudioResult)
from ._shared.models import CommunicationIdentifier

if TYPE_CHECKING:
    from ._generated.operations import CallConnectionsOperations
    from ._models import PlayAudioOptions

from .utils._utils import CallingServerUtils

class CallConnection(object):
    def __init__(
            self,
            call_connection_id,  # type: str
            call_connection_client  # type: CallConnectionsOperations
        ): # type: (...) -> None

        self.call_connection_id = call_connection_id
        self._call_connection_client = call_connection_client

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
    def cancel_all_media_operations(
            self,
            operation_context=None,  # type: Optional[str]
            **kwargs  # type: Any
        ): # type: (...) -> CancelAllMediaOperationsResult

        cancel_all_media_operations_request = CancelAllMediaOperationsConverter.convert(operation_context)

        return self._call_connection_client.cancel_all_media_operations(
            call_connection_id=self.call_connection_id,
            cancel_all_media_operation_request=cancel_all_media_operations_request,
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
            participant_id,  # type: str
            **kwargs  # type: Any
        ): # type: (...) -> None

        return self._call_connection_client.remove_participant(
            call_connection_id=self.call_connection_id,
            participant_id=participant_id,
            **kwargs
        )

    @distributed_trace()
    def cancel_participant_media_operation(
            self,
            participant_id,  # type: str
            media_operation_id,  # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> None

        if not participant_id:
            raise ValueError("participant_id can not be None")

        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        cancel_media_operation_request = CancelMediaOperationRequestConverter.convert(
            media_operation_id=media_operation_id
            )

        return self._call_connection_client.cancel_participant_media_operation(
            call_connection_id=self.call_connection_id,
            participant_id=participant_id,
            cancel_media_operation_request=cancel_media_operation_request,
            **kwargs
        )

    @distributed_trace()
    def transfer_call(
            self,
            target_participant,  # type: CommunicationIdentifier
            user_to_user_information, # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> None

        if not target_participant:
            raise ValueError("target_participant can not be None")

        transfer_call_request = TransferCallRequestConverter.convert(
            target_participant=serialize_identifier(target_participant),
            user_to_user_information=user_to_user_information
            )

        return self._call_connection_client.transfer(
            call_connection_id=self.call_connection_id,
            transfer_call_request=transfer_call_request,
            **kwargs
        )
