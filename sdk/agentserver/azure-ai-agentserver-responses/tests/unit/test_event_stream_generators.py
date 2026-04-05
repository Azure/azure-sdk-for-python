# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for ResponseEventStream generator convenience methods."""

from __future__ import annotations

from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream


RESPONSE_ID = "resp_gen_test_12345"


def _make_stream(**kwargs) -> ResponseEventStream:
    return ResponseEventStream(response_id=RESPONSE_ID, **kwargs)


def _started_stream(**kwargs) -> ResponseEventStream:
    """Return a stream that has already emitted start() events."""
    stream = _make_stream(**kwargs)
    list(stream.start())
    return stream


# ---- start() ----


def test_start_yields_created_and_in_progress() -> None:
    stream = _make_stream()
    events = list(stream.start())

    assert len(events) == 2
    assert events[0]["type"] == "response.created"
    assert events[1]["type"] == "response.in_progress"
    assert all(e["payload"]["response_id"] == RESPONSE_ID for e in events)


# ---- complete() ----


def test_complete_yields_completed() -> None:
    stream = _started_stream()
    events = list(stream.complete())

    assert len(events) == 1
    assert events[0]["type"] == "response.completed"
    assert events[0]["payload"]["status"] == "completed"


# ---- fail() ----


def test_fail_yields_failed_with_defaults() -> None:
    stream = _started_stream()
    events = list(stream.fail())

    assert len(events) == 1
    assert events[0]["type"] == "response.failed"
    payload = events[0]["payload"]
    assert payload["status"] == "failed"
    assert payload["error"]["code"] == "server_error"
    assert payload["error"]["message"] == "An internal server error occurred."


def test_fail_yields_failed_with_custom_code_and_message() -> None:
    stream = _started_stream()
    events = list(stream.fail(code="rate_limit_exceeded", message="Too many requests"))

    assert len(events) == 1
    assert events[0]["type"] == "response.failed"
    payload = events[0]["payload"]
    assert payload["error"]["code"] == "rate_limit_exceeded"
    assert payload["error"]["message"] == "Too many requests"


# ---- incomplete() ----


def test_incomplete_yields_incomplete_without_reason() -> None:
    stream = _started_stream()
    events = list(stream.incomplete())

    assert len(events) == 1
    assert events[0]["type"] == "response.incomplete"
    assert events[0]["payload"]["status"] == "incomplete"


def test_incomplete_yields_incomplete_with_reason() -> None:
    stream = _started_stream()
    events = list(stream.incomplete(reason="max_output_tokens"))

    assert len(events) == 1
    assert events[0]["type"] == "response.incomplete"
    payload = events[0]["payload"]
    assert payload["incomplete_details"]["reason"] == "max_output_tokens"


# ---- text_message() ----


def test_text_message_yields_full_lifecycle() -> None:
    stream = _started_stream()
    events = list(stream.text_message("Hello world"))

    assert len(events) == 6
    types = [e["type"] for e in events]
    assert types == [
        "response.output_item.added",
        "response.content_part.added",
        "response.output_text.delta",
        "response.output_text.done",
        "response.content_part.done",
        "response.output_item.done",
    ]

    # Verify text content in delta event
    delta_event = events[2]
    assert delta_event["payload"]["delta"] == "Hello world"

    # Verify text content in done event
    done_event = events[3]
    assert done_event["payload"]["text"] == "Hello world"


# ---- function_call() ----


def test_function_call_yields_full_lifecycle() -> None:
    stream = _started_stream()
    events = list(stream.function_call("get_weather", "call_abc", '{"city":"Seattle"}'))

    assert len(events) == 4
    types = [e["type"] for e in events]
    assert types == [
        "response.output_item.added",
        "response.function_call_arguments.delta",
        "response.function_call_arguments.done",
        "response.output_item.done",
    ]

    # Verify function name in added event
    added_item = events[0]["payload"]["item"]
    assert added_item["name"] == "get_weather"
    assert added_item["call_id"] == "call_abc"

    # Verify arguments in delta
    assert events[1]["payload"]["delta"] == '{"city":"Seattle"}'

    # Verify arguments in done
    assert events[2]["payload"]["arguments"] == '{"city":"Seattle"}'


# ---- function_call_output() ----


def test_function_call_output_yields_added_and_done() -> None:
    stream = _started_stream()
    events = list(stream.function_call_output("call_abc", "Sunny, 72F"))

    assert len(events) == 2
    types = [e["type"] for e in events]
    assert types == [
        "response.output_item.added",
        "response.output_item.done",
    ]

    # Verify output content
    added_item = events[0]["payload"]["item"]
    assert added_item["call_id"] == "call_abc"
    assert added_item["output"] == "Sunny, 72F"


# ---- reasoning() ----


def test_reasoning_yields_full_lifecycle() -> None:
    stream = _started_stream()
    events = list(stream.reasoning("The user asked about weather"))

    assert len(events) == 6
    types = [e["type"] for e in events]
    assert types == [
        "response.output_item.added",
        "response.reasoning_summary_part.added",
        "response.reasoning_summary_text.delta",
        "response.reasoning_summary_text.done",
        "response.reasoning_summary_part.done",
        "response.output_item.done",
    ]

    # Verify summary text in delta
    assert events[2]["payload"]["delta"] == "The user asked about weather"

    # Verify summary text in done
    assert events[3]["payload"]["text"] == "The user asked about weather"


# ---- Sequence number continuity across generators ----


def test_sequence_numbers_are_continuous_across_generators() -> None:
    """Verify that sequence numbers increase monotonically when chaining generators."""
    stream = _make_stream()
    all_events = []
    all_events.extend(stream.start())
    all_events.extend(stream.text_message("hi"))
    all_events.extend(stream.complete())

    seq_numbers = [e["payload"]["sequence_number"] for e in all_events]
    assert seq_numbers == list(range(len(all_events)))
