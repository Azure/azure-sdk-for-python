# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_with_file_search_attachment.py

DESCRIPTION:
    This sample demonstrates how to use agent operations to create messages with file search attachments from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_with_file_search_attachment.py

    Before running the sample:

    pip install azure.ai.client azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os
from azure.ai.client import AzureAIClient
from azure.ai.client.models import FilePurpose
from azure.ai.client.models import MessageAttachment
from azure.ai.client.models import FileSearchTool
from azure.identity import DefaultAzureCredential


# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

with ai_client:

    # upload a file and wait for it to be processed
    file = ai_client.agents.upload_file_and_poll(file_path="product_info_1.md", purpose=FilePurpose.AGENTS)
    print(f"Uploaded file, file ID: {file.id}")

    # Create agent with file search tool
    agent = ai_client.agents.create_agent(
        model="gpt-4-1106-preview",
        name="my-assistant",
        instructions="You are helpful assistant",
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = ai_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    # Create a message with the file search attachment
    # Notice that vector store is created temporarily when using attachments with a default expiration policy of seven days.
    attachment = MessageAttachment(file_id=file.id, tools=FileSearchTool().definitions)
    message = ai_client.agents.create_message(
        thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?", attachments=[attachment]
    )
    print(f"Created message, message ID: {message.id}")

    run = ai_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Created run, run ID: {run.id}")

    ai_client.agents.delete_file(file.id)
    print("Deleted file")

    ai_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    messages = ai_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
