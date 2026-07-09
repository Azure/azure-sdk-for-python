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
    JSONObject,
    KeyPage,
    Order,
    StateItem,
    StateItemMetadata,
    StateStoreInfo,
    DeletedStateItem,
    DeletedStateStore,
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
DELEGATED_USER_ID_HEADER = "x-ms-user-id"
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
    name itself (for example ``checkpoints/<conversation-id>``), matching spec
    PR 247's removal of built-in session isolation.
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
        user_id: str | None = None,
        api_version: str = "v1",
        **kwargs: Any,
    ) -> None:
        """Create a store-bound durable state-store client.

        :param name: The logical state-store name. Encode conversation/thread
            identity into this name when you need that scope.
        :type name: str
        :param credential: Async token credential. Defaults to
            ``DefaultAzureCredential`` when omitted.
        :type credential: AsyncTokenCredential | None
        :param endpoint: Foundry storage endpoint or project endpoint URL.
        :type endpoint: FoundryStorageEndpoint | str | None
        :keyword user_isolation: Whether item operations should be partitioned
            per resolved user.
        :paramtype user_isolation: bool
        :keyword item_ttl_seconds: Store-level default TTL inherited by every
            item.
        :paramtype item_ttl_seconds: int
        :keyword description: Optional mutable store description.
        :paramtype description: str or None
        :keyword tags: Optional mutable store metadata tags.
        :paramtype tags: ~collections.abc.Mapping[str, str] or None
        :keyword user_id: Delegated end-user identity for trusted callers.
        :paramtype user_id: str or None
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
        self._user_id = user_id
        super().__init__(credential, resolved, **kwargs)

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
        return f"statestores/{_encode_segment(self._name)}"

    def _item_path(self, key: str) -> str:
        _validate_key(key)
        return f"{self._store_path()}/items/{_encode_segment(key)}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        content: bytes | None = None,
        include_user_id: bool = False,
        if_match: str | None = None,
        **query: str,
    ) -> HttpRequest:
        headers: dict[str, str] = {}
        if content is not None:
            headers["Content-Type"] = JSON_CONTENT_TYPE
        if include_user_id and self._user_id is not None:
            headers[DELEGATED_USER_ID_HEADER] = self._user_id
        if if_match is not None:
            headers["If-Match"] = if_match
        return HttpRequest(method, self._endpoint.build_url(path, **query), content=content, headers=headers)

    async def create(self) -> StateStoreInfo:
        """Create the bound store resource."""
        body = serialize_store_create_request(
            self._name,
            user_isolation=self._user_isolation,
            item_ttl_seconds=self._item_ttl_seconds,
            description=self._description,
            tags=self._tags,
        )
        response = await self._send_storage_request(self._request("POST", "statestores", content=body))
        return deserialize_state_store(response.text())

    async def create_or_get(self) -> StateStoreInfo:
        """Create the bound store resource, or fetch it when it already exists."""
        try:
            return await self.create()
        except FoundryStorageConflictError:
            return await self.get_properties()

    async def get_or_create(self) -> StateStoreInfo:
        """Fetch the bound store resource, or create it when it does not exist."""
        try:
            return await self.get_properties()
        except FoundryStorageNotFoundError:
            try:
                return await self.create()
            except FoundryStorageConflictError:
                return await self.get_properties()

    async def get_properties(self) -> StateStoreInfo:
        """Fetch the bound store descriptor."""
        response = await self._send_storage_request(self._request("GET", self._store_path()))
        return deserialize_state_store(response.text())

    async def update_metadata(
        self,
        *,
        description: str | None | object = _UNSET,
        tags: Mapping[str, str] | None | object = _UNSET,
    ) -> StateStoreInfo:
        """Update mutable store metadata on the bound store."""
        body = serialize_store_update_request(description, tags)
        response = await self._send_storage_request(self._request("PATCH", self._store_path(), content=body))
        if description is not _UNSET:
            self._description = description if isinstance(description, str) or description is None else self._description
        if tags is not _UNSET:
            self._tags = {} if tags is None else dict(tags)
        return deserialize_state_store(response.text())

    async def delete_store(self) -> DeletedStateStore:
        """Delete the bound store and cascade-delete its items."""
        response = await self._send_storage_request(self._request("DELETE", self._store_path()))
        return deserialize_deleted_state_store(response.text())

    async def create_item(self, key: str, value: JSONObject, *, tags: Mapping[str, str] | None = None) -> StateItemMetadata:
        """Create a new item and fail on duplicate keys."""
        body = serialize_item_create_request(key, value, tags)
        response = await self._send_storage_request(
            self._request("POST", f"{self._store_path()}/items", content=body, include_user_id=True)
        )
        return deserialize_state_item_metadata(response.text())

    async def set(
        self,
        key: str,
        value: JSONObject,
        *,
        tags: Mapping[str, str] | None = None,
        if_match: str | None = None,
        require_exists: bool = False,
    ) -> StateItemMetadata:
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
                include_user_id=True,
                if_match=header,
            )
        )
        return deserialize_state_item_metadata(response.text())

    async def get(self, key: str) -> StateItem | None:
        """Fetch one item by key, returning ``None`` when it is absent."""
        try:
            response = await self._send_storage_request(self._request("GET", self._item_path(key), include_user_id=True))
        except FoundryStorageNotFoundError:
            return None
        return deserialize_state_item(response.text())

    async def delete(self, key: str, *, if_match: str | None = None) -> DeletedStateItem:
        """Delete one item by key."""
        response = await self._send_storage_request(
            self._request("DELETE", self._item_path(key), include_user_id=True, if_match=if_match)
        )
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
        response = await self._send_storage_request(
            self._request("GET", f"{self._store_path()}/items:keys", include_user_id=True, **query)
        )
        return deserialize_list_keys_response(response.text())
