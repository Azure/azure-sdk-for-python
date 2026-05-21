# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use VoiceLive operations with console tracing
    and a custom SpanProcessor that adds custom attributes to spans. This is useful
    for correlating VoiceLive traces with your application-specific context such as
    session IDs, user IDs, or request identifiers.

USAGE:
    python sample_voicelive_with_console_tracing_custom_attributes.py

    Before running the sample:

    pip install azure-ai-voicelive azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry

    Set these environment variables with your own values:
    1) AZURE_VOICELIVE_ENDPOINT - The Azure VoiceLive endpoint URL.
    2) AZURE_VOICELIVE_API_KEY - The Azure VoiceLive API key.
    3) AZURE_VOICELIVE_MODEL - The model deployment name (e.g., gpt-realtime).
    4) AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING - Set to "true" to enable tracing.
    5) OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT - Optional. Set to "true" to trace the content of
       messages, which may contain personal data. False by default.
"""

import asyncio
import os
from typing import cast

from azure.core.settings import settings

settings.tracing_implementation = "opentelemetry"

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor, ReadableSpan, Span
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    InputTextContentPart,
    Modality,
    OutputAudioFormat,
    RequestSession,
    ServerEventType,
    ServerVad,
    UserMessageItem,
)
from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor


# Define the custom span processor that is used for adding custom
# attributes to spans when they are started.
# [START custom_attribute_span_processor]
class CustomAttributeSpanProcessor(SpanProcessor):
    def __init__(self):
        pass

    def on_start(self, span: Span, parent_context=None):
        # Add this attribute to all spans
        span.set_attribute("trace_sample.sessionid", "my-session-123")

        # Add another attribute only to "send" spans
        if span.name and span.name.startswith("send"):
            span.set_attribute("trace_sample.send.context", "user-interaction")

        # Add another attribute only to "recv" spans
        if span.name and span.name.startswith("recv"):
            span.set_attribute("trace_sample.recv.priority", "normal")

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

# Enable VoiceLive tracing
os.environ.setdefault("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "true")
VoiceLiveInstrumentor().instrument()

# Add the custom span processor to the global tracer provider
# [START add_custom_span_processor_to_tracer_provider]
provider = cast(TracerProvider, trace.get_tracer_provider())
provider.add_span_processor(CustomAttributeSpanProcessor())
# [END add_custom_span_processor_to_tracer_provider]

scenario = os.path.basename(__file__)


async def main() -> None:
    endpoint = os.environ["AZURE_VOICELIVE_ENDPOINT"]
    api_key = os.environ["AZURE_VOICELIVE_API_KEY"]
    model = os.environ.get("AZURE_VOICELIVE_MODEL", "gpt-realtime")

    credential = AzureKeyCredential(api_key)

    with tracer.start_as_current_span(scenario):
        async with connect(
            endpoint=endpoint,
            credential=credential,
            model=model,
        ) as connection:
            print(f"Connected to VoiceLive at {endpoint}")

            # Configure session
            session_config = RequestSession(
                modalities=[Modality.TEXT],
                instructions="You are a helpful assistant. Say hello briefly.",
                turn_detection=ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=500),
                output_audio_format=OutputAudioFormat.PCM16,
            )
            await connection.session.update(session=session_config)
            print("Session configured.")

            # Send a user message
            await connection.conversation.item.create(
                item=UserMessageItem(content=[InputTextContentPart(text="Hello, tell me a joke")])
            )
            await connection.response.create()
            print("User message sent.")

            # Receive events
            async for event in connection:
                event_type = getattr(event, "type", None)
                print(f"Received event: {event_type}")

                if event_type == ServerEventType.RESPONSE_DONE:
                    print("Response complete.")
                    break

        print("Connection closed.")

    # Flush remaining spans
    tracer_provider.force_flush()
    tracer_provider.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
