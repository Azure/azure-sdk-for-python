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

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) BING_CONNECTION_NAME - The connection name of the Bing connection, as found in the "Connected resources" tab
       in your Azure AI Foundry project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentStreamEvent, RunStepDeltaChunk
from azure.ai.projects.models import (
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

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

with project_client:
    bing_connection = project_client.connections.get(connection_name=os.environ["BING_CONNECTION_NAME"])
    bing = BingGroundingTool(connection_id=bing_connection.id)
    print(f"Bing Connection ID: {bing_connection.id}")

    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=bing.definitions,
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = project_client.agents.create_message(
        thread_id=thread.id, role=MessageRole.USER, content="How does wikipedia explain Euler's Identity?"
    )
    print(f"Created message, message ID {message.id}")

    with project_client.agents.create_stream(thread_id=thread.id, agent_id=agent.id) as stream:

        for event_type, event_data, _ in stream:

            if isinstance(event_data, MessageDeltaChunk):
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

    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    response_message = project_client.agents.list_messages(thread_id=thread.id).get_last_message_by_role(
        MessageRole.AGENT
    )
    if response_message:
        for text_message in response_message.text_messages:
            print(f"Agent response: {text_message.text.value}")
        for annotation in response_message.url_citation_annotations:
            print(f"URL Citation: [{annotation.url_citation.title}]({annotation.url_citation.url})")
