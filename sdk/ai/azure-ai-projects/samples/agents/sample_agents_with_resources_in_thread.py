# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with file searching from
    the Azure Agents service using a synchronous client.   The file is attached to thread.

USAGE:
    python sample_agents_with_resources_in_thread.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

with project_client:

    # Upload file and create vector store
    # [START create_agent_and_thread_for_file_search]
    file = project_client.agents.upload_file_and_poll(file_path="product_info_1.md", purpose="assistants")
    print(f"Uploaded file, file ID: {file.id}")

    vector_store = project_client.agents.create_vector_store_and_poll(file_ids=[file.id], name="my_vectorstore")
    print(f"Created vector store, vector store ID: {vector_store.id}")

    # Create file search tool with resources followed by creating agent
    file_search = FileSearchTool(vector_store_ids=[vector_store.id])

    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="Hello, you are helpful assistant and can search information from uploaded files",
        tools=file_search.definitions,
    )

    print(f"Created agent, ID: {agent.id}")

    # Create thread with file resources.
    # If the agent has multiple threads, only this thread can search this file.
    thread = project_client.agents.create_thread(tool_resources=file_search.resources)
    # [END create_agent_and_thread_for_file_search]
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.create_message(
        thread_id=thread.id, role="user", content="Hello, what Contoso products do you know?"
    )
    print(f"Created message, ID: {message.id}")

    # Create and process assistant run in thread with tools
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        # Check if you got "Rate limit is exceeded.", then you want to get more quota
        print(f"Run failed: {run.last_error}")

    # [START teardown]
    # Delete the file when done
    project_client.agents.delete_vector_store(vector_store.id)
    print("Deleted vector store")

    project_client.agents.delete_file(file_id=file.id)
    print("Deleted file")

    # Delete the agent when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")
    # [END teardown]

    # Fetch and log all messages
    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
