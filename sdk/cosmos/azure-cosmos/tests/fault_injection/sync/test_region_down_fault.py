# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Legacy regional-outage outcomes through the synchronous Rust-backed APIs."""

import asyncio

import pytest

from fault_injection._region_down import exercise

pytestmark = [
    pytest.mark.cosmosEmulator,
    pytest.mark.cosmosSdkFaultInjection,
    pytest.mark.unittest,
    pytest.mark.timeout(180),
    pytest.mark.parametrize("inject", [True, False], ids=["outage", "no-outage"]),
]


def test_swr_mrr_region_down_read_succeeds_rust(request, regional_target, monkeypatch, inject):
    # Source: tests/test_fault_injection_transport.py::TestFaultInjectionTransport.test_swr_mrr_region_down_read_succeeds
    asyncio.run(
        exercise(request, regional_target, monkeypatch, "read-down", inject, asynchronous=False, _backend="rust")
    )


def test_swr_mrr_region_down_envoy_read_succeeds_rust(request, regional_target, monkeypatch, inject):
    # Source: tests/test_fault_injection_transport.py::TestFaultInjectionTransport.test_swr_mrr_region_down_envoy_read_succeeds
    asyncio.run(
        exercise(request, regional_target, monkeypatch, "read-envoy", inject, asynchronous=False, _backend="rust")
    )


def test_mwr_region_down_succeeds_rust(request, regional_target, monkeypatch, inject):
    # Source: tests/test_fault_injection_transport.py::TestFaultInjectionTransport.test_mwr_region_down_succeeds
    asyncio.run(
        exercise(request, regional_target, monkeypatch, "mwr-down", inject, asynchronous=False, _backend="rust")
    )


def test_swr_mrr_all_regions_down_for_read_rust(request, regional_target, monkeypatch, inject):
    # Source: tests/test_fault_injection_transport.py::TestFaultInjectionTransport.test_swr_mrr_all_regions_down_for_read
    asyncio.run(
        exercise(request, regional_target, monkeypatch, "all-reads-down", inject, asynchronous=False, _backend="rust")
    )


def test_mwr_all_regions_down_rust(request, regional_target, monkeypatch, inject):
    # Source: tests/test_fault_injection_transport.py::TestFaultInjectionTransport.test_mwr_all_regions_down
    asyncio.run(
        exercise(request, regional_target, monkeypatch, "all-down", inject, asynchronous=False, _backend="rust")
    )
