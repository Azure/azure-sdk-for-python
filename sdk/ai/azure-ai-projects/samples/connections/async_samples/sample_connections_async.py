# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an asynchronous AIProjectClient, this sample demonstrates how to enumerate the properties of all connections,
    get the properties of a default connection, and get the properties of a connection by its name.

USAGE:
    python sample_connections_async.py

    Before running the sample:

    pip install azure-ai-projects aiohttp azure-identity azure-ai-inference openai

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) CONNECTION_NAME - The name of a connection, as found in the "Connected resources" tab
       in the Management Center of your AI Foundry project.
"""

import asyncio
import os
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.identity.aio import DefaultAzureCredential


async def sample_connections_async() -> None:

    project_connection_string = os.environ["PROJECT_CONNECTION_STRING"]
    connection_name = os.environ["CONNECTION_NAME"]

    async with DefaultAzureCredential() as credential:

        async with AIProjectClient.from_connection_string(
            credential=credential,
            conn_str=project_connection_string,
        ) as project_client:

            # List the properties of all connections
            connections = await project_client.connections.list()
            print(f"====> Listing of all connections (found {len(connections)}):")
            for connection in connections:
                print(connection)

            # List the properties of all connections of a particular "type" (in this sample, Azure OpenAI connections)
            connections = await project_client.connections.list(
                connection_type=ConnectionType.AZURE_OPEN_AI,
            )
            print(f"====> Listing of all Azure Open AI connections (found {len(connections)}):")
            for connection in connections:
                print(connection)

            # Get the properties of the default connection of a particular "type", with credentials
            connection = await project_client.connections.get_default(
                connection_type=ConnectionType.AZURE_AI_SERVICES,
                include_credentials=True,  # Optional. Defaults to "False"
            )
            print("====> Get default Azure AI Services connection:")
            print(connection)

            # Get the properties of a connection by its connection name:
            connection = await project_client.connections.get(
                connection_name=connection_name, include_credentials=True  # Optional. Defaults to "False"
            )
            print("====> Get connection by name:")
            print(connection)


async def main():
    await sample_connections_async()


if __name__ == "__main__":
    asyncio.run(main())
