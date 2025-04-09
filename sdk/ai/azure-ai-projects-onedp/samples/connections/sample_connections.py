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
from azure.core.credentials import AzureKeyCredential # TODO: Remove me when EntraID is supported
from azure.ai.projects.onedp import AIProjectClient
from azure.ai.projects.onedp.models import ConnectionType

# TODO: Remove console logging
import sys
import logging
logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
# End logging

endpoint = os.environ["PROJECT_ENDPOINT"]
connection_name = os.environ["CONNECTION_NAME"]

with AIProjectClient(
    endpoint=endpoint,
    # credential=DefaultAzureCredential(),
    credential=AzureKeyCredential(os.environ["PROJECT_API_KEY"]),
    logging_enable=True,  # TODO: Remove console logging
) as project_client:

    print("List the properties of all connections:")
    connections = project_client.connections.list()
    for connection in connections:
        print(connection)

    print("List the properties of all connections of a particular type (in this case, Azure OpenAI connections):")
    connections = project_client.connections.list(
        connection_type=ConnectionType.AZURE_OPEN_AI,
    )
    for connection in connections:
        print(connection)

    print(f"Get the properties of a connection named `{connection_name}`:")
    connection = project_client.connections.get(connection_name)
    print(connection)
