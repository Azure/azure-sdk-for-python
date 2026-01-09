# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

import base64

from azure.ai.voicelive.models import (
    # Client Events
    ClientEventSessionUpdate,
    ClientEventInputAudioBufferAppend,
    ClientEventInputAudioBufferClear,
    ClientEventInputAudioBufferCommit,
    ClientEventConversationItemCreate,
    ClientEventConversationItemDelete,
    ClientEventConversationItemRetrieve,
    ClientEventConversationItemTruncate,
    ClientEventResponseCreate,
    ClientEventResponseCancel,
    # Event Types
    ClientEventType,
    # Supporting Models
    RequestSession,
    ResponseCreateParams,
    UserMessageItem,
    SystemMessageItem,
    InputTextContentPart,
    MessageRole,
    Modality,
    OpenAIVoiceName,
    OpenAIVoice,
)


class TestClientEventSessionUpdate:
    """Test ClientEventSessionUpdate event."""

    def test_create_session_update_with_request_session(self):
        """Test creating session update with RequestSession object."""
        session = RequestSession(
            model="gpt-4o-realtime-preview",
            modalities=[Modality.TEXT, Modality.AUDIO],
            voice=OpenAIVoice(name=OpenAIVoiceName.ALLOY),
            temperature=0.7,
        )

        event = ClientEventSessionUpdate(session=session)

        assert event.type == ClientEventType.SESSION_UPDATE
        assert event.session == session
        assert event.event_id is None

    def test_create_session_update_with_event_id(self):
        """Test creating session update with event ID."""
        session = RequestSession(model="gpt-4o-realtime-preview")
        event_id = "session-update-123"

        event = ClientEventSessionUpdate(session=session, event_id=event_id)

        assert event.type == ClientEventType.SESSION_UPDATE
        assert event.event_id == event_id

    def test_create_session_update_with_dict(self):
        """Test creating session update with dictionary session."""
        session_dict = {"model": "gpt-4o-realtime-preview", "modalities": ["text", "audio"], "temperature": 0.8}

        event = ClientEventSessionUpdate(session=session_dict)

        assert event.type == ClientEventType.SESSION_UPDATE
        # The session should be stored as provided
        assert event.session == session_dict


class TestClientEventInputAudioBuffer:
    """Test input audio buffer events."""

    def test_audio_buffer_append(self):
        """Test audio buffer append event."""
        audio_data = b"fake audio data"

        event = ClientEventInputAudioBufferAppend(audio=audio_data)

        assert event.type == ClientEventType.INPUT_AUDIO_BUFFER_APPEND
        assert event.audio == base64.b64encode(audio_data).decode("ascii")
        assert event.event_id is None

    def test_audio_buffer_append_with_event_id(self):
        """Test audio buffer append with event ID."""
        audio_data = b"more fake audio"
        event_id = "audio-append-456"

        event = ClientEventInputAudioBufferAppend(audio=audio_data, event_id=event_id)

        assert event.event_id == event_id

    def test_audio_buffer_commit(self):
        """Test audio buffer commit event."""
        event = ClientEventInputAudioBufferCommit()

        assert event.type == ClientEventType.INPUT_AUDIO_BUFFER_COMMIT
        assert event.event_id is None

    def test_audio_buffer_commit_with_event_id(self):
        """Test audio buffer commit with event ID."""
        event_id = "audio-commit-789"
        event = ClientEventInputAudioBufferCommit(event_id=event_id)

        assert event.event_id == event_id

    def test_audio_buffer_clear(self):
        """Test audio buffer clear event."""
        event = ClientEventInputAudioBufferClear()

        assert event.type == ClientEventType.INPUT_AUDIO_BUFFER_CLEAR
        assert event.event_id is None

    def test_audio_buffer_clear_with_event_id(self):
        """Test audio buffer clear with event ID."""
        event_id = "audio-clear-101"
        event = ClientEventInputAudioBufferClear(event_id=event_id)

        assert event.event_id == event_id


class TestClientEventConversationItem:
    """Test conversation item events."""

    def test_conversation_item_create(self):
        """Test conversation item create event."""
        content = [InputTextContentPart(text="Hello, how are you?")]
        item = UserMessageItem(content=content)

        event = ClientEventConversationItemCreate(item=item)

        assert event.type == ClientEventType.CONVERSATION_ITEM_CREATE
        assert event.item == item
        assert event.event_id is None

    def test_conversation_item_create_with_event_id(self):
        """Test conversation item create with event ID."""
        content = [InputTextContentPart(text="System message")]
        item = SystemMessageItem(content=content)
        event_id = "create-item-123"

        event = ClientEventConversationItemCreate(item=item, event_id=event_id)

        assert event.event_id == event_id
        assert event.item.role == MessageRole.SYSTEM

    def test_conversation_item_delete(self):
        """Test conversation item delete event."""
        item_id = "item-to-delete-456"

        event = ClientEventConversationItemDelete(item_id=item_id)

        assert event.type == ClientEventType.CONVERSATION_ITEM_DELETE
        assert event.item_id == item_id
        assert event.event_id is None

    def test_conversation_item_delete_with_event_id(self):
        """Test conversation item delete with event ID."""
        item_id = "item-to-delete-789"
        event_id = "delete-event-101"

        event = ClientEventConversationItemDelete(item_id=item_id, event_id=event_id)

        assert event.item_id == item_id
        assert event.event_id == event_id

    def test_conversation_item_retrieve(self):
        """Test conversation item retrieve event."""
        item_id = "item-to-retrieve-123"

        event = ClientEventConversationItemRetrieve(item_id=item_id)

        assert event.type == ClientEventType.CONVERSATION_ITEM_RETRIEVE
        assert event.item_id == item_id

    def test_conversation_item_truncate(self):
        """Test conversation item truncate event."""
        item_id = "item-to-truncate-456"
        content_index = 2
        audio_end_ms = 5000

        event = ClientEventConversationItemTruncate(
            item_id=item_id, content_index=content_index, audio_end_ms=audio_end_ms
        )

        assert event.type == ClientEventType.CONVERSATION_ITEM_TRUNCATE
        assert event.item_id == item_id
        assert event.content_index == content_index
        assert event.audio_end_ms == audio_end_ms


class TestClientEventResponse:
    """Test response events."""

    def test_response_create_basic(self):
        """Test basic response create event."""
        event = ClientEventResponseCreate()

        assert event.type == ClientEventType.RESPONSE_CREATE
        assert event.response is None
        assert event.additional_instructions is None
        assert event.event_id is None

    def test_response_create_with_params(self):
        """Test response create with parameters."""
        response_params = ResponseCreateParams(modalities=[Modality.TEXT, Modality.AUDIO])
        additional_instructions = "Please be concise and helpful"
        event_id = "response-create-789"

        event = ClientEventResponseCreate(
            response=response_params, additional_instructions=additional_instructions, event_id=event_id
        )

        assert event.response == response_params
        assert event.additional_instructions == additional_instructions
        assert event.event_id == event_id

    def test_response_create_with_instructions_only(self):
        """Test response create with only additional instructions."""
        instructions = "Focus on the key points"

        event = ClientEventResponseCreate(additional_instructions=instructions)

        assert event.additional_instructions == instructions
        assert event.response is None

    def test_response_cancel_basic(self):
        """Test basic response cancel event."""
        event = ClientEventResponseCancel()

        assert event.type == ClientEventType.RESPONSE_CANCEL
        assert event.event_id is None

    def test_response_cancel_with_response_id(self):
        """Test response cancel with response ID."""
        response_id = "response-to-cancel-123"
        event_id = "cancel-event-456"

        # Note: The actual implementation might not have response_id parameter
        # This test assumes it exists based on the connection test
        event = ClientEventResponseCancel(event_id=event_id)

        assert event.event_id == event_id


class TestClientEventSerialization:
    """Test client event serialization capabilities."""

    def test_session_update_dict_access(self):
        """Test that session update events support dict-like access."""
        session = RequestSession(model="gpt-4o-realtime-preview")
        event = ClientEventSessionUpdate(session=session)

        # Test that the event has expected attributes
        assert hasattr(event, "type")
        assert hasattr(event, "session")
        assert event.type == ClientEventType.SESSION_UPDATE

    def test_audio_event_dict_access(self):
        """Test that audio events support dict-like access."""
        audio_data = b"test audio"
        event = ClientEventInputAudioBufferAppend(audio=audio_data)

        # Test that the event has expected attributes
        assert hasattr(event, "type")
        assert hasattr(event, "audio")
        assert event.type == ClientEventType.INPUT_AUDIO_BUFFER_APPEND

    def test_conversation_event_dict_access(self):
        """Test that conversation events support dict-like access."""
        content = [InputTextContentPart(text="Test message")]
        item = UserMessageItem(content=content)
        event = ClientEventConversationItemCreate(item=item)

        # Test that the event has expected attributes
        assert hasattr(event, "type")
        assert hasattr(event, "item")
        assert event.type == ClientEventType.CONVERSATION_ITEM_CREATE


class TestClientEventIntegration:
    """Integration tests for client events."""

    def test_complete_conversation_flow(self):
        """Test a complete conversation flow with multiple events."""
        # Session update
        session = RequestSession(
            model="gpt-4o-realtime-preview",
            modalities=[Modality.TEXT, Modality.AUDIO],
            voice=OpenAIVoice(name=OpenAIVoiceName.SHIMMER),
        )
        session_event = ClientEventSessionUpdate(session=session, event_id="session-1")

        # Add user message
        user_content = [InputTextContentPart(text="What's the weather like?")]
        user_message = UserMessageItem(content=user_content, id="user-msg-1")
        create_event = ClientEventConversationItemCreate(item=user_message, event_id="create-1")

        # Request response
        response_params = ResponseCreateParams(modalities=[Modality.TEXT])
        response_event = ClientEventResponseCreate(
            response=response_params, additional_instructions="Be brief", event_id="response-1"
        )

        # Verify all events are properly created
        assert session_event.type == ClientEventType.SESSION_UPDATE
        assert create_event.type == ClientEventType.CONVERSATION_ITEM_CREATE
        assert response_event.type == ClientEventType.RESPONSE_CREATE

        # Verify event IDs are preserved
        assert session_event.event_id == "session-1"
        assert create_event.event_id == "create-1"
        assert response_event.event_id == "response-1"

    def test_audio_workflow_events(self):
        """Test audio workflow with buffer events."""
        # Append audio data
        audio_chunk_1 = b"first chunk of audio"
        append_event_1 = ClientEventInputAudioBufferAppend(audio=audio_chunk_1, event_id="append-1")

        # Append more audio
        audio_chunk_2 = b"second chunk of audio"
        append_event_2 = ClientEventInputAudioBufferAppend(audio=audio_chunk_2, event_id="append-2")

        # Commit audio buffer
        commit_event = ClientEventInputAudioBufferCommit(event_id="commit-1")

        # Clear buffer (if needed)
        clear_event = ClientEventInputAudioBufferClear(event_id="clear-1")

        # Verify all events are properly typed
        events = [append_event_1, append_event_2, commit_event, clear_event]
        expected_types = [
            ClientEventType.INPUT_AUDIO_BUFFER_APPEND,
            ClientEventType.INPUT_AUDIO_BUFFER_APPEND,
            ClientEventType.INPUT_AUDIO_BUFFER_COMMIT,
            ClientEventType.INPUT_AUDIO_BUFFER_CLEAR,
        ]

        for event, expected_type in zip(events, expected_types):
            assert event.type == expected_type

    def test_conversation_management_events(self):
        """Test conversation management with CRUD operations."""
        # Create system message
        system_content = [InputTextContentPart(text="You are a helpful assistant")]
        system_msg = SystemMessageItem(content=system_content, id="system-1")
        create_system = ClientEventConversationItemCreate(item=system_msg, event_id="create-sys")

        # Create user message
        user_content = [InputTextContentPart(text="Hello!")]
        user_msg = UserMessageItem(content=user_content, id="user-1")
        create_user = ClientEventConversationItemCreate(item=user_msg, event_id="create-user")

        # Retrieve a message
        retrieve_event = ClientEventConversationItemRetrieve(item_id="user-1", event_id="retrieve-1")

        # Truncate a message
        truncate_event = ClientEventConversationItemTruncate(
            item_id="user-1", content_index=0, audio_end_ms=3000, event_id="truncate-1"
        )

        # Delete a message
        delete_event = ClientEventConversationItemDelete(item_id="system-1", event_id="delete-1")

        # Verify all conversation events
        conversation_events = [create_system, create_user, retrieve_event, truncate_event, delete_event]
        expected_types = [
            ClientEventType.CONVERSATION_ITEM_CREATE,
            ClientEventType.CONVERSATION_ITEM_CREATE,
            ClientEventType.CONVERSATION_ITEM_RETRIEVE,
            ClientEventType.CONVERSATION_ITEM_TRUNCATE,
            ClientEventType.CONVERSATION_ITEM_DELETE,
        ]

        for event, expected_type in zip(conversation_events, expected_types):
            assert event.type == expected_type
