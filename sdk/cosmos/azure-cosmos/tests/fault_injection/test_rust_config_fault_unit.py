# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline contracts for Rust-only fault setup; no service execution is implied."""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from config import clients
from fault_injection._regional_routing import READ_REGION, WRITE_REGION, mock_account, rules, topology


def test_fault_setup_uses_independent_direct_rust_runtimes_rust(monkeypatch):
    runtimes = [object(), object()]
    create_runtime = Mock(side_effect=runtimes)
    constructor = Mock()
    monkeypatch.setattr(clients, "CosmosRuntime", SimpleNamespace(create=create_runtime))
    monkeypatch.setattr(clients, "CosmosClient", constructor)
    for runtime in runtimes:
        clients.create_fault_setup_client("https://localhost:8081/", "test-key")
        constructor.assert_called_with(
            "https://localhost:8081/", "test-key", _backend="rust", runtime=runtime, timeout=30,
        )
    assert create_runtime.call_count == 2
    assert all(call.kwargs["connection_pool"].proxy_allowed is False for call in create_runtime.call_args_list)


def test_fault_setup_does_not_replace_a_rust_failure_with_legacy_rust(monkeypatch):
    create_runtime = Mock(side_effect=RuntimeError("Rust unavailable"))
    constructor = Mock()
    monkeypatch.setattr(clients, "CosmosRuntime", SimpleNamespace(create=create_runtime))
    monkeypatch.setattr(clients, "CosmosClient", constructor)
    with pytest.raises(RuntimeError, match="Rust unavailable"):
        clients.create_fault_setup_client("https://localhost:8081/", "test-key")
    constructor.assert_not_called()


def test_mock_account_document_parses_and_always_refreshes_rust():
    account = json.loads(rules("rule", "orders", topology(
        mock_account(), "https://127.0.0.1:8081/", "https://localhost:8081/", False))[0]["response_body"])
    # The Rust driver requires these three fields; the rest have defaults.
    assert {"_self", "id", "_rid"} <= account.keys()
    # A repeated etag would make the driver skip the injected refresh.
    assert "_etag" not in account
    assert [region["name"] for region in account["readableLocations"]] == [WRITE_REGION, READ_REGION]
