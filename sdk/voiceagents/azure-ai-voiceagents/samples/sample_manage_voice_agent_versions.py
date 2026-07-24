# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: sample_manage_voice_agent_versions.py

DESCRIPTION:
    This sample demonstrates working with voice-agent versions. Voice agents are
    immutable: every create or update produces a new version. This sample creates
    an agent, adds a new version to it, lists the versions, and reads a single
    version back.

USAGE:
    python sample_manage_voice_agent_versions.py

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

from azure.identity import DefaultAzureCredential

from azure.ai.voiceagents import VoiceAgentsClient
from azure.ai.voiceagents.models import AgentDefinitionOptInKeys, VoiceAgentDefinition


def manage_voice_agent_versions() -> None:
    endpoint = os.environ["AZURE_VOICE_AGENTS_ENDPOINT"]
    model = os.environ.get("AZURE_VOICE_AGENTS_MODEL", "gpt-realtime")
    agent_name = "sample-versioned-voice-agent"
    preview = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

    def definition(instructions: str) -> VoiceAgentDefinition:
        # Each version differs only by its instructions; the rest is identical.
        return VoiceAgentDefinition(model_type="managed", model=model, instructions=instructions)

    with VoiceAgentsClient(endpoint=endpoint, credential=DefaultAzureCredential()) as client:
        # Create the initial agent (this is version 1).
        created = client.voice_agents.create_voice_agent(
            name=agent_name,
            definition=definition("You are a helpful voice assistant."),
            foundry_features=preview,
        )
        print(f"Created agent '{created.name}', latest version: {created.versions.latest.version}")

        # Create a new version with updated instructions.
        new_version = client.voice_agents.create_voice_agent_version(
            agent_name,
            definition=definition("You are a helpful voice assistant. Always greet the caller by name."),
            description="Added a personalized greeting.",
            foundry_features=preview,
        )
        print(f"Created new version: {new_version.version}")

        # Create a draft version. Drafts are recorded but excluded from the default
        # 'latest' resolution and from version listings unless include_drafts=True.
        draft_version = client.voice_agents.create_voice_agent_version(
            agent_name,
            definition=definition("You are a helpful voice assistant. Experimental draft persona."),
            description="Candidate persona under review.",
            draft=True,
            foundry_features=preview,
        )
        print(f"Created draft version: {draft_version.version}")

        # List released versions (drafts excluded by default).
        print(f"Released versions of '{agent_name}':")
        for version in client.voice_agents.list_voice_agent_versions(agent_name, foundry_features=preview):
            print(f"  - version {version.version} (created_at={version.created_at})")

        # List including drafts.
        print(f"All versions of '{agent_name}' (including drafts):")
        for version in client.voice_agents.list_voice_agent_versions(
            agent_name, include_drafts=True, foundry_features=preview
        ):
            print(f"  - version {version.version} (draft={version.draft})")

        # Read a single version back.
        fetched = client.voice_agents.get_voice_agent_version(agent_name, new_version.version, foundry_features=preview)
        print(f"Fetched version {fetched.version}: {fetched.definition.instructions}")

        # Clean up.
        client.voice_agents.delete_voice_agent(agent_name, foundry_features=preview)
        print(f"Deleted agent: {agent_name}")


if __name__ == "__main__":
    manage_voice_agent_versions()
