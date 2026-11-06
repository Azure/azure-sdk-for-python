# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Configure a voice agent with audio settings, speech detection, transcription,
    a local function tool, and a service-managed end-conversation tool.
    MCP and toolbox settings are shown as examples, not executed.

    Use a managed model, or select "self_deployed" to use your own Foundry
    model deployment.

USAGE:
    python sample_voice_agent_with_tools.py

    pip install "azure-ai-projects>=2.7.0" python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (optional) - Managed model or your deployment
       name; defaults to "gpt-realtime". The deprecated FOUNDRY_VOICE_MODEL
       variable is still accepted as a fallback.
    3) FOUNDRY_VOICE_MODEL_TYPE (optional) - "managed" (default) or "self_deployed".
    4) FOUNDRY_VOICE_AGENT_NAME (optional) - Agent name;
       defaults to "sample-voice-agent-with-tools".
"""

import os
from typing import Any, cast

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    RealtimeAudioFormatsAudioPcm,
    VoiceAgentDefinition,
    VoiceAgentFunctionTool,
    VoiceAgentMcpTool,
    VoiceAgentAudioConfig,
    VoiceAgentAudioInputConfig,
    VoiceAgentAudioOutputConfig,
    VoiceAgentEndConversationSystemTool,
    VoiceAgentInputTranscription,
    VoiceAgentInputTranscriptionModel,
    VoiceModelType,
    VoiceOutputModality,
    VoiceAgentServerVadTurnDetection,
    VoiceAgentToolboxTool,
    VoiceType,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
# Keep existing BYOM configurations targeting the caller's deployment.
model = os.environ.get("FOUNDRY_VOICE_AGENT_MODEL") or os.environ.get("FOUNDRY_VOICE_MODEL") or "gpt-realtime"
# Choose a managed model or your own deployment; the service selects its protocol.
model_type = os.environ.get("FOUNDRY_VOICE_MODEL_TYPE") or VoiceModelType.MANAGED
agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or "sample-voice-agent-with-tools"

# A client-executed tool: the service forwards the function call to your app,
# and your app returns the result over the live session.
get_weather = VoiceAgentFunctionTool(
    name="get_weather",
    description="Get the current weather for a city.",
    parameters=cast(
        Any,
        {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name, e.g. Seattle."}},
            "required": ["city"],
        },
    ),
)

# A service-managed control tool: the platform can end the call on the agent's behalf.
end_call = VoiceAgentEndConversationSystemTool()

# An MCP tool is executed by the service against a remote MCP server you own.
# It references an external server, so it is constructed here for illustration
# and not attached below. Provide server_url; connector and tunnel IDs are not supported.
_example_mcp_tool = VoiceAgentMcpTool(
    server_label="my-mcp-server",
    server_url="https://example.com/mcp",
    require_approval="never",
)

# A toolbox tool references a versioned Foundry toolbox you have created. It is
# constructed here for illustration; attach it only if the toolbox exists.
_example_toolbox_tool = VoiceAgentToolboxTool(toolbox_name="my-toolbox", toolbox_version="1")

definition = VoiceAgentDefinition(
    model_type=model_type,
    model=model,
    instructions="You are a helpful voice assistant. Use tools when they help answer the caller.",
    audio=VoiceAgentAudioConfig(
        # Input (microphone) side: 24 kHz PCM, server-side VAD so the agent
        # auto-responds when the caller stops speaking, plus input-audio
        # transcription so user speech is transcribed.
        input=VoiceAgentAudioInputConfig(
            format=RealtimeAudioFormatsAudioPcm(rate=24000),
            turn_detection=VoiceAgentServerVadTurnDetection(
                threshold=0.5,
                prefix_padding_ms=300,
                silence_duration_ms=500,
            ),
            transcription=VoiceAgentInputTranscription(model=VoiceAgentInputTranscriptionModel.WHISPER1),
        ),
        # Output (agent speech) side: the voice the agent speaks with.
        output=VoiceAgentAudioOutputConfig(voice="en-US-AvaNeural", voice_type=VoiceType.AZURE_STANDARD),
    ),
    output_modalities=[VoiceOutputModality.AUDIO],
    # Attach the self-contained tools. `_example_mcp_tool` and `_example_toolbox_tool`
    # reference external resources you must own, so they are left out here.
    tools=[get_weather, end_call],
    store=True,
)

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
):
    created_version = None
    try:
        created_version = project_client.agents.create_version(agent_name=agent_name, definition=definition)
        print(f"Created voice agent '{agent_name}' (model_type={model_type}, model={model})")

        agent_version = project_client.agents.get_version(agent_name=agent_name, agent_version=created_version.version)
        tools = agent_version.definition.tools or []  # type: ignore[attr-defined]
        print(f"Configured {len(tools)} tool(s):")
        for tool in tools:
            # `name` isn't declared on every tool kind (e.g. MCP tools have no `name`),
            # so fall back to a placeholder for kinds that don't define it.
            print(f"  - {tool.type}: {getattr(tool, 'name', '(unnamed)')}")
    finally:
        if created_version is not None:
            project_client.agents.delete_version(agent_name=agent_name, agent_version=created_version.version)
            print(f"Deleted voice agent version: {created_version.version}")
