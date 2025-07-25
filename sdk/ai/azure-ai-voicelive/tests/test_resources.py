# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Tests for VoiceLive SDK resource classes."""

import unittest
from unittest.mock import MagicMock, patch
import json

from azure.ai.voicelive import (
    VoiceLiveConnection,
    VoiceLiveSessionResource,
    VoiceLiveResponseResource,
    VoiceLiveInputAudioBufferResource,
    VoiceLiveOutputAudioBufferResource,
    VoiceLiveConversationResource,
    VoiceLiveConversationItemResource,
    VoiceLiveTranscriptionSessionResource,
)


class TestVoiceLiveResources(unittest.TestCase):
    """Test case for VoiceLive resource classes."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection = MagicMock()
        self.connection = VoiceLiveConnection(self.mock_connection)

    def test_session_resource(self):
        """Test SessionResource."""
        # Test update method
        session_data = {"modalities": ["audio", "text"]}
        self.connection.session.update(session=session_data)

        # Verify send was called with correct event
        expected_event = {"type": "session.update", "session": session_data}
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))

    def test_response_resource(self):
        """Test ResponseResource."""
        # Test create method
        self.connection.response.create()
        expected_event = {"type": "response.create"}
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))

        # Reset mock and test create with options
        self.mock_connection.reset_mock()
        response_config = {"temperature": 0.7}
        self.connection.response.create(response=response_config, event_id="test-event-1")
        expected_event = {"type": "response.create", "response": response_config, "event_id": "test-event-1"}
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))

        # Reset mock and test cancel
        self.mock_connection.reset_mock()
        self.connection.response.cancel(response_id="resp-123", event_id="test-event-2")
        expected_event = {"type": "response.cancel", "response_id": "resp-123", "event_id": "test-event-2"}
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))

    def test_input_audio_buffer_resource(self):
        """Test InputAudioBufferResource."""
        # Test append method
        audio_data = "base64-encoded-audio"
        self.connection.input_audio_buffer.append(audio=audio_data)
        expected_event = {"type": "input_audio_buffer.append", "audio": audio_data}
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))

        # Reset mock and test commit
        self.mock_connection.reset_mock()
        self.connection.input_audio_buffer.commit()
        expected_event = {"type": "input_audio_buffer.commit"}
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))

        # Reset mock and test clear
        self.mock_connection.reset_mock()
        self.connection.input_audio_buffer.clear()
        expected_event = {"type": "input_audio_buffer.clear"}
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))

    def test_output_audio_buffer_resource(self):
        """Test OutputAudioBufferResource."""
        # Test clear method
        self.connection.output_audio_buffer.clear()
        expected_event = {"type": "output_audio_buffer.clear"}
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))

    def test_conversation_item_resource(self):
        """Test ConversationItemResource."""
        # Test create method
        item_data = {"type": "message", "role": "user", "content": [{"type": "text", "text": "Hello"}]}
        self.connection.conversation.item.create(item=item_data)
        expected_event = {"type": "conversation.item.create", "item": item_data}
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))

        # Reset mock and test create with previous_item_id
        self.mock_connection.reset_mock()
        self.connection.conversation.item.create(item=item_data, previous_item_id="prev-123", event_id="test-event-3")
        expected_event = {
            "type": "conversation.item.create",
            "item": item_data,
            "previous_item_id": "prev-123",
            "event_id": "test-event-3",
        }
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))

        # Reset mock and test delete
        self.mock_connection.reset_mock()
        self.connection.conversation.item.delete(item_id="item-123")
        expected_event = {"type": "conversation.item.delete", "item_id": "item-123"}
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))

        # Reset mock and test retrieve
        self.mock_connection.reset_mock()
        self.connection.conversation.item.retrieve(item_id="item-456")
        expected_event = {"type": "conversation.item.retrieve", "item_id": "item-456"}
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))

        # Reset mock and test truncate
        self.mock_connection.reset_mock()
        self.connection.conversation.item.truncate(item_id="item-789", audio_end_ms=5000, content_index=0)
        expected_event = {
            "type": "conversation.item.truncate",
            "item_id": "item-789",
            "audio_end_ms": 5000,
            "content_index": 0,
        }
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))

    def test_transcription_session_resource(self):
        """Test TranscriptionSessionResource."""
        # Test update method
        session_data = {"model": "whisper-1"}
        self.connection.transcription_session.update(session=session_data)
        expected_event = {"type": "transcription_session.update", "session": session_data}
        self.mock_connection.send.assert_called_once_with(json.dumps(expected_event))


if __name__ == "__main__":
    unittest.main()
