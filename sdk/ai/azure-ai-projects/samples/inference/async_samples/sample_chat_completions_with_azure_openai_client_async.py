# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    AsyncAzureOpenAI client from the azure.ai.inference package.

USAGE:
    python sample_chat_completions_with_azure_openai_client_async.py

    Before running the sample:

    pip install azure-ai-projects aiohttp openai

    Set these environment variables with your own values:
    * PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
    * MODEL_DEPLOYMENT_NAME - The model deployment name, as found in your AI Foundry project.

    Update the Azure OpenAI api-version as needed (see `api_version=` below). Values can be found here:
    https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
"""
import os
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential


async def sample_get_azure_openai_client_async():

    project_connection_string = os.environ["PROJECT_CONNECTION_STRING"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

    async with DefaultAzureCredential() as credential:

        async with AIProjectClient.from_connection_string(
            credential=credential,
            conn_str=project_connection_string,
        ) as project_client:

            # Get an authenticated AsyncAzureOpenAI client for your default Azure OpenAI connection:
            async with await project_client.inference.get_azure_openai_client(api_version="2024-06-01") as client:

                response = await client.chat.completions.create(
                    model=model_deployment_name,
                    messages=[
                        {
                            "role": "user",
                            "content": "How many feet are in a mile?",
                        },
                    ],
                )

                print(response.choices[0].message.content)


async def main():
    await sample_get_azure_openai_client_async()


if __name__ == "__main__":
    asyncio.run(main())
