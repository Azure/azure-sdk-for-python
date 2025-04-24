# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    asynchronous AgentsClient from the azure.ai.agents package. For more information on 
    the azure.ai.agents package see https://pypi.org/project/azure-ai-agents/.

USAGE:
    python sample_get_agents_client_async.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents aiohttp azure-identity

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
"""

import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.onedp.aio import AIProjectClient


async def sample_get_agents_client_async():

    endpoint = os.environ["PROJECT_ENDPOINT"]

    async with AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    ) as project_client:

        async with project_client.clients.get_agents_client() as client:
            # TODO: Do something with the agents client...
            pass


async def main():
    await sample_get_agents_client_async()


if __name__ == "__main__":
    asyncio.run(main())
