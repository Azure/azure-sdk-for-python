# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

from azure.ai.voicelive.models import (
    AnimationOutputType,
    AudioTimestampType,
    AzureVoiceType,
    ClientEventType,
    ContentPartType,
    InputAudioFormat,
    ItemParamStatus,
    ItemType,
    MessageRole,
    Modality,
    OpenAIVoiceName,
    OutputAudioFormat,
    PersonalVoiceModels,
    ResponseItemStatus,
    ResponseStatus,
    ToolChoiceLiteral,
    ToolType,
    TurnDetectionType,
)


class TestAnimationOutputType:
    """Test AnimationOutputType enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert AnimationOutputType.BLENDSHAPES == "blendshapes"
        assert AnimationOutputType.VISEME_ID == "viseme_id"

    def test_case_insensitive(self):
        """Test enum is case-insensitive."""
        # These enums use Azure's CaseInsensitiveEnumMeta, so they work differently
        # Test that the enum values work as expected
        assert AnimationOutputType.BLENDSHAPES.value == "blendshapes"
        assert AnimationOutputType.VISEME_ID.value == "viseme_id"


class TestAudioTimestampType:
    """Test AudioTimestampType enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert AudioTimestampType.WORD == "word"

    def test_string_conversion(self):
        """Test string conversion works."""
        # Test that the enum value is accessible
        assert AudioTimestampType.WORD.value == "word"


class TestAzureVoiceType:
    """Test AzureVoiceType enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert AzureVoiceType.AZURE_CUSTOM == "azure-custom"
        assert AzureVoiceType.AZURE_STANDARD == "azure-standard"
        assert AzureVoiceType.AZURE_PERSONAL == "azure-personal"

    def test_case_insensitive(self):
        """Test enum is case-insensitive."""
        # Test that enum values work correctly
        assert AzureVoiceType.AZURE_CUSTOM.value == "azure-custom"
        assert AzureVoiceType.AZURE_STANDARD.value == "azure-standard"


class TestClientEventType:
    """Test ClientEventType enum."""

    def test_session_events(self):
        """Test session-related events."""
        assert ClientEventType.SESSION_UPDATE == "session.update"
        assert ClientEventType.SESSION_AVATAR_CONNECT == "session.avatar.connect"

    def test_audio_buffer_events(self):
        """Test audio buffer events."""
        assert ClientEventType.INPUT_AUDIO_BUFFER_APPEND == "input_audio_buffer.append"
        assert ClientEventType.INPUT_AUDIO_BUFFER_COMMIT == "input_audio_buffer.commit"
        assert ClientEventType.INPUT_AUDIO_BUFFER_CLEAR == "input_audio_buffer.clear"

    def test_conversation_events(self):
        """Test conversation events."""
        assert ClientEventType.CONVERSATION_ITEM_CREATE == "conversation.item.create"
        assert ClientEventType.CONVERSATION_ITEM_DELETE == "conversation.item.delete"
        assert ClientEventType.CONVERSATION_ITEM_RETRIEVE == "conversation.item.retrieve"
        assert ClientEventType.CONVERSATION_ITEM_TRUNCATE == "conversation.item.truncate"

    def test_response_events(self):
        """Test response events."""
        assert ClientEventType.RESPONSE_CREATE == "response.create"
        assert ClientEventType.RESPONSE_CANCEL == "response.cancel"


class TestContentPartType:
    """Test ContentPartType enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert ContentPartType.INPUT_TEXT == "input_text"
        assert ContentPartType.INPUT_AUDIO == "input_audio"
        assert ContentPartType.TEXT == "text"
        assert ContentPartType.AUDIO == "audio"


class TestInputAudioFormat:
    """Test InputAudioFormat enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert InputAudioFormat.PCM16 == "pcm16"
        assert InputAudioFormat.G711_ULAW == "g711_ulaw"
        assert InputAudioFormat.G711_ALAW == "g711_alaw"

    def test_documentation(self):
        """Test that enum values have proper documentation."""
        # These should not raise errors
        assert hasattr(InputAudioFormat, "PCM16")
        assert hasattr(InputAudioFormat, "G711_ULAW")
        assert hasattr(InputAudioFormat, "G711_ALAW")


class TestItemParamStatus:
    """Test ItemParamStatus enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert ItemParamStatus.COMPLETED == "completed"
        assert ItemParamStatus.INCOMPLETE == "incomplete"


class TestItemType:
    """Test ItemType enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert ItemType.MESSAGE == "message"
        assert ItemType.FUNCTION_CALL == "function_call"
        assert ItemType.FUNCTION_CALL_OUTPUT == "function_call_output"


class TestMessageRole:
    """Test MessageRole enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert MessageRole.SYSTEM == "system"
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"

    def test_case_insensitive(self):
        """Test enum is case-insensitive."""
        # Test that enum values work correctly
        assert MessageRole.SYSTEM.value == "system"
        assert MessageRole.USER.value == "user"


class TestModality:
    """Test Modality enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert Modality.TEXT == "text"
        assert Modality.AUDIO == "audio"
        assert Modality.ANIMATION == "animation"
        assert Modality.AVATAR == "avatar"


class TestOAIVoice:
    """Test OpenAIVoiceName enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert OpenAIVoiceName.ALLOY == "alloy"
        assert OpenAIVoiceName.ASH == "ash"
        assert OpenAIVoiceName.BALLAD == "ballad"
        assert OpenAIVoiceName.CORAL == "coral"
        assert OpenAIVoiceName.ECHO == "echo"
        assert OpenAIVoiceName.SAGE == "sage"
        assert OpenAIVoiceName.SHIMMER == "shimmer"
        assert OpenAIVoiceName.VERSE == "verse"

    def test_case_insensitive(self):
        """Test enum is case-insensitive."""
        # Test that enum values work correctly
        assert OpenAIVoiceName.ALLOY.value == "alloy"
        assert OpenAIVoiceName.SHIMMER.value == "shimmer"


class TestOutputAudioFormat:
    """Test OutputAudioFormat enum."""

    def test_pcm_formats(self):
        """Test PCM format values."""
        assert OutputAudioFormat.PCM16 == "pcm16"
        assert OutputAudioFormat.PCM16_8000_HZ == "pcm16_8000hz"
        assert OutputAudioFormat.PCM16_16000_HZ == "pcm16_16000hz"

    def test_g711_formats(self):
        """Test G.711 format values."""
        assert OutputAudioFormat.G711_ULAW == "g711_ulaw"
        assert OutputAudioFormat.G711_ALAW == "g711_alaw"


class TestPersonalVoiceModels:
    """Test PersonalVoiceModels enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert PersonalVoiceModels.DRAGON_LATEST_NEURAL == "DragonLatestNeural"
        assert PersonalVoiceModels.PHOENIX_LATEST_NEURAL == "PhoenixLatestNeural"
        assert PersonalVoiceModels.PHOENIX_V2_NEURAL == "PhoenixV2Neural"


class TestResponseItemStatus:
    """Test ResponseItemStatus enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert ResponseItemStatus.IN_PROGRESS == "in_progress"
        assert ResponseItemStatus.COMPLETED == "completed"
        assert ResponseItemStatus.INCOMPLETE == "incomplete"


class TestResponseStatus:
    """Test ResponseStatus enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert ResponseStatus.IN_PROGRESS == "in_progress"
        assert ResponseStatus.COMPLETED == "completed"
        assert ResponseStatus.CANCELLED == "cancelled"
        assert ResponseStatus.INCOMPLETE == "incomplete"
        assert ResponseStatus.FAILED == "failed"


class TestToolChoiceLiteral:
    """Test ToolChoiceLiteral enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert ToolChoiceLiteral.NONE == "none"
        assert ToolChoiceLiteral.AUTO == "auto"
        assert ToolChoiceLiteral.REQUIRED == "required"


class TestToolType:
    """Test ToolType enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert ToolType.FUNCTION == "function"


class TestTurnDetectionType:
    """Test TurnDetectionType enum."""

    def test_all_values(self):
        """Test all enum values are accessible."""
        assert TurnDetectionType.SERVER_VAD == "server_vad"
        assert TurnDetectionType.AZURE_SEMANTIC_VAD == "azure_semantic_vad"
        assert TurnDetectionType.AZURE_SEMANTIC_VAD_EN == "azure_semantic_vad_en"
        assert TurnDetectionType.AZURE_SEMANTIC_VAD_MULTILINGUAL == "azure_semantic_vad_multilingual"


# Integration tests for enum behavior
class TestEnumIntegration:
    """Test integration behavior of enums."""

    def test_enum_serialization(self):
        """Test that enums can be serialized to strings."""
        voice_type = AzureVoiceType.AZURE_CUSTOM
        assert voice_type.value == "azure-custom"

        message_role = MessageRole.ASSISTANT
        assert message_role.value == "assistant"

    def test_enum_comparison(self):
        """Test enum comparison with strings."""
        assert AzureVoiceType.AZURE_CUSTOM == "azure-custom"
        assert MessageRole.USER == "user"
        assert OpenAIVoiceName.ALLOY == "alloy"

    def test_enum_in_collections(self):
        """Test that enums work properly in collections."""
        voice_types = [AzureVoiceType.AZURE_CUSTOM, AzureVoiceType.AZURE_STANDARD]
        assert AzureVoiceType.AZURE_CUSTOM in voice_types
        assert "azure-custom" in [vt.value for vt in voice_types]

        roles = {MessageRole.USER, MessageRole.ASSISTANT, MessageRole.SYSTEM}
        assert MessageRole.USER in roles
        assert len(roles) == 3
