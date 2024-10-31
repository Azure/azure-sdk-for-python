# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_basics_async_with_tracing.py

DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using a asynchronous client with tracing.

USAGE:
    python sample_agents_basics_async_with_tracing.py

    Before running the sample:

    pip install azure.ai.projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import asyncio
import time
import sys
from azure.ai.projects.aio import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.tracing.agents import AIAgentsInstrumentor
# To use console exporter, uncomment following three lines and install opentelemetry-sdk
# from opentelemetry import trace
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
import os
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tracing_helpers import configure_tracing

tracer = configure_tracing("agent-samples").get_tracer(__file__)
# To setup tracing to console, comment out the previous line and
# uncomment the four lines below. Requires opentelemetry-sdk.
# exporter = ConsoleSpanExporter()
# trace.set_tracer_provider(TracerProvider())
# tracer = trace.get_tracer(__name__)
# trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

@tracer.start_as_current_span(__file__)
async def main():

    AIAgentsInstrumentor().instrument()

    # Create an Azure AI Project Client from a connection string, copied from your AI Studio project.
    # At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
    # Customer needs to login to Azure subscription via Azure CLI and set the environment variables

    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
    )

    async with project_client:
        agent = await project_client.agents.create_agent(
            model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant"
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = await project_client.agents.create_thread()
        print(f"Created thread, thread ID: {thread.id}")

        message = await project_client.agents.create_message(
            thread_id=thread.id, role="user", content="Hello, tell me a joke"
        )
        print(f"Created message, message ID: {message.id}")

        run = await project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)

        # poll the run as long as run status is queued or in progress
        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(1)
            run = await project_client.agents.get_run(thread_id=thread.id, run_id=run.id)

            print(f"Run status: {run.status}")

        print(f"Run completed with status: {run.status}")

        await project_client.agents.delete_agent(agent.id)
        print("Deleted agent")

        messages = await project_client.agents.list_messages(thread_id=thread.id)
        print(f"Messages: {messages}")

        AIAgentsInstrumentor().uninstrument()


if __name__ == "__main__":
    asyncio.run(main())
