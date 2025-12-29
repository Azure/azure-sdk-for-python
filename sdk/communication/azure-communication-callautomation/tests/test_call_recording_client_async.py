# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import pytest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock
from unittest_helpers import mock_response

from azure.core.credentials import AzureKeyCredential
from azure.core.async_paging import AsyncItemPaged

from azure.communication.callautomation.aio import CallAutomationClient
from azure.communication.callautomation import (
    ServerCallLocator,
    GroupCallLocator,
    ChannelAffinity,
    CommunicationUserIdentifier,
)
from azure.communication.callautomation._utils import serialize_identifier


class TestCallRecordingClientAsync(IsolatedAsyncioTestCase):
    recording_id = "123"
    call_connection_id = "10000000-0000-0000-0000-000000000000"

    async def test_start_recording(self):
        async def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            kwargs.pop("call_locator", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=200, json_payload={"recording_id": "1", "recording_state": "2"})

        callautomation_client = CallAutomationClient(
            "https://endpoint",
            AzureKeyCredential("fakeCredential=="),
            transport=Mock(send=AsyncMock(side_effect=mock_send)),
        )
        call_locator = ServerCallLocator(server_call_id="locatorId")
        target_participant = CommunicationUserIdentifier("testId")
        channel_affinity = ChannelAffinity(target_participant=target_participant, channel=0)
        await callautomation_client.start_recording(call_locator=call_locator, channel_affinity=[channel_affinity])
        await callautomation_client.start_recording(group_call_id="locatorId", channel_affinity=[channel_affinity])
        await callautomation_client.start_recording(server_call_id="locatorId", channel_affinity=[channel_affinity])

        with pytest.raises(ValueError):
            call_locator = ServerCallLocator(server_call_id="locatorId")
            await callautomation_client.start_recording(call_locator=call_locator, group_call_id="foo")
        with pytest.raises(ValueError):
            call_locator = GroupCallLocator(group_call_id="locatorId")
            await callautomation_client.start_recording(call_locator=call_locator, server_call_id="foo")
        with pytest.raises(ValueError):
            await callautomation_client.start_recording(group_call_id="foo", server_call_id="bar")

    async def test_stop_recording(self):
        async def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=204)

        callautomation_client = CallAutomationClient(
            "https://endpoint",
            AzureKeyCredential("fakeCredential=="),
            transport=Mock(send=AsyncMock(side_effect=mock_send)),
        )
        await callautomation_client.stop_recording(recording_id=self.recording_id)

    async def test_resume_recording(self):
        async def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=202)

        callautomation_client = CallAutomationClient(
            "https://endpoint",
            AzureKeyCredential("fakeCredential=="),
            transport=Mock(send=AsyncMock(side_effect=mock_send)),
        )
        await callautomation_client.resume_recording(recording_id=self.recording_id)

    async def test_pause_recording(self):
        async def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=202)

        callautomation_client = CallAutomationClient(
            "https://endpoint",
            AzureKeyCredential("fakeCredential=="),
            transport=Mock(send=AsyncMock(side_effect=mock_send)),
        )
        await callautomation_client.pause_recording(recording_id=self.recording_id)

    async def test_get_recording_properties(self):
        async def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            if kwargs:
                raise ValueError(f"Received unexpected kwargs in transport: {kwargs}")
            return mock_response(status_code=200, json_payload={"recording_id": "1", "recording_state": "2"})

        callautomation_client = CallAutomationClient(
            "https://endpoint",
            AzureKeyCredential("fakeCredential=="),
            transport=Mock(send=AsyncMock(side_effect=mock_send)),
        )
        await callautomation_client.get_recording_properties(recording_id=self.recording_id)
