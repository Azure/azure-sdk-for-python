# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using a synchronous client with tracing to console and adding
    custom attributes to the span.

USAGE:
    python sample_agents_basics_with_console_tracing_custom_attributes.py

    Before running the sample:

    pip install azure-ai-agents azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry

    If you want to export telemetry to OTLP endpoint (such as Aspire dashboard
    https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone?tabs=bash)
    install:

    pip install opentelemetry-exporter-otlp-proto-grpc

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
"""

import os, sys, time
from typing import cast
from azure.core.settings import settings

settings.tracing_implementation = "opentelemetry"
# Install opentelemetry with command "pip install opentelemetry-sdk".
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor, ReadableSpan, Span
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ListSortOrder
from azure.identity import DefaultAzureCredential
from azure.ai.agents.telemetry import AIAgentsInstrumentor


# Define the custom span processor that is used for adding the custom
# attributes to spans when they are started.
class CustomAttributeSpanProcessor(SpanProcessor):
    def __init__(self):
        pass

    def on_start(self, span: Span, parent_context=None):
        # Add this attribute to all spans
        span.set_attribute("trace_sample.sessionid", "123")

        # Add another attribute only to create_message spans
        if span.name == "create_message":
            span.set_attribute("trace_sample.message.context", "abc")

    def on_end(self, span: ReadableSpan):
        # Clean-up logic can be added here if necessary
        pass


# Setup tracing to console
# Requires opentelemetry-sdk
span_exporter = ConsoleSpanExporter()
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

AIAgentsInstrumentor().instrument()

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Add the custom span processor to the global tracer provider
provider = cast(TracerProvider, trace.get_tracer_provider())
provider.add_span_processor(CustomAttributeSpanProcessor())

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span(scenario):
    with agents_client:
        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-agent", instructions="You are helpful agent"
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = agents_client.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        message = agents_client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        print(f"Created message, message ID: {message.id}")

        run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        print(f"Run completed with status: {run.status}")

        agents_client.delete_agent(agent.id)
        print("Deleted agent")

        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        for msg in messages:
            if msg.text_messages:
                last_text = msg.text_messages[-1]
                print(f"{msg.role}: {last_text.text.value}")
