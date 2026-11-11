# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Ownership and deterministic work bounds for event normalization and seeding."""

from __future__ import annotations

import asyncio
from collections import UserDict
from copy import deepcopy
from datetime import datetime, timezone
import json
from unittest.mock import patch

import pytest

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses.hosting import _orchestrator
from azure.ai.agentserver.responses.hosting._execution_context import _ExecutionContext
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider
from azure.ai.agentserver.responses.streaming import _internals
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from azure.ai.agentserver.responses.streaming._text_response import TextResponse


class _CountedTree(dict):
    """Retain traversal instrumentation across copies, without sharing payloads."""

    visits: list[str] = []

    def __deepcopy__(self, memo):
        self.visits.append(self["label"])
        result = type(self)()
        memo[id(self)] = result
        result.update(deepcopy(dict(self), memo))
        return result


def _item():
    return {
        "id": "msg_copy_reuse",
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "output_text", "text": "echo", "annotations": []}],
    }


def test_completed_item_uses_one_copy_and_detaches_both_directions():
    item = _item()
    event = {"type": "response.output_item.done", "output_index": 2, "item": item}
    response = {"output": ["retained"]}
    with patch.object(_internals, "deepcopy", wraps=deepcopy) as copies:
        _internals.track_completed_output_item(response, event)
    assert copies.call_count == 1
    assert response["output"] == ["retained", None, item]
    event["item"]["content"][0]["text"] = "raw mutation"
    assert response["output"][2]["content"][0]["text"] == "echo"
    response["output"][2]["content"][0]["annotations"].append({"extra": True})
    assert item["content"][0]["annotations"] == []


@pytest.mark.parametrize("index,item", [(-1, {}), ("0", {}), (None, {}), (0, None), (0, UserDict())])
def test_completed_item_invalid_values_do_not_change_response(index, item):
    response = {"output": ("untouched",)}
    with patch.object(_internals, "deepcopy", wraps=deepcopy) as copies:
        _internals.track_completed_output_item(
            response, {"type": "response.output_item.done", "output_index": index, "item": item}
        )
    assert copies.call_count == 0
    assert response == {"output": ("untouched",)}


@pytest.mark.parametrize("index", [0, 3, False, True])
def test_completed_item_retains_sparse_and_bool_index_semantics(index):
    response = {"output": None}
    _internals.track_completed_output_item(
        response, {"type": "response.output_item.done", "output_index": index, "item": {"nested": []}}
    )
    assert response == {"output": [None] * index + [{"nested": []}]}
    before = deepcopy(response)
    _internals.track_completed_output_item(response, {"type": "response.output_item.added", "output_index": 0})
    assert response == before


def test_extract_fields_does_not_copy_unrelated_graph():
    response = {
        "model": "echo",
        "agent_reference": UserDict({"name": "agent", "extension": {"versions": ["1"]}}),
        "output": [_CountedTree(label="output", nested=[{}])],
    }
    _CountedTree.visits = []
    reference, model = _internals.extract_response_fields(response)
    assert _CountedTree.visits == []
    assert model == "echo"
    assert type(reference) is dict
    reference["extension"]["versions"].append("2")
    assert response["agent_reference"]["extension"]["versions"] == ["1"]
    response["agent_reference"]["extension"]["versions"].append("3")
    assert reference["extension"]["versions"] == ["1", "2"]


def test_request_seeding_copies_only_used_mutable_fields():
    reference = {"type": "agent_reference", "name": "agent", "extension": {"versions": ["1"]}}
    request = {
        "input": [_CountedTree(label="input", content=[{"text": "unused"}])],
        "tools": [_CountedTree(label="tools", parameters={"properties": {}})],
        "metadata": {"origin": "request"},
        "background": True,
        "previous_response_id": "resp_previous",
        "conversation": {"id": "conv_seed"},
        "model": "echo",
        "agent_reference": reference,
    }
    _CountedTree.visits = []
    stream = ResponseEventStream(response_id="resp_copy_reuse", request=request)
    assert _CountedTree.visits == []
    request["metadata"]["origin"] = "raw mutation"
    reference["extension"]["versions"].append("raw")
    request["conversation"]["id"] = "conv_raw"
    assert stream.response["metadata"] == {"origin": "request"}
    assert stream.response["conversation"] == {"id": "conv_seed"}
    assert stream.response["background"] is True
    assert stream.response["previous_response_id"] == "resp_previous"
    assert stream.response["model"] == "echo"
    assert stream.response["agent_reference"]["extension"]["versions"] == ["1"]
    stream.response["agent_reference"]["extension"]["versions"].append("live")
    assert stream._agent_reference["extension"]["versions"] == ["1"]
    stream._agent_reference["extension"]["versions"].append("cached")
    assert stream.response["agent_reference"]["extension"]["versions"] == ["1", "live"]
    assert reference["extension"]["versions"] == ["1", "raw"]


def test_recovery_seed_is_copied_once_and_remains_independent():
    item = _CountedTree(_item(), label="seed-output")
    seed = {
        "id": "resp_recovered_copy",
        "output": [item],
        "model": "echo",
        "created_at": datetime(2026, 9, 1, tzinfo=timezone.utc),
        "metadata": {"origin": "seed"},
        "agent_reference": {"type": "agent_reference", "name": "agent", "extension": {"versions": ["1"]}},
        "extension": ({"values": [1]},),
    }
    _CountedTree.visits = []
    stream = ResponseEventStream(response=seed)
    assert _CountedTree.visits == ["seed-output"]
    created = stream.emit_created()
    assert created["response"]["created_at"] == int(seed["created_at"].timestamp())
    assert created["response"]["extension"] == [{"values": [1]}]
    assert stream.response["extension"] == ({"values": [1]},)
    seed["output"][0]["content"][0]["text"] = "seed mutation"
    seed["metadata"]["origin"] = "seed mutation"
    seed["agent_reference"]["extension"]["versions"].append("seed")
    assert stream.response["output"][0]["content"][0]["text"] == "echo"
    assert stream.response["metadata"] == {"origin": "seed"}
    stream.response["output"][0]["content"][0]["text"] = "live mutation"
    stream.response["extension"][0]["values"].append(2)
    stream.response["agent_reference"]["extension"]["versions"].append("live")
    assert seed["extension"][0]["values"] == [1]
    assert created["response"]["output"][0]["content"][0]["text"] == "echo"
    created["response"]["agent_reference"]["extension"]["versions"].append("emitted")
    assert stream._agent_reference["extension"]["versions"] == ["1"]
    message = stream.add_output_item_message()
    added = message.emit_added()
    assert added["output_index"] == 1
    assert added["item"]["agent_reference"]["extension"]["versions"] == ["1"]
    added["item"]["agent_reference"]["extension"]["versions"].append("added")
    assert stream._agent_reference["extension"]["versions"] == ["1"]


def test_seeding_preserves_aliases_within_the_detached_response_graph():
    shared = {"values": [1]}
    seed = {"id": "resp_alias", "output": [], "left": shared, "right": shared}
    stream = ResponseEventStream(response=seed)
    assert stream.response["left"] is stream.response["right"]
    assert stream.response["left"] is not shared
    stream.response["left"]["values"].append(2)
    assert seed["left"]["values"] == [1]


def test_mapping_acceptance_and_constructor_overrides_are_unchanged():
    mapping = UserDict({"id": "resp_mapping", "model": "ignored", "metadata": {"origin": "ignored"}})
    assert _internals.coerce_model_mapping(mapping) is None
    assert _internals.extract_response_fields(mapping) == (None, None)
    with pytest.raises(ValueError, match="response_id is required"):
        ResponseEventStream(response=mapping)
    stream = ResponseEventStream(response_id="resp_explicit", request=mapping)
    assert "model" not in stream.response
    assert "metadata" not in stream.response
    with pytest.raises(ValueError, match="cannot both"):
        ResponseEventStream(response_id="resp_explicit", request={}, response={})
    reference = UserDict({"type": "agent_reference", "name": "override", "extension": {"values": []}})
    stream = ResponseEventStream(
        response_id="resp_override",
        response={"id": "resp_seed", "model": "seed"},
        model="override",
        agent_reference=reference,
    )
    assert stream.response["id"] == "resp_override"
    assert stream.response["model"] == "override"
    assert isinstance(stream.response["agent_reference"], UserDict)
    reference["extension"]["values"].append("raw")
    assert stream.response["agent_reference"]["extension"]["values"] == []
    assert type(stream._agent_reference) is dict
    for model in (None, "", 3):
        assert _internals.extract_response_fields({"model": model, "agent_reference": []}) == (None, None)


def test_materialization_and_remaining_copy_boundaries_are_unchanged():
    stream = ResponseEventStream(response_id="resp_materialize")
    mutable_mapping = UserDict({"values": [1]})
    when = datetime(2026, 9, 1, tzinfo=timezone.utc)
    stream.response["extension"] = {
        "generated": ({"at": when, "tuple": (1, 2)} for _ in range(1)),
        "mapping": mutable_mapping,
    }
    created = stream.emit_created()
    assert created["response"]["extension"]["generated"] == [{"at": int(when.timestamp()), "tuple": [1, 2]}]
    assert isinstance(created["response"]["extension"]["mapping"], UserDict)
    created["response"]["extension"]["mapping"]["values"].append(2)
    assert mutable_mapping["values"] == [1]
    assert list(stream.response["extension"]["generated"]) == []
    generator = (value for value in [1])
    try:
        with pytest.raises(TypeError):
            ResponseEventStream(response={"id": "resp_generator", "output": generator})
    finally:
        generator.close()


def _pipeline():
    orchestrator = object.__new__(_orchestrator._ResponseOrchestrator)
    orchestrator._runtime_options = ResponsesServerOptions(resilient_background=False)
    orchestrator._shutdown_event = None
    ctx = _ExecutionContext(
        response_id="resp_copy_reuse",
        agent_reference={"type": "agent_reference", "name": "agent"},
        model="echo",
        store=False,
        background=False,
        stream=True,
        input_items=[],
        previous_response_id=None,
        conversation_id=None,
        cancellation_signal=asyncio.Event(),
        span=None,
        parsed={},
    )
    return orchestrator, ctx, _orchestrator._PipelineState()


async def _iterate(events):
    for event in events:
        yield event


def _echo_events():
    stream = ResponseEventStream(response_id="resp_copy_reuse")
    message = stream.add_output_item_message()
    text = message.add_text_content()
    return stream, [
        stream.emit_created(),
        stream.emit_in_progress(),
        message.emit_added(),
        text.emit_added(),
        text.emit_delta("echo"),
        text.emit_text_done(),
        text.emit_done(),
        message.emit_done(),
        stream.emit_completed(),
    ]


@pytest.mark.asyncio
async def test_drain_coerces_each_event_once_without_changing_output_or_raw_ownership():
    stream, raw = _echo_events()
    original = deepcopy(raw)
    orchestrator, ctx, state = _pipeline()
    _, _, comparator = _pipeline()
    expected = [await orchestrator._normalize_and_append(ctx, comparator, event) for event in raw]
    with patch.object(_orchestrator, "_coerce_handler_event", wraps=_orchestrator._coerce_handler_event) as copies:
        first = await orchestrator._normalize_and_append(ctx, state, raw[0])
        emitted = [first] + [
            event async for event in orchestrator._drain_remaining_events(ctx, state, _iterate(raw[1:]))
        ]
    assert copies.call_count == len(raw) == 9
    assert emitted + [state.pending_terminal] == expected
    assert state.handler_events == expected
    assert state.next_seq == 9
    assert raw == original
    emitted[2]["item"]["content"].append({"mutated": "emitted"})
    assert raw[2]["item"]["content"] == []
    raw[-2]["item"]["content"][0]["text"] = "raw mutation"
    assert emitted[-1]["item"]["content"][0]["text"] == "echo"
    assert stream.response["output"][0]["content"][0]["text"] == "echo"


@pytest.mark.asyncio
async def test_reused_raw_dict_is_snapshotted_at_each_normalization():
    orchestrator, ctx, state = _pipeline()
    stream = ResponseEventStream(response_id=ctx.response_id)
    raw = stream.emit_created()
    await orchestrator._normalize_and_append(ctx, state, raw)
    raw.clear()
    raw.update(stream.emit_in_progress())
    emitted = [event async for event in orchestrator._drain_remaining_events(ctx, state, _iterate([raw]))]
    raw["response"]["status"] = "raw mutation"
    assert state.handler_events[0]["type"] == "response.created"
    assert state.handler_events[0]["response"]["status"] != "raw mutation"
    assert emitted[0]["response"]["status"] == "in_progress"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bad",
    [
        {"type": "response.completed", "response": {"output": [_item()]}},
        {"type": "response.completed", "response": {"output": [_item()], "status": 123}},
        {"type": "response.completed", "response": "not a snapshot"},
        {"type": "response.output_item.added", "output_index": None, "item": _item()},
        {"type": "response.output_item.added", "output_index": 0},
        {"type": ""},
    ],
)
async def test_bad_event_rejected_before_pipeline_state_advances(bad):
    orchestrator, ctx, state = _pipeline()
    first = ResponseEventStream(response_id=ctx.response_id).emit_created()
    await orchestrator._normalize_and_append(ctx, state, first)
    prior = deepcopy(state.handler_events)
    next_seq = state.next_seq
    failed = {"type": "response.failed"}

    async def make_failed(_ctx, checked_state):
        assert checked_state.handler_events == prior
        assert checked_state.next_seq == next_seq
        assert checked_state.captured_error is not None
        return failed

    with patch.object(orchestrator, "_make_failed_event", side_effect=make_failed) as rejection:
        emitted = [event async for event in orchestrator._drain_remaining_events(ctx, state, _iterate([bad]))]
    assert emitted == []
    assert rejection.call_count == 1
    assert state.pending_terminal is failed
    assert state.handler_events == prior


@pytest.mark.asyncio
async def test_recovered_output_count_and_sequence_baseline_are_preserved():
    orchestrator, ctx, state = _pipeline()
    stream = ResponseEventStream(response={"id": ctx.response_id, "output": [_item()]})
    raw = [stream.emit_created(), stream.emit_in_progress(), stream.emit_completed()]
    state.next_seq = 12
    await orchestrator._normalize_and_append(ctx, state, raw[0])
    emitted = [event async for event in orchestrator._drain_remaining_events(ctx, state, _iterate(raw[1:]), 1)]
    assert state.captured_error is None
    assert [event["sequence_number"] for event in state.handler_events] == [12, 13, 14]
    assert emitted[0]["response"]["output"] == [_item()]
    assert state.pending_terminal["type"] == "response.completed"


@pytest.mark.asyncio
@pytest.mark.parametrize("store", [False, True])
async def test_foreground_echo_asgi_uses_nine_coercions(store):
    raw_events = []
    host = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=False),
        store=InMemoryResponseProvider(),
        configure_observability=None,
    )

    @host.response_handler
    async def echo(request, context, cancellation_signal):
        async for event in TextResponse(context, request, text="echo"):
            raw_events.append(event)
            yield event

    body = json.dumps({"input": "echo", "model": "echo", "stream": True, "store": store}).encode()
    sent = False
    messages = []

    async def receive():
        nonlocal sent
        if not sent:
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}
        await asyncio.Event().wait()

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.4"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/responses",
        "raw_path": b"/responses",
        "query_string": b"",
        "root_path": "",
        "headers": [(b"content-type", b"application/json")],
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 12345),
    }
    with patch.object(_orchestrator, "_coerce_handler_event", wraps=_orchestrator._coerce_handler_event) as copies:
        async with host.router.lifespan_context(host):
            await asyncio.wait_for(host(scope, receive, send), timeout=15)
    events = [
        json.loads(line[5:].strip())
        for line in b"".join(message.get("body", b"") for message in messages).decode().splitlines()
        if line.startswith("data:") and line[5:].strip() != "[DONE]"
    ]
    assert messages[0]["status"] == 200
    assert not messages[-1].get("more_body", False)
    assert len(events) == len(raw_events) == copies.call_count == 9
    assert [event["type"] for event in events] == [event["type"] for event in raw_events]
    assert [event["sequence_number"] for event in events] == list(range(9))
    assert events[-1]["type"] == "response.completed"
    assert events[-1]["response"]["output"][0]["content"][0]["text"] == "echo"
    assert events[-1]["response"]["output"] == raw_events[-1]["response"]["output"]
