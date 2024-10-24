# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_embeddings_client.py

DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    async EmbeddingsClient from the azure.ai.inference package.

USAGE:
    python sample_get_embeddings_client.py

    Before running the sample:

    pip install azure.ai.project azure-identity

    Set this environment variable with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import os
from azure.ai.project import AIProjectClient
from azure.identity import DefaultAzureCredential

with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
) as project_client:

    # Get an authenticated azure.ai.inference embeddings client for your default Serverless connection:
    with project_client.inference.get_embeddings_client() as client:

        response = client.embed(input=["first phrase", "second phrase", "third phrase"])

        for item in response.data:
            length = len(item.embedding)
            print(
                f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
                f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
            )
