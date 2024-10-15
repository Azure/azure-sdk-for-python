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

    pip install azure.ai.client azure-identity

    Set this environment variables with your own values:
    AI_CLIENT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import asyncio

from azure.ai.client.aio import AzureAIClient
from azure.ai.client.models import FilePurpose
from azure.ai.client.models import FileSearchToolDefinition, FileSearchToolResource, MessageAttachment, ToolResources
from azure.identity import DefaultAzureCredential

import os


async def main():
    # Create an Azure AI Client from a connection string, copied from your AI Studio project.
    # At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
    # Customer needs to login to Azure subscription via Azure CLI and set the environment variables

    ai_client = AzureAIClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=os.environ["AI_CLIENT_CONNECTION_STRING"]
    )

    # Or, you can create the Azure AI Client by giving all required parameters directly
    """
    ai_client = AzureAIClient(
        credential=DefaultAzureCredential(),
        host_name=os.environ["AI_CLIENT_HOST_NAME"],
        subscription_id=os.environ["AI_CLIENT_SUBSCRIPTION_ID"],
        resource_group_name=os.environ["AI_CLIENT_RESOURCE_GROUP_NAME"],
        workspace_name=os.environ["AI_CLIENT_WORKSPACE_NAME"],
        logging_enable=True, # Optional. Remove this line if you don't want to show how to enable logging
    )
    """        
    
    # upload a file and wait for it to be processed
    async with ai_client:
        file = await ai_client.agents.upload_file_and_poll(file_path="../product_info_1.md", purpose=FilePurpose.AGENTS, sleep_interval=4)

        # create a vector store with the file and wait for it to be processed
        # if you do not specify a vector store, create_message will create a vector store with a default expiration policy of seven days after they were last active 
        vector_store = await ai_client.agents.create_vector_store_and_poll(file_ids=[file.id], name="sample_vector_store", sleep_interval=4)
            
        file_search_tool = FileSearchToolDefinition()
        
        # notices that CodeInterpreterToolDefinition as tool must be added or the assistant unable to search the file
        # also, you do not need to provide tool_resources if you did not create a vector store above
        agent = await ai_client.agents.create_agent(
            model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant",
            tools=[file_search_tool],
            tool_resources=ToolResources(file_search=FileSearchToolResource(vector_store_ids=[vector_store.id]))        
        )
        print(f"Created agent, agent ID: {agent.id}")
        
        thread = await ai_client.agents.create_thread()
        print(f"Created thread, thread ID: {thread.id}")    

        # create a message with the attachment
        attachment = MessageAttachment(file_id=file.id, tools=[file_search_tool])
        message = await ai_client.agents.create_message(thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?", attachments=[attachment])
        print(f"Created message, message ID: {message.id}")

        run = await ai_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id, sleep_interval=4)
        print(f"Created run, run ID: {run.id}")

        print(f"Run completed with status: {run.status}")
                
        await ai_client.agents.delete_file(file.id)
        print("Deleted file")

        await ai_client.agents.delete_vector_store(vector_store.id)
        print("Deleted vectore store")

        await ai_client.agents.delete_agent(agent.id)
        print("Deleted agent")
        
        messages = await ai_client.agents.list_messages(thread_id=thread.id)        
        print(f"Messages: {messages}")      


if __name__ == "__main__":
    asyncio.run(main())
