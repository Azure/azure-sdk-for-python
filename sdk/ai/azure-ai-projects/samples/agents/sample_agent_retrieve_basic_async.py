# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Prompt Agent operations
    using the asynchronous client. It first creates an Agent version
    and Conversation as prerequisites, then demonstrates retrieve/get
    operations against those created resources.

    For OpenAI operations in this sample, see:
    https://platform.openai.com/docs/api-reference/conversations/retrieve?lang=python
    https://platform.openai.com/docs/api-reference/conversations/create-items?lang=python

USAGE:
    python sample_agent_retrieve_basic_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
"""

import os
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
from util import create_version_with_endpoint_async
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

_SAMPLES_DIR = Path(__file__).resolve().parents[1]
if str(_SAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(_SAMPLES_DIR))

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")


async def main():
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        create_version_with_endpoint_async(
            project_client=project_client,
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant.",
            ),
        ),
        project_client.get_openai_client(agent_name=agent_name) as openai_client,
    ):
        agent_version = await project_client.agents.get(agent_name=agent_name)
        print(
            f"Agent created (id: {agent_version.id}, name: {agent_version.name}, "
            f"version: {agent_version.versions.latest.version})"
        )

        conversation = await openai_client.conversations.create()
        print(f"Conversation created (id: {conversation.id})")

        # Retrieve latest version for the prerequisite agent.
        agent = await project_client.agents.get(agent_name=agent_name)
        print(f"Agent retrieved (id: {agent.id}, name: {agent.name}, version: {agent.versions.latest.version})")

        # Retrieve the prerequisite conversation.
        conversation = await openai_client.conversations.retrieve(conversation_id=conversation.id)
        print(f"Retrieved conversation (id: {conversation.id})")

        # Add a new user text message to the conversation
        await openai_client.conversations.items.create(
            conversation_id=conversation.id,
            items=[{"type": "message", "role": "user", "content": "How many feet are in a mile?"}],
        )
        print("Added a user message to the conversation")

        response = await openai_client.responses.create(
            conversation=conversation.id,
        )
        print(f"Response output: {response.output_text}")


if __name__ == "__main__":
    asyncio.run(main())
