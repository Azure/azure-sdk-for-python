# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to list all versions of a Hosted Agent,
    and the status of their associated container. The sample uses
    the synchronous client.

USAGE:
    python sample_agent_get_hosted_agent.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents>=2.0.0b1 azure-identity

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.core.exceptions import ResourceNotFoundError

load_dotenv()

project_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
if not project_endpoint:
    raise EnvironmentError(
        "AZURE_AI_PROJECT_ENDPOINT not set. Please add it to a .env file or set the environment variable."
    )

agent_name = "MyContainerAgent"

project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)
with project_client:

    # Retrieve latest version of an Agent
    try:
        agent = project_client.agents.retrieve(agent_name=agent_name)
    except ResourceNotFoundError as _:
        print(f"Could not find Agent named {agent_name}")
        exit(0)

    print(f"Agent retrieved (id: {agent.id}, name: {agent.name})")

    # List all versions of an Agent and retrieve their container status
    for version in project_client.agents.list_versions(agent_name=agent_name):
        print(f" - Version: {version.version}, Description: {version.description}, Created at: {version.created_at}")
        container = project_client.agents.retrieve_container(agent_name=agent_name, agent_version=version.version)
        print(f"   - Container: {container}")
