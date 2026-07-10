# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for SSE encoding helpers."""

from __future__ import annotations

import asyncio
import contextvars
from typing import AsyncIterator, List

import pytest

from azure.ai.agentserver.responses.streaming import _sse
from azure.ai.agentserver.responses.streaming._sse import encode_keep_alive_comment, with_keep_alive

_KA = encode_keep_alive_comment()


class _FakeEvent:
    def __init__(self, type: str, sequence_number: int, text: str) -> None:
        self.type = type
        self.sequence_number = sequence_number
        self.text = text


def test_sse_writer__encodes_event_and_data_lines_with_separator() -> None:
    event = _FakeEvent(type="response.created", sequence_number=0, text="hello")

    encoded = _sse.encode_sse_event(event)  # type: ignore[arg-type]
    assert encoded.startswith("event: response.created\n")
    assert "data:" in encoded
    assert encoded.endswith("\n\n")


def test_sse_writer__encodes_multiline_text_as_single_data_line() -> None:
    event = _FakeEvent(type="response.output_text.delta", sequence_number=1, text="line1\nline2")

    encoded = _sse.encode_sse_event(event)  # type: ignore[arg-type]
    # Spec requires a single data: line with JSON payload — no extra data: lines
    assert encoded.count("data: ") == 1
    assert "data: line1" not in encoded
    assert r"line1\nline2" in encoded


def test_sse_writer__keep_alive_comment_frame_format() -> None:
    keep_alive_frame = _sse.encode_keep_alive_comment()  # type: ignore[attr-defined]
    assert keep_alive_frame == ": keep-alive\n\n"


def test_sse_writer__injects_monotonic_sequence_numbers() -> None:
    import json as _json

    _sse.new_stream_counter()

    first_event = _FakeEvent(type="response.created", sequence_number=-1, text="a")
    second_event = _FakeEvent(type="response.in_progress", sequence_number=-1, text="b")

    encoded_first = _sse.encode_sse_event(first_event)  # type: ignore[arg-type]
    encoded_second = _sse.encode_sse_event(second_event)  # type: ignore[arg-type]

    def _extract_sequence_number(encoded: str) -> int:
        data_line = next(line for line in encoded.splitlines() if line.startswith("data:"))
        payload = _json.loads(data_line[len("data:") :].strip())
        return int(payload["sequence_number"])

    seq_first = _extract_sequence_number(encoded_first)
    seq_second = _extract_sequence_number(encoded_second)

    assert seq_first == 0, f"first sequence_number must be 0 for a new stream, got {seq_first}"
    assert seq_second == 1, f"second sequence_number must be 1 for a new stream, got {seq_second}"


async def _collect(stream: AsyncIterator[str]) -> List[str]:
    return [item async for item in stream]


async def test_with_keep_alive__passthrough_when_disabled() -> None:
    """A None or 0 interval yields the source unchanged with no keep-alive frames."""

    async def source() -> AsyncIterator[str]:
        yield "a"
        yield "b"

    assert await _collect(with_keep_alive(source(), None)) == ["a", "b"]
    assert await _collect(with_keep_alive(source(), 0)) == ["a", "b"]


async def test_with_keep_alive__emits_heartbeat_on_idle_gap() -> None:
    """A keep-alive frame is emitted when the source stays idle past the interval."""

    async def source() -> AsyncIterator[str]:
        yield "a"
        await asyncio.sleep(0.25)
        yield "b"

    out = await _collect(with_keep_alive(source(), 0.05))
    assert _KA in out
    assert [item for item in out if item != _KA] == ["a", "b"]
    assert out.index("a") < out.index("b")


async def test_with_keep_alive__preserves_contextvars_across_yields() -> None:
    """A ContextVar the source sets once stays set across all of its yields, because the
    source is advanced by a single task."""

    cvar: contextvars.ContextVar[str] = contextvars.ContextVar("cvar", default="UNSET")
    seen: List[str] = []

    async def source() -> AsyncIterator[str]:
        cvar.set("SET")
        seen.append(cvar.get())
        yield "a"
        seen.append(cvar.get())
        yield "b"
        seen.append(cvar.get())

    out = await _collect(with_keep_alive(source(), 5))
    assert out == ["a", "b"]
    assert seen == ["SET", "SET", "SET"]


async def test_with_keep_alive__runs_source_finally_on_early_close() -> None:
    """Closing the wrapper after one item runs the source's finally before returning."""

    finalized = asyncio.Event()

    async def source() -> AsyncIterator[str]:
        try:
            yield "a"
            await asyncio.Event().wait()
            yield "b"
        finally:
            finalized.set()

    stream = with_keep_alive(source(), 5)
    assert await stream.__anext__() == "a"
    await stream.aclose()
    await asyncio.wait_for(finalized.wait(), timeout=1.0)


async def test_with_keep_alive__emits_heartbeat_while_source_idle_from_start() -> None:
    """A source idle from the start still emits keep-alive frames, matching a reconnect
    GET subscribed to an in-flight run that has not emitted since the cursor."""

    async def idle_source() -> AsyncIterator[str]:
        await asyncio.Event().wait()
        yield "never"  # pragma: no cover

    stream = with_keep_alive(idle_source(), 0.05)
    assert await asyncio.wait_for(stream.__anext__(), timeout=1.0) == _KA
    await stream.aclose()


async def test_with_keep_alive__propagates_source_error() -> None:
    """An error raised by the source surfaces to the consumer after buffered items."""

    async def source() -> AsyncIterator[str]:
        yield "a"
        raise RuntimeError("boom")

    collected: List[str] = []
    with pytest.raises(RuntimeError, match="boom"):
        async for item in with_keep_alive(source(), 5):
            collected.append(item)

    assert collected == ["a"]
