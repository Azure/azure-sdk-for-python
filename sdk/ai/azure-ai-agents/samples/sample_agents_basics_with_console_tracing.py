# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using a synchronous client with tracing to console.

USAGE:
    python sample_agents_basics_with_console_tracing.py

    Before running the sample:

    pip install azure-ai-agents azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry

    If you want to export telemetry to OTLP endpoint (such as Aspire dashboard
    https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone?tabs=bash)
    install:

    pip install opentelemetry-exporter-otlp-proto-grpc

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - the Azure AI Agents endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
"""

import os, time
from azure.core.settings import settings

settings.tracing_implementation = "opentelemetry"
# Install opentelemetry with command "pip install opentelemetry-sdk".
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.telemetry import AIAgentsInstrumentor

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

scenario = os.path.basename(__file__)
with tracer.start_as_current_span(scenario):
    with agents_client:
        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-agent", instructions="You are helpful agent"
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = agents_client.create_thread()
        print(f"Created thread, thread ID: {thread.id}")

        message = agents_client.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        print(f"Created message, message ID: {message.id}")

        run = agents_client.create_run(thread_id=thread.id, agent_id=agent.id)

        # Poll the run as long as run status is queued or in progress
        while run.status in ["queued", "in_progress", "requires_action"]:
            # Wait for a second
            time.sleep(1)
            run = agents_client.get_run(thread_id=thread.id, run_id=run.id)

            print(f"Run status: {run.status}")

        agents_client.delete_agent(agent.id)
        print("Deleted agent")

        messages = agents_client.list_messages(thread_id=thread.id)
        print(f"messages: {messages}")
