# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a new version of
    a Hosted Agent and start its container, using the synchronous client.

USAGE:
    python sample_agent_create_hosted_agent.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity openai python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) AGENT_IMAGE - The container image for the Agent.
    3) CONTAINER_ENV_... - Optional. Any other variables you want to pass to the container
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    ImageBasedHostedAgentDefinition,
    ProtocolVersionRecord,
    AgentContainerOperationStatus,
    AgentProtocol,
)
import time

load_dotenv()

project_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
if not project_endpoint:
    raise EnvironmentError(
        "AZURE_AI_PROJECT_ENDPOINT not set. Please add it to a .env file or set the environment variable."
    )

project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)
with project_client:
    environment_variables = {
        k[len("CONTAINER_ENV_") :]: v for k, v in os.environ.items() if k.startswith("CONTAINER_ENV_")
    }

    # Create a new version of a Hosted Agent
    agent = project_client.agents.create_version(
        agent_name="MyContainerAgent",
        definition=ImageBasedHostedAgentDefinition(
            container_protocol_versions=[ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="v1")],
            cpu="1",
            memory="2Gi",
            image=os.environ["AGENT_IMAGE"],
            # Add any environment variables your container needs here
            environment_variables=environment_variables,
        ),
        description="You are a container agent.",
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    operation = project_client.agents.start_container(
        agent_name=agent.name, agent_version=agent.version, min_replicas=1, max_replicas=1
    )
    print(f"Starting its container (operation id: {operation.id}, status: {operation.status})")

    # Poll until the operation is done
    while operation.status in [AgentContainerOperationStatus.NOT_STARTED, AgentContainerOperationStatus.IN_PROGRESS]:
        time.sleep(5)
        operation = project_client.agents.retrieve_container_operation(agent_name=agent.name, operation_id=operation.id)
        print(f"    Operation status: {operation.status}")

    if operation.status == AgentContainerOperationStatus.SUCCEEDED:
        container = project_client.agents.retrieve_container(agent_name=agent.name, agent_version=agent.version)
        print(f"Container status: {container.status}, created at: {container.created_at}")
    elif operation.status == AgentContainerOperationStatus.FAILED:
        print(f"Operation failed. Error message: {operation.error}")
    else:
        print(f"Unexpected operation status: {operation.status}")
