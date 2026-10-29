# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Create published and draft versions of a voice agent, list them, and read
    their settings. Each create_version call makes a new version rather than
    changing an existing one.

USAGE:
    python sample_voice_agent_versions.py

    pip install "azure-ai-projects>=2.7.0" python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (optional) - Managed Realtime model;
       defaults to "gpt-realtime".
    3) FOUNDRY_VOICE_AGENT_NAME (optional) - Agent name;
       defaults to "sample-versioned-voice-agent".
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import VoiceAgentDefinition, VoiceModelType

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model = os.environ.get("FOUNDRY_VOICE_AGENT_MODEL") or "gpt-realtime"
agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or "sample-versioned-voice-agent"


def make_definition(instructions: str) -> VoiceAgentDefinition:
    # Each version differs only by its instructions; the rest is identical.
    return VoiceAgentDefinition(model_type=VoiceModelType.MANAGED, model=model, instructions=instructions)


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
):
    created_versions = []
    try:
        # Create the initial agent (this is version 1).
        created = project_client.agents.create_version(
            agent_name=agent_name,
            definition=make_definition("You are a helpful voice assistant."),
        )
        created_versions.append(created)
        print(f"Created agent '{agent_name}', version: {created.version}")

        # Create a new version with updated instructions.
        new_version = project_client.agents.create_version(
            agent_name=agent_name,
            definition=make_definition("You are a helpful voice assistant. Always greet the caller by name."),
            description="Added a personalized greeting.",
        )
        created_versions.append(new_version)
        print(f"Created new version: {new_version.version}")

        # Create a draft version. Drafts are recorded but excluded from the default
        # 'latest' resolution and from version listings unless include_drafts=True.
        draft_version = project_client.agents.create_version(
            agent_name=agent_name,
            definition=make_definition("You are a helpful voice assistant. Experimental draft persona."),
            description="Candidate persona under review.",
            draft=True,
        )
        created_versions.append(draft_version)
        print(f"Created draft version: {draft_version.version}")

        # List released versions (drafts excluded by default).
        print(f"Released versions of '{agent_name}':")
        for version in project_client.agents.list_versions(agent_name=agent_name):
            print(f"  - version {version.version} (created_at={version.created_at})")

        # List including drafts.
        print(f"All versions of '{agent_name}' (including drafts):")
        for version in project_client.agents.list_versions(agent_name=agent_name, include_drafts=True):
            print(f"  - version {version.version} (draft={version.draft})")

        # Read a single version back.
        fetched = project_client.agents.get_version(agent_name=agent_name, agent_version=new_version.version)
        print(f"Fetched version {fetched.version}: {fetched.definition.instructions}")  # type: ignore[attr-defined]
    finally:
        for version in reversed(created_versions):
            project_client.agents.delete_version(agent_name=agent_name, agent_version=version.version)
            print(f"Deleted agent version: {version.version}")
