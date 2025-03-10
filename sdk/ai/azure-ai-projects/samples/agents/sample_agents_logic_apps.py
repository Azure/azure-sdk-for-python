# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agents with Logic Apps to execute the task of sending an email.
 
PREREQUISITES:
    1) Create a Logic App within the same resource group as your Azure AI Project in Azure Portal
    2) To configure your Logic App to send emails, you must include an HTTP request trigger that is 
    configured to accept JSON with 'to', 'subject', and 'body'. The guide to creating a Logic App Workflow
    can be found here: 
    https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/assistants-logic-apps#create-logic-apps-workflows-for-function-calling
    
USAGE:
    python sample_agents_logic_apps.py
 
    Before running the sample:
 
    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.

    Replace the following values in the sample with your own values:
    1) <LOGIC_APP_NAME> - The name of the Logic App you created.
    2) <TRIGGER_NAME> - The name of the trigger in the Logic App you created (the default name for HTTP
        triggers in the Azure Portal is "When_a_HTTP_request_is_received").
    3) <RECIPIENT_EMAIL> - The email address of the recipient.
"""


import os
import requests
from typing import Set

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential

# Example user function
from user_functions import fetch_current_datetime

# Import AzureLogicAppTool and the function factory from user_logic_apps
from user_logic_apps import AzureLogicAppTool, create_send_email_function

# [START register_logic_app]

# Create the project client
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

# Extract subscription and resource group from the project scope
subscription_id = project_client.scope["subscription_id"]
resource_group = project_client.scope["resource_group_name"]

# Logic App details
logic_app_name = "<LOGIC_APP_NAME>"
trigger_name = "<TRIGGER_NAME>"

# Create and initialize AzureLogicAppTool utility
logic_app_tool = AzureLogicAppTool(subscription_id, resource_group)
logic_app_tool.register_logic_app(logic_app_name, trigger_name)
print(f"Registered logic app '{logic_app_name}' with trigger '{trigger_name}'.")

# Create the specialized "send_email_via_logic_app" function for your agent tools
send_email_func = create_send_email_function(logic_app_tool, logic_app_name)

# Prepare the function tools for the agent
functions_to_use: Set = {
    fetch_current_datetime,
    send_email_func,  # This references the AzureLogicAppTool instance via closure
}
# [END register_logic_app]

with project_client:
    # Create an agent
    functions = FunctionTool(functions=functions_to_use)
    toolset = ToolSet()
    toolset.add(functions)

    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="SendEmailAgent",
        instructions="You are a specialized agent for sending emails.",
        toolset=toolset,
    )
    print(f"Created agent, ID: {agent.id}")

    # Create a thread for communication
    thread = project_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create a message in the thread
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Hello, please send an email to <RECIPIENT_EMAIL> with the date and time in '%Y-%m-%d %H:%M:%S' format.",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process an agent run in the thread
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the agent when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
