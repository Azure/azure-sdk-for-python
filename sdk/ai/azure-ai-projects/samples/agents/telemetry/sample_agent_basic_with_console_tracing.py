# pylint: disable=wrong-import-position,wrong-import-order,docstring-missing-param,ungrouped-imports
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

    pip install "azure-ai-projects>=2.0.0" python-dotenv opentelemetry-sdk azure-core-tracing-opentelemetry

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
from typing import Any
from dotenv import load_dotenv
from util import create_version_with_endpoint

from azure.core.settings import settings

settings.tracing_implementation = "opentelemetry"
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from azure.ai.projects.telemetry import AIProjectInstrumentor


from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from openai.types.responses.response_input_text import ResponseInputText
from openai.types.responses.response_output_text import ResponseOutputText

load_dotenv()


def display_conversation_item(item: Any) -> None:  # pylint: disable=redefined-outer-name
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


# Setup tracing to console
# Requires opentelemetry-sdk
span_exporter = ConsoleSpanExporter()
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# Enable instrumentation with content tracing
AIProjectInstrumentor().instrument()

scenario = os.path.basename(__file__)
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")
with (
    tracer.start_as_current_span(scenario),
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], credential=credential) as project_client,
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

    request = "Hello, tell me a joke."
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=request,
    )
    print(f"Answer: {response.output}")

    response = openai_client.responses.create(
        conversation=conversation.id,
        input="Tell another one about computers.",
    )
    print(f"Answer: {response.output}")

    print("\n📋 Listing conversation items...")
    items = openai_client.conversations.items.list(conversation_id=conversation.id)

    # Print all the items
    for item in items:
        display_conversation_item(item)
