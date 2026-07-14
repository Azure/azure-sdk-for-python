# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Developer-facing Foundry state-store client bound to one explicit store."""

# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
# pylint: disable=client-accepts-api-version-keyword

from __future__ import annotations

import base64
from collections.abc import Mapping
from typing import Any

from azure.core.credentials_async import AsyncTokenCredential
from azure.core.rest import HttpRequest

from ._client import JSON_CONTENT_TYPE, FoundryStorageClient
from ._endpoint import FoundryStorageEndpoint
from ._errors import FoundryStorageConflictError, FoundryStorageNotFoundError
from ._state_serializer import (
    DeletedStateStore,
    DeletedStateStoreItem,
    JSONObject,
    KeyPage,
    Order,
    StateStore,
    StateStoreItem,
    StateStoreItemMetadata,
    deserialize_deleted_state_item,
    deserialize_deleted_state_store,
    deserialize_list_keys_response,
    deserialize_state_item,
    deserialize_state_item_metadata,
    deserialize_state_store,
    serialize_item_create_request,
    serialize_item_put_request,
    serialize_store_create_request,
    serialize_store_update_request,
)

DEFAULT_ITEM_TTL_SECONDS = 30 * 24 * 60 * 60
_UNSET = object()


def _encode_segment(value: str) -> str:
    encoded = base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii")
    return encoded.rstrip("=")


def _validate_key(key: str) -> None:
    if not key:
        raise ValueError("key must be a non-empty string")


class FoundryStateStore(FoundryStorageClient):
    """Developer-facing client for one explicit Foundry state store.

    The instance is bound to a single caller-chosen store ``name``. Session or
    conversation scoping is expressed by encoding that identity into the store
    name itself (for example ``checkpoints/<conversation-id>``).

    Prefer :meth:`get_or_create` over the constructor: it resolves (or creates)
    the store's server-side resource in one call, so you never need a separate
    lifecycle step before reading or writing items::

        store = await FoundryStateStore.get_or_create("checkpoints/thread-abc")
        await store.set_item("step-1", {"done": False})

    Store-level operations (:meth:`get`, :meth:`update`, :meth:`delete`) act on
    the bound store itself. The explicit ``*_item`` methods
    (:meth:`create_item`, :meth:`get_item`, :meth:`set_item`,
    :meth:`delete_item`, :meth:`list_keys`) act on individual items within it.
    """

    def __init__(
        self,
        name: str,
        credential: AsyncTokenCredential | None = None,
        endpoint: FoundryStorageEndpoint | str | None = None,
        *,
        user_isolation: bool = False,
        item_ttl_seconds: int = DEFAULT_ITEM_TTL_SECONDS,
        description: str | None = None,
        tags: Mapping[str, str] | None = None,
        api_version: str = "v1",
        **kwargs: Any,
    ) -> None:
        """Create a store-bound durable state-store client.

        Prefer :meth:`get_or_create`, which also resolves the server-side store
        resource; use the constructor directly only when you already know the
        store exists and want to skip that round trip.

        :param name: The logical state-store name. Encode conversation/thread
            identity into this name when you need that scope.
        :type name: str
        :param credential: Async token credential. Defaults to
            ``DefaultAzureCredential`` when omitted.
        :type credential: AsyncTokenCredential | None
        :param endpoint: Foundry storage endpoint or project endpoint URL.
        :type endpoint: FoundryStorageEndpoint | str | None
        :keyword user_isolation: Whether item operations should be partitioned
            per resolved user. Fixed at store creation; ignored if the store
            already exists.
        :paramtype user_isolation: bool
        :keyword item_ttl_seconds: Store-level default TTL inherited by every
            item. Fixed at store creation; ignored if the store already exists.
        :paramtype item_ttl_seconds: int
        :keyword description: Optional mutable store description, set at
            creation. Change it later with :meth:`update`.
        :paramtype description: str or None
        :keyword tags: Optional mutable store metadata tags, set at creation.
            Change them later with :meth:`update`.
        :paramtype tags: ~collections.abc.Mapping[str, str] or None
        :keyword api_version: Storage API version.
        :paramtype api_version: str
        :raises ValueError: If ``name`` is empty.
        """
        if not name:
            raise ValueError("name must be a non-empty string")
        self._owns_credential = False
        if credential is None:
            try:
                from azure.identity.aio import DefaultAzureCredential
            except ImportError as exc:  # pragma: no cover
                raise ImportError(
                    "FoundryStateStore requires azure-identity when no credential is supplied. "
                    "Install azure-identity or pass an async credential."
                ) from exc
            credential = DefaultAzureCredential()
            self._owns_credential = True
        self._credential = credential

        if isinstance(endpoint, FoundryStorageEndpoint):
            resolved = endpoint
        elif isinstance(endpoint, str):
            resolved = FoundryStorageEndpoint.from_endpoint(endpoint, api_version=api_version)
        else:
            resolved = FoundryStorageEndpoint.from_env(api_version=api_version)

        self._name = name
        self._user_isolation = user_isolation
        self._item_ttl_seconds = item_ttl_seconds
        self._description = description
        self._tags = {} if tags is None else dict(tags)
        super().__init__(credential, resolved, **kwargs)

    @classmethod
    async def get_or_create(
        cls,
        name: str,
        credential: AsyncTokenCredential | None = None,
        endpoint: FoundryStorageEndpoint | str | None = None,
        *,
        user_isolation: bool = False,
        item_ttl_seconds: int = DEFAULT_ITEM_TTL_SECONDS,
        description: str | None = None,
        tags: Mapping[str, str] | None = None,
        api_version: str = "v1",
        **kwargs: Any,
    ) -> "FoundryStateStore":
        """Return a client bound to *name*, creating the store if needed.

        This is the recommended entry point: it resolves the server-side store
        resource in one call (fetch, or create on first use) so callers never
        need a separate lifecycle step before reading or writing items.

        :param name: The logical state-store name. See the constructor.
        :type name: str
        :param credential: Async token credential. See the constructor.
        :type credential: AsyncTokenCredential | None
        :param endpoint: Foundry storage endpoint or project endpoint URL.
        :type endpoint: FoundryStorageEndpoint | str | None
        :keyword user_isolation: See the constructor. Only applied if the store
            does not already exist.
        :paramtype user_isolation: bool
        :keyword item_ttl_seconds: See the constructor. Only applied if the
            store does not already exist.
        :paramtype item_ttl_seconds: int
        :keyword description: See the constructor. Only applied if the store
            does not already exist.
        :paramtype description: str or None
        :keyword tags: See the constructor. Only applied if the store does not
            already exist.
        :paramtype tags: ~collections.abc.Mapping[str, str] or None
        :keyword api_version: Storage API version.
        :paramtype api_version: str
        :return: The bound, ready-to-use store client.
        :rtype: FoundryStateStore
        """
        store = cls(
            name,
            credential,
            endpoint,
            user_isolation=user_isolation,
            item_ttl_seconds=item_ttl_seconds,
            description=description,
            tags=tags,
            api_version=api_version,
            **kwargs,
        )
        try:
            await store._fetch_properties()
        except FoundryStorageNotFoundError:
            try:
                await store._create_properties()
            except FoundryStorageConflictError:
                await store._fetch_properties()
        return store

    async def aclose(self) -> None:
        """Close the pipeline client and any owned default credential."""
        await super().aclose()
        if self._owns_credential and hasattr(self._credential, "close"):
            await self._credential.close()

    @property
    def name(self) -> str:
        """Return the logical store name bound to this client."""
        return self._name

    def _store_path(self) -> str:
        return f"state_stores/{_encode_segment(self._name)}"

    def _item_path(self, key: str) -> str:
        _validate_key(key)
        return f"{self._store_path()}/items/{_encode_segment(key)}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        content: bytes | None = None,
        if_match: str | None = None,
        **query: str,
    ) -> HttpRequest:
        headers: dict[str, str] = {}
        if content is not None:
            headers["Content-Type"] = JSON_CONTENT_TYPE
        if if_match is not None:
            headers["If-Match"] = if_match
        return HttpRequest(method, self._endpoint.build_url(path, **query), content=content, headers=headers)

    async def _create_properties(self) -> StateStore:
        body = serialize_store_create_request(
            self._name,
            user_isolation=self._user_isolation,
            item_ttl_seconds=self._item_ttl_seconds,
            description=self._description,
            tags=self._tags,
        )
        response = await self._send_storage_request(self._request("POST", "state_stores", content=body))
        return deserialize_state_store(response.text())

    async def _fetch_properties(self) -> StateStore:
        response = await self._send_storage_request(self._request("GET", self._store_path()))
        return deserialize_state_store(response.text())

    async def update(
        self,
        *,
        description: str | None | object = _UNSET,
        tags: Mapping[str, str] | None | object = _UNSET,
    ) -> StateStore:
        """Update the bound store's mutable metadata (``description`` / ``tags``).

        :keyword description: The new description, or ``None`` to clear it.
            Omit to leave the description unchanged.
        :paramtype description: str or None
        :keyword tags: The new tags (replaces the existing set wholesale), or
            ``None`` to clear them. Omit to leave the tags unchanged.
        :paramtype tags: ~collections.abc.Mapping[str, str] or None
        :return: The updated store descriptor.
        :rtype: ~azure.ai.agentserver.core.storage.StateStore
        """
        body = serialize_store_update_request(description, tags)
        response = await self._send_storage_request(self._request("PATCH", self._store_path(), content=body))
        if description is not _UNSET:
            self._description = (
                description if isinstance(description, str) or description is None else self._description
            )
        if tags is not _UNSET:
            self._tags = dict(tags) if isinstance(tags, Mapping) else {}
        return deserialize_state_store(response.text())

    async def create_item(
        self,
        key: str,
        value: JSONObject,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> StateStoreItemMetadata:
        """Create a new item and fail on duplicate keys."""
        body = serialize_item_create_request(key, value, tags)
        response = await self._send_storage_request(self._request("POST", f"{self._store_path()}/items", content=body))
        return deserialize_state_item_metadata(response.text())

    async def set_item(
        self,
        key: str,
        value: JSONObject,
        *,
        tags: Mapping[str, str] | None = None,
        if_match: str | None = None,
        require_exists: bool = False,
    ) -> StateStoreItemMetadata:
        """Create or replace one item by key."""
        if if_match is not None and require_exists:
            raise ValueError("if_match and require_exists are mutually exclusive")
        body = serialize_item_put_request(value, tags)
        header = "*" if require_exists else if_match
        response = await self._send_storage_request(
            self._request(
                "PUT",
                self._item_path(key),
                content=body,
                if_match=header,
            )
        )
        return deserialize_state_item_metadata(response.text())

    async def get(self) -> StateStore | None:
        """Fetch the bound store's own descriptor.

        :return: The store descriptor, or ``None`` if the store does not exist.
        :rtype: ~azure.ai.agentserver.core.storage.StateStore or None
        """
        try:
            return await self._fetch_properties()
        except FoundryStorageNotFoundError:
            return None

    async def get_item(self, key: str) -> StateStoreItem | None:
        """Fetch one item by key.

        :param key: The item key to fetch.
        :type key: str
        :return: The item, or ``None`` if it does not exist.
        :rtype: ~azure.ai.agentserver.core.storage.StateStoreItem or None
        """
        try:
            response = await self._send_storage_request(self._request("GET", self._item_path(key)))
        except FoundryStorageNotFoundError:
            return None
        return deserialize_state_item(response.text())

    async def delete(self) -> DeletedStateStore:
        """Delete the bound store, cascading to every item under it.

        :return: The deleted-store marker.
        :rtype: ~azure.ai.agentserver.core.storage.DeletedStateStore
        """
        response = await self._send_storage_request(self._request("DELETE", self._store_path()))
        return deserialize_deleted_state_store(response.text())

    async def delete_item(self, key: str, *, if_match: str | None = None) -> DeletedStateStoreItem:
        """Delete one item by key.

        :param key: The item key to delete.
        :type key: str
        :keyword if_match: Optional concurrency token.
        :paramtype if_match: str or None
        :return: The deleted-item marker.
        :rtype: ~azure.ai.agentserver.core.storage.DeletedStateStoreItem
        """
        response = await self._send_storage_request(self._request("DELETE", self._item_path(key), if_match=if_match))
        return deserialize_deleted_state_item(response.text())

    async def list_keys(
        self,
        *,
        tags: Mapping[str, str] | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        order: Order = "desc",
    ) -> KeyPage:
        """List keys within the bound store."""
        if after is not None and before is not None:
            raise ValueError("after and before are mutually exclusive")
        query: dict[str, str] = {}
        if tags is not None:
            for key, value in tags.items():
                query[f"tags.{key}"] = value
        if limit is not None:
            query["limit"] = str(limit)
        if after is not None:
            query["after"] = after
        if before is not None:
            query["before"] = before
        query["order"] = order
        response = await self._send_storage_request(self._request("GET", f"{self._store_path()}/items:keys", **query))
        return deserialize_list_keys_response(response.text())
