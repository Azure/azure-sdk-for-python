# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with the Bing Custom Search tool from
    the Azure Agents service using a synchronous client.
    For more information on the Bing Custom Search tool, see: https://aka.ms/AgentCustomSearchDoc

USAGE:
    python sample_agents_bing_custom_search.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) BING_CUSTOM_CONNECTION_NAME - The connection name of the Bing Custom Search connection, as found in the 
       "Connected resources" tab in your Azure AI Foundry project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MessageRole, BingCustomSearchTool
from azure.identity import DefaultAzureCredential


project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

# [START create_agent_with_bing_custom_search_tool]
bing_custom_connection = project_client.connections.get(connection_name=os.environ["BING_CUSTOM_CONNECTION_NAME"])
conn_id = bing_custom_connection.id

print(conn_id)

# Initialize agent bing custom search tool and add the connection id
bing_custom_tool = BingCustomSearchTool(connection_id=conn_id, instance_name="<config_instance_name>")

# Create agent with the bing custom search tool and process assistant run
with project_client:
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=bing_custom_tool.definitions,
        headers={"x-ms-enable-preview": "true"},
    )
    # [END create_agent_with_bing_custom_search_tool]

    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = project_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role=MessageRole.USER,
        content="How many medals did the USA win in the 2024 summer olympics?",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process agent run in thread with tools
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the assistant when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    # Print the Agent's response message with optional citation
    response_message = project_client.agents.list_messages(thread_id=thread.id).get_last_message_by_role(
        MessageRole.AGENT
    )
    if response_message:
        for text_message in response_message.text_messages:
            print(f"Agent response: {text_message.text.value}")
        for annotation in response_message.url_citation_annotations:
            print(f"URL Citation: [{annotation.url_citation.title}]({annotation.url_citation.url})")
