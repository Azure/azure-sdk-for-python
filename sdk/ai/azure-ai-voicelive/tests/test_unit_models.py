# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

from azure.ai.voicelive.models import (
    AssistantMessageItem,
    AzureCustomVoice,
    AzurePersonalVoice,
    AzureStandardVoice,
    AzureVoiceType,
    InputAudioContentPart,
    InputTextContentPart,
    MessageContentPart,
    MessageItem,
    MessageRole,
    OpenAIVoice,
    OutputTextContentPart,
    PersonalVoiceModels,
    RequestSession,
    ResponseSession,
    SystemMessageItem,
    UserMessageItem,
    ItemParamStatus,
    OpenAIVoiceName,
)


class TestAzureVoiceModels:
    """Test Azure voice model classes."""

    def test_azure_custom_voice(self):
        """Test AzureCustomVoice model."""
        voice = AzureCustomVoice(name="custom-voice", endpoint_id="endpoint-123")

        assert voice.type == AzureVoiceType.AZURE_CUSTOM
        assert voice.name == "custom-voice"
        assert voice.endpoint_id == "endpoint-123"

    def test_azure_standard_voice(self):
        """Test AzureStandardVoice model."""
        voice = AzureStandardVoice(name="standard-voice")

        assert voice.type == AzureVoiceType.AZURE_STANDARD
        assert voice.name == "standard-voice"
        assert voice.temperature is None

    def test_azure_standard_voice_with_params(self):
        """Test AzureStandardVoice with optional parameters."""
        voice = AzureStandardVoice(
            name="standard-voice", temperature=0.7, style="friendly", pitch="+10%", rate="+20%", volume="-5%"
        )

        assert voice.temperature == 0.7
        assert voice.style == "friendly"
        assert voice.pitch == "+10%"
        assert voice.rate == "+20%"
        assert voice.volume == "-5%"

    def test_azure_personal_voice(self):
        """Test AzurePersonalVoice model."""
        voice = AzurePersonalVoice(name="personal-voice", model=PersonalVoiceModels.PHOENIX_LATEST_NEURAL)

        assert voice.type == AzureVoiceType.AZURE_PERSONAL
        assert voice.name == "personal-voice"
        assert voice.model == PersonalVoiceModels.PHOENIX_LATEST_NEURAL

    def test_azure_personal_voice_with_temperature(self):
        """Test AzurePersonalVoice with temperature parameter."""
        voice = AzurePersonalVoice(
            name="personal-voice", temperature=0.5, model=PersonalVoiceModels.DRAGON_LATEST_NEURAL
        )

        assert voice.temperature == 0.5
        assert voice.model == PersonalVoiceModels.DRAGON_LATEST_NEURAL


class TestOpenAIVoice:
    """Test OpenAIVoice model."""

    def test_openai_voice_creation(self):
        """Test creating OpenAI voice model."""
        voice = OpenAIVoice(name=OpenAIVoiceName.ALLOY)

        assert voice.type == "openai"
        assert voice.name == OpenAIVoiceName.ALLOY

    def test_openai_voice_with_string(self):
        """Test creating OpenAI voice with string name."""
        voice = OpenAIVoice(name="shimmer")

        assert voice.type == "openai"
        assert voice.name == "shimmer"


class TestMessageContentParts:
    """Test message content part models."""

    def test_input_text_content_part(self):
        """Test InputTextContentPart model."""
        content = InputTextContentPart(text="Hello, world!")

        assert content.type == "input_text"
        assert content.text == "Hello, world!"

    def test_input_audio_content_part(self):
        """Test InputAudioContentPart model."""
        audio_data = b"fake audio data"
        content = InputAudioContentPart(audio=audio_data)

        assert content.type == "input_audio"
        # Audio data gets base64 encoded
        import base64

        expected_audio = base64.b64encode(audio_data).decode("utf-8")
        assert content.audio == expected_audio

    def test_output_text_content_part(self):
        """Test OutputTextContentPart model."""
        content = OutputTextContentPart(text="Response text")

        assert content.type == "text"
        assert content.text == "Response text"

    def test_message_content_part_inheritance(self):
        """Test that content parts inherit from MessageContentPart."""
        text_content = InputTextContentPart(text="test")
        audio_content = InputAudioContentPart(audio=b"test")
        output_content = OutputTextContentPart(text="test")

        assert isinstance(text_content, MessageContentPart)
        assert isinstance(audio_content, MessageContentPart)
        assert isinstance(output_content, MessageContentPart)


class TestMessageItems:
    """Test message item models."""

    def test_user_message_item(self):
        """Test UserMessageItem model."""
        content = [InputTextContentPart(text="Hello")]
        message = UserMessageItem(content=content)

        assert message.role == MessageRole.USER
        assert message.type == "message"
        assert len(message.content) == 1
        assert message.content[0].text == "Hello"

    def test_user_message_item_with_id(self):
        """Test UserMessageItem with optional ID."""
        content = [InputTextContentPart(text="Hello")]
        message = UserMessageItem(id="msg-123", content=content, status=ItemParamStatus.COMPLETED)

        assert message.id == "msg-123"
        assert message.status == ItemParamStatus.COMPLETED

    def test_assistant_message_item(self):
        """Test AssistantMessageItem model."""
        content = [OutputTextContentPart(text="Hi there!")]
        message = AssistantMessageItem(content=content)

        assert message.role == MessageRole.ASSISTANT
        assert message.type == "message"
        assert len(message.content) == 1
        assert message.content[0].text == "Hi there!"

    def test_system_message_item(self):
        """Test SystemMessageItem model."""
        content = [InputTextContentPart(text="You are a helpful assistant.")]
        message = SystemMessageItem(content=content)

        assert message.role == MessageRole.SYSTEM
        assert message.type == "message"
        assert len(message.content) == 1
        assert message.content[0].text == "You are a helpful assistant."

    def test_message_item_polymorphism(self):
        """Test that all message items are instances of MessageItem."""
        user_content = [InputTextContentPart(text="User message")]
        assistant_content = [OutputTextContentPart(text="Assistant response")]
        system_content = [InputTextContentPart(text="System prompt")]

        user_msg = UserMessageItem(content=user_content)
        assistant_msg = AssistantMessageItem(content=assistant_content)
        system_msg = SystemMessageItem(content=system_content)

        assert isinstance(user_msg, MessageItem)
        assert isinstance(assistant_msg, MessageItem)
        assert isinstance(system_msg, MessageItem)

    def test_mixed_content_types(self):
        """Test message with mixed content types."""
        mixed_content = [InputTextContentPart(text="Text content"), InputAudioContentPart(audio=b"audio data")]
        message = UserMessageItem(content=mixed_content)

        assert len(message.content) == 2
        assert message.content[0].type == "input_text"
        assert message.content[1].type == "input_audio"


class TestRequestSession:
    """Test RequestSession model."""

    def test_basic_request_session(self):
        """Test creating a basic request session."""
        session = RequestSession(model="gpt-4o-realtime-preview")

        assert session.model == "gpt-4o-realtime-preview"
        assert session.modalities is None
        assert session.voice is None

    def test_request_session_with_voice(self):
        """Test request session with voice configuration."""
        voice = OpenAIVoice(name=OpenAIVoiceName.ALLOY)
        session = RequestSession(model="gpt-4o-realtime-preview", voice=voice, instructions="Be helpful and concise")

        assert session.voice == voice
        assert session.instructions == "Be helpful and concise"

    def test_request_session_with_modalities(self):
        """Test request session with modalities."""
        from azure.ai.voicelive.models import Modality

        session = RequestSession(model="gpt-4o-realtime-preview", modalities=[Modality.TEXT, Modality.AUDIO])

        assert len(session.modalities) == 2
        assert Modality.TEXT in session.modalities
        assert Modality.AUDIO in session.modalities

    def test_request_session_with_temperature(self):
        """Test request session with temperature settings."""
        session = RequestSession(model="gpt-4o-realtime-preview", temperature=0.7, max_response_output_tokens=1000)

        assert session.temperature == 0.7
        assert session.max_response_output_tokens == 1000


class TestResponseSession:
    """Test ResponseSession model."""

    def test_response_session_with_agent(self):
        """Test response session with agent configuration."""
        session = ResponseSession(model="gpt-4o-realtime-preview", id="session-789")

        assert session.id == "session-789"
        assert session.model == "gpt-4o-realtime-preview"


class TestModelValidation:
    """Test model validation and error cases."""

    def test_enum_values_work_correctly(self):
        """Test that enum values work correctly in models."""
        # Test that voice configurations work with proper enums
        from azure.ai.voicelive.models import AzureStandardVoice, AzureVoiceType

        voice = AzureStandardVoice(name="test-voice")
        assert voice.type == AzureVoiceType.AZURE_STANDARD


class TestModelSerialization:
    """Test model serialization capabilities."""

    def test_voice_model_dict_conversion(self):
        """Test converting voice models to dictionaries."""
        voice = AzureStandardVoice(name="test-voice", temperature=0.7)

        # Test that the model has serialization capabilities
        assert hasattr(voice, "__dict__")
        assert voice.name == "test-voice"
        assert voice.temperature == 0.7

    def test_message_item_dict_conversion(self):
        """Test converting message items to dictionaries."""
        content = [InputTextContentPart(text="Test message")]
        message = UserMessageItem(content=content)

        # Test that the model has expected attributes
        assert hasattr(message, "__dict__")
        assert message.role == MessageRole.USER
        assert len(message.content) == 1

    def test_complex_model_structure(self):
        """Test complex model with nested objects."""

        voice = AzurePersonalVoice(name="personal-voice", model=PersonalVoiceModels.PHOENIX_LATEST_NEURAL)

        session = ResponseSession(model="gpt-4o-realtime-preview", voice=voice, id="complex-session")

        # Verify the nested structure
        assert session.voice.name == "personal-voice"
        assert session.voice.model == PersonalVoiceModels.PHOENIX_LATEST_NEURAL
