# Copyright (c) Microsoft. All rights reserved.

"""
Workflow Agent with Foundry Managed Checkpoints

This sample demonstrates how to use FoundryCheckpointRepository with
a WorkflowBuilder agent to persist workflow checkpoints in Azure AI Foundry.

Foundry managed checkpoints enable workflow state to be persisted across
requests, allowing workflows to be paused, resumed, and replayed.

Prerequisites:
    - Set AZURE_AI_PROJECT_ENDPOINT to your Azure AI Foundry project endpoint
      e.g. "https://<resource>.services.ai.azure.com/api/projects/<project-id>"
    - Azure credentials configured (e.g. az login)
"""

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import ChatAgent, WorkflowBuilder
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

from azure.ai.agentserver.agentframework import from_agent_framework
from azure.ai.agentserver.agentframework.persistence import FoundryCheckpointRepository

load_dotenv()


def create_writer_agent(client: AzureAIAgentClient) -> ChatAgent:
    """Create a writer agent that generates content."""
    return client.create_agent(
        name="Writer",
        instructions=(
            "You are an excellent content writer. "
            "You create new content and edit contents based on the feedback."
        ),
    )


def create_reviewer_agent(client: AzureAIAgentClient) -> ChatAgent:
    """Create a reviewer agent that provides feedback."""
    return client.create_agent(
        name="Reviewer",
        instructions=(
            "You are an excellent content reviewer. "
            "Provide actionable feedback to the writer about the provided content. "
            "Provide the feedback in the most concise manner possible."
        ),
    )


async def main() -> None:
    """Run the workflow agent with Foundry managed checkpoints."""
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")

    async with AzureCliCredential() as cred, AzureAIAgentClient(credential=cred) as client:
        builder = (
            WorkflowBuilder()
            .register_agent(lambda: create_writer_agent(client), name="writer")
            .register_agent(lambda: create_reviewer_agent(client), name="reviewer", output_response=True)
            .set_start_executor("writer")
            .add_edge("writer", "reviewer")
        )

        # Use FoundryCheckpointRepository for Azure AI Foundry managed storage.
        # This persists workflow checkpoints remotely, enabling pause/resume
        # across requests and server restarts.
        checkpoint_repository = FoundryCheckpointRepository(
            project_endpoint=project_endpoint,
            credential=cred,
        )

        await from_agent_framework(
            builder,
            checkpoint_repository=checkpoint_repository,
        ).run_async()


if __name__ == "__main__":
    asyncio.run(main())
