"""Unit tests for .NET-aligned response event stream APIs."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses._event_stream import ResponseEventStream
from azure.ai.agentserver.responses._state_machine import LifecycleStateMachineError


def test_event_stream_builder__builds_lifecycle_events() -> None:
    stream = ResponseEventStream(
        response_id="resp_builder_12345",
        agent_reference={"type": "agent_reference", "name": "unit-agent"},
        model="gpt-4o-mini",
    )

    events = [
        stream.emit_created(status="queued"),
        stream.emit_in_progress(),
        stream.emit_completed(),
    ]

    assert [event["type"] for event in events] == [
        "response.created",
        "response.in_progress",
        "response.completed",
    ]
    assert [event["payload"]["sequence_number"] for event in events] == [0, 1, 2]
    assert all(event["payload"]["response_id"] == "resp_builder_12345" for event in events)
    assert all(event["payload"]["agent_reference"]["name"] == "unit-agent" for event in events)


def test_event_stream_builder__builds_output_item_events() -> None:
    stream = ResponseEventStream(response_id="resp_builder_output_12345")
    output_item = stream.add_output_item(output_index=0)

    events = [
        stream.emit_created(status="queued"),
        stream.emit_in_progress(),
        output_item.emit_added(item={"id": "item-1"}),
        output_item.emit_delta(item={"delta": "hello"}),
        output_item.emit_done(item={"id": "item-1"}),
        stream.emit_completed(),
    ]

    event_types = [event["type"] for event in events]
    assert "response.output_item.added" in event_types
    assert "response.output_item.delta" in event_types
    assert "response.output_item.done" in event_types


def test_event_stream_builder__output_item_added_returns_event_immediately() -> None:
    stream = ResponseEventStream(
        response_id="resp_builder_incremental_12345",
        agent_reference={"type": "agent_reference", "name": "unit-agent"},
        model="gpt-4o-mini",
    )
    stream.emit_created(status="queued")
    stream.emit_in_progress()
    output_item = stream.add_output_item(output_index=0)

    emitted = output_item.emit_added(item={"id": "item-1"})

    assert emitted["type"] == "response.output_item.added"
    assert emitted["payload"]["output_index"] == 0
    assert emitted["payload"]["item"]["id"] == "item-1"
    assert emitted["payload"]["response_id"] == "resp_builder_incremental_12345"
    assert emitted["payload"]["agent_reference"]["name"] == "unit-agent"
    assert emitted["payload"]["model"] == "gpt-4o-mini"
    assert emitted["payload"]["sequence_number"] == 2


def test_event_stream_builder__auto_appends_failed_terminal_when_missing() -> None:
    stream = ResponseEventStream(response_id="resp_builder_failed_12345")
    stream.emit_created(status="queued")
    events = stream.build()
    assert events[-1]["type"] == "response.failed"


def test_event_stream_builder__rejects_illegal_output_item_sequence() -> None:
    stream = ResponseEventStream(response_id="resp_builder_bad_12345")
    stream.emit_created(status="queued")
    stream.emit_in_progress()
    output_item = stream.add_output_item(output_index=0)

    with pytest.raises(ValueError):
        output_item.emit_done(item={"id": "item-1"})


def test_event_stream_builder__rejects_invalid_global_stream_order() -> None:
    with pytest.raises(LifecycleStateMachineError):
        stream = ResponseEventStream(response_id="resp_builder_bad_order_12345")
        stream.emit_created(status="queued")
        stream.emit_in_progress()
        output_item = stream.add_output_item(output_index=0)
        output_item.emit_added(item={"id": "item-1"})
        stream.emit_completed()
        output_item.emit_done(item={"id": "item-1"})
