# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_with_file_search_attachment_async.py

DESCRIPTION:
    This sample demonstrates how to use agent operations to create messages with file search attachments from
    the Azure Agents service using a asynchronous client.

USAGE:
    python sample_agents_with_file_search_attachment_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import asyncio

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import FilePurpose
from azure.ai.projects.models import FileSearchTool, MessageAttachment, ToolResources
from azure.identity.aio import DefaultAzureCredential

import os


async def main() -> None:
    # Create an Azure AI Client from a connection string, copied from your AI Studio project.
    # At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
    # Customer needs to login to Azure subscription via Azure CLI and set the environment variables

    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
    )

    # upload a file and wait for it to be processed
    async with project_client:
        file = await project_client.agents.upload_file_and_poll(
            file_path="../product_info_1.md", purpose=FilePurpose.AGENTS
        )

        # Create agent
        agent = await project_client.agents.create_agent(
            model="gpt-4-1106-preview",
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
            thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?", attachments=[attachment]
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
