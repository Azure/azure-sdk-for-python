# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
 
"""
DESCRIPTION:
    This sample demonstrates how to use agents to execute tasks with Logic Apps.
 
PREREQUISITES:
    Create a Logic App configured to send emails. The Logic App must include an HTTP request trigger that is 
    configured to accept JSON with 'to', 'subject', and 'body'. The guide to creating a Logic App Workflow
    can be found here: 
    https://learn.microsoft.com/azure/ai-services/openai/how-to/assistants-logic-apps#create-logic-apps-workflows-for-function-calling
    
USAGE:
    python sample_agents_logic_apps.py
 
    Before running the sample:
 
    pip install azure-ai-projects azure-identity

    Replace <recipient@example.com> with a valid email address in the message content.

    Set this environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) LOGIC_APP_URL - the URL of the Logic App Workflow URL to send emails, as found in your Azure Portal.
"""
 
import os, sys
 
# Get the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Add the parent directory to the system path
sys.path.append(parent_dir)
from typing import Set
from user_functions import fetch_current_datetime
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential
import requests, json
 
 
LOGIC_APP_URL = os.environ.get("LOGIC_APP_URL", "")
 
 
def send_email_via_logic_app(recipient: str, subject: str, body: str) -> str:
    """
    Sends an email by triggering an Azure Logic App endpoint. 
    The Logic App must be configured to accept JSON with 'to', 'subject', and 'body'.
    """
    if not LOGIC_APP_URL:
        raise ValueError("Logic App URL is not set.")
 
    payload = {
        "to": recipient,
        "subject": subject,
        "body": body
    }
 
    response = requests.post(url=LOGIC_APP_URL, json=payload)
    if response.ok:
        return json.dumps({"result": "Email sent successfully."})
    else:
        return json.dumps({"error": f"Error sending email request ({response.status_code}): {response.text}"})
 
 
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)
 
functions_to_use: Set = {
    fetch_current_datetime,
    send_email_via_logic_app,
}
 
with project_client:
 
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

    # Create thread for communication
    thread = project_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Hello, please send an email to <recipient@example.com> with the date and time in '%Y-%m-%d %H:%M:%S' format.",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process agent run in thread with tools
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Run finished with status: {run.status}")    

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the assistant when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")