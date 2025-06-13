# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AI Foundry Project endpoint, this sample demonstrates how to get an authenticated 
    async ChatCompletionsClient from the azure.ai.inference package, and perform one
    chat completions operation. For more information on the azure.ai.inference package see
    https://pypi.org/project/azure-ai-inference/.

USAGE:
    python sample_chat_completions_with_azure_ai_inference_client_async.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-inference aiohttp azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The AI model deployment name, as found in your AI Foundry project.
"""

import os
import asyncio
from urllib.parse import urlparse
from azure.identity.aio import DefaultAzureCredential
from azure.ai.inference.aio import ChatCompletionsClient
from azure.ai.inference.models import UserMessage


async def main():

    endpoint = os.environ["PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

    # Project endpoint has the form:   https://<your-ai-services-account-name>.services.ai.azure.com/api/projects/<your-project-name>
    # Inference endpoint has the form: https://<your-ai-services-account-name>.services.ai.azure.com/models
    # Strip the "/api/projects/<your-project-name>" part and replace with "/models":
    inference_endpoint = f"https://{urlparse(endpoint).netloc}/models"

    async with DefaultAzureCredential() as credential:

        async with ChatCompletionsClient(
            endpoint=inference_endpoint,
            credential=credential,
            credential_scopes=["https://ai.azure.com/.default"],
        ) as client:

            response = await client.complete(
                model=model_deployment_name, messages=[UserMessage(content="How many feet are in a mile?")]
            )
            print(response.choices[0].message.content)


if __name__ == "__main__":
    asyncio.run(main())
