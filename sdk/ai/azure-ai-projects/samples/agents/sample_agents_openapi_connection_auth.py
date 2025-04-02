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
    https://aka.ms/azsdk/azure-ai-projects/custom-key-setup

    Save that connection name as the PROJECT_OPENAPI_CONNECTION_NAME environment variable

    pip install azure-ai-projects azure-identity jsonref

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your Foundry Project.
    PROJECT_OPENAPI_CONNECTION_NAME - the connection name for the OpenAPI connection authentication
    MODEL_DEPLOYMENT_NAME - name of the model deployment in the project to use Agents against
"""

import os
import jsonref
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import OpenApiTool, OpenApiConnectionAuthDetails, OpenApiConnectionSecurityScheme 


project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

connection_name = os.environ["PROJECT_OPENAPI_CONNECTION_NAME"]
model_name = os.environ["MODEL_DEPLOYMENT_NAME"]
connection = project_client.connections.get(connection_name=connection_name)

print(connection.id)

with open('./tripadvisor_openapi.json', 'r') as f:
    openapi_spec = jsonref.loads(f.read())

# Create Auth object for the OpenApiTool (note that connection or managed identity auth setup requires additional setup in Azure)
auth = OpenApiConnectionAuthDetails(security_scheme=OpenApiConnectionSecurityScheme(connection_id=connection.id))

# Initialize an Agent OpenApi tool using the read in OpenAPI spec
openapi = OpenApiTool(name="get_weather", spec=openapi_spec, description="Retrieve weather information for a location", auth=auth)

# Create an Agent with OpenApi tool and process Agent run
with project_client:
    agent = project_client.agents.create_agent(
        model=model_name,
        name="my-agent",
        instructions="You are a helpful agent",
        tools=openapi.definitions
    )
    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = project_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Summarize the reviews for the top rated hotel in Paris",
    )
    print(f"Created message: {message['id']}")

    # Create and process an Agent run in thread with tools
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the Agent when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
