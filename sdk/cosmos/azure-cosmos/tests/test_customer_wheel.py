# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run against the shipped wheel, never the instrumented test wheel."""

import inspect
import json
from types import SimpleNamespace

import pytest

from azure.cosmos import CosmosClient, _rust
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos._backend.binding_adapter import BindingAdapter
from azure.cosmos.aio._backend.binding_adapter import AsyncBindingAdapter
from azure.cosmos._feed_ranges_rust_routing import build_feed_range_subset_request


pytestmark = pytest.mark.cosmosCustomerWheel


def test_customer_wheel_has_no_test_probes_rust():
    assert not hasattr(_rust, "_AsyncOperationProbe")
    assert not [name for name in dir(_rust) if name.startswith("_debug_")]
    for adapter_type in (BindingAdapter, AsyncBindingAdapter):
        assert not hasattr(adapter_type, "_debug_fault_injection_rule_hit_count")


@pytest.mark.parametrize("operation", ["create_item", "create_item_async", "read_item", "read_item_async"])
@pytest.mark.parametrize("enabled", [False, True])
def test_customer_wheel_omits_fault_diagnostics_keyword_rust(operation, enabled):
    function = getattr(_rust, operation)
    assert "include_fault_diagnostics" not in inspect.signature(function).parameters
    with pytest.raises(TypeError, match="unexpected keyword argument 'include_fault_diagnostics'"):
        function(None, None, include_fault_diagnostics=enabled)


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
@pytest.mark.parametrize("rules", [[], (), [{"id": "test", "operation_type": "ReadItem", "status_code": 503}]])
def test_customer_wheel_rejects_fault_rules_even_with_test_switch_rust(monkeypatch, client_type, rules):
    monkeypatch.setenv("COSMOS_ENABLE_FAULT_INJECTION", "1")
    with pytest.raises(TypeError, match="--features test-probes"):
        client_type("https://127.0.0.1:1/", "a2V5", _backend="rust", _fault_injection_rules=rules)


@pytest.mark.parametrize("acquire", [False, True])
def test_customer_wheel_rejects_fault_rules_at_native_boundary_rust(monkeypatch, acquire):
    monkeypatch.setenv("COSMOS_ENABLE_FAULT_INJECTION", "1")
    config = SimpleNamespace(fault_injection_rules=(object(),))
    with pytest.raises(ValueError, match="--features test-probes"):
        if acquire:
            _rust.acquire_driver_handle("https://127.0.0.1:1/", "a2V5", config=config)
        else:
            _rust._validate_runtime_configuration(config)


@pytest.mark.parametrize("child_max,expected", [("60", True), ("C0", False)])
def test_customer_wheel_executes_without_debug_counters_rust(child_max, expected):
    prepared = build_feed_range_subset_request(
        parent_feed_range={"Range": {"min": "00", "max": "80", "isMinInclusive": True, "isMaxInclusive": False}},
        child_feed_range={"Range": {"min": "40", "max": child_max, "isMinInclusive": True, "isMaxInclusive": False}},
    )
    status, _, _, body, _ = _rust.is_feed_range_subset(None, prepared)
    assert status == 200
    assert json.loads(body) == {"IsSubset": expected}
