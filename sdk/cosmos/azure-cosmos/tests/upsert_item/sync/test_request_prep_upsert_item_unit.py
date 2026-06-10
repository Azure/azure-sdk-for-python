# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Pure-Python unit tests for the ``upsert_item`` wire-prep path.

No network, no Cosmos emulator, no Rust binding required. Pins the
behaviour of the three pure helpers that the migrated ``upsert_item``
adds:

* ``build_upsert_item_prepared`` -- write-with-body like create (the id
  rides inside the body, the body is serialised to JSON bytes), but it
  never mints an id and it emits ``If-Match`` / ``If-None-Match`` from an
  access condition (an upsert honours ``etag`` / ``match_condition``).
* ``build_upsert_item_request_options`` -- always sets
  ``disableAutomaticIdGeneration`` and honours ``etag`` /
  ``match_condition`` (consumed into the ``accessCondition`` shape).
* ``merge_upsert_item_explicit_kwargs`` -- the upsert kwarg set:
  create's write-with-body kwargs (keeps ``no_response``) plus
  ``etag`` / ``match_condition``, and *no*
  ``indexing_directive`` / ``enable_automatic_id_generation``.

Sibling of ``tests/create_item/sync/test_request_prep_unit.py`` (the
write-with-body shape) and
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
# Write-with-body baseline shape (parity with create, not with delete/read)
# ---------------------------------------------------------------------------


def test_baseline_is_write_with_body_not_bodiless():
    """An upsert carries the id inside the body, so the prep serialises
    the body to JSON bytes and leaves ``item_id`` unset -- unlike the
    bodiless delete / read prep."""
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
    # The id rides in the body, so the dedicated id slot stays empty
    # (a create / upsert never carry item_id; delete / read do).
    assert prepared.item_id is None
    # Drop-and-recreate guard: rid stamped under the canonical key.
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
    """Unlike create with ``enable_automatic_id_generation=True``, an
    upsert never mints an id. A body without one is serialised as-is and
    the server rejects it -- the prep must not invent an id (which would
    defeat the "replace if present" half of insert-or-replace)."""
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
    """``build_upsert_item_request_options`` hardwires
    ``disableAutomaticIdGeneration=True`` -- the same value the legacy
    ``upsert_item`` wrote unconditionally."""
    request_options = build_upsert_item_request_options({})
    assert request_options["disableAutomaticIdGeneration"] is True


# ---------------------------------------------------------------------------
# Access-condition translation -- the upsert-meaningful cases.
# ``IfMissing`` (insert-only) is the case that earns its keep on an upsert.
# ---------------------------------------------------------------------------


def test_if_missing_translates_to_if_none_match_wildcard_insert_only():
    """``match_condition=IfMissing`` (no etag) narrows the insert-or-replace
    to *insert-only*: ``If-None-Match: *``. This is the canonical upsert
    precondition (a redelivered write fails instead of overwriting)."""
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
    refuses to guess and raises before any network round trip (on the
    caller's frame), the same gate delete / read enforce."""
    with pytest.raises(ValueError, match=r"'etag' specified without 'match_condition'"):
        build_upsert_item_request_options({"etag": "abc"})


# ---------------------------------------------------------------------------
# Header-map shaping (parity with create / delete / read prep)
# ---------------------------------------------------------------------------


def test_initial_headers_are_flattened_into_outer_headers():
    """``initial_headers={'x-trace-id': 'abc'}`` surfaces as a bare
    ``x-trace-id`` entry so the binding forwards it verbatim."""
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
    """The write-with-body option set reaches the headers map under the
    internal option-key names (the binding then renders each on the
    wire). ``no_response`` is kept on upsert (unlike delete / read)."""
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
    """``timeout=30`` → ``__overall_timeout_seconds: 30`` so the binding
    can lift it into the driver's typed timeout policy. Same mechanism
    as create / delete / read prep."""
    prepared = build_upsert_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "x", "pk": "a"},
        partition_key_value="a",
        container_rid=None,
        kwargs={"timeout": 30},
    )
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 30


def test_compose_consumes_recognised_kwargs():
    """The recognised option-shortcut kwargs are popped out of the input
    dict so the caller doesn't double-forward them to the legacy path."""
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
# merge_upsert_item_explicit_kwargs -- the upsert kwarg set
# ---------------------------------------------------------------------------


def test_merge_omits_none_entries():
    """Only non-None explicit kwargs land in the merged dict -- None means
    'not supplied' and must not be stamped."""
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
    """Upsert is the one op that carries *both* the write-with-body
    ``no_response`` (kept, unlike delete / read) *and* the
    ``etag`` / ``match_condition`` precondition pair (kept, unlike
    create which drops them)."""
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
# populate_query_metrics deprecation (sync-only) -- legacy parity
# ---------------------------------------------------------------------------


def test_populate_query_metrics_warns_and_writes_for_any_explicit_value():
    """The legacy ``upsert_item`` warned (and wrote the option) for any
    explicit ``populate_query_metrics`` value, including ``False``. The
    migrated options build preserves that exact gate so nothing
    regresses for the deprecated flag."""
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

