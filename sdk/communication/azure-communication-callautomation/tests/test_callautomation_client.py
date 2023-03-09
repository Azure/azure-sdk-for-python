# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.core.credentials import AzureKeyCredential
from azure.communication.callautomation import (
    CallAutomationClient,
    CallInvite,
    CommunicationUserIdentifier
)
from unittest_helpers import mock_response

from unittest.mock import Mock

class TestCallAutomationClient(unittest.TestCase):
    call_connection_id = "10000000-0000-0000-0000-000000000000"
    server_callI_id = "12345"
    callback_uri = "https://contoso.com/event"
    communication_user_id = "8:acs:123"
    communication_user_source_id = "8:acs:456"

    def test_create_call(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=201, json_payload={
                "callConnectionId": self.call_connection_id,
                "serverCallId": self.server_callI_id,
                "callbackUri": self.callback_uri,
                "targets": [{"rawId": self.communication_user_id, "communicationUser": { "id": self.communication_user_id }}],
                "sourceIdentity": {"rawId": self.communication_user_source_id,"communicationUser": {"id": self.communication_user_source_id}}})

        # target endpoint for ACS User
        user = CommunicationUserIdentifier(self.communication_user_id)

        # make invitation
        call_invite = CallInvite(target=user)

        callautomation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        response = None
        try:
            response = callautomation_client.create_call(call_invite, self.callback_uri)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(self.call_connection_id, response.call_connection_properties.call_connection_id)
        self.assertEqual(self.server_callI_id, response.call_connection_properties.server_call_id)
        self.assertEqual(self.callback_uri, response.call_connection_properties.callback_uri)