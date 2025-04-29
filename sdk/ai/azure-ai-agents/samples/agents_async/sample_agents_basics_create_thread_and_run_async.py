# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    Asynchronous variant of sample_agents_basics_thread_and_run.py.
    It creates an agent, starts a new thread, and immediately runs it
    using the async Azure AI Agents client.

USAGE:
    python sample_agents_basics_thread_and_run_async.py

    Before running:

        pip install azure-ai-agents azure-identity aiohttp

    Required environment variables:
        1) PROJECT_ENDPOINT       - Azure AI Agents endpoint.
        2) MODEL_DEPLOYMENT_NAME  - Deployment name of the model.
"""
import asyncio
import os

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import (
    AgentThreadCreationOptions,
    ThreadMessageOptions,
    MessageTextContent,
    ListSortOrder,
)
from azure.identity.aio import DefaultAzureCredential


async def main() -> None:
    async with DefaultAzureCredential() as credential:
        agents_client = AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=credential,
        )

        async with agents_client:
            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="sample-agent",
                instructions="You are a helpful assistant that tells jokes.",
            )
            print(f"Created agent, agent ID: {agent.id}")

            # Prepare the initial user message
            initial_message = ThreadMessageOptions(
                role="user",
                content="Hello! Can you tell me a joke?",
            )

            # Create a new thread and immediately start a run on it
            run = await agents_client.create_thread_and_run(
                agent_id=agent.id,
                thread=AgentThreadCreationOptions(messages=[initial_message]),
            )

            # Poll the run as long as run status is queued or in progress
            while run.status in {"queued", "in_progress", "requires_action"}:
                await asyncio.sleep(1)
                run = await agents_client.runs.get(thread_id=run.thread_id, run_id=run.id)
                print(f"Run status: {run.status}")

            if run.status == "failed":
                print(f"Run error: {run.last_error}")

            # List all messages in the thread, in ascending order of creation
            messages = await agents_client.messages.list(
                thread_id=run.thread_id,
                order=ListSortOrder.ASCENDING,
            )

            for msg in messages.data:
                for block in msg.content:
                    if isinstance(block, MessageTextContent):
                        print(f"{msg.role}: {block.text.value}")

            await agents_client.delete_agent(agent.id)
            print(f"Deleted agent {agent.id!r}")


if __name__ == "__main__":
    asyncio.run(main())
