# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations to create messages with file search attachments from
    the Azure Agents service using a asynchronous client.

USAGE:
    python sample_agents_with_file_search_attachment_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model.
"""
import asyncio

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import FilePurpose
from azure.ai.agents.models import FileSearchTool, MessageAttachment, ListSortOrder, MessageTextContent
from azure.identity.aio import DefaultAzureCredential

import os

asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/product_info_1.md"))


async def main() -> None:
    async with DefaultAzureCredential() as creds:
        async with AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        ) as agents_client:
            # Upload a file and wait for it to be processed
            file = await agents_client.files.upload_and_poll(file_path=asset_file_path, purpose=FilePurpose.AGENTS)

            # Create agent
            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-agent",
                instructions="You are helpful agent",
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await agents_client.threads.create()
            print(f"Created thread, thread ID: {thread.id}")

            # Create a message with the file search attachment
            # Notice that vector store is created temporarily when using attachments with a default expiration policy of seven days.
            attachment = MessageAttachment(file_id=file.id, tools=FileSearchTool().definitions)
            message = await agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content="What feature does Smart Eyewear offer?",
                attachments=[attachment],
            )
            print(f"Created message, message ID: {message.id}")

            run = await agents_client.runs.create_and_process(
                thread_id=thread.id, agent_id=agent.id, polling_interval=4
            )
            print(f"Created run, run ID: {run.id}")

            print(f"Run completed with status: {run.status}")

            await agents_client.files.delete(file.id)
            print("Deleted file")

            await agents_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            async for msg in messages:
                last_part = msg.content[-1]
                if isinstance(last_part, MessageTextContent):
                    print(f"{msg.role}: {last_part.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
