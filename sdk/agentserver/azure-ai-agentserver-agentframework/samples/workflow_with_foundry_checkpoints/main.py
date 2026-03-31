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

from agent_framework import Agent, Workflow, WorkflowBuilder
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from azure.ai.agentserver.agentframework import from_agent_framework
from azure.ai.agentserver.agentframework.persistence import FoundryCheckpointRepository

load_dotenv()


def create_writer_agent(client: AzureOpenAIResponsesClient) -> Agent:
    """Create a writer agent that generates content."""
    return Agent(
        client=client,
        name="Writer",
        instructions=(
            "You are an excellent content writer. You create new content and edit contents based on the feedback."
        ),
    )


def create_reviewer_agent(client: AzureOpenAIResponsesClient) -> Agent:
    """Create a reviewer agent that provides feedback."""
    return Agent(
        client=client,
        name="Reviewer",
        instructions=(
            "You are an excellent content reviewer. "
            "Provide actionable feedback to the writer about the provided content. "
            "Provide the feedback in the most concise manner possible."
        ),
    )


def create_workflow(client: AzureOpenAIResponsesClient) -> Workflow:
    writer = create_writer_agent(client)
    reviewer = create_reviewer_agent(client)
    return WorkflowBuilder(start_executor=writer).add_edge(writer, reviewer).build()


async def main() -> None:
    """Run the workflow agent with Foundry managed checkpoints."""
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
    credential = AzureCliCredential()
    client = AzureOpenAIResponsesClient(
        project_endpoint=project_endpoint,
        credential=credential,
    )
    # Use FoundryCheckpointRepository for Azure AI Foundry managed storage.
    # This persists workflow checkpoints remotely, enabling pause/resume
    # across requests and server restarts.
    checkpoint_repository = FoundryCheckpointRepository(
        project_endpoint=project_endpoint,
        credential=credential,
    )

    await from_agent_framework(
        lambda: create_workflow(client),
        checkpoint_repository=checkpoint_repository,
    ).run_async()


if __name__ == "__main__":
    asyncio.run(main())
