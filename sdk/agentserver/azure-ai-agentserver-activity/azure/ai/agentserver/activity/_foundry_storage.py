# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""M365 Agents SDK storage adapter backed by per-key Foundry state stores."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import hashlib
import logging
import re
from collections import OrderedDict
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, TypeVar, cast

from azure.ai.agentserver.core.storage import FoundryStateStore, FoundryStorageEndpoint, FoundryStorageNotFoundError
from azure.core.credentials_async import AsyncTokenCredential

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    # pylint: disable=import-error,no-name-in-module
    from microsoft_agents.hosting.core.storage import AsyncStorageBase, StoreItem
else:
    try:
        # pylint: disable=import-error,no-name-in-module
        from microsoft_agents.hosting.core.storage import AsyncStorageBase
    except ImportError:  # pragma: no cover - keeps the package importable without the optional M365 SDK.

        class AsyncStorageBase:  # pylint: disable=too-few-public-methods
            """Fallback base class used only when the M365 Agents SDK is not installed."""


StoreItemT = TypeVar("StoreItemT", bound="StoreItem")

#: Regex matching the M365 storage keys that identify a single user, so their
#: backing store gets ``user_isolation=True``. Two shapes are recognized:
#:
#: * ``"{channel}/users/{user_id}"`` -- the M365 ``UserState`` key shape (see
#:   ``microsoft_agents.hosting.core.state.user_state.UserState.get_storage_key``).
#: * ``"auth:_SignInState:{channel}:{user_id}"`` -- the M365 ``Authorization``
#:   sign-in state key shape.
_USER_SCOPED_KEY_RE = re.compile(r"/users/|^auth:_SignInState:[^:]+:.+$")

#: Upper bound on the number of per-key ``FoundryStateStore`` clients the adapter
#: keeps in its in-memory LRU cache. Once exceeded, the least-recently-used store
#: is evicted and closed; its server-side state is untouched and gets a fresh
#: client on next access. Active clients are retired and closed only after their
#: in-flight operation completes.
_MAX_CACHED_STORES = 1024

#: Maximum length the Foundry state-store backend allows for a store name (the
#: ``state_store`` field). M365 keys can exceed this -- a Microsoft Teams
#: conversation key like ``"msteams/conversations/a:1..."`` runs ~150+ chars
#: because the Teams conversation id alone is ~130 chars -- so any key longer
#: than this is shortened with a digest suffix by :func:`_bounded_store_name`.
_MAX_STORE_NAME_LEN = 128
_STORE_NAME_DIGEST_LEN = 16


@dataclass
class _StoreEntry:
    store: FoundryStateStore
    ensured: bool
    active_operations: int = 0
    retired: bool = False


def _bounded_store_name(key: str) -> str:
    """Return a deterministic, collision-resistant store name of at most 128 characters.

    The Foundry backend caps a store name (the ``state_store`` field) at
    :data:`_MAX_STORE_NAME_LEN` characters, but M365 keys (notably Microsoft
    Teams conversation keys) can be longer. When *key* fits, it is returned
    verbatim; otherwise a SHA-256 digest suffix preserves uniqueness when keys
    share a long prefix. The same value is used as both the store name and the
    single item key, so a given M365 key always resolves to the same location.

    :param key: The original M365 storage key.
    :type key: str
    :return: *key* if it fits, otherwise a prefix plus digest suffix.
    :rtype: str
    """
    if len(key) <= _MAX_STORE_NAME_LEN:
        return key
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:_STORE_NAME_DIGEST_LEN]
    prefix_length = _MAX_STORE_NAME_LEN - _STORE_NAME_DIGEST_LEN - 1
    return f"{key[:prefix_length]}-{digest}"


def _default_is_user_scoped(key: str) -> bool:
    """Match the per-user M365 key shapes.

    :param key: The M365 storage key to classify.
    :type key: str
    :return: Whether the key represents user or authorization state.
    :rtype: bool
    """
    return _USER_SCOPED_KEY_RE.search(key) is not None


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
        per-user M365 key shapes ``"{channel}/users/{user_id}"`` (``UserState``)
        and ``"auth:_SignInState:{channel}:{user_id}"`` (``Authorization``).
    """

    def __init__(
        self,
        *,
        credential: AsyncTokenCredential | None = None,
        endpoint: FoundryStorageEndpoint | str | None = None,
        item_ttl_seconds: int | None = None,
        is_user_scoped: Callable[[str], bool] = _default_is_user_scoped,
    ) -> None:
        """Create the adapter. No backing stores are created until first use.

        :keyword credential: Async token credential shared by every per-key
            store, or ``None`` to build an owned ``DefaultAzureCredential``.
        :paramtype credential: ~azure.core.credentials_async.AsyncTokenCredential | None
        :keyword endpoint: Foundry storage endpoint or project endpoint URL
            override, or ``None`` to resolve from the environment.
        :paramtype endpoint: ~azure.ai.agentserver.core.storage.FoundryStorageEndpoint | str | None
        :keyword item_ttl_seconds: Store-level TTL applied to every per-key
            store, or ``None`` to use ``FoundryStateStore``'s own default.
        :paramtype item_ttl_seconds: int | None
        :keyword is_user_scoped: Predicate deciding which keys get
            ``user_isolation=True`` on their backing store.
        :paramtype is_user_scoped: ~collections.abc.Callable[[str], bool]
        :raises ImportError: If no ``credential`` is supplied and
            ``azure-identity`` is not installed.
        :return: None.
        :rtype: None
        """
        super().__init__()
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
        self._max_cached_stores = _MAX_CACHED_STORES

        # LRU-ordered cache: most-recently-used key at the end, coldest at the front.
        self._stores: "OrderedDict[str, _StoreEntry]" = OrderedDict()
        self._creation_lock = asyncio.Lock()

    def _store_kwargs(self, key: str) -> dict[str, Any]:
        """Build the keyword arguments for the per-key backing store.

        :param key: The M365 storage key the store will be bound to.
        :type key: str
        :return: Keyword arguments for ``FoundryStateStore(key, **kwargs)`` /
            ``FoundryStateStore.get_or_create(key, **kwargs)``.
        :rtype: dict[str, ~typing.Any]
        """
        kwargs: dict[str, Any] = {
            "credential": self._credential,
            "endpoint": self._endpoint,
            "user_isolation": self._is_user_scoped(key),
        }
        if self._item_ttl_seconds is not None:
            kwargs["item_ttl_seconds"] = self._item_ttl_seconds
        return kwargs

    @asynccontextmanager
    async def _use_store(self, key: str, *, ensure_exists: bool) -> AsyncIterator[FoundryStateStore]:
        """Lease the cached per-key store, creating it on first use.

        Reads/deletes get a plain (unconfirmed) client -- ``FoundryStateStore``
        gracefully treats a not-yet-created store as a missing key/item, so no
        network round trip is needed just to look something up. Writes need
        the server-side store to actually exist, so the first write for a key
        upgrades the cache entry via :meth:`~FoundryStateStore.get_or_create`.

        :param key: The M365 storage key to resolve a store for.
        :type key: str
        :keyword ensure_exists: When ``True``, ensures the server-side store
            resource exists (once per key) before returning.
        :paramtype ensure_exists: bool
        :return: An async context manager yielding the cached store.
        :rtype: ~collections.abc.AsyncIterator[
            ~azure.ai.agentserver.core.storage.FoundryStateStore]
        """
        store_name = _bounded_store_name(key)
        _LOGGER.debug(
            "[FoundryStorage] resolving M365 storage key (ensure_exists=%s, user_isolation=%s)",
            ensure_exists,
            self._is_user_scoped(key),
        )
        async with self._creation_lock:
            entry = self._stores.get(key)
            if ensure_exists and (entry is None or not entry.ensured):
                store = await FoundryStateStore.get_or_create(store_name, **self._store_kwargs(key))
                replacement = _StoreEntry(store=store, ensured=True, active_operations=1)
                self._stores[key] = replacement
                if entry is not None:
                    await self._retire_entry(entry)
                entry = replacement
            elif entry is None:
                store = FoundryStateStore(store_name, **self._store_kwargs(key))
                entry = _StoreEntry(store=store, ensured=False, active_operations=1)
                self._stores[key] = entry
            else:
                entry.active_operations += 1
            self._stores.move_to_end(key)  # mark most-recently-used
            await self._evict_if_needed()
        try:
            yield entry.store
        finally:
            async with self._creation_lock:
                entry.active_operations -= 1
                if entry.retired and entry.active_operations == 0:
                    await entry.store.aclose()

    @staticmethod
    async def _retire_entry(entry: _StoreEntry) -> None:
        """Close an unused entry now, or defer close until its active leases finish.

        :param entry: Cache entry to retire.
        :type entry: _StoreEntry
        :return: None.
        :rtype: None
        """
        entry.retired = True
        if entry.active_operations == 0:
            await entry.store.aclose()

    async def _evict_if_needed(self) -> None:
        """Evict and close least-recently-used stores until the cache is within bounds.

        Must be called while holding ``_creation_lock``. Only ever evicts the
        coldest entries (front of the LRU order), which -- given ``max_cached_stores``
        exceeds the fan-out width of any single batch -- are never stores currently
        being read from or written to. A later access recreates the client and
        re-runs ``get_or_create`` on the next write; the server-side state
        remains untouched.

        :return: None.
        :rtype: None
        """
        while len(self._stores) > self._max_cached_stores:
            _, evicted_entry = self._stores.popitem(last=False)
            await self._retire_entry(evicted_entry)

    async def aclose(self) -> None:
        """Close every cached per-key store and an owned default credential.

        :return: None.
        :rtype: None
        """
        for entry in list(self._stores.values()):
            await self._retire_entry(entry)
        self._stores.clear()
        if self._owns_credential and hasattr(self._credential, "close"):
            await self._credential.close()

    async def __aenter__(self) -> "FoundryStorage":
        """Enter the async context manager.

        :return: This instance.
        :rtype: ~azure.ai.agentserver.activity.FoundryStorage
        """
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit the async context manager, closing all cached stores.

        :param args: The exception type, value, and traceback (unused).
        :type args: object
        :return: None.
        :rtype: None
        """
        await self.aclose()

    async def _read_item(
        self,
        key: str,
        *,
        target_cls: type[StoreItemT] | None = None,
        **kwargs: Any,
    ) -> tuple[str | None, StoreItemT | None]:
        """Fetch one item. A store that does not exist yet is just a missing key.

        :param key: The M365 storage key to read (also the store name).
        :type key: str
        :keyword target_cls: The ``StoreItem`` subclass to deserialize into.
        :paramtype target_cls: type[StoreItemT] | None
        :return: ``(key, item)`` if found, otherwise ``(None, None)``.
        :rtype: tuple[str | None, StoreItemT | None]
        """
        _ = kwargs
        async with self._use_store(key, ensure_exists=False) as store:
            item = await store.get_item(_bounded_store_name(key))
        if item is None or target_cls is None:
            return None, None
        # ``StoreItem.from_json_to_store_item`` is annotated ``-> StoreItem`` upstream, so
        # calling it through ``type[StoreItemT]`` does not narrow to the concrete subclass.
        return key, cast(StoreItemT, target_cls.from_json_to_store_item(item.value))

    async def _write_item(self, key: str, value: StoreItem) -> None:
        """Create-or-replace one item, creating its backing store on first write.

        :param key: The M365 storage key to write (also the store name).
        :type key: str
        :param value: The ``StoreItem`` to persist.
        :type value: ~microsoft_agents.hosting.core.storage.StoreItem
        :return: None.
        :rtype: None
        """
        async with self._use_store(key, ensure_exists=True) as store:
            await store.set_item(_bounded_store_name(key), value.store_item_to_json())

    async def _delete_item(self, key: str) -> None:
        """Delete one item. Missing keys (or stores) are ignored.

        :param key: The M365 storage key to delete (also the store name).
        :type key: str
        :return: None.
        :rtype: None
        """
        async with self._use_store(key, ensure_exists=False) as store:
            try:
                await store.delete_item(_bounded_store_name(key))
            except FoundryStorageNotFoundError:
                pass
