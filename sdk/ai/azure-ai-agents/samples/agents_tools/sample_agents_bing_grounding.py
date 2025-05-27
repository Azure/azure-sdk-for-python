# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with the Bing grounding tool from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_bing_grounding.py

    Before running the sample:

    pip install azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AZURE_BING_CONNECTION_ID - The ID of the Bing connection, in the format of:
       /subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/Microsoft.MachineLearningServices/workspaces/{workspace-name}/connections/{connection-name}
"""

import os
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageRole, BingGroundingTool
from azure.identity import DefaultAzureCredential


agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# [START create_agent_with_bing_grounding_tool]
conn_id = os.environ["AZURE_BING_CONNECTION_ID"]

# Initialize agent bing tool and add the connection id
bing = BingGroundingTool(connection_id=conn_id)

# Create agent with the bing tool and process agent run
with agents_client:
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=bing.definitions,
    )
    # [END create_agent_with_bing_grounding_tool]

    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content="How does wikipedia explain Euler's Identity?",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process agent run in thread with tools
    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Fetch run steps to get the details of the agent run
    run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)
    for step in run_steps:
        print(f"Step {step['id']} status: {step['status']}")
        step_details = step.get("step_details", {})
        tool_calls = step_details.get("tool_calls", [])

        if tool_calls:
            print("  Tool calls:")
            for call in tool_calls:
                print(f"    Tool Call ID: {call.get('id')}")
                print(f"    Type: {call.get('type')}")

                bing_grounding_details = call.get("bing_grounding", {})
                if bing_grounding_details:
                    print(f"    Bing Grounding ID: {bing_grounding_details.get('requesturl')}")

        print()  # add an extra newline between steps

    # Delete the agent when done
    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    # Print the Agent's response message with optional citation
    response_message = agents_client.messages.get_last_message_by_role(thread_id=thread.id, role=MessageRole.AGENT)
    if response_message:
        for text_message in response_message.text_messages:
            print(f"Agent response: {text_message.text.value}")
        for annotation in response_message.url_citation_annotations:
            print(f"URL Citation: [{annotation.url_citation.title}]({annotation.url_citation.url})")
