# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Prompt Agent operations
    using the synchronous client with telemetry tracing enabled to
    Azure Monitor. View the results in the "Tracing" tab in your
    Microsoft Foundry project page.

USAGE:
    python sample_agent_basic_with_azure_monitor_tracing.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv azure-monitor-opentelemetry

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
    4) AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING - Set to `true` to enable GenAI telemetry tracing, which is
       disabled by default.
    5) OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
"""

import os
from dotenv import load_dotenv
from util import create_version_with_endpoint

from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

agent = None
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], credential=credential) as project_client,
):
    # Enable Azure Monitor tracing
    application_insights_connection_string = project_client.telemetry.get_application_insights_connection_string()
    configure_azure_monitor(connection_string=application_insights_connection_string)

    tracer = trace.get_tracer(__name__)
    scenario = os.path.basename(__file__)

    with tracer.start_as_current_span(scenario):
        with (
            create_version_with_endpoint(
                project_client=project_client,
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=os.environ["FOUNDRY_MODEL_NAME"],
                    instructions="You are a helpful assistant that answers general questions",
                ),
            ),
            project_client.get_openai_client(agent_name=agent_name) as openai_client,
        ):
            conversation = openai_client.conversations.create()
            print(f"Created conversation with initial user message (id: {conversation.id})")

            response = openai_client.responses.create(
                conversation=conversation.id,
                input="What is the size of France in square miles?",
            )
            print(f"Response output: {response.output_text}")

            openai_client.conversations.delete(conversation_id=conversation.id)
