# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Stream a real WAV recording to a preview GPT Live voice agent while receiving
    its speech concurrently. The input must contain spoken audio encoded as
    PCM16 little-endian, mono, 24 kHz. Only raw frames are sent, without the WAV
    header, in paced 50 ms chunks followed by one second of silence.

    Aggregate audio byte counts and any emitted input/output transcripts are
    displayed. Live has no speech-finished event: after sending finishes, this
    bounded demonstration stops after three seconds without non-silent reply
    audio or nonblank output transcript updates. This is an inactivity heuristic;
    a long speech pause can still split a reply. Low-level PCM with peak
    amplitude at or below 256 does not restart the timer or count as a reply.
    Captured PCM, including silence, is still counted and optionally saved.
    Client-owned delegations are answered with commentary tied to their ID.

USAGE:
    python sample_voice_agent_live_audio_conversation_async.py

    pip install "azure-ai-projects[voice]" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (required) - Your GPT Live DEPLOYMENT name.
    3) FOUNDRY_VOICE_AUDIO_INPUT_PATH (required) - Path to an actual spoken-audio
       WAV file: uncompressed PCM16, mono, 24000 Hz. No microphone is needed.
    4) FOUNDRY_VOICE_AUDIO_OUTPUT_PATH (optional) - Explicit WAV output path.
       When set, saves actual returned audio, not telemetry. Without it no audio
       file is written. The path must differ from the input path.
    5) FOUNDRY_VOICE_AGENT_NAME (optional) - Prefix for a uniquely named sample
       agent. Only the version created by this run is deleted.

    Authenticates with DefaultAzureCredential. No audio-device dependency.
    Choose a short recording; Ctrl-C cancels local tasks and closes the session.
    Conversation persistence is disabled; explicitly saving audio still writes
    conversation content to your chosen local file.
"""

from __future__ import annotations

import asyncio
import base64
from contextlib import ExitStack
from dataclasses import dataclass
import os
from pathlib import Path
import time
from typing import Optional, TYPE_CHECKING
import wave

from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects import models

from live_sample_utils import (
    audio_settings,
    check_event,
    check_session_open,
    close_session_async,
    remaining_time,
    safe_print,
    sample_agent_name,
    wait_for_event_async,
)

if TYPE_CHECKING:
    from azure.ai.projects.aio.operations import AsyncBetaLiveConnection


_SAMPLE_RATE = 24000
_CHUNK_FRAMES = 1200
_OUTPUT_IDLE_SECONDS = 3.0
_SILENCE_PEAK_THRESHOLD = 256


@dataclass
class _AudioOutput:
    num_bytes: int = 0
    chunks: int = 0
    input_transcript: str = ""
    output_transcript: str = ""
    has_audio_activity: bool = False


def _has_audio_activity(pcm: bytes) -> bool:
    return any(
        abs(int.from_bytes(pcm[offset : offset + 2], "little", signed=True)) > _SILENCE_PEAK_THRESHOLD
        for offset in range(0, len(pcm), 2)
    )


def _validate_recording(recording: wave.Wave_read) -> None:
    if (
        recording.getnchannels() != 1
        or recording.getsampwidth() != 2
        or recording.getframerate() != _SAMPLE_RATE
        or recording.getcomptype() != "NONE"
    ):
        raise ValueError("FOUNDRY_VOICE_AUDIO_INPUT_PATH must be an uncompressed PCM16, mono, 24000 Hz WAV file.")
    if recording.getnframes() == 0:
        raise ValueError("The input WAV contains no audio frames.")


async def _send_audio(connection: AsyncBetaLiveConnection, recording: wave.Wave_read, finished: asyncio.Event) -> int:
    num_bytes = 0
    while chunk := recording.readframes(_CHUNK_FRAMES):
        await connection.session.input_audio.append(audio=chunk)
        num_bytes += len(chunk)
        await asyncio.sleep(len(chunk) / (2 * _SAMPLE_RATE))
    if num_bytes == 0:
        raise RuntimeError("No recorded audio frames were sent.")
    # Trailing silence lets the model finish the recorded speech turn.
    for _ in range(_SAMPLE_RATE // _CHUNK_FRAMES):
        silence = b"\x00\x00" * _CHUNK_FRAMES
        await connection.session.input_audio.append(audio=silence)
        num_bytes += len(silence)
        await asyncio.sleep(_CHUNK_FRAMES / _SAMPLE_RATE)
    finished.set()
    return num_bytes


async def _receive_audio(
    connection: AsyncBetaLiveConnection,
    finished: asyncio.Event,
    timeout: float,
    output_file: Optional[wave.Wave_write],
) -> _AudioOutput:
    output = _AudioOutput()
    deadline = time.monotonic() + timeout
    last_content = time.monotonic()
    while True:
        if finished.is_set() and output.has_audio_activity and time.monotonic() - last_content >= _OUTPUT_IDLE_SECONDS:
            return output
        remaining = remaining_time(deadline, "GPT Live reply audio")
        try:
            event = await asyncio.wait_for(connection.recv(), timeout=min(remaining, 1.0))
        except asyncio.TimeoutError:
            continue
        check_event(event)
        check_session_open(event)
        if isinstance(event, models.LiveOutputAudioDelta):
            pcm = base64.b64decode(event.delta, validate=True)
            if len(pcm) % 2:
                raise ValueError("The service returned an incomplete PCM16 sample.")
            output.num_bytes += len(pcm)
            output.chunks += 1
            if output_file is not None:
                output_file.writeframesraw(pcm)
            if _has_audio_activity(pcm):
                output.has_audio_activity = True
                last_content = time.monotonic()
        elif isinstance(event, models.LiveServerEventLiveInputTranscriptDelta):
            output.input_transcript += event.delta
        elif isinstance(event, models.LiveServerEventLiveOutputTranscriptDelta):
            output.output_transcript += event.delta
            if event.delta.strip():
                last_content = time.monotonic()
        elif isinstance(event, models.LiveServerEventLiveDelegationCreated):
            if event.delegation.target == "client":
                await connection.session.commentary.append(
                    content="This sample cannot look up external information. Briefly acknowledge the recorded request.",
                    delegation_id=event.delegation.id,
                )
                print("Replied to a client-owned delegation with associated commentary.")


async def _stream_recording(
    connection: AsyncBetaLiveConnection, recording: wave.Wave_read, output_file: Optional[wave.Wave_write]
) -> None:
    finished = asyncio.Event()
    timeout = recording.getnframes() / _SAMPLE_RATE + 60
    sender = asyncio.create_task(_send_audio(connection, recording, finished))
    receiver = asyncio.create_task(_receive_audio(connection, finished, timeout, output_file))
    try:
        input_bytes, output = await asyncio.wait_for(asyncio.gather(sender, receiver), timeout=timeout)
    except asyncio.TimeoutError as exc:
        raise TimeoutError("Timed out streaming the recording or waiting for nonempty GPT Live reply audio.") from exc
    finally:
        # Live has no response.cancel. Cancel local work and then request session.close.
        for task in (sender, receiver):
            if not task.done():
                task.cancel()
        await asyncio.gather(sender, receiver, return_exceptions=True)
    if input_bytes <= 0 or output.num_bytes <= 0 or not output.has_audio_activity:
        raise RuntimeError("A successful conversation requires nonzero input and non-silent reply audio.")
    for label, transcript in (("Input", output.input_transcript), ("Output", output.output_transcript)):
        if transcript and not transcript.strip():
            raise RuntimeError(f"{label} transcript events contained no usable text.")
        safe_print(f"{label} transcript: {transcript.strip() or '(not emitted by the service)'}")
    print(f"Sent {input_bytes} PCM16 bytes, including 48000 bytes of trailing silence.")
    print(f"Received {output.num_bytes} PCM16 bytes in {output.chunks} chunks ({output.num_bytes / 48000:.2f}s).")


async def _run_audio_conversation(
    project_client: AIProjectClient,
    agent_name: str,
    agent_version: str,
    recording: wave.Wave_read,
    output_file: Optional[wave.Wave_write],
) -> None:
    async with project_client.beta.voice_agents.live.connect(
        agent_name=agent_name, agent_version=agent_version, store=False
    ) as connection:
        try:
            await wait_for_event_async(connection, "session.started")
            print("Live session started; sending the recording and receiving audio concurrently.")
            await _stream_recording(connection, recording, output_file)
        finally:
            await close_session_async(connection)


async def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["FOUNDRY_VOICE_AGENT_MODEL"]
    input_path = Path(os.environ["FOUNDRY_VOICE_AUDIO_INPUT_PATH"])
    output_path = os.environ.get("FOUNDRY_VOICE_AUDIO_OUTPUT_PATH")
    if output_path and Path(output_path).resolve() == input_path.resolve():
        raise ValueError("The audio output path must not overwrite the input recording.")
    agent_name = sample_agent_name("audio")

    with ExitStack() as files:
        recording = files.enter_context(wave.open(str(input_path), "rb"))
        _validate_recording(recording)
        output_file = files.enter_context(wave.open(output_path, "wb")) if output_path else None
        if output_file is not None:
            output_file.setnchannels(1)
            output_file.setsampwidth(2)
            output_file.setframerate(_SAMPLE_RATE)
        async with (
            DefaultAzureCredential() as credential,
            AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
        ):
            created_version = None
            try:
                created_version = await project_client.agents.create_version(
                    agent_name=agent_name,
                    definition=models.VoiceAgentLiveDefinition(
                        model=model,
                        instructions=(
                            "You are a friendly voice assistant. Briefly answer the recorded speech. "
                            "Keep replies to one short sentence. Delegate external lookups to the client."
                        ),
                        audio=audio_settings(),
                        delegation=models.LiveClientDelegationParam(),
                        store=False,
                    ),
                )
                await _run_audio_conversation(
                    project_client, agent_name, created_version.version, recording, output_file
                )
            finally:
                if created_version is not None:
                    await project_client.agents.delete_version(
                        agent_name=agent_name, agent_version=created_version.version
                    )
                    print(f"Deleted sample agent version: {created_version.version}")
    if output_path:
        print("Saved actual returned PCM16 WAV audio to FOUNDRY_VOICE_AUDIO_OUTPUT_PATH (not telemetry).")


if __name__ == "__main__":
    asyncio.run(main())
