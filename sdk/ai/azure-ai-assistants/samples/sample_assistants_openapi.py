# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use assistant operations with the 
    OpenAPI tool from the Azure Assistants service using a synchronous client.
    To learn more about OpenAPI specs, visit https://learn.microsoft.com/openapi

USAGE:
    python sample_assistants_openapi.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity jsonref

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
import jsonref
from azure.ai.assistants import AssistantsClient
from azure.identity import DefaultAzureCredential
from azure.ai.assistants.models import OpenApiTool, OpenApiAnonymousAuthDetails


assistants_client = AssistantsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
# [START create_assistant_with_openapi]

with open("./weather_openapi.json", "r") as f:
    openapi_weather = jsonref.loads(f.read())

with open("./countries.json", "r") as f:
    openapi_countries = jsonref.loads(f.read())

# Create Auth object for the OpenApiTool (note that connection or managed identity auth setup requires additional setup in Azure)
auth = OpenApiAnonymousAuthDetails()

# Initialize assistant OpenApi tool using the read in OpenAPI spec
openapi_tool = OpenApiTool(
    name="get_weather", spec=openapi_weather, description="Retrieve weather information for a location", auth=auth
)
openapi_tool.add_definition(
    name="get_countries", spec=openapi_countries, description="Retrieve a list of countries", auth=auth
)

# Create assistant with OpenApi tool and process assistant run
with assistants_client:
    assistant = assistants_client.create_assistant(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=openapi_tool.definitions,
    )

    # [END create_assistant_with_openapi]

    print(f"Created assistant, ID: {assistant.id}")

    # Create thread for communication
    thread = assistants_client.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = assistants_client.create_message(
        thread_id=thread.id,
        role="user",
        content="What's the weather in Seattle and What is the name and population of the country that uses currency with abbreviation THB?",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process assistant run in thread with tools
    run = assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    run_steps = assistants_client.list_run_steps(thread_id=thread.id, run_id=run.id)

    # Loop through each step
    for step in run_steps.data:
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

    # Delete the assistant when done
    assistants_client.delete_assistant(assistant.id)
    print("Deleted assistant")

    # Fetch and log all messages
    messages = assistants_client.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
