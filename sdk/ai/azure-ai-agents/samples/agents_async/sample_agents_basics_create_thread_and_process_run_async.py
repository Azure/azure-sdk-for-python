# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    Asynchronous variant of sample_agents_basics_thread_and_process_run.py.
    This sample demonstrates how to use the new convenience method
    `create_thread_and_process_run` in the Azure AI Agents service.
    This single call will create a thread, start a run, poll to
    completion (including any tool calls), and return the final result.

USAGE:
    python sample_agents_basics_thread_and_process_run_async.py

    Before running:

        pip install azure-ai-agents azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
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

            run = await agents_client.create_thread_and_process_run(
                agent_id=agent.id,
                thread=AgentThreadCreationOptions(
                    messages=[ThreadMessageOptions(role="user", content="Hi! Tell me your favorite programming joke.")]
                ),
            )

            if run.status == "failed":
                print(f"Run error: {run.last_error}")

            # List all messages in the thread, in ascending order of creation
            messages = agents_client.messages.list(
                thread_id=run.thread_id,
                order=ListSortOrder.ASCENDING,
            )
            async for msg in messages:
                last_part = msg.content[-1]
                if isinstance(last_part, MessageTextContent):
                    print(f"{msg.role}: {last_part.text.value}")

            await agents_client.delete_agent(agent.id)
            print(f"Deleted agent {agent.id!r}")


if __name__ == "__main__":
    asyncio.run(main())
