# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.connections` methods to enumerate the properties of all connections
    and get the properties of a connection by its name.

USAGE:
    python sample_connections.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) CONNECTION_NAME - The name of a connection, as found in the "Connected resources" tab
       in the Management Center of your AI Foundry project.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType

endpoint = os.environ["PROJECT_ENDPOINT"]
connection_name = os.environ["CONNECTION_NAME"]

with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

    with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

        # [START connections_sample]
        print("List all connections:")
        for connection in project_client.connections.list():
            print(connection)

        print("List all connections of a particular type:")
        for connection in project_client.connections.list(
            connection_type=ConnectionType.AZURE_OPEN_AI,
        ):
            print(connection)

        print("Get the default connection of a particular type, without its credentials:")
        connection = project_client.connections.get_default(connection_type=ConnectionType.AZURE_OPEN_AI)
        print(connection)

        print("Get the default connection of a particular type, with its credentials:")
        connection = project_client.connections.get_default(
            connection_type=ConnectionType.AZURE_OPEN_AI, include_credentials=True
        )
        print(connection)

        print(f"Get the connection named `{connection_name}`, without its credentials:")
        connection = project_client.connections.get(connection_name)
        print(connection)

        print(f"Get the connection named `{connection_name}`, with its credentials:")
        connection = project_client.connections.get(connection_name, include_credentials=True)
        print(connection)
        # [END connection_sample]
