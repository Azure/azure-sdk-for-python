# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_stream_eventhandler_with_tracing.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with an event handler in streaming from
    the Azure Agents service using a synchronous client with tracing.

USAGE:
    python sample_agents_stream_eventhandler_with_tracing.py

    Before running the sample:

    pip install azure.ai.projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models._enums import RunStepType
from azure.identity import DefaultAzureCredential
from azure.ai.projects.agents.tracing import AIAgentsInstrumentor
from azure.ai.projects.models import (
    AgentEventHandler,
    MessageDeltaTextContent,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    RunStep,
)
from typing import Any
from tracing_helpers import configure_tracing
# To use console exporter, uncomment following lines and install opentelemetry-sdk
#from opentelemetry import trace
#from opentelemetry.sdk.trace import TracerProvider
#from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter


# Create an Azure AI Project Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)


class MyEventHandler(AgentEventHandler):
    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        for content_part in delta.delta.content:
            if isinstance(content_part, MessageDeltaTextContent):
                text_value = content_part.text.value if content_part.text else "No text"
                print(f"Text delta received: {text_value}")

    def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

    def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"Message status: {message.status}, Content: {message.content[0].as_dict()}")

    def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    def on_done(self) -> None:
        print("Stream completed.")

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")


scenario = os.path.basename(__file__)
tracer = configure_tracing("agent-samples").get_tracer(scenario)
# To setup tracing to console, comment out the previous line and
# uncomment the four lines below. Requires opentelemetry-sdk.
#exporter = ConsoleSpanExporter()
#trace.set_tracer_provider(TracerProvider())
#tracer = trace.get_tracer(__name__)
#trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

AIAgentsInstrumentor().instrument()

with tracer.start_as_current_span(scenario):
    with project_client:
        # Create an agent and run stream with event handler
        agent = project_client.agents.create_agent(
            model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant"
        )
        print(f"Created agent, agent ID {agent.id}")

        thread = project_client.agents.create_thread()
        print(f"Created thread, thread ID {thread.id}")

        message = project_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        print(f"Created message, message ID {message.id}")

        with project_client.agents.create_stream(
            thread_id=thread.id, assistant_id=agent.id, event_handler=MyEventHandler()
        ) as stream:
            stream.until_done()

        project_client.agents.delete_agent(agent.id)
        print("Deleted agent")

        messages = project_client.agents.list_messages(thread_id=thread.id)
        print(f"Messages: {messages}")

AIAgentsInstrumentor().uninstrument()