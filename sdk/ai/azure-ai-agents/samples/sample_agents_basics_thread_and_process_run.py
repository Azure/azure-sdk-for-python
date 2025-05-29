# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use the new convenience method
    `create_thread_and_process_run` in the Azure AI Agents service.
    This single call will create a thread, start a run, poll to
    completion (including any tool calls), and return the final result.

USAGE:
    python sample_agents_create_thread_and_process_run.py

    Before running the sample:

    pip install azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME  - The deployment name of the AI model, as found under
                                "Models + endpoints" in your Azure AI Foundry project.
"""

import os
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import AgentThreadCreationOptions, ThreadMessageOptions, ListSortOrder
from azure.identity import DefaultAzureCredential

agents_client = AgentsClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())

with agents_client:
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="process-run-sample-agent",
        instructions="You are a friendly assistant that generates jokes.",
    )
    print(f"Created agent: {agent.id}")

    # [START create_thread_and_process_run]
    run = agents_client.create_thread_and_process_run(
        agent_id=agent.id,
        thread=AgentThreadCreationOptions(
            messages=[ThreadMessageOptions(role="user", content="Hi! Tell me your favorite programming joke.")]
        ),
    )
    # [END create_thread_and_process_run]
    print(f"Run completed with status: {run.status!r}")

    if run.status == "failed":
        print("Run failed:", run.last_error)

    # List out all messages in the thread
    messages = agents_client.messages.list(thread_id=run.thread_id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")

    # clean up
    agents_client.delete_agent(agent.id)
    print(f"Deleted agent {agent.id}")
