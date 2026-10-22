# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample shows the minimum code changes needed to enable VoiceLive telemetry
    on top of existing VoiceLive client code.

USAGE:
    python sample_voicelive_with_telemetry_enablement.py

    Before running the sample:

    pip install azure-ai-voicelive azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry

    Set these environment variables with your own values:
    1) AZURE_VOICELIVE_ENDPOINT - The Azure VoiceLive endpoint URL.
    2) AZURE_VOICELIVE_MODEL - The model deployment name (e.g., gpt-realtime).

    Optional authentication variables:
    3) AZURE_VOICELIVE_USE_API_KEY - Set to "true" to use AZURE_VOICELIVE_API_KEY instead of Entra ID.
    4) AZURE_VOICELIVE_API_KEY - The Azure VoiceLive API key used when AZURE_VOICELIVE_USE_API_KEY is enabled.

    Optional telemetry variables:
    5) AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING - Set to "true" to enable tracing.
    6) OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT - Optional. Set to "true" to include
       message content in telemetry events. False by default.
"""

import asyncio
import os
from typing import Union

from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.settings import settings
from azure.identity.aio import DefaultAzureCredential
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

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter


def enable_telemetry_minimal():
    """Enable telemetry with the smallest practical setup for existing code."""
    # Add these lines to your existing app to enable VoiceLive telemetry.
    # 1) Tell azure-core to use OpenTelemetry tracing.
    settings.tracing_implementation = "opentelemetry"

    # 2) Configure a tracer provider and exporter (console in this sample).
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)

    # 3) Enable the VoiceLive instrumentation gate and instrument the SDK.
    os.environ.setdefault("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "true")
    VoiceLiveInstrumentor().instrument()

    return provider


async def main() -> None:
    tracer_provider = enable_telemetry_minimal()

    endpoint = os.environ["AZURE_VOICELIVE_ENDPOINT"]
    model = os.environ.get("AZURE_VOICELIVE_MODEL", "gpt-realtime")
    use_api_key = os.environ.get("AZURE_VOICELIVE_USE_API_KEY", "").strip().lower() in {"1", "true", "yes"}
    api_key = os.environ.get("AZURE_VOICELIVE_API_KEY")

    credential: Union[AzureKeyCredential, AsyncTokenCredential]
    if use_api_key:
        if not api_key:
            raise RuntimeError("AZURE_VOICELIVE_API_KEY must be set when AZURE_VOICELIVE_USE_API_KEY=true.")
        credential = AzureKeyCredential(api_key)
    else:
        credential = DefaultAzureCredential()

    try:
        async with connect(
            endpoint=endpoint,
            credential=credential,
            model=model,
        ) as connection:
            print(f"Connected to VoiceLive at {endpoint}")

            session_config = RequestSession(
                modalities=[Modality.TEXT],
                instructions="You are a helpful assistant. Keep the answer short.",
                turn_detection=ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=500),
                output_audio_format=OutputAudioFormat.PCM16,
            )
            await connection.session.update(session=session_config)

            await connection.conversation.item.create(
                item=UserMessageItem(content=[InputTextContentPart(text="Say hello in one sentence")])
            )
            await connection.response.create()

            async for event in connection:
                event_type = getattr(event, "type", None)
                print(f"Received event: {event_type}")
                if event_type == ServerEventType.RESPONSE_DONE:
                    break
    finally:
        if isinstance(credential, AsyncTokenCredential):
            await credential.close()
        tracer_provider.force_flush()
        tracer_provider.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
