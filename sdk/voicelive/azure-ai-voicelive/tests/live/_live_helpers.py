# pylint: disable=line-too-long,useless-suppression
# Shared helpers for the LIVE async realtime tests.
# Used by the test_live_realtime_*.py modules.
import asyncio
import base64

from pathlib import Path
from typing import Any, Callable, Iterator, Optional

from azure.ai.voicelive.models import (
    AudioInputTranscriptionOptions,
    ServerEventType,
)


def _load_audio_b64(path: Path) -> str:
    with open(path, "rb") as f:
        audio_bytes = f.read()
    return base64.b64encode(audio_bytes).decode("utf-8")


def _get_trailing_silence_bytes(sample_rate: int = 24000, duration_s: float = 2.0) -> bytes:
    num_samples = int(sample_rate * duration_s)
    return b"\x00\x00" * num_samples  # 16-bit PCM silence


def _iter_audio_b64_chunks(path: Path, chunk_bytes: int = 10_240) -> Iterator[str]:
    """Yield base64-encoded chunks of the file, ~10 KB of raw bytes per chunk."""
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_bytes)
            if not chunk:
                break
            yield base64.b64encode(chunk).decode("utf-8")


def _get_speech_recognition_setting(model: str) -> AudioInputTranscriptionOptions:
    speech_recognition_model = (
        "whisper-1" if model.startswith(("gpt-realtime", "gpt-realtime-mini")) else "azure-speech"
    )
    return AudioInputTranscriptionOptions(model=speech_recognition_model, language="en-US")


async def _wait_for_event(conn, wanted_types: set, timeout_s: float = 10.0):
    """Wait until we receive any event whose type is in wanted_types."""

    async def _next():
        while True:
            evt = await conn.recv()
            if evt.type in wanted_types:
                return evt

    return await asyncio.wait_for(_next(), timeout=timeout_s)


async def _wait_for_match(
    conn,
    predicate: Callable[[Any], bool],
    timeout_s: float = 10.0,
):
    """Wait until we receive an event that satisfies the given predicate."""

    async def _next():
        while True:
            evt = await conn.recv()
            if predicate(evt):
                return evt

    return await asyncio.wait_for(_next(), timeout=timeout_s)


async def _collect_event(conn, *, event_type: Optional[ServerEventType], timeout: int = 10):
    events = 0
    audio_bytes = 0
    loop = asyncio.get_event_loop()
    end = loop.time() + timeout

    while True:
        remaining = end - loop.time()
        if remaining <= 0:
            break

        try:
            evt = await asyncio.wait_for(conn.recv(), timeout=remaining)
        except asyncio.TimeoutError:
            break  # no event arrived before the overall timeout

        if evt.type == event_type:
            events += 1

        if evt.type == ServerEventType.RESPONSE_AUDIO_DELTA:
            audio_bytes += len(evt.delta)

    return events, audio_bytes


async def _collect_audio_trans_outputs(conn, duration_s: float) -> tuple[int, int]:
    trans_events = 0
    audio_events = 0
    loop = asyncio.get_event_loop()
    end = loop.time() + duration_s

    while True:
        remaining = end - loop.time()
        if remaining <= 0:
            break

        try:
            event = await asyncio.wait_for(conn.recv(), timeout=remaining)
        except asyncio.TimeoutError:
            break

        if event.type == ServerEventType.RESPONSE_AUDIO_DELTA or event.type == ServerEventType.RESPONSE_AUDIO_DONE:
            audio_events += 1

        if (
            event.type == ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA
            or event.type == ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE
        ):
            trans_events += 1

    return audio_events, trans_events
