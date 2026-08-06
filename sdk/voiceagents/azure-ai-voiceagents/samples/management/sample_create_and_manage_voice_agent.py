# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: sample_create_and_manage_voice_agent.py

DESCRIPTION:
    This sample demonstrates the voice-agent management lifecycle over the HTTP
    surface: creating a voice agent (with an audio/voice configuration and
    conversation storage enabled), retrieving it, listing the agents in the
    project, updating it, disabling/enabling it, and deleting it.

USAGE:
    python sample_create_and_manage_voice_agent.py

    Set the environment variable before running the sample:
    1) AZURE_VOICE_AGENTS_ENDPOINT - the Foundry project endpoint, in the form
       https://<account>.services.ai.azure.com/api/projects/<project>

    Optional:
    2) AZURE_VOICE_AGENTS_MODEL - the realtime model deployment to use.
       Defaults to "gpt-realtime".

    The sample authenticates with DefaultAzureCredential, so sign in first
    (for example, with `az login`).
"""

import os
from typing import Final

from azure.identity import DefaultAzureCredential

from azure.ai.voiceagents import VoiceAgentsClient
from azure.ai.voiceagents.models import (
    AgentDefinitionOptInKeys,
    AzureStandardVoice,
    VoiceAgentDefinition,
    VoiceAudioConfig,
    VoiceAudioOutputConfig,
    VoiceOutputModality,
)


def create_and_manage_voice_agent() -> None:
    endpoint = os.environ["AZURE_VOICE_AGENTS_ENDPOINT"]
    model = os.environ.get("AZURE_VOICE_AGENTS_MODEL", "gpt-realtime")
    agent_name = "sample-voice-agent"

    # Voice agent preview operations require this feature-flag opt-in.
    preview: Final = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

    definition = VoiceAgentDefinition(
        # `managed` uses a service-hosted model; use `self_deployed` with a Foundry
        # deployment name to bring your own model.
        model_type="managed",
        model=model,
        instructions="You are a friendly voice assistant. Keep replies short and natural.",
        audio=VoiceAudioConfig(
            output=VoiceAudioOutputConfig(voice=AzureStandardVoice(name="en-US-AvaNeural")),
        ),
        output_modalities=[VoiceOutputModality.AUDIO],
        # Persist conversations so the transcript and audio can be read back later
        # (see sample_read_conversation.py). Defaults to False, which stores nothing.
        store=True,
    )

    with VoiceAgentsClient(endpoint=endpoint, credential=DefaultAzureCredential()) as client:
        created = client.voice_agents.create_voice_agent(
            name=agent_name,
            definition=definition,
            description="Created by the azure-ai-voiceagents sample.",
            foundry_features=preview,
        )
        print(f"Created voice agent: {created.name}")

        agent = client.voice_agents.get_voice_agent(agent_name, foundry_features=preview)
        print(f"Retrieved voice agent: {agent.name}")

        print("Voice agents in this project:")
        for item in client.voice_agents.list_voice_agents(foundry_features=preview):
            print(f"  - {item.name}")

        # Update the agent. Each update that changes the definition produces a new version.
        # Preserve the audio and output-modality configuration from the original
        # definition so the new version keeps the same voice behavior.
        updated = client.voice_agents.update_voice_agent(
            agent_name,
            definition=VoiceAgentDefinition(
                model_type="managed",
                model=model,
                instructions="You are a friendly voice assistant. Always greet the caller warmly.",
                audio=definition.audio,
                output_modalities=definition.output_modalities,
                store=definition.store,
            ),
            description="Updated instructions.",
            foundry_features=preview,
        )
        print(f"Updated voice agent to version: {updated.versions.latest.version}")

        # Disable the agent so its endpoint rejects new requests, then re-enable it.
        client.voice_agents.disable_voice_agent(agent_name, foundry_features=preview)
        print("Disabled voice agent")
        client.voice_agents.enable_voice_agent(agent_name, foundry_features=preview)
        print("Enabled voice agent")

        client.voice_agents.delete_voice_agent(agent_name, foundry_features=preview)
        print(f"Deleted voice agent: {agent_name}")


if __name__ == "__main__":
    create_and_manage_voice_agent()
