# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Backend-agnostic unit tests for the read_items query-leg routing marker.

No emulator and no Rust binding needed -- these exercise the pure gate
``can_use_rust_backend_for_query_page`` directly, in milliseconds.

read_items keeps its client-side orchestration in Python and routes each leaf
read to the Rust backend: a single-item chunk becomes a point read (Rust), and a
multi-item chunk becomes one per-partition ``id IN (...)`` query. That query
shape currently panics the Rust query path, so read_items marks those queries
with ``Constants.ReadItemsQueryLeg`` and the gate keeps them on legacy. These
tests pin that marker branch -- the one line that stops the panic -- so a
regression is caught here instead of in a slow live run (or in production as a
process-killing panic). The gate is shared by the sync and async client
connections, so this covers both paths.
"""
from __future__ import annotations

from azure.cosmos import http_constants
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._query_rust_routing import can_use_rust_backend_for_query_page


# A representative read_items multi-item chunk query: a cross-partition
# ``id IN (...)`` with none of the shapes the Rust cross-partition path rejects.
_ID_IN_QUERY = {"query": "SELECT * FROM c WHERE c.id IN (@id0, @id1)"}


def _gate(options):
    """Run the gate for the read_items query shape with the given options."""
    return can_use_rust_backend_for_query_page(
        backend=object(),
        query_payload=_ID_IN_QUERY,
        options=options,
        kwargs={},
        container_properties=None,
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )


def test_query_leg_marker_forces_legacy():
    """With the marker set, the gate must say no so the query stays on legacy and
    never reaches the panicking Rust query path."""
    assert _gate({Constants.ReadItemsQueryLeg: True}) is False


def test_same_query_without_marker_is_eligible_for_rust():
    """Control: the identical query without the marker is otherwise eligible for
    Rust, proving the marker -- not some other gate -- is what forces legacy."""
    assert _gate({}) is True


def test_marker_uses_the_shared_constant_value():
    """Guard against the producers (read_items helpers) and this consumer drifting
    on the raw key: the constant is the single source of truth."""
    assert Constants.ReadItemsQueryLeg == "_read_items_query_leg"
    assert _gate({"_read_items_query_leg": True}) is False
