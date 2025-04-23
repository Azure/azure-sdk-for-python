# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use Agent operations with the Connected Agent tool from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_connected_agent.py

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
from azure.ai.projects.models import ConnectedAgentTool, MessageRole 
from azure.identity import DefaultAzureCredential


project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

connected_agent_name = "stock_price_bot"
weather_agent_name = "weather_bot"

stock_price_agent = project_client.agents.create_agent( 
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name=connected_agent_name, 
    instructions=( 
        "Your job is to get the stock price of a company. If asked for the Microsoft stock price, always return $350." 
    ), 
) 

weather_agent = project_client.agents.create_agent( 
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name=weather_agent_name, 
    instructions=( 
        "Your job is to get the weather for a given location. If asked for the weather in Seattle, always return 60 degrees and cloudy." 
    ), 
) 

# Initialize Connected Agent tools with the agent id, name, and description
connected_agent = ConnectedAgentTool(id=stock_price_agent.id, name=connected_agent_name, description="Gets the stock price of a company")
connected_weather_agent = ConnectedAgentTool(id=weather_agent.id, name=weather_agent_name, description="Gets the weather for a given location")

# Create agent with the Connected Agent tool and process assistant run
with project_client:
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant, and use the connected agents to get stock prices and weather.",
        tools=[
            connected_agent.definitions[0],
            connected_weather_agent.definitions[0],
        ],
    )
    # [END create_agent_with_connected_agent_tool]

    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = project_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role=MessageRole.USER,
        content="What is the stock price of Microsoft and the weather in Seattle?",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process Agent run in thread with tools
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the Agent when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    # Delete the connected Agent when done
    project_client.agents.delete_agent(stock_price_agent.id)
    print("Deleted stock price agent")

    # Delete the connected Agent when done
    project_client.agents.delete_agent(weather_agent.id)
    print("Deleted weather agent")

    # Print the Agent's response message with optional citation
    response_message = project_client.agents.list_messages(thread_id=thread.id).get_last_message_by_role(
        MessageRole.AGENT
    )
    if response_message:
        for text_message in response_message.text_messages:
            print(f"Agent response: {text_message.text.value}")
        for annotation in response_message.url_citation_annotations:
            print(f"URL Citation: [{annotation.url_citation.title}]({annotation.url_citation.url})")
