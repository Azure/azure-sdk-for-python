# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Parity checks for provider surface method naming."""

from __future__ import annotations

from azure.ai.agentserver.responses.store._base import ResponseProviderProtocol
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider


def test_provider_parity__in_memory_class_name_is_canonical() -> None:
    provider = InMemoryResponseProvider()

    assert isinstance(provider, InMemoryResponseProvider)


def test_provider_parity__interface_name_is_responseproviderprotocol() -> None:
    provider = InMemoryResponseProvider()

    assert isinstance(provider, ResponseProviderProtocol)


def test_provider_parity__surface_methods_exist() -> None:
    provider = InMemoryResponseProvider()

    assert hasattr(provider, "create_response")
    assert hasattr(provider, "get_response")
    assert hasattr(provider, "update_response")
    assert hasattr(provider, "delete_response")
    assert hasattr(provider, "get_input_items")
    assert hasattr(provider, "get_items")
    assert hasattr(provider, "get_history_item_ids")
