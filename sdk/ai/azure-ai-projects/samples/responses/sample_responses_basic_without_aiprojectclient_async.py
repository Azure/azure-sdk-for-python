# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run a basic responses operation
    using the asynchronous AsyncOpenAI client. We do not use AIProjectClient
    in this sample, but rather construct the AsyncOpenAI client directly.

    See also https://platform.openai.com/docs/api-reference/responses/create?lang=python

USAGE:
    python sample_responses_basic_without_aiprojectclient_async.py

    Before running the sample:

    pip install openai azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

load_dotenv()


async def main() -> None:

    credential = DefaultAzureCredential()

    async with credential:

        openai = AsyncOpenAI(
            api_key=get_bearer_token_provider(credential, "https://ai.azure.com/.default"),
            base_url=os.environ["AZURE_AI_PROJECT_ENDPOINT"].rstrip("/") + "/openai",
            default_query={"api-version": "2025-11-15-preview"},
        )

        async with openai:

            response = await openai.responses.create(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                input="How many feet are in a mile?",
            )

            print(f"Response output: {response.output_text}")


if __name__ == "__main__":
    asyncio.run(main())
