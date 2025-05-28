# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a new thread and immediately run it
    in one call using the Azure AI Agents service.

USAGE:
    python sample_agents_create_thread_and_run.py

    Before running the sample:

    pip install azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME  - The deployment name of the AI model, as found under
                                the "Name" column in the "Models + endpoints" tab in
                                your Azure AI Foundry project.
"""

import os
import time

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import AgentThreadCreationOptions, ThreadMessageOptions, ListSortOrder
from azure.identity import DefaultAzureCredential

agents_client = AgentsClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())

with agents_client:
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="sample-agent",
        instructions="You are a helpful assistant that tells jokes.",
    )
    print(f"Created agent, agent ID: {agent.id}")

    # [START create_thread_and_run]
    # Prepare the initial user message
    initial_message = ThreadMessageOptions(role="user", content="Hello! Can you tell me a joke?")

    # Create a new thread and immediately start a run on it
    run = agents_client.create_thread_and_run(
        agent_id=agent.id,
        thread=AgentThreadCreationOptions(messages=[initial_message]),
    )
    # [END create_thread_and_run]

    # Poll the run as long as run status is queued or in progress
    while run.status in ["queued", "in_progress", "requires_action"]:
        # Wait for a second
        time.sleep(1)
        run = agents_client.runs.get(thread_id=run.thread_id, run_id=run.id)
        print(f"Run status: {run.status}")

    if run.status == "failed":
        print(f"Run error: {run.last_error}")

    # List all messages in the thread, in ascending order of creation
    messages = agents_client.messages.list(thread_id=run.thread_id, order=ListSortOrder.ASCENDING)

    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")

    # clean up
    agents_client.delete_agent(agent.id)
    print(f"Deleted agent {agent.id!r}")
