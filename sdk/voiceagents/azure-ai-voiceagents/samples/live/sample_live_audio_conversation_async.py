# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: sample_live_audio_conversation_async.py

DESCRIPTION:
    End-to-end hands-free, bidirectional voice conversation. Management (create/
    version/read/delete) uses azure-ai-voiceagents; the realtime session uses
    azure-ai-voicelive against the same voice-agent endpoint, exchanging
    strongly-typed events.

      1. Create an agent with ``store=True`` so conversations persist.
      2. Publish a new version.
      3. Stream live mic audio and let the agent's server-side VAD detect your
         turns: your speech is transcribed, the agent replies through the
         speakers, and talking over it barges in.
      4. Read the persisted conversation back.
      5. Delete the agent.

    Capture and playback use non-blocking pyaudio callbacks; reply audio is
    sequence-numbered so a barge-in can skip whatever is still queued. The agent
    owns turn detection and noise suppression server-side, so no session config
    is sent. Use a headset to avoid echo.

    Mic audio is sent as base64 PCM16; the reply arrives as typed
    ``response.audio.*`` events, decoded to PCM16, mono, 24 kHz. Requires
    ``pyaudio``.

      pip install azure-ai-voiceagents azure-ai-voicelive[aiohttp] azure-identity pyaudio

USAGE:
    python sample_live_audio_conversation_async.py

    Environment variables:
    1) AZURE_VOICE_AGENTS_ENDPOINT (required) - Foundry project endpoint:
       https://<account>.services.ai.azure.com/api/projects/<project>
    2) AZURE_VOICE_AGENTS_MODEL (optional) - realtime deployment. Default "gpt-realtime".

    Runs until you press Ctrl-C. Authenticates with DefaultAzureCredential, so
    sign in first (e.g. `az login`).
"""

import asyncio
import base64
import os
import queue
from typing import Any, Final, Optional
from urllib.parse import urlparse, urlunparse

import aiohttp
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import AioHttpTransport
from azure.identity.aio import DefaultAzureCredential

from azure.ai.voiceagents.aio import VoiceAgentsClient
from azure.ai.voiceagents.models import (
    AgentDefinitionOptInKeys,
    VoiceAgentDefinition,
    VoiceOutputModality,
)
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    ServerEventConversationItemInputAudioTranscriptionCompleted,
    ServerEventError,
    ServerEventInputAudioBufferSpeechStarted,
    ServerEventResponseAudioDelta,
    ServerEventResponseAudioTranscriptDone,
)

PREVIEW: Final = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

# Opt into the gated preview via this handshake header.
_FOUNDRY_FEATURES: Final = {"Foundry-Features": "VoiceAgents=V1Preview"}

# Preview API version that streams the reply as typed ``response.audio.*`` events.
_REALTIME_API_VERSION: Final = "2025-11-15-preview"

# Audio is streamed both ways as PCM16, mono, 24 kHz.
_SAMPLE_RATE: Final = 24000

# pyaudio callback buffer size (~50 ms of PCM16 audio per callback).
_CHUNK_SAMPLES: Final = 1200


def _voice_agent_realtime_url(project_endpoint: str, agent_name: str) -> str:
    """Build the WebSocket URL for a voice agent's dedicated realtime route."""
    parsed = urlparse(project_endpoint)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    path = parsed.path.rstrip("/") + f"/agents/{agent_name}/endpoint/protocols/voice"
    return urlunparse((scheme, parsed.netloc, path, "", f"api-version={_REALTIME_API_VERSION}", ""))

try:
    import pyaudio
except ImportError:  # pragma: no cover - required audio dependency
    pyaudio = None  # type: ignore[assignment]


class _AudioProcessor:
    """Real-time mic capture and speaker playback via non-blocking pyaudio callbacks.

    * Capture base64-encodes each frame and appends it to the input buffer.
    * Playback pulls sequence-numbered PCM16 from a queue, always returning the
      exact sample count pyaudio asked for (a wrong size corrupts audio).
    * ``skip_pending_audio`` bumps a base sequence number so audio queued before
      a barge-in is dropped, stopping playback the instant the user speaks.
    """

    def __init__(self, connection: Any) -> None:
        self._conn = connection
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._audio = pyaudio.PyAudio()

        # Playback with sequence numbers for interrupt handling.
        self._playback_queue: "queue.Queue[tuple[int, Optional[bytes]]]" = queue.Queue()
        self._playback_base = 0
        self._next_seq = 0
        self._bytes = 0

        self._input_stream = None
        self._output_stream = None

    # -- capture -----------------------------------------------------------

    def start_capture(self) -> None:
        """Start streaming microphone audio to the service via a callback."""
        if self._input_stream is not None:
            return
        self._loop = asyncio.get_running_loop()

        def _capture_callback(in_data, _frame_count, _time_info, _status):
            # Runs on a pyaudio thread: hand the frame to the event loop to append.
            audio_b64 = base64.b64encode(in_data).decode("utf-8")
            assert self._loop is not None
            asyncio.run_coroutine_threadsafe(
                self._conn.input_audio_buffer.append(audio=audio_b64), self._loop
            )
            return (None, pyaudio.paContinue)

        self._input_stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=_SAMPLE_RATE,
            input=True,
            frames_per_buffer=_CHUNK_SAMPLES,
            stream_callback=_capture_callback,
        )

    # -- playback ----------------------------------------------------------

    def start_playback(self) -> None:
        """Initialize the speaker playback callback."""
        if self._output_stream is not None:
            return
        remaining = b""

        def _playback_callback(_in_data, frame_count, _time_info, _status):
            nonlocal remaining
            wanted = frame_count * pyaudio.get_sample_size(pyaudio.paInt16)
            out = remaining[:wanted]
            remaining = remaining[wanted:]

            while len(out) < wanted:
                try:
                    seq, data = self._playback_queue.get_nowait()
                except queue.Empty:
                    out = out + bytes(wanted - len(out))  # pad with silence
                    continue
                if not data:
                    break  # end-of-stream marker
                if seq < self._playback_base:
                    remaining = b""  # skipped by a barge-in
                    continue
                take = wanted - len(out)
                out = out + data[:take]
                remaining = data[take:]

            return (out, pyaudio.paContinue)

        self._output_stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=_SAMPLE_RATE,
            output=True,
            frames_per_buffer=_CHUNK_SAMPLES,
            stream_callback=_playback_callback,
        )

    def _next_seq_num(self) -> int:
        seq = self._next_seq
        self._next_seq += 1
        return seq

    def queue_audio(self, pcm: bytes) -> None:
        """Queue one decoded PCM16 chunk of the agent's reply for playback."""
        self._bytes += len(pcm)
        self._playback_queue.put((self._next_seq_num(), pcm))

    def skip_pending_audio(self) -> None:
        """Drop audio still queued for playback (used on barge-in)."""
        self._playback_base = self._next_seq_num()

    def shutdown(self) -> None:
        """Stop capture and playback and release the audio device."""
        if self._input_stream is not None:
            self._input_stream.stop_stream()
            self._input_stream.close()
            self._input_stream = None
        if self._output_stream is not None:
            self.skip_pending_audio()
            self._playback_queue.put((self._next_seq_num(), None))
            self._output_stream.stop_stream()
            self._output_stream.close()
            self._output_stream = None
        self._audio.terminate()

    @property
    def seconds(self) -> float:
        """Total reply audio received, in seconds (PCM16 = 2 bytes/sample)."""
        return self._bytes / 2 / _SAMPLE_RATE


async def _run_audio_conversation(
    project_endpoint: str,
    credential: DefaultAzureCredential,
    agent_name: str,
) -> Optional[str]:
    """Hold a live, hands-free conversation with barge-in; return the persisted conversation id."""
    if pyaudio is None:
        print("This sample needs pyaudio for audio: pip install pyaudio")
        return None

    conversation_id: Optional[str] = None

    # Open the realtime session on the voice agent's dedicated route. The
    # voicelive ``connect`` provides the typed event stream and auth; point it
    # at the agent URL built above (its default route is a non-agent one).
    session = connect(
        credential=credential,
        endpoint=project_endpoint,
        api_version=_REALTIME_API_VERSION,
        headers=_FOUNDRY_FEATURES,
    )
    agent_url = _voice_agent_realtime_url(project_endpoint, agent_name)
    session._prepare_url = lambda: agent_url  # type: ignore[attr-defined]
    async with session as conn:
        # A voice agent owns its model, instructions, voice, turn detection, and
        # noise suppression server-side, so this client sends no ``session.update``.
        ap = _AudioProcessor(conn)
        ap.start_playback()
        ap.start_capture()

        print("Speak now -- the agent replies after you pause.")
        print("(talk over the agent to interrupt it; press Ctrl-C to end the session)")

        try:
            async for event in conn:
                # Every server event is strongly typed by voicelive.
                if isinstance(event, ServerEventInputAudioBufferSpeechStarted):
                    # Barge-in: drop whatever reply audio is still queued.
                    ap.skip_pending_audio()
                    print("(listening...)")
                elif isinstance(event, ServerEventConversationItemInputAudioTranscriptionCompleted):
                    print(f"You:   {event.transcript.strip()}")
                elif isinstance(event, ServerEventError):
                    # Non-fatal errors are reported; a fatal one closes the socket.
                    print(f"Session error: {event.error.message}")
                elif isinstance(event, ServerEventResponseAudioDelta):
                    # Each delta is a decoded PCM16 chunk; queue it.
                    ap.queue_audio(event.delta)
                elif isinstance(event, ServerEventResponseAudioTranscriptDone):
                    print(f"Agent: {event.transcript}")
                elif event.type == "conversation.created":
                    # Carries the persisted id (untyped in this build).
                    conversation_id = event.get("conversation_id") or conversation_id
                    print(f"(conversation.created -> persisted id: {conversation_id})")
        except (KeyboardInterrupt, asyncio.CancelledError):
            # Ctrl-C ends the session; read back whatever was persisted so far.
            print("\n(ending session...)")
        finally:
            print(f"(received {ap.seconds:.2f}s of reply audio this session)")
            ap.shutdown()

    return conversation_id


async def _read_conversation(client: VoiceAgentsClient, agent_name: str, conversation_id: str) -> None:
    """Read the persisted conversation back over the read-only conversation API."""
    conversations = client.agent_endpoint_conversations

    conversation = await conversations.get_agent_conversation(
        agent_name, conversation_id, foundry_features=PREVIEW
    )
    print(f"Conversation {conversation.id}: status={conversation.status}, created_at={conversation.created_at}")

    print("Items (transcript):")
    async for item in conversations.list_agent_conversation_items(
        agent_name, conversation_id, foundry_features=PREVIEW
    ):
        role = item.get("role") or item.get("type")
        # Audio turns expose ``transcript``; text turns expose ``text``.
        parts = [
            (part.get("transcript") or part.get("text") or "").strip()
            for part in (item.get("content") or [])
        ]
        transcript = " ".join(p for p in parts if p)
        print(f"  - {role} id={item.get('id')}")
        if transcript:
            print(f"      {transcript}")


async def audio_conversation() -> None:
    project_endpoint = os.environ["AZURE_VOICE_AGENTS_ENDPOINT"]
    model = os.environ.get("AZURE_VOICE_AGENTS_MODEL", "gpt-realtime")
    agent_name = "sample-audio-agent"

    credential = DefaultAzureCredential()
    # Foundry may return Brotli responses (Content-Encoding: br) that aiohttp
    # won't decode; ask only for gzip/deflate so the transport handles it.
    transport = AioHttpTransport(
        session=aiohttp.ClientSession(auto_decompress=False, headers={"Accept-Encoding": "gzip, deflate"})
    )

    async with credential, VoiceAgentsClient(
        endpoint=project_endpoint, credential=credential, transport=transport
    ) as client:
        conversation_id: Optional[str] = None
        try:
            # 1) Create the agent. `store = true` persists conversations for later reading.
            await client.voice_agents.create_voice_agent(
                name=agent_name,
                definition=VoiceAgentDefinition(
                    model_type="managed",
                    model=model,
                    instructions="You are a friendly voice assistant. Keep replies short.",
                    output_modalities=[VoiceOutputModality.TEXT, VoiceOutputModality.AUDIO],
                    store=True,
                ),
                description="Created by the azure-ai-voiceagents audio conversation sample.",
                foundry_features=PREVIEW,
            )
            print(f"Created voice agent: {agent_name}")

            # 2) Publish a new version with refined instructions.
            new_version = await client.voice_agents.create_voice_agent_version(
                agent_name,
                definition=VoiceAgentDefinition(
                    model_type="managed",
                    model=model,
                    instructions="You are a helpful voice assistant. Give concise, clear answers.",
                    output_modalities=[VoiceOutputModality.TEXT, VoiceOutputModality.AUDIO],
                    store=True,
                ),
                description="Refined instructions.",
                foundry_features=PREVIEW,
            )
            print(f"Published agent version: {new_version.version}")

            # 3) Hold a live microphone conversation with the agent.
            print("Starting realtime session...")
            conversation_id = await _run_audio_conversation(project_endpoint, credential, agent_name)

            # 4) Read the persisted conversation back with the voice-agents client.
            if conversation_id:
                print(f"Reading persisted conversation {conversation_id!r}...")
                try:
                    await _read_conversation(client, agent_name, conversation_id)
                except HttpResponseError as e:
                    body = getattr(e, "response", None)
                    text = body.text() if body is not None else ""
                    print(f"Could not read conversation: {e.status_code} {e.reason}\n{text}")
            else:
                print("No conversation id was returned; nothing to read.")
        except HttpResponseError as e:
            print(f"Service responded with an error: {e.status_code} {e.reason}")
        finally:
            # 5) Clean up: delete the agent.
            try:
                await client.voice_agents.delete_voice_agent(agent_name, foundry_features=PREVIEW)
                print(f"Deleted voice agent: {agent_name}")
            except HttpResponseError as e:
                print(f"Could not delete agent: {e.status_code} {e.reason}")


if __name__ == "__main__":
    try:
        asyncio.run(audio_conversation())
    except KeyboardInterrupt:
        print("\nInterrupted.")
