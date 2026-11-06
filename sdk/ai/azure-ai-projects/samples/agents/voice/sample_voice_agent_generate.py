# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Describe the voice agent you want and create it with create_from_prompt.
    The service chooses initial settings. You can later customize them by
    creating another agent version.

USAGE:
    python sample_voice_agent_generate.py

    pip install "azure-ai-projects>=2.7.0" python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_NAME (optional) - Agent name;
       defaults to "MyGeneratedVoiceAgent".
"""

import os
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentKind, GenerateVoiceAgentRequest

load_dotenv()


def _safe_print(text: str) -> None:
    """Print model text, replacing characters the console cannot display."""
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "ascii"
        print(text.encode(encoding, errors="replace").decode(encoding))


endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or "MyGeneratedVoiceAgent"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
):
    agent = project_client.beta.agents.create_from_prompt(
        GenerateVoiceAgentRequest(kind=AgentKind.VOICE, name=agent_name)
    )
    print(f"Generated voice agent: {agent.name}")
    _safe_print(f"Instructions:\n{agent.versions.latest.definition.instructions}")  # type: ignore[attr-defined]

    project_client.agents.delete(agent_name=agent.name)
    print(f"Deleted voice agent: {agent.name}")
