# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use Agent operations with the Bing grounding
    tool, and iteration in streaming. It uses a synchronous client.

USAGE:
    python sample_agents_stream_iteration_with_bing_grounding.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) BING_CONNECTION_NAME - The name of a connection to the Bing search resource as it is
       listed in Azure AI Foundry connected resources.
"""

import os
import re
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import AgentStreamEvent, RunStepDeltaChunk
from azure.ai.agents.models import (
    MessageDeltaChunk,
    RunStep,
    ThreadMessage,
    ThreadRun,
    BingGroundingTool,
    MessageRole,
    MessageDeltaTextContent,
    MessageDeltaTextUrlCitationAnnotation,
)
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    agents_client = project_client.agents

    bing_connection_id = project_client.connections.get(os.environ["BING_CONNECTION_NAME"]).id
    bing = BingGroundingTool(connection_id=bing_connection_id)
    print(f"Bing Connection ID: {bing_connection_id}")

    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=bing.definitions,
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID {thread.id}")

    message = agents_client.messages.create(
        thread_id=thread.id, role=MessageRole.USER, content="How does wikipedia explain Euler's Identity?"
    )
    print(f"Created message, message ID {message.id}")

    # Process Agent run and stream events back to the client. It may take a few minutes for the agent to complete the run.
    reference_text = re.compile(r"\u3010(.+)\u3011")
    with agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:

        for event_type, event_data, _ in stream:

            if isinstance(event_data, MessageDeltaChunk):
                # Do not print reference text as we will show actual citation instead.
                if reference_text.match(event_data.text) is None:
                    print(f"Text delta received: {event_data.text}")
                if event_data.delta.content and isinstance(event_data.delta.content[0], MessageDeltaTextContent):
                    delta_text_content = event_data.delta.content[0]
                    if delta_text_content.text and delta_text_content.text.annotations:
                        for delta_annotation in delta_text_content.text.annotations:
                            if isinstance(delta_annotation, MessageDeltaTextUrlCitationAnnotation):
                                print(
                                    f"URL citation delta received: [{delta_annotation.url_citation.title}]({delta_annotation.url_citation.url})"
                                )

            elif isinstance(event_data, RunStepDeltaChunk):
                print(f"RunStepDeltaChunk received. ID: {event_data.id}.")

            elif isinstance(event_data, ThreadMessage):
                print(f"ThreadMessage created. ID: {event_data.id}, Status: {event_data.status}")

            elif isinstance(event_data, ThreadRun):
                print(f"ThreadRun status: {event_data.status}")

                if event_data.status == "failed":
                    print(f"Run failed. Error: {event_data.last_error}")

            elif isinstance(event_data, RunStep):
                print(f"RunStep type: {event_data.type}, Status: {event_data.status}")

            elif event_type == AgentStreamEvent.ERROR:
                print(f"An error occurred. Data: {event_data}")

            elif event_type == AgentStreamEvent.DONE:
                print("Stream completed.")

            else:
                print(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    response_message = agents_client.messages.get_last_message_by_role(thread_id=thread.id, role=MessageRole.AGENT)
    if response_message:
        responses = []
        for text_message in response_message.text_messages:
            responses.append(text_message.text.value)
        message = " ".join(responses)
        for annotation in response_message.url_citation_annotations:
            message = message.replace(
                annotation.text, f" [{annotation.url_citation.title}]({annotation.url_citation.url})"
            )
        print(f"Agent response: {message}")
