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
    https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/agents-logic-apps#create-logic-apps-workflows-for-function-calling

USAGE:
    python sample_agents_logic_apps.py

    Before running the sample:

    pip install azure-ai-agents azure-identity azure-mgmt-logic

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.

    Replace the following values in the sample with your own values:
    1) <LOGIC_APP_NAME> - The name of the Logic App you created.
    2) <TRIGGER_NAME> - The name of the trigger in the Logic App you created (the default name for HTTP
        triggers in the Azure Portal is "When_a_HTTP_request_is_received").
    3) <RECIPIENT_EMAIL> - The email address of the recipient.
"""


import os
import sys
from typing import Set

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential

# Example user function
current_path = os.path.dirname(__file__)
root_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
from samples.utils.user_functions import fetch_current_datetime

# Import AzureLogicAppTool and the function factory from user_logic_apps
from utils.user_logic_apps import AzureLogicAppTool, create_send_email_function

# [START register_logic_app]

# Create the agents client
agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Extract subscription and resource group from the project scope
subscription_id = os.environ["SUBSCRIPTION_ID"]
resource_group = os.environ["resource_group_name"]

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

with agents_client:
    # Create an agent
    functions = FunctionTool(functions=functions_to_use)
    toolset = ToolSet()
    toolset.add(functions)

    agents_client.enable_auto_function_calls(toolset)

    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="SendEmailAgent",
        instructions="You are a specialized agent for sending emails.",
        toolset=toolset,
    )
    print(f"Created agent, ID: {agent.id}")

    # Create a thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create a message in the thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello, please send an email to <RECIPIENT_EMAIL> with the date and time in '%Y-%m-%d %H:%M:%S' format.",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process an agent run in the thread
    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the agent when done
    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = agents_client.messages.list(thread_id=thread.id)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
