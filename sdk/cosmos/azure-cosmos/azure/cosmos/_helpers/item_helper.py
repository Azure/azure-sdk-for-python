# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Per-client helper that runs every ``Container.create_item`` /
``Container.delete_item`` call.

``ItemHelper`` is where backend dispatch and the request-prep logic
(previously inlined in the container methods) live. The container
methods just stamp their explicit kwargs into ``kwargs`` and hand off
to one ``ItemHelper.create_item`` / ``ItemHelper.delete_item`` call.

Flow (same shape for both ops):

1. Build the legacy-shape ``request_options`` via the matching
   ``build_*_request_options`` helper.
2. Look up (or refresh) the container's ``_rid`` from the
   container-properties cache.
3. If a backend (today: ``RustBackend``) is wired, build a
   ``PreparedRequest``, call ``backend.execute``, parse the returned
   ``BackendResponse`` into a ``CosmosDict`` (raising the typed
   exception for non-2xx).
4. When no backend is wired, fall through to the legacy
   ``client_connection.CreateItem`` / ``.DeleteItem`` path.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .._backend.base import CosmosBackend
from .._constants import _Constants as Constants
from ..partition_key import _Empty
from ._item_dispatch import (
    build_create_item_request_options,
    build_delete_item_request_options,
)
from ._request_prep import build_create_item_prepared, build_delete_item_prepared
from ._response_parse import parse_backend_response


class ItemHelper:
    """Per-call request-prep + dispatch for ``create_item``.

    Cheap to construct (only holds references). One instance per
    ``Container.create_item`` invocation today.
    """

    def __init__(
        self,
        backend: Optional[CosmosBackend],
        client_connection: Any,
        ensure_container_cached: Optional[Callable[[Dict[str, Any]], Any]] = None,
    ) -> None:
        """Bind the helper to the chosen backend and the client connection.

        :param backend: The backend wired for this client, or ``None``
            for the legacy / bare-mock case.
        :type backend: Optional[CosmosBackend]
        :param client_connection: The ``CosmosClientConnection`` (or
            async sibling) used for the cache, PK extraction, and
            legacy fall-through.
        :type client_connection: Any
        :param ensure_container_cached: Optional callable supplied by
            the container proxy to perform the cache-populate step
            under the container's lock with proper option forwarding.
        :type ensure_container_cached: Optional[Callable]
        """
        self._backend = backend
        self.client_connection = client_connection
        self._ensure_container_cached = ensure_container_cached

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
        """Run a single ``create_item`` call end to end."""

        # Snapshot kwargs BEFORE the legacy options build drains them:
        # ``_base.build_options`` (called inside
        # ``build_create_item_request_options`` below) pops every
        # recognised kwarg. The Rust prep needs to see them later
        # (``compose_options_from_kwargs`` reads this dict to build
        # ``PreparedRequest.headers``), so keep a fresh copy here.
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_create_item_request_options(
            kwargs,
            enable_automatic_id_generation=enable_automatic_id_generation,
            indexing_directive=indexing_directive,
            populate_query_metrics=populate_query_metrics,
        )

        # Container-rid lookup. Best effort: bare-mock connections in
        # unit tests may not produce a real rid. We continue with
        # ``container_rid=None`` so the backend still gets called.
        container_rid: Optional[str] = None
        try:
            if self._ensure_container_cached is not None:
                self._ensure_container_cached(request_options)
            else:
                cache = self.client_connection._container_properties_cache
                if container_link not in cache:
                    self.client_connection._refresh_container_properties_cache(container_link)
            cached = self.client_connection._container_properties_cache[container_link]
            rid_value = cached.get("_rid") if isinstance(cached, dict) else None
            if isinstance(rid_value, str):
                container_rid = rid_value
                request_options[Constants.ContainerRID] = container_rid
        except Exception:  # pylint: disable=broad-except
            container_rid = None

        if self._backend is not None:
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
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = self._backend.execute(prepared)
            if backend_response is not None:
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        # Fall-through: legacy path.
        return self.client_connection.CreateItem(
            database_or_container_link=container_link,
            document=body,
            options=request_options,
            **kwargs,
        )

    def _extract_partition_key_value(
        self,
        container_link: str,
        body: Dict[str, Any],
        request_options: Dict[str, Any],
    ) -> Any:
        """Pull the partition-key value to put on the wire.

        Precedence (matches legacy ``_AddPartitionKey``):

        1. ``request_options["partitionKey"]`` if the caller set it.
        2. Extracted from ``body`` using the container's PK definition.
        3. ``_Empty()`` fallback for bare-mock connections that have
           no ``_AddPartitionKey`` method.
        """
        if "partitionKey" in request_options:
            return request_options["partitionKey"]
        try:
            new_options = self.client_connection._AddPartitionKey(
                container_link, body, request_options
            )
            if isinstance(new_options, dict):
                request_options.update(new_options)
                return new_options.get("partitionKey", _Empty())
        except Exception:  # pylint: disable=broad-except
            pass
        return _Empty()

    def delete_item(
        self,
        *,
        container_link: str,
        document_link: str,
        item_id: str,
        **kwargs: Any,
    ) -> Any:
        """Run a single ``delete_item`` call end to end.

        :param container_link: Container self-link.
        :param document_link: The ``dbs/.../docs/<id-or-rid>`` link the
            legacy ``DeleteItem`` consumes. Built by the caller via
            ``Container._get_document_link``.
        :param item_id: The document id the binding writes onto
            ``PreparedRequest.item_id``.
        :param kwargs: Caller's remaining kwargs. The caller has
            already stamped ``partitionKey`` into ``request_options``
            via ``Container._set_partition_key``.
        """
        # Snapshot kwargs before the legacy options build drains them.
        # Same reason as create_item: ``_base.build_options`` pops every
        # recognised key, but the rust prep still needs them.
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_delete_item_request_options(kwargs)

        # The caller stamped the PK into ``request_options`` before
        # getting here. Use that value so the rust prep does not need
        # to re-derive the wire shape.
        partition_key_value = request_options.get("partitionKey", _Empty())

        # Container-rid lookup; best-effort, same shape as create_item.
        container_rid: Optional[str] = None
        try:
            if self._ensure_container_cached is not None:
                self._ensure_container_cached(request_options)
            else:
                cache = self.client_connection._container_properties_cache
                if container_link not in cache:
                    self.client_connection._refresh_container_properties_cache(container_link)
            cached = self.client_connection._container_properties_cache[container_link]
            rid_value = cached.get("_rid") if isinstance(cached, dict) else None
            if isinstance(rid_value, str):
                container_rid = rid_value
                request_options[Constants.ContainerRID] = container_rid
        except Exception:  # pylint: disable=broad-except
            container_rid = None

        if self._backend is not None:
            prepared = build_delete_item_prepared(
                container_link=container_link,
                item_id=item_id,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = self._backend.execute(prepared)
            if backend_response is not None:
                # Delete returns 204 with an empty body. We still
                # invoke the response_hook so callers can observe
                # response headers; the helper returns None because
                # the public ``delete_item`` is typed ``-> None``.
                parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )
                return None

        # Fall-through: legacy path.
        return self.client_connection.DeleteItem(
            document_link=document_link,
            options=request_options,
            **kwargs,
        )

