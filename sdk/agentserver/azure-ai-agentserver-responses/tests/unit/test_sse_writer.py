# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for SSE encoding helpers."""

from __future__ import annotations

from azure.ai.agentserver.responses.streaming import _sse


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
