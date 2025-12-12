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

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv azure-monitor-opentelemetry

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
"""

import os
from dotenv import load_dotenv

# [START imports_for_azure_monitor_tracing]
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

# [END imports_for_azure_monitor_tracing]
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

agent = None

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as project_client,
):
    # [START setup_azure_monitor_tracing]
    # Enable Azure Monitor tracing
    application_insights_connection_string = project_client.telemetry.get_application_insights_connection_string()
    configure_azure_monitor(connection_string=application_insights_connection_string)
    # [END setup_azure_monitor_tracing]

    # [START create_span_for_scenario]
    tracer = trace.get_tracer(__name__)
    scenario = os.path.basename(__file__)

    with tracer.start_as_current_span(scenario):
        # [END create_span_for_scenario]
        with project_client.get_openai_client() as openai_client:
            agent_definition = PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                instructions="You are a helpful assistant that answers general questions",
            )

            agent = project_client.agents.create_version(agent_name="MyAgent", definition=agent_definition)
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

            conversation = openai_client.conversations.create()
            print(f"Created conversation with initial user message (id: {conversation.id})")

            response = openai_client.responses.create(
                conversation=conversation.id,
                extra_body={"agent": {"name": agent.name, "id": agent.id, "type": "agent_reference"}},
                input="What is the size of France in square miles?",
            )
            print(f"Response output: {response.output_text}")

            openai_client.conversations.delete(conversation_id=conversation.id)
            print("Conversation deleted")

    if agent:
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")
