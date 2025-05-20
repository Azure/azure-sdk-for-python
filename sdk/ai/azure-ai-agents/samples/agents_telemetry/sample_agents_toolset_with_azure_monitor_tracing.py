# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with toolset from
    the Azure Agents service using a synchronous client with Azure Monitor tracing.
    View the results in the "Tracing" tab in your Azure AI Foundry project page.

USAGE:
    python sample_agents_toolset_with_azure_monitor_tracing.py

    Before running the sample:

    pip install azure-ai-agents azure-identity opentelemetry-sdk azure-monitor-opentelemetry

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
    4) APPLICATIONINSIGHTS_CONNECTION_STRING - Set to the connection string of your Application Insights resource.
       This is used to send telemetry data to Azure Monitor. You can also get the connection string programmatically
       from AIProjectClient using the `telemetry.get_connection_string` method. A code sample showing how to do this
       can be found in the `sample_telemetry.py` file in the azure-ai-projects telemetry samples.
"""
from typing import Any, Callable, Set

import os, time, json
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    FunctionTool,
    ToolSet,
    ListSortOrder,
)
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.ai.agents.telemetry import trace_function

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Enable Azure Monitor tracing
application_insights_connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
configure_azure_monitor(connection_string=application_insights_connection_string)

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)


# The trace_func decorator will trace the function call and enable adding additional attributes
# to the span in the function implementation. Note that this will trace the function parameters and their values.
@trace_function()
def fetch_weather(location: str) -> str:
    """
    Fetches the weather information for the specified location.

    :param location (str): The location to fetch weather for.
    :return: Weather information as a JSON string.
    :rtype: str
    """
    # In a real-world scenario, you'd integrate with a weather API.
    # Here, we'll mock the response.
    mock_weather_data = {"New York": "Sunny, 25°C", "London": "Cloudy, 18°C", "Tokyo": "Rainy, 22°C"}

    # Adding attributes to the current span
    span = trace.get_current_span()
    span.set_attribute("requested_location", location)

    weather = mock_weather_data.get(location, "Weather data not available for this location.")
    weather_json = json.dumps({"weather": weather})
    return weather_json


# Statically defined user functions for fast reference
user_functions: Set[Callable[..., Any]] = {
    fetch_weather,
}

# Initialize function tool with user function
functions = FunctionTool(functions=user_functions)
toolset = ToolSet()
toolset.add(functions)

# To enable tool calls executed automatically
agents_client.enable_auto_function_calls(toolset)

with tracer.start_as_current_span(scenario):
    with agents_client:
        # Create an agent and run user's request with function calls
        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="my-agent",
            instructions="You are a helpful agent",
            toolset=toolset,
        )
        print(f"Created agent, ID: {agent.id}")

        thread = agents_client.threads.create()
        print(f"Created thread, ID: {thread.id}")

        message = agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello, what is the weather in New York?",
        )
        print(f"Created message, ID: {message.id}")

        run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id, toolset=toolset)
        print(f"Run completed with status: {run.status}")

        # Delete the agent when done
        agents_client.delete_agent(agent.id)
        print("Deleted agent")

        # Fetch and log all messages
        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        for msg in messages:
            if msg.text_messages:
                last_text = msg.text_messages[-1]
                print(f"{msg.role}: {last_text.text.value}")
