# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: sample_live_audio_conversation_async.py

DESCRIPTION:
    End-to-end hands-free, bidirectional voice conversation using only the
    azure-ai-voiceagents SDK (REST management + realtime streaming):

      1. Create an agent with ``store = true`` so conversations persist.
      2. Publish a new version.
      3. Open a realtime session, stream live microphone audio, and let server
         VAD detect your turns. Your speech is transcribed, the agent replies
         through the speakers, and talking over it barges in.
      4. Read the persisted conversation back.
      5. Delete the agent.

    Uses non-blocking pyaudio callbacks for capture and playback; reply audio is
    sequence-numbered so a barge-in can skip whatever is still queued. The GA
    session schema configures ``server_vad`` (with an activation threshold) and
    deep noise suppression on the input. For no echo on speakers, use a headset.

    Audio both ways is base64 PCM16, mono, 24 kHz. Requires ``pyaudio``.

      pip install azure-ai-voiceagents aiohttp azure-identity pyaudio

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

PREVIEW: Final = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

# Audio is streamed both ways as PCM16, mono, 24 kHz.
_SAMPLE_RATE: Final = 24000

# pyaudio callback buffer size (~50 ms of PCM16 audio per callback).
_CHUNK_SAMPLES: Final = 1200

try:
    import pyaudio
except ImportError:  # pragma: no cover - required audio dependency
    pyaudio = None  # type: ignore[assignment]


class _AudioProcessor:
    """Real-time microphone capture and speaker playback via non-blocking pyaudio callbacks.

    * Capture base64-encodes each frame and appends it to the input buffer.
    * Playback pulls sequence-numbered PCM16 from a queue, always handing pyaudio
      exactly the sample count it asked for (wrong size corrupts audio).
    * ``skip_pending_audio`` bumps a "base" sequence number so audio queued before
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
    client: VoiceAgentsClient,
    agent_name: str,
) -> Optional[str]:
    """Hold a live, hands-free conversation with barge-in; return the persisted conversation id."""
    if pyaudio is None:
        print("This sample needs pyaudio for audio: pip install pyaudio")
        return None

    conversation_id: Optional[str] = None

    async with client.realtime.connect(
        agent_name=agent_name,
        foundry_features=PREVIEW,
    ) as conn:
        # Configure the session (GA schema): server_vad turn detection (an
        # activation threshold avoids phantom turns from noise) plus deep noise
        # suppression on the input audio.
        try:
            await conn.session.update(
                session={
                    "type": "realtime",
                    "audio": {
                        "input": {
                            "noise_reduction": {"type": "azure_deep_noise_suppression"},
                            "turn_detection": {
                                "type": "server_vad",
                                "threshold": 0.5,
                                "prefix_padding_ms": 300,
                                "silence_duration_ms": 500,
                            },
                        }
                    },
                }
            )
        except HttpResponseError as e:
            print(f"(session config not applied: {e.status_code} {e.reason})")

        ap = _AudioProcessor(conn)
        ap.start_playback()
        ap.start_capture()

        print("Speak now -- the agent replies after you pause.")
        print("(talk over the agent to interrupt it; press Ctrl-C to end the session)")

        try:
            async for event in conn:
                event_type = event.get("type")
                if event_type == "conversation.created":
                    # Only ``conversation.created`` carries the persisted id;
                    # the id on ``response.done`` is a per-turn runtime id.
                    conversation_id = event.get("conversation_id") or conversation_id
                    print(f"(conversation.created -> persisted id: {conversation_id})")
                elif event_type == "input_audio_buffer.speech_started":
                    # Barge-in: drop whatever reply audio is still queued.
                    ap.skip_pending_audio()
                    print("(listening...)")
                elif event_type == "conversation.item.input_audio_transcription.completed":
                    print(f"You:   {event.get('transcript', '').strip()}")
                elif event_type in ("response.output_audio.delta", "response.audio.delta"):
                    ap.queue_audio(base64.b64decode(event.get("delta", "")))
                elif event_type in (
                    "response.output_audio_transcript.done",
                    "response.audio_transcript.done",
                ):
                    print(f"Agent: {event.get('transcript', '')}")
                elif event_type == "error":
                    # Non-fatal errors are reported and ignored; a fatal error
                    # closes the socket, ending this loop on its own.
                    error = event.get("error") or {}
                    print(f"Session error: {error.get('message', error)}")
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
        created_agent = False
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
            created_agent = True
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
            conversation_id = await _run_audio_conversation(client, agent_name)

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
            if created_agent:
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
