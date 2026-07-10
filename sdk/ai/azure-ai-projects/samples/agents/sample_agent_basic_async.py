# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Prompt Agent operations
    using the asynchronous AIProjectClient. It uses Entra ID authentication to
    connect to the Microsoft Foundry service.

    The OpenAI compatible Responses and Conversation calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

USAGE:
    python sample_agent_basic_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import asyncio
import os
from dotenv import load_dotenv
from util import create_version_with_endpoint_async
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        create_version_with_endpoint_async(
            project_client=project_client,
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=os.environ["FOUNDRY_MODEL_NAME"],
                instructions="You are a helpful assistant that answers general questions.",
            ),
        ),
        project_client.get_openai_client(agent_name=agent_name) as openai_client,
    ):
        agent = await project_client.agents.get(agent_name=agent_name)
        print(f"Agent created (name: {agent.name}, id: {agent.id}, version: {agent.versions.latest.version})")

        conversation = await openai_client.conversations.create(
            items=[{"type": "message", "role": "user", "content": "What is the size of France in square miles?"}],
        )
        print(f"Created conversation with initial user message (id: {conversation.id})")

        response = await openai_client.responses.create(
            conversation=conversation.id,
        )
        print(f"Response output: {response.output_text}")

        await openai_client.conversations.items.create(
            conversation_id=conversation.id,
            items=[{"type": "message", "role": "user", "content": "And what is the capital city?"}],
        )
        print("Added a second user message to the conversation")

        response = await openai_client.responses.create(
            conversation=conversation.id,
        )
        print(f"Response output: {response.output_text}")

        await openai_client.conversations.delete(conversation_id=conversation.id)
        print("Conversation deleted")


if __name__ == "__main__":
    asyncio.run(main())
