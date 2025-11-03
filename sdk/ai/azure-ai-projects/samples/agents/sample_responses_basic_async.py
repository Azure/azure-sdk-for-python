# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run a basic responses operation
    using the asynchronous client.

USAGE:
    python sample_responses_basic_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity aiohttp python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient

load_dotenv()


async def main() -> None:

    credential = DefaultAzureCredential()

    project_client = AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential)

    try:
        async with project_client:

            openai_client = await project_client.get_openai_client()

            # See https://platform.openai.com/docs/api-reference/responses/create?lang=python
            response = await openai_client.responses.create(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                input="What is the size of France in square miles?",
            )
            print(f"Response output: {response.output_text}")

            response = await openai_client.responses.create(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                input="And what is the capital city?",
                previous_response_id=response.id,
            )
            print(f"Response output: {response.output_text}")

    finally:
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
