# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for ``prepare_read_item_request`` -- no network, no emulator.

These pin how a ``read_item`` call is turned into a request, end to end:

* A positive ``max_integrated_cache_staleness_in_ms=N`` becomes the
  header ``x-ms-dedicatedgateway-max-age: N``. ``0`` sends no header at
  all, because a falsy value is dropped (the same rule the legacy path
  used).
* ``etag`` with ``MatchConditions.IfModified`` becomes
  ``If-None-Match: <etag>``; ``IfNotModified`` becomes ``If-Match: <etag>``.
* ``etag`` without ``match_condition`` raises ``ValueError`` before any
  network round trip.

Sibling of ``tests/create_item/sync/test_request_prep_unit.py``.
"""
from __future__ import annotations
from common.typed_requests import legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings

import pytest

from azure.core import MatchConditions

from azure.cosmos._backend.operations import OP_READ_ITEM
from azure.cosmos._backend.contracts import PreparedRequest
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._item_dispatch import (
    build_read_item_request_options,
    merge_read_item_explicit_kwargs,
)
from common.request_preparation import (
    prepare_read_item_request,
)


# ---------------------------------------------------------------------------
# Baseline shape
# ---------------------------------------------------------------------------


def test_baseline_returns_read_item_prepared_with_no_body():
    """Baseline: the container link, the partition-key shape, and the
    item-id slot are all set, and a read carries no body."""
    prepared = prepare_read_item_request(
        container_link="dbs/d/colls/c",
        item_id="order-42",
        partition_key_value="customerA",
        container_rid="RID==",
        kwargs={},
    )
    assert isinstance(prepared, PreparedRequest)
    assert prepared.op == OP_READ_ITEM
    assert prepared.container_link == "dbs/d/colls/c"
    assert prepared.body_bytes == b""  # a read sends no body
    assert legacy_partition_key_from_request(prepared) == '["customerA"]'
    assert prepared.item_id == "order-42"


def test_baseline_stamps_container_rid_into_headers():
    """The container rid is set under the key the binding turns into
    ``x-ms-cosmos-intended-collection-rid``. This is the same guard against a
    dropped-and-recreated container that ``create_item`` and ``delete_item``
    get: if someone deletes the container and makes a new one with the same
    name, the rid no longer matches and the service rejects the read instead
    of silently answering from the replacement container."""
    prepared = prepare_read_item_request(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid="RID==",
        kwargs={},
    )
    assert wire_headers(prepared)["x-ms-cosmos-intended-collection-rid"] == "RID=="


# ---------------------------------------------------------------------------
# max_integrated_cache_staleness_in_ms -> x-ms-dedicatedgateway-max-age
# ---------------------------------------------------------------------------


def test_cache_staleness_positive_emits_dedicated_gateway_header():
    """``max_integrated_cache_staleness_in_ms=5000`` becomes
    ``x-ms-dedicatedgateway-max-age: 5000``.

    This is how a customer says "an answer up to 5 seconds old is fine",
    which lets the dedicated gateway serve the read from its cache."""
    prepared = prepare_read_item_request(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"max_integrated_cache_staleness_in_ms": 5000},
    )
    assert wire_headers(prepared)["x-ms-dedicatedgateway-max-age"] == "5000"
    # It must not also set the option-key form -- the prep translates
    # the value, it doesn't just copy it under a new name.
    assert "maxIntegratedCacheStaleness" not in wire_headers(prepared)


def test_cache_staleness_zero_is_silent_no_op():
    """``max_integrated_cache_staleness_in_ms=0`` must emit no header.

    ``0`` sends nothing on the wire. A falsy value is dropped, and the
    read prep has to match. If this regressed, behaviour would quietly
    change for customers who pass ``0`` (a common way of saying "don't
    serve this call from a stale cache").
    """
    prepared = prepare_read_item_request(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"max_integrated_cache_staleness_in_ms": 0},
    )
    assert "x-ms-dedicatedgateway-max-age" not in wire_headers(prepared)
    assert "maxIntegratedCacheStaleness" not in wire_headers(prepared)


# ---------------------------------------------------------------------------
# Access conditions on a read: ``etag`` + ``IfModified`` becomes
# ``If-None-Match``; ``etag`` + ``IfNotModified`` becomes ``If-Match``.
# ---------------------------------------------------------------------------


def test_etag_if_modified_translates_to_if_none_match():
    """``etag=<v>`` + ``IfModified`` (the cache-validation case) becomes
    ``If-None-Match: <v>``."""
    options = build_read_item_request_options({
        "request_options": {"partitionKey": "a"},
        "etag": "abc",
        "match_condition": MatchConditions.IfModified,
    })
    # The options build folded the etag + match_condition pair into the
    # ``accessCondition`` shape ``{type: IfNoneMatch, condition: abc}``.
    assert options["accessCondition"] == {"type": "IfNoneMatch", "condition": "abc"}

    prepared = prepare_read_item_request(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value=options["partitionKey"],
        container_rid=None,
        # The prep reads ``accessCondition`` out of the seed and emits the
        # wire header; the caller passes that same options dict back in as
        # the ``request_options`` seed.
        kwargs={"request_options": options},
    )
    assert wire_headers(prepared)["if-none-match"] == "abc"
    assert "if-match" not in wire_headers(prepared)


def test_etag_if_not_modified_translates_to_if_match():
    """``etag=<v>`` + ``IfNotModified`` (a rare precondition on a read)
    becomes ``If-Match: <v>``."""
    options = build_read_item_request_options({
        "request_options": {"partitionKey": "a"},
        "etag": "abc",
        "match_condition": MatchConditions.IfNotModified,
    })
    assert options["accessCondition"] == {"type": "IfMatch", "condition": "abc"}
    prepared = prepare_read_item_request(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value=options["partitionKey"],
        container_rid=None,
        kwargs={"request_options": options},
    )
    assert wire_headers(prepared)["if-match"] == "abc"
    assert "if-none-match" not in wire_headers(prepared)


def test_etag_without_match_condition_raises_value_error_up_front():
    """``etag`` without ``match_condition`` is an application bug, and the
    SDK refuses to guess which one was meant. The error fires before any
    network round trip, so the customer's traceback points at their own
    call site.
    """
    with pytest.raises(ValueError, match=r"'etag' specified without 'match_condition'"):
        build_read_item_request_options({"etag": "abc"})


# ---------------------------------------------------------------------------
# initial_headers flattening (same as create / delete prep)
# ---------------------------------------------------------------------------


def test_initial_headers_are_flattened_into_outer_headers():
    """A customer's ``initial_headers={'x-trace-id': 'abc'}`` is kept as a nested
    ``initialHeaders`` dict in ``PreparedRequest.headers`` so the binding forwards
    each entry verbatim -- including non-``x-ms-`` names it would otherwise drop."""
    prepared = prepare_read_item_request(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"initial_headers": {"x-trace-id": "abc-123"}},
    )
    assert all(wire_headers(prepared).get(key.lower()) == str(value) for key, value in ({"x-trace-id": "abc-123"}).items())
    # The customer header is not flattened to the top level, and the snake_case
    # keyword-argument name never survives as a header.
    assert wire_headers(prepared)["x-trace-id"] == "abc-123"
    assert "initial_headers" not in wire_headers(prepared)


# ---------------------------------------------------------------------------
# Trigger headers / priority / throughput bucket (one each)
# ---------------------------------------------------------------------------


def test_post_trigger_include_lands_as_option_key():
    """``post_trigger_include='auditRead'`` lands as the ``postTriggerInclude``
    option key in the headers map (the binding then turns it into
    ``x-ms-documentdb-post-trigger-include``)."""
    prepared = prepare_read_item_request(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"post_trigger_include": "auditRead"},
    )
    assert wire_headers(prepared)["x-ms-documentdb-post-trigger-include"] == "auditRead"


def test_priority_high_lands_as_option_key():
    """``priority="High"`` is set as the ``priorityLevel`` request header the
    driver reads.

    Priority tells the service which requests to shed first when the account
    is over its throughput limit, so customers mark background work low and
    customer-facing work high."""
    prepared = prepare_read_item_request(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"priority": "High"},
    )
    assert wire_headers(prepared)["x-ms-cosmos-priority-level"] == "High"


def test_throughput_bucket_lands_as_option_key():
    """``throughput_bucket=1`` is set as the ``throughputBucket`` request header.

    Buckets let a customer cap how much of a container's throughput one class
    of traffic may consume, so a batch job cannot starve live traffic."""
    prepared = prepare_read_item_request(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"throughput_bucket": 1},
    )
    assert wire_headers(prepared)["x-ms-cosmos-throughput-bucket"] == '1'


# ---------------------------------------------------------------------------
# Timeout sentinel header (same as create / delete prep)
# ---------------------------------------------------------------------------


def test_timeout_kwarg_is_forwarded_under_sentinel_header():
    """``timeout=30`` is forwarded as ``__overall_timeout_seconds: 30``, an
    internal marker header that never reaches the wire: the binding reads it
    out and turns it into the driver's own timeout setting."""
    prepared = prepare_read_item_request(
        container_link="dbs/d/colls/c",
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"timeout": 30},
    )
    assert settings_options(prepared)["timeout_seconds"] == 30


# ---------------------------------------------------------------------------
# merge_read_item_explicit_kwargs -- building the kwargs dict
# ---------------------------------------------------------------------------


def test_merge_read_item_explicit_kwargs_omits_none_entries():
    """Only the explicit keyword arguments that aren't None land in the
    merged dict. None means "not supplied" and must not be set, otherwise
    the options build would write ``priorityLevel: None`` and so on, and the
    customer would get a header they never asked for."""
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
    """A positive ``max_integrated_cache_staleness_in_ms`` is kept in the merged
    kwargs (it is a real supplied value, unlike ``None``)."""
    kwargs: dict = {}
    merge_read_item_explicit_kwargs(
        kwargs,
        max_integrated_cache_staleness_in_ms=5000,
    )
    assert kwargs == {"max_integrated_cache_staleness_in_ms": 5000}


def test_merge_read_item_explicit_kwargs_does_not_expose_retry_write_or_no_response():
    """A read has no response body to suppress (so ``no_response`` is
    meaningless) and is already idempotent (so ``retry_write`` is
    meaningless). The merge helper must not even accept those parameter
    names."""
    kwargs: dict = {}
    with pytest.raises(TypeError):
        # ``retry_write`` is not a parameter on this merge function.
        merge_read_item_explicit_kwargs(kwargs, retry_write=1)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        merge_read_item_explicit_kwargs(kwargs, no_response=True)  # type: ignore[call-arg]
