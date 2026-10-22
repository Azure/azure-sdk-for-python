# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.ai.agents.models._models import RunStepConnectedAgentToolCall

"""
DESCRIPTION:
    This sample demonstrates how to use Agent operations with the Connected Agent tool from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_multiple_connected_agents.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) STORAGE_QUEUE_URI - the storage service queue endpoint, triggering Azure function.

    Please see Getting Started with Azure Functions page for more information on Azure Functions:
    https://learn.microsoft.com/azure/azure-functions/functions-get-started
    **Note:** The Azure Function may be only used in standard agent setup. Please follow the instruction on the web page
    https://github.com/azure-ai-foundry/foundry-samples/tree/main/infrastructure/infrastructure-setup-bicep/41-standard-agent-setup
    to deploy an agent, capable of calling Azure Functions.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    AzureFunctionStorageQueue,
    AzureFunctionTool,
    ConnectedAgentTool,
    ListSortOrder,
    MessageRole,
    RunStepToolCallDetails,
)
from azure.identity import DefaultAzureCredential


project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
storage_service_endpoint = os.environ["STORAGE_QUEUE_URI"]

with project_client:
    agents_client = project_client.agents

    # [START create_two_toy_agents]
    connected_agent_name = "stock_price_bot"
    weather_agent_name = "weather_bot"

    stock_price_agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name=connected_agent_name,
        instructions=(
            "Your job is to get the stock price of a company. If asked for the Microsoft stock price, always return $350."
        ),
    )

    azure_function_tool = AzureFunctionTool(
        name="GetWeather",
        description="Get answers from the weather bot.",
        parameters={
            "type": "object",
            "properties": {
                "Location": {"type": "string", "description": "The location to get the weather for."},
            },
        },
        input_queue=AzureFunctionStorageQueue(
            queue_name="weather-input",
            storage_service_endpoint=storage_service_endpoint,
        ),
        output_queue=AzureFunctionStorageQueue(
            queue_name="weather-output",
            storage_service_endpoint=storage_service_endpoint,
        ),
    )

    weather_agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name=weather_agent_name,
        instructions=(
            "Your job is to get the weather for a given location. "
            "Use the provided function to get the weather in the given location."
        ),
        tools=azure_function_tool.definitions,
    )

    # Initialize Connected Agent tools with the agent id, name, and description
    connected_agent = ConnectedAgentTool(
        id=stock_price_agent.id, name=connected_agent_name, description="Gets the stock price of a company"
    )
    connected_weather_agent = ConnectedAgentTool(
        id=weather_agent.id, name=weather_agent_name, description="Gets the weather for a given location"
    )
    # [END create_two_toy_agents]

    # [START create_agent_with_connected_agent_tool]
    # Create agent with the Connected Agent tool and process assistant run
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

    # [START run_agent_with_connected_agent_tool]
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
    # [END run_agent_with_connected_agent_tool]

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

    # [START list_tool_calls]
    for run_step in agents_client.run_steps.list(thread_id=thread.id, run_id=run.id, order=ListSortOrder.ASCENDING):
        if isinstance(run_step.step_details, RunStepToolCallDetails):
            for tool_call in run_step.step_details.tool_calls:
                if isinstance(tool_call, RunStepConnectedAgentToolCall):
                    print(
                        f"\tAgent: {tool_call.connected_agent.name} " f"query: {tool_call.connected_agent.arguments} ",
                        f"output: {tool_call.connected_agent.output}",
                    )
    # [END list_tool_calls]

    # [START list_messages]
    # Fetch and log all messages
    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            text = last_text.text.value.replace("\u3010", "[").replace("\u3011", "]")
            print(f"{msg.role}: {text}")
    # [END list_messages]

    agents_client.threads.delete(thread.id)
