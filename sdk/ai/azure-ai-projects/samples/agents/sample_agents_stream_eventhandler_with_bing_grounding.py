# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use Agent operations with an event handler and
    the Bing grounding tool. It uses a synchronous client.

USAGE:
    python sample_agents_stream_eventhandler_with_bing_grounding.py

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
from typing import Any
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MessageDeltaChunk,
    RunStep,
    ThreadMessage,
    ThreadRun,
    AgentEventHandler,
    BingGroundingTool,
    MessageRole,
    MessageDeltaTextUrlCitationAnnotation,
    MessageDeltaTextContent,
)


# When using FunctionTool with ToolSet in agent creation, the tool call events are handled inside the create_stream
# method and functions gets automatically called by default.
class MyEventHandler(AgentEventHandler):

    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        print(f"Text delta received: {delta.text}")
        if delta.delta.content and isinstance(delta.delta.content[0], MessageDeltaTextContent):
            delta_text_content = delta.delta.content[0]
            if delta_text_content.text and delta_text_content.text.annotations:
                for delta_annotation in delta_text_content.text.annotations:
                    if isinstance(delta_annotation, MessageDeltaTextUrlCitationAnnotation):
                        print(
                            f"URL citation delta received: [{delta_annotation.url_citation.title}]({delta_annotation.url_citation.url})"
                        )

    def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

        if run.status == "failed":
            print(f"Run failed. Error: {run.last_error}")

    def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    def on_done(self) -> None:
        print("Stream completed.")

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")


project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

with project_client:

    bing_connection = project_client.connections.get(connection_name=os.environ["BING_CONNECTION_NAME"])
    print(f"Bing Connection ID: {bing_connection.id}")

    # Initialize agent bing tool and add the connection id
    bing = BingGroundingTool(connection_id=bing_connection.id)

    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=bing.definitions,
    )
    print(f"Created agent, ID: {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = project_client.agents.create_message(
        thread_id=thread.id,
        role=MessageRole.USER,
        content="How does wikipedia explain Euler's Identity?",
    )
    print(f"Created message, message ID {message.id}")

    with project_client.agents.create_stream(
        thread_id=thread.id, agent_id=agent.id, event_handler=MyEventHandler()
    ) as stream:
        stream.until_done()

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
