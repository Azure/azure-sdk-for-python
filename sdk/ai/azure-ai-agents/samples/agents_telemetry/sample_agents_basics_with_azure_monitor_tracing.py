# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using a synchronous client with Azure Monitor tracing.
    View the results in the "Tracing" tab in your Azure AI Foundry project page.

USAGE:
    python sample_agents_basics_with_azure_monitor_tracing.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity azure-monitor-opentelemetry

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
    4) APPLICATIONINSIGHTS_CONNECTION_STRING - Set to the connection string of your Application Insights resource.
       This is used to send telemetry data to Azure Monitor. You can also get the connection string programmatically
       from AIProjectClient using the `telemetry.get_application_insights_connection_string()` method. A code sample showing
       how to do this can be found in the `sample_telemetry.py` file in the azure-ai-projects telemetry samples.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# [START enable_tracing]
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

# Enable Azure Monitor tracing
application_insights_connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
configure_azure_monitor(connection_string=application_insights_connection_string)

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span(scenario):
    with project_client:
        agents_client = project_client.agents

        # [END enable_tracing]
        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-agent", instructions="You are helpful agent"
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = agents_client.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        message = agents_client.messages.create(
            thread_id=thread.id, role="user", content="Hello, tell me a hilarious joke"
        )
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
