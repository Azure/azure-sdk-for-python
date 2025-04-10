# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    asynchronous AssistantClient from the azure.ai.assistants package. For more information on 
    the azure.ai.assistants package see https://pypi.org/project/azure-ai-assistants/.

USAGE:
    python sample_get_assistant_client_async.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-assistants aiohttp azure-identity

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
"""

import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.onedp.aio import AIProjectClient


async def sample_get_assistant_client_async():

    endpoint = os.environ["PROJECT_ENDPOINT"]

    async with AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    ) as project_client:

        with project_client.assistants.get_client() as client:
            # TODO: Do something with the assistant client...
            pass


async def main():
    await sample_get_assistant_client_async()


if __name__ == "__main__":
    asyncio.run(main())
