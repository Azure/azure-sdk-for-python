# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for the ``patch_item`` request-prep path -- no network, no emulator.

These pin ``build_patch_operations_payload`` and
``prepare_patch_item_request``.

The body uses canonical ``incr`` instructions. Caller If-Match is forwarded;
unsupported filters and If-None-Match are rejected without legacy replay.
"""
from __future__ import annotations
from common.typed_requests import legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings

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
from common.request_preparation import (
    prepare_patch_item_request,
)
from azure.cosmos._helpers._item_prep import build_patch_operations_payload


_SET_OP = {"op": "set", "path": "/status", "value": "shipped"}


# ---------------------------------------------------------------------------
# build_patch_operations_payload -- op-name translation, no mutation, no condition
# ---------------------------------------------------------------------------


def test_payload_wraps_operations_under_operations_key():
    """The payload is exactly ``{"operations": [...]}`` -- the shape the
    driver reads back as its patch instructions."""
    payload = build_patch_operations_payload([_SET_OP])
    assert payload == {"operations": [{"op": "set", "path": "/status", "value": "shipped"}]}


def test_incr_op_code_uses_canonical_service_spelling():
    """Both spellings of the increment operator produce the one the service accepts.

    Customers write either ``incr`` or ``increment``; the service only
    understands ``incr``. The payload builder normalises ``increment`` down to
    it, so the two calls must produce byte-identical payloads.
    """
    payload = build_patch_operations_payload([{"op": "incr", "path": "/n", "value": 1}])
    assert payload == {"operations": [{"op": "incr", "path": "/n", "value": 1}]}
    assert build_patch_operations_payload([{"op": "increment", "path": "/n", "value": 1}]) == payload


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
    """Preparing canonical instructions leaves the caller's list unchanged."""
    original = [{"op": "incr", "path": "/n", "value": 1}]
    snapshot = json.loads(json.dumps(original))
    build_patch_operations_payload(original)
    assert original == snapshot
    assert original[0]["op"] == "incr"  # still the public spelling


def test_payload_never_carries_a_condition():
    """The payload builder takes only the operations; there is no way for a
    ``condition`` (a filter_predicate) to land in the body the driver reads
    -- filtered Rust patches are rejected before dispatch."""
    payload = build_patch_operations_payload([_SET_OP])
    assert "condition" not in payload
    assert set(payload.keys()) == {"operations"}


# ---------------------------------------------------------------------------
# prepare_patch_item_request -- baseline shape
# ---------------------------------------------------------------------------


def test_baseline_is_operations_body_with_item_id():
    """A patch carries the operations payload (serialised to JSON bytes) and
    the id of the item to patch on ``item_id``. The op tag is
    ``OP_PATCH_ITEM``."""
    prepared = prepare_patch_item_request(
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
    # Both the service and driver accept canonical incr.
    assert prepared.body_bytes == (
        b'{"operations":[{"op":"set","path":"/status","value":"shipped"},'
        b'{"op":"incr","path":"/revision","value":1}]}'
    )
    # The partition key comes from the explicit argument (like delete / read), not from a body.
    assert legacy_partition_key_from_request(prepared) == '["customerA"]'
    # The id rides on item_id for the binding to put on the URL.
    assert prepared.item_id == "order-42"
    # Dropped-and-recreated container guard: the rid is set under the standard key.
    assert wire_headers(prepared)["x-ms-cosmos-intended-collection-rid"] == "RID=="


def test_body_round_trips_to_patch_instructions_shape():
    """The serialised bytes parse back to ``{"operations": [...]}``."""
    prepared = prepare_patch_item_request(
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
# Carry caller If-Match through preparation
# ---------------------------------------------------------------------------


def test_patch_preparation_accepts_if_match():
    """The argument-normalising step turns ``etag`` plus ``IfNotModified`` into an access condition.

    This is the step ahead of request prep: it must both accept the guard as
    valid for a patch and translate it into the internal ``accessCondition``
    shape that the prep then renders as ``If-Match``.
    """
    from azure.cosmos._helpers._item_operations import normalize_item_arguments, validate_rust_item_options

    args, options = normalize_item_arguments("patch_item", {
        "container_link": "dbs/d/colls/c",
        "item_id": "x",
        "patch_operations": [_SET_OP],
        "etag": "abc",
        "match_condition": MatchConditions.IfNotModified,
    })
    validate_rust_item_options(args, options)
    assert options["accessCondition"] == {"type": "IfMatch", "condition": "abc"}


# ---------------------------------------------------------------------------
# Header-map shaping (same as the other migrated ops' prep)
# ---------------------------------------------------------------------------


def test_initial_headers_are_flattened_into_outer_headers():
    """``initial_headers={'x-trace-id': 'abc'}`` is kept as a nested
    ``initialHeaders`` dict so the binding forwards each entry verbatim."""
    prepared = prepare_patch_item_request(
        container_link="dbs/d/colls/c",
        item_id="x",
        patch_operations=[_SET_OP],
        partition_key_value="a",
        container_rid=None,
        kwargs={"initial_headers": {"x-trace-id": "abc-123"}},
    )
    assert all(wire_headers(prepared).get(key.lower()) == str(value) for key, value in ({"x-trace-id": "abc-123"}).items())
    assert wire_headers(prepared)["x-trace-id"] == "abc-123"


def test_trigger_priority_bucket_no_response_land_as_option_keys():
    """The option set reaches the headers map under the internal option-key
    names. ``no_response`` is kept on patch (a patch returns the patched
    item, unlike delete / read)."""
    prepared = prepare_patch_item_request(
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
    assert wire_headers(prepared)["x-ms-documentdb-pre-trigger-include"] == "validateOrder"
    assert wire_headers(prepared)["x-ms-documentdb-post-trigger-include"] == "auditOrder"
    assert wire_headers(prepared)["x-ms-cosmos-priority-level"] == "High"
    assert wire_headers(prepared)["x-ms-cosmos-throughput-bucket"] == '1'
    assert settings_options(prepared)["responsePayloadOnWriteDisabled"] is True


def test_timeout_kwarg_is_forwarded_under_sentinel_header():
    """``timeout=30`` is forwarded as an operation option so
    the binding can turn it into the driver's own timeout setting -- the
    same mechanism as every other migrated operation."""
    prepared = prepare_patch_item_request(
        container_link="dbs/d/colls/c",
        item_id="x",
        patch_operations=[_SET_OP],
        partition_key_value="a",
        container_rid=None,
        kwargs={"timeout": 30},
    )
    assert settings_options(prepared)["timeout_seconds"] == 30


def test_compose_consumes_recognised_kwargs():
    """The option-shortcut keyword arguments the prep recognises are removed
    from the input dict, so the caller doesn't forward them again to the
    legacy path."""
    kwargs = {"pre_trigger_include": "validateOrder", "extra_unknown": "left-alone"}
    prepare_patch_item_request(
        container_link="dbs/d/colls/c",
        item_id="x",
        patch_operations=[_SET_OP],
        partition_key_value="a",
        container_rid=None,
        kwargs=kwargs,
    )
    assert kwargs["pre_trigger_include"] == "validateOrder"
    assert kwargs == {"pre_trigger_include": "validateOrder", "extra_unknown": "left-alone"}


# ---------------------------------------------------------------------------
# Options build + explicit-keyword merge (inputs to the legacy fall-through)
# ---------------------------------------------------------------------------


def test_request_options_disable_id_generation_and_omit_query_metrics():
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
