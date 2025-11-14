# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Prompt Agent operations
    using the synchronous client with telemetry tracing enabled to console.

USAGE:
    python sample_agent_basic_with_console_tracing.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry openai python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
"""

import os
from typing import Any
from dotenv import load_dotenv

# [START imports_for_console_tracing]
from azure.core.settings import settings

settings.tracing_implementation = "opentelemetry"
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from azure.ai.projects.telemetry import AIProjectInstrumentor

# [END imports_for_console_tracing]

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, AgentReference
from openai.types.responses.response_input_text import ResponseInputText
from openai.types.responses.response_output_text import ResponseOutputText


load_dotenv()


def display_conversation_item(item: Any) -> None:
    """Safely display conversation item information"""
    print(f"Item ID: {getattr(item, 'id', 'N/A')}")
    print(f"Type: {getattr(item, 'type', 'N/A')}")

    if hasattr(item, "content") and item.content and len(item.content) > 0:
        try:
            content_item = item.content[0]
            if isinstance(content_item, ResponseInputText):
                print(f"Content: {content_item.text}")
            elif isinstance(content_item, ResponseOutputText):
                print(f"Content: {content_item.text}")
            else:
                print(f"Content: [Unsupported content type: {type(content_item)}]")
        except (IndexError, AttributeError) as e:
            print(f"Content: [Error accessing content: {e}]")
    else:
        print("Content: [No content available]")
    print("---")


# [START setup_console_tracing]
# Setup tracing to console
# Requires opentelemetry-sdk
span_exporter = ConsoleSpanExporter()
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# Enable instrumentation with content tracing
AIProjectInstrumentor().instrument()
# [END setup_console_tracing]

# [START create_span_for_scenario]
scenario = os.path.basename(__file__)
with tracer.start_as_current_span(scenario):
    # [END create_span_for_scenario]
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        agent_definition = PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant that answers general questions",
        )

        agent = project_client.agents.create_version(agent_name="MyAgent", definition=agent_definition)
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        conversation = openai_client.conversations.create()

        request = "Hello, tell me a joke."
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent": AgentReference(name=agent.name).as_dict()},
            input=request,
        )
        print(f"Answer: {response.output}")

        response = openai_client.responses.create(
            conversation=conversation.id,
            input="Tell another one about computers.",
            extra_body={"agent": AgentReference(name=agent.name).as_dict()},
        )
        print(f"Answer: {response.output}")

        print(f"\n📋 Listing conversation items...")
        items = openai_client.conversations.items.list(conversation_id=conversation.id)

        # Print all the items
        for item in items:
            display_conversation_item(item)

        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")
