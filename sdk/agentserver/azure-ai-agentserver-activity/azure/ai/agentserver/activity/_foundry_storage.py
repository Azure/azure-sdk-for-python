# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""M365 Agents SDK storage adapter backed by per-key Foundry state stores."""
# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
# pylint: disable=docstring-keyword-should-match-keyword-only,import-error,no-name-in-module

from __future__ import annotations

import asyncio
from typing import Any, Callable, Optional, Tuple, Type, TypeVar

from azure.ai.agentserver.core.storage import FoundryStateStore, FoundryStorageEndpoint, FoundryStorageNotFoundError
from azure.core.credentials_async import AsyncTokenCredential

try:
    from microsoft_agents.hosting.core.storage import AsyncStorageBase, Storage
except ImportError:  # pragma: no cover - keeps package importable without optional M365 SDK bits.
    class Storage:  # type: ignore[no-redef]
        """Fallback base class used only when the M365 Agents SDK is not installed."""

    class AsyncStorageBase(Storage):  # type: ignore[no-redef]
        """Fallback base class used only when the M365 Agents SDK is not installed."""


StoreItemT = TypeVar("StoreItemT")

#: Segment the M365 Agents SDK ``UserState`` uses to build per-user storage keys
#: (``f"{channel_id}/users/{user_id}"`` -- see
#: ``microsoft_agents.hosting.core.state.user_state.UserState.get_storage_key``).
#: Keys containing this segment get ``user_isolation=True`` on their backing
#: store by default.
_USER_SCOPE_SEGMENT = "/users/"


def _default_is_user_scoped(key: str) -> bool:
    """Match the M365 ``UserState`` key shape ``"{channel_id}/users/{user_id}"``."""
    return _USER_SCOPE_SEGMENT in key


class FoundryStorage(AsyncStorageBase):
    """Durable M365 Agents SDK storage adapter for Foundry-hosted Activity agents.

    Backed by :class:`~azure.ai.agentserver.core.storage.FoundryStateStore`, whose
    protocol binds every client to one explicit, caller-named store -- "store
    name = scope". Each M365 storage key (already a scope identifier, for
    example ``f"{channel_id}/conversations/{conversation_id}"`` or
    ``f"{channel_id}/users/{user_id}"``) gets its own lazily-created,
    lazily-cached :class:`FoundryStateStore`, with the key doubling as both the
    store name and the single item key stored in it. This mirrors the M365 SDK
    itself, which never batches keys from different scopes in one call (every
    ``AgentState`` / ``Authorization`` / ``Proactive`` call operates on exactly
    one key).

    Subclasses :class:`~microsoft_agents.hosting.core.storage.AsyncStorageBase`,
    which implements the batch :meth:`read` / :meth:`write` / :meth:`delete`
    (validation + concurrent fan-out) in terms of the single-item
    ``_read_item`` / ``_write_item`` / ``_delete_item`` hooks below.

    :keyword credential: Async token credential shared by every per-key store.
        Defaults to ``DefaultAzureCredential`` (requires ``azure-identity``).
    :keyword endpoint: Foundry storage endpoint or project endpoint URL override.
    :keyword item_ttl_seconds: Store-level TTL applied to every per-key store
        created by this adapter. Defaults to ``FoundryStateStore``'s own default
        (30 days) when omitted.
    :keyword is_user_scoped: Predicate deciding which keys get
        ``user_isolation=True`` on their backing store. Defaults to matching the
        M365 ``UserState`` key shape (``"{channel_id}/users/{user_id}"``).
    """

    def __init__(
        self,
        *,
        credential: AsyncTokenCredential | None = None,
        endpoint: FoundryStorageEndpoint | str | None = None,
        item_ttl_seconds: int | None = None,
        is_user_scoped: Callable[[str], bool] = _default_is_user_scoped,
    ) -> None:
        self._owns_credential = credential is None
        if credential is None:
            try:
                from azure.identity.aio import DefaultAzureCredential
            except ImportError as exc:  # pragma: no cover
                raise ImportError(
                    "FoundryStorage requires azure-identity when no credential is supplied. "
                    "Install azure-identity or pass an async credential."
                ) from exc
            credential = DefaultAzureCredential()
        self._credential = credential
        self._endpoint = endpoint
        self._item_ttl_seconds = item_ttl_seconds
        self._is_user_scoped = is_user_scoped

        self._stores: dict[str, FoundryStateStore] = {}
        self._ensured_keys: set[str] = set()
        self._creation_lock = asyncio.Lock()

    def _new_store(self, key: str) -> FoundryStateStore:
        kwargs: dict[str, Any] = {
            "credential": self._credential,
            "endpoint": self._endpoint,
            "user_isolation": self._is_user_scoped(key),
        }
        if self._item_ttl_seconds is not None:
            kwargs["item_ttl_seconds"] = self._item_ttl_seconds
        return FoundryStateStore(key, **kwargs)

    async def _get_store(self, key: str, *, ensure_exists: bool) -> FoundryStateStore:
        """Return the cached per-key store, creating the client (and, when
        ``ensure_exists``, the server-side store resource) on first use."""
        store = self._stores.get(key)
        if store is None:
            async with self._creation_lock:
                store = self._stores.get(key)
                if store is None:
                    store = self._new_store(key)
                    self._stores[key] = store
        if ensure_exists and key not in self._ensured_keys:
            async with self._creation_lock:
                if key not in self._ensured_keys:
                    await store.get_or_create()
                    self._ensured_keys.add(key)
        return store

    async def aclose(self) -> None:
        """Close every cached per-key store and an owned default credential."""
        for store in list(self._stores.values()):
            await store.aclose()
        self._stores.clear()
        self._ensured_keys.clear()
        if self._owns_credential and hasattr(self._credential, "close"):
            await self._credential.close()

    async def __aenter__(self) -> "FoundryStorage":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    async def _read_item(
        self,
        key: str,
        *,
        target_cls: Type[StoreItemT] | None = None,
        **kwargs: Any,
    ) -> Tuple[Optional[str], Optional[StoreItemT]]:
        """Fetch one item. A store that does not exist yet is just a missing key."""
        _ = kwargs
        store = await self._get_store(key, ensure_exists=False)
        try:
            item = await store.get(key)
        except FoundryStorageNotFoundError:
            item = None
        if item is None:
            return None, None
        return key, target_cls.from_json_to_store_item(item.value)  # type: ignore[attr-defined]

    async def _write_item(self, key: str, value: StoreItemT) -> None:
        """Create-or-replace one item, creating its backing store on first write."""
        store = await self._get_store(key, ensure_exists=True)
        await store.set(key, value.store_item_to_json())  # type: ignore[attr-defined]

    async def _delete_item(self, key: str) -> None:
        """Delete one item. Missing keys (or stores) are ignored."""
        store = await self._get_store(key, ensure_exists=False)
        try:
            await store.delete(key)
        except FoundryStorageNotFoundError:
            pass
