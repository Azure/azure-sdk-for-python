# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Pure-Python unit tests for ``build_read_item_prepared``.

No network, no Cosmos emulator, no Rust binding required. Pins the
wire-prep behaviour for ``read_item`` end to end:

* ``max_integrated_cache_staleness_in_ms=N`` (positive) translates to
  the header ``x-ms-dedicatedgateway-max-age: N``. ``0`` is a silent
  no-op -- no header on the wire -- because the legacy gate drops
  falsy values.
* ``etag`` plus ``MatchConditions.IfModified`` translates to
  ``If-None-Match: <etag>``; ``IfNotModified`` translates to
  ``If-Match: <etag>``.
* ``etag`` without ``match_condition`` raises ``ValueError`` before
  any network round trip.

Sibling of ``tests/create_item/sync/test_request_prep_unit.py``.
"""
from __future__ import annotations

import pytest

from azure.core import MatchConditions

from azure.cosmos._backend.base import OP_READ_ITEM, PreparedRequest
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._item_dispatch import (
    build_read_item_request_options,
    merge_read_item_explicit_kwargs,
)
from azure.cosmos._helpers._request_prep import build_read_item_prepared


# ---------------------------------------------------------------------------
# Baseline shape
# ---------------------------------------------------------------------------


def test_baseline_returns_read_item_prepared_with_no_body():
    """L0 baseline: container-link, partition-key wire-shape, item-id slot."""
    prepared = build_read_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="order-42",
        partition_key_value="customerA",
        container_rid="RID==",
        kwargs={},
    )
    assert isinstance(prepared, PreparedRequest)
    assert prepared.op == OP_READ_ITEM
    assert prepared.container_link == "dbs/d/colls/c"
    assert prepared.body_bytes == b""  # GET is bodiless
    assert prepared.partition_key_header == '["customerA"]'
    assert prepared.item_id == "order-42"


def test_baseline_stamps_container_rid_into_headers():
    """``container_rid`` reaches the wire under the canonical key so the binding
    forwards ``x-ms-cosmos-intended-collection-rid`` — the same
    drop-and-recreate guard ``create_item`` / ``delete_item`` get."""
    prepared = build_read_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid="RID==",
        kwargs={},
    )
    assert prepared.headers[Constants.ContainerRID] == "RID=="


# ---------------------------------------------------------------------------
# max_integrated_cache_staleness_in_ms → x-ms-dedicatedgateway-max-age
# ---------------------------------------------------------------------------


def test_cache_staleness_positive_emits_dedicated_gateway_header():
    """``max_integrated_cache_staleness_in_ms=5000`` →
    ``x-ms-dedicatedgateway-max-age: 5000``."""
    prepared = build_read_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"max_integrated_cache_staleness_in_ms": 5000},
    )
    assert prepared.headers["x-ms-dedicatedgateway-max-age"] == "5000"
    # Must NOT also stamp the option-key form -- the prep translates,
    # not aliases.
    assert "maxIntegratedCacheStaleness" not in prepared.headers


def test_cache_staleness_zero_is_silent_no_op():
    """``max_integrated_cache_staleness_in_ms=0`` must emit no header.

    ``0`` is a silent no-op on the wire. The legacy gate drops the
    value because ``0`` is falsy; the Rust prep must match. A
    regression here would silently change behaviour for customers
    that pass ``0`` (a common "I don't want a stale cache for this
    call" idiom).
    """
    prepared = build_read_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"max_integrated_cache_staleness_in_ms": 0},
    )
    assert "x-ms-dedicatedgateway-max-age" not in prepared.headers
    assert "maxIntegratedCacheStaleness" not in prepared.headers


# ---------------------------------------------------------------------------
# Access-condition translation for the read side ("Conditional read on
# read_item"): ``etag`` + ``IfModified`` becomes ``If-None-Match``;
# ``etag`` + ``IfNotModified`` becomes ``If-Match``.
# ---------------------------------------------------------------------------


def test_etag_if_modified_translates_to_if_none_match():
    """``etag=<v>`` + ``IfModified`` (cache-validation idiom) →
    ``If-None-Match: <v>``."""
    options = build_read_item_request_options({
        "request_options": {"partitionKey": "a"},
        "etag": "abc",
        "match_condition": MatchConditions.IfModified,
    })
    # ``build_options`` consumed the etag+match_condition pair into
    # the ``accessCondition`` shape ``{type: IfNoneMatch, condition: abc}``.
    assert options["accessCondition"] == {"type": "IfNoneMatch", "condition": "abc"}

    prepared = build_read_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value=options["partitionKey"],
        container_rid=None,
        # The prep reads ``accessCondition`` out of the seed and emits
        # the wire header; the caller passes the same options dict in
        # as the ``request_options`` seed.
        kwargs={"request_options": options},
    )
    assert prepared.headers["If-None-Match"] == "abc"
    assert "If-Match" not in prepared.headers


def test_etag_if_not_modified_translates_to_if_match():
    """``etag=<v>`` + ``IfNotModified`` (rare write-precondition-on-read
    idiom) → ``If-Match: <v>``."""
    options = build_read_item_request_options({
        "request_options": {"partitionKey": "a"},
        "etag": "abc",
        "match_condition": MatchConditions.IfNotModified,
    })
    assert options["accessCondition"] == {"type": "IfMatch", "condition": "abc"}
    prepared = build_read_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value=options["partitionKey"],
        container_rid=None,
        kwargs={"request_options": options},
    )
    assert prepared.headers["If-Match"] == "abc"
    assert "If-None-Match" not in prepared.headers


def test_etag_without_match_condition_raises_value_error_up_front():
    """``etag`` without ``match_condition`` is an application bug and
    the SDK refuses to guess. The error must fire before any network
    round trip so the customer's traceback points at the call site.
    """
    with pytest.raises(ValueError, match=r"'etag' specified without 'match_condition'"):
        build_read_item_request_options({"etag": "abc"})


# ---------------------------------------------------------------------------
# initialHeaders flattening (parity with create / delete prep)
# ---------------------------------------------------------------------------


def test_initial_headers_are_flattened_into_outer_headers():
    """Customer ``initial_headers={'x-trace-id': 'abc'}`` must surface as a
    bare ``x-trace-id`` entry in ``PreparedRequest.headers`` so the
    binding's per-header pass-through forwards it verbatim — same shape
    as create / delete prep."""
    prepared = build_read_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"initial_headers": {"x-trace-id": "abc-123"}},
    )
    assert prepared.headers["x-trace-id"] == "abc-123"
    # The grouping key itself must NOT survive as a header (it's the
    # snake_case kwarg name, not a wire-header name).
    assert "initial_headers" not in prepared.headers
    assert "initialHeaders" not in prepared.headers


# ---------------------------------------------------------------------------
# Trigger headers / priority / throughput bucket (one row each)
# ---------------------------------------------------------------------------


def test_post_trigger_include_lands_as_option_key():
    """``post_trigger_include='auditRead'`` → ``postTriggerInclude`` option-key
    in the headers map (the binding then translates to
    ``x-ms-documentdb-post-trigger-include``)."""
    prepared = build_read_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"post_trigger_include": "auditRead"},
    )
    assert prepared.headers["postTriggerInclude"] == "auditRead"


def test_priority_high_lands_as_option_key():
    prepared = build_read_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"priority": "High"},
    )
    assert prepared.headers["priorityLevel"] == "High"


def test_throughput_bucket_lands_as_option_key():
    prepared = build_read_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"throughput_bucket": 1},
    )
    assert prepared.headers["throughputBucket"] == 1


# ---------------------------------------------------------------------------
# Timeout sentinel header (parity with create / delete prep)
# ---------------------------------------------------------------------------


def test_timeout_kwarg_is_forwarded_under_sentinel_header():
    """``timeout=30`` → ``__overall_timeout_seconds: 30`` so the binding can
    lift it into the driver's typed ``EndToEndOperationLatencyPolicy``."""
    prepared = build_read_item_prepared(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"timeout": 30},
    )
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 30


# ---------------------------------------------------------------------------
# merge_read_item_explicit_kwargs — kwarg dict assembly
# ---------------------------------------------------------------------------


def test_merge_read_item_explicit_kwargs_omits_none_entries():
    """Only non-None explicit kwargs land in the merged dict — None means
    'not supplied' and must not be stamped (otherwise the legacy
    ``build_options`` would write ``priorityLevel: None`` etc.)."""
    kwargs: dict = {}
    merge_read_item_explicit_kwargs(
        kwargs,
        post_trigger_include=None,
        session_token="0:1#42",
        initial_headers=None,
        etag=None,
        match_condition=None,
        max_integrated_cache_staleness_in_ms=None,
        priority=None,
        throughput_bucket=None,
        availability_strategy=None,
        response_hook=None,
    )
    assert kwargs == {"session_token": "0:1#42"}


def test_merge_read_item_explicit_kwargs_includes_cache_staleness_when_positive():
    kwargs: dict = {}
    merge_read_item_explicit_kwargs(
        kwargs,
        max_integrated_cache_staleness_in_ms=5000,
    )
    assert kwargs == {"max_integrated_cache_staleness_in_ms": 5000}


def test_merge_read_item_explicit_kwargs_does_not_expose_retry_write_or_no_response():
    """Reads have no body to suppress (``no_response`` is meaningless) and
    are idempotent (``retry_write`` is meaningless). The merge helper
    must not even accept those parameter names."""
    kwargs: dict = {}
    with pytest.raises(TypeError):
        # ``retry_write`` is not a parameter on this merge function.
        merge_read_item_explicit_kwargs(kwargs, retry_write=1)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        merge_read_item_explicit_kwargs(kwargs, no_response=True)  # type: ignore[call-arg]

