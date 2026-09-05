# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates working with voice-agent versions. Agents are
    immutable: every `create_version` call produces a new version. This sample
    creates an agent, adds a new version to it, adds a draft version, lists the
    versions, and reads a single version back.

USAGE:
    python sample_voice_agent_versions.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_VOICE_MODEL - Optional. The realtime model deployment name.
       Defaults to "gpt-realtime".
    3) FOUNDRY_VOICE_AGENT_NAME - Optional. The name of the voice agent. If not
       set, defaults to "sample-versioned-voice-agent".
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import VoiceAgentDefinition, VoiceModelType

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model = os.environ.get("FOUNDRY_VOICE_MODEL") or "gpt-realtime"
agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or "sample-versioned-voice-agent"


def make_definition(instructions: str) -> VoiceAgentDefinition:
    # Each version differs only by its instructions; the rest is identical.
    return VoiceAgentDefinition(model_type=VoiceModelType.MANAGED, model=model, instructions=instructions)


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
):
    try:
        # Create the initial agent (this is version 1).
        created = project_client.agents.create_version(
            agent_name=agent_name,
            definition=make_definition("You are a helpful voice assistant."),
        )
        print(f"Created agent '{agent_name}', version: {created.version}")

        # Create a new version with updated instructions.
        new_version = project_client.agents.create_version(
            agent_name=agent_name,
            definition=make_definition("You are a helpful voice assistant. Always greet the caller by name."),
            description="Added a personalized greeting.",
        )
        print(f"Created new version: {new_version.version}")

        # Create a draft version. Drafts are recorded but excluded from the default
        # 'latest' resolution and from version listings unless include_drafts=True.
        draft_version = project_client.agents.create_version(
            agent_name=agent_name,
            definition=make_definition("You are a helpful voice assistant. Experimental draft persona."),
            description="Candidate persona under review.",
            draft=True,
        )
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
        project_client.agents.delete(agent_name=agent_name)
        print(f"Deleted agent: {agent_name}")
