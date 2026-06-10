# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async sibling of ``azure.cosmos._helpers.item_helper.ItemHelper``.

Same behaviour, parameter contract, dispatch rules, and option-build
sequence as the sync sibling. The option-build is imported from the
shared ``_item_dispatch`` module so the two cannot drift; what remains
here is the per-call I/O wired with ``await``.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional

from ..._constants import _Constants as Constants
from ..._helpers._item_dispatch import (
    build_create_item_request_options,
    build_delete_item_request_options,
    build_read_item_request_options,
    build_upsert_item_request_options,
)
from ..._helpers._request_prep import (
    build_create_item_prepared,
    build_delete_item_prepared,
    build_read_item_prepared,
    build_replace_item_prepared,
    build_upsert_item_prepared,
)
from ..._helpers._response_parse import parse_backend_response
from ...partition_key import _Empty
from .._backend.base import AsyncCosmosBackend


class AsyncItemHelper:
    """Async per-call helper for ``Container.create_item``,
    ``Container.read_item``, ``Container.delete_item``, and
    ``Container.upsert_item``.

    See the sync sibling ``azure.cosmos._helpers.item_helper.ItemHelper``
    for the design rationale and the per-parameter docs.
    """

    def __init__(
        self,
        backend: Optional[AsyncCosmosBackend],
        client_connection: Any,
        ensure_container_cached: Optional[Callable[[Dict[str, Any]], Awaitable[Any]]] = None,
    ) -> None:
        """Bind the async helper to the chosen backend and the connection.

        :param backend: The async backend the wiring function picked
            for this client. ``None`` is permitted only for unit tests
            that build the helper without going through the async
            ``CosmosClient``.
        :type backend: Optional[AsyncCosmosBackend]
        :param client_connection: The async ``CosmosClientConnection``
            from ``azure.cosmos.aio``. The helper awaits its
            ``CreateItem`` and ``_refresh_container_properties_cache``.
        :type client_connection: Any
        :param ensure_container_cached: Optional async callable the
            container proxy passes in. See the sync sibling for the
            full rationale.
        :type ensure_container_cached: Optional[Callable]
        """
        self._backend = backend
        self.client_connection = client_connection
        self._ensure_container_cached = ensure_container_cached

    async def _resolve_container_rid(
        self,
        container_link: str,
        request_options: Dict[str, Any],
    ) -> Optional[str]:
        """Async sibling of ``ItemHelper._resolve_container_rid``.

        Shared by all five ops. Best-effort: on any failure returns
        ``None`` and lets the backend run without the
        intended-collection-rid header. On success writes the rid to
        ``request_options`` (under ``Constants.ContainerRID``) and returns
        it.
        """
        try:
            if self._ensure_container_cached is not None:
                await self._ensure_container_cached(request_options)
            else:
                cache = self.client_connection._container_properties_cache
                if container_link not in cache:
                    await self.client_connection._refresh_container_properties_cache(container_link)
            cached = self.client_connection._container_properties_cache[container_link]
            rid_value = cached.get("_rid") if isinstance(cached, dict) else None
            if isinstance(rid_value, str):
                request_options[Constants.ContainerRID] = rid_value
                return rid_value
        except Exception:  # pylint: disable=broad-except
            pass
        return None

    async def create_item(
        self,
        *,
        container_link: str,
        body: Dict[str, Any],
        indexing_directive: Optional[int] = None,
        enable_automatic_id_generation: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Run a single async ``create_item`` call end to end."""

        # Snapshot kwargs before the legacy options build pops them.
        # See the sync sibling for the full rationale. Without this
        # snapshot, recognised kwargs (pre_trigger_include, no_response,
        # priority, etc.) never reach the binding.
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_create_item_request_options(
            kwargs,
            enable_automatic_id_generation=enable_automatic_id_generation,
            indexing_directive=indexing_directive,
            populate_query_metrics=None,
        )

        container_rid = await self._resolve_container_rid(container_link, request_options)

        if self._backend is not None:
            partition_key_value = await self._extract_partition_key_value(
                container_link, body, request_options
            )
            prepared, _item_id = build_create_item_prepared(
                container_link=container_link,
                body=body,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                enable_automatic_id_generation=enable_automatic_id_generation,
                indexing_directive=indexing_directive,
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = await self._backend.execute(prepared)
            if backend_response is not None:
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        return await self.client_connection.CreateItem(
            database_or_container_link=container_link,
            document=body,
            options=request_options,
            **kwargs,
        )

    async def _extract_partition_key_value(
        self,
        container_link: str,
        body: Dict[str, Any],
        request_options: Dict[str, Any],
    ) -> Any:
        """Async sibling of the sync helper's PK extraction. See sync docstring."""
        if "partitionKey" in request_options:
            return request_options["partitionKey"]
        try:
            new_options = await self.client_connection._AddPartitionKey(
                container_link, body, request_options
            )
            if isinstance(new_options, dict):
                request_options.update(new_options)
                return new_options.get("partitionKey", _Empty())
        except Exception:  # pylint: disable=broad-except
            pass
        return _Empty()

    async def delete_item(
        self,
        *,
        container_link: str,
        document_link: str,
        item_id: str,
        **kwargs: Any,
    ) -> Any:
        """Async sibling of ``ItemHelper.delete_item``. See sync docstring."""
        kwargs_for_rust_prep = dict(kwargs)
        request_options = build_delete_item_request_options(kwargs)
        partition_key_value = request_options.get("partitionKey", _Empty())

        container_rid = await self._resolve_container_rid(container_link, request_options)

        if self._backend is not None:
            prepared = build_delete_item_prepared(
                container_link=container_link,
                item_id=item_id,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = await self._backend.execute(prepared)
            if backend_response is not None:
                parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )
                return None

        return await self.client_connection.DeleteItem(
            document_link=document_link,
            options=request_options,
            **kwargs,
        )

    async def read_item(
        self,
        *,
        container_link: str,
        document_link: str,
        item_id: str,
        **kwargs: Any,
    ) -> Any:
        """Async sibling of ``ItemHelper.read_item``. See sync docstring."""
        kwargs_for_rust_prep = dict(kwargs)
        request_options = build_read_item_request_options(kwargs)
        partition_key_value = request_options.get("partitionKey", _Empty())

        container_rid = await self._resolve_container_rid(container_link, request_options)

        if self._backend is not None:
            prepared = build_read_item_prepared(
                container_link=container_link,
                item_id=item_id,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = await self._backend.execute(prepared)
            if backend_response is not None:
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        return await self.client_connection.ReadItem(
            document_link=document_link,
            options=request_options,
            **kwargs,
        )

    async def upsert_item(
        self,
        *,
        container_link: str,
        body: Dict[str, Any],
        **kwargs: Any,
    ) -> Any:
        """Async sibling of ``ItemHelper.upsert_item``. See sync docstring.

        The async public ``upsert_item`` never exposed
        ``populate_query_metrics``, so this helper passes ``None`` for it
        (the sync sibling threads the deprecated sync-only flag through).
        """
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_upsert_item_request_options(
            kwargs,
            populate_query_metrics=None,
        )

        container_rid = await self._resolve_container_rid(container_link, request_options)

        if self._backend is not None:
            partition_key_value = await self._extract_partition_key_value(
                container_link, body, request_options
            )
            prepared = build_upsert_item_prepared(
                container_link=container_link,
                body=body,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                access_condition=request_options.get("accessCondition"),
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = await self._backend.execute(prepared)
            if backend_response is not None:
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        return await self.client_connection.UpsertItem(
            database_or_container_link=container_link,
            document=body,
            options=request_options,
            **kwargs,
        )

    async def replace_item(
        self,
        *,
        container_link: str,
        document_link: str,
        item_id: str,
        body: Dict[str, Any],
        **kwargs: Any,
    ) -> Any:
        """Async sibling of ``ItemHelper.replace_item``. See sync docstring.

        The async public ``replace_item`` never exposed
        ``populate_query_metrics``, so this helper passes ``None`` for it
        (the sync sibling threads the deprecated sync-only flag through).
        ``item_id`` (resolved from ``item``) is what the binding puts in the
        wire URL, not the body's own id.
        """
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_upsert_item_request_options(
            kwargs,
            populate_query_metrics=None,
        )

        container_rid = await self._resolve_container_rid(container_link, request_options)

        if self._backend is not None:
            partition_key_value = await self._extract_partition_key_value(
                container_link, body, request_options
            )
            prepared = build_replace_item_prepared(
                container_link=container_link,
                body=body,
                item_id=item_id,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                access_condition=request_options.get("accessCondition"),
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = await self._backend.execute(prepared)
            if backend_response is not None:
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        return await self.client_connection.ReplaceItem(
            document_link=document_link,
            new_document=body,
            options=request_options,
            **kwargs,
        )

