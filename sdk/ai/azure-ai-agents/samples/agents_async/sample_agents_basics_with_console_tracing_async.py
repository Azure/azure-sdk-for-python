# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using an asynchronous client with tracing to console.

USAGE:
    python sample_agents_basics_with_console_tracing_async.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry aiohttp

    If you want to export telemetry to OTLP endpoint (such as Aspire dashboard
    https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone?tabs=bash)
    install:

    pip install azure-ai-projects opentelemetry-exporter-otlp-proto-grpc

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
"""

import asyncio
import os
from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import ListSortOrder
from azure.identity.aio import DefaultAzureCredential

from azure.core.settings import settings
settings.tracing_implementation = "opentelemetry"

# Install opentelemetry with command "pip install azure-ai-projects opentelemetry-sdk".
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

# Setup tracing to console
# Requires opentelemetry-sdk
span_exporter = ConsoleSpanExporter()
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

from azure.ai.agents.telemetry import AIAgentsInstrumentor
AIAgentsInstrumentor().instrument()


async def main() -> None:

    credential = DefaultAzureCredential()

    async with credential:

        project_client = AIProjectClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=credential,
        )

        scenario = os.path.basename(__file__)
        with tracer.start_as_current_span(scenario):

            async with project_client:

                agent = await project_client.agents.create_agent(
                    model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-agent", instructions="You are helpful agent"
                )
                print(f"Created agent, agent ID: {agent.id}")

                thread = await project_client.agents.threads.create()
                print(f"Created thread, thread ID: {thread.id}")

                message = await project_client.agents.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
                print(f"Created message, message ID: {message.id}")

                run = await project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
                print(f"Run completed with status: {run.status}")

                await project_client.agents.delete_agent(agent.id)
                print("Deleted agent")

                messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
                async for msg in messages:
                    if msg.text_messages:
                        last_text = msg.text_messages[-1]
                        print(f"{msg.role}: {last_text.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
