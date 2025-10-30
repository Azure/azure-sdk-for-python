# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to do Create/Read/Update/Delete (CRUD) Agent conversations
    using the asynchronous client.

USAGE:
    python sample_conversation_crud_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" azure-identity aiohttp load_dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient

load_dotenv()


async def main() -> None:

    credential = DefaultAzureCredential()

    async with credential:

        project_client = AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential)

        async with project_client:

            # Get OpenAI client
            openai_client = await project_client.get_openai_client()

            # Create conversations
            conversation1 = await openai_client.conversations.create()
            print(f"Created conversation (id: {conversation1.id})")

            conversation2 = await openai_client.conversations.create()
            print(f"Created conversation (id: {conversation2.id})")

            # Retrieve a conversation
            conversation = await openai_client.conversations.retrieve(conversation_id=conversation1.id)
            print(f"Retrieved conversation (id: {conversation.id}, metadata: {conversation.metadata})")

            # List conversations
            # Disabled since OpenAI client does not have a conversation listing API.
            # async for conversation in openai_client.conversations.list():
            #     print(f"Listed conversation (id: {conversation.id})")

            # Update conversation
            await openai_client.conversations.update(conversation_id=conversation1.id, metadata={"key": "value"})

            conversation = await openai_client.conversations.retrieve(conversation_id=conversation1.id)
            print(f"Got updated conversation (id: {conversation.id}, metadata: {conversation.metadata})")

            # Delete conversation
            result = await openai_client.conversations.delete(conversation_id=conversation1.id)
            print(f"Conversation deleted (id: {result.id}, deleted: {result.deleted})")

            result = await openai_client.conversations.delete(conversation_id=conversation2.id)
            print(f"Conversation deleted (id: {result.id}, deleted: {result.deleted})")


if __name__ == "__main__":
    asyncio.run(main())
