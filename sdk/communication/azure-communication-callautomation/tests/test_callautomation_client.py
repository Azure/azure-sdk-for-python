# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import unittest
import pytest

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
    callback_url = "https://contoso.com/event"
    communication_user_id = "8:acs:123"
    communication_user_source_id = "8:acs:456"
    incoming_call_context = "env2REDACTEDINCOMINGCALLCONTEXT"

    def test_create_call(self):
        def mock_send(request, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            body = json.loads(request.content)
            assert body["sourceDisplayName"] == "baz", "Parameter value not as expected"
            return mock_response(status_code=201, json_payload={
                "callConnectionId": self.call_connection_id,
                "serverCallId": self.server_callI_id,
                "callbackUri": self.callback_url,
                "targets": [
                    {"rawId": self.communication_user_id, "communicationUser": {"id": self.communication_user_id}}],
                "sourceIdentity": {"rawId": self.communication_user_source_id,
                                   "communicationUser": {"id": self.communication_user_source_id}}})

        # target endpoint for ACS User
        user = CommunicationUserIdentifier(self.communication_user_id)

        # make invitation
        call_invite = CallInvite(
            target=user,
            source_display_name="baz"
        )
        call_automation_client = CallAutomationClient(
            "https://endpoint",
            AzureKeyCredential("fakeCredential=="),
            transport=Mock(send=mock_send)
        )
        call_connection_properties = call_automation_client.create_call(call_invite, self.callback_url)
        self.assertEqual(self.call_connection_id, call_connection_properties.call_connection_id)
        self.assertEqual(self.server_callI_id, call_connection_properties.server_call_id)
        self.assertEqual(self.callback_url, call_connection_properties.callback_url)

        call_invite = CallInvite(
            target=user,
            source_display_name="WRONG"
        )
        call_connection_properties = call_automation_client.create_call(
            target_participant=call_invite,
            callback_url=self.callback_url,
            voip_headers={"foo": "bar"},
            source_display_name="baz"
        )
        self.assertEqual(self.call_connection_id, call_connection_properties.call_connection_id)
        self.assertEqual(self.server_callI_id, call_connection_properties.server_call_id)
        self.assertEqual(self.callback_url, call_connection_properties.callback_url)

        call_connection_properties = call_automation_client.create_call(
            target_participant=user,
            callback_url=self.callback_url,
            voip_headers={"foo": "bar"},
            source_display_name="baz"
        )
        self.assertEqual(self.call_connection_id, call_connection_properties.call_connection_id)
        self.assertEqual(self.server_callI_id, call_connection_properties.server_call_id)
        self.assertEqual(self.callback_url, call_connection_properties.callback_url)

    def test_create_group_call(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=201, json_payload={
                "callConnectionId": self.call_connection_id,
                "serverCallId": self.server_callI_id,
                "callbackUri": self.callback_url,
                "targets": [{"rawId": self.communication_user_id,
                             "communicationUser": {"id": self.communication_user_id}}],
                "sourceIdentity": {"rawId": self.communication_user_source_id,
                                   "communicationUser": {"id": self.communication_user_source_id}}})

        # target endpoint for ACS User
        user = CommunicationUserIdentifier(self.communication_user_id)

        call_automation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="),
                                                      transport=Mock(send=mock_send))
        call_connection_properties = call_automation_client.create_call([user], self.callback_url)
        self.assertEqual(self.call_connection_id, call_connection_properties.call_connection_id)
        self.assertEqual(self.server_callI_id, call_connection_properties.server_call_id)
        self.assertEqual(self.callback_url, call_connection_properties.callback_url)

    def test_create_group_call_back_compat(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=201, json_payload={
                "callConnectionId": self.call_connection_id,
                "serverCallId": self.server_callI_id,
                "callbackUri": self.callback_url,
                "targets": [{"rawId": self.communication_user_id,
                             "communicationUser": {"id": self.communication_user_id}}],
                "sourceIdentity": {"rawId": self.communication_user_source_id,
                                   "communicationUser": {"id": self.communication_user_source_id}}})

        # target endpoint for ACS User
        user = CommunicationUserIdentifier(self.communication_user_id)

        call_automation_client = CallAutomationClient(
            "https://endpoint",
            AzureKeyCredential("fakeCredential=="),
            transport=Mock(send=mock_send))
        call_connection_properties = call_automation_client.create_group_call([user], self.callback_url)
        self.assertEqual(self.call_connection_id, call_connection_properties.call_connection_id)
        self.assertEqual(self.server_callI_id, call_connection_properties.server_call_id)
        self.assertEqual(self.callback_url, call_connection_properties.callback_url)

    def test_answer_call(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=200, json_payload={
                "callConnectionId": self.call_connection_id,
                "serverCallId": self.server_callI_id,
                "callbackUri": self.callback_url,
                "targets": [{"rawId": self.communication_user_id,
                             "communicationUser": {"id": self.communication_user_id}}],
                "sourceIdentity": {"rawId": self.communication_user_source_id,
                                   "communicationUser": {"id": self.communication_user_source_id}}})

        # target endpoint for ACS User
        user = CommunicationUserIdentifier(self.communication_user_id)
        call_automation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="),
                                                      transport=Mock(send=mock_send))
        call_connection_properties = call_automation_client.answer_call(self.incoming_call_context, self.callback_url)
        self.assertEqual(self.call_connection_id, call_connection_properties.call_connection_id)
        self.assertEqual(self.server_callI_id, call_connection_properties.server_call_id)
        self.assertEqual(self.callback_url, call_connection_properties.callback_url)

    def test_redirect_call(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=204)

        # target endpoint for ACS User
        user = CommunicationUserIdentifier(self.communication_user_id)
        call_redirect_to = CallInvite(
            target=user,
            source_display_name="baz"
        )

        call_automation_client = CallAutomationClient(
            "https://endpoint",
            AzureKeyCredential("fakeCredential=="),
            transport=Mock(send=mock_send)
        )
        call_automation_client.redirect_call(self.incoming_call_context, call_redirect_to)
        call_automation_client.redirect_call(self.incoming_call_context, user, voip_headers={"foo": "bar"})
        with pytest.raises(ValueError) as e:
            call_automation_client.redirect_call(
                self.incoming_call_context,
                user,
                voip_headers={"foo": "bar"},
                source_display_name="baz"
            )
        assert "unexpected kwargs" in str(e.value)

    def test_reject_call(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=204)

        call_automation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="),
                                                      transport=Mock(send=mock_send))
        call_automation_client.reject_call(self.incoming_call_context)
