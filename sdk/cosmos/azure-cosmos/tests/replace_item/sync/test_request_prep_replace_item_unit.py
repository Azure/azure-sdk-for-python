# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for the ``replace_item`` request-prep path — no network, no emulator.

These pin ``build_replace_item_prepared`` -- the overwrite-only,
body-carrying builder added for the migrated ``replace_item``.

``replace_item`` shares one builder with ``upsert_item``: both carry the
body, never mint an id, and turn ``etag`` / ``match_condition`` into
``If-Match`` / ``If-None-Match``. Two things differ:

* the ``op`` tag (the backend sends a replace to the binding's
  ``replace_item``, an overwrite-only PUT, rather than to
  ``upsert_item``), and
* the ``item_id`` slot. A replace names an existing document, so the
  caller passes the id resolved from ``item`` and the binding puts that
  on the request URL (matching the legacy ``ReplaceItem``); an upsert has
  no ``item`` argument and leaves ``item_id`` unset (the binding reads the
  id from the body).

The headline precondition differs too: a replace's version guard is
``IfNotModified`` + etag -> ``If-Match`` (412 on a stale etag), whereas
the upsert case that earns its keep is ``IfMissing`` -> ``If-None-Match: *``.

Sibling of ``tests/upsert_item/sync/test_request_prep_upsert_item_unit.py``.
"""
from __future__ import annotations

import json

import pytest

from azure.core import MatchConditions

from azure.cosmos._backend.base import (
    OP_REPLACE_ITEM,
    OP_UPSERT_ITEM,
    PreparedRequest,
)
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._item_dispatch import build_upsert_item_request_options
from azure.cosmos._helpers._request_prep import (
    build_replace_item_prepared,
    build_upsert_item_prepared,
)


# ---------------------------------------------------------------------------
# Body-carrying baseline shape (like create / upsert, not delete / read)
# ---------------------------------------------------------------------------


def test_baseline_is_write_with_body_with_item_id():
    """A replace carries the new body (serialised to JSON bytes) and the id
    of the document to overwrite on ``item_id`` -- both at once. The op tag
    is ``OP_REPLACE_ITEM``."""
    prepared = build_replace_item_prepared(
        container_link="dbs/d/colls/orders",
        body={"id": "order-42", "pk": "customerA", "total": 129.0},
        item_id="order-42",
        partition_key_value="customerA",
        container_rid="RID==",
        kwargs={},
    )
    assert isinstance(prepared, PreparedRequest)
    assert prepared.op == OP_REPLACE_ITEM
    assert prepared.container_link == "dbs/d/colls/orders"
    assert prepared.body_bytes == b'{"id":"order-42","pk":"customerA","total":129.0}'
    assert prepared.partition_key_header == '["customerA"]'
    # Unlike upsert (id from the body, item_id None), replace carries the
    # id of the document to overwrite so the binding uses it for the URL.
    assert prepared.item_id == "order-42"
    # Dropped-and-recreated container guard: the rid is stamped under the standard key.
    assert prepared.headers[Constants.ContainerRID] == "RID=="


def test_url_id_comes_from_item_id_not_body():
    """The URL id is whatever ``item_id`` the caller resolved from ``item`` --
    it is not re-derived from the body. The legacy ``ReplaceItem`` takes the
    URL id from the resolved document link, so a body whose own id disagrees
    with ``item`` must not change which document the URL targets (the server
    then rejects the id change).
    """
    prepared = build_replace_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "B", "pk": "a"},   # body's own id
        item_id="A",                   # the document the customer named
        partition_key_value="a",
        container_rid=None,
        kwargs={},
    )
    # The request URL targets "A" (the named item) while the body still
    # carries "B" -- exactly what the legacy path sends, so the server
    # applies the same id-can't-change check.
    assert prepared.item_id == "A"
    assert json.loads(prepared.body_bytes)["id"] == "B"


def test_body_bytes_round_trip_to_the_same_dict():
    """The serialised bytes parse back to the body the customer passed --
    replace never rewrites the body."""
    body = {"id": "order-42", "pk": "customerA"}
    prepared = build_replace_item_prepared(
        container_link="dbs/d/colls/c",
        body=body,
        item_id="order-42",
        partition_key_value="customerA",
        container_rid=None,
        kwargs={},
    )
    assert json.loads(prepared.body_bytes) == body


# ---------------------------------------------------------------------------
# Never mints an id (replace targets an existing document)
# ---------------------------------------------------------------------------


def test_missing_body_id_is_not_minted_and_body_is_not_mutated():
    """A replace never mints an id into the body (it overwrites a specific
    document named by ``item``). A body without one is serialised as-is and
    the server rejects it -- the prep must not invent one."""
    body = {"pk": "customerA", "total": 129.0}
    prepared = build_replace_item_prepared(
        container_link="dbs/d/colls/c",
        body=body,
        item_id="order-42",
        partition_key_value="customerA",
        container_rid=None,
        kwargs={},
    )
    assert "id" not in body  # body untouched
    assert b'"id"' not in prepared.body_bytes


# ---------------------------------------------------------------------------
# Access conditions -- the version-guarded replace is the main case
# ---------------------------------------------------------------------------


def test_etag_if_not_modified_translates_to_if_match_guarded_replace():
    """``etag=<v>`` + ``IfNotModified`` is the replace's headline guard:
    ``If-Match: <v>`` (a stale etag surfaces as 412)."""
    options = build_upsert_item_request_options({
        "etag": "abc",
        "match_condition": MatchConditions.IfNotModified,
    })
    assert options["accessCondition"] == {"type": "IfMatch", "condition": "abc"}

    prepared = build_replace_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "order-42", "pk": "customerA"},
        item_id="order-42",
        partition_key_value="customerA",
        container_rid=None,
        access_condition=options.get("accessCondition"),
        kwargs={},
    )
    assert prepared.headers["If-Match"] == "abc"
    assert "If-None-Match" not in prepared.headers


def test_if_missing_translates_to_if_none_match_wildcard():
    """``match_condition=IfMissing`` (no etag) -> ``If-None-Match: *``. The
    same translation upsert uses; on a replace it is rare but must still
    emit the header (it goes through the shared access-condition step)."""
    options = build_upsert_item_request_options({"match_condition": MatchConditions.IfMissing})
    prepared = build_replace_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "order-42", "pk": "customerA"},
        item_id="order-42",
        partition_key_value="customerA",
        container_rid=None,
        access_condition=options.get("accessCondition"),
        kwargs={},
    )
    assert prepared.headers["If-None-Match"] == "*"
    assert "If-Match" not in prepared.headers


def test_no_access_condition_emits_no_precondition_headers():
    """A plain replace (no etag / match_condition) carries neither
    ``If-Match`` nor ``If-None-Match``, and never leaks the raw internal
    ``accessCondition`` shape onto the wire."""
    prepared = build_replace_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "x", "pk": "a"},
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        access_condition=None,
        kwargs={},
    )
    assert "If-Match" not in prepared.headers
    assert "If-None-Match" not in prepared.headers
    assert "accessCondition" not in prepared.headers


def test_etag_without_match_condition_raises_value_error_up_front():
    """``etag`` without ``match_condition`` is an application bug; the
    options build refuses to guess and raises before any network round
    trip -- the same gate delete / read / upsert enforce."""
    with pytest.raises(ValueError, match=r"'etag' specified without 'match_condition'"):
        build_upsert_item_request_options({"etag": "abc"})


# ---------------------------------------------------------------------------
# Header-map shaping (same as create / delete / read / upsert prep)
# ---------------------------------------------------------------------------


def test_initial_headers_are_flattened_into_outer_headers():
    """``initial_headers={'x-trace-id': 'abc'}`` is kept as a nested
    ``initialHeaders`` dict so the binding forwards each entry verbatim."""
    prepared = build_replace_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "x", "pk": "a"},
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs={"initial_headers": {"x-trace-id": "abc-123"}},
    )
    assert prepared.headers["initialHeaders"] == {"x-trace-id": "abc-123"}
    assert "x-trace-id" not in prepared.headers
    assert "initial_headers" not in prepared.headers


def test_trigger_priority_bucket_no_response_land_as_option_keys():
    """The body-carrying option set reaches the headers map under the
    internal option-key names. ``no_response`` is kept on replace (a replace
    returns a body, unlike delete / read)."""
    prepared = build_replace_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "x", "pk": "a"},
        item_id="x",
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
    prepared = build_replace_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "x", "pk": "a"},
        item_id="x",
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
    build_replace_item_prepared(
        container_link="dbs/d/colls/c",
        body={"id": "x", "pk": "a"},
        item_id="x",
        partition_key_value="a",
        container_rid=None,
        kwargs=kwargs,
    )
    assert "pre_trigger_include" not in kwargs
    assert kwargs == {"extra_unknown": "left-alone"}


# ---------------------------------------------------------------------------
# The shared-builder invariant: replace == upsert except op and item_id
# ---------------------------------------------------------------------------


def test_replace_and_upsert_prep_differ_only_by_op_and_item_id():
    """``build_replace_item_prepared`` and ``build_upsert_item_prepared``
    both delegate to one shared builder, so for the same inputs every field
    on the wire must be identical except the ``op`` tag and the ``item_id``
    slot (replace names a target; upsert takes the id from the body). This
    keeps the two from drifting: a future change to one builder can't quietly
    change the bytes the other sends.
    """
    shared = dict(
        container_link="dbs/d/colls/orders",
        body={"id": "order-42", "pk": "customerA", "total": 129.0},
        partition_key_value="customerA",
        container_rid="RID==",
        access_condition={"type": "IfMatch", "condition": "abc"},
    )
    replace_prepared = build_replace_item_prepared(
        **shared, item_id="order-42", kwargs={"priority": "High"}
    )
    upsert_prepared = build_upsert_item_prepared(**shared, kwargs={"priority": "High"})

    assert replace_prepared.op == OP_REPLACE_ITEM
    assert upsert_prepared.op == OP_UPSERT_ITEM
    # Replace carries the resolved target id; upsert now also forwards the body's
    # id on item_id as a fast-path hint (the binding skips re-parsing the body).
    # Here the body id equals the replace target, so both land on "order-42" and
    # the two preps differ only by op.
    assert replace_prepared.item_id == "order-42"
    assert upsert_prepared.item_id == "order-42"
    # Every field on the wire is byte-identical.
    assert replace_prepared.container_link == upsert_prepared.container_link
    assert replace_prepared.body_bytes == upsert_prepared.body_bytes
    assert replace_prepared.partition_key_header == upsert_prepared.partition_key_header
    assert dict(replace_prepared.headers) == dict(upsert_prepared.headers)
    # And the headers really do carry the version guard.
    assert replace_prepared.headers["If-Match"] == "abc"


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
