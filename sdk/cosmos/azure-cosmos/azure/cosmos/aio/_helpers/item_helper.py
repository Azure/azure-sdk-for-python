# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async version of the single-item helper.

Same behaviour and arguments as the sync helper. The option building is
shared with the sync side so the two cannot drift; what is here is the
per-call work done with ``await``.
"""
from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict, Optional

from ..._constants import _Constants as Constants
from ..._helpers._item_dispatch import (
    build_create_item_request_options,
    build_delete_item_request_options,
    build_patch_item_request_options,
    build_read_item_request_options,
    build_upsert_item_request_options,
)
from ..._helpers._request_prep import (
    build_create_item_prepared,
    build_delete_item_prepared,
    build_patch_item_prepared,
    build_read_item_prepared,
    build_replace_item_prepared,
    build_upsert_item_prepared,
)
from ..._helpers._response_parse import parse_backend_response
from ...partition_key import _Empty
from .._backend.base import AsyncCosmosBackend
from ._metadata_provider import AsyncContainerMetadataProvider

_LOGGER = logging.getLogger(__name__)


class AsyncItemHelper:
    """Async per-call logic for the single-item operations.

    See the sync helper for the full per-argument notes.
    """

    def __init__(
        self,
        backend: Optional[AsyncCosmosBackend],
        client_connection: Any,
        ensure_container_cached: Optional[Callable[[Dict[str, Any]], Awaitable[Any]]] = None,
    ) -> None:
        """Store the backend and connection this helper will use.

        :param backend: The async backend for this client. ``None`` is
            allowed only in unit tests that build the helper directly.
        :type backend: Optional[AsyncCosmosBackend]
        :param client_connection: The async connection used for the cache,
            partition-key extraction, and the fallback path.
        :type client_connection: Any
        :param ensure_container_cached: Optional async callable from the
            container. See the sync helper for the details.
        :type ensure_container_cached: Optional[Callable]
        """
        self._backend = backend
        self.client_connection = client_connection
        # Reads the container rid and partition-key definition off one container
        # read (async version of the sync provider), instead of calling the
        # connection's ``_container_properties_cache`` / ``_AddPartitionKey``
        # directly.
        self._metadata = AsyncContainerMetadataProvider(client_connection, ensure_container_cached)

    def _no_response_on_write_default(self) -> bool:
        """Read the client-level ``no_response_on_write`` setting.

        Async version of the sync helper method. The write preps fall back to
        this client-level flag when a call passes no per-call ``no_response``.

        :rtype: bool
        """
        policy = getattr(self.client_connection, "connection_policy", None)
        return bool(getattr(policy, "ResponsePayloadOnWriteDisabled", False))

    async def _resolve_container_rid(
        self,
        container_link: str,
        request_options: Dict[str, Any],
    ) -> Optional[str]:
        """Look up the container's resource id and add it to the options.

        Async version of the sync method. Best-effort: if the id cannot be
        found the request still goes out, just without the header that
        guards against a recreated container. On success the id is stored
        in the options and returned. The lookup is delegated to the async
        metadata provider; the best-effort policy stays here.
        """
        try:
            rid_value = await self._metadata.container_rid(container_link, request_options)
            if isinstance(rid_value, str):
                request_options[Constants.ContainerRID] = rid_value
                return rid_value
        except (AttributeError, KeyError, TypeError) as exc:
            # Only the stub connections used in unit tests produce these;
            # a real connection never does. A real failure from the lookup
            # is left to propagate so the caller sees it. Log this case so
            # a genuine one is visible instead of quietly skipping the
            # recreated-container guard header.
            _LOGGER.warning(
                "Could not resolve container rid for %r (%s: %s); proceeding "
                "without the intended-collection-rid header.",
                container_link,
                type(exc).__name__,
                exc,
            )
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
        """Run one async create call."""

        # Copy the arguments first. Building the options below removes the
        # recognized keywords, but the request still needs the full set.
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
                no_response_on_write_default=self._no_response_on_write_default(),
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = await self._backend.execute(prepared)
            if backend_response is not None:
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        # No backend configured: use the existing client.
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
        """Find the partition-key value to send. Async version of the sync method."""
        try:
            return await self._metadata.extract_partition_key(container_link, body, request_options)
        except (AttributeError, TypeError):
            # Only the stub connections used in unit tests reach here. A real
            # extraction error is left to propagate so a wrong partition key
            # fails loudly instead of writing to the wrong place.
            return _Empty()

    async def delete_item(
        self,
        *,
        container_link: str,
        document_link: str,
        item_id: str,
        **kwargs: Any,
    ) -> Any:
        """Run one async delete call. See the sync method for the arguments."""
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
                # Delete has no body. Run the response hook so the caller
                # can read the response headers, then return nothing.
                parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )
                return None

        # No backend configured: use the existing client.
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
        """Run one async read call. See the sync method for the arguments."""
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

        # No backend configured: use the existing client.
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
        """Run one async upsert call.

        Async version of the sync method. The async upsert has no
        populate_query_metrics flag, so ``None`` is passed for it.
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
                no_response_on_write_default=self._no_response_on_write_default(),
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = await self._backend.execute(prepared)
            if backend_response is not None:
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        # No backend configured: use the existing client.
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
        """Run one async replace call.

        Async version of the sync method. The async replace has no
        populate_query_metrics flag, so ``None`` is passed for it.
        ``item_id`` names the document to replace, not the id inside the
        body.
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
                no_response_on_write_default=self._no_response_on_write_default(),
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = await self._backend.execute(prepared)
            if backend_response is not None:
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        # No backend configured: use the existing client.
        return await self.client_connection.ReplaceItem(
            document_link=document_link,
            new_document=body,
            options=request_options,
            **kwargs,
        )

    async def patch_item(
        self,
        *,
        container_link: str,
        document_link: str,
        item_id: str,
        patch_operations: Any,
        filter_predicate: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """Run one async patch call.

        Async version of the sync method. A patch with a filter or an
        etag / match-condition guard uses the existing client; a plain
        patch uses the backend.
        """
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_patch_item_request_options(kwargs)
        if filter_predicate is not None:
            request_options["filterPredicate"] = filter_predicate

        partition_key_value = request_options.get("partitionKey", _Empty())

        container_rid = await self._resolve_container_rid(container_link, request_options)

        # Use the backend only for a plain patch. A filter or an
        # etag / match-condition guard uses the existing client below.
        backend_supports_patch = (
            self._backend is not None
            and filter_predicate is None
            and "accessCondition" not in request_options
        )
        if backend_supports_patch:
            prepared = build_patch_item_prepared(
                container_link=container_link,
                item_id=item_id,
                patch_operations=patch_operations,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                no_response_on_write_default=self._no_response_on_write_default(),
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = await self._backend.execute(prepared)
            if backend_response is not None:
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        # No backend configured (or a guarded patch): use the existing client.
        return await self.client_connection.PatchItem(
            document_link=document_link,
            operations=patch_operations,
            options=request_options,
            **kwargs,
        )
