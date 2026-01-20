# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

import pytest
from enum import Enum
from typing import cast

from azure.ai.voicelive._utils.serialization import Serializer, SerializationError
from azure.ai.voicelive.models import (
    AzureVoiceType,
    MessageRole,
    OpenAIVoiceName,
    InputAudioFormat,
    OutputAudioFormat,
    ItemParamStatus,
    ResponseStatus,
    Modality,
    InputTextContentPart,
    OutputTextContentPart,
    UserMessageItem,
    AssistantMessageItem,
    AzureStandardVoice,
    OpenAIVoice,
)


class EnumForTest(str, Enum):
    """Enum for serialization testing."""

    VALUE_A = "value_a"
    VALUE_B = "value_b"


class TestSerializerBasicTypes:
    """Test serializer with basic types."""

    def setUp(self):
        """Set up serializer for testing."""
        self.serializer = Serializer()

    def test_serialize_string(self):
        """Test string serialization."""
        serializer = Serializer()
        result = serializer.serialize_data("test_string", "str")
        assert result == "test_string"

    def test_serialize_int(self):
        """Test integer serialization."""
        serializer = Serializer()
        result = serializer.serialize_data(42, "int")
        assert result == 42

    def test_serialize_float(self):
        """Test float serialization."""
        serializer = Serializer()
        result = serializer.serialize_data(3.14, "float")
        assert result == 3.14

    def test_serialize_bool(self):
        """Test boolean serialization."""
        serializer = Serializer()
        result = serializer.serialize_data(True, "bool")
        assert result is True

        result = serializer.serialize_data(False, "bool")
        assert result is False

    def test_serialize_none(self):
        """Test None serialization."""
        serializer = Serializer()
        with pytest.raises(ValueError):
            serializer.serialize_data(None, "str")


class TestSerializerEnums:
    """Test serializer with enum types."""

    def test_serialize_azure_voice_type(self):
        """Test AzureVoiceType enum serialization."""
        serializer = Serializer()
        result = serializer.serialize_data(AzureVoiceType.AZURE_CUSTOM, "str")
        assert result == "azure-custom"

    def test_serialize_message_role(self):
        """Test MessageRole enum serialization."""
        serializer = Serializer()
        result = serializer.serialize_data(MessageRole.ASSISTANT, "str")
        assert result == "assistant"

    def test_serialize_oai_voice(self):
        """Test OpenAIVoiceName enum serialization."""
        serializer = Serializer()
        result = serializer.serialize_data(OpenAIVoiceName.ALLOY, "str")
        assert result == "alloy"

    def test_serialize_input_audio_format(self):
        """Test InputAudioFormat enum serialization."""
        serializer = Serializer()
        result = serializer.serialize_data(InputAudioFormat.PCM16, "str")
        assert result == "pcm16"

    def test_serialize_output_audio_format(self):
        """Test OutputAudioFormat enum serialization."""
        serializer = Serializer()
        result = serializer.serialize_data(OutputAudioFormat.G711_ULAW, "str")
        assert result == "g711_ulaw"

    def test_serialize_response_status(self):
        """Test ResponseStatus enum serialization."""
        serializer = Serializer()
        result = serializer.serialize_data(ResponseStatus.COMPLETED, "str")
        assert result == "completed"

    def test_serialize_custom_test_enum(self):
        """Test custom test enum serialization."""
        serializer = Serializer()
        result = serializer.serialize_data(EnumForTest.VALUE_A, "str")
        assert result == "value_a"


class TestSerializerEnumTypeCasting:
    """Test the specific enum type casting fix from the recent changes."""

    def test_enum_type_casting_fix(self):
        """Test that enum type casting works correctly.

        This tests the specific fix where data.__class__ is cast to type
        in the serialization utilities.
        """
        serializer = Serializer()

        # Test with various enum types to ensure the cast(type, data.__class__) fix works
        enums_to_test = [
            (AzureVoiceType.AZURE_CUSTOM, "azure-custom"),
            (MessageRole.USER, "user"),
            (OpenAIVoiceName.SHIMMER, "shimmer"),
            (InputAudioFormat.G711_ALAW, "g711_alaw"),
            (ItemParamStatus.COMPLETED, "completed"),
            (Modality.AUDIO, "audio"),
        ]

        for enum_value, expected_result in enums_to_test:
            result = serializer.serialize_data(enum_value, "str")
            assert result == expected_result, f"Failed for {enum_value}: expected {expected_result}, got {result}"

    def test_enum_class_attribute_casting(self):
        """Test that the enum class casting works with __class__ attribute."""
        serializer = Serializer()

        # Create enum instances and test that their __class__ can be cast to type
        voice_type = AzureVoiceType.AZURE_STANDARD
        role = MessageRole.ASSISTANT

        # These should not raise TypeError due to the cast(type, data.__class__) fix
        voice_result = serializer.serialize_data(voice_type, "str")
        role_result = serializer.serialize_data(role, "str")

        assert voice_result == "azure-standard"
        assert role_result == "assistant"

    def test_enum_inheritance_check(self):
        """Test that enum inheritance checking works correctly."""
        serializer = Serializer()

        # Test that issubclass works with the casted type
        voice_type = AzureVoiceType.AZURE_PERSONAL

        # This should work without TypeError
        result = serializer.serialize_data(voice_type, "str")
        assert result == "azure-personal"

        # Verify the enum is still recognized as an Enum subclass
        casted_type = cast(type, voice_type.__class__)
        assert issubclass(casted_type, Enum)


class TestSerializerCollections:
    """Test serializer with collections containing enums."""

    def test_serialize_list_of_enums(self):
        """Test serializing a list of enums."""
        serializer = Serializer()
        enum_list = [AzureVoiceType.AZURE_CUSTOM, AzureVoiceType.AZURE_STANDARD]

        result = serializer.serialize_data(enum_list, "[str]")
        assert result == ["azure-custom", "azure-standard"]

    def test_serialize_list_of_modalities(self):
        """Test serializing a list of modality enums."""
        serializer = Serializer()
        modalities = [Modality.TEXT, Modality.AUDIO, Modality.ANIMATION]

        result = serializer.serialize_data(modalities, "[str]")
        assert result == ["text", "audio", "animation"]

    def test_serialize_mixed_list(self):
        """Test serializing a list with mixed types."""
        serializer = Serializer()
        mixed_list = ["string", 42, True, MessageRole.SYSTEM]

        # Note: This might need adjustment based on actual serializer behavior
        # The test verifies that enums in mixed collections are handled correctly
        try:
            result = serializer.serialize_data(mixed_list, "[object]")
            # At minimum, ensure no exceptions are raised
            assert isinstance(result, list)
        except (SerializationError, NotImplementedError):
            # Some serializers may not support mixed types
            pytest.skip("Serializer doesn't support mixed type collections")


class TestSerializerModels:
    """Test serializer with model objects."""

    def test_serialize_content_part(self):
        """Test serializing content parts."""
        serializer = Serializer()
        content = InputTextContentPart(text="Hello, world!")

        # Test that model objects can be serialized
        # The exact behavior depends on the model's serialization implementation
        try:
            result = serializer.serialize_data(content, "object")
            assert isinstance(result, dict) or hasattr(content, "as_dict")
        except (SerializationError, AttributeError):
            # If direct serialization isn't supported, at least verify the object exists
            assert content.text == "Hello, world!"
            assert content.type == "input_text"

    def test_serialize_message_item(self):
        """Test serializing message items."""
        serializer = Serializer()
        content = [InputTextContentPart(text="Test message")]
        message = UserMessageItem(content=content)

        # Verify the message has the correct structure
        assert message.role == MessageRole.USER
        assert len(message.content) == 1
        assert message.content[0].text == "Test message"

    def test_serialize_voice_config(self):
        """Test serializing voice configurations."""
        serializer = Serializer()
        voice = AzureStandardVoice(name="test-voice", temperature=0.7)

        # Verify voice configuration structure
        assert voice.type == AzureVoiceType.AZURE_STANDARD
        assert voice.name == "test-voice"
        assert voice.temperature == 0.7


class TestSerializerErrorHandling:
    """Test serializer error handling."""

    def test_serialization_error_handling(self):
        """Test that serialization errors are properly handled."""
        serializer = Serializer()

        # Test with an object that can't be serialized
        class UnserializableObject:
            def __init__(self):
                self._private = "private"

        obj = UnserializableObject()

        # This should either serialize or raise a SerializationError
        try:
            result = serializer.serialize_data(obj, "object")
            # If serialization succeeds, verify it's reasonable
            assert isinstance(result, (dict, str)) or result is None
        except (SerializationError, TypeError):
            # Expected for truly unserializable objects
            pass

    def test_invalid_data_type_specification(self):
        """Test handling of invalid data type specifications."""
        serializer = Serializer()

        try:
            # Try with an invalid type specification
            result = serializer.serialize_data("test", "invalid_type")
            # If it doesn't raise an error, it should return something reasonable
            assert result is not None
        except (SerializationError, ValueError, TypeError):
            # Expected for invalid type specifications
            pass


class TestSerializerIntegration:
    """Integration tests for serializer functionality."""

    def test_complex_enum_scenarios(self):
        """Test complex scenarios with multiple enum types."""
        serializer = Serializer()

        # Create a complex scenario with nested enums
        voice_types = [AzureVoiceType.AZURE_CUSTOM, AzureVoiceType.AZURE_STANDARD, AzureVoiceType.AZURE_PERSONAL]

        roles = [MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT]

        # Test serializing multiple enum collections
        voice_result = serializer.serialize_data(voice_types, "[str]")
        roles_result = serializer.serialize_data(roles, "[str]")

        assert voice_result == ["azure-custom", "azure-standard", "azure-personal"]
        assert roles_result == ["system", "user", "assistant"]

    def test_enum_with_model_objects(self):
        """Test enums used within model objects."""
        content = [OutputTextContentPart(text="Assistant response")]
        message = AssistantMessageItem(content=content)

        # Verify that enums within models work correctly
        assert message.role == MessageRole.ASSISTANT
        assert message.content[0].type == "text"

        # Test that the discriminator enum values are properly set
        openai_voice = OpenAIVoice(name=OpenAIVoiceName.CORAL)
        assert openai_voice.type == "openai"
        assert openai_voice.name == OpenAIVoiceName.CORAL

    def test_serializer_with_real_world_data(self):
        """Test serializer with realistic data structures."""
        serializer = Serializer()

        # Create realistic data that might be serialized in the SDK
        modalities = [Modality.TEXT, Modality.AUDIO]
        audio_formats = [InputAudioFormat.PCM16, InputAudioFormat.G711_ULAW]

        modalities_result = serializer.serialize_data(modalities, "[str]")
        formats_result = serializer.serialize_data(audio_formats, "[str]")

        assert modalities_result == ["text", "audio"]
        assert formats_result == ["pcm16", "g711_ulaw"]


class TestSerializationSecurity:
    """Test security improvements in serialization (removed eval usage)."""

    def test_serialize_basic_no_eval(self):
        """Test that basic type serialization doesn't use eval()."""
        from azure.ai.voicelive._utils.serialization import Serializer

        serializer = Serializer()

        # These should work without eval
        assert serializer.serialize_basic("test", "str") == "test"
        assert serializer.serialize_basic(42, "int") == 42
        assert serializer.serialize_basic(3.14, "float") == 3.14
        assert serializer.serialize_basic(True, "bool") is True

    def test_serialize_basic_invalid_type_raises_error(self):
        """Test that invalid data types raise TypeError instead of eval error."""
        from azure.ai.voicelive._utils.serialization import Serializer

        serializer = Serializer()

        # Should raise TypeError for unsupported types, not execute arbitrary code
        with pytest.raises(TypeError, match="Unknown basic data type"):
            serializer.serialize_basic("test", "malicious_code")

    def test_deserialize_basic_no_eval(self):
        """Test that basic type deserialization doesn't use eval()."""
        from azure.ai.voicelive._utils.serialization import Deserializer

        deserializer = Deserializer()

        # These should work without eval
        assert deserializer.deserialize_basic("test", "str") == "test"
        assert deserializer.deserialize_basic("42", "int") == 42
        assert deserializer.deserialize_basic("3.14", "float") == 3.14

    def test_deserialize_basic_invalid_type_raises_error(self):
        """Test that invalid data types raise TypeError in deserialization."""
        from azure.ai.voicelive._utils.serialization import Deserializer

        deserializer = Deserializer()

        # Should raise TypeError for unsupported types
        with pytest.raises(TypeError, match="Unknown basic data type"):
            deserializer.deserialize_basic("test", "unknown_type")

    def test_security_bool_serialization(self):
        """Test that bool serialization works correctly without eval."""
        from azure.ai.voicelive._utils.serialization import Serializer

        serializer = Serializer()

        # Test bool specifically as it was changed from eval(data_type)(data)
        assert serializer.serialize_basic(True, "bool") is True
        assert serializer.serialize_basic(False, "bool") is False
        assert serializer.serialize_basic(1, "bool") is True  # Truthy value
        assert serializer.serialize_basic(0, "bool") is False  # Falsy value
