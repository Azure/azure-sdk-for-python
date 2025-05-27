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

    pip install azure-ai-agents azure-identity opentelemetry-sdk azure-monitor-opentelemetry

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
    4) APPLICATIONINSIGHTS_CONNECTION_STRING - Set to the connection string of your Application Insights resource.
       This is used to send telemetry data to Azure Monitor. You can also get the connection string programmatically
       from AIProjectClient using the `telemetry.get_connection_string` method. A code sample showing how to do this
       can be found in the `sample_telemetry.py` file in the azure-ai-projects telemetry samples.
"""

import os
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    AgentEventHandler,
    MessageDeltaChunk,
    ListSortOrder,
    ThreadMessage,
    ThreadRun,
    RunStep,
)
from typing import Any
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
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
application_insights_connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
configure_azure_monitor(connection_string=application_insights_connection_string)

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span(scenario):
    with agents_client:
        # Create an agent and run stream with event handler
        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-agent", instructions="You are a helpful agent"
        )
        print(f"Created agent, agent ID {agent.id}")

        thread = agents_client.threads.create()
        print(f"Created thread, thread ID {thread.id}")

        message = agents_client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        print(f"Created message, message ID {message.id}")

        with agents_client.runs.stream(
            thread_id=thread.id, agent_id=agent.id, event_handler=MyEventHandler()
        ) as stream:
            stream.until_done()

        agents_client.delete_agent(agent.id)
        print("Deleted agent")

        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        for msg in messages:
            if msg.text_messages:
                last_text = msg.text_messages[-1]
                print(f"{msg.role}: {last_text.text.value}")
