# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.core.credentials import AzureKeyCredential
from azure.communication.callautomation import (
    CallAutomationClient, ServerCallLocator
)
from unittest_helpers import mock_response
from unittest.mock import Mock

class TestCallRecordingClient(unittest.TestCase):
    recording_id = "123"

    def test_start_recording(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "recording_id": "1",
                "recording_state": "2"
            })

        callautomation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        call_locator = ServerCallLocator(server_call_id = "locatorId")

        try:
            callautomation_client.start_recording(call_locator=call_locator)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')


    def test_stop_recording(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=204)

        callautomation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        try:
            callautomation_client.stop_recording(recording_id=self.recording_id)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')

    def test_resume_recording(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=202)

        callautomation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        try:
            callautomation_client.resume_recording(recording_id=self.recording_id)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')

    def test_pause_recording(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=202)

        callautomation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        try:
            callautomation_client.pause_recording(recording_id=self.recording_id)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')


    def test_get_recording_properties(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "recording_id": "1",
                "recording_state": "2"
            })

        callautomation_client = CallAutomationClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        try:
            callautomation_client.get_recording_properties(recording_id=self.recording_id)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')