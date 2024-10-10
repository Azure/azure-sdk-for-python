# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_embeddings_client.py

DESCRIPTION:
    Given an AzureAIClient, this sample demonstrates how to get an authenticated 
    async EmbeddingsClient from the azure.ai.inference package.

USAGE:
    python sample_get_embeddings_client.py

    Before running the sample:

    pip install azure.ai.client azure-identity

    Set this environment variable with your own values:
    AI_CLIENT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import os
from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# It should have the format "<Endpoint>;<AzureSubscriptionId>;<ResourceGroup>;<WorkspaceName>"
ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["AI_CLIENT_CONNECTION_STRING"],
)

# Get an authenticated azure.ai.inference embeddings client for your default Serverless connection:
client = ai_client.inference.get_embeddings_client()

response = client.embed(input=["first phrase", "second phrase", "third phrase"])

for item in response.data:
    length = len(item.embedding)
    print(
        f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
        f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
    )
