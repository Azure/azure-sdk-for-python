# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Prompt Agent operations
    using the synchronous client with telemetry tracing enabled to console
    and adding custom attributes to spans.

USAGE:
    python sample_agent_basic_with_console_tracing_custom_attributes.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" opentelemetry-sdk azure-core-tracing-opentelemetry python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
"""

import os
from typing import cast
from dotenv import load_dotenv
from azure.core.settings import settings

settings.tracing_implementation = "opentelemetry"
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor, ReadableSpan, Span
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from azure.ai.projects.telemetry import AIProjectInstrumentor

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]


# Define the custom span processor that is used for adding the custom
# attributes to spans when they are started.
# [START custom_attribute_span_processor]
class CustomAttributeSpanProcessor(SpanProcessor):
    def __init__(self):
        pass

    def on_start(self, span: Span, parent_context=None):
        # Add this attribute to all spans
        span.set_attribute("trace_sample.sessionid", "123")

        # Add another attribute only to create_thread spans
        if span.name == "create_thread":
            span.set_attribute("trace_sample.create_thread.context", "abc")

    def on_end(self, span: ReadableSpan):
        # Clean-up logic can be added here if necessary
        pass


# [END custom_attribute_span_processor]

# Setup tracing to console
# Requires opentelemetry-sdk
span_exporter = ConsoleSpanExporter()
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# Enable instrumentation with content tracing
AIProjectInstrumentor().instrument()

# Add the custom span processor to the global tracer provider
# [START add_custom_span_processor_to_tracer_provider]
provider = cast(TracerProvider, trace.get_tracer_provider())
provider.add_span_processor(CustomAttributeSpanProcessor())
# [END add_custom_span_processor_to_tracer_provider]

scenario = os.path.basename(__file__)
with tracer.start_as_current_span(scenario):
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as client,
    ):

        agent_definition = PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant that answers general questions",
        )

        agent = client.agents.create_version(agent_name="MyAgent", definition=agent_definition)

        client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")
