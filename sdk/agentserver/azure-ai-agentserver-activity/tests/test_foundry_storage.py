# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for the M365 FoundryStorage adapter (backed by FoundryStateStore)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.ai.agentserver.activity import FoundryStorage
import azure.ai.agentserver.activity._foundry_storage as module
from azure.ai.agentserver.core.storage import FoundryStorageNotFoundError, StateItem


class _TestStoreItem:
    def __init__(self, value: dict[str, Any]) -> None:
        self.value = value

    def store_item_to_json(self) -> dict[str, Any]:
        return self.value

    @staticmethod
    def from_json_to_store_item(json_data: dict[str, Any]) -> "_TestStoreItem":
        return _TestStoreItem(json_data)


def _fake_store() -> MagicMock:
    store = MagicMock()
    store.get = AsyncMock(return_value=None)
    store.set = AsyncMock()
    store.delete = AsyncMock()
    store.aclose = AsyncMock()
    return store


def _patch_stores(monkeypatch: pytest.MonkeyPatch, stores_by_key: dict[str, MagicMock]) -> MagicMock:
    """Patch ``FoundryStateStore`` so both the plain constructor (reads/deletes)
    and the ``get_or_create`` classmethod (writes) resolve to the given fakes."""

    def factory(key: str, **kwargs: Any) -> MagicMock:
        return stores_by_key[key]

    mock_cls = MagicMock(side_effect=factory)
    mock_cls.get_or_create = AsyncMock(side_effect=lambda key, **kwargs: stores_by_key[key])
    monkeypatch.setattr(module, "FoundryStateStore", mock_cls)
    return mock_cls


@pytest.mark.asyncio
async def test_read_missing_key_does_not_create_a_store(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _fake_store()
    mock_cls = _patch_stores(monkeypatch, {"k": store})
    storage = FoundryStorage()

    result = await storage.read(["k"], target_cls=_TestStoreItem)

    assert result == {}
    mock_cls.assert_called_once()  # plain client constructed to issue the GET ...
    mock_cls.get_or_create.assert_not_awaited()  # ... but the store resource is never created for a read


@pytest.mark.asyncio
async def test_read_deserializes_existing_item(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _fake_store()
    store.get = AsyncMock(return_value=StateItem(id="i1", key="k", value={"count": 3}, etag="e1"))
    _patch_stores(monkeypatch, {"k": store})
    storage = FoundryStorage()

    result = await storage.read(["k"], target_cls=_TestStoreItem)

    assert result["k"].value == {"count": 3}
    store.get.assert_awaited_once_with("k")


@pytest.mark.asyncio
async def test_read_treats_missing_item_as_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """FoundryStateStore.get() already returns None for a missing store/item."""
    store = _fake_store()
    store.get = AsyncMock(return_value=None)
    _patch_stores(monkeypatch, {"k": store})
    storage = FoundryStorage()

    result = await storage.read(["k"], target_cls=_TestStoreItem)

    assert result == {}


@pytest.mark.asyncio
async def test_write_creates_the_store_then_sets_the_item(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _fake_store()
    mock_cls = _patch_stores(monkeypatch, {"k": store})
    storage = FoundryStorage()

    await storage.write({"k": _TestStoreItem({"turn": 4})})

    mock_cls.get_or_create.assert_awaited_once()
    store.set.assert_awaited_once_with("k", {"turn": 4})


@pytest.mark.asyncio
async def test_write_only_ensures_the_store_exists_once(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _fake_store()
    mock_cls = _patch_stores(monkeypatch, {"k": store})
    storage = FoundryStorage()

    await storage.write({"k": _TestStoreItem({"turn": 1})})
    await storage.write({"k": _TestStoreItem({"turn": 2})})

    mock_cls.get_or_create.assert_awaited_once()
    assert store.set.await_count == 2


@pytest.mark.asyncio
async def test_delete_forwards_the_key_and_ignores_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _fake_store()
    store.delete = AsyncMock(side_effect=FoundryStorageNotFoundError("not found"))
    _patch_stores(monkeypatch, {"k": store})
    storage = FoundryStorage()

    await storage.delete(["k"])  # must not raise

    store.delete.assert_awaited_once_with("k")


@pytest.mark.asyncio
async def test_user_scoped_keys_get_user_isolation(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def factory(key: str, **kwargs: Any) -> MagicMock:
        captured[key] = kwargs
        return _fake_store()

    monkeypatch.setattr(module, "FoundryStateStore", MagicMock(side_effect=factory))
    storage = FoundryStorage()

    await storage.read(["teams/conversations/abc"], target_cls=_TestStoreItem)
    await storage.read(["teams/users/user-42"], target_cls=_TestStoreItem)

    assert captured["teams/conversations/abc"]["user_isolation"] is False
    assert captured["teams/users/user-42"]["user_isolation"] is True


@pytest.mark.asyncio
async def test_custom_is_user_scoped_predicate_is_honored(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def factory(key: str, **kwargs: Any) -> MagicMock:
        captured[key] = kwargs
        return _fake_store()

    monkeypatch.setattr(module, "FoundryStateStore", MagicMock(side_effect=factory))
    storage = FoundryStorage(is_user_scoped=lambda key: key.startswith("private/"))

    await storage.read(["private/whatever"], target_cls=_TestStoreItem)

    assert captured["private/whatever"]["user_isolation"] is True


@pytest.mark.asyncio
async def test_validates_like_m365_storage(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_stores(monkeypatch, {})
    storage = FoundryStorage()

    with pytest.raises(ValueError, match="Keys are required"):
        await storage.read([], target_cls=_TestStoreItem)
    with pytest.raises(ValueError, match="target_cls cannot be None"):
        await storage.read(["k"])
    with pytest.raises(ValueError, match="Changes are required"):
        await storage.write({})
    with pytest.raises(ValueError, match="Keys are required"):
        await storage.delete([])


@pytest.mark.asyncio
async def test_aclose_closes_every_cached_store_but_not_a_supplied_credential(monkeypatch: pytest.MonkeyPatch) -> None:
    store_a, store_b = _fake_store(), _fake_store()
    _patch_stores(monkeypatch, {"a": store_a, "b": store_b})
    credential = MagicMock()
    credential.close = AsyncMock()
    storage = FoundryStorage(credential=credential)

    await storage.read(["a"], target_cls=_TestStoreItem)
    await storage.read(["b"], target_cls=_TestStoreItem)
    await storage.aclose()

    store_a.aclose.assert_awaited_once()
    store_b.aclose.assert_awaited_once()
    credential.close.assert_not_called()  # caller-supplied credential is not owned
