# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from typing import TYPE_CHECKING, Any, Dict, Optional  # pylint: disable=unused-import
from azure.core.credentials import AzureKeyCredential
from azure.communication.callautomation import (
    CallAutomationClient,StartRecordingOptions, ServerCallLocator
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

        start = ServerCallLocator(locator_id = "locatorId")

        start = StartRecordingOptions(call_locator=start,recording_state_callback_uri='https://contoso.com') 

        try:
            callautomation_client.get_call_recording().start_recording(start_recording_options = start)
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
            callautomation_client.get_call_recording().stop_recording(self.recording_id)
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
            callautomation_client.get_call_recording().resume_recording(self.recording_id)
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
            callautomation_client.get_call_recording().pause_recording(self.recording_id)
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
            callautomation_client.get_call_recording().get_recording_properties(self.recording_id)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')