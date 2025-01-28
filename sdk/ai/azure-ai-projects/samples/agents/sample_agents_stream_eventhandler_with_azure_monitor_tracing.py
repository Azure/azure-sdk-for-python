# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with an event handler in streaming from
    the Azure Agents service using a synchronous client with Azure Monitor tracing.
    View the results in the "Tracing" tab in your Azure AI Foundry project page.

USAGE:
    python sample_agents_stream_eventhandler_with_azure_monitor_tracing.py

    Before running the sample:

    pip install azure-ai-projects azure-identity opentelemetry-sdk azure-monitor-opentelemetry

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.

"""

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import (
    AgentEventHandler,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    RunStep,
)
from typing import Any
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)


class MyEventHandler(AgentEventHandler):
    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        print(f"Text delta received: {delta.text}")

    def on_thread_message(self, message: "ThreadMessage") -> None:
        if len(message.content):
            print(
                f"ThreadMessage created. ID: {message.id}, "
                f"Status: {message.status}, Content: {message.content[0].as_dict()}"
            )
        else:
            print(f"ThreadMessage created. ID: {message.id}, " f"Status: {message.status}")

    def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

    def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    def on_done(self) -> None:
        print("Stream completed.")

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")


# Enable Azure Monitor tracing
application_insights_connection_string = project_client.telemetry.get_connection_string()
if not application_insights_connection_string:
    print("Application Insights was not enabled for this project.")
    print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
    exit()
configure_azure_monitor(connection_string=application_insights_connection_string)

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span(scenario):
    with project_client:
        # Create an agent and run stream with event handler
        agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-assistant", instructions="You are a helpful assistant"
        )
        print(f"Created agent, agent ID {agent.id}")

        thread = project_client.agents.create_thread()
        print(f"Created thread, thread ID {thread.id}")

        message = project_client.agents.create_message(
            thread_id=thread.id, role="user", content="Hello, tell me a joke"
        )
        print(f"Created message, message ID {message.id}")

        with project_client.agents.create_stream(
            thread_id=thread.id, assistant_id=agent.id, event_handler=MyEventHandler()
        ) as stream:
            stream.until_done()

        project_client.agents.delete_agent(agent.id)
        print("Deleted agent")

        messages = project_client.agents.list_messages(thread_id=thread.id)
        print(f"Messages: {messages}")
