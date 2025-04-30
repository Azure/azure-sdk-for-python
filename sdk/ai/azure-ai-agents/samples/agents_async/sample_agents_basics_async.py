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

    Set this environment variables with your own values:
    PROJECT_ENDPOINT - the Azure AI Agents endpoint.
"""
import asyncio
import time

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import MessageTextContent, ListSortOrder
from azure.identity.aio import DefaultAzureCredential

import os


async def main() -> None:

    async with DefaultAzureCredential() as creds:
        agent_client = AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        )

        async with agent_client:
            agent = await agent_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-agent", instructions="You are helpful agent"
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await agent_client.threads.create()
            print(f"Created thread, thread ID: {thread.id}")

            message = await agent_client.messages.create(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            print(f"Created message, message ID: {message.id}")

            run = await agent_client.runs.create(thread_id=thread.id, agent_id=agent.id)

            # Poll the run as long as run status is queued or in progress
            while run.status in ["queued", "in_progress", "requires_action"]:
                # Wait for a second
                time.sleep(1)
                run = await agent_client.runs.get(thread_id=thread.id, run_id=run.id)
                print(f"Run status: {run.status}")

            if run.status == "failed":
                print(f"Run error: {run.last_error}")

            await agent_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = await agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            for data_point in messages.data:
                last_message_content = data_point.content[-1]
                if isinstance(last_message_content, MessageTextContent):
                    print(f"{data_point.role}: {last_message_content.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
