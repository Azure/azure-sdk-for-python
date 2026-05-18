# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic VoiceLive operations with
    Azure Monitor tracing. View the results in the "Tracing" tab in your
    Azure AI Foundry project page or in Application Insights.

USAGE:
    python sample_voicelive_with_azure_monitor_tracing.py

    Before running the sample:

    pip install azure-ai-voicelive azure-identity azure-monitor-opentelemetry

    Set these environment variables with your own values:
    1) AZURE_VOICELIVE_ENDPOINT - The Azure VoiceLive endpoint URL.
    2) AZURE_VOICELIVE_API_KEY - The Azure VoiceLive API key.
    3) AZURE_VOICELIVE_MODEL - The model deployment name (e.g., gpt-realtime).
    4) AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING - Set to "true" to enable tracing.
    5) APPLICATIONINSIGHTS_CONNECTION_STRING - The connection string for your Application Insights resource.
    6) OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT - Optional. Set to "true" to trace the content of
       messages, which may contain personal data. False by default.
"""

import asyncio
import os

from azure.core.settings import settings

settings.tracing_implementation = "opentelemetry"

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

# [START enable_tracing]
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

# Enable Azure Monitor tracing
application_insights_connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
configure_azure_monitor(connection_string=application_insights_connection_string)

# Enable VoiceLive tracing - requires AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING=true
os.environ.setdefault("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "true")
VoiceLiveInstrumentor().instrument()
# [END enable_tracing]

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)


async def main() -> None:
    endpoint = os.environ["AZURE_VOICELIVE_ENDPOINT"]
    api_key = os.environ["AZURE_VOICELIVE_API_KEY"]
    model = os.environ.get("AZURE_VOICELIVE_MODEL", "gpt-realtime")

    credential = AzureKeyCredential(api_key)

    with tracer.start_as_current_span(scenario):
        # The connect() call is traced automatically — a "connect" span is created.
        async with connect(
            endpoint=endpoint,
            credential=credential,
            model=model,
        ) as connection:
            print(f"Connected to VoiceLive at {endpoint}")

            # Configure session — produces a "send session.update" span.
            session_config = RequestSession(
                modalities=[Modality.TEXT],
                instructions="You are a helpful assistant. Say hello briefly.",
                turn_detection=ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=500),
                output_audio_format=OutputAudioFormat.PCM16,
            )
            await connection.session.update(session=session_config)
            print("Session configured.")

            # Send a user message — traced as a "send" span.
            await connection.conversation.item.create(
                item=UserMessageItem(content=[InputTextContentPart(text="Hello, tell me a joke")])
            )
            await connection.response.create()
            print("User message sent.")

            # Receive events — each recv() call produces a "recv" span.
            async for event in connection:
                event_type = getattr(event, "type", None)
                print(f"Received event: {event_type}")

                if event_type == ServerEventType.RESPONSE_DONE:
                    print("Response complete.")
                    break

        # Exiting the async context manager closes the connection and ends the connect span.
        print("Connection closed.")


if __name__ == "__main__":
    asyncio.run(main())
