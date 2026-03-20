"""Unit tests for SSE encoding helpers."""

from __future__ import annotations

from dataclasses import dataclass

from azure.ai.agentserver.responses.streaming import _sse


@dataclass
class _FakeEvent:
    type: str
    sequence_number: int
    text: str


def test_sse_writer__encodes_event_and_data_lines_with_separator() -> None:
    event = _FakeEvent(type="response.created", sequence_number=0, text="hello")

    encoded = _sse.encode_sse_event(event)  # type: ignore[arg-type]
    assert encoded.startswith("event: response.created\n")
    assert "data:" in encoded
    assert encoded.endswith("\n\n")


def test_sse_writer__encodes_multiline_data_as_multiple_data_lines() -> None:
    event = _FakeEvent(type="response.output_text.delta", sequence_number=1, text="line1\nline2")

    encoded = _sse.encode_sse_event(event)  # type: ignore[arg-type]
    assert "data: line1" in encoded
    assert "data: line2" in encoded


def test_sse_writer__keep_alive_comment_frame_format() -> None:
    keep_alive_frame = _sse.encode_keep_alive_comment()  # type: ignore[attr-defined]
    assert keep_alive_frame == ": keep-alive\n\n"


def test_sse_writer__injects_monotonic_sequence_numbers() -> None:
    first_event = _FakeEvent(type="response.created", sequence_number=-1, text="a")
    second_event = _FakeEvent(type="response.in_progress", sequence_number=-1, text="b")

    encoded_first = _sse.encode_sse_event(first_event)  # type: ignore[arg-type]
    encoded_second = _sse.encode_sse_event(second_event)  # type: ignore[arg-type]

    assert '"sequence_number": 0' in encoded_first
    assert '"sequence_number": 1' in encoded_second
