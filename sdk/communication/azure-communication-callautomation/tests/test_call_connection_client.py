# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import unittest

from azure.core.credentials import AzureKeyCredential
from azure.communication.callautomation import (
    CommunicationUserIdentifier,
    CallConnectionClient,
    CallParticipant,
    TransferCallResult
)
from azure.communication.callautomation._generated.models import (
    AddParticipantRequest,
)
from unittest_helpers import mock_response

from unittest.mock import Mock
from azure.communication.callautomation._utils import serialize_identifier

class TestCallConnectionClient(unittest.TestCase):
    call_connection_id = "10000000-0000-0000-0000-000000000000"
    communication_user_id = "8:acs:123"
    transferee_user_id = "8:acs:456"
    operation_context = "operationContext"
    call_participant = {
        "identifier": {"rawId": communication_user_id, "communicationUser": {"id": communication_user_id}},
        "isMuted": False
    }
    invitation_id = "invitationId"

    def test_hangup(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=204)

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))
        call_connection.hang_up(False)

    def test_terminate(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=204)

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))
        call_connection.hang_up(True)

    def test_transfer_call_to_participant(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=202, json_payload={
                "operationContext": self.operation_context})

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))
        user = CommunicationUserIdentifier(self.communication_user_id)

        response = call_connection.transfer_call_to_participant(user)
        assert isinstance(response, TransferCallResult)
        self.assertEqual(self.operation_context, response.operation_context)

    def test_transfer_call_to_participant_with_transferee(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=202, json_payload={
                "operationContext": self.operation_context})

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))
        user = CommunicationUserIdentifier(self.communication_user_id)
        transferee = CommunicationUserIdentifier(self.transferee_user_id)
        try:
            response = call_connection.transfer_call_to_participant(user, transferee=transferee)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.operation_context, response.operation_context)

    def test_list_participants(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=200, json_payload={
                "values": [self.call_participant],
                "nextLink": ""})

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))

        response = call_connection.list_participants()
        participants = [p for p in response]
        for p in participants:
            assert isinstance(p, CallParticipant)

    def test_get_participants(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=200, json_payload=self.call_participant)

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))
        response = call_connection.get_participant(CommunicationUserIdentifier(self.call_connection_id))
        self.assertEqual(self.communication_user_id, response.identifier.raw_id)

    def test_add_participant(self):
        def mock_send(request, **kwargs):
            kwargs.pop("stream", None)
            body = json.loads(request.content)
            assert body["sourceDisplayName"] == "baz", "Parameter value not as expected"
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=202, json_payload={
                "participant": self.call_participant,
                "operationContext": self.operation_context})

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))
        user = CommunicationUserIdentifier(self.communication_user_id)

        response = call_connection.add_participant(
            target_participant=user,
            voip_headers={"foo": "bar"},
            source_display_name="baz",
            invitation_timeout=10,
            operation_context="operationContext")
        self.assertEqual(self.communication_user_id, response.participant.identifier.raw_id)
        self.assertEqual(self.operation_context, response.operation_context)

        response = call_connection.add_participant(
            user,
            voip_headers={"foo": "bar"},
            source_display_name="baz"
        )
        self.assertEqual(self.communication_user_id, response.participant.identifier.raw_id)
        self.assertEqual(self.operation_context, response.operation_context)

        # checking input and request match here
        mock_add = Mock()
        call_connection.add_participant = mock_add

        expected_add_request = AddParticipantRequest(
            participant_to_add=serialize_identifier(user),
            source_caller_id_number="123",
            source_display_name="baz",
            invitation_timeout_in_seconds=10,
            operation_context="operationContext")

        call_connection.add_participant(
            target_participant=user,
            source_caller_id_number="123",
            source_display_name="baz",
            invitation_timeout=10,
            operation_context="operationContext")

        actual_request = dict(mock_add.call_args[1].items())
        self.assertEqual(expected_add_request.source_caller_id_number, actual_request["source_caller_id_number"])
        self.assertEqual(expected_add_request.source_display_name, actual_request["source_display_name"])
        self.assertEqual(expected_add_request.operation_context, actual_request["operation_context"])
        self.assertEqual(expected_add_request.invitation_timeout_in_seconds, actual_request["invitation_timeout"])

    def test_remove_participant(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=202, json_payload={
                "operationContext": self.operation_context})

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))
        user = CommunicationUserIdentifier(self.communication_user_id)
        response = call_connection.remove_participant(user)
        self.assertEqual(self.operation_context, response.operation_context)

    def test_mute_participants(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=202, json_payload={
                "operationContext": self.operation_context})

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))

        user = CommunicationUserIdentifier(self.communication_user_id)
        response = call_connection.mute_participants(user)
        self.assertEqual(self.operation_context, response.operation_context)

    def test_cancel_add_participant(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=202, json_payload={
                "invitationId": self.invitation_id,
                "operationContext": self.operation_context})

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))
        response = call_connection.cancel_add_participant(self.invitation_id)
        self.assertEqual(self.invitation_id, response.invitation_id)
        self.assertEqual(self.operation_context, response.operation_context)
