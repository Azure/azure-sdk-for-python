# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to delete all versions of a given Hosted Agent.
    This first requires stopping their associated containers. The sample uses
    the synchronous client.

USAGE:
    python sample_agent_delete_hosted_agent.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents>=2.0.0b1 azure-identity

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
"""

import os
import time

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentContainerOperationStatus, AgentContainerStatus

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

    # Loop over all versions of the given Agent
    for version in project_client.agents.list_versions(agent_name=agent_name):

        # Retrieve a particular Agent version
        container = project_client.agents.retrieve_container(agent_name=agent_name, agent_version=version.version)
        print(f"Retrieved Agent name: {agent_name}, version: {version.version}")

        if container.status != AgentContainerStatus.DELETED:

            # Delete the associated container
            operation = project_client.agents.delete_container(agent_name=agent_name, agent_version=version.version)
            print(f"Deleting associated container (operation id: {operation.id}, status: {operation.status})")

            # Poll until the operation is done
            while operation.status in [
                AgentContainerOperationStatus.NOT_STARTED,
                AgentContainerOperationStatus.IN_PROGRESS,
            ]:
                time.sleep(5)
                operation = project_client.agents.retrieve_container_operation(
                    agent_name=agent_name, operation_id=operation.id
                )
                print(f"    Operation status: {operation.status}")

            if operation.status == AgentContainerOperationStatus.SUCCEEDED:
                print(f"Container has been deleted")
                # TODO: When I do the below, resulting "container" does not have a status field.
                # container = project_client.agents.retrieve_container(agent_name=agent_name, agent_version=version.version)
                # print(f"Container status: {container.status}, id: {container.id}, created at: {container.created_at}")
            elif operation.status == AgentContainerOperationStatus.FAILED:
                print(f"Failed to delete container. Error message: {operation.error}")
            else:
                print(f"Unexpected operation status: {operation.status}")

        project_client.agents.delete_version(agent_name=agent_name, agent_version=version.version)
        print(f"Deleted Agent name: {agent_name}, version: {version.version}")
