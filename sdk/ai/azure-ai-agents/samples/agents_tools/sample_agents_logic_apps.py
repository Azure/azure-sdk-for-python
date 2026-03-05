# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample shows how to use agents with Azure Logic Apps to execute a task, such as sending an email.

PREREQUISITES:
    1) Create a Consumption logic app resource in the same resource group as your Microsoft Foundry project in Azure portal.
    2) For the agent to run the logic app workflow, you must start the workflow with the HTTP **Request** trigger. 
    To set up the trigger and workflow for sending emails, configure the trigger to accept JSON with the 'to', 'subject', 
    and 'body' parameter values. To learn how to create a logic app resource and workflow, see: 
    https://learn.microsoft.com/azure/foundry-classic/openai/how-to/assistants-logic-apps#create-logic-apps-workflows-for-function-calling

USAGE:
    python sample_agents_logic_apps.py

    Before you run the sample, install the following Azure-related Python client libraries:

    pip install azure-ai-projects azure-ai-agents azure-identity azure-mgmt-logic

    Set the following environment variables with your own values:
    1) PROJECT_ENDPOINT - The Microsoft Foundry project endpoint. To find this value, in the Foundry portal, go to your project's "Overview" page.
    2) MODEL_DEPLOYMENT_NAME - The deployment name for the AI model. To find this value, in the Foundry portal, go to your project's "Models + endpoints" page, and look in the "Name" column.
    3) SUBSCRIPTION_ID - The ID for your Azure subscription.
    4) resource_group_name - The name for your Azure resource group.

    Replace the following values in the sample with your own values:
    1) <LOGIC_APP_NAME> - The name for the logic app you created.
    2) <TRIGGER_NAME> - The name for the trigger that starts the logic app workflow. The default JSON name for HTTP **Request** triggers is "When_an_HTTP_request_is_received".
    3) <RECIPIENT_EMAIL> - The email address for the recipient.
"""


import os
import sys
from typing import Set

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder, ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential

# Add package directory to sys.path to import user_functions
current_dir = os.path.dirname(os.path.abspath(__file__))
package_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)
from samples.utils.user_functions import fetch_current_datetime

# Import AzureLogicAppTool and the function factory from user_logic_apps
from utils.user_logic_apps import AzureLogicAppTool, create_send_email_function

# Create the agents client
project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# [START register_logic_app]
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

with project_client:
    agents_client = project_client.agents

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
    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
