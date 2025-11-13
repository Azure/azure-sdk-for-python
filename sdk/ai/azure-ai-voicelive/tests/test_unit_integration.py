# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
Integration test runner and test suite validation.
This file contains tests that verify the test suite itself and run integration scenarios.
"""

import pytest
import importlib

pytest.importorskip(
    "aiohttp",
    reason="Skipping aio tests: aiohttp not installed (whl_no_aio).",
)

# Import the modules we want to test
import azure.ai.voicelive.models as models
import azure.ai.voicelive.aio as aio_module


class TestSuiteValidation:
    """Validate that our test suite covers the main components."""

    def test_can_import_all_test_modules(self):
        """Test that all our test modules can be imported."""
        test_modules = [
            "tests.test_unit_enums",
            "tests.test_unit_models",
            "tests.test_unit_serialization",
            "tests.test_unit_connection",
            "tests.test_unit_client_events",
            "tests.test_unit_voice_config",
            "tests.test_unit_message_handling",
        ]

        for module_name in test_modules:
            try:
                module = importlib.import_module(module_name)
                assert module is not None
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")

    def test_main_package_imports(self):
        """Test that main package components can be imported."""
        # Test main models import
        assert models is not None

        # Test async module import
        assert aio_module is not None

    def test_key_enum_coverage(self):
        """Test that we cover all key enums."""
        key_enums = [
            "AzureVoiceType",
            "MessageRole",
            "OpenAIVoiceName",
            "ClientEventType",
            "ContentPartType",
            "InputAudioFormat",
            "OutputAudioFormat",
            "Modality",
            "ResponseStatus",
        ]

        for enum_name in key_enums:
            assert hasattr(models, enum_name), f"Missing enum: {enum_name}"

    def test_key_model_coverage(self):
        """Test that we cover all key models."""
        key_models = [
            "MessageContentPart",
            "InputTextContentPart",
            "InputAudioContentPart",
            "OutputTextContentPart",
            "UserMessageItem",
            "AssistantMessageItem",
            "SystemMessageItem",
            "OpenAIVoice",
            "AzureCustomVoice",
            "AzureStandardVoice",
            "AzurePersonalVoice",
            "RequestSession",
            "ResponseSession",
        ]

        for model_name in key_models:
            assert hasattr(models, model_name), f"Missing model: {model_name}"

    def test_async_components_coverage(self):
        """Test that we cover async components."""
        async_components = [
            "VoiceLiveConnection",
            "SessionResource",
            "ResponseResource",
            "ConnectionError",
            "ConnectionClosed",
        ]

        for component_name in async_components:
            assert hasattr(aio_module, component_name), f"Missing async component: {component_name}"


class TestRecentChangesIntegration:
    """Test integration of recent changes from the staged commits."""

    def test_azure_voice_type_enum_integration(self):
        """Test that AzureVoiceType enum works with voice models."""
        # Test the new AzureVoiceType enum
        from azure.ai.voicelive.models import (
            AzureVoiceType,
            AzureCustomVoice,
            AzureStandardVoice,
            AzurePersonalVoice,
            PersonalVoiceModels,
        )

        # Test custom voice with enum discriminator
        custom_voice = AzureCustomVoice(
            name="test-custom",
            endpoint_id="endpoint-123",
        )
        assert custom_voice.type == AzureVoiceType.AZURE_CUSTOM

        # Test standard voice with enum discriminator
        standard_voice = AzureStandardVoice(name="test-standard")
        assert standard_voice.type == AzureVoiceType.AZURE_STANDARD

        # Test personal voice with enum discriminator
        personal_voice = AzurePersonalVoice(name="test-personal", model=PersonalVoiceModels.PHOENIX_LATEST_NEURAL)
        assert personal_voice.type == AzureVoiceType.AZURE_PERSONAL

    def test_message_role_enum_integration(self):
        """Test that MessageRole enum works with message items."""
        from azure.ai.voicelive.models import (
            MessageRole,
            UserMessageItem,
            AssistantMessageItem,
            SystemMessageItem,
            InputTextContentPart,
            OutputTextContentPart,
        )

        # Test user message with enum role
        user_msg = UserMessageItem(content=[InputTextContentPart(text="User message")])
        assert user_msg.role == MessageRole.USER

        # Test assistant message with enum role
        assistant_msg = AssistantMessageItem(content=[OutputTextContentPart(text="Assistant response")])
        assert assistant_msg.role == MessageRole.ASSISTANT

        # Test system message with enum role
        system_msg = SystemMessageItem(content=[InputTextContentPart(text="System instruction")])
        assert system_msg.role == MessageRole.SYSTEM

    def test_message_content_part_renaming(self):
        """Test that MessageContentPart (renamed from UserContentPart) works correctly."""
        from azure.ai.voicelive.models import (
            MessageContentPart,
            InputTextContentPart,
            InputAudioContentPart,
            OutputTextContentPart,
        )

        # Test that all content parts inherit from MessageContentPart
        text_part = InputTextContentPart(text="Test text")
        audio_part = InputAudioContentPart(audio=b"test audio")
        output_part = OutputTextContentPart(text="Test output")

        assert isinstance(text_part, MessageContentPart)
        assert isinstance(audio_part, MessageContentPart)
        assert isinstance(output_part, MessageContentPart)

    def test_cross_language_package_id_update(self):
        """Test that the cross-language package ID update doesn't break functionality."""
        # This change is in apiview-properties.json and metadata
        # The actual Python SDK functionality should be unaffected

        from azure.ai.voicelive.models import (
            UserMessageItem,
            InputTextContentPart,
            ClientEventSessionUpdate,
            RequestSession,
        )

        # Test that models still work correctly after the package ID change
        content = [InputTextContentPart(text="Test cross-language compatibility")]
        message = UserMessageItem(content=content)

        session = RequestSession(model="test-model")
        event = ClientEventSessionUpdate(session=session)

        assert message.content[0].text == "Test cross-language compatibility"
        assert event.session == session

    def test_api_version_update_compatibility(self):
        """Test that API version update doesn't break SDK functionality."""
        # API version changed from "2025-05-01-preview" to "2025-10-01"
        # This shouldn't affect the Python SDK functionality directly

        from azure.ai.voicelive.models import RequestSession, OpenAIVoice, OpenAIVoiceName

        # Test that session creation still works
        session = RequestSession(model="gpt-4o-realtime-preview", voice=OpenAIVoice(name=OpenAIVoiceName.ALLOY))

        assert session.model == "gpt-4o-realtime-preview"
        assert session.voice.name == OpenAIVoiceName.ALLOY


class TestErrorHandlingIntegration:
    """Test error handling across the SDK."""

    def test_connection_errors_are_properly_typed(self):
        """Test that connection errors inherit correctly."""
        from azure.ai.voicelive.aio import ConnectionError, ConnectionClosed

        # Test basic error
        basic_error = ConnectionError("Test error")
        assert isinstance(basic_error, Exception)

        # Test connection closed error
        closed_error = ConnectionClosed(1000, "Normal closure")
        assert isinstance(closed_error, ConnectionError)
        assert isinstance(closed_error, Exception)
        assert closed_error.code == 1000
        assert closed_error.reason == "Normal closure"


class TestSerializationIntegration:
    """Test serialization integration across the SDK."""

    def test_enum_serialization_fix(self):
        """Test that the enum serialization fix works correctly."""
        from azure.ai.voicelive._utils.serialization import Serializer
        from azure.ai.voicelive.models import AzureVoiceType, MessageRole, OpenAIVoiceName

        serializer = Serializer()

        # Test that enums serialize correctly (this tests the cast(type, data.__class__) fix)
        voice_type_result = serializer.serialize_data(AzureVoiceType.AZURE_CUSTOM, "str")
        role_result = serializer.serialize_data(MessageRole.ASSISTANT, "str")
        oai_voice_result = serializer.serialize_data(OpenAIVoiceName.ALLOY, "str")

        assert voice_type_result == "azure-custom"
        assert role_result == "assistant"
        assert oai_voice_result == "alloy"

    def test_model_serialization_compatibility(self):
        """Test that models can be serialized properly."""
        from azure.ai.voicelive.models import UserMessageItem, InputTextContentPart, AzureStandardVoice, RequestSession

        # Create complex nested structure
        content = [InputTextContentPart(text="Serialization test")]
        message = UserMessageItem(content=content, id="test-msg")

        voice = AzureStandardVoice(name="test-voice", temperature=0.7)
        session = RequestSession(model="test-model", voice=voice)

        # Test that all objects have the necessary attributes for serialization
        for obj in [content[0], message, voice, session]:
            assert hasattr(obj, "__dict__")


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_complete_voice_assistant_setup(self):
        """Test setting up a complete voice assistant configuration."""
        from azure.ai.voicelive.models import (
            RequestSession,
            AzureStandardVoice,
            Modality,
            SystemMessageItem,
            UserMessageItem,
            InputTextContentPart,
            ClientEventSessionUpdate,
            ClientEventConversationItemCreate,
        )

        # Set up voice configuration
        voice = AzureStandardVoice(name="en-US-JennyNeural", style="friendly", temperature=0.7)

        # Set up session
        session = RequestSession(
            model="gpt-4o-realtime-preview",
            voice=voice,
            modalities=[Modality.TEXT, Modality.AUDIO],
            instructions="You are a helpful voice assistant. Be concise and friendly.",
        )

        # Create system message
        system_content = [InputTextContentPart(text="You are a helpful voice assistant.")]
        system_message = SystemMessageItem(content=system_content)

        # Create user message
        user_content = [InputTextContentPart(text="Hello, can you help me?")]
        user_message = UserMessageItem(content=user_content)

        # Create events
        session_update = ClientEventSessionUpdate(session=session)
        create_system = ClientEventConversationItemCreate(item=system_message)
        create_user = ClientEventConversationItemCreate(item=user_message)

        # Verify everything is set up correctly
        assert session.voice.name == "en-US-JennyNeural"
        assert session.voice.style == "friendly"
        assert len(session.modalities) == 2
        assert system_message.role == "system"
        assert user_message.role == "user"
        assert session_update.session == session

    def test_multi_modal_conversation(self):
        """Test a multi-modal conversation with text and audio."""
        from azure.ai.voicelive.models import (
            UserMessageItem,
            AssistantMessageItem,
            InputTextContentPart,
            InputAudioContentPart,
            OutputTextContentPart,
            MessageRole,
        )

        # User message with text and audio
        user_content = [
            InputTextContentPart(text="I have a question:"),
            InputAudioContentPart(audio=b"fake spoken question audio data"),
        ]
        user_message = UserMessageItem(content=user_content)

        # Assistant text response
        assistant_content = [OutputTextContentPart(text="I understand your question. Let me help you with that.")]
        assistant_message = AssistantMessageItem(content=assistant_content)

        # Verify conversation structure
        conversation = [user_message, assistant_message]

        assert user_message.role == MessageRole.USER
        assert assistant_message.role == MessageRole.ASSISTANT
        assert len(user_message.content) == 2
        assert len(assistant_message.content) == 1
        assert user_message.content[0].type == "input_text"
        assert user_message.content[1].type == "input_audio"
        assert assistant_message.content[0].type == "text"

    def test_voice_switching_scenario(self):
        """Test switching between different voice types."""
        from azure.ai.voicelive.models import (
            OpenAIVoice,
            AzureStandardVoice,
            AzurePersonalVoice,
            OpenAIVoiceName,
            PersonalVoiceModels,
            RequestSession,
        )

        # Start with OpenAI voice
        openai_voice = OpenAIVoice(name=OpenAIVoiceName.ALLOY)
        session1 = RequestSession(model="gpt-4o-realtime-preview", voice=openai_voice)

        # Switch to Azure standard voice
        azure_standard = AzureStandardVoice(name="en-US-AriaNeural", style="cheerful")
        session2 = RequestSession(model="gpt-4o-realtime-preview", voice=azure_standard)

        # Switch to Azure personal voice
        azure_personal = AzurePersonalVoice(
            name="my-personal-voice", model=PersonalVoiceModels.PHOENIX_LATEST_NEURAL, temperature=0.8
        )
        session3 = RequestSession(model="gpt-4o-realtime-preview", voice=azure_personal)

        # Verify each configuration
        assert session1.voice.type == "openai"
        assert session2.voice.type == "azure-standard"
        assert session3.voice.type == "azure-personal"

        # Verify voice-specific properties
        assert session2.voice.style == "cheerful"
        assert session3.voice.temperature == 0.8


class TestBackwardsCompatibility:
    """Test backwards compatibility with previous versions."""

    def test_enum_string_compatibility(self):
        """Test that enums maintain string compatibility."""
        from azure.ai.voicelive.models import MessageRole, AzureVoiceType, OpenAIVoiceName
        from enum import Enum

        # Test that enums can still be compared to strings
        assert MessageRole.USER == "user"
        assert AzureVoiceType.AZURE_CUSTOM == "azure-custom"
        assert OpenAIVoiceName.ALLOY == "alloy"

        # Test case insensitive behavior
        assert MessageRole["USER"] == MessageRole.USER
        assert AzureVoiceType["AZURE_CUSTOM"] == AzureVoiceType.AZURE_CUSTOM

    def test_model_attribute_compatibility(self):
        """Test that model attributes are still accessible."""
        from azure.ai.voicelive.models import UserMessageItem, InputTextContentPart, AzureStandardVoice

        # Test that all expected attributes are accessible
        content = [InputTextContentPart(text="Test message")]
        message = UserMessageItem(content=content, id="test-123")

        voice = AzureStandardVoice(name="test-voice", temperature=0.5)

        # These should all work as before
        assert message.role == "user"  # String comparison should still work
        assert message.content[0].text == "Test message"
        assert message.id == "test-123"
        assert voice.name == "test-voice"
        assert voice.temperature == 0.5


if __name__ == "__main__":
    # Run the tests when this file is executed directly
    pytest.main([__file__])
