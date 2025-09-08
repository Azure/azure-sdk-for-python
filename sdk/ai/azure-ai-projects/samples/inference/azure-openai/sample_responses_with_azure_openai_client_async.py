# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated
    AsyncAzureOpenAI client from the openai package, and perform one `responses`
    operation.

USAGE:
    python sample_responses_with_azure_openai_client_async.py

    Before running the sample:

    pip install azure-ai-projects aiohttp openai

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project. Required.
    2) MODEL_DEPLOYMENT_NAME - The model deployment name, as found in your AI Foundry project. Required.
    3) CONNECTION_NAME - The name of an Azure OpenAI connection, as found in the "Connected resources" tab
       in the Management Center of your AI Foundry project. Required.

    Update the Azure OpenAI api-version as needed (see `api_version=` below). Values can be found here:
    https://learn.microsoft.com/azure/ai-foundry/openai/reference#api-specs. Note that `responses` operations
    are only supported in the preview API version at the moment.
"""

import os
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential


async def main():

    endpoint = os.environ["PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]
    connection_name = os.environ["CONNECTION_NAME"]

    async with DefaultAzureCredential() as credential:

        async with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

            print(
                "Get an authenticated Azure OpenAI client for the parent AI Services resource, and perform a 'responses' operation:"
            )
            async with await project_client.get_openai_client(api_version="2025-04-01-preview") as client:

                response = await client.responses.create(
                    model=model_deployment_name,
                    input="How many feet are in a mile?",
                )

                print(response.output_text)

            print(
                "Get an authenticated Azure OpenAI client for a connected Azure OpenAI service, and perform a 'responses' operation:"
            )
            async with await project_client.get_openai_client(
                api_version="2025-04-01-preview", connection_name=connection_name
            ) as client:

                response = await client.responses.create(
                    model=model_deployment_name,
                    input="How many feet are in a mile?",
                )

                print(response.output_text)


if __name__ == "__main__":
    asyncio.run(main())
