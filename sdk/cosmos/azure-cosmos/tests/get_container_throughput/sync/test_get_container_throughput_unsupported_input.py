# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Rust behavior test
"""Container ``get_throughput`` on Rust rejects unsupported input before any service call."""

import os

import pytest

from azure.cosmos import CosmosClient
from config.diagnostics import _binding_operation_count, _rust_fallback_count

pytestmark = [pytest.mark.cosmosEmulator]


@pytest.mark.parametrize("options", [
    {"availability_strategy": True}, {"initial_headers": {"Accept": "unsupported"}},
], ids=["availability_strategy", "accept_header"])
def test_get_container_throughput_unsupported_input_raises_not_implemented_rust(monkeypatch, options):
    """availability_strategy or an Accept header raises NotImplementedError pointing at the legacy Python path.

    Nothing reaches the Rust binding, container metadata, or a legacy QueryOffers fallback.
    """
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        container = client.get_database_client("not-requested").get_container_client("not-requested")

        def forbidden(*args, **kwargs):
            pytest.fail("unsupported input reached metadata or legacy query")

        monkeypatch.setattr(container, "_get_properties", forbidden)
        monkeypatch.setattr(container, "read", forbidden)
        monkeypatch.setattr(client.client_connection, "QueryOffers", forbidden)

        before = (_binding_operation_count(), _rust_fallback_count())
        with pytest.raises(NotImplementedError, match="legacy Python path"):
            container.get_throughput(**options)
        assert (_binding_operation_count(), _rust_fallback_count()) == before
