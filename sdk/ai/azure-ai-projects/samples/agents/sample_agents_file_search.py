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

    pip install azure.ai.projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os

from samples.tracing_helpers import configure_tracing
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models._patch import FileSearchTool
from azure.identity import DefaultAzureCredential


# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

scenario = os.path.basename(__file__)
tracer = configure_tracing().get_tracer(scenario)

with tracer.start_as_current_span(scenario):
    with project_client:

        openai_file = project_client.agents.upload_file_and_poll(file_path="product_info_1.md", purpose="assistants")
        print(f"Uploaded file, file ID: {openai_file.id}")

        openai_vectorstore = project_client.agents.create_vector_store_and_poll(file_ids=[openai_file.id], name="my_vectorstore")
        print(f"Created vector store, vector store ID: {openai_vectorstore.id}")

        # Create file search tool with resources
        file_search = FileSearchTool(vector_store_ids=[openai_vectorstore.id])

        # Create agent with file search tool and process assistant run
        agent = project_client.agents.create_agent(
            model="gpt-4-1106-preview",
            name="my-assistant",
            instructions="Hello, you are helpful assistant and can search information from uploaded files",
            tools=file_search.definitions,
            tool_resources=file_search.resources,
        )
        print(f"Created agent, agent ID: {agent.id}")

        # Create thread for communication
        thread = project_client.agents.create_thread()
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

        # Delete the file when done
        project_client.agents.delete_vector_store(openai_vectorstore.id)
        print("Deleted vector store")

        # Delete the agent when done
        project_client.agents.delete_agent(agent.id)
        print("Deleted agent")

        # Fetch and log all messages
        messages = project_client.agents.list_messages(thread_id=thread.id)
        print(f"Messages: {messages}")
