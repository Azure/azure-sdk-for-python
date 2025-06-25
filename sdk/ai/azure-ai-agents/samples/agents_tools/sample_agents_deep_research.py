# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use Agent operations with the Deep Research tool from
    the Azure Agents service using a synchronous client. This sample uses a blocking call
    `agents_client.runs.create_and_process` to process the Agent run. However, since research
    results may take a few minutes to complete, it's recommended to use one of the two
    streaming samples so you can see the progress of the Agent run in real-time:
    - /agents_streaming/sample_agents_stream_iteration_with_deep_research_tool.py
    - /agents_streaming/sample_agents_stream_eventhandler_with_deep_research_tool.py

    For more information see the Deep Research Tool document: https://aka.ms/agents-deep-research

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
from azure.ai.agents.models import DeepResearchTool, MessageRole

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
            instructions="You are a helpful Agent that assists in researching scientific topics.",
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
            content=(
                "What is the latest research on quantum computing? "
                "Please summarize your findings in a 5-point bullet list, "
                "each one a few sentences long, and provide citations for the sources you used. "
                "Conclude with a short summary of the findings."
            ),
        )
        print(f"Created message, ID: {message.id}")

        # Create and process Agent run in thread with tools
        print(f"Start processing the message... this may take a few minutes to finish. Be patient!")
        run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        # Delete the Agent when done
        agents_client.delete_agent(agent.id)
        print("Deleted agent")

        # Fetch the last message from the agent in the thread
        response_message = agents_client.messages.get_last_message_by_role(thread_id=thread.id, role=MessageRole.AGENT)
        if response_message:
            for text_message in response_message.text_messages:
                print(f"Agent response: {text_message.text.value}")
            for annotation in response_message.url_citation_annotations:
                print(f"URL Citation: [{annotation.url_citation.title}]({annotation.url_citation.url})")
