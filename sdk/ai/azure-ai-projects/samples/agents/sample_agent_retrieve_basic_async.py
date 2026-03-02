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

    pip install "azure-ai-projects>=2.0.0b4" aiohttp python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import asyncio
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from agent_retrieve_helper import create_and_retrieve_agent_and_conversation_async

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]


async def main():
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        # Creates prerequisite resources and yields (agent_name, conversation_id).
        # Then automatically deletes the created agent version when this context manager exits.
        create_and_retrieve_agent_and_conversation_async(project_client=project_client, model=model) as (
            agent_name,
            conversation_id,
        ),
        project_client.get_openai_client() as openai_client,
    ):

        # Retrieve latest version for the prerequisite agent.
        agent = await project_client.agents.get(agent_name=agent_name)
        print(f"Agent retrieved (id: {agent.id}, name: {agent.name}, version: {agent.versions.latest.version})")

        # Retrieve the prerequisite conversation.
        conversation = await openai_client.conversations.retrieve(conversation_id=conversation_id)
        print(f"Retrieved conversation (id: {conversation.id})")

        # Add a new user text message to the conversation
        await openai_client.conversations.items.create(
            conversation_id=conversation.id,
            items=[{"type": "message", "role": "user", "content": "How many feet are in a mile?"}],
        )
        print(f"Added a user message to the conversation")

        response = await openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        )
        print(f"Response output: {response.output_text}")


if __name__ == "__main__":
    asyncio.run(main())
