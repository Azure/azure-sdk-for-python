# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_file_search.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with file searching from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_file_search.py

    Before running the sample:

    pip install azure.ai.client azure-identity

    Set this environment variables with your own values:
    AI_CLIENT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
from azure.ai.client import AzureAIClient
from azure.ai.client.models._patch import FileSearchTool, ToolSet
from azure.identity import DefaultAzureCredential


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

with ai_client:
    # Create file search tool
    file_search = FileSearchTool()
    openai_file = ai_client.agents.upload_file_and_poll(file_path="product_info_1.md", purpose="assistants")
    print(f"Uploaded file, file ID: {openai_file.id}")
    
    openai_vectorstore = ai_client.agents.create_vector_store_and_poll(file_ids=[openai_file.id], name="my_vectorstore")
    print(f"Created vector store, vector store ID: {openai_vectorstore.id}")
    
    file_search.add_vector_store(openai_vectorstore.id)

    toolset = ToolSet()
    toolset.add(file_search)

    #Create agent with toolset and process assistant run
    agent = ai_client.agents.create_agent(
        model="gpt-4-1106-preview", name="my-assistant", instructions="Hello, you are helpful assistant and can search information from uploaded files", toolset=toolset
    )
    print(f"Created agent, agent ID: {agent.id}")

    # Create thread for communication
    thread = ai_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = ai_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, what Contoso products do you know?")
    print(f"Created message, ID: {message.id}")

    # Create and process assistant run in thread with tools
    run = ai_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        # Check if you got "Rate limit is exceeded.", then you want to get more quota
        print(f"Run failed: {run.last_error}")

    # Delete the file when done
    ai_client.agents.delete_vector_store(openai_vectorstore.id)
    print("Deleted vector store")

    # Delete the assistant when done
    ai_client.agents.delete_agent(agent.id)
    print("Deleted assistant")

    # Fetch and log all messages
    messages = ai_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
