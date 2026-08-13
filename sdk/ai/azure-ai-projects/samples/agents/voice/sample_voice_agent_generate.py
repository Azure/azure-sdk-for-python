# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates guided authoring: generating and creating a voice
    agent through `POST /agents:generate` (`project_client.agents.generate_agent`)
    with `kind="voice"`. The service creates a voice agent with a
    service-selected starter definition, which is fully editable afterward
    through the standard create_version/update flow.

USAGE:
    python sample_voice_agent_generate.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set this environment variable with your own value:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    agent = project_client.agents.generate_agent(kind="voice")
    print(f"Generated voice agent: {agent.name}")
    print(f"Instructions:\n{agent.versions.latest.definition.instructions}")  # type: ignore[union-attr]

    project_client.agents.delete(agent_name=agent.name)
    print(f"Deleted voice agent: {agent.name}")
