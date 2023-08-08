# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import unittest

from azure.core.credentials import AzureKeyCredential
from azure.communication.callautomation import (
    CallInvite,
    CommunicationUserIdentifier,
    CallConnectionClient,
    CallParticipant,
    TransferCallResult
)
from azure.core.paging import ItemPaged

from unittest_helpers import mock_response

from unittest.mock import Mock


class TestCallConnectionClient(unittest.TestCase):
    call_connection_id = "10000000-0000-0000-0000-000000000000"
    communication_user_id = "8:acs:123"
    operation_context = "operationContext"
    call_participant = {
        "identifier": {"rawId": communication_user_id, "communicationUser": {"id": communication_user_id}},
        "isMuted": False
    }

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
        assert isinstance(response, ItemPaged)

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
        call_invite = CallInvite(
            target=user,
            source_display_name="baz"
        )
        response = call_connection.add_participant(call_invite)
        self.assertEqual(self.communication_user_id, response.participant.identifier.raw_id)
        self.assertEqual(self.operation_context, response.operation_context)

        call_invite = CallInvite(
            target=user,
            source_display_name="WRONG"
        )
        response = call_connection.add_participant(
            call_invite,
            source_display_name="baz"
        )
        self.assertEqual(self.communication_user_id, response.participant.identifier.raw_id)
        self.assertEqual(self.operation_context, response.operation_context)

        response = call_connection.add_participant(
            user,
            source_display_name="baz"
        )
        self.assertEqual(self.communication_user_id, response.participant.identifier.raw_id)
        self.assertEqual(self.operation_context, response.operation_context)

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

    def test_mute_participant(self):
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
        response = call_connection.mute_participant(user)
        self.assertEqual(self.operation_context, response.operation_context)
