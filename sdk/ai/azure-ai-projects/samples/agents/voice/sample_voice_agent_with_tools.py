# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates the richer parts of a voice agent definition:

    * Input (microphone) audio configuration: audio format, server-side turn
      detection (VAD), input-audio transcription.
    * Tools the agent may use during a live session: a client-executed
      `function` tool and a service-managed `system` control tool (`mcp` and
      `toolbox` tools are shown as constructed objects for illustration).
    * Bring-your-own-model (BYOM): set `model_type="self_deployed"` to point
      the agent at your own Foundry model deployment instead of a
      service-managed model.

USAGE:
    python sample_voice_agent_with_tools.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_VOICE_MODEL - Optional. The realtime model (managed) or the
       Foundry deployment name (BYOM). Defaults to "gpt-realtime".
    3) FOUNDRY_VOICE_MODEL_TYPE - Optional. "managed" (default) for a
       service-hosted model, or "self_deployed" to bring your own deployment.
"""

import os
from typing import Any, cast

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    RealtimeAudioFormatsAudioPcm,
    RealtimeFunctionTool,
    ToolType,
    VoiceAgentDefinition,
    VoiceAgentMcpTool,
    VoiceAgentAudioConfig,
    VoiceAgentAudioInputConfig,
    VoiceAgentAudioOutputConfig,
    VoiceAgentInputTranscription,
    VoiceAgentInputTranscriptionModel,
    VoiceModelType,
    VoiceOutputModality,
    VoiceAgentServerVadTurnDetection,
    VoiceAgentSystemTool,
    VoiceAgentSystemToolName,
    VoiceAgentToolboxTool,
    VoiceType,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model = os.environ.get("FOUNDRY_VOICE_MODEL") or "gpt-realtime"
# "managed" runs a service-hosted model; "self_deployed" (BYOM) uses your own
# Foundry deployment named by `model`. The service derives whether the model is
# realtime or cascaded; you don't set that here.
model_type = os.environ.get("FOUNDRY_VOICE_MODEL_TYPE") or VoiceModelType.MANAGED
agent_name = "sample-voice-agent-with-tools"

# A client-executed tool: the service forwards the function call to your app,
# and your app returns the result over the live session.
get_weather = RealtimeFunctionTool(
    type="function",
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
end_call = VoiceAgentSystemTool(name=VoiceAgentSystemToolName.END_CONVERSATION)

# An MCP tool is executed by the service against a remote MCP server you own.
# It references an external server, so it is constructed here for illustration
# and not attached below. Provide one of server_url, connector_id, or tunnel_id.
_example_mcp_tool = VoiceAgentMcpTool(
    type=ToolType.MCP,
    server_label="my-mcp-server",
    server_url="https://example.com/mcp",
    require_approval="never",
)  # type: ignore[call-overload]

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
    tools=[get_weather, end_call],  # type: ignore[list-item]
    store=True,
)

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
):
    try:
        created_version = project_client.agents.create_version(agent_name=agent_name, definition=definition)
        print(f"Created voice agent '{agent_name}' (model_type={model_type}, model={model})")

        agent_version = project_client.agents.get_version(agent_name=agent_name, agent_version=created_version.version)
        tools = agent_version.definition.tools or []  # type: ignore[attr-defined]
        print(f"Configured {len(tools)} tool(s):")
        for tool in tools:
            # Tools belong to an open union, so on read they surface as mappings
            # keyed by their wire fields (``type`` and, for most kinds, ``name``).
            print(f"  - {tool['type']}: {tool.get('name', '(unnamed)')}")
    finally:
        project_client.agents.delete(agent_name=agent_name)
        print(f"Deleted voice agent: {agent_name}")
