# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    async ImageEmbeddingsClient from the azure.ai.inference package. For more information
    on the azure.ai.inference package see https://pypi.org/project/azure-ai-inference/.

USAGE:
    python sample_image_embeddings_with_azure_ai_inference_client_async.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-inference aiohttp azure-identity

    Set these environment variables with your own values:
    * PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
    * MODEL_DEPLOYMENT_NAME - The model deployment name, as found in your AI Foundry project.
"""
import asyncio
import os
from azure.ai.projects.aio import AIProjectClient
from azure.ai.inference.models import ImageEmbeddingInput
from azure.identity.aio import DefaultAzureCredential


async def sample_get_image_embeddings_client_async():

    project_connection_string = os.environ["PROJECT_CONNECTION_STRING"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

    async with DefaultAzureCredential() as credential:

        async with AIProjectClient.from_connection_string(
            credential=credential,
            conn_str=project_connection_string,
        ) as project_client:

            # Get an authenticated async azure.ai.inference image embeddings client for your default Serverless connection:
            async with await project_client.inference.get_image_embeddings_client() as client:

                response = await client.embed(
                    model=model_deployment_name,
                    input=[ImageEmbeddingInput.load(image_file="sample1.png", image_format="png")],
                )

                for item in response.data:
                    length = len(item.embedding)
                    print(
                        f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
                        f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
                    )


async def main():
    await sample_get_image_embeddings_client_async()


if __name__ == "__main__":
    asyncio.run(main())
