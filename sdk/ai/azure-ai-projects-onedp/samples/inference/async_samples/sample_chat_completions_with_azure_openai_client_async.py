# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    AsyncAzureOpenAI client from the openai package, and perform one chat completions
    operation.

USAGE:
    python sample_chat_completions_with_azure_openai_client_async.py

    Before running the sample:

    pip install azure-ai-projects aiohttp openai

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) DEPLOYMENT_NAME - The model deployment name, as found in your AI Foundry project.

    Update the Azure OpenAI api-version as needed (see `api_version=` below). Values can be found here:
    https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
"""

import os
import asyncio
from azure.ai.projects.onedp.aio import AIProjectClient
from azure.core.credentials import (
    AzureKeyCredential,
)  # TODO: Remove me when EntraID is supported # TODO: Remove me when EntraID is supported
from azure.identity.aio import DefaultAzureCredential


async def sample_chat_completions_with_azure_openai_client_async():

    endpoint = os.environ["PROJECT_ENDPOINT"]
    deployment_name = os.environ["DEPLOYMENT_NAME"]

    async with DefaultAzureCredential() as credential:

        async with AIProjectClient(
            endpoint=endpoint,
            # credential=DefaultAzureCredential(),
            credential=AzureKeyCredential(os.environ["PROJECT_API_KEY"]),
            logging_enable=True,  # TODO: Remove console logging
        ) as project_client:

            # Get an authenticated AsyncAzureOpenAI client for your default Azure OpenAI connection:
            async with await project_client.inference.get_azure_openai_client(api_version="2024-06-01") as client:

                response = await client.chat.completions.create(
                    model=deployment_name,
                    messages=[
                        {
                            "role": "user",
                            "content": "How many feet are in a mile?",
                        },
                    ],
                )

                print(response.choices[0].message.content)


async def main():
    await sample_chat_completions_with_azure_openai_client_async()


if __name__ == "__main__":
    asyncio.run(main())
