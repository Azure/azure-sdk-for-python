# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.core.credentials import AzureKeyCredential
from azure.communication.callautomation import (
    CallInvite,
    CommunicationUserIdentifier,
    CallConnectionClient
)

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
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=204)

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))

        try:
            call_connection.hang_up(False)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')

    def test_terminate(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=204)

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))
        try:
            call_connection.hang_up(True)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')

    def test_transfer_call_to_participant(self):
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
        try:
            response = call_connection.transfer_call_to_participant(user)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.operation_context, response.operation_context)

    def test_list_participants(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "values": [self.call_participant],
                "nextLink": ""})

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))
        try:
            response = call_connection.list_participants()
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')

    def test_get_participants(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload=self.call_participant)

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))
        try:
            response = call_connection.get_participant(CommunicationUserIdentifier(self.call_connection_id))
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.communication_user_id, response.identifier.raw_id)

    def test_add_participant(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=202, json_payload={
                "participant": self.call_participant,
                "operationContext": self.operation_context})

        call_connection = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
            transport=Mock(send=mock_send))
        user = CommunicationUserIdentifier(self.communication_user_id)
        call_invite = CallInvite(target=user)
        try:
            response = call_connection.add_participant(call_invite)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.communication_user_id, response.participant.identifier.raw_id)
        self.assertEqual(self.operation_context, response.operation_context)

    def test_remove_participant(self):
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
        try:
            response = call_connection.remove_participant(user)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.operation_context, response.operation_context)