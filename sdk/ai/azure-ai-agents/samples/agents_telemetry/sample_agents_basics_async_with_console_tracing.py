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
    * PROJECT_ENDPOINT - the Azure AI Agents endpoint.
    * AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
      messages, which may contain personal data. False by default.
"""
import asyncio
import time
import sys
from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import ListSortOrder
from azure.ai.agents.telemetry import enable_telemetry
from azure.identity.aio import DefaultAzureCredential
from opentelemetry import trace
import os


tracer = trace.get_tracer(__name__)


@tracer.start_as_current_span(__file__)
async def main() -> None:

    async with DefaultAzureCredential() as creds:
        async with AgentsClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=creds) as agent_client:

            # Enable console tracing
            # or, if you have local OTLP endpoint running, change it to
            # agent_client.telemetry.enable(destination="http://localhost:4317")
            enable_telemetry(destination=sys.stdout)

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

            run = await agent_client.runs.create(thread_id=thread.id, agent_id=agent.id)

            # Poll the run as long as run status is queued or in progress
            while run.status in ["queued", "in_progress", "requires_action"]:
                # Wait for a second
                time.sleep(1)
                run = await agent_client.runs.get(thread_id=thread.id, run_id=run.id)

                print(f"Run status: {run.status}")

            print(f"Run completed with status: {run.status}")

            await agent_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = await agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
