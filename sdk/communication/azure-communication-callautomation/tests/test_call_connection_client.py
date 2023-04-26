# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from typing import TYPE_CHECKING, Any, Dict, Optional  # pylint: disable=unused-import
from azure.core.credentials import AzureKeyCredential
from azure.communication.callautomation import (
    CallAutomationClient,
    CallInvite,
    CommunicationUserIdentifier
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

        call_automation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="),
                                                      transport=Mock(send=mock_send))
        call_connection = call_automation_client.get_call_connection(self.call_connection_id)
        response = None
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

        call_automation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="),
                                                      transport=Mock(send=mock_send))
        call_connection = call_automation_client.get_call_connection(self.call_connection_id)
        response = None
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

        call_automation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="),
                                                      transport=Mock(send=mock_send))
        call_connection = call_automation_client.get_call_connection(self.call_connection_id)
        response = None
        user = CommunicationUserIdentifier(self.communication_user_id)
        call_invite = CallInvite(target=user)

        try:
            response = call_connection.transfer_call_to_participant(call_invite)
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

        call_automation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="),
                                                      transport=Mock(send=mock_send))
        call_connection = call_automation_client.get_call_connection(self.call_connection_id)
        response = None

        try:
            response = call_connection.list_participants()
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.communication_user_id, response.values[0].identifier.raw_id)

    def test_get_participants(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload=self.call_participant)

        call_automation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="),
                                                      transport=Mock(send=mock_send))
        call_connection = call_automation_client.get_call_connection(self.call_connection_id)
        response = None

        try:
            response = call_connection.get_participant(self.communication_user_id)
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

        call_automation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="),
                                                      transport=Mock(send=mock_send))
        call_connection = call_automation_client.get_call_connection(self.call_connection_id)
        user = CommunicationUserIdentifier(self.communication_user_id)
        call_invite = CallInvite(target=user)
        response = None

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

        call_automation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="),
                                                      transport=Mock(send=mock_send))
        call_connection = call_automation_client.get_call_connection(self.call_connection_id)
        user = CommunicationUserIdentifier(self.communication_user_id)
        response = None

        try:
            response = call_connection.remove_participant(user)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.operation_context, response.operation_context)