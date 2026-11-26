# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Legacy regional-outage outcomes through the asynchronous Rust-backed APIs."""

import pytest

from fault_injection._region_down import exercise

pytestmark = [
    pytest.mark.cosmosEmulator,
    pytest.mark.cosmosSdkFaultInjection,
    pytest.mark.asyncio,
    pytest.mark.timeout(180),
    pytest.mark.parametrize("inject", [True, False], ids=["outage", "no-outage"]),
]


async def test_swr_mrr_region_down_read_succeeds_async_rust(request, regional_target, monkeypatch, inject):
    # Source: tests/test_fault_injection_transport_async.py::TestFaultInjectionTransportAsync.test_swr_mrr_region_down_read_succeeds_async
    await exercise(request, regional_target, monkeypatch, "read-down", inject, asynchronous=True, _backend="rust")


async def test_swr_mrr_region_down_envoy_read_succeeds_async_rust(request, regional_target, monkeypatch, inject):
    # Source: tests/test_fault_injection_transport_async.py::TestFaultInjectionTransportAsync.test_swr_mrr_region_down_envoy_read_succeeds_async
    await exercise(request, regional_target, monkeypatch, "read-envoy", inject, asynchronous=True, _backend="rust")


async def test_mwr_region_down_succeeds_async_rust(request, regional_target, monkeypatch, inject):
    # Source: tests/test_fault_injection_transport_async.py::TestFaultInjectionTransportAsync.test_mwr_region_down_succeeds_async
    await exercise(request, regional_target, monkeypatch, "mwr-down", inject, asynchronous=True, _backend="rust")


async def test_swr_mrr_all_regions_down_for_read_async_rust(request, regional_target, monkeypatch, inject):
    # Source: tests/test_fault_injection_transport_async.py::TestFaultInjectionTransportAsync.test_swr_mrr_all_regions_down_for_read_async
    await exercise(request, regional_target, monkeypatch, "all-reads-down", inject, asynchronous=True, _backend="rust")


async def test_mwr_all_regions_down_async_rust(request, regional_target, monkeypatch, inject):
    # Source: tests/test_fault_injection_transport_async.py::TestFaultInjectionTransportAsync.test_mwr_all_regions_down_async
    await exercise(request, regional_target, monkeypatch, "all-down", inject, asynchronous=True, _backend="rust")
