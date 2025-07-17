# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using a synchronous client, including
    working with blueprints.

USAGE:
    python sample_agents_blueprints.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os, time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder, RunStatus

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    agents_client = project_client.agents

    # List available blueprints (latest versions)
    blueprints = project_client.agent_blueprints.list_latest()
    print("Available blueprints:")
    for blueprint in blueprints:
        print(f"  - ID: {blueprint.id}, Name: {blueprint.name}, Version: {blueprint.version}")
        print(f"    Display Name: {blueprint.display_name}")
        print(f"    Description: {blueprint.description}")
    
    # Convert to list to check if empty and access first item
    blueprints_list = list(blueprints)
    
    if not blueprints_list:
        print("No blueprints available. Creating agent without blueprint.")
        selected_blueprint = None
    else:
        # Select the first blueprint
        selected_blueprint = blueprints_list[0]
        print(f"Selected blueprint: {selected_blueprint.display_name} (Name: {selected_blueprint.name}, Version: {selected_blueprint.version})")

    if selected_blueprint:
        # Create agent with blueprint metadata
        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="my-blueprint-agent",
            metadata={"blueprintId": selected_blueprint.id}
        )
        print(f"Created agent from blueprint, agent ID: {agent.id}")
    else:
        # Create agent without blueprint
        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="my-agent",
            instructions="You are helpful agent",
        )
        print(f"Created agent without blueprint, agent ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID: {thread.id}")

    # List all threads for the agent
    threads = agents_client.threads.list()

    message = agents_client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
    print(f"Created message, message ID: {message.id}")

    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    if run.status != RunStatus.COMPLETED:
        print(f"Run did not complete successfully.")

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
