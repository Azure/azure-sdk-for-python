# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: sample_create_voice_agent_with_tools.py

DESCRIPTION:
    This sample demonstrates the richer parts of a voice agent definition that the
    basic create sample leaves out:

    * Input (microphone) audio configuration: audio format, server-side turn
      detection (VAD), input-audio transcription, and noise reduction.
    * Tools the agent may use during a live session: a client-executed `function`
      tool, a service-managed `system` control tool, and (shown as constructed
      objects) `mcp` and `toolbox` tools.
    * Bring-your-own-model (BYOM): set `model_type="self_deployed"` to point the
      agent at your own Foundry model deployment instead of a service-managed model.

    The tools and audio settings are session defaults baked into the agent; the live
    realtime session that actually invokes them is established through a separate
    connect operation that is not part of this client library.

USAGE:
    python sample_create_voice_agent_with_tools.py

    Set these environment variables before running the sample:
    1) AZURE_VOICE_AGENTS_ENDPOINT - the Foundry project endpoint, in the form
       https://<account>.services.ai.azure.com/api/projects/<project>
    2) AZURE_VOICE_AGENTS_MODEL - optional. The realtime model (managed) or the
       Foundry deployment name (BYOM). Defaults to "gpt-realtime".
    3) AZURE_VOICE_AGENTS_MODEL_TYPE - optional. "managed" (default) for a
       service-hosted model, or "self_deployed" to bring your own deployment.

    The sample authenticates with DefaultAzureCredential, so sign in first
    (for example, with `az login`).
"""

import os
from typing import Final

from azure.identity import DefaultAzureCredential

from azure.ai.voiceagents import VoiceAgentsClient
from azure.ai.voiceagents.models import (
    AgentDefinitionOptInKeys,
    AzureVoice,
    FunctionTool,
    MCPTool,
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
    VoiceToolboxTool,
)


def create_voice_agent_with_tools() -> None:
    endpoint = os.environ["AZURE_VOICE_AGENTS_ENDPOINT"]
    model = os.environ.get("AZURE_VOICE_AGENTS_MODEL", "gpt-realtime")
    # "managed" runs a service-hosted model; "self_deployed" (BYOM) uses your own
    # Foundry deployment named by `model`. The service derives whether the model is
    # realtime or cascaded; you don't set that here.
    model_type = os.environ.get("AZURE_VOICE_AGENTS_MODEL_TYPE", VoiceModelType.MANAGED)
    agent_name = "sample-voice-agent-with-tools"

    # Voice agent preview operations require this feature-flag opt-in.
    preview: Final = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

    # A client-executed tool: the service forwards the function call to your app,
    # and your app returns the result over the live session.
    get_weather = FunctionTool(
        name="get_weather",
        description="Get the current weather for a city.",
        parameters={
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name, e.g. Seattle."}},
            "required": ["city"],
        },
        strict=True,
    )

    # A service-managed control tool: the platform can end the call on the agent's behalf.
    end_call = VoiceSystemTool(name=VoiceSystemToolName.END_CONVERSATION)

    # An MCP tool is executed by the service against a remote MCP server you own.
    # It references an external server, so it is constructed here for illustration
    # and not attached below. Provide one of server_url, connector_id, or tunnel_id.
    _example_mcp_tool = MCPTool(
        server_label="my-mcp-server",
        server_url="https://example.com/mcp",
        require_approval="never",
    )

    # A toolbox tool references a versioned Foundry toolbox you have created. It is
    # constructed here for illustration; attach it only if the toolbox exists.
    _example_toolbox_tool = VoiceToolboxTool(toolbox_name="my-toolbox", toolbox_version="1")

    definition = VoiceAgentDefinition(
        model_type=model_type,
        model=model,
        instructions="You are a helpful voice assistant. Use tools when they help answer the caller.",
        audio=VoiceAudioConfig(
            # Input (microphone) side: 24 kHz PCM, server-side VAD so the agent
            # auto-responds when the caller stops speaking, plus input-audio
            # transcription so user speech is transcribed.
            input=VoiceAudioInputConfig(
                format=VoiceAudioFormat(type="audio/pcm", rate=24000),
                turn_detection=ServerVadTurnDetection(
                    threshold=0.5,
                    prefix_padding_ms=300,
                    silence_duration_ms=500,
                ),
                transcription=VoiceInputTranscription(model="whisper-1"),
            ),
            # Output (agent speech) side: the voice the agent speaks with. Pass an
            # AzureVoice for an Azure neural voice, or a plain string such as "alloy"
            # for a built-in OpenAI voice (realtime models only):
            #     output=VoiceAudioOutputConfig(voice="alloy"),
            output=VoiceAudioOutputConfig(voice=AzureVoice(type="azure-standard", name="en-US-AvaNeural")),
        ),
        output_modalities=[VoiceOutputModality.AUDIO],
        # Attach the self-contained tools. `_example_mcp_tool` and `_example_toolbox_tool`
        # reference external resources you must own, so they are left out here.
        tools=[get_weather, end_call],
        store=True,
    )

    with VoiceAgentsClient(endpoint=endpoint, credential=DefaultAzureCredential()) as client:
        created = client.voice_agents.create_voice_agent(
            name=agent_name,
            definition=definition,
            description="Voice agent with tools and input-audio config (azure-ai-voiceagents sample).",
            foundry_features=preview,
        )
        print(f"Created voice agent: {created.name} (model_type={model_type}, model={model})")

        agent = client.voice_agents.get_voice_agent(agent_name, foundry_features=preview)
        tools = agent.versions.latest.definition.tools or []
        print(f"Configured {len(tools)} tool(s):")
        for tool in tools:
            # Tools belong to an open union, so on read they surface as mappings
            # keyed by their wire fields (``type`` and, for most kinds, ``name``).
            print(f"  - {tool['type']}: {tool.get('name', '(unnamed)')}")

        client.voice_agents.delete_voice_agent(agent_name, foundry_features=preview)
        print(f"Deleted voice agent: {agent_name}")


if __name__ == "__main__":
    create_voice_agent_with_tools()
