# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using a asynchronous client.

USAGE:
    python sample_agents_basics_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import asyncio
import time

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import MessageTextContent, ListSortOrder
from azure.identity.aio import DefaultAzureCredential

import os


async def main() -> None:

    async with DefaultAzureCredential() as creds:
        agents_client = AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        )

        async with agents_client:
            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-agent", instructions="You are helpful agent"
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await agents_client.threads.create()
            print(f"Created thread, thread ID: {thread.id}")

            message = await agents_client.messages.create(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            print(f"Created message, message ID: {message.id}")

            run = await agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)

            # Poll the run as long as run status is queued or in progress
            while run.status in ["queued", "in_progress", "requires_action"]:
                # Wait for a second
                time.sleep(1)
                run = await agents_client.runs.get(thread_id=thread.id, run_id=run.id)
                print(f"Run status: {run.status}")

            if run.status == "failed":
                print(f"Run error: {run.last_error}")

            await agents_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = agents_client.messages.list(
                thread_id=thread.id,
                order=ListSortOrder.ASCENDING,
            )
            async for msg in messages:
                last_part = msg.content[-1]
                if isinstance(last_part, MessageTextContent):
                    print(f"{msg.role}: {last_part.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
