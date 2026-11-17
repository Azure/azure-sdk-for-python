# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Strip-on-egress + ingress conformance (spec 025 §A.2 / §7.2).

Covers the strip helper, the SSE encoder chokepoint, the live-object-untouched
invariants (T17a/T17r), and the empty-map normalisation (T15r2). The HTTP
endpoint egress/ingress are covered by the contract tests in
``tests/contract/test_internal_metadata_egress.py``.
"""

from __future__ import annotations

from copy import deepcopy

from azure.ai.agentserver.responses import CreateResponse, ResponseEventStream
from azure.ai.agentserver.responses._egress import strip_internal_metadata
from azure.ai.agentserver.responses.streaming._sse import encode_sse_event


def test_strip_removes_item_bag_recursively():
    payload = {
        "id": "r",
        "output": [
            {"type": "message", "id": "m", "internal_metadata": {"phase": "g"}},
            {"type": "message", "id": "m2", "internal_metadata": {}},
        ],
        "input": [{"type": "message", "id": "i", "internal_metadata": {"x": 1}}],
    }
    strip_internal_metadata(payload)
    assert "internal_metadata" not in payload["output"][0]
    assert "internal_metadata" not in payload["output"][1]
    assert "internal_metadata" not in payload["input"][0]


def test_strip_removes_response_reserved_key_preserves_client_keys():
    payload = {"id": "r", "metadata": {"user": "x", "_internal_metadata": '{"cp":3}'}, "output": []}
    strip_internal_metadata(payload)
    assert payload["metadata"] == {"user": "x"}


def test_t15r2_reserved_key_only_normalises_to_none():
    payload = {"id": "r", "metadata": {"_internal_metadata": '{"cp":3}'}, "output": []}
    strip_internal_metadata(payload)
    assert payload["metadata"] is None


def test_strip_is_failclosed_on_unexpected_shapes():
    assert strip_internal_metadata(None) is None
    assert strip_internal_metadata("scalar") == "scalar"
    assert strip_internal_metadata(5) == 5
    assert strip_internal_metadata({"no_items": True}) == {"no_items": True}


def test_strip_nested_lifecycle_event_response_envelope():
    # response.created / .completed wrap the full envelope.
    event = {
        "type": "response.completed",
        "response": {
            "id": "r",
            "metadata": {"user": "x", "_internal_metadata": '{"cp":3}'},
            "output": [{"type": "message", "id": "m", "internal_metadata": {"phase": "g"}}],
        },
    }
    strip_internal_metadata(event)
    assert event["response"]["metadata"] == {"user": "x"}
    assert "internal_metadata" not in event["response"]["output"][0]


def _stream_with_stamped_item():
    req = CreateResponse({"model": "m", "input": "hi"})
    stream = ResponseEventStream(response_id="resp_1", request=req)
    stream.internal_metadata["cp"] = 3
    return stream, req


def test_t12_t13_sse_lifecycle_events_strip_reserved_key():
    stream, _ = _stream_with_stamped_item()
    created = encode_sse_event(stream.emit_created())
    assert "_internal_metadata" not in created
    in_prog = encode_sse_event(stream.emit_in_progress())
    assert "_internal_metadata" not in in_prog
    completed = encode_sse_event(stream.emit_completed())
    assert "_internal_metadata" not in completed


def test_t14_t15_sse_item_events_strip_internal_metadata():
    stream, _ = _stream_with_stamped_item()
    encode_sse_event(stream.emit_created())
    encode_sse_event(stream.emit_in_progress())
    msg = stream.add_output_item_message()
    msg.internal_metadata["phase"] = "gather"
    added = encode_sse_event(msg.emit_added())
    assert "internal_metadata" not in added
    text = msg.add_text_content()
    encode_sse_event(text.emit_added())
    encode_sse_event(text.emit_delta("hi"))
    encode_sse_event(text.emit_text_done("hi"))
    encode_sse_event(text.emit_done())
    done = encode_sse_event(msg.emit_done())
    assert "internal_metadata" not in done


def test_t17a_t17r_live_objects_untouched_after_sse_encode():
    stream, _ = _stream_with_stamped_item()
    encode_sse_event(stream.emit_created())
    encode_sse_event(stream.emit_in_progress())
    msg = stream.add_output_item_message()
    msg.internal_metadata["phase"] = "gather"
    encode_sse_event(msg.emit_added())
    text = msg.add_text_content()
    encode_sse_event(text.emit_added())
    encode_sse_event(text.emit_delta("hi"))
    encode_sse_event(text.emit_text_done("hi"))
    encode_sse_event(text.emit_done())
    encode_sse_event(msg.emit_done())
    # Encode a terminal carrying the full envelope.
    encode_sse_event(stream.emit_completed())
    # T17r: live response still carries the reserved key.
    assert stream.response["metadata"]["_internal_metadata"] == '{"cp":3}'
    # T17a: live output item still carries its bag.
    assert dict(stream.response["output"][0]["internal_metadata"]) == {"phase": "gather"}


def test_strip_mutates_in_place_returns_same_object():
    payload = {"output": [{"internal_metadata": {"a": 1}}]}
    result = strip_internal_metadata(payload)
    assert result is payload
