# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use Agent operations with the Connected Agent tool from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_multiple_connected_agents.py

    Before running the sample:

    pip install azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ConnectedAgentTool, MessageRole
from azure.identity import DefaultAzureCredential


agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

connected_agent_name = "stock_price_bot"
weather_agent_name = "weather_bot"

stock_price_agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name=connected_agent_name,
    instructions=(
        "Your job is to get the stock price of a company. If asked for the Microsoft stock price, always return $350."
    ),
)

weather_agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name=weather_agent_name,
    instructions=(
        "Your job is to get the weather for a given location. If asked for the weather in Seattle, always return 60 degrees and cloudy."
    ),
)

# Initialize Connected Agent tools with the agent id, name, and description
connected_agent = ConnectedAgentTool(
    id=stock_price_agent.id, name=connected_agent_name, description="Gets the stock price of a company"
)
connected_weather_agent = ConnectedAgentTool(
    id=weather_agent.id, name=weather_agent_name, description="Gets the weather for a given location"
)

# Create agent with the Connected Agent tool and process assistant run
with agents_client:
    agent = agents_client.create_agent(
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
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content="What is the stock price of Microsoft and the weather in Seattle?",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process Agent run in thread with tools
    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the Agent when done
    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    # Delete the connected Agent when done
    agents_client.delete_agent(stock_price_agent.id)
    print("Deleted stock price agent")

    # Delete the connected Agent when done
    agents_client.delete_agent(weather_agent.id)
    print("Deleted weather agent")

    # Fetch and log all messages
    messages = agents_client.messages.list(thread_id=thread.id)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
