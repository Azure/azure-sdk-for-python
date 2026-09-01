# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates the voice-agent management lifecycle using the
    unified Agents API in the Microsoft Foundry Python SDK (azure-ai-projects):
    creating a voice agent (with an audio/voice configuration and conversation
    storage enabled), retrieving it, listing the voice agents in the project,
    creating a new version, disabling/enabling it, and deleting it.

    Voice agents are exposed through `project_client.agents` with
    `kind="voice"`, the same surface used for prompt, workflow, hosted, and
    external agents.

USAGE:
    python sample_voice_agent_basic.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_VOICE_MODEL - Optional. The realtime model deployment name.
       Defaults to "gpt-realtime".
    3) FOUNDRY_VOICE_AGENT_NAME - Optional. The name of the voice agent. If not
       set, defaults to "MyVoiceAgent".
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentKind,
    VoiceAgentDefinition,
    VoiceAgentAudioConfig,
    VoiceAgentAudioOutputConfig,
    VoiceModelType,
    VoiceOutputModality,
    VoiceType,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model = os.environ.get("FOUNDRY_VOICE_MODEL") or "gpt-realtime"
agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or "MyVoiceAgent"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
):
    try:
        definition = VoiceAgentDefinition(
            # `managed` uses a service-hosted model; use `self_deployed` with a Foundry
            # deployment name to bring your own model.
            model_type=VoiceModelType.MANAGED,
            model=model,
            instructions="You are a friendly voice assistant. Keep replies short and natural.",
            audio=VoiceAgentAudioConfig(
                output=VoiceAgentAudioOutputConfig(voice="en-US-AvaNeural", voice_type=VoiceType.AZURE_STANDARD),
            ),
            output_modalities=[VoiceOutputModality.AUDIO],
            # Persist conversations so the transcript and audio can be read back later
            # (see sample_voice_agent_read_conversation.py). Defaults to False, which stores nothing.
            store=True,
        )

        created_version = project_client.agents.create_version(agent_name=agent_name, definition=definition)
        print(f"Created voice agent '{agent_name}', version: {created_version.version}")

        agent = project_client.agents.get(agent_name=agent_name)
        print(f"Retrieved voice agent: {agent.name} (state={agent.state})")

        print("Voice agents in this project:")
        for item in project_client.agents.list(kind=AgentKind.VOICE):
            print(f"  - {item.name}")

        # Each update produces a new immutable version.
        updated_version = project_client.agents.create_version(
            agent_name=agent_name,
            definition=VoiceAgentDefinition(
                model_type=VoiceModelType.MANAGED,
                model=model,
                instructions="You are a friendly voice assistant. Always greet the caller warmly.",
                audio=definition.audio,
                output_modalities=definition.output_modalities,
                store=definition.store,
            ),
            description="Updated instructions.",
        )
        print(f"Updated voice agent to version: {updated_version.version}")

        # Disable the agent so its endpoint rejects new requests, then re-enable it.
        project_client.agents.disable(agent_name=agent_name)
        print("Disabled voice agent")
        project_client.agents.enable(agent_name=agent_name)
        print("Enabled voice agent")
    finally:
        project_client.agents.delete(agent_name=agent_name)
        print(f"Deleted voice agent: {agent_name}")
