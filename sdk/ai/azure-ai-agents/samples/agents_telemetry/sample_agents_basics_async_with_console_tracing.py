# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using a asynchronous client with tracing to console.

USAGE:
    python sample_agents_basics_async_with_console_tracing.py

    Before running the sample:

    pip install azure-ai-agents azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry aiohttp

    If you want to export telemetry to OTLP endpoint (such as Aspire dashboard
    https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone?tabs=bash)
    install:

    pip install opentelemetry-exporter-otlp-proto-grpc

    Set these environment variables with your own values:
    * PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    * AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
      messages, which may contain personal data. False by default.
"""
import asyncio
import time
import sys
from azure.core.settings import settings

settings.tracing_implementation = "opentelemetry"
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import ListSortOrder, MessageTextContent
from azure.identity.aio import DefaultAzureCredential
from opentelemetry import trace
import os
from azure.ai.agents.telemetry import AIAgentsInstrumentor

# Setup tracing to console
# Requires opentelemetry-sdk
span_exporter = ConsoleSpanExporter()
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

AIAgentsInstrumentor().instrument()

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)


@tracer.start_as_current_span(__file__)
async def main() -> None:

    async with DefaultAzureCredential() as creds:
        async with AgentsClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=creds) as agent_client:

            agent = await agent_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-agent", instructions="You are helpful agent"
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await agent_client.threads.create()
            print(f"Created thread, thread ID: {thread.id}")

            message = await agent_client.messages.create(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            print(f"Created message, message ID: {message.id}")

            run = await agent_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
            print(f"Run completed with status: {run.status}")

            await agent_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            async for msg in messages:
                last_part = msg.content[-1]
                if isinstance(last_part, MessageTextContent):
                    print(f"{msg.role}: {last_part.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
