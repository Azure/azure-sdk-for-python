# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for the M365 FoundryStorage adapter (backed by FoundryStateStore)."""

from __future__ import annotations

import asyncio
from collections import UserDict
from typing import Any, MutableMapping
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.ai.agentserver.activity import FoundryStorage
import azure.ai.agentserver.activity._foundry_storage as module
from azure.ai.agentserver.core.storage import FoundryStorageNotFoundError, StateStoreItem


class _TestStoreItem:
    def __init__(self, value: dict[str, Any]) -> None:
        self.value = value

    def store_item_to_json(self) -> dict[str, Any]:
        return self.value

    @staticmethod
    def from_json_to_store_item(json_data: dict[str, Any]) -> "_TestStoreItem":
        return _TestStoreItem(json_data)


class _MappingStoreItem:
    """A store item whose payload is a non-``dict`` ``MutableMapping``.

    M365's ``StoreItem.store_item_to_json()`` is annotated to return a
    ``MutableMapping``, not a concrete ``dict``, and implementations are free to
    honor that literally. ``FoundryStateStore.set_item()`` requires a ``dict``.
    """

    def __init__(self, value: dict[str, Any]) -> None:
        self.value: MutableMapping[str, Any] = UserDict(value)

    def store_item_to_json(self) -> MutableMapping[str, Any]:
        return self.value

    @staticmethod
    def from_json_to_store_item(json_data: dict[str, Any]) -> "_MappingStoreItem":
        return _MappingStoreItem(dict(json_data))


def _fake_store() -> MagicMock:
    store = MagicMock()
    store.get_item = AsyncMock(return_value=None)
    store.set_item = AsyncMock()
    store.delete_item = AsyncMock()
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
    store.get_item = AsyncMock(
        return_value=StateStoreItem(
            {
                "id": "i1",
                "object": "state_store.item",
                "key": "k",
                "value": {"count": 3},
                "etag": "e1",
                "created_at": 0,
                "updated_at": 0,
            }
        )
    )
    _patch_stores(monkeypatch, {"k": store})
    storage = FoundryStorage()

    result = await storage.read(["k"], target_cls=_TestStoreItem)

    assert result["k"].value == {"count": 3}
    store.get_item.assert_awaited_once_with("k")


@pytest.mark.asyncio
async def test_read_treats_missing_item_as_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """FoundryStateStore.get_item() already returns None for a missing store/item."""
    store = _fake_store()
    store.get_item = AsyncMock(return_value=None)
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
    store.set_item.assert_awaited_once_with("k", {"turn": 4})


@pytest.mark.asyncio
async def test_write_materializes_a_dict_from_a_non_dict_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    """``set_item()`` must receive a real ``dict``, not whatever ``Mapping`` the item returned."""
    store = _fake_store()
    _patch_stores(monkeypatch, {"k": store})
    storage = FoundryStorage()

    await storage.write({"k": _MappingStoreItem({"turn": 4})})

    _, payload = store.set_item.await_args.args
    assert type(payload) is dict
    assert payload == {"turn": 4}


@pytest.mark.asyncio
async def test_write_only_ensures_the_store_exists_once(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _fake_store()
    mock_cls = _patch_stores(monkeypatch, {"k": store})
    storage = FoundryStorage()

    await storage.write({"k": _TestStoreItem({"turn": 1})})
    await storage.write({"k": _TestStoreItem({"turn": 2})})

    mock_cls.get_or_create.assert_awaited_once()
    assert store.set_item.await_count == 2


@pytest.mark.asyncio
async def test_write_closes_unconfirmed_read_client_after_upgrade(monkeypatch: pytest.MonkeyPatch) -> None:
    read_store = _fake_store()
    write_store = _fake_store()
    mock_cls = MagicMock(return_value=read_store)
    mock_cls.get_or_create = AsyncMock(return_value=write_store)
    monkeypatch.setattr(module, "FoundryStateStore", mock_cls)
    storage = FoundryStorage()

    await storage.read(["k"], target_cls=_TestStoreItem)
    await storage.write({"k": _TestStoreItem({"turn": 1})})

    read_store.aclose.assert_awaited_once()
    write_store.set_item.assert_awaited_once_with("k", {"turn": 1})


@pytest.mark.asyncio
async def test_write_defers_replaced_client_close_until_active_read_finishes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    read_store = _fake_store()
    write_store = _fake_store()
    read_started = asyncio.Event()
    finish_read = asyncio.Event()

    async def slow_get_item(key: str) -> None:
        read_started.set()
        await finish_read.wait()

    read_store.get_item = AsyncMock(side_effect=slow_get_item)
    mock_cls = MagicMock(return_value=read_store)
    mock_cls.get_or_create = AsyncMock(return_value=write_store)
    monkeypatch.setattr(module, "FoundryStateStore", mock_cls)
    storage = FoundryStorage()

    active_read = asyncio.create_task(storage.read(["k"], target_cls=_TestStoreItem))
    await read_started.wait()
    await storage.write({"k": _TestStoreItem({"turn": 1})})

    read_store.aclose.assert_not_awaited()
    finish_read.set()
    await active_read
    read_store.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_forwards_the_key_and_ignores_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _fake_store()
    store.delete_item = AsyncMock(side_effect=FoundryStorageNotFoundError("not found"))
    _patch_stores(monkeypatch, {"k": store})
    storage = FoundryStorage()

    await storage.delete(["k"])  # must not raise

    store.delete_item.assert_awaited_once_with("k")


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
async def test_sign_in_key_with_colon_user_id_gets_user_isolation(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}
    key = "auth:_SignInState:msteams:29:user-id"

    def factory(store_name: str, **kwargs: Any) -> MagicMock:
        captured[store_name] = kwargs
        return _fake_store()

    monkeypatch.setattr(module, "FoundryStateStore", MagicMock(side_effect=factory))
    storage = FoundryStorage()

    await storage.read([key], target_cls=_TestStoreItem)

    assert captured[key]["user_isolation"] is True


def test_bounded_store_name_distinguishes_long_keys_with_the_same_prefix() -> None:
    common_prefix = "msteams/conversations/" + ("a" * 140)
    first = module._bounded_store_name(f"{common_prefix}-first")
    second = module._bounded_store_name(f"{common_prefix}-second")

    assert len(first) == module._MAX_STORE_NAME_LEN
    assert len(second) == module._MAX_STORE_NAME_LEN
    assert first != second


@pytest.mark.asyncio
async def test_store_resolution_log_does_not_include_identifiers(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    key = "msteams/users/sensitive-user-id"
    _patch_stores(monkeypatch, {key: _fake_store()})
    storage = FoundryStorage()

    with caplog.at_level("DEBUG", logger=module.__name__):
        await storage.read([key], target_cls=_TestStoreItem)

    assert key not in caplog.text


@pytest.mark.asyncio
async def test_eviction_defers_close_until_active_operation_finishes(monkeypatch: pytest.MonkeyPatch) -> None:
    first_store = _fake_store()
    second_store = _fake_store()
    read_started = asyncio.Event()
    finish_read = asyncio.Event()

    async def slow_get_item(key: str) -> None:
        read_started.set()
        await finish_read.wait()

    first_store.get_item = AsyncMock(side_effect=slow_get_item)
    _patch_stores(monkeypatch, {"first": first_store, "second": second_store})
    storage = FoundryStorage()
    storage._max_cached_stores = 1

    first_read = asyncio.create_task(storage.read(["first"], target_cls=_TestStoreItem))
    await read_started.wait()
    await storage.read(["second"], target_cls=_TestStoreItem)

    first_store.aclose.assert_not_awaited()
    finish_read.set()
    await first_read
    first_store.aclose.assert_awaited_once()


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
    # microsoft-agents-hosting-core >= 1.3.0 makes AsyncStorageBase.read require
    # target_cls (omitting it raises TypeError at the API boundary); older
    # supported versions (>= 1.1.0 floor) raise ValueError from the validation
    # path. Accept both so the test covers the full declared dependency range.
    with pytest.raises((ValueError, TypeError), match="target_cls"):
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
