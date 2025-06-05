# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_openapi_connection_auth.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with the
    OpenAPI tool from the Azure Agents service using a synchronous client, using
    custom key authentication against the TripAdvisor API.
    To learn more about OpenAPI specs, visit https://learn.microsoft.com/openapi

USAGE:
    python sample_agents_openapi_connection_auth.py

    Before running the sample:

    Set up an account at https://www.tripadvisor.com/developers and get an API key.

    Set up a custom key connection and save the connection name following the steps at
    https://aka.ms/azsdk/azure-ai-agents/custom-key-setup

    Save that connection name as the PROJECT_OPENAPI_CONNECTION_NAME environment variable

    pip install azure-ai-agents azure-identity jsonref

    Set this environment variables with your own values:
    PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                       page of your Azure AI Foundry portal.
    OPENAPI_CONNECTION_ID - the connection ID for the OpenAPI connection, taken from Azure AI Foundry.
    MODEL_DEPLOYMENT_NAME - name of the model deployment in the project to use Agents against
"""

import os
import jsonref
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import OpenApiTool, OpenApiConnectionAuthDetails, OpenApiConnectionSecurityScheme

asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/tripadvisor_openapi.json"))

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

model_name = os.environ["MODEL_DEPLOYMENT_NAME"]
connection_id = os.environ["OPENAPI_CONNECTION_ID"]

print(connection_id)

with open(asset_file_path, "r") as f:
    openapi_spec = jsonref.loads(f.read())

# Create Auth object for the OpenApiTool (note that connection or managed identity auth setup requires additional setup in Azure)
auth = OpenApiConnectionAuthDetails(security_scheme=OpenApiConnectionSecurityScheme(connection_id=connection_id))

# Initialize an Agent OpenApi tool using the read in OpenAPI spec
openapi = OpenApiTool(
    name="get_weather", spec=openapi_spec, description="Retrieve weather information for a location", auth=auth
)

# Create an Agent with OpenApi tool and process Agent run
with agents_client:
    agent = agents_client.create_agent(
        model=model_name, name="my-agent", instructions="You are a helpful agent", tools=openapi.definitions
    )
    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Summarize the reviews for the top rated hotel in Paris",
    )
    print(f"Created message: {message['id']}")

    # Create and process an Agent run in thread with tools
    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the Agent when done
    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = agents_client.messages.list(thread_id=thread.id)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
