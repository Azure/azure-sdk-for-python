# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Developer-facing Foundry state-store client bound to one explicit store."""

# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
# pylint: disable=client-accepts-api-version-keyword

from __future__ import annotations

import base64
import json
from collections.abc import Mapping
from typing import Any, overload

from azure.core.credentials_async import AsyncTokenCredential
from azure.core.rest import HttpRequest

from azure.ai.agentserver.core._request_context import get_request_context

from ._client import JSON_CONTENT_TYPE, FoundryStorageClient
from ._endpoint import FoundryStorageEndpoint
from ._errors import FoundryStorageConflictError, FoundryStorageNotFoundError
from ._state_serializer import (
    CreateItemRequest,
    CreateStateStoreRequest,
    DeletedStateStore,
    DeletedStateStoreItem,
    JSONObject,
    KeyPage,
    Order,
    PutItemRequest,
    StateStore,
    StateStoreItem,
    StateStoreItemMetadata,
    UpdateStateStoreRequest,
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


def _resolve_create_options(
    *,
    user_isolation: bool,
    item_ttl_seconds: int,
    description: str | None,
    tags: Mapping[str, str] | None,
    options: CreateStateStoreRequest | None,
) -> tuple[bool, int, str | None, Mapping[str, str] | None]:
    """Reconcile the scattered creation keywords with an optional typed ``options`` request.

    ``options`` is a convenience alternative to passing ``user_isolation`` /
    ``item_ttl_seconds`` / ``description`` / ``tags`` individually; the two
    are mutually exclusive. ``options.name`` is ignored -- the store's name
    always comes from this client's required ``name`` parameter, not from
    the request object.
    """
    if options is None:
        return user_isolation, item_ttl_seconds, description, tags
    if user_isolation or item_ttl_seconds != DEFAULT_ITEM_TTL_SECONDS or description is not None or tags is not None:
        raise ValueError(
            "options is mutually exclusive with user_isolation/item_ttl_seconds/description/tags; "
            "set those fields on options instead."
        )
    return (
        options.user_isolation if options.user_isolation is not None else False,
        options.item_ttl_seconds if options.item_ttl_seconds is not None else DEFAULT_ITEM_TTL_SECONDS,
        options.description,
        options.tags,
    )


def _resolve_tags_option(
    tags: Mapping[str, str] | None,
    options: CreateItemRequest | PutItemRequest | None,
) -> Mapping[str, str] | None:
    """Reconcile the ``tags`` keyword with an optional typed ``options`` request.

    Only ``options.tags`` is read here; ``options.key`` / ``options.value``
    (present on ``CreateItemRequest`` / ``PutItemRequest``) are ignored --
    ``key`` and ``value`` always come from the method's own required
    parameters, not from the request object.
    """
    if options is None:
        return tags
    if tags is not None:
        raise ValueError("tags and options are mutually exclusive; set tags on options instead.")
    return options.tags


class FoundryStateStore(FoundryStorageClient):
    """Developer-facing client for one explicit Foundry state store.

    The instance is bound to a single caller-chosen store ``name``. Session or
    conversation scoping is expressed by encoding that identity into the store
    name itself (for example ``checkpoints/<conversation-id>``).

    Prefer :meth:`get_or_create` over the constructor: it resolves (or creates)
    the store's server-side resource in one call, so you never need a separate
    lifecycle step before reading or writing items::

        store = await FoundryStateStore.get_or_create("checkpoints/thread-abc")
        await store.set("step-1", {"done": False})

    ``get`` and ``delete`` are overloaded on whether *key* is supplied: with no
    *key* they act on the store itself (its descriptor, or the whole store
    cascade-deleted); with a *key* they act on one item within it.
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
        options: CreateStateStoreRequest | None = None,
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
        :keyword options: A typed ``CreateStateStoreRequest`` bundling
            ``user_isolation`` / ``item_ttl_seconds`` / ``description`` /
            ``tags`` in one object, as an alternative to passing them
            individually. Mutually exclusive with those keywords;
            ``options.name`` is ignored (``name`` above always wins).
        :paramtype options: ~azure.ai.agentserver.core.storage.CreateStateStoreRequest or None
        :keyword api_version: Storage API version.
        :paramtype api_version: str
        :raises ValueError: If ``name`` is empty, or if both ``options`` and
            one of ``user_isolation`` / ``item_ttl_seconds`` / ``description``
            / ``tags`` are supplied.
        """
        if not name:
            raise ValueError("name must be a non-empty string")
        user_isolation, item_ttl_seconds, description, tags = _resolve_create_options(
            user_isolation=user_isolation,
            item_ttl_seconds=item_ttl_seconds,
            description=description,
            tags=tags,
            options=options,
        )
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
        options: CreateStateStoreRequest | None = None,
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
        :keyword options: See the constructor. Only applied if the store does
            not already exist.
        :paramtype options: ~azure.ai.agentserver.core.storage.CreateStateStoreRequest or None
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
            options=options,
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
        include_user_id: bool = False,
        if_match: str | None = None,
        **query: str,
    ) -> HttpRequest:
        headers: dict[str, str] = {}
        if content is not None:
            headers["Content-Type"] = JSON_CONTENT_TYPE
        if include_user_id:
            # x-ms-user-id is a per-request delegation header, not a store-level
            # setting: it must reflect the caller resolved for *this* request
            # (azure.ai.agentserver.core's request-scoped platform context),
            # not a value fixed when this (possibly long-lived, reused) client
            # was constructed.
            user_id = get_request_context().user_id
            if user_id is not None:
                headers[DELEGATED_USER_ID_HEADER] = user_id
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
        options: UpdateStateStoreRequest | None = None,
    ) -> StateStore:
        """Update the bound store's mutable metadata (``description`` / ``tags``).

        :keyword description: The new description, or ``None`` to clear it.
            Omit to leave the description unchanged.
        :paramtype description: str or None
        :keyword tags: The new tags (replaces the existing set wholesale), or
            ``None`` to clear them. Omit to leave the tags unchanged.
        :paramtype tags: ~collections.abc.Mapping[str, str] or None
        :keyword options: A typed ``UpdateStateStoreRequest`` bundling
            ``description`` / ``tags`` in one object, as an alternative to
            passing them individually. A field's *absence* from ``options``
            (not just a ``None`` value) means "leave unchanged", matching
            ``description`` / ``tags``'s own unset-vs-null semantics -- build
            ``options`` via its mapping constructor (for example
            ``UpdateStateStoreRequest({"tags": None})``) to clear a field, or
            omit the key to leave it unchanged. Mutually exclusive with
            ``description`` / ``tags``.
        :paramtype options: ~azure.ai.agentserver.core.storage.UpdateStateStoreRequest or None
        :return: The updated store descriptor.
        :rtype: ~azure.ai.agentserver.core.storage.StateStore
        :raises ValueError: If both ``options`` and ``description`` / ``tags``
            are supplied.
        """
        if options is not None:
            if description is not _UNSET or tags is not _UNSET:
                raise ValueError("options is mutually exclusive with description/tags; set fields on options instead.")
            body = json.dumps(dict(options)).encode("utf-8")
            response = await self._send_storage_request(self._request("PATCH", self._store_path(), content=body))
            if "description" in options:
                self._description = options.description
            if "tags" in options:
                self._tags = dict(options.tags) if options.tags else {}
            return deserialize_state_store(response.text())

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
        options: CreateItemRequest | None = None,
    ) -> StateStoreItemMetadata:
        """Create a new item and fail on duplicate keys.

        :keyword options: A typed ``CreateItemRequest`` as an alternative to
            ``tags`` (only ``options.tags`` is read; ``key`` / ``value`` above
            always win). Mutually exclusive with ``tags``.
        :paramtype options: ~azure.ai.agentserver.core.storage.CreateItemRequest or None
        """
        tags = _resolve_tags_option(tags, options)
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
        options: PutItemRequest | None = None,
    ) -> StateStoreItemMetadata:
        """Create or replace one item by key.

        :keyword options: A typed ``PutItemRequest`` as an alternative to
            ``tags`` (only ``options.tags`` is read; ``key`` / ``value`` above
            always win). Mutually exclusive with ``tags``.
        :paramtype options: ~azure.ai.agentserver.core.storage.PutItemRequest or None
        """
        if if_match is not None and require_exists:
            raise ValueError("if_match and require_exists are mutually exclusive")
        tags = _resolve_tags_option(tags, options)
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

    @overload
    async def get(self, key: None = None) -> StateStore | None: ...
    @overload
    async def get(self, key: str) -> StateStoreItem | None: ...
    async def get(self, key: str | None = None) -> StateStoreItem | StateStore | None:
        """Fetch the bound store's own descriptor, or one item by key.

        :param key: The item key to fetch, or ``None`` (the default) to fetch
            the bound store's own descriptor instead.
        :type key: str or None
        :return: The store descriptor (``key=None``) or the item (``key=<key>``),
            or ``None`` if it does not exist.
        :rtype: ~azure.ai.agentserver.core.storage.StateStore or
            ~azure.ai.agentserver.core.storage.StateStoreItem or None
        """
        if key is None:
            try:
                return await self._fetch_properties()
            except FoundryStorageNotFoundError:
                return None
        try:
            response = await self._send_storage_request(
                self._request("GET", self._item_path(key), include_user_id=True)
            )
        except FoundryStorageNotFoundError:
            return None
        return deserialize_state_item(response.text())

    @overload
    async def delete(self, key: None = None, *, if_match: str | None = None) -> DeletedStateStore: ...
    @overload
    async def delete(self, key: str, *, if_match: str | None = None) -> DeletedStateStoreItem: ...
    async def delete(
        self, key: str | None = None, *, if_match: str | None = None
    ) -> DeletedStateStoreItem | DeletedStateStore:
        """Delete the bound store (cascades to every item), or one item by key.

        :param key: The item key to delete, or ``None`` (the default) to
            delete the bound store itself, cascading to every item under it.
        :type key: str or None
        :keyword if_match: Optional concurrency token. Only meaningful for a
            single-item delete (``key`` supplied); ignored for a store delete.
        :paramtype if_match: str or None
        :return: The deleted-store marker (``key=None``) or the deleted-item
            marker (``key=<key>``).
        :rtype: ~azure.ai.agentserver.core.storage.DeletedStateStore or
            ~azure.ai.agentserver.core.storage.DeletedStateStoreItem
        """
        if key is None:
            response = await self._send_storage_request(self._request("DELETE", self._store_path()))
            return deserialize_deleted_state_store(response.text())
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
