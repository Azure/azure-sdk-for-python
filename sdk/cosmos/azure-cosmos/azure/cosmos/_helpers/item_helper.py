# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Runs each single-item container operation: create, read, delete,
upsert, replace, patch.

A container method gathers its arguments and calls the matching method
here. Each method builds the request options, looks up the container's
resource id, then drives the operation through the configured backend
(Rust, or the current core-Python ``LegacyBackend``) via
:meth:`~azure.cosmos._backend.base.CosmosBackend.run_operation`.

On a Rust-selected client, ``LegacyBackend`` is also the temporary fallback
for request shapes that have not been migrated yet. That fallback is migration
debt and is not part of the intended Rust-only architecture.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

from .._backend.base import CosmosBackend
from .._backend.contracts import BackendResponse, LegacyOperation, PreparedRequest
from .._backend.operations import (
    OP_CREATE_ITEM,
    OP_DELETE_ITEM,
    OP_PATCH_ITEM,
    OP_READ_ITEM,
    OP_REPLACE_ITEM,
    OP_UPSERT_ITEM,
)
from .._constants import _Constants as Constants
from ..partition_key import _Empty
from ._item_dispatch import (
    build_create_item_request_options,
    build_delete_item_request_options,
    build_patch_item_request_options,
    build_read_item_request_options,
    build_upsert_item_request_options,
)
from ._metadata_provider import ContainerMetadataProvider
from ._request_item import (
    build_create_item_prepared,
    build_delete_item_prepared,
    build_patch_item_prepared,
    build_read_item_prepared,
    build_replace_item_prepared,
    build_upsert_item_prepared,
)
from ._response_parse import parse_backend_response

_LOGGER = logging.getLogger(__name__)


class ItemHelper:
    """Per-call logic for the single-item operations.

    Cheap to construct -- it only holds references. One instance is made
    per container call.
    """

    def __init__(
        self,
        backend: CosmosBackend,
        client_connection: Any,
        ensure_container_cached: Optional[Callable[[Dict[str, Any]], Any]] = None,
    ) -> None:
        """Store the backend and connection this helper will use.

        :param backend: The selected concrete backend.
        :type backend: CosmosBackend
        :param client_connection: The connection used for the cache,
            partition-key extraction, response compatibility, and the
            core-Python path used either as the selected backend or as a
            temporary fallback during migration.
        :type client_connection: Any
        :param ensure_container_cached: Optional callable from the
            container that fills the cache under the container's lock.
        :type ensure_container_cached: Optional[Callable]
        """
        self._backend = backend
        self.client_connection = client_connection
        # Reads the two container facts the request prep needs (the rid and the
        # partition-key definition) off one container read, instead of calling
        # the connection's ``_container_properties_cache`` / ``_AddPartitionKey``
        # directly.
        self._metadata = ContainerMetadataProvider(
            client_connection,
            ensure_container_cached,
            self._backend.resolve_container_metadata,
        )

    def _run_item_operation(
        self,
        *,
        op: str,
        build_prepared: Callable[[], PreparedRequest],
        run_legacy: Callable[[], Any],
        response_hook: Optional[Callable[..., Any]],
        discard_result: bool = False,
        rust_eligible: bool = True,
    ) -> Any:
        """Drive one item op through the backend and return the final result.

        Wraps :meth:`~azure.cosmos._backend.base.CosmosBackend.run_operation`
        with the one piece that is common to every op: turning a rust
        ``BackendResponse`` into the value the public method returns. The rust
        path is taken only when this backend is the Rust engine and
        ``rust_eligible`` is true. During migration, other requests use the
        temporary legacy parity operation. This fallback is migration debt, not
        part of the intended Rust-only architecture. Either way this helper
        never inspects the backend type or a ``None`` sentinel.

        ``run_legacy`` is wrapped in a :class:`~azure.cosmos._backend.base.LegacyOperation`
        here -- a small, named, typed request/context, not a bare callable --
        before it crosses into the backend; see that class for why a fully
        generic reconstruction of the legacy call from wire-shaped fields alone
        is not safe (the six legacy item calls take differently-shaped
        arguments a ``PreparedRequest`` cannot carry).

        :keyword op: One of the ``OP_*`` constants, naming this operation.
        :keyword build_prepared: Builds the rust ``PreparedRequest`` (called
            lazily, only on the rust path, so the legacy path does no extra work).
        :keyword run_legacy: Runs the legacy ``client_connection.<Op>Item`` call.
        :keyword response_hook: Per-call response hook, invoked once on the rust
            path by ``parse_backend_response`` (the legacy path invokes its own).
        :keyword discard_result: When ``True`` (delete), parse the rust response
            for its side effects but return ``None``, matching the legacy delete.
        :keyword rust_eligible: During migration, ``False`` forces the temporary
            legacy call even on a Rust client (for example, a filtered or guarded
            patch the Rust preparation code cannot yet represent).
        :returns: The value the public method returns to the caller.
        :rtype: Any
        """
        def parse_response(response: BackendResponse) -> Any:
            parsed = parse_backend_response(
                response,
                client_connection=self.client_connection,
                response_hook=response_hook,
            )
            return None if discard_result else parsed

        return self._backend.run_operation(
            build_prepared=build_prepared,
            legacy_operation=LegacyOperation(op=op, invoke=run_legacy),
            parse_response=parse_response,
            rust_eligible=rust_eligible,
        )

    def _no_response_on_write_default(self) -> bool:
        """Read the client-level ``no_response_on_write`` setting.

        This is the ``no_response_on_write=True`` flag the customer can set at
        client construction (stored as
        ``connection_policy.ResponsePayloadOnWriteDisabled``). The write preps
        fall back to it when a call carries no per-call ``no_response``. A
        connection without a policy reads as ``False``.

        :rtype: bool
        """
        policy = getattr(self.client_connection, "connection_policy", None)
        return bool(getattr(policy, "ResponsePayloadOnWriteDisabled", False))

    def _resolve_container_rid(
        self,
        container_link: str,
        request_options: Dict[str, Any],
    ) -> Optional[str]:
        """Look up the container's resource id and add it to the options.

        Shared by every operation. Best-effort: if the id cannot be found
        the request still goes out, just without the header that guards
        against a recreated container. On success the id is stored in the
        options and returned. The lookup itself is delegated to the
        metadata provider; this method keeps the best-effort policy
        (logging a miss, stamping the header).
        """
        try:
            rid_value = self._metadata.container_rid(container_link, request_options)
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

    def create_item(
        self,
        *,
        container_link: str,
        body: Dict[str, Any],
        populate_query_metrics: Optional[bool] = None,
        indexing_directive: Optional[int] = None,
        enable_automatic_id_generation: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Run one create call."""

        # Copy the arguments first. Building the options below removes the
        # recognized keywords, but the request still needs the full set.
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_create_item_request_options(
            kwargs,
            enable_automatic_id_generation=enable_automatic_id_generation,
            indexing_directive=indexing_directive,
            populate_query_metrics=populate_query_metrics,
        )

        container_rid = self._resolve_container_rid(container_link, request_options)

        def build_prepared() -> Any:
            partition_key_value = self._extract_partition_key_value(
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

        return self._run_item_operation(
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

    def _extract_partition_key_value(
        self,
        container_link: str,
        body: Dict[str, Any],
        request_options: Dict[str, Any],
    ) -> Any:
        """Find the partition-key value to send.

        Order of preference: the value the caller already set, then the
        value the metadata provider digs out of the body (using the
        container's partition-key definition), then an empty placeholder
        when the connection cannot provide a definition (the stub
        connections used in unit tests). Replaces the old direct borrow of
        the connection's ``_AddPartitionKey``.
        """
        try:
            return self._metadata.extract_partition_key(container_link, body, request_options)
        except (AttributeError, TypeError):
            # Only the stub connections used in unit tests reach here (no
            # cache/read method, or a stub that is not callable). A real
            # extraction error is left to propagate so a wrong partition
            # key fails loudly instead of writing to the wrong place.
            return _Empty()

    def delete_item(
        self,
        *,
        container_link: str,
        document_link: str,
        item_id: str,
        **kwargs: Any,
    ) -> Any:
        """Run one delete call.

        :param container_link: The container link.
        :param document_link: The document link the fallback path uses,
            built by the caller.
        :param item_id: The document id sent on the request.
        :param kwargs: The caller's remaining arguments. The partition key
            is already in the options.
        """
        # Copy the arguments first (see create for why).
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_delete_item_request_options(kwargs)

        # The caller already put the partition key in the options.
        partition_key_value = request_options.get("partitionKey", _Empty())

        container_rid = self._resolve_container_rid(container_link, request_options)

        return self._run_item_operation(
            op=OP_DELETE_ITEM,
            build_prepared=lambda: build_delete_item_prepared(
                container_link=container_link,
                item_id=item_id,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                kwargs=kwargs_for_rust_prep,
            ),
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

    def read_item(
        self,
        *,
        container_link: str,
        document_link: str,
        item_id: str,
        **kwargs: Any,
    ) -> Any:
        """Run one read call.

        Same shape as delete. Returns the item for a 200, or an empty
        result for a 304 (a conditional read whose version matched).

        :param container_link: The container link.
        :param document_link: The document link the fallback path uses,
            built by the caller.
        :param item_id: The document id sent on the request.
        :param kwargs: The caller's remaining arguments. The partition key
            is already in the options.
        """
        # Copy the arguments first (see create for why).
        kwargs_for_rust_prep = dict(kwargs)

        # Building the options also checks the etag / match-condition pair
        # and raises on the caller before any network call.
        request_options = build_read_item_request_options(kwargs)

        # The caller already put the partition key in the options.
        partition_key_value = request_options.get("partitionKey", _Empty())

        container_rid = self._resolve_container_rid(container_link, request_options)

        return self._run_item_operation(
            op=OP_READ_ITEM,
            build_prepared=lambda: build_read_item_prepared(
                container_link=container_link,
                item_id=item_id,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                kwargs=kwargs_for_rust_prep,
            ),
            run_legacy=lambda: self.client_connection.ReadItem(
                document_link=document_link,
                options=request_options,
                **kwargs,
            ),
            # A 200 returns the item; a 304 returns an empty result that still
            # carries the current version. The response hook runs once either way.
            response_hook=kwargs.get("response_hook"),
        )

    def upsert_item(
        self,
        *,
        container_link: str,
        body: Dict[str, Any],
        populate_query_metrics: Optional[bool] = None,
        **kwargs: Any,
    ) -> Any:
        """Run one upsert call.

        Like create, the partition key comes from the body and the body is
        sent as-is, but an upsert never generates an id and it honors the
        etag / match-condition pair.
        """
        # Copy the arguments first (see create for why).
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_upsert_item_request_options(
            kwargs,
            populate_query_metrics=populate_query_metrics,
        )

        container_rid = self._resolve_container_rid(container_link, request_options)

        def build_prepared() -> Any:
            partition_key_value = self._extract_partition_key_value(
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

        return self._run_item_operation(
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

    def replace_item(
        self,
        *,
        container_link: str,
        document_link: str,
        item_id: str,
        body: Dict[str, Any],
        populate_query_metrics: Optional[bool] = None,
        **kwargs: Any,
    ) -> Any:
        """Run one replace call.

        Like upsert, but it overwrites an existing document. ``item_id``
        (taken from the caller's ``item``) names the document to replace,
        not the id inside the body.

        :param container_link: The container link.
        :param document_link: The document link the fallback path uses,
            built by the caller.
        :param item_id: The id of the document to overwrite.
        :param body: The replacement document.
        :param populate_query_metrics: Deprecated flag kept for the sync
            method; the async method passes ``None``.
        """
        # Copy the arguments first (see create for why).
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_upsert_item_request_options(
            kwargs,
            populate_query_metrics=populate_query_metrics,
        )

        container_rid = self._resolve_container_rid(container_link, request_options)

        def build_prepared() -> Any:
            partition_key_value = self._extract_partition_key_value(
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

        return self._run_item_operation(
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

    def patch_item(
        self,
        *,
        container_link: str,
        document_link: str,
        item_id: str,
        patch_operations: Any,
        filter_predicate: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """Run one patch call.

        The backend is used only for a plain patch. A patch with a filter
        or an etag / match-condition guard uses the existing client
        instead, which is the only path that applies them.

        :param container_link: The container link.
        :param document_link: The document link the fallback path uses,
            built by the caller.
        :param item_id: The id of the document to patch.
        :param patch_operations: The list of patch operations.
        :param filter_predicate: Optional filter; when set, forces the
            existing-client path.
        :param kwargs: The caller's remaining arguments.
        """
        # Copy the arguments first (see create for why).
        kwargs_for_rust_prep = dict(kwargs)

        # Building the options also checks the etag / match-condition pair
        # (raising on the caller before any network call) and records a
        # valid pair so the check below can see it.
        request_options = build_patch_item_request_options(kwargs)
        if filter_predicate is not None:
            request_options["filterPredicate"] = filter_predicate

        # The caller already put the partition key in the options.
        partition_key_value = request_options.get("partitionKey", _Empty())

        container_rid = self._resolve_container_rid(container_link, request_options)

        # Rust currently supports only a plain patch. A filter or an
        # etag / match-condition guard cannot yet be represented by the Rust
        # preparation code, so migration parity temporarily routes those
        # requests through the legacy client.
        rust_eligible = (
            filter_predicate is None
            and "accessCondition" not in request_options
        )

        return self._run_item_operation(
            op=OP_PATCH_ITEM,
            build_prepared=lambda: build_patch_item_prepared(
                container_link=container_link,
                item_id=item_id,
                patch_operations=patch_operations,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                no_response_on_write_default=self._no_response_on_write_default(),
                kwargs=kwargs_for_rust_prep,
            ),
            # Existing client. This path also applies the filter and the
            # etag / match-condition guard.
            run_legacy=lambda: self.client_connection.PatchItem(
                document_link=document_link,
                operations=patch_operations,
                options=request_options,
                **kwargs,
            ),
            response_hook=kwargs.get("response_hook"),
            rust_eligible=rust_eligible,
        )
