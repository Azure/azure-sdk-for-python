# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Conformance tests for the ``internal_metadata`` surface (spec 025 §A.1 / §A.1.2).

Covers the item-level and response-level live ``MutableMapping[str, Any]`` views,
the output-item builders' stamping, and the ``ResponseEventStream`` proxy.
Test IDs map to spec 025 §7.1.
"""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses import CreateResponse, ResponseEventStream
from azure.ai.agentserver.responses.models._generated import ResponseObject
from azure.ai.agentserver.responses.models._generated.sdk.models.models._models import (
    OutputItemMessage,
)


def _item() -> OutputItemMessage:
    return OutputItemMessage(id="item_1", role="assistant", content=[], status="completed")


def _response() -> ResponseObject:
    return ResponseObject(
        {"id": "resp_1", "object": "response", "status": "in_progress", "output": [], "model": "m"}
    )


# --------------------------------------------------------------------------
# §7.1 Item internal-metadata
# --------------------------------------------------------------------------


def test_t1_item_empty_view_when_unset():
    item = _item()
    assert item.internal_metadata is not None
    assert len(item.internal_metadata) == 0
    assert "internal_metadata" not in item.as_dict()


def test_t2_item_roundtrips_under_json_key():
    item = _item()
    item.internal_metadata["k"] = "v"
    assert item.as_dict()["internal_metadata"] == {"k": "v"}
    reloaded = OutputItemMessage(item.as_dict())
    assert dict(reloaded.internal_metadata) == {"k": "v"}


def test_t3_item_any_values_no_typeerror():
    item = _item()
    item.internal_metadata["n"] = 123
    item.internal_metadata["b"] = True
    item.internal_metadata["nested"] = {"a": [1, 2]}
    reloaded = OutputItemMessage(item.as_dict())
    assert reloaded.internal_metadata["n"] == 123
    assert reloaded.internal_metadata["b"] is True
    assert reloaded.internal_metadata["nested"] == {"a": [1, 2]}


def test_t3_item_non_string_key_raises():
    item = _item()
    with pytest.raises(TypeError):
        item.internal_metadata[5] = "x"  # type: ignore[index]


def test_t4_item_in_place_mutation_writes_through():
    item = _item()
    item.internal_metadata["k"] = "v"
    item.internal_metadata.update({"a": 1, "b": 2})
    item.internal_metadata.pop("a")
    del item.internal_metadata["b"]
    assert dict(item.internal_metadata) == {"k": "v"}
    assert item.as_dict()["internal_metadata"] == {"k": "v"}


def test_t5_item_clear_removes_key():
    item = _item()
    item.internal_metadata["k"] = "v"
    item.internal_metadata = None
    assert "internal_metadata" not in item.as_dict()
    item.internal_metadata["k"] = "v"
    item.internal_metadata = {}
    assert "internal_metadata" not in item.as_dict()


def test_t6_item_strip_internal_metadata_idempotent():
    item = _item()
    item.internal_metadata["k"] = "v"
    item.strip_internal_metadata()
    assert "internal_metadata" not in item.as_dict()
    item.strip_internal_metadata()  # idempotent
    assert "internal_metadata" not in item.as_dict()


def test_t7_v_shaped_dict_loads_empty_view():
    # A dict with no internal_metadata key loads to an empty live view.
    item = OutputItemMessage(
        {"type": "message", "id": "m", "role": "assistant", "content": [], "status": "completed"}
    )
    assert len(item.internal_metadata) == 0
    # Writing lazily creates the key.
    item.internal_metadata["k"] = "v"
    assert item.as_dict()["internal_metadata"] == {"k": "v"}


def test_t7a_builder_stamping_flows_to_event_and_output():
    req = CreateResponse({"model": "m", "input": "hi"})
    stream = ResponseEventStream(response_id="resp_1", request=req)
    stream.emit_created()
    stream.emit_in_progress()
    msg = stream.add_output_item_message()
    msg.internal_metadata["phase"] = "gather"
    added = msg.emit_added()
    assert added["item"]["internal_metadata"] == {"phase": "gather"}
    text = msg.add_text_content()
    text.emit_added()
    text.emit_delta("hi")
    text.emit_text_done("hi")
    text.emit_done()
    done = msg.emit_done()
    assert done["item"]["internal_metadata"] == {"phase": "gather"}
    assert dict(stream.response.output[0].internal_metadata) == {"phase": "gather"}


# --------------------------------------------------------------------------
# §7.1 Response-level internal-metadata
# --------------------------------------------------------------------------


def test_t1r_response_empty_view_when_unset():
    resp = _response()
    assert resp.internal_metadata is not None
    assert len(resp.internal_metadata) == 0


def test_t2r_response_stores_under_reserved_key():
    resp = _response()
    resp.internal_metadata["phase"] = 3
    assert resp.as_dict()["metadata"]["_internal_metadata"] == '{"phase":3}'
    assert dict(resp.internal_metadata) == {"phase": 3}


def test_t3r_in_place_mutation_writes_through():
    resp = _response()
    resp.internal_metadata["a"] = 1
    resp.internal_metadata["b"] = "x"
    del resp.internal_metadata["a"]
    assert dict(resp.internal_metadata) == {"b": "x"}


def test_t4r_does_not_clobber_client_metadata():
    resp = _response()
    resp.metadata = {"user": "x"}
    resp.internal_metadata["phase"] = 3
    assert set(resp.as_dict()["metadata"].keys()) == {"user", "_internal_metadata"}


def test_t5r_clear_removes_only_reserved_key():
    resp = _response()
    resp.metadata = {"user": "x"}
    resp.internal_metadata["phase"] = 3
    resp.internal_metadata = None
    assert dict(resp.metadata) == {"user": "x"}


def test_t6r_512_char_guard():
    resp = _response()
    with pytest.raises(ValueError):
        resp.internal_metadata["big"] = "x" * 600


def test_t6r2_16_key_guard():
    resp15 = _response()
    resp15.metadata = {f"k{i}": "v" for i in range(15)}
    resp15.internal_metadata["p"] = 1  # 16th key — ok
    assert "_internal_metadata" in resp15.metadata

    resp16 = _response()
    resp16.metadata = {f"k{i}": "v" for i in range(16)}
    with pytest.raises(ValueError):
        resp16.internal_metadata["p"] = 1


def test_t7r_v_shaped_response_empty_view():
    resp = _response()
    assert len(resp.internal_metadata) == 0
    resp_no_md = ResponseObject(
        {"id": "r", "object": "response", "status": "in_progress", "output": [], "model": "m"}
    )
    assert len(resp_no_md.internal_metadata) == 0


def test_t10r_stream_proxy_is_response_view():
    req = CreateResponse({"model": "m", "input": "hi"})
    stream = ResponseEventStream(response_id="resp_1", request=req)
    stream.internal_metadata["phase"] = 3
    assert dict(stream.response.internal_metadata) == {"phase": 3}
    stream.response.internal_metadata["x"] = 1
    assert stream.internal_metadata["x"] == 1


def test_t28d_response_reserved_key_roundtrips():
    resp = _response()
    resp.internal_metadata["phase"] = 3
    reloaded = ResponseObject(resp.as_dict())
    assert dict(reloaded.internal_metadata) == {"phase": 3}
    assert reloaded.as_dict()["metadata"]["_internal_metadata"] == '{"phase":3}'


def test_t7a_compact_deterministic_encoding():
    # Deterministic so checkpoint idempotency byte-compare is stable.
    resp = _response()
    resp.internal_metadata["b"] = 2
    resp.internal_metadata["a"] = 1
    encoded = resp.as_dict()["metadata"]["_internal_metadata"]
    assert encoded == '{"a":1,"b":2}'  # sorted keys, compact separators
