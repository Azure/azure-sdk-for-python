# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for the ``upsert_item`` request-prep path — no network, no emulator.

These pin the three helpers the migrated ``upsert_item`` adds:

* ``build_upsert_item_prepared`` -- carries the body like create does (the
  id rides inside the body, which is serialised to JSON bytes), but it
  never mints an id and it can emit ``If-Match`` / ``If-None-Match`` from
  an access condition (an upsert honours ``etag`` / ``match_condition``).
* ``build_upsert_item_request_options`` -- always sets
  ``disableAutomaticIdGeneration`` and honours ``etag`` /
  ``match_condition`` (folded into the ``accessCondition`` shape).
* ``merge_upsert_item_explicit_kwargs`` -- the upsert keyword set:
  create's body-carrying keywords (it keeps ``no_response``) plus
  ``etag`` / ``match_condition``, and no
  ``indexing_directive`` / ``enable_automatic_id_generation``.

Sibling of ``tests/create_item/sync/test_request_prep_unit.py`` (the
body-carrying shape) and
``tests/read_item/sync/test_request_prep_read_item_unit.py`` (the
access-condition translation).
"""
from __future__ import annotations

import json

import pytest

from azure.core import MatchConditions

from azure.cosmos._backend.base import OP_UPSERT_ITEM, PreparedRequest
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._item_dispatch import (
    build_upsert_item_request_options,
    merge_upsert_item_explicit_kwargs,
)
from azure.cosmos._helpers._request_prep import build_upsert_item_prepared


# ---------------------------------------------------------------------------
# Body-carrying baseline shape (like create, not like delete / read)
# ---------------------------------------------------------------------------


def test_baseline_is_write_with_body_not_bodiless():
    """An upsert carries the id inside the body, so the prep serialises the
    body to JSON bytes -- unlike the bodiless delete / read prep. It also copies
    the body's id onto ``item_id`` as a fast-path hint so the binding can skip
    re-parsing the whole body just to read one field."""
    prepared = build_upsert_item_prepared(
        container_link="dbs/d/colls/orders",
        body={"id": "order-42", "pk": "customerA", "total": 109.5},
        partition_key_value="customerA",
        container_rid="RID==",
        kwargs={},
    )
    assert isinstance(prepared, PreparedRequest)
    assert prepared.op == OP_UPSERT_ITEM
    assert prepared.container_link == "dbs/d/colls/orders"
    assert prepared.body_bytes == b'{"id":"order-42","pk":"customerA","total":109.5}'
    assert prepared.partition_key_header == '["customerA"]'
    # The id is authoritative in the body; the prep also forwards it on item_id
    # so the binding reads one Python attribute instead of re-parsing the body.
    assert prepared.item_id == "order-42"
    # Dropped-and-recreated container guard: the rid is stamped under the standard key.
    assert prepared.headers[Constants.ContainerRID] == "RID=="


def test_body_bytes_round_trip_to_the_same_dict():
    """The serialised bytes parse back to the body the customer passed --
    upsert never rewrites the body."""
    body = {"id": "order-42", "pk": "customerA"}
    prepared = build_upsert_item_prepared(
        container_link="dbs/d/colls/c",
        body=body,
        partition_key_value="customerA",
        container_rid=None,
        kwargs={},
    )
    assert json.loads(prepared.body_bytes) == body


# ---------------------------------------------------------------------------
# Never mints an id (the create-vs-upsert difference)
# ---------------------------------------------------------------------------


def test_missing_id_is_not_minted_and_body_is_not_mutated():
    """Unlike create with ``enable_automatic_id_generation=True``, an upsert
    never mints an id. A body without one is serialised as-is and the
    server rejects it -- the prep must not invent an id, which would defeat
    the "replace if present" half of insert-or-replace."""
    body = {"pk": "customerA", "total": 109.5}
    prepared = build_upsert_item_prepared(
        container_link="dbs/d/colls/c",
        body=body,
        partition_key_value="customerA",
        container_rid=None,
        kwargs={},
    )
    assert "id" not in body  # body untouched
    assert b'"id"' not in prepared.body_bytes


def test_options_build_always_disables_id_generation():
    """``build_upsert_item_request_options`` always sets
    ``disableAutomaticIdGeneration=True`` -- the same value the legacy
    ``upsert_item`` wrote every time."""
    request_options = build_upsert_item_request_options({})
    assert request_options["disableAutomaticIdGeneration"] is True


# ---------------------------------------------------------------------------
# Access conditions -- the cases that matter on an upsert.
# ``IfMissing`` (insert-only) is the one that earns its keep here.
# ---------------------------------------------------------------------------


def test_if_missing_translates_to_if_none_match_wildcard_insert_only():
    """``match_condition=IfMissing`` (no etag) narrows insert-or-replace to
    insert-only: ``If-None-Match: *``. This is the classic upsert
    precondition -- a redelivered write fails instead of overwriting."""
    options = build_upsert_item_request_options({"match_condition": MatchConditions.IfMissing})
    assert options["accessCondition"] == {"type": "IfNoneMatch", "condition": "*"}

    prepared = build_upsert_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "order-42", "pk": "customerA"},
        partition_key_value="customerA",
        container_rid=None,
        access_condition=options.get("accessCondition"),
        kwargs={},
    )
    assert prepared.headers["If-None-Match"] == "*"
    assert "If-Match" not in prepared.headers


def test_etag_if_not_modified_translates_to_if_match_guarded_replace():
    """``etag=<v>`` + ``IfNotModified`` narrows it to a version-guarded
    replace: ``If-Match: <v>``."""
    options = build_upsert_item_request_options({
        "etag": "abc",
        "match_condition": MatchConditions.IfNotModified,
    })
    assert options["accessCondition"] == {"type": "IfMatch", "condition": "abc"}

    prepared = build_upsert_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "order-42", "pk": "customerA"},
        partition_key_value="customerA",
        container_rid=None,
        access_condition=options.get("accessCondition"),
        kwargs={},
    )
    assert prepared.headers["If-Match"] == "abc"
    assert "If-None-Match" not in prepared.headers


def test_if_present_translates_to_if_match_wildcard():
    """``match_condition=IfPresent`` (no etag) → ``If-Match: *`` (replace
    only if it exists at all)."""
    options = build_upsert_item_request_options({"match_condition": MatchConditions.IfPresent})
    prepared = build_upsert_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "x", "pk": "a"},
        partition_key_value="a",
        container_rid=None,
        access_condition=options.get("accessCondition"),
        kwargs={},
    )
    assert prepared.headers["If-Match"] == "*"


def test_no_access_condition_emits_no_precondition_headers():
    """A plain upsert (no etag / match_condition) carries neither
    ``If-Match`` nor ``If-None-Match``."""
    prepared = build_upsert_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "x", "pk": "a"},
        partition_key_value="a",
        container_rid=None,
        access_condition=None,
        kwargs={},
    )
    assert "If-Match" not in prepared.headers
    assert "If-None-Match" not in prepared.headers
    # The raw internal shape must never leak onto the wire as a header.
    assert "accessCondition" not in prepared.headers


def test_etag_without_match_condition_raises_value_error_up_front():
    """``etag`` without ``match_condition`` is an application bug; the SDK
    refuses to guess and raises before any network round trip, on the
    caller's own frame -- the same gate delete / read enforce."""
    with pytest.raises(ValueError, match=r"'etag' specified without 'match_condition'"):
        build_upsert_item_request_options({"etag": "abc"})


# ---------------------------------------------------------------------------
# Header-map shaping (same as create / delete / read prep)
# ---------------------------------------------------------------------------


def test_initial_headers_are_flattened_into_outer_headers():
    """``initial_headers={'x-trace-id': 'abc'}`` shows up as a plain
    ``x-trace-id`` entry so the binding forwards it as-is."""
    prepared = build_upsert_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "x", "pk": "a"},
        partition_key_value="a",
        container_rid=None,
        kwargs={"initial_headers": {"x-trace-id": "abc-123"}},
    )
    assert prepared.headers["x-trace-id"] == "abc-123"
    assert "initial_headers" not in prepared.headers
    assert "initialHeaders" not in prepared.headers


def test_trigger_priority_bucket_no_response_land_as_option_keys():
    """The body-carrying option set reaches the headers map under the
    internal option-key names (the binding then renders each on the wire).
    ``no_response`` is kept on upsert, unlike delete / read."""
    prepared = build_upsert_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "x", "pk": "a"},
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
    same mechanism as create / delete / read prep."""
    prepared = build_upsert_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "x", "pk": "a"},
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
    build_upsert_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "x", "pk": "a"},
        partition_key_value="a",
        container_rid=None,
        kwargs=kwargs,
    )
    assert "pre_trigger_include" not in kwargs
    assert kwargs == {"extra_unknown": "left-alone"}


# ---------------------------------------------------------------------------
# merge_upsert_item_explicit_kwargs -- the upsert keyword set
# ---------------------------------------------------------------------------


def test_merge_omits_none_entries():
    """Only the explicit keyword arguments that aren't None land in the
    merged dict -- None means "not supplied" and must not be stamped."""
    kwargs: dict = {}
    merge_upsert_item_explicit_kwargs(
        kwargs,
        pre_trigger_include=None,
        post_trigger_include=None,
        session_token="0:1#42",
        initial_headers=None,
        etag=None,
        match_condition=None,
        priority=None,
        no_response=None,
        retry_write=None,
        throughput_bucket=None,
        availability_strategy=None,
        response_hook=None,
    )
    assert kwargs == {"session_token": "0:1#42"}


def test_merge_keeps_etag_match_condition_and_no_response():
    """Upsert is the one operation that keeps both the body-carrying
    ``no_response`` (unlike delete / read) and the
    ``etag`` / ``match_condition`` precondition pair (unlike create, which
    drops them)."""
    kwargs: dict = {}
    merge_upsert_item_explicit_kwargs(
        kwargs,
        etag="abc",
        match_condition=MatchConditions.IfNotModified,
        no_response=True,
    )
    assert kwargs["etag"] == "abc"
    assert kwargs["match_condition"] == MatchConditions.IfNotModified
    assert kwargs["no_response"] is True


def test_merge_does_not_accept_create_only_kwargs():
    """``indexing_directive`` / ``enable_automatic_id_generation`` are not
    on the public ``upsert_item`` signature, so the merge helper must not
    even accept those parameter names."""
    kwargs: dict = {}
    with pytest.raises(TypeError):
        merge_upsert_item_explicit_kwargs(kwargs, indexing_directive=1)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        merge_upsert_item_explicit_kwargs(  # type: ignore[call-arg]
            kwargs, enable_automatic_id_generation=True
        )


# ---------------------------------------------------------------------------
# populate_query_metrics deprecation (sync-only)
# ---------------------------------------------------------------------------


def test_populate_query_metrics_warns_and_writes_for_any_explicit_value():
    """The legacy ``upsert_item`` warned (and still wrote the option) for any
    explicit ``populate_query_metrics`` value, ``False`` included. The
    migrated options build keeps that exact behaviour so nothing regresses
    for the deprecated flag."""
    with pytest.warns(DeprecationWarning):
        opts_true = build_upsert_item_request_options({}, populate_query_metrics=True)
    assert opts_true["populateQueryMetrics"] is True

    with pytest.warns(DeprecationWarning):
        opts_false = build_upsert_item_request_options({}, populate_query_metrics=False)
    assert opts_false["populateQueryMetrics"] is False


def test_populate_query_metrics_none_is_silent():
    """``None`` (the default, and what the async sibling always passes)
    emits no warning and writes no option."""
    import warnings as _warnings

    with _warnings.catch_warnings():
        _warnings.simplefilter("error")  # any warning becomes an error
        request_options = build_upsert_item_request_options({}, populate_query_metrics=None)
    assert "populateQueryMetrics" not in request_options

