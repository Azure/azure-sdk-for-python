# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for the response event stream APIs."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.models import _generated as generated_models
from azure.ai.agentserver.responses.models._generated import (
    AgentReference,
    OutputItemComputerToolCallOutputResource,
    ResponseCompletedEvent,
    ResponseCreatedEvent,
    ResponseFailedEvent,
    ResponseIncompleteEvent,
    ResponseInProgressEvent,
    ResponseObject,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseStreamEvent,
    ResponseUsage,
)
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream


def test_event_stream_builder__builds_lifecycle_events() -> None:
    stream = ResponseEventStream(
        response_id="resp_builder_12345",
        agent_reference=AgentReference(type="agent_reference", name="unit-agent"),
        model="gpt-4o-mini",
    )

    events = [
        stream.emit_created(status="queued"),
        stream.emit_in_progress(),
        stream.emit_completed(),
    ]

    # All events must be typed ResponseStreamEvent subtypes
    for event in events:
        assert isinstance(event, ResponseStreamEvent), f"Expected ResponseStreamEvent, got {type(event)}"
    assert isinstance(events[0], ResponseCreatedEvent)
    assert isinstance(events[1], ResponseInProgressEvent)
    assert isinstance(events[2], ResponseCompletedEvent)

    assert [event["type"] for event in events] == [
        "response.created",
        "response.in_progress",
        "response.completed",
    ]
    assert [event["sequence_number"] for event in events] == [0, 1, 2]
    assert all(event["response"]["response_id"] == "resp_builder_12345" for event in events)
    assert all(event["response"]["agent_reference"]["name"] == "unit-agent" for event in events)


def test_event_stream_builder__builds_output_item_events() -> None:
    stream = ResponseEventStream(response_id="resp_builder_output_12345")
    message = stream.add_output_item_message()
    text = message.add_text_content()

    events = [
        stream.emit_created(status="queued"),
        stream.emit_in_progress(),
        message.emit_added(),
        text.emit_added(),
        text.emit_delta("hello"),
        text.emit_text_done(),
        text.emit_done(),
        message.emit_done(),
        stream.emit_completed(),
    ]

    for event in events:
        assert isinstance(event, ResponseStreamEvent), f"Expected ResponseStreamEvent, got {type(event)}"

    event_types = [event["type"] for event in events]
    assert "response.output_item.added" in event_types
    assert "response.output_text.delta" in event_types
    assert "response.output_item.done" in event_types


def test_event_stream_builder__output_item_added_returns_event_immediately() -> None:
    stream = ResponseEventStream(
        response_id="resp_builder_incremental_12345",
        agent_reference=AgentReference(type="agent_reference", name="unit-agent"),
        model="gpt-4o-mini",
    )
    stream.emit_created(status="queued")
    stream.emit_in_progress()
    message = stream.add_output_item_message()

    emitted = message.emit_added()

    assert isinstance(emitted, ResponseStreamEvent)
    assert isinstance(emitted, ResponseOutputItemAddedEvent)
    assert emitted["type"] == "response.output_item.added"
    assert emitted["output_index"] == 0
    assert emitted["item"]["id"] == message.item_id
    assert emitted["item"]["type"] == "message"
    # B20/B21: response_id and agent_reference must be stamped on output items
    assert emitted["item"]["response_id"] == "resp_builder_incremental_12345"
    assert emitted["item"]["agent_reference"] == {"name": "unit-agent", "type": "agent_reference"}
    assert emitted["sequence_number"] == 2


def test_event_stream_builder__rejects_illegal_output_item_sequence() -> None:
    stream = ResponseEventStream(response_id="resp_builder_bad_12345")
    stream.emit_created(status="queued")
    stream.emit_in_progress()
    message = stream.add_output_item_message()

    with pytest.raises(ValueError):
        message.emit_done()


def test_event_stream_builder__rejects_invalid_global_stream_order() -> None:
    with pytest.raises(ValueError):
        stream = ResponseEventStream(response_id="resp_builder_bad_order_12345")
        stream.emit_created(status="queued")
        stream.emit_in_progress()
        message = stream.add_output_item_message()
        text = message.add_text_content()
        message.emit_added()
        stream.emit_completed()
        text.emit_added()
        text.emit_text_done()
        text.emit_done()
        message.emit_done()


def test_event_stream_builder__emit_completed_accepts_usage_and_sets_terminal_fields() -> None:
    stream = ResponseEventStream(response_id="resp_builder_completed_params")
    stream.emit_created(status="in_progress")

    message = stream.add_output_item_message()
    message.emit_added()
    text = message.add_text_content()
    text.emit_added()
    text.emit_delta("hello")
    text.emit_text_done()
    text.emit_done()
    message.emit_done()

    usage = ResponseUsage(
        input_tokens=1,
        input_tokens_details={"cached_tokens": 0},
        output_tokens=2,
        output_tokens_details={"reasoning_tokens": 0},
        total_tokens=3,
    )

    completed = stream.emit_completed(usage=usage)

    assert isinstance(completed, ResponseStreamEvent)
    assert isinstance(completed, ResponseCompletedEvent)
    assert completed["type"] == "response.completed"
    assert completed["response"]["status"] == "completed"
    assert completed["response"]["usage"]["total_tokens"] == 3
    assert isinstance(completed["response"]["completed_at"], int)


def test_event_stream_builder__emit_failed_accepts_error_and_usage() -> None:
    stream = ResponseEventStream(response_id="resp_builder_failed_params")
    stream.emit_created(status="in_progress")

    usage = ResponseUsage(
        input_tokens=4,
        input_tokens_details={"cached_tokens": 0},
        output_tokens=5,
        output_tokens_details={"reasoning_tokens": 0},
        total_tokens=9,
    )

    failed = stream.emit_failed(code="server_error", message="boom", usage=usage)

    assert isinstance(failed, ResponseStreamEvent)
    assert isinstance(failed, ResponseFailedEvent)
    assert failed["type"] == "response.failed"
    assert failed["response"]["status"] == "failed"
    assert failed["response"]["error"]["code"] == "server_error"
    assert failed["response"]["error"]["message"] == "boom"
    assert failed["response"]["usage"]["total_tokens"] == 9
    assert failed["response"].get("completed_at") is None


def test_event_stream_builder__emit_incomplete_accepts_reason_and_usage() -> None:
    stream = ResponseEventStream(response_id="resp_builder_incomplete_params")
    stream.emit_created(status="in_progress")

    usage = ResponseUsage(
        input_tokens=2,
        input_tokens_details={"cached_tokens": 0},
        output_tokens=3,
        output_tokens_details={"reasoning_tokens": 0},
        total_tokens=5,
    )

    incomplete = stream.emit_incomplete(reason="max_output_tokens", usage=usage)

    assert isinstance(incomplete, ResponseStreamEvent)
    assert isinstance(incomplete, ResponseIncompleteEvent)
    assert incomplete["type"] == "response.incomplete"
    assert incomplete["response"]["status"] == "incomplete"
    assert incomplete["response"]["incomplete_details"]["reason"] == "max_output_tokens"
    assert incomplete["response"]["usage"]["total_tokens"] == 5
    assert incomplete["response"].get("completed_at") is None


def test_event_stream_builder__add_output_item_generic_emits_added_and_done() -> None:
    stream = ResponseEventStream(response_id="resp_builder_generic_item")
    stream.emit_created(status="in_progress")

    item_id = IdGenerator.new_computer_call_output_item_id("resp_builder_generic_item")
    builder = stream.add_output_item(item_id)
    added_item = OutputItemComputerToolCallOutputResource(
        {
            "id": item_id,
            "type": "computer_call_output",
            "call_id": "call_1",
            "output": {"type": "computer_screenshot", "image_url": "https://example.com/1.png"},
            "status": "in_progress",
        }
    )
    done_item = OutputItemComputerToolCallOutputResource(
        {
            "id": item_id,
            "type": "computer_call_output",
            "call_id": "call_1",
            "output": {"type": "computer_screenshot", "image_url": "https://example.com/2.png"},
            "status": "completed",
        }
    )

    added = builder.emit_added(added_item)
    done = builder.emit_done(done_item)

    assert isinstance(added, ResponseStreamEvent)
    assert isinstance(added, ResponseOutputItemAddedEvent)
    assert isinstance(done, ResponseStreamEvent)
    assert isinstance(done, ResponseOutputItemDoneEvent)
    assert added["type"] == "response.output_item.added"
    assert added["output_index"] == 0
    assert done["type"] == "response.output_item.done"
    assert done["item"]["status"] == "completed"


def test_event_stream_builder__constructor_accepts_seed_response() -> None:
    seed_response = generated_models.ResponseObject(
        {
            "id": "resp_builder_seed_response",
            "object": "response",
            "output": [],
            "model": "gpt-4o-mini",
            "metadata": {"source": "seed"},
        }
    )

    stream = ResponseEventStream(response=seed_response)
    created = stream.emit_created()

    assert isinstance(stream.response, ResponseObject)
    assert isinstance(created, ResponseCreatedEvent)
    assert created["response"]["id"] == "resp_builder_seed_response"
    assert created["response"]["model"] == "gpt-4o-mini"
    assert created["response"]["metadata"] == {"source": "seed"}


def test_event_stream_builder__constructor_accepts_request_seed_fields() -> None:
    request = generated_models.CreateResponse(
        {
            "model": "gpt-4o-mini",
            "background": True,
            "metadata": {"tag": "seeded"},
            "previous_response_id": "resp_prev_seed",
        }
    )

    stream = ResponseEventStream(response_id="resp_builder_seed_request", request=request)
    created = stream.emit_created()

    assert created["response"]["id"] == "resp_builder_seed_request"
    assert created["response"]["model"] == "gpt-4o-mini"
    assert created["response"]["background"] is True
    assert created["response"]["previous_response_id"] == "resp_prev_seed"
    assert created["response"]["metadata"] == {"tag": "seeded"}
