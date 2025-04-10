# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_assistants_openapi_connection_auth.py

DESCRIPTION:
    This sample demonstrates how to use assistant operations with the 
    OpenAPI tool from the Azure Assistants service using a synchronous client, using
    custom key authentication against the TripAdvisor API.
    To learn more about OpenAPI specs, visit https://learn.microsoft.com/openapi

USAGE:
    python sample_assistants_openapi_connection_auth.py

    Before running the sample:

    Set up an account at https://www.tripadvisor.com/developers and get an API key.

    Set up a custom key connection and save the connection name following the steps at
    https://aka.ms/azsdk/azure-ai-assistants/custom-key-setup

    Save that connection name as the PROJECT_OPENAPI_CONNECTION_NAME environment variable

    pip install azure-ai-assistants azure-identity jsonref

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your Foundry Project.
    PROJECT_OPENAPI_CONNECTION_NAME - the connection name for the OpenAPI connection authentication
    MODEL_DEPLOYMENT_NAME - name of the model deployment in the project to use Assistants against
"""

import os
import jsonref
from azure.ai.assistants import AssistantsClient
from azure.identity import DefaultAzureCredential
from azure.ai.assistants.models import OpenApiTool, OpenApiConnectionAuthDetails, OpenApiConnectionSecurityScheme 


assistants_client = AssistantsClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

connection_name = os.environ["PROJECT_OPENAPI_CONNECTION_NAME"]
model_name = os.environ["MODEL_DEPLOYMENT_NAME"]
connection_id = os.environ["OPENAPI_CONNECTION_ID"]

print(connection_id)

with open('./tripadvisor_openapi.json', 'r') as f:
    openapi_spec = jsonref.loads(f.read())

# Create Auth object for the OpenApiTool (note that connection or managed identity auth setup requires additional setup in Azure)
auth = OpenApiConnectionAuthDetails(security_scheme=OpenApiConnectionSecurityScheme(connection_id=connection_id))

# Initialize an Assistant OpenApi tool using the read in OpenAPI spec
openapi = OpenApiTool(name="get_weather", spec=openapi_spec, description="Retrieve weather information for a location", auth=auth)

# Create an Assistant with OpenApi tool and process Assistant run
with assistants_client:
    assistant = assistants_client.create_assistant(
        model=model_name,
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=openapi.definitions
    )
    print(f"Created assistant, ID: {assistant.id}")

    # Create thread for communication
    thread = assistants_client.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = assistants_client.create_message(
        thread_id=thread.id,
        role="user",
        content="Summarize the reviews for the top rated hotel in Paris",
    )
    print(f"Created message: {message['id']}")

    # Create and process an Assistant run in thread with tools
    run = assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the Assistant when done
    assistants_client.delete_assistant(assistant.id)
    print("Deleted assistant")

    # Fetch and log all messages
    messages = assistants_client.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
