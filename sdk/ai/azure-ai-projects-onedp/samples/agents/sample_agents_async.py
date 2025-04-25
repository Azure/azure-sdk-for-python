# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an asynchronous AIProjectClient, this sample demonstrates how to access an authenticated
    asynchronous AgentsClient from the azure.ai.agents package, associated with your AI Foundry project.
    For more information on the azure.ai.agents package see https://pypi.org/project/azure-ai-agents.
    Find Agent samples here: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/samples.

USAGE:
    python sample_agents_async.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity aiohttp

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The AI model deployment name, to be used by your Agent, as found
       in your AI Foundry project.
"""

import os, asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.onedp.aio import AIProjectClient


async def sample_agents_async() -> None:

    endpoint = os.environ["PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

    async with AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
    ) as project_client:

        agent = await project_client.agents.create_agent(
            model=model_deployment_name,
            name="my-agent",
            instructions="You are helpful agent",
        )
        print(f"Created agent, agent ID: {agent.id}")

        # Do something with your Agent!
        # See samples here https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/samples

        await project_client.agents.delete_agent(agent.id)
        print("Deleted agent")


async def main():
    await sample_agents_async()


if __name__ == "__main__":
    asyncio.run(main())
