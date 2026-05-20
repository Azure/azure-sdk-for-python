# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use VoiceLive operations with console tracing
    and content recording enabled. When content recording is enabled, the full
    message payloads (send and receive) are captured in span events as
    gen_ai.event.content attributes.

    WARNING: Content recording may capture personal data. Only enable in
    development or controlled environments.

USAGE:
    python sample_voicelive_with_content_recording.py

    Before running the sample:

    pip install azure-ai-voicelive azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry

    Set these environment variables with your own values:
    1) AZURE_VOICELIVE_ENDPOINT - The Azure VoiceLive endpoint URL.
    2) AZURE_VOICELIVE_API_KEY - The Azure VoiceLive API key.
    3) AZURE_VOICELIVE_MODEL - The model deployment name (e.g., gpt-realtime).
    4) AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING - Set to "true" to enable tracing.
"""

import asyncio
import os

from azure.core.settings import settings

settings.tracing_implementation = "opentelemetry"

# Setup tracing to console
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

span_exporter = ConsoleSpanExporter()
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

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

# Enable tracing with content recording
os.environ.setdefault("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "true")

# [START enable_content_recording]
# Option 1: Enable via environment variable
# os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "true"

# Option 2: Enable programmatically
VoiceLiveInstrumentor().instrument(enable_content_recording=True)
# [END enable_content_recording]

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

            # Configure session — the full session config payload will appear
            # in the span event as gen_ai.event.content.
            session_config = RequestSession(
                modalities=[Modality.TEXT],
                instructions="You are a helpful assistant. Say hello briefly.",
                turn_detection=ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=500),
                output_audio_format=OutputAudioFormat.PCM16,
            )
            await connection.session.update(session=session_config)
            print("Session configured.")

            # Send a user message — the full message content will be captured.
            await connection.conversation.item.create(
                item=UserMessageItem(content=[InputTextContentPart(text="Hello, tell me a joke")])
            )
            await connection.response.create()
            print("User message sent.")

            # Receive events — the full event payloads will be captured.
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
