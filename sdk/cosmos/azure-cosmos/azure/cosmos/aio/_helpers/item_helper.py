# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async version of the single-item helper.

Same behaviour and arguments as the sync helper. The option building is
shared with the sync side so the two cannot diverge; what is here is the
per-call work done with ``await``.
"""
from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict, Optional

from ..._backend.base import (
    OP_CREATE_ITEM,
    OP_DELETE_ITEM,
    OP_PATCH_ITEM,
    OP_READ_ITEM,
    OP_REPLACE_ITEM,
    OP_UPSERT_ITEM,
)
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
from .._backend.base import (
    AsyncCosmosBackend,
    BackendResponse,
    LegacyOperation,
    PreparedRequest,
)
from .._backend.legacy import coerce_async_backend
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

        :param backend: The selected async backend, or ``None`` for core-python.
            Coerced to an explicit backend (never ``None``) via
            :func:`~azure.cosmos.aio._backend.legacy.coerce_async_backend`,
            so each op below runs through one interface and never branches on
            ``None``.
        :type backend: Optional[AsyncCosmosBackend]
        :param client_connection: The async connection used for the cache,
            partition-key extraction, and the legacy path.
        :type client_connection: Any
        :param ensure_container_cached: Optional async callable from the
            container. See the sync helper for the details.
        :type ensure_container_cached: Optional[Callable]
        """
        self._backend = coerce_async_backend(backend)
        self.client_connection = client_connection
        # Reads the container rid and partition-key definition off one container
        # read (async version of the sync provider), instead of calling the
        # connection's ``_container_properties_cache`` / ``_AddPartitionKey``
        # directly.
        self._metadata = AsyncContainerMetadataProvider(client_connection, ensure_container_cached)

    async def _run_item_operation(
        self,
        *,
        op: str,
        build_prepared: Callable[[], Awaitable[PreparedRequest]],
        run_legacy: Callable[[], Awaitable[Any]],
        response_hook: Optional[Callable[..., Any]],
        discard_result: bool = False,
        rust_eligible: bool = True,
    ) -> Any:
        """Drive one async item op through the backend and return the result.

        Async twin of the sync helper's ``_run_item_operation``: wraps
        :meth:`~azure.cosmos.aio._backend.base.AsyncCosmosBackend.run_operation`
        with the rust-response parsing common to every op. ``parse_response`` is
        synchronous (matching the async helper's existing call to
        ``parse_backend_response``); ``build_prepared`` and ``run_legacy`` are
        awaitable and awaited behind the interface. ``run_legacy`` is wrapped in
        a :class:`~azure.cosmos._backend.base.LegacyOperation` -- a small, named,
        typed request/context, not a bare callable -- before it crosses into the
        backend; see the sync helper / that class for the full rationale.
        """
        def parse_response(response: BackendResponse) -> Any:
            parsed = parse_backend_response(
                response,
                client_connection=self.client_connection,
                response_hook=response_hook,
            )
            return None if discard_result else parsed

        return await self._backend.run_operation(
            build_prepared=build_prepared,
            legacy_operation=LegacyOperation(op=op, invoke=run_legacy),
            parse_response=parse_response,
            rust_eligible=rust_eligible,
        )

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

        async def build_prepared() -> Any:
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
            return prepared

        return await self._run_item_operation(
            op=OP_CREATE_ITEM,
            build_prepared=build_prepared,
            run_legacy=lambda: self.client_connection.CreateItem(
                database_or_container_link=container_link,
                document=body,
                options=request_options,
                **kwargs,
            ),
            response_hook=kwargs.get("response_hook"),
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
            # raises instead of writing to the wrong place.
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

        async def build_prepared() -> Any:
            return build_delete_item_prepared(
                container_link=container_link,
                item_id=item_id,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                kwargs=kwargs_for_rust_prep,
            )

        return await self._run_item_operation(
            op=OP_DELETE_ITEM,
            build_prepared=build_prepared,
            run_legacy=lambda: self.client_connection.DeleteItem(
                document_link=document_link,
                options=request_options,
                **kwargs,
            ),
            response_hook=kwargs.get("response_hook"),
            # Delete has no body. Parse the rust response for its side effects
            # (response hook + last_response_headers) but return nothing.
            discard_result=True,
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

        async def build_prepared() -> Any:
            return build_read_item_prepared(
                container_link=container_link,
                item_id=item_id,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                kwargs=kwargs_for_rust_prep,
            )

        return await self._run_item_operation(
            op=OP_READ_ITEM,
            build_prepared=build_prepared,
            run_legacy=lambda: self.client_connection.ReadItem(
                document_link=document_link,
                options=request_options,
                **kwargs,
            ),
            response_hook=kwargs.get("response_hook"),
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

        async def build_prepared() -> Any:
            partition_key_value = await self._extract_partition_key_value(
                container_link, body, request_options
            )
            return build_upsert_item_prepared(
                container_link=container_link,
                body=body,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                access_condition=request_options.get("accessCondition"),
                no_response_on_write_default=self._no_response_on_write_default(),
                kwargs=kwargs_for_rust_prep,
            )

        return await self._run_item_operation(
            op=OP_UPSERT_ITEM,
            build_prepared=build_prepared,
            run_legacy=lambda: self.client_connection.UpsertItem(
                database_or_container_link=container_link,
                document=body,
                options=request_options,
                **kwargs,
            ),
            response_hook=kwargs.get("response_hook"),
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

        async def build_prepared() -> Any:
            partition_key_value = await self._extract_partition_key_value(
                container_link, body, request_options
            )
            return build_replace_item_prepared(
                container_link=container_link,
                body=body,
                item_id=item_id,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                access_condition=request_options.get("accessCondition"),
                no_response_on_write_default=self._no_response_on_write_default(),
                kwargs=kwargs_for_rust_prep,
            )

        return await self._run_item_operation(
            op=OP_REPLACE_ITEM,
            build_prepared=build_prepared,
            run_legacy=lambda: self.client_connection.ReplaceItem(
                document_link=document_link,
                new_document=body,
                options=request_options,
                **kwargs,
            ),
            response_hook=kwargs.get("response_hook"),
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

        # Use the rust path only for a plain patch. A filter or an
        # etag / match-condition guard cannot be represented by the rust prep,
        # so those force the legacy client even on a rust-backed client.
        rust_eligible = (
            filter_predicate is None
            and "accessCondition" not in request_options
        )

        async def build_prepared() -> Any:
            return build_patch_item_prepared(
                container_link=container_link,
                item_id=item_id,
                patch_operations=patch_operations,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                no_response_on_write_default=self._no_response_on_write_default(),
                kwargs=kwargs_for_rust_prep,
            )

        return await self._run_item_operation(
            op=OP_PATCH_ITEM,
            build_prepared=build_prepared,
            run_legacy=lambda: self.client_connection.PatchItem(
                document_link=document_link,
                operations=patch_operations,
                options=request_options,
                **kwargs,
            ),
            response_hook=kwargs.get("response_hook"),
            rust_eligible=rust_eligible,
        )
