# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Rust-adapter replacements for the retired legacy cache regressions.

Both public clients use their real Rust adapters; only the extension boundary
and clock are faked. Native items.rs tests separately verify the resolved RID,
metadata/write routing, and one deadline across actual driver execution.
The legacy Python cache-lock assertion has no Rust equivalent and is retired.
"""

import pytest

from azure.cosmos._backend.binding_adapter import BindingAdapter
from azure.cosmos.aio._backend.binding_adapter import AsyncBindingAdapter
from azure.cosmos.exceptions import CosmosClientTimeoutError
from create_item.test_create_item_contract_unit import (  # pylint: disable=unused-import
    point_create, point_read,
)

pytestmark = pytest.mark.parametrize(
    "point_read", [(False, True), (True, True)], ids=["sync-rust", "async-rust"], indirect=True
)


@pytest.fixture
def rust_create(point_create):
    assert point_create.rust
    assert isinstance(point_create.cc._backend, (BindingAdapter, AsyncBindingAdapter))
    point_create.cc.CreateItem.side_effect = AssertionError("Rust create used the legacy connection")
    point_create.proxy.read.side_effect = AssertionError("Rust create used Python metadata lookup")
    yield point_create
    point_create.cc.CreateItem.assert_not_called()
    point_create.proxy.read.assert_not_called()


@pytest.mark.parametrize("legacy_cache_populated", [False, True])
def test_container_identity_is_resolved_by_driver_rust(rust_create, legacy_cache_populated):
    """The driver resolves the target; stale Python cache identity must not leak."""
    if legacy_cache_populated:
        rust_create.cc._container_properties_cache["dbs/db/colls/c"] = {
            "_rid": "stale-python-rid", "partitionKey": {"paths": ["/obsolete"], "kind": "Hash"},
        }
    created = rust_create.call({"id": "item", "pk": "A"})
    assert created["id"] == "item"
    assert rust_create.native_calls == 1
    prepared = rust_create.prepared
    assert prepared.op == "create_item"
    assert prepared.container_link == "dbs/db/colls/c"
    assert prepared.partition_key.kind == "extract"
    assert prepared.settings.resource.container_rid is None
    assert "x-ms-cosmos-intended-collection-rid" not in prepared.headers


@pytest.mark.parametrize("excluded", [[], ["West US"], ["West US", "East US"]])
def test_metadata_exclusions_reach_native_create_rust(rust_create, excluded):
    """One native call carries the exclusions used during lazy metadata resolution."""
    supplied = list(excluded)
    created = rust_create.call({"id": "item", "pk": "A"}, excluded_locations=supplied)
    assert created["id"] == "item"
    assert rust_create.native_calls == 1
    assert rust_create.prepared.settings.excluded_locations == tuple(excluded)
    assert supplied == excluded


@pytest.mark.parametrize("init_delay,metadata_delay,write_delay,expires,events", [
    (0.25, 0.5, 0.125, False, [("metadata", 0.75), ("write", 0.25)]),
    (0.25, 0.75, 0, True, [("metadata", 0.75)]),
    (0.25, 0.5, 0.5, True, [("metadata", 0.75), ("write", 0.25)]),
])
def test_initialization_metadata_and_create_share_budget_rust(
    rust_create, init_delay, metadata_delay, write_delay, expires, events
):
    rust_create.init_delay = init_delay
    rust_create.metadata_delay = metadata_delay
    rust_create.write_delay = write_delay
    if expires:
        with pytest.raises(CosmosClientTimeoutError):
            rust_create.call({"id": "item", "pk": "A"}, timeout=1)
    else:
        assert rust_create.call({"id": "item", "pk": "A"}, timeout=1)["id"] == "item"
    assert rust_create.native_calls == 1
    assert rust_create.events == events
    assert rust_create.clock.now <= 101
