# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Unit tests for model construction and serialization round-trips.

All tests are offline: they build models in memory and assert on the JSON
shape produced by ``as_dict()`` / accepted by mapping-based construction.
"""

from azure.ai.voiceagents.models import (
    AzureVoice,
    FunctionTool,
    ServerVadTurnDetection,
    VoiceAgentDefinition,
    VoiceAudioConfig,
    VoiceAudioFormat,
    VoiceAudioInputConfig,
    VoiceAudioOutputConfig,
    VoiceInputTranscription,
    VoiceModelType,
    VoiceOutputModality,
    VoiceSystemTool,
    VoiceSystemToolName,
)


def test_voice_agent_definition_minimal():
    definition = VoiceAgentDefinition(
        model_type=VoiceModelType.MANAGED,
        model="gpt-realtime",
        instructions="Be helpful.",
    )

    assert definition.model_type == "managed"
    assert definition.model == "gpt-realtime"
    assert definition.instructions == "Be helpful."
    # ``kind`` is the discriminator and is always "voice".
    assert definition.kind == "voice"


def test_voice_agent_definition_as_dict_round_trip():
    definition = VoiceAgentDefinition(
        model_type="managed",
        model="gpt-realtime",
        instructions="Hello",
        output_modalities=[VoiceOutputModality.AUDIO],
        store=True,
    )

    data = definition.as_dict()
    assert data["model_type"] == "managed"
    assert data["model"] == "gpt-realtime"
    assert data["store"] is True
    assert data["output_modalities"] == ["audio"]

    # Rebuild from the emitted mapping and confirm equality.
    rebuilt = VoiceAgentDefinition(data)
    assert rebuilt.model == definition.model
    assert rebuilt.store is True
    assert rebuilt == definition


def test_azure_voice_construction():
    voice = AzureVoice(type="azure-standard", name="en-US-AvaNeural")
    assert voice.type == "azure-standard"
    assert voice.name == "en-US-AvaNeural"
    assert voice.as_dict() == {"type": "azure-standard", "name": "en-US-AvaNeural"}


def test_output_config_accepts_plain_string_voice():
    # A bare string voice denotes a built-in (OpenAI) voice.
    output = VoiceAudioOutputConfig(voice="alloy")
    assert output.voice == "alloy"


def test_output_config_accepts_azure_voice():
    output = VoiceAudioOutputConfig(voice=AzureVoice(type="azure-standard", name="en-US-AvaNeural"))
    assert isinstance(output.voice, AzureVoice)
    assert output.voice.name == "en-US-AvaNeural"


def test_audio_config_input_round_trip():
    audio = VoiceAudioConfig(
        input=VoiceAudioInputConfig(
            format=VoiceAudioFormat(type="audio/pcm", rate=24000),
            turn_detection=ServerVadTurnDetection(threshold=0.5),
            transcription=VoiceInputTranscription(model="whisper-1"),
        )
    )

    data = audio.as_dict()
    assert data["input"]["format"]["type"] == "audio/pcm"
    assert data["input"]["format"]["rate"] == 24000
    assert data["input"]["transcription"]["model"] == "whisper-1"


def test_function_tool_discriminator_is_set():
    tool = FunctionTool(
        name="get_weather",
        parameters={"type": "object", "properties": {}},
        strict=True,
    )
    assert tool.type == "function"
    assert tool.name == "get_weather"
    assert tool.strict is True
    assert tool.as_dict()["type"] == "function"


def test_system_tool_discriminator_is_set():
    tool = VoiceSystemTool(name=VoiceSystemToolName.END_CONVERSATION)
    assert tool.type == "system"
    assert tool.name == "end_conversation"


def test_definition_with_tools_serializes_each_tool_type():
    definition = VoiceAgentDefinition(
        model_type="managed",
        model="gpt-realtime",
        instructions="Hi",
        tools=[
            FunctionTool(name="get_weather", parameters={"type": "object"}, strict=True),
            VoiceSystemTool(name=VoiceSystemToolName.END_CONVERSATION),
        ],
    )

    tool_types = [tool["type"] for tool in definition.as_dict()["tools"]]
    assert tool_types == ["function", "system"]
