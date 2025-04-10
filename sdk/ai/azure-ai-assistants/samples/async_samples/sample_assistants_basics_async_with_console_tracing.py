# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic assistant operations from
    the Azure Assistants service using a asynchronous client with tracing to console.

USAGE:
    python sample_assistants_basics_async_with_console_tracing.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry aiohttp

    If you want to export telemetry to OTLP endpoint (such as Aspire dashboard
    https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone?tabs=bash)
    install:

    pip install opentelemetry-exporter-otlp-proto-grpc

    Set these environment variables with your own values:
    * PROJECT_CONNECTION_STRING - The Azure AI Project connection string, as found in your AI Foundry project.
    * AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
      messages, which may contain personal data. False by default.
"""
import asyncio
import time
import sys
from azure.ai.assistants.aio import AssistantsClient
from azure.ai.assistants.models import ListSortOrder
from azure.ai.assistants.telemetry import enable_telemetry
from azure.identity.aio import DefaultAzureCredential
from opentelemetry import trace
import os


tracer = trace.get_tracer(__name__)


@tracer.start_as_current_span(__file__)
async def main() -> None:

    async with DefaultAzureCredential() as creds:
        async with AssistantsClient.from_connection_string(
            credential=creds, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
        ) as assistant_client:

            # Enable console tracing
            # or, if you have local OTLP endpoint running, change it to
            # assistant_client.telemetry.enable(destination="http://localhost:4317")
            enable_telemetry(destination=sys.stdout)

            assistant = await assistant_client.create_assistant(
                model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-assistant", instructions="You are helpful assistant"
            )
            print(f"Created assistant, assistant ID: {assistant.id}")

            thread = await assistant_client.create_thread()
            print(f"Created thread, thread ID: {thread.id}")

            message = await assistant_client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            print(f"Created message, message ID: {message.id}")

            run = await assistant_client.create_run(thread_id=thread.id, assistant_id=assistant.id)

            # Poll the run as long as run status is queued or in progress
            while run.status in ["queued", "in_progress", "requires_action"]:
                # Wait for a second
                time.sleep(1)
                run = await assistant_client.get_run(thread_id=thread.id, run_id=run.id)

                print(f"Run status: {run.status}")

            print(f"Run completed with status: {run.status}")

            await assistant_client.delete_assistant(assistant.id)
            print("Deleted assistant")

            messages = await assistant_client.list_messages(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
