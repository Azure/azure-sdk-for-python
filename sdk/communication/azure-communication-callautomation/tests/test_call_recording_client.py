# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest

from azure.core.credentials import AzureKeyCredential
from azure.communication.callautomation import (
    CallAutomationClient,
    ServerCallLocator,
    GroupCallLocator,
    ChannelAffinity,
    CommunicationUserIdentifier,
)
from unittest_helpers import mock_response
from unittest.mock import Mock


class TestCallRecordingClient(unittest.TestCase):
    recording_id = "123"

    def test_start_recording(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=200, json_payload={"recording_id": "1", "recording_state": "2"})

        callautomation_client = CallAutomationClient(
            "https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send)
        )
        call_locator = ServerCallLocator(server_call_id="locatorId")
        target_participant = CommunicationUserIdentifier("testId")
        channel_affinity = ChannelAffinity(target_participant=target_participant, channel=0)
        callautomation_client.start_recording(call_locator=call_locator, channel_affinity=[channel_affinity])
        callautomation_client.start_recording(call_locator, channel_affinity=[channel_affinity])
        callautomation_client.start_recording(group_call_id="locatorId", channel_affinity=[channel_affinity])
        callautomation_client.start_recording(server_call_id="locatorId", channel_affinity=[channel_affinity])

        with pytest.raises(ValueError):
            call_locator = ServerCallLocator(server_call_id="locatorId")
            callautomation_client.start_recording(call_locator, group_call_id="foo")
        with pytest.raises(ValueError):
            call_locator = GroupCallLocator(group_call_id="locatorId")
            callautomation_client.start_recording(call_locator=call_locator, server_call_id="foo")
        with pytest.raises(ValueError):
            callautomation_client.start_recording(group_call_id="foo", server_call_id="bar")

    def test_stop_recording(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=204)

        callautomation_client = CallAutomationClient(
            "https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send)
        )
        callautomation_client.stop_recording(recording_id=self.recording_id)

    def test_resume_recording(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=202)

        callautomation_client = CallAutomationClient(
            "https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send)
        )
        callautomation_client.resume_recording(recording_id=self.recording_id)

    def test_pause_recording(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=202)

        callautomation_client = CallAutomationClient(
            "https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send)
        )
        callautomation_client.pause_recording(recording_id=self.recording_id)

    def test_get_recording_properties(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=200, json_payload={"recording_id": "1", "recording_state": "2"})

        callautomation_client = CallAutomationClient(
            "https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send)
        )
        callautomation_client.get_recording_properties(recording_id=self.recording_id)
