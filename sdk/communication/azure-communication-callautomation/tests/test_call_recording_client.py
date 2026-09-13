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
from unittest.mock import Mock, MagicMock

from azure.communication.callautomation._content_downloader import ContentDownloader


class TestCallRecordingClient(unittest.TestCase):
    recording_id = "123"
    call_connection_id = "10000000-0000-0000-0000-000000000000"

    def test_start_recording(self):
        def mock_send(_, **kwargs):
            kwargs.pop("stream", None)
            kwargs.pop("call_locator", None)
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
        callautomation_client.start_recording(
            call_connection_id=self.call_connection_id, channel_affinity=[channel_affinity]
        )

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


def _make_sync_downloader() -> ContentDownloader:
    mock_config = MagicMock()
    mock_config.endpoint = "https://endpoint"
    mock_recording_client = MagicMock()
    mock_recording_client._config = mock_config  # pylint: disable=protected-access
    return ContentDownloader(mock_recording_client)


class TestSyncContentDownloaderValidation(unittest.TestCase):
    def test_download_streaming_rejects_invalid_recording_url(self):
        with pytest.raises(ValueError, match="HTTPS"):
            _make_sync_downloader().download_streaming("http://storage.asm.skype.com/rec", None, None)

    def test_delete_recording_rejects_invalid_recording_url(self):
        with pytest.raises(ValueError, match="HTTPS"):
            _make_sync_downloader().delete_recording("http://storage.asm.skype.com/rec")

    def test_download_streaming_accepts_valid_recording_url(self):
        downloader = _make_sync_downloader()
        mock_pr = MagicMock()
        mock_pr.http_response.status_code = 200
        downloader._call_recording_client._client._pipeline.run.return_value = mock_pr  # pylint: disable=protected-access
        response = downloader.download_streaming("https://storage.asm.skype.com/rec", None, None)
        assert response.status_code == 200
