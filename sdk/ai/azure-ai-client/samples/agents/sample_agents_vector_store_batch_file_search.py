# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_vector_store_batch_file_search_async.py

DESCRIPTION:
    This sample demonstrates how to use agent operations to add files to an existing vector store and perform search from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_vector_store_batch_file_search_async.py

    Before running the sample:

    pip install azure.ai.client azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os
from azure.ai.client import AzureAIClient
from azure.ai.client.models import FileSearchTool, FilePurpose
from azure.identity import DefaultAzureCredential


# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"]
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

with ai_client:
    
    # upload a file and wait for it to be processed
    file = ai_client.agents.upload_file_and_poll(file_path="product_info_1.md", purpose=FilePurpose.AGENTS)    
    print(f"Uploaded file, file ID: {file.id}")

    # create a vector store with no file and wait for it to be processed
    # if you do not specify a vector store, create_message will create a vector store with a default expiration policy of seven days after they were last active 
    vector_store = ai_client.agents.create_vector_store_and_poll(file_ids=[], name="sample_vector_store")
    print(f"Created vector store, vector store ID: {vector_store.id}")
    
    # add the file to the vector store
    vector_store_file_batch = ai_client.agents.create_vector_store_file_batch_and_poll(vector_store_id=vector_store.id, file_ids=[file.id])    
    print(f"Created vector store file batch, vector store file batch ID: {vector_store_file_batch.id}")
    
    # create a file search tool
    file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])
    
    # notices that CodeInterpreterToolDefinition as tool must be added or the assistant unable to search the file
    # also, you do not need to provide tool_resources if you did not create a vector store above
    agent = ai_client.agents.create_agent(
        model="gpt-4-1106-preview", name="my-assistant", 
        instructions="You are helpful assistant",
        tools=file_search_tool.definitions,
        tool_resources=file_search_tool.resources
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = ai_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")    

    message = ai_client.agents.create_message(thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?")
    print(f"Created message, message ID: {message.id}")

    run = ai_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Created run, run ID: {run.id}")
        
    ai_client.agents.delete_file(file.id)
    print("Deleted file")

    ai_client.agents.delete_vector_store(vector_store.id)
    print("Deleted vectore store")

    ai_client.agents.delete_agent(agent.id)
    print("Deleted agent")
    
    messages = ai_client.agents.list_messages(thread_id=thread.id)    
    print(f"Messages: {messages}")
