# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: sample_quickstart_async.py

DESCRIPTION:
    Generate a temporary voice agent, start a live microphone/speaker realtime
    conversation with it, then delete the agent when the sample exits.

    This is the shortest end-to-end path for trying voice agents with live audio:
    management API for agent setup, realtime WebSocket API for the conversation.

    Requires ``pyaudio`` for microphone capture and speaker playback.

      pip install azure-ai-voiceagents azure-identity aiohttp pyaudio

USAGE:
    python sample_quickstart_async.py

    Environment variables:
    1) AZURE_VOICE_AGENTS_ENDPOINT (required) - Foundry project endpoint:
       https://<account>.services.ai.azure.com/api/projects/<project>
    2) AZURE_VOICE_AGENTS_MODEL (optional) - realtime model deployment name.
       Defaults to "gpt-realtime".

    Runs until you press Ctrl-C. Authenticates with DefaultAzureCredential, so
    sign in first (for example, with `az login`).
"""

import asyncio
import os
import queue
import uuid
from typing import Any, Final, Optional

from azure.core.exceptions import HttpResponseError
from azure.identity.aio import DefaultAzureCredential

from azure.ai.voiceagents.aio import AsyncRealtimeConnection, VoiceAgentsClient
from azure.ai.voiceagents.models import (
    AgentDefinitionOptInKeys,
    VoiceAgentType,
    VoiceAgentUseCase,
    VoiceAgentServerEventConversationItemInputAudioTranscriptionCompleted,
    VoiceAgentServerEventError,
    VoiceAgentServerEventInputAudioBufferSpeechStarted,
    VoiceAgentServerEventResponseAudioDelta,
    VoiceAgentServerEventResponseAudioTranscriptDone,
    VoiceModelType,
)

PREVIEW: Final = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW
_SAMPLE_RATE: Final = 24000
_CHUNK_SAMPLES: Final = 1200

try:
    import pyaudio  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - required audio dependency
    pyaudio: Any = None  # type: ignore[no-redef]


class _AudioProcessor:
    def __init__(self, connection: AsyncRealtimeConnection) -> None:
        self._conn = connection
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._audio = pyaudio.PyAudio()
        self._playback_queue: "queue.Queue[tuple[int, Optional[bytes]]]" = queue.Queue()
        self._playback_base = 0
        self._next_seq = 0
        self._input_stream = None
        self._output_stream = None

    def start(self) -> None:
        self._loop = asyncio.get_running_loop()

        def capture_callback(in_data, _frame_count, _time_info, _status):
            assert self._loop is not None
            asyncio.run_coroutine_threadsafe(self._conn.input_audio_buffer.append(audio=in_data), self._loop)
            return (None, pyaudio.paContinue)

        self._input_stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=_SAMPLE_RATE,
            input=True,
            frames_per_buffer=_CHUNK_SAMPLES,
            stream_callback=capture_callback,
        )

        remaining = b""

        def playback_callback(_in_data, frame_count, _time_info, _status):
            nonlocal remaining
            wanted = frame_count * pyaudio.get_sample_size(pyaudio.paInt16)
            out = remaining[:wanted]
            remaining = remaining[wanted:]

            while len(out) < wanted:
                try:
                    seq, data = self._playback_queue.get_nowait()
                except queue.Empty:
                    out += bytes(wanted - len(out))
                    continue
                if data is None:
                    break
                if seq < self._playback_base:
                    remaining = b""
                    continue
                take = wanted - len(out)
                out += data[:take]
                remaining = data[take:]

            return (out, pyaudio.paContinue)

        self._output_stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=_SAMPLE_RATE,
            output=True,
            frames_per_buffer=_CHUNK_SAMPLES,
            stream_callback=playback_callback,
        )

    def queue_audio(self, pcm: bytes) -> None:
        self._playback_queue.put((self._next_seq_num(), pcm))

    def skip_pending_audio(self) -> None:
        self._playback_base = self._next_seq_num()

    def close(self) -> None:
        if self._input_stream is not None:
            self._input_stream.stop_stream()
            self._input_stream.close()
        if self._output_stream is not None:
            self.skip_pending_audio()
            self._playback_queue.put((self._next_seq_num(), None))
            self._output_stream.stop_stream()
            self._output_stream.close()
        self._audio.terminate()

    def _next_seq_num(self) -> int:
        seq = self._next_seq
        self._next_seq += 1
        return seq


async def _generate_agent(client: VoiceAgentsClient, model: str) -> str:
    agent_name = f"sample-quickstart-agent-{uuid.uuid4().hex[:8]}"
    agent = await client.voice_agents.generate_voice_agent(
        name=agent_name,
        model_type=VoiceModelType.MANAGED,
        model=model,
        agent_type=VoiceAgentType.BUSINESS,
        use_case=VoiceAgentUseCase.CUSTOMER_SUPPORT,
        goal="Answer questions in a friendly voice. Keep replies short and natural.",
        description="Temporary agent generated by the azure-ai-voiceagents quickstart.",
        foundry_features=PREVIEW,
    )
    print(f"Generated temporary voice agent: {agent.name}")
    return agent.name


async def _delete_agent(client: VoiceAgentsClient, agent_name: str) -> None:
    try:
        await client.voice_agents.delete_voice_agent(agent_name, foundry_features=PREVIEW)
    except HttpResponseError as exc:
        if exc.response is None or exc.response.status_code != 200:
            raise
    print(f"Deleted temporary voice agent: {agent_name}")


async def _run_audio_session(client: VoiceAgentsClient, agent_name: str) -> None:
    async with client.realtime.connect(agent_name=agent_name) as conn:
        audio = _AudioProcessor(conn)
        audio.start()
        print("Speak now. Talk over the agent to interrupt it. Press Ctrl-C to stop.")

        try:
            async for event in conn:
                if isinstance(event, VoiceAgentServerEventInputAudioBufferSpeechStarted):
                    # Cancel the in-flight response before dropping audio that is
                    # still queued in the local speaker buffer. The service only
                    # supports output_audio_buffer.clear in avatar mode.
                    await conn.response.cancel()
                    audio.skip_pending_audio()
                    print("(listening...)")
                elif isinstance(event, VoiceAgentServerEventConversationItemInputAudioTranscriptionCompleted):
                    print(f"You: {event.transcript.strip()}")
                elif isinstance(event, VoiceAgentServerEventResponseAudioDelta):
                    audio.queue_audio(event.delta)
                elif isinstance(event, VoiceAgentServerEventResponseAudioTranscriptDone):
                    print(f"Agent: {event.transcript}")
                elif isinstance(event, VoiceAgentServerEventError):
                    print(f"Session error: {event.error.message}")
        finally:
            audio.close()


async def main() -> None:
    if pyaudio is None:
        print("This quickstart needs pyaudio for microphone and speaker audio: pip install pyaudio")
        return

    endpoint = os.environ["AZURE_VOICE_AGENTS_ENDPOINT"]
    model = os.environ.get("AZURE_VOICE_AGENTS_MODEL", "gpt-realtime")
    agent_name: Optional[str] = None

    async with DefaultAzureCredential() as credential, VoiceAgentsClient(
        endpoint=endpoint, credential=credential
    ) as client:
        try:
            agent_name = await _generate_agent(client, model)
            await _run_audio_session(client, agent_name)
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\nStopping quickstart...")
        finally:
            if agent_name is not None:
                await _delete_agent(client, agent_name)


if __name__ == "__main__":
    asyncio.run(main())
