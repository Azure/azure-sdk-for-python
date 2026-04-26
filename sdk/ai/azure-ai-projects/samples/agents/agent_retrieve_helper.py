# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Helper utilities for retrieve samples.

This module centralizes setup used by the retrieve samples. It provides a
context manager that creates an agent version and conversation, yields
their identifiers for retrieve/get demonstrations, and performs agent cleanup
when the context exits.
"""

from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator

from azure.ai.projects.models import PromptAgentDefinition

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient


@contextmanager
def create_and_retrieve_agent_and_conversation(
    project_client: AIProjectClient, model: str
) -> Generator[tuple[str, str], None, None]:

    with (project_client.get_openai_client() as openai_client,):
        agent = project_client.agents.create_version(
            agent_name="MyAgent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant.",
            ),
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        conversation = openai_client.conversations.create()
        print(f"Conversation created (id: {conversation.id})")

        try:
            yield agent.name, conversation.id
        finally:
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")


@asynccontextmanager
async def create_and_retrieve_agent_and_conversation_async(
    project_client: AsyncAIProjectClient, model: str
) -> AsyncGenerator[tuple[str, str], None]:

    async with (project_client.get_openai_client() as openai_client,):
        agent = await project_client.agents.create_version(
            agent_name="MyAgent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant.",
            ),
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        conversation = await openai_client.conversations.create()
        print(f"Conversation created (id: {conversation.id})")

        try:
            yield agent.name, conversation.id
        finally:
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")
