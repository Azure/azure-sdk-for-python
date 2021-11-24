# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import List
from .._generated.models import (
    CallMediaType,
    AudioRoutingMode,
    CallingEventSubscriptionType,
    JoinCallRequest,
    AnswerCallRequest,
    CallRejectReason,
    PlayAudioRequest,
    PlayAudioWithCallLocatorRequest,
    PlayAudioToParticipantRequest,
    PlayAudioToParticipantWithCallLocatorRequest,
    TransferCallRequest,
    CommunicationIdentifierModel,
    AddParticipantRequest,
    AddParticipantWithCallLocatorRequest,
    GetParticipantRequest,
    RemoveParticipantRequest,
    RemoveParticipantWithCallLocatorRequest,
    CancelMediaOperationWithCallLocatorRequest,
    CancelParticipantMediaOperationRequest,
    CancelParticipantMediaOperationWithCallLocatorRequest,
    PhoneNumberIdentifierModel,
    CallLocatorModel,
    RedirectCallRequest,
    AudioRoutingGroupRequest,
    MuteParticipantRequest,
    UnmuteParticipantRequest,
    HoldMeetingAudioRequest,
    ResumeMeetingAudioRequest,
    UpdateAudioRoutingGroupRequest,
    GetAllParticipantsWithCallLocatorRequest,
    GetParticipantWithCallLocatorRequest
    )

class JoinCallRequestConverter(object):
    @staticmethod
    def convert(
        call_locator, # type: CallLocatorModel
        source, # type: CommunicationIdentifierModel
        callback_uri=None,  # type: str
        requested_media_types=None,  # type: List[CallMediaType]
        requested_call_events=None,  # type: List[CallingEventSubscriptionType]
        subject=None,  # type: str
        ): # type: (...) -> JoinCallRequest

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not source:
            raise ValueError("source can not be None")

        return JoinCallRequest(
            call_locator=call_locator,
            source=source,
            callback_uri=callback_uri,
            requested_media_types=requested_media_types,
            requested_call_events=requested_call_events,
            subject=subject
            )

class AnswerCallRequestConverter(object):
    @staticmethod
    def convert(
        incoming_call_context,  # type: str
        callback_uri=None,  # type: str
        requested_media_types=None,  # type: List[CallMediaType]
        requested_call_events=None,  # type: List[CallingEventSubscriptionType]
        ): # type: (...) -> AnswerCallRequest

        if not incoming_call_context:
            raise ValueError("incoming_call_context can not be None")

        return AnswerCallRequest(
            incoming_call_context=incoming_call_context,
            callback_uri=callback_uri,
            requested_media_types=requested_media_types,
            requested_call_events=requested_call_events
            )

class RejectCallRequestConverter(object):
    @staticmethod
    def convert(
        incoming_call_context,  # type: str
        call_reject_reason=None  # type: CallRejectReason
        ): # type: (...) -> AnswerCallRequest

        if not incoming_call_context:
            raise ValueError("incoming_call_context can not be None")

        return AnswerCallRequest(
            incoming_call_context=incoming_call_context,
            call_reject_reason=call_reject_reason
            )

class RedirectCallRequestConverter(object):
    @staticmethod
    def convert(
        incoming_call_context,  # type: str
        target_identity  # type: CommunicationIdentifierModel
        ): # type: (...) -> RedirectCallRequest

        if not incoming_call_context:
            raise ValueError("incoming_call_context can not be None")
        if not target_identity:
            raise ValueError("target_identity can not be None")

        return RedirectCallRequest(
            incoming_call_context=incoming_call_context,
            target=target_identity
            )

class PlayAudioRequestConverter(object):
    @staticmethod
    def convert(
        audio_url, # type: str
        loop,  # type: bool
        operation_context,  # type: str
        audio_file_id  # type: str
        ): # type: (...) -> PlayAudioRequest

        if not audio_url:
            raise ValueError("audio_url can not be None")

        return PlayAudioRequest(
            audio_file_uri=audio_url,
            loop=loop,
            operation_context=operation_context,
            audio_file_id=audio_file_id
            )

class PlayAudioWithCallLocatorRequestConverter(object):
    @staticmethod
    def convert(
        call_locator, # type: CallLocatorModel
        audio_url, # type: str
        loop,  # type: bool
        operation_context,  # type: str
        audio_file_id,  # type: str
        callback_uri  # type: str
        ): # type: (...) -> PlayAudioWithCallLocatorRequest

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not audio_url:
            raise ValueError("audio_url can not be None")

        return PlayAudioWithCallLocatorRequest(
            call_locator=call_locator,
            audio_file_uri=audio_url,
            loop=loop,
            operation_context=operation_context,
            audio_file_id=audio_file_id,
            callback_uri=callback_uri
            )

class PlayAudioToParticipantRequestConverter(object):
    @staticmethod
    def convert(
        identifier, # type: CommunicationIdentifierModel
        audio_url, # type: str
        loop,  # type: bool
        operation_context,  # type: str
        audio_file_id  # type: str
        ): # type: (...) -> PlayAudioToParticipantRequest

        if not audio_url:
            raise ValueError("audio_url can not be None")

        return PlayAudioToParticipantRequest(
            identifier=identifier,
            audio_file_uri=audio_url,
            loop=loop,
            operation_context=operation_context,
            audio_file_id=audio_file_id
            )

class PlayAudioToParticipantWithCallLocatorRequestConverter(object):
    @staticmethod
    def convert(
        call_locator, # type: CallLocatorModel
        identifier, # type: CommunicationIdentifierModel
        audio_url, # type: str
        loop,  # type: bool
        operation_context,  # type: str
        audio_file_id,  # type: str
        callback_uri  # type: str
        ): # type: (...) -> PlayAudioToParticipantWithCallLocatorRequest

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not audio_url:
            raise ValueError("audio_url can not be None")

        return PlayAudioToParticipantWithCallLocatorRequest(
            call_locator=call_locator,
            identifier=identifier,
            audio_file_uri=audio_url,
            loop=loop,
            operation_context=operation_context,
            audio_file_id=audio_file_id,
            callback_uri=callback_uri
            )

class AddParticipantRequestConverter(object):
    @staticmethod
    def convert(
        participant, # type: CommunicationIdentifierModel
        alternate_caller_id=None, # type: PhoneNumberIdentifierModel
        operation_context=None # type: str
        ): # type: (...) -> AddParticipantRequest

        if not participant:
            raise ValueError("participant can not be None")

        return AddParticipantRequest(
            alternate_caller_id=alternate_caller_id,
            participant=participant,
            operation_context=operation_context
            )

class AddParticipantWithCallLocatorRequestConverter(object):
    @staticmethod
    def convert(
        call_locator, # type: CallLocatorModel
        participant, # type: CommunicationIdentifierModel
        alternate_caller_id=None, # type: PhoneNumberIdentifierModel
        operation_context=None, # type: str
        callback_uri=None # type: str
        ): # type: (...) -> AddParticipantRequest

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not participant:
            raise ValueError("participant can not be None")

        return AddParticipantWithCallLocatorRequest(
            call_locator=call_locator,
            alternate_caller_id=alternate_caller_id,
            participant=participant,
            operation_context=operation_context,
            callback_uri=callback_uri
            )

class GetParticipantRequestConverter(object):
    @staticmethod
    def convert(
        identifier # type: CommunicationIdentifierModel
        ): # type: (...) -> GetParticipantRequest

        if not identifier:
            raise ValueError("identifier can not be None")

        return GetParticipantRequest(
            identifier=identifier
            )

class GetAllParticipantsWithCallLocatorRequestConverter(object):
    @staticmethod
    def convert(
        call_locator # type: CallLocatorModel
        ): # type: (...) -> GetAllParticipantsWithCallLocatorRequest

        if not call_locator:
            raise ValueError("call_locator can not be None")

        return GetAllParticipantsWithCallLocatorRequest(
            call_locator=call_locator
            )

class GetParticipantWithCallLocatorRequestConverter(object):
    @staticmethod
    def convert(
        call_locator, # type: CallLocatorModel
        identifier # type: CommunicationIdentifierModel
        ): # type: (...) -> GetParticipantWithCallLocatorRequest

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not identifier:
            raise ValueError("identifier can not be None")

        return GetParticipantWithCallLocatorRequest(
            call_locator=call_locator,
            identifier=identifier
            )

class RemoveParticipantRequestConverter(object):
    @staticmethod
    def convert(
        identifier # type: CommunicationIdentifierModel
        ): # type: (...) -> RemoveParticipantRequest

        if not identifier:
            raise ValueError("identifier can not be None")

        return RemoveParticipantRequest(
            identifier=identifier
            )

class RemoveParticipantWithCallLocatorRequestConverter(object):
    @staticmethod
    def convert(
        call_locator, # type: CallLocatorModel
        identifier # type: CommunicationIdentifierModel
        ): # type: (...) -> RemoveParticipantWithCallLocatorRequest

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not identifier:
            raise ValueError("identifier can not be None")

        return RemoveParticipantWithCallLocatorRequest(
            call_locator=call_locator,
            identifier=identifier
            )

class CancelMediaOperationWithCallLocatorRequestConverter(object):
    @staticmethod
    def convert(
        call_locator, # type: CallLocatorModel
        media_operation_id # type: str
        ): # type: (...) -> CancelMediaOperationWithCallLocatorRequest

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        return CancelMediaOperationWithCallLocatorRequest(
            call_locator=call_locator,
            media_operation_id=media_operation_id
        )

class CancelParticipantMediaOperationRequestConverter(object):
    @staticmethod
    def convert(
        identifier, # type: CommunicationIdentifierModel
        media_operation_id # type: str
        ): # type: (...) -> CancelParticipantMediaOperationRequest

        if not identifier:
            raise ValueError("identifier can not be None")
        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        return CancelParticipantMediaOperationRequest(
            identifier=identifier,
            media_operation_id=media_operation_id
        )

class CancelParticipantMediaOperationWithCallLocatorRequestConverter(object):
    @staticmethod
    def convert(
        call_locator, # type: CallLocatorModel
        identifier, # type: CommunicationIdentifierModel
        media_operation_id # type: str
        ): # type: (...) -> CancelParticipantMediaOperationWithCallLocatorRequest

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not identifier:
            raise ValueError("identifier can not be None")
        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        return CancelParticipantMediaOperationWithCallLocatorRequest(
            call_locator=call_locator,
            identifier=identifier,
            media_operation_id=media_operation_id
        )

class TransferCallRequestConverter(object):
    @staticmethod
    def convert(
        target_participant, # type: CommunicationIdentifierModel
        target_call_connection_id, # type: str
        alternate_caller_id=None, # type: PhoneNumberIdentifierModel
        user_to_user_information=None, # type: str
        operation_context=None # type: str
        ): # type: (...) -> TransferCallRequest

        if not target_participant:
            raise ValueError("target_participant can not be None")

        return TransferCallRequest(
            target_participant=target_participant,
            target_call_connection_id=target_call_connection_id,
            alternate_caller_id=alternate_caller_id,
            user_to_user_information=user_to_user_information,
            operation_context=operation_context
        )

class MuteParticipantRequestConverter(object):
    @staticmethod
    def convert(
        identifier, # type: CommunicationIdentifierModel
        ): # type: (...) -> MuteParticipantRequest

        if not identifier:
            raise ValueError("identifier can not be None")

        return MuteParticipantRequest(
            identifier=identifier
        )

class UnmuteParticipantRequestConverter(object):
    @staticmethod
    def convert(
        identifier, # type: CommunicationIdentifierModel
        ): # type: (...) -> UnmuteParticipantRequest

        if not identifier:
            raise ValueError("identifier can not be None")

        return UnmuteParticipantRequest(
            identifier=identifier
        )

class HoldMeetingAudioRequestConverter(object):
    @staticmethod
    def convert(
        identifier, # type: CommunicationIdentifierModel
        ): # type: (...) -> HoldMeetingAudioRequest

        if not identifier:
            raise ValueError("identifier can not be None")

        return HoldMeetingAudioRequest(
            identifier=identifier
        )

class ResumeMeetingAudioRequestConverter(object):
    @staticmethod
    def convert(
        identifier, # type: CommunicationIdentifierModel
        ): # type: (...) -> ResumeMeetingAudioRequest

        if not identifier:
            raise ValueError("identifier can not be None")

        return ResumeMeetingAudioRequest(
            identifier=identifier
        )

class AudioRoutingGroupRequestConverter(object):
    @staticmethod
    def convert(
        audio_routing_mode, # type: AudioRoutingMode
        target_identities, # type: List[CommunicationIdentifierModel]
        ): # type: (...) -> CommunicationIdentifierModel

        if not audio_routing_mode:
            raise ValueError("audio_routing_mode can not be None")
        if not target_identities:
            raise ValueError("target_identities can not be None")

        return AudioRoutingGroupRequest(
            audio_routing_mode=audio_routing_mode,
            targets=target_identities
        )

class UpdateAudioRoutingGroupRequestConverter(object):
    @staticmethod
    def convert(
        target_identities, # type: CommunicationIdentifierModel
        ): # type: (...) -> UpdateAudioRoutingGroupRequest

        if not target_identities:
            raise ValueError("target_identities can not be None")

        return UpdateAudioRoutingGroupRequest(
            targets=target_identities
        )
