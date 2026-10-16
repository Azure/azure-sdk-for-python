# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Backend-agnostic unit tests for the read_items query-leg routing marker.

No emulator and no Rust binding needed -- these exercise the pure gate
``can_use_rust_backend_for_query_page`` directly, in milliseconds.

read_items keeps its orchestration in Python. Singleton chunks can use Rust
point reads; multi-item chunks deliberately retain legacy queries using
``Constants.ReadItemsQueryLeg``. These tests pin that strategy boundary, shared
by both connections. Earlier topology-panic reports are historical, not a
current reproduction established by this unit test.
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
        query_payload=_ID_IN_QUERY,
        options=options,
        kwargs={},
        container_properties=None,
        is_query_plan=False,
        resource_type=http_constants.ResourceType.Document,
    )


def test_query_leg_marker_forces_legacy():
    """The marker keeps internal query chunks on the selected legacy strategy."""
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
