# Copyright (c) Microsoft. All rights reserved.

"""
Workflow Agent with Foundry Managed Checkpoints

This sample demonstrates how to use FoundryCheckpointRepository with
an Agent Framework workflow to persist workflow checkpoints in Azure AI Foundry.
"""

import asyncio
import os

from agent_framework import SupportsAgentRun, WorkflowBuilder
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

from azure.ai.agentserver.agentframework import from_agent_framework
from azure.ai.agentserver.agentframework.persistence import FoundryCheckpointRepository

load_dotenv()


def create_writer_agent(client: AzureAIAgentClient) -> SupportsAgentRun:
    """Create a writer agent that generates content."""
    return client.as_agent(
        name="Writer",
        instructions=(
            "You are an excellent content writer. "
            "You create new content and edit contents based on the feedback."
        ),
    )


def create_reviewer_agent(client: AzureAIAgentClient) -> SupportsAgentRun:
    """Create a reviewer agent that provides feedback."""
    return client.as_agent(
        name="Reviewer",
        instructions=(
            "You are an excellent content reviewer. "
            "Provide actionable feedback to the writer about the provided content. "
            "Provide the feedback in the most concise manner possible."
        ),
    )


async def main() -> None:
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")

    async with AzureCliCredential() as cred, AzureAIAgentClient(async_credential=cred) as client:
        writer = create_writer_agent(client)
        reviewer = create_reviewer_agent(client)
        workflow = WorkflowBuilder(start_executor=writer).add_edge(writer, reviewer).build()

        checkpoint_repository = FoundryCheckpointRepository(
            project_endpoint=project_endpoint,
            credential=cred,
        )

        await from_agent_framework(
            workflow,
            checkpoint_repository=checkpoint_repository,
        ).run_async()


if __name__ == "__main__":
    asyncio.run(main())
