# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Trace preview Voice Agent REST and realtime operations to the console using
    the existing AIProjectInstrumentor. Create/read an agent, send one public
    text prompt, receive audio and its transcript, read/delete the persisted
    conversation, and delete the agent version in finally.

    Tracing uses the global Foundry enablement and content-recording settings.

    Console spans show one application trace containing REST spans and
    voice_agents.realtime.session, voice_agents.realtime.connect, and
    invoke_agent spans. Realtime diagnostic logs show event types and sizes,
    not raw audio. No microphone, speaker, or remote exporter is required.

USAGE:
    python sample_voice_agent_with_tracing.py

    From the package root of this updated source checkout:
    pip install -e ".[voice]"
    pip install azure-identity python-dotenv
    pip install opentelemetry-sdk azure-core-tracing-opentelemetry
    When released, "azure-ai-projects[voice]>=2.9.0" can replace the editable install.

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - Your Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL - Optional managed model; defaults to "gpt-realtime".
    3) FOUNDRY_VOICE_AGENT_NAME - Optional name for the sample agent. Defaults to
       a unique "sample-voice-agent-with-tracing-<suffix>" name.
    4) AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING - Set to "true" to enable Foundry
       GenAI instrumentation. Without it, only ordinary Core/application tracing remains.
    5) OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT - Optional. "true"
       enables bounded message/tool content in spans; defaults to false.

    Sign in with your usual DefaultAzureCredential authentication. Run this
    standalone so the sample owns its console tracing provider. The application
    prints the public example transcript independently of content recording.
"""

import logging
import os
import time
import uuid
from typing import Final

from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline import PipelineResponse
from azure.core.settings import settings
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    RealtimeAudioFormatsAudioPcm,
    RealtimeConversationItemMessageUser,
    RealtimeConversationItemMessageUserContent,
    RealtimeConversationItemType,
    RealtimeServerEventError,
    RealtimeServerEventResponseAudioDelta,
    RealtimeServerEventResponseAudioTranscriptDone,
    RealtimeServerEventResponseDone,
    RealtimeServerEventSessionCreated,
    VoiceAgentAudioConfig,
    VoiceAgentAudioOutputConfig,
    VoiceAgentDefinition,
    VoiceModelType,
    VoiceOutputModality,
    VoiceType,
)
from azure.ai.projects.telemetry import AIProjectInstrumentor

load_dotenv()

_SAMPLE_RATE: Final = 24000
_RESPONSE_TIMEOUT: Final = 60


def _print_http_status(response: PipelineResponse) -> None:
    """Print request metadata without headers, bodies, or query values.

    :param response: The REST pipeline response.
    :type response: ~azure.core.pipeline.PipelineResponse
    """
    print(f"HTTP {response.http_request.method} -> {response.http_response.status_code}")


def _stream_reply(project_client: AIProjectClient, agent_name: str) -> str:
    """Stream a public text prompt's audio reply and return its conversation ID.

    :param project_client: The Foundry project client.
    :type project_client: ~azure.ai.projects.AIProjectClient
    :param agent_name: The sample's voice agent name.
    :type agent_name: str
    :return: The persisted conversation ID.
    :rtype: str
    """
    audio_bytes = 0
    transcript = ""
    conversation_id = None
    with project_client.beta.voice_agents.realtime.connect(agent_name=agent_name) as connection:
        connection.conversation.item.create(
            item=RealtimeConversationItemMessageUser(
                type=RealtimeConversationItemType.MESSAGE,
                content=[
                    RealtimeConversationItemMessageUserContent(
                        type="input_text", text="What is two plus three? Answer in one short sentence."
                    )
                ],
            )
        )
        connection.response.create()
        deadline = time.monotonic() + _RESPONSE_TIMEOUT
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("The voice response did not finish within 60 seconds.")
            event = connection.recv(timeout=remaining)
            if isinstance(event, RealtimeServerEventSessionCreated):
                conversation_id = event.conversation_id
                print(f"Received session.created: conversation={conversation_id}")
            elif isinstance(event, RealtimeServerEventResponseAudioDelta):
                audio_bytes += len(event.delta)
            elif isinstance(event, RealtimeServerEventResponseAudioTranscriptDone):
                transcript = event.transcript
                print(f"Transcript: {transcript}")
            elif isinstance(event, RealtimeServerEventError):
                raise RuntimeError("The realtime service returned an error. Inspect its error event.")
            elif isinstance(event, RealtimeServerEventResponseDone):
                print(f"Received response.done: status={event.response.status}")
                if event.response.status != "completed":
                    raise RuntimeError("The voice response did not complete successfully.")
                break
    if not audio_bytes or not transcript or not conversation_id:
        raise RuntimeError("Expected audio, transcript, and a persisted conversation ID.")
    print("Input audio: 0 bytes (the sample sends text)")
    print(f"Output audio: {audio_bytes} bytes ({audio_bytes / 1024:.2f} KB)")
    print(f"Total audio: {audio_bytes} bytes ({audio_bytes / 1024:.2f} KB)")
    print(f"Audio format: PCM16, mono, {_SAMPLE_RATE} Hz; duration={audio_bytes / (2 * _SAMPLE_RATE):.2f}s")
    return conversation_id


def main() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ.get("FOUNDRY_VOICE_AGENT_MODEL") or "gpt-realtime"
    agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or f"sample-voice-agent-with-tracing-{uuid.uuid4().hex[:8]}"

    settings.tracing_implementation = "opentelemetry"
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    instrumentor = AIProjectInstrumentor()
    logger = logging.getLogger("azure.ai.projects.realtime")
    previous_level = logger.level
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    try:
        instrumentor.instrument()
        print(f"Foundry GenAI tracing enabled: {instrumentor.is_instrumented()}")
        print(f"Message content recording: {instrumentor.is_content_recording_enabled()}")
        tracer = trace.get_tracer(__name__)
        with (
            tracer.start_as_current_span("sample_voice_agent_with_tracing") as application_span,
            DefaultAzureCredential() as credential,
            AIProjectClient(
                endpoint=endpoint, credential=credential, allow_preview=True, raw_response_hook=_print_http_status
            ) as project_client,
        ):
            print(f"Trace ID: {application_span.get_span_context().trace_id:032x}")
            created_version = None
            try:
                created_version = project_client.agents.create_version(
                    agent_name=agent_name,
                    definition=VoiceAgentDefinition(
                        model_type=VoiceModelType.MANAGED,
                        model=model,
                        instructions="You are a friendly voice assistant. Keep replies short.",
                        audio=VoiceAgentAudioConfig(
                            output=VoiceAgentAudioOutputConfig(
                                voice="en-US-AvaNeural",
                                voice_type=VoiceType.AZURE_STANDARD,
                                format=RealtimeAudioFormatsAudioPcm(rate=_SAMPLE_RATE),
                            )
                        ),
                        output_modalities=[VoiceOutputModality.AUDIO],
                        store=True,
                    ),
                )
                print(f"Created voice agent {agent_name}, version {created_version.version}")
                fetched = project_client.agents.get_version(
                    agent_name=agent_name, agent_version=created_version.version
                )
                print(f"Retrieved version {fetched.version}: kind={fetched.definition.kind}")

                conversation_id = _stream_reply(project_client, agent_name)
                conversations = project_client.beta.voice_agents.conversations
                for attempt in range(15):
                    try:
                        conversation = conversations.get(agent_name, conversation_id)
                        break
                    except ResourceNotFoundError:
                        if attempt == 14:
                            raise
                        time.sleep(1)
                print(f"Read persisted conversation {conversation.id}: status={conversation.status}")
                conversations.delete(agent_name, conversation_id)
                print(f"Deleted conversation {conversation_id}")
            finally:
                if created_version is not None:
                    project_client.agents.delete_version(agent_name=agent_name, agent_version=created_version.version)
                    print(f"Deleted voice agent version {created_version.version}")
    finally:
        instrumentor.uninstrument()
        provider.force_flush()
        provider.shutdown()
        logger.removeHandler(handler)
        handler.close()
        logger.setLevel(previous_level)


if __name__ == "__main__":
    main()
