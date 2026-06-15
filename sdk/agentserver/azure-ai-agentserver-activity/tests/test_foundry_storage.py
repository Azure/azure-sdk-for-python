# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for the M365 FoundryStorage adapter and host storage wiring."""

from __future__ import annotations

import sys
import types
from typing import Any
from unittest.mock import AsyncMock

import pytest

from azure.ai.agentserver.activity import ActivityAgentServerHost, FoundryStorage
from azure.ai.agentserver.activity import _m365_bridge


class _TestStoreItem:
    def __init__(self, value: dict[str, Any]) -> None:
        self.value = value

    def store_item_to_json(self) -> dict[str, Any]:
        return self.value

    @staticmethod
    def from_json_to_store_item(json_data: dict[str, Any]) -> "_TestStoreItem":
        return _TestStoreItem(json_data)


def _make_storage(client: Any) -> FoundryStorage:
    return FoundryStorage(client=client)


@pytest.mark.asyncio
async def test_foundry_storage_read_deserializes_store_items_and_omits_missing() -> None:
    client = AsyncMock()
    client.read = AsyncMock(return_value={"present": {"value": {"count": 3}, "etag": "e1"}})
    storage = _make_storage(client)

    result = await storage.read(["present", "missing"], target_cls=_TestStoreItem)

    assert list(result) == ["present"]
    assert result["present"].value == {"count": 3}
    client.read.assert_awaited_once_with(["present", "missing"])


@pytest.mark.asyncio
async def test_foundry_storage_write_serializes_store_items_for_lww_upsert() -> None:
    client = AsyncMock()
    storage = _make_storage(client)

    await storage.write({"k": _TestStoreItem({"turn": 4})})

    client.write.assert_awaited_once_with({"k": {"turn": 4}})


@pytest.mark.asyncio
async def test_foundry_storage_delete_forwards_keys() -> None:
    client = AsyncMock()
    storage = _make_storage(client)

    await storage.delete(["a", "b"])

    client.delete.assert_awaited_once_with(["a", "b"])


@pytest.mark.asyncio
async def test_foundry_storage_validates_like_m365_storage() -> None:
    storage = _make_storage(AsyncMock())

    with pytest.raises(ValueError, match="Keys are required"):
        await storage.read([], target_cls=_TestStoreItem)
    with pytest.raises(ValueError, match="target_cls cannot be None"):
        await storage.read(["k"])
    with pytest.raises(ValueError, match="key cannot be empty"):
        await storage.write({"": _TestStoreItem({})})
    with pytest.raises(ValueError, match="Keys are required"):
        await storage.delete([])


def test_activity_host_stores_storage_for_bridge() -> None:
    storage = object()
    app = ActivityAgentServerHost(storage=storage, configure_observability=None)

    assert app.state.activity_storage is storage


def test_m365_bridge_uses_supplied_storage(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    activity_mod = types.ModuleType("microsoft_agents.activity")
    activity_mod.Activity = object
    activity_mod.load_configuration_from_env = lambda _env: {"bot_app_id": "app"}

    msal_mod = types.ModuleType("microsoft_agents.authentication.msal")

    class FakeMsalConnectionManager:
        def __init__(self, **kwargs: Any) -> None:
            captured["config"] = kwargs

    msal_mod.MsalConnectionManager = FakeMsalConnectionManager

    hosting_mod = types.ModuleType("microsoft_agents.hosting.core")

    class FakeMemoryStorage:
        pass

    class FakeHttpAdapterBase:
        def __init__(self, **kwargs: Any) -> None:
            captured["adapter_kwargs"] = kwargs

    class FakeRestChannelServiceClientFactory:
        def __init__(self, connection_manager: Any) -> None:
            captured["connection_manager"] = connection_manager

    class FakeAuthorization:
        def __init__(self, storage: Any, connection_manager: Any, **kwargs: Any) -> None:
            captured["auth_storage"] = storage
            captured["auth_connection_manager"] = connection_manager

    class FakeAgentApplication:
        def __init__(self, **kwargs: Any) -> None:
            captured["app_storage"] = kwargs["storage"]
            captured["app_authorization"] = kwargs["authorization"]

        @classmethod
        def __class_getitem__(cls, _item: Any) -> type["FakeAgentApplication"]:
            return cls

    hosting_mod.AgentApplication = FakeAgentApplication
    hosting_mod.Authorization = FakeAuthorization
    hosting_mod.HttpAdapterBase = FakeHttpAdapterBase
    hosting_mod.MemoryStorage = FakeMemoryStorage
    hosting_mod.RestChannelServiceClientFactory = FakeRestChannelServiceClientFactory
    hosting_mod.TurnState = object

    monkeypatch.setitem(sys.modules, "microsoft_agents.activity", activity_mod)
    monkeypatch.setitem(sys.modules, "microsoft_agents.authentication.msal", msal_mod)
    monkeypatch.setitem(sys.modules, "microsoft_agents.hosting.core", hosting_mod)

    supplied_storage = object()
    _m365_bridge._reset_for_testing()
    try:
        _m365_bridge._ensure_m365_initialized(supplied_storage)
    finally:
        _m365_bridge._reset_for_testing()

    assert captured["auth_storage"] is supplied_storage
    assert captured["app_storage"] is supplied_storage
