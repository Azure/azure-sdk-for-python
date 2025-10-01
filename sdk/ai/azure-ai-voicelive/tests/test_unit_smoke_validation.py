# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
Simple smoke tests to verify the unit test suite functionality.
Run this file directly to test the basic imports and functionality.
"""

import pytest

pytest.importorskip(
    "aiohttp",
    reason="Skipping aio tests: aiohttp not installed (whl_no_aio).",
)


def test_basic_imports():
    """Test that key components can be imported."""
    try:
        # Test enum imports
        from azure.ai.voicelive.models import (
            AzureVoiceType,
            MessageRole,
            OpenAIVoiceName,
            InputAudioFormat,
            OutputAudioFormat,
            Modality,
        )

        # Test model imports
        from azure.ai.voicelive.models import (
            InputTextContentPart,
            OutputTextContentPart,
            UserMessageItem,
            AssistantMessageItem,
            SystemMessageItem,
            OpenAIVoice,
            AzureStandardVoice,
            AzurePersonalVoice,
            RequestSession,
        )

        # Test async imports
        from azure.ai.voicelive.aio import (
            VoiceLiveConnection,
            SessionResource,
            ResponseResource,
            ConnectionError,
            ConnectionClosed,
        )

        print("✅ All imports successful!")
        assert True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        assert False


def test_enum_functionality():
    """Test basic enum functionality."""
    try:
        from azure.ai.voicelive.models import AzureVoiceType, MessageRole, OpenAIVoiceName

        # Test enum values
        assert AzureVoiceType.AZURE_CUSTOM == "azure-custom"
        assert MessageRole.USER == "user"
        assert OpenAIVoiceName.ALLOY == "alloy"

        # Test enum comparison
        assert AzureVoiceType.AZURE_STANDARD.value == "azure-standard"
        assert MessageRole.ASSISTANT.value == "assistant"

        print("✅ Enum functionality works!")
        assert True
    except (ImportError, AssertionError) as e:
        print(f"❌ Enum test failed: {e}")
        assert False


def test_model_creation():
    """Test basic model creation."""
    try:
        from azure.ai.voicelive.models import (
            InputTextContentPart,
            UserMessageItem,
            AzureStandardVoice,
            OpenAIVoice,
            OpenAIVoiceName,
            RequestSession,
        )

        # Test content part creation
        content = InputTextContentPart(text="Hello, world!")
        assert content.text == "Hello, world!"
        assert content.type == "input_text"

        # Test message creation
        message = UserMessageItem(content=[content])
        assert message.role == "user"
        assert len(message.content) == 1

        # Test voice creation
        openai_voice = OpenAIVoice(name=OpenAIVoiceName.ALLOY)
        assert openai_voice.type == "openai"
        assert openai_voice.name == OpenAIVoiceName.ALLOY

        azure_voice = AzureStandardVoice(name="en-US-JennyNeural")
        assert azure_voice.type == "azure-standard"
        assert azure_voice.name == "en-US-JennyNeural"

        # Test session creation
        session = RequestSession(model="gpt-4o-realtime-preview", voice=openai_voice)
        assert session.model == "gpt-4o-realtime-preview"
        assert session.voice == openai_voice

        print("✅ Model creation works!")
        assert True
    except Exception as e:
        print(f"❌ Model creation test failed: {e}")
        assert False


def test_recent_changes():
    """Test recent changes from the staged commits."""
    try:
        from azure.ai.voicelive.models import (
            AzureVoiceType,
            MessageRole,
            MessageContentPart,
            InputTextContentPart,
            OutputTextContentPart,
            AzureCustomVoice,
            AzureStandardVoice,
            AzurePersonalVoice,
            PersonalVoiceModels,
        )

        # Test new AzureVoiceType enum
        assert AzureVoiceType.AZURE_CUSTOM == "azure-custom"
        assert AzureVoiceType.AZURE_STANDARD == "azure-standard"
        assert AzureVoiceType.AZURE_PERSONAL == "azure-personal"

        # Test MessageRole enum
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
        assert MessageRole.SYSTEM == "system"

        # Test MessageContentPart hierarchy (renamed from UserContentPart)
        text_part = InputTextContentPart(text="Test")
        output_part = OutputTextContentPart(text="Response")

        assert isinstance(text_part, MessageContentPart)
        assert isinstance(output_part, MessageContentPart)

        # Test Azure voice types with enum discriminators
        standard_voice = AzureStandardVoice(name="test-voice")
        assert standard_voice.type == AzureVoiceType.AZURE_STANDARD

        custom_voice = AzureCustomVoice(name="custom-voice", endpoint_id="endpoint-123")
        assert custom_voice.type == AzureVoiceType.AZURE_CUSTOM

        personal_voice = AzurePersonalVoice(name="personal-voice", model=PersonalVoiceModels.PHOENIX_LATEST_NEURAL)
        assert personal_voice.type == AzureVoiceType.AZURE_PERSONAL

        print("✅ Recent changes work correctly!")
        assert True
    except Exception as e:
        print(f"❌ Recent changes test failed: {e}")
        assert False


def run_all_tests():
    """Run all smoke tests."""
    print("🧪 Running Azure AI VoiceLive SDK unit test validation...\n")

    tests = [
        ("Basic Imports", test_basic_imports),
        ("Enum Functionality", test_enum_functionality),
        ("Model Creation", test_model_creation),
        ("Recent Changes", test_recent_changes),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()

    print(f"🏁 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All smoke tests passed! The unit test suite should work correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the implementation or test setup.")
        return False


if __name__ == "__main__":
    run_all_tests()
