# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline contracts for Rust-only fault setup; no service execution is implied."""

from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import pytest

from azure.cosmos.documents import DatabaseAccount
from config import clients, fault_resources


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


@pytest.mark.parametrize("error", [
    NotImplementedError("get_database_account() is not yet available through the Rust binding"),
    RuntimeError("account read failed"),
])
def test_account_api_failure_is_propagated_without_skip_or_substitution_rust(monkeypatch, error):
    client = MagicMock()
    client.__enter__.return_value = client
    client.get_database_account.side_effect = error
    factory = Mock(return_value=client)
    monkeypatch.setattr(clients, "create_fault_setup_client", factory)
    with pytest.raises(type(error)) as caught:
        fault_resources.load_account("https://localhost:8081/", "test-key")
    assert caught.value is error
    factory.assert_called_once_with("https://localhost:8081/", "test-key")
    client.get_database_account.assert_called_once_with()
    client.__exit__.assert_called_once()


def test_account_model_is_not_mistaken_for_the_complete_service_document_rust(monkeypatch):
    client = MagicMock()
    client.__enter__.return_value = client
    client.get_database_account.return_value = DatabaseAccount()
    monkeypatch.setattr(clients, "create_fault_setup_client", Mock(return_value=client))
    with pytest.raises(NotImplementedError, match="complete account document"):
        fault_resources.load_account("https://localhost:8081/", "test-key")
