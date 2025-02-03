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

    pip install azure-ai-projects azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import FilePurpose
from azure.ai.projects.models import FileSearchTool, MessageAttachment
from azure.identity.aio import DefaultAzureCredential

import os


async def main() -> None:
    async with DefaultAzureCredential() as creds:
        async with AIProjectClient.from_connection_string(
            credential=creds, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
        ) as project_client:
            # Upload a file and wait for it to be processed
            file = await project_client.agents.upload_file_and_poll(
                file_path="../product_info_1.md", purpose=FilePurpose.AGENTS
            )

            # Create agent
            agent = await project_client.agents.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are helpful assistant",
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await project_client.agents.create_thread()
            print(f"Created thread, thread ID: {thread.id}")

            # Create a message with the file search attachment
            # Notice that vector store is created temporarily when using attachments with a default expiration policy of seven days.
            attachment = MessageAttachment(file_id=file.id, tools=FileSearchTool().definitions)
            message = await project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content="What feature does Smart Eyewear offer?",
                attachments=[attachment],
            )
            print(f"Created message, message ID: {message.id}")

            run = await project_client.agents.create_and_process_run(
                thread_id=thread.id, assistant_id=agent.id, sleep_interval=4
            )
            print(f"Created run, run ID: {run.id}")

            print(f"Run completed with status: {run.status}")

            await project_client.agents.delete_file(file.id)
            print("Deleted file")

            await project_client.agents.delete_agent(agent.id)
            print("Deleted agent")

            messages = await project_client.agents.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
