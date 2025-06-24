# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use Agent operations with the Deep Research tool from
    the Azure Agents service using a synchronous client.
    For more information on the Deep Research tool, see: TBD

USAGE:
    python sample_agents_deep_research.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the arbitration AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) DEEP_RESEARCH_MODEL_DEPLOYMENT_NAME - The deployment name of the Deep Research AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    4) AZURE_BING_CONNECTION_ID - The ID of the Bing connection, in the format of:
       /subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/Microsoft.MachineLearningServices/workspaces/{workspace-name}/connections/{connection-name}
"""

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import DeepResearchTool

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# [START create_agent_with_deep_research_tool]
conn_id = os.environ["AZURE_BING_CONNECTION_ID"]

# Initialize a Deep Research tool with Bing Connection ID and Deep Research model deployment name
deep_research_tool = DeepResearchTool(
    bing_grounding_connection_id=conn_id,
    deep_research_model=os.environ["DEEP_RESEARCH_MODEL_DEPLOYMENT_NAME"],
)

# Create Agent with the Deep Research tool and process Agent run
with project_client:

    with project_client.agents as agents_client:

        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="my-agent",
            instructions="You are a helpful agent",
            tools=deep_research_tool.definitions,
        )

        # [END create_agent_with_deep_research_tool]
        print(f"Created agent, ID: {agent.id}")

        # Create thread for communication
        thread = agents_client.threads.create()
        print(f"Created thread, ID: {thread.id}")

        # Create message to thread
        message = agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="TBD",
        )
        print(f"Created message, ID: {message.id}")

        # Create and process Agent run in thread with tools
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
                for text_message in msg.text_messages:
                    print(f"Agent response: {text_message.text.value}")
                for annotation in msg.url_citation_annotations:
                    print(f"URL Citation: [{annotation.url_citation.title}]({annotation.url_citation.url})")
