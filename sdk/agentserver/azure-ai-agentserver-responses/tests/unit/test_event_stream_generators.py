# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for ResponseEventStream generator convenience methods."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses.models._generated import ResponseStreamEvent
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

RESPONSE_ID = "resp_gen_test_12345"


def _make_stream(**kwargs) -> ResponseEventStream:
    return ResponseEventStream(response_id=RESPONSE_ID, **kwargs)


def _started_stream(**kwargs) -> ResponseEventStream:
    """Return a stream that has already emitted created + in_progress events."""
    stream = _make_stream(**kwargs)
    stream.emit_created()
    stream.emit_in_progress()
    return stream


# ---- output_item_message() ----


def test_output_item_message_yields_full_lifecycle() -> None:
    stream = _started_stream()
    events = list(stream.output_item_message("Hello world"))

    assert len(events) == 6
    # Every yielded event must be a ResponseStreamEvent model, not a plain dict
    for event in events:
        assert isinstance(event, ResponseStreamEvent), f"Expected ResponseStreamEvent, got {type(event)}"
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
    assert delta_event["delta"] == "Hello world"

    # Verify text content in done event
    done_event = events[3]
    assert done_event["text"] == "Hello world"


# ---- output_item_function_call() ----


def test_output_item_function_call_yields_full_lifecycle() -> None:
    stream = _started_stream()
    events = list(stream.output_item_function_call("get_weather", "call_abc", '{"city":"Seattle"}'))

    assert len(events) == 4
    for event in events:
        assert isinstance(event, ResponseStreamEvent), f"Expected ResponseStreamEvent, got {type(event)}"
    types = [e["type"] for e in events]
    assert types == [
        "response.output_item.added",
        "response.function_call_arguments.delta",
        "response.function_call_arguments.done",
        "response.output_item.done",
    ]

    # Verify function name in added event
    added_item = events[0]["item"]
    assert added_item["name"] == "get_weather"
    assert added_item["call_id"] == "call_abc"

    # Verify arguments in delta
    assert events[1]["delta"] == '{"city":"Seattle"}'

    # Verify arguments in done
    assert events[2]["arguments"] == '{"city":"Seattle"}'


# ---- output_item_function_call_output() ----


def test_output_item_function_call_output_yields_added_and_done() -> None:
    stream = _started_stream()
    events = list(stream.output_item_function_call_output("call_abc", "Sunny, 72F"))

    assert len(events) == 2
    for event in events:
        assert isinstance(event, ResponseStreamEvent), f"Expected ResponseStreamEvent, got {type(event)}"
    types = [e["type"] for e in events]
    assert types == [
        "response.output_item.added",
        "response.output_item.done",
    ]

    # Verify output content
    added_item = events[0]["item"]
    assert added_item["call_id"] == "call_abc"
    assert added_item["output"] == "Sunny, 72F"


# ---- output_item_reasoning_item() ----


def test_output_item_reasoning_item_yields_full_lifecycle() -> None:
    stream = _started_stream()
    events = list(stream.output_item_reasoning_item("The user asked about weather"))

    assert len(events) == 6
    for event in events:
        assert isinstance(event, ResponseStreamEvent), f"Expected ResponseStreamEvent, got {type(event)}"
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
    assert events[2]["delta"] == "The user asked about weather"

    # Verify summary text in done
    assert events[3]["text"] == "The user asked about weather"


# ---- Sequence number continuity across generators ----


def test_sequence_numbers_are_continuous_across_generators() -> None:
    """Verify that sequence numbers increase monotonically when chaining generators."""
    stream = _make_stream()
    all_events: list[dict] = []
    all_events.append(stream.emit_created())
    all_events.append(stream.emit_in_progress())
    all_events.extend(stream.output_item_message("hi"))
    all_events.append(stream.emit_completed())

    seq_numbers = [e["sequence_number"] for e in all_events]
    assert seq_numbers == list(range(len(all_events)))


# ---- Async generator variants ----


async def _collect(async_iter):
    """Collect all items from an async iterator."""
    result = []
    async for item in async_iter:
        result.append(item)
    return result


@pytest.mark.asyncio
async def test_async_output_item_message_yields_same_as_sync() -> None:
    stream = _started_stream()
    sync_events = list(stream.output_item_message("hello async"))

    stream2 = _started_stream()
    async_events = await _collect(stream2.aoutput_item_message("hello async"))

    assert len(async_events) == len(sync_events)
    for s, a in zip(sync_events, async_events):
        assert s["type"] == a["type"]


@pytest.mark.asyncio
async def test_async_output_item_message_streams_deltas() -> None:
    """Verify that AsyncIterable[str] input produces one delta per chunk."""

    async def chunks():
        yield "Hello"
        yield " world"
        yield "!"

    stream = _started_stream()
    events = await _collect(stream.aoutput_item_message(chunks()))

    # added, content_added, delta("Hello"), delta(" world"), delta("!"),
    # text_done("Hello world!"), content_done, item_done
    assert len(events) == 8
    types = [e["type"] for e in events]
    assert types == [
        "response.output_item.added",
        "response.content_part.added",
        "response.output_text.delta",
        "response.output_text.delta",
        "response.output_text.delta",
        "response.output_text.done",
        "response.content_part.done",
        "response.output_item.done",
    ]

    # Verify individual deltas
    assert events[2]["delta"] == "Hello"
    assert events[3]["delta"] == " world"
    assert events[4]["delta"] == "!"

    # Verify accumulated done text
    assert events[5]["text"] == "Hello world!"


@pytest.mark.asyncio
async def test_async_output_item_function_call_yields_same_as_sync() -> None:
    stream = _started_stream()
    sync_events = list(stream.output_item_function_call("fn", "call_1", '{"x":1}'))

    stream2 = _started_stream()
    async_events = await _collect(stream2.aoutput_item_function_call("fn", "call_1", '{"x":1}'))

    assert len(async_events) == len(sync_events)
    for s, a in zip(sync_events, async_events):
        assert s["type"] == a["type"]


@pytest.mark.asyncio
async def test_async_output_item_function_call_streams_arguments() -> None:
    """Verify streaming arguments via AsyncIterable[str]."""

    async def arg_chunks():
        yield '{"city":'
        yield '"Seattle"}'

    stream = _started_stream()
    events = await _collect(stream.aoutput_item_function_call("get_weather", "call_1", arg_chunks()))

    # added, delta, delta, args_done, item_done
    assert len(events) == 5
    assert events[1]["delta"] == '{"city":'
    assert events[2]["delta"] == '"Seattle"}'
    assert events[3]["arguments"] == '{"city":"Seattle"}'


@pytest.mark.asyncio
async def test_async_output_item_function_call_output_yields_same_as_sync() -> None:
    stream = _started_stream()
    sync_events = list(stream.output_item_function_call_output("call_1", "result"))

    stream2 = _started_stream()
    async_events = await _collect(stream2.aoutput_item_function_call_output("call_1", "result"))

    assert len(async_events) == len(sync_events)
    for s, a in zip(sync_events, async_events):
        assert s["type"] == a["type"]


@pytest.mark.asyncio
async def test_async_output_item_reasoning_item_yields_same_as_sync() -> None:
    stream = _started_stream()
    sync_events = list(stream.output_item_reasoning_item("thinking..."))

    stream2 = _started_stream()
    async_events = await _collect(stream2.aoutput_item_reasoning_item("thinking..."))

    assert len(async_events) == len(sync_events)
    for s, a in zip(sync_events, async_events):
        assert s["type"] == a["type"]


@pytest.mark.asyncio
async def test_async_output_item_reasoning_item_streams_deltas() -> None:
    """Verify streaming reasoning summary via AsyncIterable[str]."""

    async def summary_chunks():
        yield "Let me "
        yield "think..."

    stream = _started_stream()
    events = await _collect(stream.aoutput_item_reasoning_item(summary_chunks()))

    # added, part_added, delta, delta, text_done, part_done, item_done
    assert len(events) == 7
    assert events[2]["delta"] == "Let me "
    assert events[3]["delta"] == "think..."
    assert events[4]["text"] == "Let me think..."
