# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Any, Optional  # pylint: disable=unused-import

if TYPE_CHECKING:
    from ._generated.operations import CallConnectionOperations, CallMediaOperations

from ._call_media import CallMediaClient

from ._models import (CallConnectionProperties,
                      CallParticipant, GetParticipantsResponse, CallInvite, AddParticipantResponse)

from ._generated.models import (
    TransferCallResponse, TransferToParticipantRequest, CustomContext, AddParticipantRequest, RemoveParticipantResponse, RemoveParticipantRequest)

from ._communication_identifier_serializer import *


class CallConnection(object):
    def __init__(
        self,
        call_connection_id,  # type: str
        call_connection_client,  # type: CallConnectionOperations
        call_media_operations,  # type: CallMediaOperations
    ):  # type: (...) -> None

        self.call_connection_id = call_connection_id
        self._call_connection_client = call_connection_client
        self._call_media_operations = call_media_operations

    def get_call_media(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> CallMediaClient

        return CallMediaClient(
            self.call_connection_id,
            self._call_media_operations,
            **kwargs
        )

    def get_call_properties(self, **kwargs) -> CallConnectionProperties:
        """Get call connection.

        Get call connection.

        :return: CallConnectionProperties
        :type: CallConnectionProperties
        """
        return CallConnectionProperties._from_generated(self._call_connection_client.get_call(call_connection_id=self.call_connection_id, **kwargs))

    def hang_up(self, is_for_everyone: bool, **kwargs) -> None:
        """Hangup the call.

        Hangup the call.

        :param is_for_everyone: Determine if the call is handed up for all participants.
        :type is_for_everyone: bool
        :param repeatability_request_id: If specified, the client directs that the request is
         repeatable; that is, that the client can make the request multiple times with the same
         Repeatability-Request-Id and get back an appropriate response without the server executing the
         request multiple times. The value of the Repeatability-Request-Id is an opaque string
         representing a client-generated unique identifier for the request. It is a version 4 (random)
         UUID. Default value is None.
        :type repeatability_request_id: str
        :param repeatability_first_sent: If Repeatability-Request-ID header is specified, then
         Repeatability-First-Sent header must also be specified. The value should be the date and time
         at which the request was first created, expressed using the IMF-fixdate form of HTTP-date.
         Example: Sun, 06 Nov 1994 08:49:37 GMT. Default value is None.
        :type repeatability_first_sent: str
        :return: None
        :type: None
        """

        repeatability_request_id = kwargs.pop("repeatability_request_id", None)
        repeatability_first_sent = kwargs.pop("repeatability_first_sent", None)

        if is_for_everyone:
            self._call_connection_client.terminate_call(
                self.call_connection_id, repeatability_first_sent=repeatability_first_sent,
                repeatability_request_id=repeatability_request_id,
                **kwargs)
        else:
            self._call_connection_client.hangup_call(
                self.call_connection_id, **kwargs)

    def get_participant(self, participantMri: str, **kwargs) -> CallParticipant:
        """Get a participant from a call.

        Get a participant from a call.

        :param call_connection_id: The call connection Id. Required.
        :type call_connection_id: str
        :param participant_raw_id: Raw id of the participant to retrieve. Required.
        :type participant_raw_id: str
        :return: CallParticipant
        """
        return CallParticipant._from_generated(self._call_connection_client.get_participant(self.call_connection_id, participantMri, **kwargs))

    def list_participants(self, **kwargs) -> GetParticipantsResponse:
        """Get participants from a call.

        Get participants from a call.

        :param call_connection_id: The call connection Id. Required.
        :type call_connection_id: str
        :param participant_raw_id: Raw id of the participant to retrieve. Required.
        :type participant_raw_id: str
        :return: GetParticipantsResponse
        """
        return GetParticipantsResponse._from_generated(self._call_connection_client.get_participants(self.call_connection_id, **kwargs))

    def transfer_call_to_participant(self, target: CallInvite, **kwargs: Any) -> TransferCallResponse:
        """
        Transfer the call to a participant.

        :param target: The transfer target. Required.
        :type transfer_to_participant_request: CallInvite
        :keyword operation_context: The operation context provided by client.
        :type operation_context: str
        :keyword repeatability_request_id: If specified, the client directs that the request is
         repeatable; that is, that the client can make the request multiple times with the same
         Repeatability-Request-Id and get back an appropriate response without the server executing the
         request multiple times. The value of the Repeatability-Request-Id is an opaque string
         representing a client-generated unique identifier for the request. It is a version 4 (random)
         UUID. Default value is None.
        :type repeatability_request_id: str
        :keyword repeatability_first_sent: If Repeatability-Request-ID header is specified, then
         Repeatability-First-Sent header must also be specified. The value should be the date and time
         at which the request was first created, expressed using the IMF-fixdate form of HTTP-date.
         Example: Sun, 06 Nov 1994 08:49:37 GMT. Default value is None.
        :type repeatability_first_sent: str
        :return: TransferCallResponse
        """
        user_custom_context = CustomContext(
            voip_headers=target.voipHeaders, sip_headers=target.sipHeaders)
        request = TransferToParticipantRequest(target_participant=serialize_identifier(target.target),
                                               transferee_caller_id=serialize_identifier(
                                                   target.sourceCallIdNumber) if target.sourceCallIdNumber else None,
                                               custom_context=user_custom_context, operation_context=kwargs.pop("operation_context", None))
        repeatability_request_id = kwargs.pop("repeatability_request_id", None)
        repeatability_first_sent = kwargs.pop("repeatability_first_sent", None)

        return self._call_connection_client.transfer_to_participant(self.call_connection_id, request, repeatability_first_sent=repeatability_first_sent,
                                                                    repeatability_request_id=repeatability_request_id,
                                                                    **kwargs)

    def add_participant(self, participant: CallInvite, **kwargs: Any) -> AddParticipantResponse:
        """
        Add participants to the call.

        :param participant: The participant being added. Required.
        :type participant: CallInvite
        :keyword invitation_timeout_in_seconds: Gets or sets the timeout to wait for the invited
         participant to pickup.
         The maximum value of this is 180 seconds.
        :type invitation_timeout_in_seconds: int
        :keyword operation_context: Used by customers when calling mid-call actions to correlate the
         request to the response event.
        :type operation_context: str
        :keyword repeatability_request_id: If specified, the client directs that the request is
         repeatable; that is, that the client can make the request multiple times with the same
         Repeatability-Request-Id and get back an appropriate response without the server executing the
         request multiple times. The value of the Repeatability-Request-Id is an opaque string
         representing a client-generated unique identifier for the request. It is a version 4 (random)
         UUID. Default value is None.
        :type repeatability_request_id: str
        :keyword repeatability_first_sent: If Repeatability-Request-ID header is specified, then
         Repeatability-First-Sent header must also be specified. The value should be the date and time
         at which the request was first created, expressed using the IMF-fixdate form of HTTP-date.
         Example: Sun, 06 Nov 1994 08:49:37 GMT. Default value is None.
        :type repeatability_first_sent: str
        :return: AddParticipantResponse
        """
        user_custom_context = CustomContext(
            voip_headers=participant.voipHeaders, sip_headers=participant.sipHeaders)
        add_participant_request = AddParticipantRequest(participant_to_add=serialize_identifier(participant.target),
                                                        source_caller_id_number=serialize_identifier(
                                                            participant.sourceCallIdNumber) if participant.sourceCallIdNumber else None,
                                                        source_display_name=participant.sourceDisplayName,
                                                        custom_context=user_custom_context,
                                                        invitation_timeout_in_seconds=kwargs.pop(
                                                            "invitation_timeout_in_seconds", None),
                                                        operation_context=kwargs.pop("operation_context", None))
        repeatability_request_id = kwargs.pop("repeatability_request_id", None)
        repeatability_first_sent = kwargs.pop("repeatability_first_sent", None)

        return AddParticipantResponse._from_generated(self._call_connection_client.add_participant(self.call_connection_id,
                                                                                                   add_participant_request,
                                                                                                   repeatability_first_sent=repeatability_first_sent,
                                                                                                   repeatability_request_id=repeatability_request_id))

    def remove_participant(self, participant: CommunicationIdentifier, **kwargs: Any) -> RemoveParticipantResponse:
        """
        Add participants to the call.

        :param participant: The participant being removed. Required.
        :type participant: CallInvite
        :keyword operation_context: Used by customers when calling mid-call actions to correlate the
         request to the response event.
        :type operation_context: str
        :keyword repeatability_request_id: If specified, the client directs that the request is
         repeatable; that is, that the client can make the request multiple times with the same
         Repeatability-Request-Id and get back an appropriate response without the server executing the
         request multiple times. The value of the Repeatability-Request-Id is an opaque string
         representing a client-generated unique identifier for the request. It is a version 4 (random)
         UUID. Default value is None.
        :type repeatability_request_id: str
        :keyword repeatability_first_sent: If Repeatability-Request-ID header is specified, then
         Repeatability-First-Sent header must also be specified. The value should be the date and time
         at which the request was first created, expressed using the IMF-fixdate form of HTTP-date.
         Example: Sun, 06 Nov 1994 08:49:37 GMT. Default value is None.
        :type repeatability_first_sent: str
        :return: AddParticipantResponse
        """

        remove_participant_request = RemoveParticipantRequest(participant_to_remove=serialize_identifier(participant),
                                                              operation_context=kwargs.pop("operation_context", None))
        repeatability_request_id = kwargs.pop("repeatability_request_id", None)
        repeatability_first_sent = kwargs.pop("repeatability_first_sent", None)

        return self._call_connection_client.add_participant(self.call_connection_id,
                                                            remove_participant_request,
                                                            repeatability_first_sent=repeatability_first_sent,
                                                            repeatability_request_id=repeatability_request_id)
