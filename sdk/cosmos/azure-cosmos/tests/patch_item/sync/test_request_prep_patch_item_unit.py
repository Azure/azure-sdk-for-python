# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for the ``patch_item`` request-prep path — no network, no emulator.

These pin ``build_patch_operations_payload`` and
``build_patch_item_prepared``.

Two things are checked: the body never carries a condition, and the prep
never emits an ``If-Match`` / ``If-None-Match`` header (a patch with a
filter or a version guard takes the legacy path). They also pin the one
operation name that differs between the public spelling (``incr``) and
the driver's spelling (``increment``).
"""
from __future__ import annotations

import json
import sys

import pytest

from azure.core import MatchConditions

from azure.cosmos._backend.operations import OP_PATCH_ITEM
from azure.cosmos._backend.contracts import PreparedRequest
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._item_dispatch import (
    build_patch_item_request_options,
    merge_patch_item_explicit_kwargs,
)
from azure.cosmos._helpers._request_item import build_patch_item_prepared, build_patch_operations_payload


_SET_OP = {"op": "set", "path": "/status", "value": "shipped"}


# ---------------------------------------------------------------------------
# build_patch_operations_payload -- op-name translation, no mutation, no condition
# ---------------------------------------------------------------------------


def test_payload_wraps_operations_under_operations_key():
    """The payload is exactly ``{"operations": [...]}`` -- the shape the
    driver reads back as its patch instructions."""
    payload = build_patch_operations_payload([_SET_OP])
    assert payload == {"operations": [{"op": "set", "path": "/status", "value": "shipped"}]}


def test_incr_op_code_is_translated_to_increment():
    """The one operation name that differs: the public/REST ``incr`` becomes
    the driver's ``increment`` so the driver understands it. The ``op`` key
    stays first in the dict so the bytes on the wire stay stable."""
    payload = build_patch_operations_payload([{"op": "incr", "path": "/n", "value": 1}])
    assert payload == {"operations": [{"op": "increment", "path": "/n", "value": 1}]}


def test_other_op_codes_pass_through_unchanged():
    """add / set / replace / remove / move are spelled identically on both
    sides and must not be rewritten."""
    ops = [
        {"op": "add", "path": "/tags/-", "value": "x"},
        {"op": "set", "path": "/a", "value": 1},
        {"op": "replace", "path": "/b", "value": 2},
        {"op": "remove", "path": "/c"},
        {"op": "move", "from": "/d", "path": "/e"},
    ]
    payload = build_patch_operations_payload(ops)
    assert payload["operations"] == ops


def test_input_operations_are_not_mutated():
    """Translating ``incr`` must not change the caller's list or dicts -- a
    customer who reuses the same ``patch_operations`` across calls is
    unaffected (the translated operation is a shallow copy)."""
    original = [{"op": "incr", "path": "/n", "value": 1}]
    snapshot = json.loads(json.dumps(original))
    build_patch_operations_payload(original)
    assert original == snapshot
    assert original[0]["op"] == "incr"  # still the public spelling


def test_payload_never_carries_a_condition():
    """The payload builder takes only the operations; there is no way for a
    ``condition`` (a filter_predicate) to land in the body the driver reads
    -- a patch with a filter is routed to the legacy path instead."""
    payload = build_patch_operations_payload([_SET_OP])
    assert "condition" not in payload
    assert set(payload.keys()) == {"operations"}


# ---------------------------------------------------------------------------
# build_patch_item_prepared -- baseline shape
# ---------------------------------------------------------------------------


def test_baseline_is_operations_body_with_item_id():
    """A patch carries the operations payload (serialised to JSON bytes) and
    the id of the document to patch on ``item_id``. The op tag is
    ``OP_PATCH_ITEM``."""
    prepared = build_patch_item_prepared(
        container_link="dbs/d/colls/orders",
        item_id="order-42",
        patch_operations=[
            {"op": "set", "path": "/status", "value": "shipped"},
            {"op": "incr", "path": "/revision", "value": 1},
        ],
        partition_key_value="customerA",
        container_rid="RID==",
        kwargs={},
    )
    assert isinstance(prepared, PreparedRequest)
    assert prepared.op == OP_PATCH_ITEM
    assert prepared.container_link == "dbs/d/colls/orders"
    # incr -> increment in the serialised body; op key stays first.
    assert prepared.body_bytes == (
        b'{"operations":[{"op":"set","path":"/status","value":"shipped"},'
        b'{"op":"increment","path":"/revision","value":1}]}'
    )
    # The partition key comes from the explicit argument (like delete / read), not from a body.
    assert prepared.partition_key_header == '["customerA"]'
    # The id rides on item_id for the binding to put on the URL.
    assert prepared.item_id == "order-42"
    # Dropped-and-recreated container guard: the rid is stamped under the standard key.
    assert prepared.headers[Constants.ContainerRID] == "RID=="


def test_body_round_trips_to_patch_instructions_shape():
    """The serialised bytes parse back to ``{"operations": [...]}``."""
    prepared = build_patch_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        patch_operations=[_SET_OP],
        partition_key_value="a",
        container_rid=None,
        kwargs={},
    )
    assert json.loads(prepared.body_bytes) == {
        "operations": [{"op": "set", "path": "/status", "value": "shipped"}]
    }


# ---------------------------------------------------------------------------
# Never emit a precondition header from the prep
# ---------------------------------------------------------------------------


def test_prep_never_emits_if_match_or_if_none_match():
    """Even if a stray ``accessCondition`` reached the option dict, the patch
    prep must not emit ``If-Match`` / ``If-None-Match`` -- the driver rejects
    a caller-set precondition on a patch. (In practice a guarded patch is
    routed to the legacy path before this builder runs; this checks the
    builder itself never sets a precondition.)"""
    prepared = build_patch_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        patch_operations=[_SET_OP],
        partition_key_value="a",
        container_rid=None,
        kwargs={"etag": "abc", "match_condition": MatchConditions.IfNotModified},
    )
    assert "If-Match" not in prepared.headers
    assert "If-None-Match" not in prepared.headers
    assert "accessCondition" not in prepared.headers


# ---------------------------------------------------------------------------
# Header-map shaping (same as the other migrated ops' prep)
# ---------------------------------------------------------------------------


def test_initial_headers_are_flattened_into_outer_headers():
    """``initial_headers={'x-trace-id': 'abc'}`` is kept as a nested
    ``initialHeaders`` dict so the binding forwards each entry verbatim."""
    prepared = build_patch_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        patch_operations=[_SET_OP],
        partition_key_value="a",
        container_rid=None,
        kwargs={"initial_headers": {"x-trace-id": "abc-123"}},
    )
    assert prepared.headers["initialHeaders"] == {"x-trace-id": "abc-123"}
    assert "x-trace-id" not in prepared.headers


def test_trigger_priority_bucket_no_response_land_as_option_keys():
    """The option set reaches the headers map under the internal option-key
    names. ``no_response`` is kept on patch (a patch returns the patched
    document, unlike delete / read)."""
    prepared = build_patch_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        patch_operations=[_SET_OP],
        partition_key_value="a",
        container_rid=None,
        kwargs={
            "pre_trigger_include": "validateOrder",
            "post_trigger_include": "auditOrder",
            "priority": "High",
            "throughput_bucket": 1,
            "no_response": True,
        },
    )
    assert prepared.headers["preTriggerInclude"] == "validateOrder"
    assert prepared.headers["postTriggerInclude"] == "auditOrder"
    assert prepared.headers["priorityLevel"] == "High"
    assert prepared.headers["throughputBucket"] == 1
    assert prepared.headers["responsePayloadOnWriteDisabled"] is True


def test_timeout_kwarg_is_forwarded_under_sentinel_header():
    """``timeout=30`` is forwarded as ``__overall_timeout_seconds: 30`` so
    the binding can lift it into the driver's own timeout setting -- the
    same mechanism as every other migrated operation."""
    prepared = build_patch_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        patch_operations=[_SET_OP],
        partition_key_value="a",
        container_rid=None,
        kwargs={"timeout": 30},
    )
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 30


def test_compose_consumes_recognised_kwargs():
    """The option-shortcut keyword arguments the prep recognises are removed
    from the input dict, so the caller doesn't forward them again to the
    legacy path."""
    kwargs = {"pre_trigger_include": "validateOrder", "extra_unknown": "left-alone"}
    build_patch_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        patch_operations=[_SET_OP],
        partition_key_value="a",
        container_rid=None,
        kwargs=kwargs,
    )
    assert "pre_trigger_include" not in kwargs
    assert kwargs == {"extra_unknown": "left-alone"}


# ---------------------------------------------------------------------------
# Options build + explicit-keyword merge (inputs to the legacy fall-through)
# ---------------------------------------------------------------------------


def test_request_options_set_disable_auto_id_and_no_metrics_knob():
    """``build_patch_item_request_options`` sets
    ``disableAutomaticIdGeneration`` (matching the legacy ``patch_item``) and
    -- unlike create / upsert -- never writes a ``populateQueryMetrics``
    option (patch never exposed it)."""
    options = build_patch_item_request_options({})
    assert options["disableAutomaticIdGeneration"] is True
    assert "populateQueryMetrics" not in options


def test_request_options_fold_etag_pair_into_access_condition():
    """A valid ``etag`` + ``match_condition`` pair becomes the internal
    ``accessCondition`` shape -- the signal the helper reads to route a
    version-guarded patch to the legacy path (the driver can't honour it)."""
    options = build_patch_item_request_options({
        "etag": "abc",
        "match_condition": MatchConditions.IfNotModified,
    })
    assert options["accessCondition"] == {"type": "IfMatch", "condition": "abc"}


def test_etag_without_match_condition_raises_up_front():
    """``etag`` without ``match_condition`` is an application bug; the options
    build refuses to guess and raises before any network round trip -- the
    same gate delete / read / upsert enforce, firing on the caller's own
    frame."""
    with pytest.raises(ValueError, match=r"'etag' specified without 'match_condition'"):
        build_patch_item_request_options({"etag": "abc"})


def test_merge_explicit_kwargs_omits_none_and_keeps_no_response():
    """Only the explicit keyword arguments that aren't None land in the
    kwargs dict. Patch keeps ``no_response`` (it's a write that returns a
    body) and has no ``initial_headers`` parameter (that rides in
    ``**kwargs``)."""
    kwargs: dict = {}
    merge_patch_item_explicit_kwargs(
        kwargs,
        pre_trigger_include="validateOrder",
        no_response=True,
        session_token=None,  # omitted
    )
    assert kwargs == {"pre_trigger_include": "validateOrder", "no_response": True}


if __name__ == "__main__":

    sys.exit(pytest.main([__file__, "-v"]))
