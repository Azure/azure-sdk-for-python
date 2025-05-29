# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with the
    OpenAPI tool from the Azure Agents service using a synchronous client.
    To learn more about OpenAPI specs, visit https://learn.microsoft.com/openapi

USAGE:
    python sample_agents_openapi.py

    Before running the sample:

    pip install azure-ai-agents azure-identity jsonref

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
import jsonref
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import OpenApiTool, OpenApiAnonymousAuthDetails

weather_asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/weather_openapi.json"))

countries_asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/countries.json"))

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
# [START create_agent_with_openapi]

with open(weather_asset_file_path, "r") as f:
    openapi_weather = jsonref.loads(f.read())

with open(countries_asset_file_path, "r") as f:
    openapi_countries = jsonref.loads(f.read())

# Create Auth object for the OpenApiTool (note that connection or managed identity auth setup requires additional setup in Azure)
auth = OpenApiAnonymousAuthDetails()

# Initialize agent OpenApi tool using the read in OpenAPI spec
openapi_tool = OpenApiTool(
    name="get_weather", spec=openapi_weather, description="Retrieve weather information for a location", auth=auth
)
openapi_tool.add_definition(
    name="get_countries", spec=openapi_countries, description="Retrieve a list of countries", auth=auth
)

# Create agent with OpenApi tool and process agent run
with agents_client:
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=openapi_tool.definitions,
    )
    # [END create_agent_with_openapi]

    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="What's the weather in Seattle and What is the name and population of the country that uses currency with abbreviation THB?",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process agent run in thread with tools
    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)

    # Loop through each step
    for step in run_steps:
        print(f"Step {step['id']} status: {step['status']}")

        # Check if there are tool calls in the step details
        step_details = step.get("step_details", {})
        tool_calls = step_details.get("tool_calls", [])

        if tool_calls:
            print("  Tool calls:")
            for call in tool_calls:
                print(f"    Tool Call ID: {call.get('id')}")
                print(f"    Type: {call.get('type')}")

                function_details = call.get("function", {})
                if function_details:
                    print(f"    Function name: {function_details.get('name')}")
        print()  # add an extra newline between steps

    # Delete the agent when done
    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = agents_client.messages.list(thread_id=thread.id)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
