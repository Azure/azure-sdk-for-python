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

    pip install azure-ai-agents azure-identity opentelemetry-sdk azure-monitor-opentelemetry aiohttp

    Set these environment variables with your own values:
    * PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    * AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
      messages, which may contain personal data. False by default.
    * AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
      messages, which may contain personal data. False by default.
    * APPLICATIONINSIGHTS_CONNECTION_STRING - Set to the connection string of your Application Insights resource.
      This is used to send telemetry data to Azure Monitor. You can also get the connection string programmatically
      from AIProjectClient using the `telemetry.get_connection_string` method. A code sample showing how to do this
      can be found in the `sample_telemetry_async.py` file in the azure-ai-projects telemetry samples.
"""
import asyncio
import time
from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import ListSortOrder, MessageTextContent
from azure.identity.aio import DefaultAzureCredential
from opentelemetry import trace
import os
from azure.monitor.opentelemetry import configure_azure_monitor

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)


async def main() -> None:

    async with DefaultAzureCredential() as creds:
        agents_client = AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        )

        # Enable Azure Monitor tracing
        application_insights_connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
        configure_azure_monitor(connection_string=application_insights_connection_string)

        with tracer.start_as_current_span(scenario):
            async with agents_client:
                agent = await agents_client.create_agent(
                    model=os.environ["MODEL_DEPLOYMENT_NAME"],
                    name="my-agent",
                    instructions="You are helpful agent",
                )
                print(f"Created agent, agent ID: {agent.id}")

                thread = await agents_client.threads.create()
                print(f"Created thread, thread ID: {thread.id}")

                message = await agents_client.messages.create(
                    thread_id=thread.id, role="user", content="Hello, tell me a joke"
                )
                print(f"Created message, message ID: {message.id}")

                run = await agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
                print(f"Run completed with status: {run.status}")

                await agents_client.delete_agent(agent.id)
                print("Deleted agent")

                messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
                async for msg in messages:
                    last_part = msg.content[-1]
                    if isinstance(last_part, MessageTextContent):
                        print(f"{msg.role}: {last_part.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
