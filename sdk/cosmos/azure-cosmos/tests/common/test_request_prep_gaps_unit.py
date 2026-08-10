# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for two request-path behaviours -- no network, no emulator.

These pin the binding-layer fixes for two behaviours:

* **Client-level ``no_response_on_write`` fallback.** A client built with
  ``no_response_on_write=True`` (stored as
  ``connection_policy.ResponsePayloadOnWriteDisabled``) must suppress the
  write response body even when the call passes no per-call ``no_response``.
  The write preps take a ``no_response_on_write_default`` and fall back to it.
  A per-call value always wins.

* **Per-request consistency override.** A ``consistencyLevel`` passed through
  ``request_options`` is translated to the ``x-ms-consistency-level`` header,
  instead of being sent as a raw ``consistencyLevel`` header the driver
  ignores.
"""
from __future__ import annotations

from azure.cosmos.http_constants import HttpHeaders
from azure.cosmos._helpers._request_headers import apply_no_response_on_write_default, flatten_options_to_headers
from azure.cosmos._helpers._request_item import (
    build_create_item_prepared,
    build_patch_item_prepared,
    build_replace_item_prepared,
    build_upsert_item_prepared,
)

# The internal option-key the binding lifts into ContentResponseOnWrite.
_NO_RESPONSE_KEY = "responsePayloadOnWriteDisabled"


# ---------------------------------------------------------------------------
# consistencyLevel -> x-ms-consistency-level
# ---------------------------------------------------------------------------


def test_consistency_level_becomes_wire_header():
    """A truthy ``consistencyLevel`` option emits ``x-ms-consistency-level`` and
    drops the raw option-key (which the driver would not recognise)."""
    headers = flatten_options_to_headers({"consistencyLevel": "Eventual"})
    assert headers[HttpHeaders.ConsistencyLevel] == "Eventual"
    assert "consistencyLevel" not in headers


def test_consistency_level_falsy_emits_no_header():
    """An empty / falsy override ships no header, matching the legacy truthy gate."""
    assert HttpHeaders.ConsistencyLevel not in flatten_options_to_headers({"consistencyLevel": ""})
    assert HttpHeaders.ConsistencyLevel not in flatten_options_to_headers({"consistencyLevel": None})


def test_consistency_level_reaches_wire_through_request_options_on_create():
    """The override the customer hand-builds in ``request_options`` survives the
    full create prep as the proper wire header."""
    prepared, _ = build_create_item_prepared(
        container_link="dbs/d/colls/orders",
        body={"id": "order-1", "pk": "a"},
        partition_key_value="a",
        container_rid="RID==",
        kwargs={"request_options": {"consistencyLevel": "Eventual"}},
    )
    assert prepared.headers[HttpHeaders.ConsistencyLevel] == "Eventual"
    assert "consistencyLevel" not in prepared.headers


# ---------------------------------------------------------------------------
# pipeline-internal option-keys must never become wire headers
# ---------------------------------------------------------------------------


def test_internal_option_keys_are_not_emitted_as_headers():
    """Keys that ride in the options dict for the legacy pipeline's own use are
    not wire headers and must be dropped, while real customer options survive.

    This is the ``read_items`` shape: its single-item legs route through the
    point-read prep with the batch's query / ``build_options`` options dict,
    which carries pipeline-internal keys (``operationStartTime``,
    ``timeoutScope``, ``timeout``, ``read_timeout``, ``retry_write``).
    The Rust prep's catch-all would otherwise copy them through as bogus headers
    (silently dropped by the binding in production, a hard error under
    ``COSMOS_WIRE_STRICT``).

    ``enableCrossPartitionQuery`` is deliberately not on that list: legacy
    ``_base.GetHeaders`` emits it as
    ``x-ms-documentdb-query-enablecrosspartition``, so the Rust path must too.

    What this looked like to a customer: ``create_item(order, retry_write=3)``
    put ``retry_write`` on the request as if it were a header. ``retry_write``
    is a retry setting the SDK reads itself; it was never meant to leave the
    process."""
    options = {
        "operationStartTime": 1784323061.0,
        "timeoutScope": "operation",
        "timeout": 5,
        "read_timeout": 3,
        "retry_write": 3,
        # Real customer options that must still reach the wire.
        "enableCrossPartitionQuery": True,
        "sessionToken": "0:-1#5",
        "priorityLevel": "High",
        "consistencyLevel": "Session",
    }
    headers = flatten_options_to_headers(options)
    for internal_key in (
        "operationStartTime",
        "timeoutScope",
        "timeout",
        "read_timeout",
        "retry_write",
    ):
        assert internal_key not in headers
    assert headers["enableCrossPartitionQuery"] is True
    assert headers["sessionToken"] == "0:-1#5"
    assert headers["priorityLevel"] == "High"
    assert headers[HttpHeaders.ConsistencyLevel] == "Session"


def test_container_rid_is_truthy_gated():
    """An empty container rid sends no header.

    Legacy ``_base.GetHeaders`` gates it with ``options.get(containerRID)``, so a
    ``""`` / ``None`` rid never becomes
    ``x-ms-cosmos-intended-collection-rid: ""`` on the wire.

    This header names the container a request is meant for. A database read has
    no container, so it must not send one -- an empty value is not the same as
    no value.
    """
    assert "containerRID" not in flatten_options_to_headers({"containerRID": ""})
    assert "containerRID" not in flatten_options_to_headers({"containerRID": None})
    assert flatten_options_to_headers({"containerRID": "rid1"})["containerRID"] == "rid1"


# ---------------------------------------------------------------------------
# apply_no_response_on_write_default helper
# ---------------------------------------------------------------------------


def test_default_fallback_sets_option_when_absent():
    """With no per-call value, a truthy client default suppresses the response body."""
    options = {}
    apply_no_response_on_write_default(options, True)
    assert options[_NO_RESPONSE_KEY] is True


def test_default_false_leaves_options_untouched():
    """A falsy client default (the common case) adds nothing."""
    options = {}
    apply_no_response_on_write_default(options, False)
    assert _NO_RESPONSE_KEY not in options


def test_percall_value_wins_over_default():
    """An explicit per-call value is never overwritten by the client default --
    including an explicit ``False`` that asks for the body back."""
    options_false = {_NO_RESPONSE_KEY: False}
    apply_no_response_on_write_default(options_false, True)
    assert options_false[_NO_RESPONSE_KEY] is False

    options_true = {_NO_RESPONSE_KEY: True}
    apply_no_response_on_write_default(options_true, False)
    assert options_true[_NO_RESPONSE_KEY] is True


# ---------------------------------------------------------------------------
# The fallback threaded through every write builder
# ---------------------------------------------------------------------------


def _create_headers(*, default, kwargs):
    """Return headers prepared for an item create request."""
    prepared, _ = build_create_item_prepared(
        container_link="dbs/d/colls/orders",
        body={"id": "o", "pk": "a"},
        partition_key_value="a",
        container_rid="RID==",
        no_response_on_write_default=default,
        kwargs=kwargs,
    )
    return prepared.headers


def _upsert_headers(*, default, kwargs):
    """Return headers prepared for an item upsert request."""
    return build_upsert_item_prepared(
        container_link="dbs/d/colls/orders",
        body={"id": "o", "pk": "a"},
        partition_key_value="a",
        container_rid="RID==",
        no_response_on_write_default=default,
        kwargs=kwargs,
    ).headers


def _replace_headers(*, default, kwargs):
    """Return headers prepared for an item replace request."""
    return build_replace_item_prepared(
        container_link="dbs/d/colls/orders",
        body={"id": "o", "pk": "a"},
        item_id="o",
        partition_key_value="a",
        container_rid="RID==",
        no_response_on_write_default=default,
        kwargs=kwargs,
    ).headers


def _patch_headers(*, default, kwargs):
    """Return headers prepared for an item patch request."""
    return build_patch_item_prepared(
        container_link="dbs/d/colls/orders",
        item_id="o",
        patch_operations=[{"op": "set", "path": "/total", "value": 1}],
        partition_key_value="a",
        container_rid="RID==",
        no_response_on_write_default=default,
        kwargs=kwargs,
    ).headers


_BUILDERS = (_create_headers, _upsert_headers, _replace_headers, _patch_headers)


def test_client_default_suppresses_echo_on_every_write_builder():
    """Each write builder honours a truthy client default when the call passes
    no per-call ``no_response``."""
    for make_headers in _BUILDERS:
        headers = make_headers(default=True, kwargs={})
        assert headers.get(_NO_RESPONSE_KEY) is True, make_headers.__name__


def test_no_default_emits_no_suppression_header_on_every_write_builder():
    """With the default off and no per-call value, no suppression header is
    added -- the driver returns the body by default."""
    for make_headers in _BUILDERS:
        headers = make_headers(default=False, kwargs={})
        assert _NO_RESPONSE_KEY not in headers, make_headers.__name__


def test_percall_no_response_false_beats_client_default_on_every_write_builder():
    """An explicit per-call ``no_response=False`` still gets the body back even
    when the client default is on."""
    for make_headers in _BUILDERS:
        headers = make_headers(default=True, kwargs={"no_response": False})
        assert headers.get(_NO_RESPONSE_KEY) is False, make_headers.__name__
