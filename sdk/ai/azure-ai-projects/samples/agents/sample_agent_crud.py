# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to do Create/Read/Update/Delete (CRUD) operations on
    Agents, using the synchronous client.

USAGE:
    python sample_agent_crud.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:

    # Create Agents
    agent1 = project_client.agents.create_version(
        agent_name="MyAgent1",
        definition=PromptAgentDefinition(model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]),
    )
    print(f"Agent created (id: {agent1.id}, name: {agent1.name}, version: {agent1.version})")

    agent2 = project_client.agents.create_version(
        agent_name="MyAgent2", definition=PromptAgentDefinition(model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"])
    )
    print(f"Agent created (id: {agent2.id}, name: {agent2.name}, version: {agent2.version})")

    # Retrieve Agent by name and version
    retrieved_agent_version = project_client.agents.retrieve_version(
        agent_name=agent1.name, agent_version=agent1.version
    )
    print(
        f"Retrieved Agent: id: {retrieved_agent_version.id}, name: {retrieved_agent_version.name}, version: {retrieved_agent_version.version}"
    )

    # Retrieve Agent by name (latest version)
    retrieved_agent = project_client.agents.retrieve(agent_name=agent1.name)
    print(f"Retrieved Agent: id: {retrieved_agent.id}, name: {retrieved_agent.name}")
    print(
        f"    latest version: id: {retrieved_agent.versions.latest.id} name: {retrieved_agent.versions.latest.name} version: {retrieved_agent.versions.latest.version}"
    )

    # List all versions of an Agent
    for listed_agent_version in project_client.agents.list_versions(agent_name="MyAgent1"):  # agent1.name):
        print(
            f"Listed Agent Version: id: {listed_agent_version.id}, name: {listed_agent_version.name}, version: {listed_agent_version.version}"
        )

    # List all Agents (latest versions)
    for listed_agent in project_client.agents.list():
        print(f"Listed Agent: id: {listed_agent.id}, name: {listed_agent.name}")
        print(
            f"    latest version: id: {listed_agent.versions.latest.id} name: {listed_agent.versions.latest.name} version: {listed_agent.versions.latest.version}"
        )

    # Update Prompt Agents that generate a different version
    agent1_object = project_client.agents.update(
        agent_name=agent1.name,
        definition=PromptAgentDefinition(model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]),
        description="This is my updated agent description.",
    )
    print(
        f"Updated Agent and now has: id: {agent1_object.id}, name: {agent1_object.name}, version: {agent1_object.versions.latest}, description: {agent1_object.versions.latest.description}"
    )

    # Delete Agents
    result = project_client.agents.delete(agent_name=agent1_object.name)
    print(f"Agent deleted (name: {result.name}")
    result = project_client.agents.delete_version(agent_name=agent2.name, agent_version=agent2.version)
    print(f"Agent deleted (name: {result.name}, version: {result.version}, deleted: {result.deleted})")
