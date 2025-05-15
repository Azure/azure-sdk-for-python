# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    async EmbeddingsClient from the azure.ai.inference package. For more information
    on the azure.ai.inference package see https://pypi.org/project/azure-ai-inference/.

USAGE:
    python sample_text_embeddings_with_azure_ai_inference_client.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-inference azure-identity

    Set these environment variable with your own values:
    * PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
    * MODEL_DEPLOYMENT_NAME - The model deployment name, as found in your AI Foundry project.
"""
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_connection_string = os.environ["PROJECT_CONNECTION_STRING"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string,
) as project_client:

    # Get an authenticated azure.ai.inference embeddings client for your default Serverless connection:
    with project_client.inference.get_embeddings_client() as client:

        response = client.embed(model=model_deployment_name, input=["first phrase", "second phrase", "third phrase"])

        for item in response.data:
            length = len(item.embedding)
            print(
                f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
                f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
            )
