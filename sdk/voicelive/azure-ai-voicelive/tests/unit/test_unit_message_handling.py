# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

import base64
from typing import List

from azure.ai.voicelive.models import (
    # Message Content Parts
    MessageContentPart,
    InputAudioContentPart,
    InputTextContentPart,
    OutputTextContentPart,
    # Message Items
    MessageItem,
    UserMessageItem,
    AssistantMessageItem,
    SystemMessageItem,
    # Enums
    MessageRole,
    ContentPartType,
    ItemParamStatus,
    ItemType,
    # Supporting Models
    ConversationRequestItem,
    InputAudioFormat,
)


class TestMessageContentPartHierarchy:
    """Test MessageContentPart hierarchy and inheritance."""

    def test_message_content_part_base_class(self):
        """Test MessageContentPart as base class."""
        # MessageContentPart is an abstract base, so we test through subclasses
        text_part = InputTextContentPart(text="Hello")
        audio_part = InputAudioContentPart(audio=b"audio data")
        output_part = OutputTextContentPart(text="Response")

        # All should inherit from MessageContentPart
        assert isinstance(text_part, MessageContentPart)
        assert isinstance(audio_part, MessageContentPart)
        assert isinstance(output_part, MessageContentPart)

    def test_content_part_type_discrimination(self):
        """Test that content parts are properly discriminated by type."""
        text_part = InputTextContentPart(text="Hello")
        audio_part = InputAudioContentPart(audio=b"audio")
        output_part = OutputTextContentPart(text="Output")

        assert text_part.type == "input_text"
        assert audio_part.type == "input_audio"
        assert output_part.type == "text"

    def test_content_part_polymorphism(self):
        """Test polymorphic usage of content parts."""
        parts: List[MessageContentPart] = [
            InputTextContentPart(text="Text input"),
            InputAudioContentPart(audio=b"audio input"),
            OutputTextContentPart(text="Text output"),
        ]

        # All items should be MessageContentPart instances
        for part in parts:
            assert isinstance(part, MessageContentPart)
            assert hasattr(part, "type")

        # Types should be different
        types = [part.type for part in parts]
        assert "input_text" in types
        assert "input_audio" in types
        assert "text" in types


class TestInputTextContentPart:
    """Test InputTextContentPart model."""

    def test_create_input_text_content_part(self):
        """Test creating input text content part."""
        text = "Hello, how can I help you today?"
        part = InputTextContentPart(text=text)

        assert part.type == "input_text"
        assert part.text == text
        assert isinstance(part, MessageContentPart)

    def test_input_text_content_part_empty_string(self):
        """Test input text content part with empty string."""
        part = InputTextContentPart(text="")

        assert part.type == "input_text"
        assert part.text == ""

    def test_input_text_content_part_long_text(self):
        """Test input text content part with long text."""
        long_text = "This is a very long text that represents a substantial user input. " * 100
        part = InputTextContentPart(text=long_text)

        assert part.type == "input_text"
        assert part.text == long_text
        assert len(part.text) > 1000

    def test_input_text_content_part_unicode(self):
        """Test input text content part with unicode characters."""
        unicode_text = "Hello 世界! 🌍 Café naïve résumé"
        part = InputTextContentPart(text=unicode_text)

        assert part.type == "input_text"
        assert part.text == unicode_text


class TestInputAudioContentPart:
    """Test InputAudioContentPart model."""

    def test_create_input_audio_content_part(self):
        """Test creating input audio content part."""
        audio_data = b"fake audio binary data"
        part = InputAudioContentPart(audio=audio_data)

        assert part.type == "input_audio"
        assert part.audio == base64.b64encode(audio_data).decode("ascii")
        assert isinstance(part, MessageContentPart)

    def test_input_audio_content_part_empty_data(self):
        """Test input audio content part with empty data."""
        part = InputAudioContentPart(audio=b"")

        assert part.type == "input_audio"
        assert part.audio == ""

    def test_input_audio_content_part_large_data(self):
        """Test input audio content part with large audio data."""
        large_audio = b"audio data chunk " * 1000
        part = InputAudioContentPart(audio=large_audio)

        assert part.type == "input_audio"
        assert part.audio == base64.b64encode(large_audio).decode("ascii")
        assert len(part.audio) > 10000


class TestOutputTextContentPart:
    """Test OutputTextContentPart model."""

    def test_create_output_text_content_part(self):
        """Test creating output text content part."""
        text = "I'm happy to help you with that!"
        part = OutputTextContentPart(text=text)

        assert part.type == "text"
        assert part.text == text
        assert isinstance(part, MessageContentPart)

    def test_output_text_content_part_inheritance(self):
        """Test that OutputTextContentPart inherits from MessageContentPart."""
        part = OutputTextContentPart(text="Test output")

        # Should inherit from MessageContentPart (this is the recent change)
        assert isinstance(part, MessageContentPart)
        assert hasattr(part, "type")

    def test_output_text_content_part_discriminator(self):
        """Test OutputTextContentPart type discriminator."""
        part = OutputTextContentPart(text="Response text")

        # Type should be "text" for output text content
        assert part.type == "text"
        assert part.type == ContentPartType.TEXT


class TestMessageItemsWithContentParts:
    """Test message items using MessageContentPart."""

    def test_user_message_with_text_content(self):
        """Test user message with text content."""
        content = [InputTextContentPart(text="What's the weather like?")]
        message = UserMessageItem(content=content)

        assert message.role == MessageRole.USER
        assert message.type == ItemType.MESSAGE
        assert len(message.content) == 1
        assert isinstance(message.content[0], MessageContentPart)
        assert message.content[0].text == "What's the weather like?"

    def test_user_message_with_audio_content(self):
        """Test user message with audio content."""
        audio_data = b"spoken question audio data"
        content = [InputAudioContentPart(audio=audio_data)]
        message = UserMessageItem(content=content)

        assert message.role == MessageRole.USER
        assert len(message.content) == 1
        assert isinstance(message.content[0], MessageContentPart)
        assert message.content[0].audio == base64.b64encode(audio_data).decode("ascii")

    def test_user_message_with_mixed_content(self):
        """Test user message with mixed content types."""
        text_part = InputTextContentPart(text="Here's my question:")
        audio_part = InputAudioContentPart(audio=b"spoken question")
        content = [text_part, audio_part]

        message = UserMessageItem(content=content)

        assert message.role == MessageRole.USER
        assert len(message.content) == 2
        assert all(isinstance(part, MessageContentPart) for part in message.content)
        assert message.content[0].type == "input_text"
        assert message.content[1].type == "input_audio"

    def test_assistant_message_with_output_content(self):
        """Test assistant message with output content."""
        content = [OutputTextContentPart(text="The weather is sunny today!")]
        message = AssistantMessageItem(content=content)

        assert message.role == MessageRole.ASSISTANT
        assert message.type == ItemType.MESSAGE
        assert len(message.content) == 1
        assert isinstance(message.content[0], MessageContentPart)
        assert message.content[0].text == "The weather is sunny today!"

    def test_system_message_with_text_content(self):
        """Test system message with text content."""
        content = [InputTextContentPart(text="You are a helpful weather assistant.")]
        message = SystemMessageItem(content=content)

        assert message.role == MessageRole.SYSTEM
        assert message.type == ItemType.MESSAGE
        assert len(message.content) == 1
        assert isinstance(message.content[0], MessageContentPart)
        assert message.content[0].text == "You are a helpful weather assistant."


class TestMessageItemPolymorphism:
    """Test message item polymorphism and inheritance."""

    def test_message_item_inheritance(self):
        """Test that all message items inherit from MessageItem."""
        user_content = [InputTextContentPart(text="User message")]
        assistant_content = [OutputTextContentPart(text="Assistant response")]
        system_content = [InputTextContentPart(text="System instruction")]

        user_msg = UserMessageItem(content=user_content)
        assistant_msg = AssistantMessageItem(content=assistant_content)
        system_msg = SystemMessageItem(content=system_content)

        # All should inherit from MessageItem
        assert isinstance(user_msg, MessageItem)
        assert isinstance(assistant_msg, MessageItem)
        assert isinstance(system_msg, MessageItem)

        # All should inherit from ConversationRequestItem
        assert isinstance(user_msg, ConversationRequestItem)
        assert isinstance(assistant_msg, ConversationRequestItem)
        assert isinstance(system_msg, ConversationRequestItem)

    def test_message_item_discrimination(self):
        """Test message item role discrimination."""
        user_content = [InputTextContentPart(text="User")]
        assistant_content = [OutputTextContentPart(text="Assistant")]
        system_content = [InputTextContentPart(text="System")]

        messages = [
            UserMessageItem(content=user_content),
            AssistantMessageItem(content=assistant_content),
            SystemMessageItem(content=system_content),
        ]

        roles = [msg.role for msg in messages]
        expected_roles = [MessageRole.USER, MessageRole.ASSISTANT, MessageRole.SYSTEM]

        assert roles == expected_roles

    def test_message_collection_polymorphism(self):
        """Test using message items in collections."""
        messages: List[MessageItem] = [
            SystemMessageItem(content=[InputTextContentPart(text="You are helpful")]),
            UserMessageItem(content=[InputTextContentPart(text="Hello")]),
            AssistantMessageItem(content=[OutputTextContentPart(text="Hi there!")]),
            UserMessageItem(
                content=[InputTextContentPart(text="Can you help me?"), InputAudioContentPart(audio=b"audio question")]
            ),
        ]

        # All should be MessageItem instances
        for message in messages:
            assert isinstance(message, MessageItem)
            assert hasattr(message, "role")
            assert hasattr(message, "content")
            assert hasattr(message, "type")
            assert message.type == ItemType.MESSAGE

        # Verify mixed content types work in collection
        last_message = messages[-1]
        assert len(last_message.content) == 2
        assert last_message.content[0].type == "input_text"
        assert last_message.content[1].type == "input_audio"


class TestMessageWithOptionalFields:
    """Test message items with optional fields."""

    def test_message_with_id_and_status(self):
        """Test message with optional ID and status."""
        content = [InputTextContentPart(text="Message with metadata")]
        message = UserMessageItem(content=content, id="msg-123", status=ItemParamStatus.COMPLETED)

        assert message.id == "msg-123"
        assert message.status == ItemParamStatus.COMPLETED
        assert message.role == MessageRole.USER

    def test_message_with_incomplete_status(self):
        """Test message with incomplete status."""
        content = [InputTextContentPart(text="Incomplete message")]
        message = AssistantMessageItem(content=content, status=ItemParamStatus.INCOMPLETE)

        assert message.status == ItemParamStatus.INCOMPLETE
        assert message.role == MessageRole.ASSISTANT

    def test_message_without_optional_fields(self):
        """Test message without optional fields."""
        content = [InputTextContentPart(text="Simple message")]
        message = UserMessageItem(content=content)

        assert message.id is None
        assert message.status is None
        assert message.role == MessageRole.USER


class TestContentPartValidation:
    """Test content part validation and edge cases."""

    def test_empty_content_list(self):
        """Test message with empty content list."""
        # This might be invalid depending on the model validation
        try:
            message = UserMessageItem(content=[])
            # If it succeeds, verify it's at least structured correctly
            assert message.role == MessageRole.USER
            assert len(message.content) == 0
        except (ValueError, TypeError):
            # If validation prevents empty content, that's also valid behavior
            pass

    def test_content_part_type_consistency(self):
        """Test that content part types are consistent."""
        text_parts = [InputTextContentPart(text="First text"), InputTextContentPart(text="Second text")]

        message = UserMessageItem(content=text_parts)

        # All parts should have the same type
        types = [part.type for part in message.content]
        assert all(t == "input_text" for t in types)

    def test_content_part_mixed_types(self):
        """Test content parts with mixed types."""
        mixed_content = [
            InputTextContentPart(text="Text part"),
            InputAudioContentPart(audio=b"Audio part"),
            InputTextContentPart(text="Another text part"),
        ]

        message = UserMessageItem(content=mixed_content)

        types = [part.type for part in message.content]
        assert types == ["input_text", "input_audio", "input_text"]


class TestMessageHandlingIntegration:
    """Integration tests for message handling."""

    def test_conversation_flow(self):
        """Test a complete conversation flow with proper content parts."""
        # System message
        system_msg = SystemMessageItem(content=[InputTextContentPart(text="You are a helpful assistant.")], id="sys-1")

        # User message with text
        user_msg_1 = UserMessageItem(content=[InputTextContentPart(text="Hello, how are you?")], id="user-1")

        # Assistant response
        assistant_msg_1 = AssistantMessageItem(
            content=[OutputTextContentPart(text="I'm doing well, thank you!")],
            id="assistant-1",
            status=ItemParamStatus.COMPLETED,
        )

        # User message with audio
        user_msg_2 = UserMessageItem(
            content=[
                InputTextContentPart(text="I have a question:"),
                InputAudioContentPart(audio=b"spoken question audio"),
            ],
            id="user-2",
        )

        # Verify conversation structure
        conversation = [system_msg, user_msg_1, assistant_msg_1, user_msg_2]

        for message in conversation:
            assert isinstance(message, MessageItem)
            assert all(isinstance(part, MessageContentPart) for part in message.content)

        # Verify roles
        roles = [msg.role for msg in conversation]
        expected_roles = [MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT, MessageRole.USER]
        assert roles == expected_roles

    def test_message_content_serialization_ready(self):
        """Test that messages and content parts are ready for serialization."""
        content_parts = [
            InputTextContentPart(text="Serializable text"),
            InputAudioContentPart(audio=b"serializable audio"),
            OutputTextContentPart(text="Serializable output"),
        ]

        messages = [
            UserMessageItem(content=[content_parts[0]], id="user-ser"),
            UserMessageItem(content=[content_parts[1]], id="user-audio"),
            AssistantMessageItem(content=[content_parts[2]], id="assistant-ser"),
        ]

        for message in messages:
            # All messages should have required serialization attributes
            assert hasattr(message, "__dict__")
            assert hasattr(message, "role")
            assert hasattr(message, "content")
            assert hasattr(message, "type")

            for part in message.content:
                assert hasattr(part, "__dict__")
                assert hasattr(part, "type")

    def test_backwards_compatibility(self):
        """Test backwards compatibility with content part changes."""
        # Verify that the rename from UserContentPart to MessageContentPart
        # doesn't break existing functionality

        # These should all work with MessageContentPart
        text_part = InputTextContentPart(text="Compatibility test")
        audio_part = InputAudioContentPart(audio=b"compatibility audio")
        output_part = OutputTextContentPart(text="Compatibility output")

        # All should be MessageContentPart instances
        assert isinstance(text_part, MessageContentPart)
        assert isinstance(audio_part, MessageContentPart)
        assert isinstance(output_part, MessageContentPart)

        # Should work in messages
        user_msg = UserMessageItem(content=[text_part, audio_part])
        assistant_msg = AssistantMessageItem(content=[output_part])

        assert len(user_msg.content) == 2
        assert len(assistant_msg.content) == 1
