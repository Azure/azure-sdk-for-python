# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using a asynchronous client with Azure Monitor tracing.
    View the results in the "Tracing" tab in your Azure AI Foundry project page.

USAGE:
    python sample_agents_basics_async_with_azure_monitor_tracing.py

    Before running the sample:

    pip install azure-ai-projects azure-identity opentelemetry-sdk azure-monitor-opentelemetry aiohttp

    Set these environment variables with your own values:
    * PROJECT_CONNECTION_STRING - The Azure AI Project connection string, as found in your AI Foundry project.
    * AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
      messages, which may contain personal data. False by default.
"""
import asyncio
import time
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.telemetry.agents import AIAgentsInstrumentor
from opentelemetry import trace
import os
from azure.monitor.opentelemetry import configure_azure_monitor


tracer = trace.get_tracer(__name__)


@tracer.start_as_current_span(__file__)
async def main() -> None:

    async with DefaultAzureCredential() as creds:
        project_client = AIProjectClient.from_connection_string(
            credential=creds, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
        )

        # Enable Azure Monitor tracing
        application_insights_connection_string = await project_client.telemetry.get_connection_string()
        configure_azure_monitor(connection_string=application_insights_connection_string)
        if not application_insights_connection_string:
            print("Application Insights was not enabled for this project.")
            print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
            exit()
        configure_azure_monitor(connection_string=application_insights_connection_string)

        async with project_client:
            agent = await project_client.agents.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-assistant", instructions="You are helpful assistant"
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await project_client.agents.create_thread()
            print(f"Created thread, thread ID: {thread.id}")

            message = await project_client.agents.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            print(f"Created message, message ID: {message.id}")

            run = await project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)

            # Poll the run as long as run status is queued or in progress
            while run.status in ["queued", "in_progress", "requires_action"]:
                # Wait for a second
                time.sleep(1)
                run = await project_client.agents.get_run(thread_id=thread.id, run_id=run.id)

                print(f"Run status: {run.status}")

            print(f"Run completed with status: {run.status}")

            await project_client.agents.delete_agent(agent.id)
            print("Deleted agent")

            messages = await project_client.agents.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
